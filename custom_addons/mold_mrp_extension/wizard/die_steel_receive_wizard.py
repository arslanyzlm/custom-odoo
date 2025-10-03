from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


DIE_STEEL_CATEGORY_XMLID = 'mold_mrp_extension.product_category_die_steel'

class DieSteelReceiveWizard(models.TransientModel):
    _name = 'die.steel.receive.wizard'
    _description = 'Yeni Çelik Lotu ve Stok Girişi'

    product_tmpl_id = fields.Many2one('product.template', string='Kalıp Çeliği', required=True)
    supplier_id = fields.Many2one('res.partner', string='Tedarikçi')
    certificate_no = fields.Char('Sertifika No', required=True)
    diameter_mm = fields.Integer('Çelik Çapı (mm)')
    length_mm = fields.Float('Çelik Boyu (mm)')
    scale_weight_kg = fields.Float('Kantar Kilosu (kg)', required=True)
    note = fields.Text('Açıklama')
    certificate_file = fields.Binary('Sertifika (PDF)')
    certificate_filename = fields.Char()

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if 'product_tmpl_id' in fields_list and not res.get('product_tmpl_id'):
            if self.env.context.get('active_model') == 'product.template' and self.env.context.get('active_id'):
                res['product_tmpl_id'] = self.env.context['active_id']
        return res
    
    @api.onchange('product_tmpl_id')
    def _onchange_product_tmpl(self):
        for w in self:
            if w.product_tmpl_id:
                w.diameter_mm = w.product_tmpl_id.x_diameter_mm
    
    def _ensure_die_steel_category(self, tmpl):
        try:
            die_cat = self.env.ref(DIE_STEEL_CATEGORY_XMLID)
        except ValueError:
            die_cat = False
        if not (tmpl and die_cat and tmpl.categ_id.id == die_cat.id):
            raise ValidationError(_('Seçilen ürün Kalıp Çeliği kategorisinde olmalıdır.'))
        
    # def _next_lot_name(self):
    #     # Sequence fallback chain
    #     seq = self.env['ir.sequence'].next_by_code('stock.lot.serial') or \
    #         self.env['ir.sequence'].next_by_code('stock.lot') or \
    #         'LOT/NEW'
    #     return seq

    def _lot_name_from_certificate(self):
        cert = (self.certificate_no or '').strip()
        if not cert:
            raise ValidationError(_('Sertifika No zorunludur.'))
        return f"KC-{cert}"
    
    def action_confirm(self):
        self.ensure_one()
        if self.scale_weight_kg <= 0:
            raise ValidationError(_('Kantar kilosu 0’dan büyük olmalı.'))
        tmpl = self.product_tmpl_id
        self._ensure_die_steel_category(tmpl)
        product = tmpl.product_variant_id
        if not product:
            raise ValidationError(_('Ürünün bir varyantı bulunamadı.'))
        
        name = self._lot_name_from_certificate()
        # Aynı isimli lot varsa uyar (şirket bazında)
        exists = self.env['stock.lot'].sudo().search_count([
            ('name', '=', name),
            ('company_id', '=', self.env.company.id),
        ])
        if exists:
            raise ValidationError(_(f'Aynı isimde lot zaten var: {name}'))
        
        # 1) LOT oluştur
        lot_vals = {
            'name': name, #_next_lot_name(),
            'product_id': product.id,
            'company_id': self.env.company.id,
            'x_certificate_no': self.certificate_no,
            'x_supplier_id': self.supplier_id.id,
            'x_diameter_mm': self.diameter_mm or tmpl.x_diameter_mm,
            'x_length_mm': self.length_mm or 0.0,
            'x_scale_weight_kg': self.scale_weight_kg,
            'x_note': self.note or '',
        }
        lot = self.env['stock.lot'].create(lot_vals)

        if self.certificate_file:
            self.env['ir.attachment'].create({
                'name': self.certificate_filename or 'certificate.pdf',
                'res_model': 'stock.lot',
                'res_id': lot.id,
                'datas': self.certificate_file,
            })

        # 2) Incoming picking yarat ve tamamla
        picking_type = self.env['stock.picking.type'].search([
            ('code', '=', 'incoming'),
            ('warehouse_id.company_id', '=', self.env.company.id)
        ], limit=1)
        if not picking_type:
            # şirket filtresi olmadan dene
            picking_type = self.env['stock.picking.type'].search([('code', '=', 'incoming')], limit=1)
        if not picking_type:
            raise ValidationError(_('Incoming (Receipts) tipi bulunamadı. Depo yapılandırmasını kontrol edin.'))


        picking = self.env['stock.picking'].create({
            'picking_type_id': picking_type.id,
            'partner_id': self.supplier_id.id,
            'location_id': picking_type.default_location_src_id.id,
            'location_dest_id': picking_type.default_location_dest_id.id,
        })
        move = self.env['stock.move'].create({
            'name': product.display_name,
            'product_id': product.id,
            'product_uom': product.uom_id.id,
            'product_uom_qty': self.scale_weight_kg,
            'picking_id': picking.id,
            'location_id': picking.location_id.id,
            'location_dest_id': picking.location_dest_id.id,
        })
        move._action_confirm(); move._action_assign()

        # Move line’a lot ve qty_done bağla
        MoveLine = self.env['stock.move.line']
        qty_field = 'quantity' if 'quantity' in MoveLine._fields else 'qty_done'
        uom_field = 'uom_id'   if 'uom_id'   in MoveLine._fields else 'product_uom_id'

        mls = move.move_line_ids
        if not mls:
            self.env['stock.move.line'].create({
                'move_id': move.id,
                'product_id': product.id,
                uom_field: product.uom_id.id,
                qty_field: self.scale_weight_kg,
                'location_id': picking.location_id.id,
                'location_dest_id': picking.location_dest_id.id,
                'picking_id': picking.id,
                'lot_id': lot.id,
            })
        else:
            mls[0].write({qty_field: self.scale_weight_kg, 'lot_id': lot.id})

        # Validate
        res = picking.button_validate()
        # bazı kurulumlarda immediate transfer wizard döndürebilir; res bir action ise yine de lot oluşturuldu ve qty girildi

        # Lot formuna dön
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.lot',
            'res_id': lot.id,
            'view_mode': 'form',
        }
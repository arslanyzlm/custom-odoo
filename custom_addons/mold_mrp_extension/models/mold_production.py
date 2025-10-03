from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


COMPONENT_MAP = {
    'havuz': {'code': 'YM-HVZ'},
    'disi': {'code': 'YM-DSI'},
    'kopru': {'code': 'YM-KPR'},
    'destek': {'code': 'YM-DST'},
    'kapak': {'code': 'YM-KPK'},
    'bolster': {'code': 'YM-BOL'},
}
SHORT_MAP = {
    'havuz': 'HVZ', 'disi': 'DSI', 'kopru': 'KPR',
    'destek': 'DST', 'kapak': 'KPK', 'bolster': 'BOL',
}

class MoldProduction(models.Model):
    _name = 'mold.production'
    _description = 'Mold Production Header'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Kalıp No', required=True, index=True, copy=False)
    type = fields.Selection([
        ('solid', 'Solid'),
        ('portol', 'Portol')
    ], string='Kalıp Tipi', required=True, default='solid')
    diameter_mm = fields.Integer('Kalıp Çapı (mm)')
    tool_packet_length_mm = fields.Float('Takım Paket Boyu (mm)')

    design_attachment_ids = fields.Many2many('ir.attachment', string='Tasarım Dosyaları')

    component_ids = fields.One2many('mold.component', 'mold_id', string='Bileşenler')

    state = fields.Selection([
        ('draft', 'Taslak'),
        ('in_progress', 'Üretimde'),
        ('done', 'Tamamlandı'),
    ], default='draft', tracking=True)

    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Kalıp No benzersiz olmalıdır!')
    ]

    def _find_semi_product(self, comp_type):
        """Yarı mamul ürününü default_code ile bul."""
        code = COMPONENT_MAP.get(comp_type, {}).get('code')
        if not code:
            raise ValidationError(_('Bileşen eşlemesi bulunamadı: %s') % comp_type)
        tmpl = self.env['product.template'].search([('default_code', '=', code)], limit=1)
        if not tmpl:
            raise ValidationError(_('Yarı mamul ürün (default_code=%s) bulunamadı. Lütfen ürünü oluşturun.') % code)
        product = tmpl.product_variant_id
        if not product:
            raise ValidationError(_('Yarı mamul ürün varyantı bulunamadı: %s') % code)
        return product
    
    def _find_bom(self, product):
        """Odoo 17 uyumlu: önce variant, sonra template bazlı BoM bulur."""
        Bom = self.env['mrp.bom']
        company_id = self.env.company.id

        # 1) Varyant için tanımlı BoM
        bom = Bom.search([
            ('product_id', '=', product.id),
            ('company_id', 'in', [False, company_id]),
            ('type', 'in', ['normal', 'phantom']),
        ], order='sequence, id', limit=1)

        # 2) Template için genel BoM (variant boş)
        if not bom:
            bom = Bom.search([
                ('product_tmpl_id', '=', product.product_tmpl_id.id),
                ('product_id', '=', False),
                ('company_id', 'in', [False, company_id]),
                ('type', 'in', ['normal', 'phantom']),
            ], order='sequence, id', limit=1)

        if not bom:
            raise ValidationError(_('Ürün için BoM bulunamadı: %s') % product.display_name)
        return bom
    
    def _next_finished_serial(self, mold_rec, comp_type, product):
        base = f"{mold_rec.name}-{SHORT_MAP.get(comp_type, 'CMP')}"
        Lot = self.env['stock.lot']
        # mevcut aynı ürün için bu kalıp+kod altında kaç lot var → +1 iki haneli
        cnt = Lot.search_count([
            ('name', 'like', f"{base}-%"),
            ('product_id', '=', product.id),
            ('company_id', 'in', [False, self.env.company.id]),
        ])
        return f"{base}-{cnt+1:02d}"
    
    def _assign_finished_lot(self, mo, lot_name):
        Lot = self.env['stock.lot']
        lot = Lot.search([
            ('name', '=', lot_name),
            ('product_id', '=', mo.product_id.id),
            ('company_id', 'in', [False, self.env.company.id]),
        ], limit=1)
        if not lot:
            lot = Lot.create({
                'name': lot_name,
                'product_id': mo.product_id.id,
                'company_id': self.env.company.id,
            })
        # Odoo 17: mrp.production’da lot_producing_id genelde mevcut
        if 'lot_producing_id' in mo._fields:
            mo.lot_producing_id = lot.id
        # fallback gerekmiyorsa başka işlem yok; mark done sırasında bu lot kullanılacak
        return lot

    def action_start(self):
        for rec in self:
            if not rec.component_ids:
                raise ValidationError(_('En az bir bileşen ekleyin.'))

            for line in rec.component_ids:
                if line.mrp_production_id:
                    continue # zaten açılmış
                # 1) Yarım mamul ürünü + BoM
                product = rec._find_semi_product(line.component_type)
                bom = rec._find_bom(product)

                # 2) MO oluştur
                Prod = self.env['mrp.production']
                uom_field = 'uom_id' if 'uom_id' in Prod._fields else 'product_uom_id'
                mo_vals = {
                    'product_id': product.id,
                    'product_qty': 1.0,
                    uom_field: product.uom_id.id,
                    'bom_id': bom.id,
                    'origin': rec.name,
                    'company_id': rec.company_id.id if hasattr(rec, 'company_id') else self.env.company.id,
                }
                mo = self.env['mrp.production'].create(mo_vals)
                mo.write({
                    'x_mold_id': rec.id,
                    'x_mold_component_id': line.id,
                    'x_component_type': line.component_type,
                    'x_part_packet_length_mm': line.part_packet_length_mm,
                    'x_steel_product_id': line.steel_product_id.id,
                    'x_theoretical_steel_kg': line.theoretical_consumption_kg,
                    'x_tool_packet_length_mm': rec.tool_packet_length_mm,
                })
                # 3) tasarım eklerini MO'ya kopyala (referans amaçlı)
                for att in rec.design_attachment_ids:
                    self.env['ir.attachment'].create({
                        'name': att.name,
                        'datas': att.datas,
                        'res_model': 'mrp.production',
                        'res_id': mo.id,
                        'mimetype': att.mimetype,
                    })
                # 4) Çelik ürününü MO Components'a "ham madde" olarak ekle
                steel = line.steel_product_id
                theo_qty = line.theoretical_consumption_kg or 0.0
                if steel and theo_qty > 0:
                    Move = self.env['stock.move']
                    move_uom_field = 'product_uom' if 'product_uom' in Move._fields else 'uom_id'
                    move_vals = {
                        'name': f"{steel.display_name} / {rec.name} - {line.component_type}",
                        'product_id': steel.id,
                        move_uom_field: steel.uom_id.id,
                        'product_uom_qty': theo_qty,          # teorik tüketim (kg)
                        'raw_material_production_id': mo.id,   # <-- MO'ya ham madde olarak bağlar
                        # Lokasyonlar genelde MO'dan türetilir; çoğu kurulumda bunları vermek şart değil.
                        # Gerekirse aşağıdaki iki satırı aç:
                        # 'location_id': mo.location_src_id.id,
                        # 'location_dest_id': self.env.ref('stock.stock_location_production').id,
                        'company_id': self.env.company.id,
                        'description_picking': f"Kalıp: {rec.name} / Bileşen: {line.component_type.upper()}",
                    }
                    self.env['stock.move'].create(move_vals)

                # 5) Seri ismi otomatik (daha önce eklediğimiz fonksiyonlarla)
                serial_name = rec._next_finished_serial(rec, line.component_type, product)
                rec._assign_finished_lot(mo, serial_name)
                # 6) Satıra MO'yu bağla
                line.mrp_production_id = mo.id

            rec.state = 'in_progress'
            rec.message_post(body=_('Bileşenler için üretim emirleri oluşturuldu.'))
        return True
    
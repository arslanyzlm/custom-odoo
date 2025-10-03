import math
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class MoldComponent(models.Model):
    _name = 'mold.component'
    _description = 'Mold Component Line'
    _rec_name = 'name'  # <<< görünür ad bu alan

    name = fields.Char(string='Ad', compute='_compute_name', store=True, index=True)

    mold_id = fields.Many2one('mold.production', required=True, ondelete='cascade')

    component_type = fields.Selection([
        ('havuz', 'Havuz'),
        ('disi', 'Dişi'),
        ('kopru', 'Köprü'),
        ('destek', 'Destek'),
        ('kapak', 'Kapak'),
        ('bolster', 'Bolster'),
    ], string='Bileşen Tipi', required=True)

    steel_product_id = fields.Many2one(
        'product.product', string='Çelik Ürünü'
    )

    @api.depends('mold_id.name', 'component_type')
    def _compute_name(self):
        labels = dict(self._fields['component_type'].selection)
        for rec in self:
            mold = rec.mold_id.name or ''
            comp  = labels.get(rec.component_type) or ''
            rec.name = f"{mold} / {comp}" if (mold or comp) else _("Bileşen")
    
    @api.constrains('steel_product_id')
    def _check_steel_category(self):
        die_cat = self.env.ref('mold_mrp_extension.product_category_die_steel', raise_if_not_found=False)
        for rec in self:
            if rec.steel_product_id and die_cat and rec.steel_product_id.product_tmpl_id.categ_id != die_cat:
                raise ValidationError(_('Seçilen ürün Kalıp Çeliği kategorisinde olmalıdır.'))

    @api.onchange('steel_product_id')
    def _onchange_steel_product_id(self):
        die_cat = self.env.ref('mold_mrp_extension.product_category_die_steel', raise_if_not_found=False)
        for rec in self:
            if rec.steel_product_id and die_cat and rec.steel_product_id.product_tmpl_id.categ_id != die_cat:
                rec.steel_product_id = False
                return {
                    'warning': {
                        'title': _('Uyarı'),
                        'message': _('Lütfen Kalıp Çeliği kategorisinden bir ürün seçin.')
                    }
                }

    part_packet_length_mm = fields.Float('Parça Paket Boyu (mm)', required=True)

    theoretical_consumption_kg = fields.Float('Teorik Çelik (kg)', compute='_compute_theoretical', store=True)

    mrp_production_id = fields.Many2one('mrp.production', string='Üretim Emri (MO)', readonly=True)


    @api.depends('part_packet_length_mm', 'steel_product_id')
    def _compute_theoretical(self):
        for rec in self:
            L = rec.part_packet_length_mm or 0.0
            D = rec.steel_product_id.product_tmpl_id.x_diameter_mm if rec.steel_product_id else 0
            rec.theoretical_consumption_kg = (L * (D ** 2) * math.pi * 7.85) / 4_000_000 if (L and D) else 0.0
            
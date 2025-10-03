# -*- coding: utf-8 -*-
from odoo import fields, models

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    x_mold_id = fields.Many2one('mold.production', string='Kalıp', readonly=True)
    x_mold_component_id = fields.Many2one('mold.component', string='Kalıp Bileşeni', readonly=True)

    x_component_type = fields.Selection([
        ('havuz', 'Havuz'), ('disi', 'Dişi'), ('kopru', 'Köprü'),
        ('destek', 'Destek'), ('kapak', 'Kapak'), ('bolster', 'Bolster'),
    ], string='Bileşen Tipi', readonly=True)

    x_part_packet_length_mm = fields.Float('Parça Paket Boyu (mm)', readonly=True)
    x_steel_product_id = fields.Many2one('product.product', string='Çelik Ürünü', readonly=True)
    x_theoretical_steel_kg = fields.Float('Teorik Kullanılacak Çelik (kg)', readonly=True)
    x_tool_packet_length_mm = fields.Float('Takım Paket Boyu (mm)', readonly=True)
from odoo import api, fields, models
import math


class ProductTemplate(models.Model):
    _inherit = "product.template"


    x_density_kg_m3 = fields.Float(
        string="Yoğunluk (kg/m³)",
        help="Density used to convert length and actual diameter to kg. Typical tool steel ~7850 kg/m³.",
        default=7850.0,
    )
    x_nominal_diameter_mm = fields.Float(
        string="Nominal Çap (mm)",
        help="Optional helper to store the template's diameter explicitly (Ø180, etc)."
    )

    x_show_steel_helpers = fields.Boolean(
        string="Show Steel Helpers",
        compute="_compute_x_show_steel_helpers",
        store=False,
    )

    @api.depends('categ_id', 'categ_id.complete_name')
    def _compute_x_show_steel_helpers(self):
        TARGET = "HAMMADDE"
        for rec in self:
            cat = rec.categ_id
            path = (cat.complete_name or "").strip().upper() if cat else ""
            rec.x_show_steel_helpers = (path == TARGET)


    def steel_kg_from_length(self, length_mm, actual_diameter_mm):
        """Helper: kg = length(m) * area(m²) * density(kg/m³)."""
        self.ensure_one()
        if not (length_mm and actual_diameter_mm and self.x_density_kg_m3):
            return 0.0
        length_m = (length_mm or 0.0) / 1000.0
        d_m = (actual_diameter_mm or 0.0) / 1000.0
        area_m2 = math.pi * (d_m ** 2) / 4.0
        kg = length_m * area_m2 * (self.x_density_kg_m3 or 0.0)
        return kg

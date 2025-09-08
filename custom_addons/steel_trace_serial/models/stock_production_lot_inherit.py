from odoo import api, fields, models
import math


class StockProductionLot(models.Model):
    _inherit = "stock.lot"


    x_certificate_no = fields.Char(string="Sertifika No", index=True)
    x_heat_no = fields.Char(string="Heat No")
    x_actual_diameter_mm = fields.Float(string="Gerçek Çap (mm)")
    x_initial_length_mm = fields.Float(string="İlk Boy (mm)")
    x_received_weight_kg = fields.Float(string="Geliş Kg")
    x_vendor_id = fields.Many2one("res.partner", string="Tedarikçi")

    # NEW: link all cuts of this lot
    steel_cut_ids = fields.One2many("steel.cut", "lot_id", string="Kesimler")

    x_remaining_length_mm = fields.Float(string="Kalan Boy (mm)", compute="_compute_remaining", store=True)
    x_remaining_weight_kg = fields.Float(string="Kalan Kg", compute="_compute_remaining", store=True)

    @api.depends(
        "x_received_weight_kg",
        "x_actual_diameter_mm",
        "steel_cut_ids.weight_used_kg",   # depend on cut lines
        "product_id.product_tmpl_id.x_density_kg_m3",
        "x_initial_length_mm",
    )
    def _compute_remaining(self):
        for lot in self:
            received_kg = lot.x_received_weight_kg or 0.0
            consumed_kg = sum(lot.steel_cut_ids.mapped("weight_used_kg")) or 0.0
            remaining_kg = max(received_kg - consumed_kg, 0.0)
            lot.x_remaining_weight_kg = remaining_kg

            tmpl = lot.product_id.product_tmpl_id
            if tmpl and tmpl.x_density_kg_m3 and lot.x_actual_diameter_mm:
                d_m = (lot.x_actual_diameter_mm or 0.0) / 1000.0
                area_m2 = math.pi * (d_m ** 2) / 4.0
                length_m = remaining_kg / (area_m2 * (tmpl.x_density_kg_m3 or 1.0)) if area_m2 else 0.0
                lot.x_remaining_length_mm = max(length_m * 1000.0, 0.0)
            else:
                # proportional fallback if initial length/received kg exist
                if (lot.x_initial_length_mm or 0.0) > 0 and (lot.x_received_weight_kg or 0.0) > 0:
                    ratio = remaining_kg / (lot.x_received_weight_kg or 1.0)
                    lot.x_remaining_length_mm = max((lot.x_initial_length_mm or 0.0) * ratio, 0.0)
                else:
                    lot.x_remaining_length_mm = 0.0
                    
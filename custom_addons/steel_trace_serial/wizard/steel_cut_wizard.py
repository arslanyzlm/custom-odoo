from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SteelCutWizard(models.TransientModel):
    _name = "steel.cut.wizard"
    _description = "Cut from Serial (Length or Weight)"


    production_id = fields.Many2one("mrp.production", required=True)
    product_id = fields.Many2one("product.product", string="Hammadde", required=True)
    lot_id = fields.Many2one("stock.production.lot", string="Seri", domain="[('product_id','=',product_id)]", required=True)


    input_mode = fields.Selection([
        ("length", "Boy (mm) gir"),
        ("weight", "Kg gir"),
    ], default="length", required=True)


    length_used_mm = fields.Float(string="Kullanılan Boy (mm)")
    weight_used_kg = fields.Float(string="Kullanılan Kg")
    note = fields.Char(string="Not")


    @api.onchange("input_mode", "length_used_mm", "lot_id")
    def _onchange_compute_weight(self):
        if self.input_mode == "length" and self.length_used_mm and self.lot_id:
            tmpl = self.lot_id.product_id.product_tmpl_id
            self.weight_used_kg = tmpl.steel_kg_from_length(self.length_used_mm, self.lot_id.x_actual_diameter_mm)


    def action_confirm(self):
        self.ensure_one()
        if self.input_mode == "length" and self.length_used_mm <= 0:
            raise UserError(_("Lütfen kullanılan boyu giriniz."))
        if self.input_mode == "weight" and self.weight_used_kg <= 0:
            raise UserError(_("Lütfen kullanılan kilogramı giriniz."))


        vals = {
            "lot_id": self.lot_id.id,
            "production_id": self.production_id.id,
            "length_used_mm": self.length_used_mm if self.input_mode == "length" else 0.0,
            "weight_used_kg": self.weight_used_kg if self.input_mode == "weight" else 0.0,
            "note": self.note,
        }
        self.env["steel.cut"].create(vals)
        return {"type": "ir.actions.act_window_close"}
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SteelCut(models.Model):
    _name = "steel.cut"
    _description = "Steel Cut Record"
    _order = "create_date desc"


    lot_id = fields.Many2one("stock.lot", string="Seri (Bar)", required=True, index=True)
    product_id = fields.Many2one(related="lot_id.product_id", store=True)
    production_id = fields.Many2one("mrp.production", string="Üretim Emri")
    date = fields.Datetime(string="Tarih", default=lambda self: fields.Datetime.now())
    length_used_mm = fields.Float(string="Kullanılan Boy (mm)")
    weight_used_kg = fields.Float(string="Kullanılan Kg")
    note = fields.Char(string="Not")
    user_id = fields.Many2one("res.users", string="Kullanıcı", default=lambda self: self.env.user)


    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            lot = rec.lot_id
            if not lot:
                continue
            # Compute missing measure
            if not rec.weight_used_kg and rec.length_used_mm:
                tmpl = lot.product_id.product_tmpl_id
                rec.weight_used_kg = tmpl.steel_kg_from_length(rec.length_used_mm, lot.x_actual_diameter_mm)


            if rec.weight_used_kg <= 0:
                raise UserError(_("Kullanılan kg (veya mm'den hesaplanan kg) 0 olamaz."))


            # Validate remaining
            if (lot.x_remaining_weight_kg or 0.0) < rec.weight_used_kg - 1e-6:
                raise UserError(_("Seçilen seri için yeterli stok yok. Kalan: %.3f kg") % (lot.x_remaining_weight_kg or 0.0))


            # Create MRP raw consumption move line when linked to a production
            if rec.production_id:
                rec._consume_on_mo()


        return records


    def _consume_on_mo(self):
        self.ensure_one()
        mo = self.production_id
        product = self.product_id
        if not mo or not product:
            return
        # Find the matching raw move in the MO for this product variant
        raw_move = mo.move_raw_ids.filtered(lambda m: m.product_id == product)
        if not raw_move:
            raise UserError(_("Üretim emrinde bu ürün için hammadde satırı bulunamadı: %s") % product.display_name)


        # Create or reuse a move line for this lot and set qty_done in kg
        move_line = self.env["stock.move.line"].create({
            "move_id": raw_move[0].id,
            "product_id": product.id,
            "lot_id": self.lot_id.id,
            "qty_done": self.weight_used_kg,
            "product_uom_id": product.uom_id.id,
            "location_id": raw_move[0].location_id.id,
            "location_dest_id": raw_move[0].location_dest_id.id,
        })
        # Let Odoo recompute; lot remaining fields are computed and will follow via dependencies/hooks
        return move_line


class MrpProduction(models.Model):
    _inherit = "mrp.production"


    def action_open_steel_cut_wizard(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "steel.cut.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
            "default_production_id": self.id,
            },
        }
from odoo import models
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        for move_line in self.move_line_ids:
            product = move_line.product_id
            if (
                product.categ_id
                and product.categ_id.name == "Kalıp Çeliği"
                and product.tracking == "serial"
                and move_line.lot_id
            ):
                lot = move_line.lot_id
                required = [
                    lot.x_certificate_no,
                    lot.x_actual_diameter_mm,
                    lot.x_initial_length_mm,
                    lot.x_received_weight_kg,
                ]
                if not all(required):
                    raise UserError(
                        "Lütfen seri üzerindeki zorunlu çelik alanlarını doldurun."
                    )
        return super().button_validate()

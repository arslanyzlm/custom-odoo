from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

DIE_STEEL_CATEGORY_XMLID = 'mold_mrp_extension.product_category_die_steel'

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    x_alloy = fields.Selection([
        ('1.2379', '1.2379'),
        ('1.2343', '1.2343'),
        ('other', 'Diğer'),
    ], string='Alaşım')
    x_diameter_mm = fields.Integer(string='Çap (mm)')

    def _is_die_steel_category(self):
        self.ensure_one()
        try:
            die_cat = self.env.ref(DIE_STEEL_CATEGORY_XMLID)
        except ValueError:
            return False
        return self.categ_id and self.categ_id.id == die_cat.id


    @api.onchange('x_alloy', 'x_diameter_mm', 'categ_id')
    def _onchange_auto_name_and_tracking(self):
        for rec in self:
            if rec._is_die_steel_category() and rec.x_alloy and rec.x_diameter_mm:
                rec.name = f"Kalıp Çeliği-{rec.x_alloy}-Ø{rec.x_diameter_mm}"
                rec.tracking = 'lot' # lot takibi zorunlu


    @api.constrains('x_alloy', 'x_diameter_mm', 'categ_id')
    def _check_die_steel_unique(self):
        for rec in self:
            if not rec._is_die_steel_category() or not rec.x_alloy or not rec.x_diameter_mm:
                continue
            domain = [
                ('id', '!=', rec.id),
                ('categ_id', '=', rec.categ_id.id),
                ('x_alloy', '=', rec.x_alloy),
                ('x_diameter_mm', '=', rec.x_diameter_mm),
            ]
            dup = self.search_count(domain)
            if dup:
                raise ValidationError(_('Aynı Alaşım ve Çap için ikinci bir Kalıp Çeliği ürünü oluşturulamaz.'))
        
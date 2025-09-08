# models/mrp_custom_wizard.py
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class CustomMrpWizard(models.TransientModel):
    _name = 'mrp.custom.wizard'
    _description = 'Custom Manufacturing Order Wizard'

    # Header
    type_selection = fields.Selection([('new', 'New'), ('spare', 'Spare')], string="Type", required=True)
    kalip_no = fields.Char("Kalıp No", required=True)
    yan_no = fields.Char("Yan No", required=True)
    mold_type = fields.Selection([('solid', 'SOLID'), ('portol', 'PORTOL')], string="Mold Type", required=True)
    cap = fields.Float("Çap")
    takim_paket_boyu = fields.Char("Takım Paket Boyu")

    # Helper for readable domain; we keep the domain in XML to avoid RPC in form open
    # but we still allow any product technically, so we validate on save.
    # --- SOLID options ---
    solid_havuz = fields.Boolean("Havuz")
    solid_havuz_celik = fields.Many2one('product.product', string="Çelik")
    solid_havuz_paket = fields.Char("Parça Paket Boyu")

    solid_destek = fields.Boolean("Destek")
    solid_destek_celik = fields.Many2one('product.product', string="Çelik")
    solid_destek_paket = fields.Char("Parça Paket Boyu")

    solid_kapak = fields.Boolean("Kapak")
    solid_kapak_celik = fields.Many2one('product.product', string="Çelik")
    solid_kapak_paket = fields.Char("Parça Paket Boyu")

    solid_bolster = fields.Boolean("Bolster")
    solid_bolster_celik = fields.Many2one('product.product', string="Çelik")
    solid_bolster_paket = fields.Char("Parça Paket Boyu")

    # --- PORTOL options ---
    portol_kopru = fields.Boolean("Köprü")
    portol_kopru_celik = fields.Many2one('product.product', string="Çelik")
    portol_kopru_paket = fields.Char("Parça Paket Boyu")

    portol_disi = fields.Boolean("Dişi")
    portol_disi_celik = fields.Many2one('product.product', string="Çelik")
    portol_disi_paket = fields.Char("Parça Paket Boyu")

    portol_destek = fields.Boolean("Destek")
    portol_destek_celik = fields.Many2one('product.product', string="Çelik")
    portol_destek_paket = fields.Char("Parça Paket Boyu")

    portol_bolster = fields.Boolean("Bolster")
    portol_bolster_celik = fields.Many2one('product.product', string="Çelik")
    portol_bolster_paket = fields.Char("Parça Paket Boyu")

    @api.onchange('mold_type')
    def _onchange_mold_type_cleanup(self):
        for w in self:
            if w.mold_type == 'solid':
                w.update({
                    'portol_kopru': False, 'portol_kopru_celik': False, 'portol_kopru_paket': False,
                    'portol_disi': False, 'portol_disi_celik': False, 'portol_disi_paket': False,
                    'portol_destek': False, 'portol_destek_celik': False, 'portol_destek_paket': False,
                    'portol_bolster': False, 'portol_bolster_celik': False, 'portol_bolster_paket': False,
                })
            elif w.mold_type == 'portol':
                w.update({
                    'solid_havuz': False, 'solid_havuz_celik': False, 'solid_havuz_paket': False,
                    'solid_destek': False, 'solid_destek_celik': False, 'solid_destek_paket': False,
                    'solid_kapak': False, 'solid_kapak_celik': False, 'solid_kapak_paket': False,
                    'solid_bolster': False, 'solid_bolster_celik': False, 'solid_bolster_paket': False,
                })

    # --- Validation helpers ---
    @staticmethod
    def _is_kalip_celigi(product):
        """Ensure the selected product is in category 'KALIP ÇELİĞİ' (name-based)."""
        return bool(product and product.categ_id and product.categ_id.name == 'HAMMADDE / KALIP ÇELİĞİ')

    def _validate_selected(self):
        self.ensure_one()
        any_selected = False

        def need(sel, celik, paket, label):
            nonlocal any_selected
            if sel:
                any_selected = True
                if not celik or not paket:
                    raise UserError(_("'%s' için Çelik ve Parça Paket Boyu zorunlu.") % label)
                if not self._is_kalip_celigi(celik):
                    raise UserError(
                        _("'%s' için seçtiğiniz Çelik, 'KALIP ÇELİĞİ' kategorisinde olmalıdır.") % label
                    )

        if self.mold_type == 'solid':
            need(self.solid_havuz,   self.solid_havuz_celik,   self.solid_havuz_paket,   "Havuz")
            need(self.solid_destek,  self.solid_destek_celik,  self.solid_destek_paket,  "Destek")
            need(self.solid_kapak,   self.solid_kapak_celik,   self.solid_kapak_paket,   "Kapak")
            need(self.solid_bolster, self.solid_bolster_celik, self.solid_bolster_paket, "Bolster")
        else:
            need(self.portol_kopru,   self.portol_kopru_celik,   self.portol_kopru_paket,   "Köprü")
            need(self.portol_disi,    self.portol_disi_celik,    self.portol_disi_paket,    "Dişi")
            need(self.portol_destek,  self.portol_destek_celik,  self.portol_destek_paket,  "Destek")
            need(self.portol_bolster, self.portol_bolster_celik, self.portol_bolster_paket, "Bolster")

        if not any_selected:
            raise UserError(_("Lütfen en az bir seçenek işaretleyin (Seç)."))

        if self.cap in (None, False):
            raise UserError(_("Çap değeri zorunludur."))

    def _selected_options_summary(self): 
        rows = []
        if self.mold_type == 'solid': 
            data = [
                ('Havuz',   self.solid_havuz,   self.solid_havuz_celik,   self.solid_havuz_paket),
                ('Destek',  self.solid_destek,  self.solid_destek_celik,  self.solid_destek_paket),
                ('Kapak',   self.solid_kapak,   self.solid_kapak_celik,   self.solid_kapak_paket),
                ('Bolster', self.solid_bolster, self.solid_bolster_celik, self.solid_bolster_paket),
            ]
        else:
            data = [
                ('Köprü',   self.portol_kopru,   self.portol_kopru_celik,   self.portol_kopru_paket),
                ('Dişi',    self.portol_disi,    self.portol_disi_celik,    self.portol_disi_paket),
                ('Destek',  self.portol_destek,  self.portol_destek_celik,  self.portol_destek_paket),
                ('Bolster', self.portol_bolster, self.portol_bolster_celik, self.portol_bolster_paket),
            ]
        for name, sel, celik, paket in data:
            if sel:
                rows.append(f"{name}: Çelik={(celik.display_name if celik else '-')}, Parça Paket Boyu={paket or '-'}")
        return "; ".join(rows)
    
    def action_create_product_and_mo(self): 
        self.ensure_one()
        self._validate_selected()

        base = f"{self.kalip_no}-{self.yan_no}-{self.mold_type.upper()}"
        suffix = []
        if self.cap not in (None, False):
            suffix.append(f"Çap={self.cap}")
        if self.takim_paket_boyu:
            suffix.append(f"Takım Paket Boyu={self.takim_paket_boyu}")
        opts = self._selected_options_summary()
        if opts:
            suffix.append(opts)
        product_name = f"{base} [{' | '.join(suffix)}]" if suffix else base

        product = self.env['product.product'].create({
            'name': product_name,
            'type': 'product',
        })

        mo = self.env['mrp.production'].create({
            'product_id': product.id,
            'product_qty': 1.0,
            'product_uom_id': product.uom_id.id,
            'origin': f"Custom Wizard ({self.type_selection})",
        })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Manufacturing Order',
            'res_model': 'mrp.production',
            'view_mode': 'form',
            'res_id': mo.id,
            'target': 'current',
        }

from odoo import fields, models


class StockProductionLot(models.Model):
    _inherit = 'stock.lot'

    x_certificate_no = fields.Char('Sertifika No')
    x_supplier_id = fields.Many2one('res.partner', string='Tedarikçi')
    x_diameter_mm = fields.Integer('Çelik Çapı (mm)')
    x_length_mm = fields.Float('Çelik Boyu (mm)')
    x_scale_weight_kg = fields.Float('Kantar Kilosu (kg)')
    x_note = fields.Text('Açıklama')
    x_certificate_attachment_ids = fields.Many2many(
        'ir.attachment', string='Sertifika Ekleri',
        help='Çeliğe ait sertifika/analiz dosyalarını ekleyin.'
    )
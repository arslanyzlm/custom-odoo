from odoo import fields, models, api

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    x_part_packet_length_mm = fields.Float(
        string='Parça Paket Boyu (mm)',
        related='production_id.x_part_packet_length_mm',
        store=False,
        readonly=True,
    )
    x_component_type = fields.Selection(
        related='production_id.x_component_type',
        store=False,
        readonly=True,
    )
    x_mold_id = fields.Many2one(
        'mold.production',
        string='Kalıp No',
        related='production_id.x_mold_id',
        store=False, readonly=True,
    )
    # x_tool_packet_length_mm = fields.Float(
    #     string='Takım Paket Boyu (mm)',
    #     related='production_id.x_tool_packet_length_mm',
    #     store=False, readonly=True,
    # )
    # ESKİ related yerine compute: önce MO alanı, yoksa kalıp başlığı
    x_tool_packet_length_mm = fields.Float(
        string='Takım Paket Boyu (mm)',
        compute='_compute_mold_extras',
        store=False, readonly=True,
    )

    @api.depends('production_id.x_tool_packet_length_mm',
                 'production_id.x_mold_id.tool_packet_length_mm')
    def _compute_mold_extras(self):
        for wo in self:
            val = wo.production_id.x_tool_packet_length_mm or 0.0
            if not val and wo.production_id.x_mold_id:
                val = wo.production_id.x_mold_id.tool_packet_length_mm or 0.0
            wo.x_tool_packet_length_mm = val

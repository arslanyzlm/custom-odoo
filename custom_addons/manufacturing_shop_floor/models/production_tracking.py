from odoo import models, fields, api

class ManufacturingTimeTracking(models.Model):
    _name = 'manufacturing.time.tracking'
    _description = 'Manufacturing Time Tracking'
    _order = 'start_time desc'

    work_order_id = fields.Many2one('manufacturing.work.order', 'Work Order', required=True, ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True)
    
    start_time = fields.Datetime('Start Time', required=True)
    end_time = fields.Datetime('End Time')
    duration = fields.Float('Duration (hours)', compute='_compute_duration', store=True)
    
    note = fields.Text('Notes')
    
    @api.depends('start_time', 'end_time')
    def _compute_duration(self):
        for record in self:
            if record.start_time and record.end_time:
                delta = record.end_time - record.start_time
                record.duration = delta.total_seconds() / 3600.0
            else:
                record.duration = 0.0
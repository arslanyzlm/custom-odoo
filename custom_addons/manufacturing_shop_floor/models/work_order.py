from odoo import models, fields

class WorkOrder(models.Model):
    _name = 'manufacturing.work.order'
    _description = 'Work Orderss'

    name = fields.Char('Work Orderss', required=True, default='New')
    work_center_id = fields.Many2one('manufacturing.work.center', 'Work Center', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('ready', 'Ready'), 
        ('progress', 'In Progress'),
        ('done', 'Done')
    ], string='Status', default='draft')

# from odoo import models, fields, api
# from datetime import datetime

# class WorkOrder(models.Model):
#     _name = 'manufacturing.work.order'
#     _description = 'Work Order'
#     _order = 'date_planned_start, sequence'
#     _rec_name = 'display_name'

#     name = fields.Char('Work Order', required=True, default='New')
#     display_name = fields.Char('Display Name', compute='_compute_display_name', store=True)
#     sequence = fields.Integer('Sequence', default=10)
    
#     # Relations
#     production_id = fields.Many2one('mrp.production', 'Manufacturing Order', required=True)
#     work_center_id = fields.Many2one('manufacturing.work.center', 'Work Center', required=True)
#     product_id = fields.Many2one('product.product', 'Product', related='production_id.product_id', store=True)
    
#     # State management
#     state = fields.Selection([
#         ('draft', 'Draft'),
#         ('ready', 'Ready'),
#         ('progress', 'In Progress'),
#         ('done', 'Done'),
#         ('cancelled', 'Cancelled')
#     ], string='Status', default='draft', tracking=True)
    
#     # Planning
#     date_planned_start = fields.Datetime('Planned Start')
#     date_planned_end = fields.Datetime('Planned End')
#     duration_expected = fields.Float('Expected Duration (hours)', default=1.0)
    
#     # Actual execution
#     date_start = fields.Datetime('Actual Start')
#     date_end = fields.Datetime('Actual End')
#     duration_real = fields.Float('Real Duration (hours)', compute='_compute_duration_real', store=True)
    
#     # Production quantities
#     qty_production = fields.Float('Production Quantity', related='production_id.product_qty', store=True)
#     qty_produced = fields.Float('Produced Quantity', default=0.0)
#     qty_remaining = fields.Float('Remaining Quantity', compute='_compute_remaining_qty')
    
#     # Workers and tracking
#     employee_ids = fields.Many2many('hr.employee', string='Assigned Employees')
#     current_employee_id = fields.Many2one('hr.employee', 'Current Operator')
    
#     # Notes and instructions
#     note = fields.Html('Instructions')
#     quality_note = fields.Text('Quality Notes')
    
#     # # Time tracking
#     # time_tracking_ids = fields.One2many('manufacturing.time.tracking', 'work_order_id', 'Time Tracking')
#     # total_time_spent = fields.Float('Total Time Spent', compute='_compute_total_time')
    
#     @api.depends('name', 'production_id.name', 'work_center_id.name')
#     def _compute_display_name(self):
#         for record in self:
#             if record.production_id and record.work_center_id:
#                 record.display_name = f"{record.production_id.name} - {record.work_center_id.name}"
#             else:
#                 record.display_name = record.name or 'New'
    
#     @api.depends('date_start', 'date_end')
#     def _compute_duration_real(self):
#         for record in self:
#             if record.date_start and record.date_end:
#                 delta = record.date_end - record.date_start
#                 record.duration_real = delta.total_seconds() / 3600.0
#             else:
#                 record.duration_real = 0.0
    
#     @api.depends('qty_production', 'qty_produced')
#     def _compute_remaining_qty(self):
#         for record in self:
#             record.qty_remaining = record.qty_production - record.qty_produced
    
#     # @api.depends('time_tracking_ids.duration')
#     # def _compute_total_time(self):
#     #     for record in self:
#     #         record.total_time_spent = sum(record.time_tracking_ids.mapped('duration'))
    
#     @api.model
#     def create(self, vals):
#         if vals.get('name', 'New') == 'New':
#             vals['name'] = self.env['ir.sequence'].next_by_code('manufacturing.work.order') or 'New'
#         return super().create(vals)
    
#     def action_start(self):
#         """Start the work order"""
#         self.write({
#             'state': 'progress',
#             'date_start': fields.Datetime.now()
#         })
#         # # Create time tracking entry
#         # self.env['manufacturing.time.tracking'].create({
#         #     'work_order_id': self.id,
#         #     'employee_id': self.current_employee_id.id,
#         #     'start_time': fields.Datetime.now(),
#         # })
    
#     def action_pause(self):
#         """Pause the work order"""
#         # End current time tracking
#         # current_tracking = self.time_tracking_ids.filtered(lambda t: not t.end_time)
#         # if current_tracking:
#         #     current_tracking.write({'end_time': fields.Datetime.now()})

#         # For now, just a notification
#         return {
#             'type': 'ir.actions.client',
#             'tag': 'display_notification',
#             'params': {
#                 'title': 'Work Order Paused',
#                 'message': f'Work order {self.name} has been paused',
#                 'type': 'warning',
#             }
#         }
    
#     # def action_resume(self):
#     #     """Resume the work order"""
#     #     # Create new time tracking entry
#     #     self.env['manufacturing.time.tracking'].create({
#     #         'work_order_id': self.id,
#     #         'employee_id': self.current_employee_id.id,
#     #         'start_time': fields.Datetime.now(),
#     #     })
    
#     def action_complete(self):
#         """Complete the work order"""
#         # # End current time tracking
#         # current_tracking = self.time_tracking_ids.filtered(lambda t: not t.end_time)
#         # if current_tracking:
#         #     current_tracking.write({'end_time': fields.Datetime.now()})
        
#         self.write({
#             'state': 'done',
#             'date_end': fields.Datetime.now(),
#             'qty_produced': self.qty_production  # Default to full quantity
#         })
    
#     # def action_set_quantity(self, quantity):
#     #     """Update produced quantity"""
#     #     self.qty_produced = quantity

#     def action_set_ready(self):
#         """Set work order to ready state"""
#         self.write({'state': 'ready'})
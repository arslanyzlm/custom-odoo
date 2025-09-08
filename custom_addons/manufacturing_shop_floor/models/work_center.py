from odoo import models, fields, api

class WorkCenter(models.Model):
    _name = 'manufacturing.work.center'
    _description = 'Work Center'
    _order = 'sequence, name'

    name = fields.Char('Work Center Name', required=True)
    code = fields.Char('Code', required=True)
    sequence = fields.Integer('Sequence', default=10)
    
    # Capacity and efficiency
    capacity = fields.Float('Capacity', default=1.0)
    time_efficiency = fields.Float('Time Efficiency (%)', default=100.0)
    costs_hour = fields.Float('Cost per Hour', default=0.0)
    
    # Working time
    resource_calendar_id = fields.Many2one('resource.calendar', 'Working Time')
    
    # Status and info
    active = fields.Boolean('Active', default=True)
    color = fields.Integer('Color', default=1)
    description = fields.Text('Description')
    note = fields.Html('Notes')

    # Related work orders - now properly linked
    work_order_ids = fields.One2many('manufacturing.work.order', 'work_center_id', 'Work Orders')
    current_work_order_ids = fields.One2many('manufacturing.work.order', 'work_center_id', 
                                            'Current Work Orders', 
                                            domain=[('state', 'in', ['ready', 'progress'])])
    
    # Simple fields for now (no relations to non-existent models)
    work_order_count = fields.Integer('Work Orders', compute='_compute_work_order_count')
    current_work_order_count = fields.Integer('Active Work Orders', compute='_compute_work_order_count') #fields.Integer('Work Orders', default=0)
    # current_work_order_count = fields.Integer('Active Work Orders', default=0)

    @api.depends('work_order_ids', 'current_work_order_ids')
    def _compute_work_order_count(self):
        for record in self:
            record.work_order_count = len(record.work_order_ids)
            record.current_work_order_count = len(record.current_work_order_ids)

    def action_view_work_orders(self):
        """Action to view work orders for this work center"""
        # return {
        #     'type': 'ir.actions.client',
        #     'tag': 'display_notification',
        #     'params': {
        #         'title': 'Work Orders',
        #         'message': f'Work orders for {self.name} - Coming soon!',
        #         'type': 'info',
        #     }
        # }
        return {
            'type': 'ir.actions.act_window',
            'name': f'Work Orders - {self.name}',
            'res_model': 'manufacturing.work.order',
            'view_mode': 'list,form',
            'domain': [('work_center_id', '=', self.id)],
            'context': {'default_work_center_id': self.id},
            'target': 'current',
        }
    
    def action_open_shop_floor(self):
        """Open shop floor interface for this work center"""
        # return {
        #     'type': 'ir.actions.client',
        #     'tag': 'display_notification',
        #     'params': {
        #         'title': 'Shop Floor',
        #         'message': f'Shop floor for {self.name} - Coming soon!',
        #         'type': 'info',
        #     }
        # }
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Shop Floor',
                'message': f'Shop floor for {self.name} - Coming soon!',
                'type': 'info',
            }
        }
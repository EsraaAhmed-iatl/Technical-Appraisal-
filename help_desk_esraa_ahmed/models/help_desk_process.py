
from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError


TICKET_PRIORITY = [
    ('1', 'Low'),
    ('2', 'Medium'),
    ('3', 'High'),
]
class HdTickit(models.Model):
    _name = 'hd.ticket'

    tickit_id = fields.Char(string='Ticket ID')
    name = fields.Text(string='Ticket ID')
    time_submitted = fields.Date(string='Time Submitted')
    time_submitted = fields.Date(string='Time Submitted',states={'solved': [('readonly', True)]})
    description = fields.Text(string='Description', help='description of issue', required=True)
    user_id = fields.Many2one('res.users', string='Assigned to')
    priority = fields.Selection(TICKET_PRIORITY, string='Priority', default='0')
    partner_id = fields.Many2one('res.partner', string="Customer", required=True)
    customer_name =fields.Char(related='partner_id.name', store=True)
    customer_email =fields.Char(related='partner_id.email')
    customer_phone =fields.Char(related='partner_id.phone')
    tag_ids = fields.Many2many('hd.tag', string='tags', track_visibility='onchange')
    hosting_type = fields.Selection([('on-premise', 'on-premise'),
                                  ('cloud', 'Cloud'), ], string='Hosting type',
                                 required=True, default='on-premise')
    server_url =fields.Char(string='Server URL')
    # resolution_time = fields.Float(string='Resolution time',readonly=True,compute='_compute_resolution_time',
    #                                 help="Total amount po time that the issue was taken to be solved.")
    state = fields.Selection([('draft', 'New'),
                              ('in_progress', 'In Progress'),
                              ('solved', 'Solved'),
                              ('cancel', 'Cancel'), ], string='State',
                              copy=False, default='draft',
                              track_visibility='onchange')

    @api.depends('time_submitted')
    def _compute_resolution_time(self):
        for rec in self:
            test=0

    def unlink(self):
        res =super(HdTickit, self).unlink()
        tickit_obj = self.env['hd.ticket']
        ability_deletion = tickit_obj.search([('state', ' not in', 'draft')])
        if ability_deletion:
            raise Warning(_("You are trying to delete a record that is not draft!"))
        return res

    # def write(self, vals):
    #     res = super(HdTickit, self).write(vals)
    #     if any(state == 'solved' for state in set(self.mapped('state'))):
    #         raise UserError(_("No edit in solved state"))
    #     else:
    #         return res

    def set_to_in_progress(self):
        self.state = 'in_progress'

    def set_to_solved(self):
        self.state = 'solved'

    def set_to_draft(self):
        self.state = 'draft'

    def action_cancel(self):
        self.state = 'cancel'


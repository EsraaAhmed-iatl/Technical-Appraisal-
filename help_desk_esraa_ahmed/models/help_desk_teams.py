from odoo import models, fields, api
# from odoo.exceptions import UserError, ValidationError

class HdTeam(models.Model):
    _name = 'hd.team'

    name = fields.Char(string='Help Desk Team')

class HdTeam(models.Model):
    _name = 'hd.tag'

    name = fields.Char(string='Help Desk Tags')
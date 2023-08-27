from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    auth_token = fields.Char(string='auth_token')

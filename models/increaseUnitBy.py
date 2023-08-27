from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError

class Pricelist(models.Model):
    _inherit = "product.pricelist.item"
    increase_unit_by  = fields.Integer(string='Increase By')
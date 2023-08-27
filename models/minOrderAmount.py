from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    customer_order_val = fields.Integer(string="customer order amount",config_parameter='cspl_eccomerce_api.customer_order_val')
    vendor_order_val = fields.Integer(string='vendore order amount',config_parameter='cspl_eccomerce_api.vendor_order_val')
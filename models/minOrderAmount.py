from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    customer_order_val = fields.Integer(string="customer order amount",config_parameter='cspl_eccomerce_api.customer_order_val')
    vendor_order_val = fields.Integer(string='vendore order amount',config_parameter='cspl_eccomerce_api.vendor_order_val')
    notify_cart_after = fields.Integer(
        string='Notify Cart After',
        default=10,
        config_parameter='cspl_eccomerce_api.notify_cart_after'
    )
    discount_on_abandoned_cart = fields.Integer(
        string='Discount ON ABandoned Cart',
        default=0,
        config_parameter='cspl_eccomerce_api.discount_on_abandoned_cart'
    )
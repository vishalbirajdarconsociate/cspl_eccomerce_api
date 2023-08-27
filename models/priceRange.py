from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    # _description = 'Product Template'
    product_price_range_ids = fields.One2many('product.price.range', 'product_id', string='Price range')


class ProductPriceRange(models.Model):
    _name = "product.price.range"
    product_id = fields.Many2one('product.template', string='product', required=True, ondelete='cascade', index=True)
    min_qty = fields.Integer(string='Min Qty',)
    max_qty = fields.Integer(string='Max Qty',)
    price_for_range = fields.Float(string='Price per unit')
    
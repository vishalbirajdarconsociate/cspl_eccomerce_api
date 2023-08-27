# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    @api.constrains('weight')
    def _check_weight(self):
        for record in self:
            if record.weight <= 0:
                raise ValidationError("Weight must be greater than zero.")
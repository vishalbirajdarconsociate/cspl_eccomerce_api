# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime,timedelta

class cspl_eccomerce_api(models.Model):
    _name = 'cspl_eccomerce_api.banners'
    _description = 'CSPL Eccomerce Api'

    name = fields.Char("Name",required=True)
    image = fields.Image("Banner",attachment=True)
    description = fields.Char("Description")
    lang_id = fields.Many2one(
        string='Language',
        comodel_name='res.lang',
        ondelete='restrict',
    )
    
    is_active = fields.Boolean("Active", default=False)
    @api.model
    def create(self, vals):
        print(self.id)
        data=super().create(vals)
        attachment_obj = self.env['ir.attachment']
        print(data.id)
        attachment_values = {
            'name': vals.get('image_filename', 'image.png'),
            'datas': vals.get('image'),
            'res_model': 'cspl_eccomerce_api.banners',
            'res_id': data.id,
            'type': 'binary',
            'public': True
        }
        attachment_obj.create(attachment_values)
        return data
    
    def write(self, vals):
        data=super().write(vals)
        attachment_obj = self.env['ir.attachment'].sudo().search([('res_model', '=', 'cspl_eccomerce_api.banners'),('res_id','=',self.id)])
        attachment_values = {
            'datas':  vals.get('image') if vals.get('image') else self.image,
            'public': True
        }
        attachment_obj.write(attachment_values)
        return data
    
    @api.model
    def notify_abandom_cart(self):
        for order in self.env["sale.order"].search([]):
            if order.state == 'draft' and order.date_order:
                public_partner_id = order.website_id.user_id.partner_id
                abandoned_delay =self.env['ir.config_parameter'].sudo().get_param('cspl_eccomerce_api.notify_cart_after') or 1.0
                abandoned_datetime = datetime.utcnow() - order.create_date
                abandoned_delay=timedelta(hours=int(abandoned_delay))
                # print(abandoned_delay,"|",abandoned_datetime)
                if abandoned_datetime>=abandoned_delay:
                    order.sudo().write({'is_abandoned_cart' : True})
                    # print("Abandoned") if order.cart_recovery_email_sent else order._cart_recovery_email_send()
                    if order.cart_recovery_email_sent:
                        print("Abandoned")
                    else:
                        order._cart_recovery_email_send()
                        discount_percentage=self.env['ir.config_parameter'].sudo().get_param('cspl_eccomerce_api.discount_on_abandoned_cart')
                        for line in order.order_line:
                            if discount_percentage:
                                line.write({'discount': discount_percentage})
                else:
                    order.sudo().write({'is_abandoned_cart' : False})
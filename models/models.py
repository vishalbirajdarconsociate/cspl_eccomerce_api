# -*- coding: utf-8 -*-

from odoo import models, fields, api


class cspl_eccomerce_api(models.Model):
    _name = 'cspl_eccomerce_api.banners'
    _description = 'cspl_eccomerce_api.banners'

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
    
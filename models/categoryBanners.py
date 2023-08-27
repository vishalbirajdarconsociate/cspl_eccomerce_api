
from odoo import fields, models, api


class ProductCategory(models.Model):
    _name = "product.category"
    _inherit = [_name, "image.mixin"]
    image = fields.Image(string="Category Image", attachment=True)
    banner = fields.Image(string="Category Banner", attachment=True)
    @api.model
    def create(self, vals):
        print(self.id)
        data=super().create(vals)
        attachment_obj = self.env['ir.attachment']
        print(data.id)
        attachment_values = {
            'name': 'category_image',
            'datas': vals.get('image'),
            'res_model': 'product.category',
            'res_id': data.id,
            'type': 'binary',
            'public': True
        }
        attachment_obj.create(attachment_values)
        
        attachment_values = {
            'name': 'category_banner',
            'datas': vals.get('banner'),
            'res_model': 'product.category',
            'res_id': data.id,
            'type': 'binary',
            'public': True
        }
        attachment_obj.create(attachment_values)
        return data
    
    def write(self, vals):
        data=super().write(vals)
        attachment_image = self.env['ir.attachment'].sudo().search([('res_model', '=', 'product.category'),('name','=','category_image'),('res_id','=',self.id)])
        attachment_values = {
            'datas': vals.get('image'),
            'public': True
        }
        attachment_image.write(attachment_values)
        
        attachment_banner = self.env['ir.attachment'].sudo().search([('res_model', '=', 'product.category'),('name','=','category_banner'),('res_id','=',self.id)])
        attachment_values = {
            'datas': vals.get('banner'),
            'public': True
        }
        attachment_banner.write(attachment_values)
        return data

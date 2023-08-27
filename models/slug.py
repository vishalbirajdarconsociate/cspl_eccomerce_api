from odoo import models, fields, api

class ProductCategory(models.Model):
    _inherit = 'product.category'
    slug = fields.Char(string='Slug', compute='_compute_slug', store=True)
    @api.depends('name')
    def _compute_slug(self):
        for category in self:
            data=str(category.name).lower()
            data=data.replace('/', '')
            data=data.replace('?', '')
            category.slug = "-".join(data.split(" "))

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    slug = fields.Char(string='Slug', compute='_compute_slug', store=True)
    @api.depends('name')
    def _compute_slug(self):
        for product in self:
            data=str(product.name).lower()
            data=data.replace('/', '')
            data=data.replace('?', '')
            product.slug = "-".join(data.split(" "))


class BlogPost(models.Model):
    _inherit = 'blog.post'
    slug = fields.Char(string='Slug', compute='_compute_slug', store=True)
    @api.depends('name')
    def _compute_slug(self):
        for blog in self:
            data=str(blog.name).lower()
            data=data.replace('/', '')
            data=data.replace('?', '')
            blog.slug = "-".join(data.split(" "))    

class Blog(models.Model):
    _inherit = 'blog.blog'
    slug = fields.Char(string='Slug', compute='_compute_slug', store=True)
    @api.depends('name')
    def _compute_slug(self):
        for blog_category in self:
            data=str(blog_category.name).lower()
            data=data.replace('/', '')
            data=data.replace('?', '')
            blog_category.slug = "-".join(data.split(" "))
# -*- coding: utf-8 -*-

import math
from odoo.addons.web.controllers.main import Session
import requests
import json
from odoo import http,fields
from odoo.http import request
from datetime import timedelta, date, datetime
import dateutil.relativedelta
from dateutil.relativedelta import relativedelta
import random
import string
from werkzeug.exceptions import BadRequest
# class InheritSession(Session):
#     @http.route('/web/session/authenticate', auth='public', type='json', csrf=False, cors='*')
#     def authenticate(self, db, login, password, **kw):
#         res = super(InheritSession, self).authenticate(db, login, password, **kw)
#         return res
    

class CsplEccomerceApi(http.Controller):
    
######################### User Management ############################### 
    @http.route('/api/saudi_states', type='json', auth='public', csrf=False, cors='*')
    def saudi_states(self):
        try:
            country_code = 'SA'
            saudi_states = request.env['res.country.state'].sudo().search([('country_id.code', '=', country_code)])
            state_names = [{"label":state.name,"value":state.name} for state in saudi_states]
            return {'states': state_names}
        except Exception as e:
            error_message = str(e)
            return {'error': error_message}
    def user_info(self, user):
        return { 'user': {
                        "id":user.id
                        ,"name":user.name
                        ,"email":user.email
                        ,"phone":user.phone
                        ,'auth_token':user.auth_token
                        ,"published":user.is_published
                        ,"image":f"/web/image?model=res.partner&id={user.id}&field=avatar_128"
                        }}
    @http.route('/api/login', type='json', auth='public', csrf=False, cors='*')
    def login(self,phone=None):
        User = request.env['res.partner']
        if User.sudo().search(['|',('phone','=',phone),('email','=',phone)]):
            user = User.sudo().search(['|',('phone','=',phone),('email','=',phone)], limit=1)
            user.sudo().write({"auth_token":f"{user.id}{''.join(random.choice(string.ascii_letters) for i in range(16))}"})
            return {'message': 'Login successfully'
                    , 'user': {
                        "id":user.id
                        ,"name":user.name
                        ,"email":user.email
                        ,"phone":user.phone
                        ,'auth_token':user.auth_token
                        ,"image":f"/web/image?model=res.partner&id={user.id}&field=avatar_128"
                        }}
        else:
            return {'error': "Invalid credentials"}
        
    @http.route('/api/registerUsers', type='json', auth='public', csrf=False, cors='*')
    def create_user(self,fname,lname,email,phone, **kw):
        User = request.env['res.partner']
        try:
            # if User.sudo().search([('phone','=',phone)]):
            if User.sudo().search(['|',('phone','=',phone),('email','=',email)]):
                return "user ealready exist"
            user = User.sudo().create({
                'name': f"{fname} {lname}",
                "email": email,
                "phone": phone,
            })
            user.sudo().write({"auth_token":f"{user.id}{''.join(random.choice(string.ascii_letters) for i in range(7))}"})
            return {'message': 'cutomer created successfully'
                    , 'user': {
                        "id":user.id
                        ,"name":user.name
                        ,"email":user.email
                        ,"phone":user.phone
                        ,'auth_token':user.auth_token
                        }}
        except KeyError as e:
            return {'error': f'Missing key: {e}'}

    @http.route('/api/customer_orders', type='json', auth='public', csrf=False, cors='*')
    def customer_orders(self, customer_id=None, **kwargs):
        try:
            customer_orders = request.env['sale.order'].sudo().search([
                ('partner_id', '=', customer_id),
                ('state', '=', 'sale'),
            ])
            orders=[self.get_origin_info(i) for i in customer_orders]
            return {'orders': orders}
        except Exception as e:
            return {'error': str(e)}

    @http.route('/api/customer_address', type='json', auth='public', csrf=False, cors='*')
    def customer_address(self, customer_id, customer_token, address_data={},update=False):
        try:
            partner = request.env['res.partner'].sudo().search([('id','=',customer_id),('auth_token','=',customer_token)])
            if partner:
                if update:
                    address={
                            "street": address_data['street'],
                            "street2": address_data['street2'],
                            "city": address_data['city'],
                            "zip": address_data['zip'],
                            "country_id": request.env['res.country'].sudo().search([("name","=",address_data['country'])]).id,
                            "state_id": request.env['res.country.state'].sudo().search([("name","like",address_data['state'])]).id,
                            }
                    partner.sudo().write(address)
                return {'message': 'Address updated or added successfully' if update else 'address of user '+partner.name+''
                        ,'address': {
                            "street": partner.street,
                            "street2": partner.street2,
                            "city": partner.city,
                            "zip": partner.zip,
                            "country_id": partner.country_id.name,
                            "state_id": partner.state_id.name
                        }}
            else:
                return {'error': 'Customer not found'}
        except Exception as e:
            return {'error': str(e)}
        
    @http.route('/api/customer_info', type='json', auth='public', csrf=False, cors='*')
    def customer_info(self,customer_id=None,customer_token=None,update=False,**kw):
        try:
            partner = request.env['res.partner'].sudo().search([('id','=',customer_id),],limit=1)
            if update :
                # if request.env['res.partner'].sudo().search([('email','=',kw.get('email')),],limit=1) and kw.get('email') != partner.email:
                #     return {'massage':'email already in use'}
                # elif request.env['res.partner'].sudo().search([('phone','=',kw.get('phone')),],limit=1) and kw.get('phone') != partner.phone:
                    # return {'massage':'number already in use'}
                data={
                    "name":kw.get('name') or partner.name,
                    "email":kw.get('email') or partner.email,
                    "phone":kw.get('phone') or partner.phone,
                    "mobile":kw.get('phone') or partner.mobile,
                    "avatar_1920":kw.get('avatar') or partner.avatar_1920,
                    "image_1920":kw.get('avatar') or partner.image_1920,
                    "profile_image":kw.get('avatar') or partner.profile_image,
                    "is_published":True
                    }
                print(data)
                partner.sudo().write(data)
            return self.user_info(partner)
        except Exception as e:
            return {'error':e}
        
    @http.route('/api/logout', type='json', auth='public', csrf=False, cors='*')
    def logout(self, customer_id,customer_token):
        partner = request.env['res.partner'].sudo().search([('id','=',customer_id),('auth_token','=',customer_token)])
        if partner:
            partner.sudo().write({"auth_token":""})
            return "Success"
        else:
            # raise BadRequest('Failure')
            return {'error': 'Failure',"partner":'user not found'}


#########################################################################


    def get_rating(self,product):
        reviews=[review.rating for review in request.env['user.review'].search([('template_id.id','=',product.id)])]
        return {
                "rating":sum(reviews)/len(reviews) if len(reviews) > 0 else 0,
                "count":len(reviews)
                }
    def get_price_range(self, product):
        return [
            {
                "minQuantity":range.min_qty,
                "maxQuantity":range.max_qty,
                "price":range.price_for_range
            } for range in product.sudo().product_price_range_ids
        ]
    def get_min_qty(self, product):
        pricelist_items = request.env['product.pricelist.item'].sudo().search([
                ('product_tmpl_id', '=', product.id),
                ('pricelist_id', '=', 1)
            ],limit=1)
        return pricelist_items.min_quantity

    def get_prod_data(self,product):
        return {
            'products': [{
                "productId":i.id,
                "productName":i.name,
                "productSlug":i.slug,
                "productImage":'/web/image?model=product.template&id=' + str(i.id) + '&field=image_128',
                "currency":i.currency_id.name,
                "price":i.list_price,
                "compare_list_price":i.compare_list_price,
                "rating":self.get_rating(i),
                "productStock":i.sudo().qty_available,
                "minQuantity":self.get_min_qty(i) if self.get_min_qty(i) else i.min_order_qty,
                # "increaseBy":1,
                "increaseBy":request.env['product.pricelist.item'].sudo().search([('product_tmpl_id', '=', i.id),('pricelist_id', '=', 1)],limit=1).increase_unit_by if request.env['product.pricelist.item'].sudo().search([('product_tmpl_id', '=', i.id),('pricelist_id', '=', 1)],limit=1).increase_unit_by >0 else 1,
                "category":{
                    "id":i.categ_id.id,
                    "name":i.categ_id.name,
                    "display_name":i.categ_id.display_name,
                    "slug":i.categ_id.slug
                    },
                "tags":[ {"id":tag.id,"tagName":tag.name} for tag in i.product_tag_ids ],
                "priceRange":self.get_price_range(i)
                # "images":[f"/web/image/product.image/{img.id}/image_1024/" for img in request.env['product.image'].search([('product_tmpl_id.id','=',i.id)])]
                } for i in product]
                }

    @http.route('/api/categoryList', auth='public', type='json', csrf=False, cors='*')
    def categoryList(self,lang=None,uid=None):
        ProductCategory = request.env['product.category'].with_context(lang=lang)
        service_categories = ProductCategory.sudo().search([('name', 'ilike', 'Service')])
        categories = ProductCategory.search([("parent_id","=",False),("id","not in",service_categories.ids)])
        data=[ 
            {
            "categoryId":i.id,
             "categoryName":i.name,
             "categorySlug":i.slug,
             "categoryImage":'/web/image?model=product.template&id=' + str(request.env['product.template'].search([('categ_id.id', '=', i.id)],limit=1).id) + '&field=image_128'
             } for i in categories 
        ]
        return ({"categories":data})


    @http.route('/api/categoryProduct' , auth='public', type='json', csrf=False, cors='*')
    def categoryProduct(self,lang='en_US',uid=None,category=None, slug=None,sort=None,minPrice=0,maxPrice=100000,tags=[],limit=12,page=1):
        ProductCategory = request.env['product.category'].with_context(lang=lang)
        service_categories = ProductCategory.sudo().search([("id","=",category) if category else ("slug","=",slug)],limit=1)
        products = request.env['product.template'].with_context(lang=lang)
        if sort=="latest":
             sortVal = 'create_date desc'
        elif sort=="top":
             sortVal ='sales_count desc'
        elif sort=="popular":
             sortVal = 'rating_avg desc'
        elif sort=="price_high_to_low":
             sortVal = 'list_price desc'
        elif sort=="price_low_to_high":
             sortVal = 'list_price'
        else:
             sortVal = 'id desc'
        slug_or_id=("categ_id","=",category) if category else ("categ_id.slug","=",slug)
        if len(tags)>0:
            products = products.search([("image_128","!=",False) ,("type","=","product"),slug_or_id,("list_price", ">=", minPrice),("list_price", "<=", maxPrice),('product_tag_ids','in',tags)])
        else:
            products = products.search([("image_128","!=",False) ,("type","=","product"),slug_or_id,("list_price", ">=", minPrice),("list_price", "<=", maxPrice)])
        current_page=(page-1)*limit
        total_records=len(products)
        total_pages=(total_records // limit) +  (1 if total_records % limit > 0 else 0)
        allData=products.search([("image_128","!=",False) ,("type","=","product"),slug_or_id])
        print(allData.mapped('product_tag_ids'))
        if len(tags)>0:
            result=self.get_prod_data(products.search([("image_128","!=",False) ,("type","=","product"),slug_or_id,("list_price", ">=", minPrice),("list_price", "<=", maxPrice),('product_tag_ids','in',tags)],order= sortVal,limit=limit, offset=current_page))
        else:
            result=self.get_prod_data(products.search([("image_128","!=",False) ,("type","=","product"),slug_or_id,("list_price", ">=", minPrice),("list_price", "<=", maxPrice)],order= sortVal,limit=limit, offset=current_page))
        result['total_records']=total_records
        result['highestPrice'] =max(allData.mapped('list_price'))
        result['current_page']=page
        result['elements']=f"{current_page+1}-{current_page+limit if limit==len(result['products']) else current_page+len(result['products'])}" if result['products'] else "0-0"
        result['total_pages']=total_pages
        result["tags"]=[ {"id":tag.id,"tagName":tag.name} for tag in allData.mapped('product_tag_ids')]
        data =request.env["cspl_eccomerce_api.banners"].sudo().search([('is_active','=',True),('lang_id.code','=',lang)])
        result['category_banners']=[ f"/web/image/{request.env['ir.attachment'].sudo().search([('res_model', '=', 'cspl_eccomerce_api.banners'), ('res_id', '=', i.id)], limit=1).id}" for i in data]
        result['category_name']=service_categories.name
        return result






    @http.route('/api/homePage', auth='user', type='json' ,csrf=False, cors='*')
    def homePage(self,uid=None):
        Attachment = request.env['ir.attachment']
        website_banners = Attachment.sudo().search([('website_id', '!=', False),('type','=', 'binary')])
        banners=[i.local_url for i in website_banners if (i.local_url).__contains__('13728') or  (i.local_url).__contains__('13730') ]
        footer={}
        brands=[{"id":i.id,"name":i.display_name,"image":i.logo} for i in  request.env['product.brand'].search([])]
        return { 
                "banners":banners,
                "footer":footer,
                "brands":brands
                }

    @http.route('/api/langCodeList', auth='public', type='json' ,csrf=False, cors='*')
    def langCodeList(self,uid=None):
        IrQweb = request.env['res.lang']
        active_languages = IrQweb.sudo().search([('active', '=', True)])

        language_codes = [{"tittle":lang.name,"code":lang.code} for lang in active_languages]

        return language_codes


    @http.route('/api/prod_filter', type='json', auth='public', csrf=False, cors='*')
    def prod_filter(self,sort=None,lang='en_US' ,uid=None,all=False,latest=False,top=False,rating=False,search=None,minPrice=0,maxPrice=100000,tags=[],limit=12,page=1):
        products = request.env['product.template'].with_context(lang=lang)
        if latest:
             sortVal = 'create_date desc'
        elif top:
             sortVal ='sales_count desc'
        elif rating:
             sortVal = 'rating_avg '
        else:
            if all or search:
                if sort=="latest":
                    sortVal = 'create_date desc'
                elif sort=="top":
                    sortVal ='sales_count desc'
                elif sort=="popular":
                    sortVal = 'rating_avg desc'
                elif sort=="price_high_to_low":
                    sortVal = 'list_price desc'
                elif sort=="price_low_to_high":
                    sortVal = 'list_price'
                else:
                    sortVal = 'id desc'
            else:
             sortVal = 'id desc'
        domain=[("image_128","!=",False),('is_published','=',True),("type","=","product"),("list_price", ">=", minPrice),("list_price", "<=", maxPrice)]
        if search:
            domain.append(("name","ilike",search))
        if len(tags)>0:
            domain.append(('product_tag_ids','in',tags))
        products = products.search(domain)
        current_page=(page-1)*limit
        total_records=len(products)
        total_pages=(total_records // limit) +  (1 if total_records % limit > 0 else 0)
        result=self.get_prod_data(products.search(domain,order= sortVal,limit=limit, offset=current_page))
        result['total_records']=total_records
        result['highestPrice'] =max(products.mapped('list_price'))
        result['current_page']=page
        result['total_pages']=total_pages
        result["tags"]=[ {"id":tag.id,"tagName":tag.name} for tag in products.mapped('product_tag_ids')]
        result['elements']=f"{current_page+1}-{current_page+limit if limit==len(result['products']) else current_page+len(result['products'])}" if result['products'] else "0-0"
        return result



    @http.route('/api/banners', type='json', auth='public', csrf=False, cors='*',website=True)
    def banners(self,lang='en_US' ,uid=None):
        data =request.env["cspl_eccomerce_api.banners"].sudo().search([('is_active','=',True),('lang_id.code','=',lang)])
        return [
            {
                "image":f"/web/image/{request.env['ir.attachment'].sudo().search([('res_model', '=', 'cspl_eccomerce_api.banners'), ('res_id', '=', i.id)], limit=1).id}"
                ,"title":i.name
                ,"subtitle":i.description
                ,"language":i.lang_id.code
            }
                for i in data]

    def top_selling_product_rank(self, product_id):
        try:
            # Query the top selling products
            products = request.env['product.template'].sudo().search([
                ("image_128", "!=", False),
                ('is_published', '=', True),
                ('type', '=', 'product')
            ], order='sales_count desc')
            product_data = [{'product_id': p.id, 'sales_count': p.sales_count} for p in products]
            rank = next((index + 1 for index, item in enumerate(product_data) if item['product_id'] == product_id), None)

            response_data = {'top_selling_products': product_data, 'product_rank': rank}
            return rank

        except Exception as e:
            response_data = {'error': str(e)}
            return {}
            # return request.make_response(json.dumps(response_data), headers={'Content-Type': 'application/json'}, status=500)
    
    def get_all_prod_data(self,product_id):
        data={
         "Color":product_id.color if product_id.color>0 else "",
         "Seller":product_id.responsible_id.name,
         "Included Components":"No",
         "Category":product_id.categ_id.name,
         "Manufacturer/Seller":product_id.marketplace_seller_id.name,
         "Dimension":f"{product_id.weight} {product_id.weight_uom_name}",
         "SKU":product_id.default_code,
         "Date First Available":product_id.create_date,
         "Best Sellers Rank":f"#{self.top_selling_product_rank(product_id.id)} in {product_id.categ_id.name}",
         "Lead Time":product_id.sale_delay,
         "Ship from":product_id.property_stock_production.name,
         "Fulfilled by":product_id.responsible_id.name,
         "Carton Packings":f"{product_id.min_order_qty} {product_id.uom_name}",
        }
        try:
            data["Brand"]=product_id.product_brand_id.name if product_id.product_brand_id.name else ""
        except :
            pass
        
        return data
        
    @http.route('/api/singleProductData', type='json', auth='public', csrf=False, cors='*')
    def singleProductData(self,lang='en_US' ,uid=None,pid=None,slug=None,):
        product = request.env['product.template'].with_context(lang=lang).sudo().search([('id','=',pid)]) or request.env['product.template'].with_context(lang=lang).sudo().search([('slug','=',slug)])
        data={}
        for prod in product:
            data['productId'] = prod.id
            data['productName']=prod.name
            data['shortDescription']=prod.description_sale if prod.description_sale else ""
            data['description']=prod.website_description
            data['productSlug']=prod.slug
            data["price"]=prod.list_price
            data["priceRange"]=self.get_price_range(prod)
            data['rating']=self.get_rating(prod)
            data['productStock']=prod.sudo().qty_available
            data["productImage"]='/web/image?model=product.template&id=' + str(prod.id) + '&field=image_128'
            data["minQuantity"]=self.get_min_qty(prod) if self.get_min_qty(prod) else prod.min_order_qty
            data["increaseBy"]=request.env['product.pricelist.item'].sudo().search([('product_tmpl_id', '=', prod.id),('pricelist_id', '=', 1)],limit=1).increase_unit_by if request.env['product.pricelist.item'].sudo().search([('product_tmpl_id', '=', prod.id),('pricelist_id', '=', 1)],limit=1).increase_unit_by >0 else 1
            price_with_taxes = prod.list_price
            if prod.taxes_id:
                for tax in prod.taxes_id:
                    price_with_taxes *= (1 + (tax.amount / 100))
            data["price_tax_include"]=price_with_taxes
            data["tags"]=[{"id":tag.id,"tagName":tag.name} for tag in prod.product_tag_ids]
            data['compare_price']=prod.compare_list_price
            data["currency"]=prod.currency_id.name
            images=[f"/web/image/product.image/{img.id}/image_1024/" for img in request.env['product.image'].search([('product_tmpl_id.id','=',prod.id)])]
            data["images"]=images if len(images)>0 else ['/cspl_eccomerce_api/static/src/img/default-img.png']
            data['taxes']=[{'id':tax.id,"name":tax.name,'amount':tax.amount} for tax in prod.taxes_id]
            data["category"]={
                    "id":prod.categ_id.id,
                    "name":prod.categ_id.name,
                    "display_name":prod.categ_id.display_name,
                    "slug":prod.categ_id.slug
                    },
            data['table']=self.get_all_prod_data(prod)
        return data
    


######################## reviews #################################
    @http.route('/api/ProductReview', type='json', auth='public', csrf=False, cors='*')
    def ProductReview(self,lang='en_US' ,uid=None,pid=None,slug=None):
        product = request.env['product.template'].with_context(lang=lang).sudo().search([('id','=',pid)]) or request.env['product.template'].with_context(lang=lang).sudo().search([('slug','=',slug)])
        review=[
            {"name":review.customer,
             "title":review.title,
            "massage":review.msg,
            "rating":review.rating, 
            "date":review.create_date}
            for review in request.env['user.review'].search([('template_id.id','=',product.id)])
            ]
        return {
            "product": product.id,
            "slug": product.slug,
            "category": product.categ_id.slug,
            "review": review
        }
    @http.route('/api/createProductReview', type='json', auth='public', csrf=False, cors='*')
    def createProductReview(self,lang='en_US' ,uid=None,product_id=None,slug=None,customer_id=None,):
        order_lines = request.env['sale.order.line'].sudo().search([
                ('order_id.partner_id', '=', customer_id),
                ('product_template_id', '=', product_id),
            ])
        if order_lines.id:
            pass
        return order_lines.id
########################################################################
        
    @http.route('/api/RelatedProducts', type='json', auth='public', csrf=False, cors='*')
    def RelatedProducts(self,lang='en_US' ,uid=None,pid=None,slug=None,limit=10):
        productsData = request.env['product.template'].with_context(lang=lang)
        product = productsData.sudo().search([('id','=',pid)]) or productsData.sudo().search([('slug','=',slug)])
        # print(product.categ_id)
        data=self.get_prod_data(productsData.sudo().search([('categ_id.id', '=', product.categ_id.id),('id','!=',product.id)],limit=limit))
        return data
   
   
################ wish list #################
    @http.route('/api/get/paymentterms', auth='public', type='json',csrf=False, cors='*')
    def showWishList(self,customer_id=None,customer_token=None): 
        User = request.env['res.partner'].sudo().search([('id','=',customer_id),('auth_token','=',customer_token)])
        if User:
            return "wishlist"
        else:
            return "not found"
############################################


    @http.route('/api/get/paymentterms', auth='public', type='json',csrf=False, cors='*')
    def getPaymentTerms(self):
        payment_term = request.env['account.payment.term'].sudo().search([]).read(['name'])
        return payment_term
    
    
##################### order api ########################
    def get_min_order_amount(self):
        return request.env['ir.config_parameter'].sudo().get_param('cspl_eccomerce_api.customer_order_val')
    def get_invoices_url(self,order):
        invoice_ulrs=''
        for invoice in order.invoice_ids:
            invoice_ulrs=f"/web/image/{request.env['ir.attachment'].sudo().search([('res_model', '=', 'account.move'), ('res_id', '=', invoice.id)], limit=1).id}"
        return invoice_ulrs
    def get_pricerange_price(self,product_id,quantity):
        for item in self.get_price_range(product_id):
            if item["minQuantity"] <= quantity <= item["maxQuantity"]:
                return item["price"]
            elif quantity > item["maxQuantity"]:
                return item["price"]
        return product_id.list_price
    def get_origin_info(self,order):
        result = {
                    'orderId': order.id,
                    "order_name": order.name,
                    "total_amount": order.amount_total,
                    "total_amount_untaxed": order.amount_untaxed,
                    "total_tax":order.amount_tax,
                    "date":order.create_date,
                    "invoices": self.get_invoices_url(order),
                    "items": [
                            {
                            "orderLineId": singleItem.id,
                            "productId":singleItem.product_template_id.id,
                            "productName":singleItem.product_template_id.name if singleItem.is_delivery == False else singleItem.name,
                            "productSlug":singleItem.product_template_id.slug,
                            "productImage":'/web/image?model=product.template&id=' + str(singleItem.product_template_id.id) + '&field=image_128',
                            "currency":singleItem.product_template_id.currency_id.name,
                            "price":singleItem.product_template_id.list_price,
                                
                            "quantity":singleItem.product_uom_qty,
                            "subtotal":singleItem.price_subtotal,
                            "minQuantity":singleItem.product_template_id.min_order_qty,
                            }for  singleItem in order.order_line if singleItem.is_delivery == False]
                }
        for  singleItem in order.order_line:
                    if singleItem.is_delivery:
                        result['shipping']={
                            "option_id": singleItem.option_id,
                            "orderLineId": singleItem.id,
                            "productId":singleItem.product_template_id.id,
                            "productName":singleItem.name,
                            "productSlug":singleItem.product_template_id.slug,
                            "productImage":'/base/static/img/truck.png',
                            "currency":singleItem.product_template_id.currency_id.name,
                            "price":self.get_pricerange_price(singleItem.product_template_id,singleItem.product_uom_qty),
                            "base_price":singleItem.product_template_id.list_price,
                            "quantity":singleItem.product_uom_qty,
                            "subtotal":singleItem.price_subtotal,
                            "minQuantity":self.get_min_qty(singleItem.product_template_id) if self.get_min_qty(singleItem.product_template_id) else singleItem.product_template_id.min_order_qty,
                            "priceRange":self.get_price_range(singleItem.product_template_id),
                            "increaseBy":request.env['product.pricelist.item'].sudo().search([('product_tmpl_id', '=', singleItem.product_template_id.id),('pricelist_id', '=', 1)],limit=1).increase_unit_by if request.env['product.pricelist.item'].sudo().search([('product_tmpl_id', '=', singleItem.product_template_id.id),('pricelist_id', '=', 1)],limit=1).increase_unit_by >0 else 1,
                            }
        
        return result

    @http.route('/api/addToCart', auth='public', type='json',csrf=False, cors='*')
    def addToCart(self,customer_id=None,customer_token=None,products=[],action='add'): 
        User = request.env['res.partner'].sudo().search([('id','=',customer_id)])
        if User:
            order = request.env['sale.order'].sudo().search([('partner_id', '=', User.id), ('state', '=', 'draft')], limit=1)
            # print(order)
            if not order:
                order = request.env['sale.order'].sudo().create({
                    'partner_id': User.id,
                })
            for line in products:
                    product_id = request.env['product.template'].sudo().browse(line.get('product_id')).product_variant_id.id
                    quantity = line.get('product_uom_qty')
                    # price_unit = self.get_pricerange_price(request.env['product.template'].sudo().browse(line.get('product_id')),line.get('product_uom_qty'))
                    order_line = order.order_line.filtered(lambda x: x.product_id.id == product_id)
                    if order_line:
                        if action == 'update':
                            order_line.sudo().write({'product_uom_qty': quantity})
                        elif action == 'add':
                            order_line.sudo().write({'product_uom_qty': order_line.product_uom_qty+quantity})
                    else:
                        request.env['sale.order.line'].sudo().create({
                            'order_id': order.id,
                            'product_id': product_id,
                            'product_uom_qty': quantity,
                            'price_unit': self.get_pricerange_price(request.env['product.template'].sudo().browse(line.get('product_id')),quantity),
                        })
            return self.showOdersList(customer_id,customer_token)
        else:
            print(User)
            # raise BadRequest( "not found")
            return {'error': 'user not found'}
    
    @http.route('/api/get/showOdersList', auth='public', type='json',csrf=False, cors='*')
    def showOdersList(self,customer_id=None,customer_token=None): 
        try:
            User = request.env['res.partner'].sudo().search([('id','=',customer_id),('auth_token','=',customer_token)])
            if User:
                order = request.env['sale.order'].sudo().search([('partner_id', '=', User.id), ('state', '=', 'draft')], limit=1)
                print(order)
                # if order.id==False:
                #     raise BadRequest ('order not found')
                result={
                    'orderId': order.id,
                    "order_name": order.name,
                    "total_amount": order.amount_total,
                    "total_amount_untaxed": order.amount_untaxed,
                    "total_tax":order.amount_tax,
                    "mimOrderAmount": self.get_min_order_amount() if self.get_min_order_amount() else 150,
                    "shipping":{},
                    "items": [
                            {
                            "orderLineId": singleItem.id,
                            "productId":singleItem.product_template_id.id,
                            "productName":singleItem.product_template_id.name,
                            "productSlug":singleItem.product_template_id.slug,
                            "productImage":'/web/image?model=product.template&id=' + str(singleItem.product_template_id.id) + '&field=image_128',
                            "currency":singleItem.product_template_id.currency_id.name,
                            # "price":singleItem.product_template_id.list_price,
                            "price":self.get_pricerange_price(singleItem.product_template_id,singleItem.product_uom_qty),
                            "base_price":singleItem.product_template_id.list_price,
                            "quantity":singleItem.product_uom_qty,
                            "subtotal":singleItem.price_subtotal,
                            "minQuantity":self.get_min_qty(singleItem.product_template_id) if self.get_min_qty(singleItem.product_template_id) else singleItem.product_template_id.min_order_qty,
                            "priceRange":self.get_price_range(singleItem.product_template_id),
                            "increaseBy":request.env['product.pricelist.item'].sudo().search([('product_tmpl_id', '=', singleItem.product_template_id.id),('pricelist_id', '=', 1)],limit=1).increase_unit_by if request.env['product.pricelist.item'].sudo().search([('product_tmpl_id', '=', singleItem.product_template_id.id),('pricelist_id', '=', 1)],limit=1).increase_unit_by >0 else 1,
                            }for  singleItem in order.order_line if singleItem.is_delivery == False ]
                }
                for  singleItem in order.order_line:
                    if singleItem.is_delivery:
                        result['shipping']={
                            "orderLineId": singleItem.id,
                            "productId":singleItem.product_template_id.id,
                            "productName":singleItem.name,
                            "productSlug":singleItem.product_template_id.slug,
                            "productImage":'/base/static/img/truck.png',
                            "currency":singleItem.product_template_id.currency_id.name,
                            "price":self.get_pricerange_price(singleItem.product_template_id,singleItem.product_uom_qty),
                            "quantity":singleItem.product_uom_qty,
                            "subtotal":singleItem.price_subtotal,
                            "minQuantity":self.get_min_qty(singleItem.product_template_id) if self.get_min_qty(singleItem.product_template_id) else singleItem.product_template_id.min_order_qty,
                            "priceRange":self.get_price_range(singleItem.product_template_id),
                            "increaseBy":request.env['product.pricelist.item'].sudo().search([('product_tmpl_id', '=', singleItem.product_template_id.id),('pricelist_id', '=', 1)],limit=1).increase_unit_by if request.env['product.pricelist.item'].sudo().search([('product_tmpl_id', '=', singleItem.product_template_id.id),('pricelist_id', '=', 1)],limit=1).increase_unit_by >0 else 1,
                            }
                return result
            else:
                return {'error': 'user not found'}
        except Exception as e:
            response_data = {'error': str(e)}
            return response_data
        
    
    @http.route('/api/get/deleteItem', auth='public', type='json',csrf=False, cors='*')
    def deleteItem(self,customer_id=None,customer_token=None,orderId=None,orderLineId=None,clear=False): 
        User = request.env['res.partner'].sudo().search([('id','=',customer_id)])
        if User:
            order = request.env['sale.order'].sudo().search([("id","=",orderId),('partner_id', '=', User.id), ('state', '=', 'draft')])
            if order:
                if orderLineId:
                    try:
                        order_line = request.env['sale.order.line'].sudo().search([
                            ('order_id', '=', orderId),
                            ('id', '=', orderLineId),
                        ], limit=1)
                        # Delete the sale.order.line
                        if order_line.id:
                            order_line.unlink()
                        # Return a response
                            result=self.showOdersList(customer_id,customer_token)
                            result['message']='Item deleted from the order'
                            return result
                        else:
                            # raise BadRequest ( "order line not found")
                            return {'error': 'order line not found'}
                    except Exception as e:
                        # raise BadRequest(e)
                        return {'error': str(e)}

                elif clear:
                    order.unlink()
                    return {'message': 'cart cleared'}
            else:
                # raise BadRequest( "order not found")
                return {'error': 'order not found'}
        else:
            # raise BadRequest( "user not found") 
            return {'error': 'user not found'}
########################################################################


############################## BLOG API #################################
    def get_blog_data(self,blog):
        return {'blogId': blog.id,
                'blogSlug': blog.slug,
                 'blogAuthor':blog.author_id.name,
                 'blogAuthorId':blog.author_id.id,
                 'blogTitle': blog.name,
                 'blogTeaser': blog.teaser,
                 'blog_id':blog.blog_id,
                 'create_date':blog.create_date,
                 "blogCover":json.loads(blog.cover_properties)['background-image'].replace('url(', '').replace(')', ''),
                 } 


    @http.route('/api/getBlogsApi', auth='public',type='json',csrf=False, cors='*')
    def getBlogsApi(self, **kw):
        try:
            category = kw.get("blogCategory")
            slug=kw.get("blogCategorySlug")
            filter=[("blog_id.id","=",category)] if category else [("blog_id.slug","=",slug)] if slug else []
            print(filter)
            # filter= slug_or_id if slug_or_id else []
            blogs = request.env['blog.post'].sudo().search(filter)
            blog_data = [ self.get_blog_data(blog) for blog in blogs]
            blogCategories=[{"id":i.id , "name":i.name,"slug":i.slug,"count":i.blog_post_count}for i in request.env['blog.blog'].sudo().search([])]
            return {"blog_data":blog_data, "blog_categories":blogCategories}
        except Exception as e:
            response_data = {'error': str(e)}
            return response_data


    @http.route('/api/singleBlog', auth='none',type='json',csrf=False, cors='*')
    def singleBlog(self, **kw):
        try:
            blogId = kw.get("blogId")
            slug=kw.get("blogSlug")
            slug_or_id=[("id","=",blogId)] if blogId else [("slug","=",slug)] if slug else []
            blog = request.env['blog.post'].sudo().search(slug_or_id)
            result={
                    'blogId': blog.id,
                    'blogSlug': blog.slug,
                    'blogTitle': blog.name,
                    'blogTeaser': blog.teaser,
                    'blog_id':blog.blog_id.name,
                    'create_date':blog.create_date,
                    "blogCover":json.loads(blog.cover_properties)['background-image'].replace('url(', '').replace(')', ''),
                    'blogContent':blog.content,
                    'blogAuthor':blog.author_id.name,
                    'blogAuthorId':blog.author_id.id,
                    # 'author_image':blog.author_avatar
            }
            return result
        except Exception as e:
            response_data = {'error': str(e)}
            return response_data
################################################################################################


########################################## check_out ###########################################
    # @http.route('/api/pay/registerClickPayment', auth='public',type='json',csrf=False, cors='*')
    def registerClickPayment(self,invoice_id,token):
        invoice = request.env['account.move'].sudo().browse(invoice_id)
        print(request.env['account.move'].sudo().search([('state','=', 'posted')]) )
        try:
            payment_method_id=request.env['account.payment.method.line'].sudo().search([("name", "=","Click Pay")])
            request.env['account.payment.register'].with_context(active_ids=invoice.ids, active_model='account.move').sudo().create({
                'amount': invoice.amount_total,
                'payment_date': fields.Date.today(),
                'payment_method_line_id': payment_method_id.id if payment_method_id.id else 1,
            })._create_payments()
            self.sendInvoice(invoice_id,invoice.partner_id.email)
            # invoice.action_invoice_sent()
            return {"invoice": "registered"}
        except Exception as e:
            # print(e)
            return {"error" : e}


    def clickpay_get_payment_url(self, customer, order,returnUrl="https://www.letsunify.in:3003/"):
        clickpay=request.env['payment.provider'].sudo().search([('code', '=', 'clickpay')], limit=1)
        # auth_key='SBJNLM6ZWH-J6HNMBTMH6-NK99HBZL2K'
        headers = {'Accept': 'text/plain',
                'Content-Type': "application/json",
                'authorization': '%s' % (clickpay.auth_key)}
        url = 'https://secure.clickpay.com.sa/payment/request'
        amount = round(order.amount_total, 2)
        txn_reference = str(order.id)
        data = {
                "profile_id": clickpay.profile_id,
                "tran_type": "sale",
                "tran_class": "ecom",
                "cart_id": txn_reference,
                "cart_amount": "%s" % amount,
                "return": returnUrl,
                "cart_currency": 'SAR',
                "cart_description": "Description of the items/services",
                # "framed": True,
                "paypage_lang": "en",
                "hide_shipping": True,
                "customer_details": {
                    "name": customer.name,
                    "email": customer.email,
                    "phone": customer.phone,
                    "street1": customer.street,
                    "city": customer.city,
                    "state": customer.state_id.name,
                    "country": customer.country_id.code,
                    "zip": customer.zip
                },
                # "shipping_details": {
                #     "name": customer.name,
                #     "email": customer.email,
                #     "phone": customer.phone,
                #     "street1": customer.street,
                #     "city": customer.city,
                #     "state": customer.state_id.name,
                #     "country": customer.country_id.name,
                #     "zip": customer.zip
                # },
                # "user_defined": {
                #     "udf3": "UDF3 Test3",
                #     "udf9": "UDF9 Test9"
                # }
                }
        payload = json.dumps(data)
        resp = requests.request('POST', url, data=payload, headers=headers)
        resp = json.loads(resp.text)

        print("clickpay INITIATION RESPONSE %s" % resp)
        try:
            url = resp['redirect_url']
            order_id = resp['tran_ref']
        except:
            print("%s %s" % (resp.get('resultCode'), payload))
            return {"error":"%s %s" % (resp.get('resultCode'), resp.get('message'))}
        # if order_id:
        #     values.provider_reference = order_id
        return {
            "url":url,
            "transaction_data":order_id
            # ,"data":data
            }
      
    @http.route('/api/pay/varifyOrder', auth='public',type='json',csrf=False, cors='*')
    def varifyOrder(self , **kw):
        try:
            test=True
            clickpay=request.env['payment.provider'].sudo().search([('code', '=', 'clickpay')], limit=1)
            headers = {'authorization': '%s' % (clickpay.auth_key)}
            url = 'https://secure.clickpay.com.sa/payment/query'
            data = {
                'profile_id': clickpay.profile_id,
                'tran_ref': kw.get('transaction_id'),        
            }
            payload = json.dumps(data)
            resp = requests.request('POST', url, data=payload, headers=headers)
            resp = json.loads(resp.text)
            if resp:
                payment_status = resp.get('payment_result').get('response_status')
                if payment_status == "A":
                    print('done')
                # elif payment_status == "D":
                #     print('canceled')
                elif payment_status in ["E","D"] and  test:
                    order = request.env['sale.order'].sudo().browse(int(resp.get('cart_id')))
                    try:
                        order.write({'state': 'sale'})
                        payment = request.env["sale.advance.payment.inv"].sudo().create ({"sale_order_ids": order})
                        payment.create_invoices ()
                        invoice_ulrs=''
                        for invoice in order.invoice_ids:
                            invoice.write({'state': 'posted'})
                            res=self.registerClickPayment(invoice.id,kw.get('transaction_id'))
                            invoice_ulrs=f"/web/image/{request.env['ir.attachment'].sudo().search([('res_model', '=', 'account.move'), ('res_id', '=', invoice.id)], limit=1).id}"
                        return {'success': True
                                , 'message': 'Order confirmed and marked as paid'
                                , 'order': self.get_origin_info(order)
                                ,'invoice_url':invoice_ulrs
                                , "customer": {"name": order.partner_id.name,
                                               "email": order.partner_id.email,
                                               "phone": order.partner_id.phone,
                                               "street": order.partner_id.street,
                                                "street2": order.partner_id.street2,
                                                "city": order.partner_id.city,
                                                "zip": order.partner_id.zip,
                                                "country_id": order.partner_id.country_id.name,
                                                "state_id": order.partner_id.state_id.name
                                               }
                                }
                    except Exception as e:
                        error_message = str(e)
                        return {'success': False, 'error': error_message}
                else:
                    return f"received data with invalid payment status {payment_status} for transaction with reference {kw.get('transaction_id')}"
            return {"error":"traction not found","data":resp}
        except Exception as e:
            return {"error": e}
        

    @http.route('/api/pay/startPayment', auth='none',type='json',csrf=False, cors='*')
    def startPayment(self , **kw):
        order=request.env['sale.order'].sudo().search([("id","=",kw.get('orderId'))])
        costomer=request.env['res.partner'].sudo().search([('id','=',kw.get('customer_id'))])
        returnUrl=kw.get("returnUrl") 
        return self.clickpay_get_payment_url(costomer,order,returnUrl)


    @http.route('/api/pay/sendInvoice', auth='public',type='json',csrf=False, cors='*')
    def sendInvoice(self ,invoice_id=None,email=None):
        try:
            invoice = request.env['account.move'].sudo().browse(invoice_id)
            template = request.env['mail.template'].sudo().browse(int(8))
            template.with_context(
                email_to=invoice.partner_id.email,
                email_from=invoice.company_id.email,
            ).send_mail(invoice.id, force_send=True)
            print(invoice.action_invoice_print())
            pdf=request.env['ir.attachment'].sudo().search([('res_model', '=', 'account.move'), ('res_id', '=', invoice_id)], limit=1)
            print(pdf)
            if pdf.id:
                pdf.write({'public': True})
            return f"/web/image/{pdf.id}"
        except Exception as e:
            return {"error": e}
################################################################################################

############################################################## shipping #################################################################
    
    @http.route('/api/pay/shipping', auth='public',type='json',csrf=False, cors='*')
    def shipping(self,order_id=None, **kwargs):
        try:
            order=request.env['sale.order'].sudo().search([("id","=",order_id)],limit=1)
            delivery_methodes = request.env['delivery.carrier'].sudo().search([])
            res={}
            for delivery_methode in delivery_methodes:
                if delivery_methode.delivery_type == 'oto':
                    res = {
                        'delivery_companies': delivery_methode.get_fees(order)
                        ,'order':self.get_origin_info(order)
                    }
                return res
        except Exception as e:
            return {"error": e}

    @http.route('/api/pay/addShipping', auth='public',type='json',csrf=False, cors='*')
    def addShipping(self,order_id=None, **kwargs):
        try:
            delivery=kwargs.get('delivery')
            order=request.env['sale.order'].sudo().search([("id","=",order_id)],limit=1)
            order.set_oto_line(delivery_id=None, name=delivery["deliveryOptionName"], price=delivery["price"], option_id=delivery["deliveryOptionId"])
            # order.write({"option_id":delivery["deliveryOptionId"]})
            # order.create_shipping_order()
            return {'success': True,"carrier_id":order.carrier_id}
        except Exception as e:
            return {"error": e}
        
################################################################################################################################
    @http.route('/api/sub_to_newsletter', type='json', auth='none',csrf=False, cors='*')
    def sub_to_newsletter(self,email=None, **kw):
        mailing_list = request.env['mailing.list'].sudo().search([("name","ilike","Newsletter")],limit=1)
        if mailing_list:
            existing_contact = request.env['mailing.contact'].sudo().search([('email', '=', email)], limit=1)
            if existing_contact:
                if existing_contact in mailing_list.contact_ids:
                    return {'success': True,'exist':True, 'message': 'Email already subscribed to this newsletter'}
                else:
                    mailing_list.contact_ids = [(4, existing_contact.id)]
                    return {'success': True,'exist':False, 'message': 'Existing contact added to the newsletter'}
            else:
                contact = request.env['mailing.contact'].sudo().create({'email': email})
                mailing_list.contact_ids = [(4, contact.id)]
                return {'success': True,'exist':False, 'message': 'New contact subscribed to the newsletter'}
        else:
            return {'success': False, 'error': 'Newsletter not found'}
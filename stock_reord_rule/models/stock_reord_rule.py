# -*- coding: utf-8 -*-
# Copyright (C) 2012 Sergio Corato (<http://www.icstools.it>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import models, fields, api
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT

from datetime import timedelta

class Orderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    @api.model
    def _qty_orderpoint_days(self):
        """Calculate quantity to create warehouse stock for n days of sales.
        Qty sold in days_stats * (1+forecast_gap)
                 / days_stats * days_warehouse)
        """

        product_obj = self.env['product.product']
        products = product_obj.search([
            ('reorder_auto_type','in',['sale','mrp']),
            ])
        for product in products:
            reorder_rule = self.env['stock.warehouse.orderpoint'].search([
                ('product_id','=',product.id),
                ])
            if not reorder_rule:
                continue
            reorder_rule = reorder_rule[0]
            from_date = (fields.Date.from_string(
                fields.Date.today()) - timedelta(
                        days=product.days_stats)).strftime(DATETIME_FORMAT)
            if product.reorder_auto_type == 'mrp':
                lines = self.env['stock.move'].search([
                    ('date','>',from_date),
                    ('product_id','=',product.id),
                    '|',('production_id','!=',False),
                    ('raw_material_production_id','!=',False),
                    ])
            else:
                lines = self.env['sale.order.line'].search([
                    ('date_order','>',from_date),
                    ('product_id','=',product.id),
                    ('order_id.state','in',['done','confirmed']),
                    ])
            #TODO: Add a conversion if UOM doesn't match
            total_qty = sum(x.product_uom_qty for x in lines if
                        x.product_uom == product.uom_id)
            if reorder_rule.qty_multiple:
                total_qty -= (total_qty % reorder_rule.qty_multiple)
            rule_max = total_qty / product.days_stats * \
                (1 + product.forecast_gap / 100) * product.days_warehouse
            reorder_rule.write({'product_max_qty': rule_max})

        return True

class Product(models.Model):
    _inherit = 'product.product'

    reorder_auto_type = fields.Selection([
        ('none','None'),
        ('mrp','Manufactured'),
        ('sale','Sold'),
        ], 'Reordering Calculation Method', default='none')
    days_warehouse = fields.Integer('Safety Stock Days')
    days_stats = fields.Integer('Statistics Days')
    forecast_gap = fields.Float('Variance Percentage',
                                 digits=(6, 3))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

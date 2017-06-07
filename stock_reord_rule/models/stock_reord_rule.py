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
            ('reorder_auto_type','=','sale'),
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

            def _sale_search(product_id):
                return self.env['sale.order.line'].search([
                ('order_id.date_order','>',from_date),
                ('product_id','=',product_id),
                ('order_id.state','in',['done','confirmed']),
                ])

            lines = _sale_search(product.id)
            #TODO: Add a conversion if UOM doesn't match
            total_qty = sum(x.product_uom_qty for x in lines if
                        x.product_uom == product.uom_id)
            bom_lines = self.env['mrp.bom.line'].search([
                ('product_id','=',product.id),
                ])
            for bom_line in bom_lines:
                bom_lines = _sale_search(bom_line.bom_id.product_id.id)
                total_qty += sum(x.product_uom_qty * bom_line.product_qty
                        for x in bom_lines if
                        x.product_uom == bom_line.bom_id.product_id.uom_id)
            rule_min = total_qty / product.days_stats * \
                (1 + product.forecast_gap / 100) * product.days_warehouse
            rule_max = rule_min + (rule_min / 2)
            if reorder_rule.qty_multiple:
                rule_min -= (rule_min % reorder_rule.qty_multiple)
                rule_max -= (rule_max % reorder_rule.qty_multiple)
            reorder_rule.write({
                'product_min_qty': rule_min,
                'product_max_qty': rule_max,
                })

        return True

class Product(models.Model):
    _inherit = 'product.product'

    reorder_auto_type = fields.Selection([
        ('none','None'),
        ('sale','Sold'),
        ], 'Reordering Calculation', default='none')
    days_warehouse = fields.Integer('Safety Stock Days')
    days_stats = fields.Integer('Statistics Days')
    forecast_gap = fields.Float('Variance Percentage',
                                 digits=(6, 3))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

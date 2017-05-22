# -*- coding: utf-8 -*-
# Copyright (C) 2012 Sergio Corato (<http://www.icstools.it>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Improved reordering rules',
    'version': '8.0.1.0.0',
    'category': 'Tools',
    'description': """
This module allows to improve reordering rules of stock module.

It works forecasting the stock needed per product for n days of sales, with
the following formula:

(( Qty sold in days_stats * (1+forecast_gap)) / days_stats * days_warehouse)

where:
- days_stats = days on wich calculate sales stats;
- forecast_gap = forecast of increase/decrease on sales (%);
- days_warehouse = days of stock to keep in the warehouse.

Usage:

insert days_stats, forecast_gap and days_warehouse vars in product form and
create a reordering rule for the same product, without inserting nothing
(neither maximum or minimum quantity are required). The cron job will be
executed daily and will update the maximum quantity in the reordering rule
(you can force it to start changing the date and hour of execution).

This module doesn't need purchase module to work, but it's useful with that
module.""",
    'author': "Sergio Corato,Odoo Community Association (OCA)",
    'website': 'http://www.icstools.it',
    'depends': [
        'procurement',
        'sale',
        ],
    'demo_xml': [],
    'data': [
        'views/stock_reord_rule_view.xml',
        'data/stock_reord_rule_data.xml',
        ],
    'images': [],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

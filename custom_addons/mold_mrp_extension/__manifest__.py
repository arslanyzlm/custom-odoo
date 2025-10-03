{
    'name': 'Mold MRP Extension',
    'category': 'Manufacturing',
    'depends': ['base','product','stock','mrp','uom'],
    'data': [
        'security/ir.model.access.csv',
        'data/product_category.xml',
        'wizard/die_steel_receive_wizard_views.xml',
        'views/product_views.xml',
        'views/stock_lot_views.xml',
        'views/mold_production_views.xml',
        'views/mrp_production_views.xml',
        'views/mrp_workorder_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}

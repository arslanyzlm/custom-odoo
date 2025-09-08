{
    'name': 'Manufacturing Shop Floor',
    'version': '2.0',
    'category': 'Manufacturing',
    'summary': 'Shop Floor interface for production workers',
    'description': """
        Shop Floor Management System:
        - Touch-friendly interface for production workers
        - Work order management and tracking
        - Real-time production reporting
        - Time tracking for operations
        - Quality control integration
    """,
    'depends': ['mrp', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        # 'data/sequences.xml',
        'views/work_center_views.xml',
        'views/work_order_views.xml',
        # 'views/shop_floor_views.xml',
        'views/manufacturing_menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'manufacturing_shop_floor/static/src/css/shop_floor.css',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
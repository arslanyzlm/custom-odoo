{
    'name': 'New Custom Manufacturing Order',
    'version': '2.0',
    'category': 'Manufacturing',
    'summary': 'Custom product creation wizard that also creates manufacturing orders',
    'description': """
        This module extends Odoo MRP to add a custom manufacturing order creation wizard.
            The wizard allows the user to:
            - Choose New or Spare
            - Enter Kalıp No and Yan No
            - Select SOLID or PORTOL
            - Pick specific options depending on type
            - Enter Çelik, Çap, and Paket Boyu for each chosen option
            - Save as a new product
            - Create a manufacturing order for the new product
    """,
    'depends': ['mrp', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'views/mrp_custom_wizard_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
{
    "name": "Steel Traceability (Serials)",
    "version": "2.0",
    'category': 'Manufacturing',
    "summary": "Per-bar steel tracking with serials, certificates, cut wizard, and MO consumption.",
    "license": "LGPL-3",
    "depends": ["stock", "mrp", "purchase"],
    "data": [
        "security/steel_trace_security.xml",
        "security/ir.model.access.csv",
        "views/product_template_views.xml",
        "views/stock_production_lot_views.xml",
        "views/mrp_views.xml",
        "views/menus.xml",
    ],
    "application": False,
    "installable": True,
}
# -*- coding: utf-8 -*-
{
    'name': "Supply Chain Management",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        to manage SoloClass freight
    """,
    'author': "Iatl-Intellisoft",
    'website': "http://www.iatlintellisoft-sd.com",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    # any module necessary for this one to work correctly
    'depends': ['base','mail', 'purchase', 'account', 'stock_landed_costs','is_solo_purchase','report_xlsx'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/supply_chain_request.xml',
        'report/reports.xml',
    ],
}
git clone --branch Technical-Appraisal https://github.com/EsraaAhmed-iatl/Technical-Appraisal-.git
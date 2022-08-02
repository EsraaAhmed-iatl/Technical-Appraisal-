# -*- coding: utf-8 -*-
{
    'name': "Help Desk-Esraa Ahmed",
    'summary': """
        To manage Iatl-intellisoft Help Desk Process""",
    'description': """
        To manage Iatl-intellisoft
         Help Desk Process
    """,
    'author': "Iatl-Intellisoft",
    'website': "http://www.iatlintellisoft-sd.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base','report_xlsx'],
    'data': [
        'security/ir.model.access.csv',
        'security/security_groups.xml',
        'views/help_desk_teams_view.xml',
        'views/help_desk_process_view.xml',
        'views/Menus.xml',
        'report/reports.xml',
    ],
}

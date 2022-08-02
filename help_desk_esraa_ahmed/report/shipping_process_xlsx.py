from odoo import models


class SupplyChainXlsx(models.AbstractModel):
    _name = 'report.is_solo_supply_chain.report_supply_chain_xlsx'
    _inherit = 'report.report_xlsx.abstract'


    def generate_xlsx_report(self, workbook, data, requests ):
        sheet = workbook.add_worksheet("test excel"[:31])
        bold = workbook.add_format({'bold': True})
        for obj in requests:
            report_name = obj.product_id
            # One sheet by partner

            sheet.write(0, 0, obj.name, bold)
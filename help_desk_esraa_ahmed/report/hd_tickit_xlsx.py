
from openerp import fields, models, api, tools, _
import xlsxwriter
import base64
from io import StringIO, BytesIO
from openerp.exceptions import Warning as UserError
from datetime import datetime ,timedelta
import datetime


class HDTickitXlsx(models.AbstractModel):
    _name = 'report.help_desk_esraa_ahmed.report_hd_tickit2_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data):
        file_name = _('hd tickits.xlsx')
        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        excel_sheet = workbook.add_worksheet(" hd ticket"[:31])
        for record in self:
            format = workbook.add_format({'bold': False, 'font_color': 'black', 'bg_color': 'white', 'border': 1})
            format.set_text_wrap()
            format.set_num_format('#,##0.000')
            col = 0
            row = 0
            excel_sheet.set_column(col, col, 25)
            excel_sheet.write(row, col, 'Ticket ID', format)
            excel_sheet.write(row, col, record.tickit_id, format)
            col += 1
            excel_sheet.set_column(col, col, 25)
            excel_sheet.write(row, col, 'Order Date', format)
            excel_sheet.write(row, col, record.tickit_id, format)

            col += 1
            excel_sheet.set_column(col, col, 25)
            excel_sheet.write(row, col, 'Customer No.', format)
            excel_sheet.write(row, col, record.tickit_id, format)

            col += 1
            excel_sheet.set_column(col, col, 25)
            excel_sheet.write(row, col, 'Name', format)
            excel_sheet.write(row, col, record.tickit_id, format)

            col += 1
            excel_sheet.set_column(col, col, 25)
            excel_sheet.write(row, col, 'name', format)
            excel_sheet.write(row, col, record.name, format)
            col += 1
            excel_sheet.set_column(col, col, 25)
            excel_sheet.write(row, col, 'Time Submitted', format)
            excel_sheet.write(row, col, record.time_submitted, format)
            col += 1
            excel_sheet.set_column(col, col, 25)
            excel_sheet.write(row, col, 'Assigned to', format)
            excel_sheet.write(row, col, record.user_id, format)
            col += 1
            excel_sheet.set_column(col, col, 25)
            excel_sheet.write(row, col, 'tags', format)
            excel_sheet.write(row, col, record.tag_ids, format)
        return {
            'name': 'Files to Download',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'report.help_desk_esraa_ahmed.report_hd_tickit2_xlsx',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
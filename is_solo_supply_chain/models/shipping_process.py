
from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError

class supply_chain_line(models.Model):
    _name = 'supply.chain.line'

    supply_id = fields.Many2one("supply.chain.request", "Supply request")
    oreder_id = fields.Many2one('purchase.order', string=" PO")
    picking_id = fields.Many2one('stock.picking', 'Pickings')
    picking_line_id = fields.Many2one('stock.move', 'Pickings line')
    product_id = fields.Many2one("product.product", 'Product')
    po_qty = fields.Float("PO QTY")
    shipped_qty = fields.Float("Shipped QTY")
    wight = fields.Float("wight")
    cbm = fields.Float("CBM")
    actual_qty = fields.Float(string='Actual quantity',
                              readonly=True, compute='_compute_actual_qty',
                              help="the actual recived quantity per the purchase order pickings ")

    @api.depends('picking_line_id', 'picking_line_id.product_uom_qty')
    def _compute_actual_qty(self):
        """
             this method compute the actual receved quantity per picking.
        """

        for record in self:
            stock_move = self.env['stock.move'].search([('state', '=', 'done'),('id','=',record.picking_line_id.id),('product_id','=',record.product_id.id)])
            if len(stock_move) > 0:
                for move in stock_move:
                    record.actual_qty = move.product_uom_qty
            else:
                record.actual_qty=0

class SupplyChainRequest(models.Model):
    _name = 'supply.chain.request'
    _inherit = ['mail.thread']

    date = fields.Date(string="Date Request", default=fields.Date.today(), readonly=True)
    total_CBM = fields.Monetary(string='Total CBM\'s', store=True, readonly=True, compute='_compute_CBM')
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id.id)
    name = fields.Char("Container", required=True)
    bill_of_lading = fields.Char("Bill of Lading")
    partner_ids = fields.Many2many('res.partner', string="Supplier")
    oreder_ids = fields.Many2many('purchase.order', string=" PO's",domain="[('partner_id', 'in', partner_ids),('purchase_type','=','external')]")
    picking_ids = fields.Many2many('stock.picking', string='Pickings',required=True,domain="[('purchase_id', 'in', oreder_ids),('state','=','assigned')]")
    ATD = fields.Date("ATD")
    AAT = fields.Date("AAT")
    return_date = fields.Date("Return Date")
    MBL = fields.Char("MBL")
    seal = fields.Char("Seal")
    document_receiving_date = fields.Date("Document Receiving Date")
    send_IM_date = fields.Date("Send IM For Bank Date")
    recive_IM_date = fields.Date("Recive IM Form Bank Date")
    port_sudan_date = fields.Date("Document Delivery TO Port Sudan Date")
    container_arrive_date = fields.Date("Container arriving Date Port Sudan")
    soba_arriving_date = fields.Date("Container arriving soba Date")
    shippment_reciving_solo = fields.Date("Shipment receiving in Solo Date")
    demurrage = fields.Boolean("Is There Charge Demurrage ?")
    demurrage_charge_days = fields.Float("Demurrage Charge Days")
    supply_request_line = fields.One2many('supply.chain.request.line','supply_request')
    po_details = fields.One2many('supply.chain.line', 'supply_id',
                                 string="PO Details")
    state = fields.Selection([('draft', 'Draft'),
                              ('freighting_supplier', 'Freighting from supplier'),
                              ('follow_up', 'Shipment Document follow up'),
                              ('arrive_port', 'Container Arrive Port Sudan'),
                              ('arrive_soba', 'Container arriving soba'),
                              ('arrive_solo', 'Shipment receiving in Solo'),
                              ('back_port', 'back to port-Sudan'),
                              ('finalize', 'Finalize'),
                              ('done', 'Done'),
                              ('cancel', 'Cancel'), ], string='State',
                              copy=False, default='draft',
                              track_visibility='onchange')
    amount_total = fields.Float(string='Total in Company Currency',
                                readonly=True,compute='_compute_total',
                                help="Total amount in the currency of the company")
    currency_id = fields.Many2one('res.currency',
                                  related='company_id.currency_id',
                                  string="Company Currency",
                                  readonly=True,
                                  help='Utility field to express amount currency', store=True)
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env['res.company']._company_default_get('mrp.production'),
                                 required=True)
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency",
                                          readonly=True,
                                          help='Utility field to express amount currency', store=True)

    @api.depends('po_details', 'po_details.cbm')
    def _compute_CBM(self):
        self.total_CBM = sum(line.cbm for line in self.po_details)

    @api.depends('supply_request_line', 'supply_request_line.cost')
    def _compute_total(self):
        sum_amount = 0.0
        for line in self.supply_request_line:
            if line.currency_id != self.company_id.currency_id:
                sum_amount += line.currency_id.compute(line.cost, self.company_id.currency_id, round=False)
            else:
                sum_amount += line.cost
        self.amount_total = sum_amount

    @api.onchange('partner_ids')
    def onchange_partner_ids(self):
            self.oreder_ids=False

    @api.onchange('oreder_ids')
    def onchange_oreder_ids(self):
        self.picking_ids = False

    @api.model
    def create(self, vals):
        res = super(SupplyChainRequest, self).create(vals)
        res.get_po_details()
        return res

    def create_landed_cost(self):
        land_cost_obj = self.env['stock.landed.cost']
        land_cost_line_obj = self.env['stock.landed.cost.lines']
        landed_vals = {
            'picking_ids': [(6, 0, self.picking_ids.ids)],
            'supply_id' : self.id,
        }
        cost_id = land_cost_obj.create(landed_vals)
        for line in self.supply_request_line:
            if line.currency_id != self.company_id.currency_id:
                cost = line.currency_id.compute(line.cost, self.company_id.currency_id, round=False)
            else:
                cost = line.cost
            landed_cost_line_vals = {
                    'product_id': line.product_id.id,
                    'cost_id': cost_id.id,
                    'split_method': line.product_id.split_method_landed_cost or 'equal',
                    'price_unit': cost,
                }
            land_id = land_cost_line_obj.create(landed_cost_line_vals)
        cost_id.compute_landed_cost()

    def get_po_details(self):
        supply_line_obj = self.env['supply.chain.line']
        if self.po_details:
            self.po_details.unlink()
        for pick in self.picking_ids:
            for line in pick.move_ids_without_package:
                vals = {
                    'product_id': line.product_id.id,
                    'po_qty': line.product_qty,
                    'oreder_id': pick.purchase_id.id,
                    'picking_id': pick.id,
                    'picking_line_id': line.id,
                    'supply_id': self.id
                }
                line_id = supply_line_obj.create(vals)
        return True

    def create_stock_backorder(self):
        for line in self.po_details:
            line.picking_line_id.write({'qty_done': line.shipped_qty})
        for line in self.po_details:
            operations_to_delete = line.picking_id.move_ids_without_package.filtered(lambda o: o.quantity_done <= 0)
            for pack in line.picking_id.move_ids_without_package - operations_to_delete:
                pack.product_qty = pack.quantity_done
            # operations_to_delete.unlink()
        self.po_details.mapped('picking_id').button_validate()

    def done(self):
        for rec in self:
            if all(line.shipped_qty == 0.0 for line in self.po_details):
                raise UserError(_('Please be sure to Enter shipped qty in all Po Details before Done.'))
            rec.create_stock_backorder()
            rec.create_landed_cost()
            rec.state = 'done'

    def set_to_draft(self):
        self.state = 'draft'

    def action_cancel(self):
        self.state = 'cancel'

    def shipment_document_follow_up(self):
        self.state = 'follow_up'

    def container_arrive_port_sudan(self):
        self.state = "arrive_port"

    def container_arriving_soba(self):
        self.state = 'arrive_soba'

    def shipment_receiving_in_solo(self):
        self.state = 'arrive_solo'

    def freight_company_detail(self):
        self.get_po_details()
        self.state = 'freighting_supplier'

    def back_to_port_sudan(self):
        self.state = 'back_port'

    def finalize(self):
        self.state = 'finalize'

class supply_chain_request_line(models.Model):
    _name = 'supply.chain.request.line'

    vendor = fields.Many2one('res.partner', "Vendor")
    product_id = fields.Many2one("product.product", 'Product')
    description = fields.Char(string="Description")
    cost = fields.Monetary(default=0.0, string="Cost", required=True)
    date = fields.Date(string="Date", default=fields.Date.today())
    currency_id = fields.Many2one('res.currency', string='Currency', required=True)
    supply_request = fields.Many2one('supply.chain.request')
    voucher_id = fields.Many2one("account.move", string='Voucher')
    invoice_id = fields.Many2one("account.move", string='Invoice')
    company_id = fields.Many2one('res.company',
                                 related='supply_request.company_id',
                                 string='Company', store=True,readonly=True)
    type = fields.Selection([('voucher', 'Voucher'),
                             ('invoice', 'Invoice'), ], string='Type',
                             required=True, default='voucher')

    def create_voucher(self):
        for line in self:
            line_ids=[]
            journal_id = self.env['account.journal'].search([('type','=','purchase'),('company_id','=',line.company_id.id)],limit=1)
            partner_id = line.vendor or line.company_id.partner_id
            accounts = line.product_id.product_tmpl_id.get_product_accounts()
            if not journal_id:
                raise UserError(_('Please define Journal for Expense Voucher in your Company.'))
            voucher_dict = {
                'invoice_date': line.date,
                'ref': line.supply_request.name,
                'journal_id': journal_id.id,
                'move_type':'in_receipt',
                'currency_id': line.currency_id.id,
                'partner_id': partner_id.id,
                # 'account_id': partner_id.property_account_payable_id.id
            }
            if not accounts['expense']:
                raise UserError(_('Please define Expense Account in the product %s.')%(line.product_id.name))
            name = line.product_id.partner_ref or '' +'\n' + line.product_id.description_purchase or ''
            line_val = (0, 0, {
                        'name': line.description or name,
                        'product_id':line.product_id.id,
                        'price_unit':line.cost,
                        'account_id':accounts['expense'].id,
                    })
            line_ids.append(line_val)
            voucher_dict['line_ids'] = line_ids
            voucher = self.env['account.move'].create(voucher_dict)
            self.write({'voucher_id':voucher.id})

    def create_invoice(self):
        for line in self:
            line_ids=[]
            journal_id = self.env['account.journal'].search([('type','=','purchase'),('company_id','=',line.company_id.id)],limit=1)
            partner_id = line.vendor or line.company_id.partner_id
            accounts = line.product_id.product_tmpl_id.get_product_accounts()
            invoice_dict = {
                'invoice_date': line.date,
                'move_type':'in_invoice',
                'currency_id': line.currency_id.id,
                'partner_id': partner_id.id,
                'journal_id': journal_id.id,
            }
            if not journal_id.default_account_id:
                raise UserError(_('Please define Default Debit Account in your purchase Journal %s.')%(journal_id.name))
            name = line.product_id.partner_ref or '' +'\n' + line.product_id.description_purchase or ''
            line_val = (0, 0, {
                        'name': line.description or name,
                        'product_id':line.product_id.id,
                        'price_unit':line.cost,
                        'account_id':accounts['expense'].id,
                    })
            line_ids.append(line_val)
            invoice_dict['invoice_line_ids'] = line_ids
            invoice = self.env['account.move'].create(invoice_dict)
            self.write({'invoice_id':invoice.id})

class LandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    supply_id = fields.Many2one('supply.chain.request', string='supply chain request')

    # def get_valuation_lines(self):
    #     """
    #     Overwrite to enable landed cost for all type of product cost methods
    #     """
    #     res = super(LandedCost, self).get_valuation_lines()
    #     print('////////',res)
    #     index = 0
    #     if self.supply_id:
    #         for line in self.supply_id.po_details:
    #             res[index]['cbm'] = line.cbm
    #             index += 1
    #     return res


        # for move in self.mapped('picking_ids').mapped('move_lines'):
        #     if move.product_id.valuation != 'real_time':
        #         continue
        #     cbm=0.0
        #     if self.supply_id:
        #         for line in self.supply_id.po_details:
        #             link = self.env['stock.move.operation.link'].search([('operation_id','=',line.picking_line_id.id),('move_id','=',move.id)])
        #             if link:
        #                 cbm=line.cbm
        #     vals = {
        #         'product_id': move.product_id.id,
        #         'account_move_id': move.id,
        #         'quantity': move.product_qty,
        #         'former_cost': sum(quant.cost * quant.qty for quant in move.quant_ids),
        #         'weight': move.product_id.weight * move.product_qty,
        #         'volume': move.product_id.volume * move.product_qty,
        #         'cbm': cbm,
        #     }
        #     lines.append(vals)
        # if not lines and self.mapped('picking_ids'):
        #     raise UserError(_('The selected picking does not contain any move that would be impacted by landed costs. Landed costs are only possible for products configured in real time valuation with real price costing method. Please make sure it is the case, or you selected the correct picking'))
        # return lines









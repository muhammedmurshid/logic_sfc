from odoo import fields,models,api
from datetime import datetime
class  PayRequestWizard(models.TransientModel):
    _name="student.faculty.pay.request.wizard"
    company_id = fields.Many2one(
            'res.company', store=True, copy=False,
            string="Company",
            default=lambda self: self.env.user.company_id.id,
            readonly=True)
    currency_id = fields.Many2one(
            'res.currency', string="Currency",
            related='company_id.currency_id',
            default=lambda
            self: self.env.user.company_id.currency_id.id,
            readonly=True)
    coordinator = fields.Many2one('res.users',string="Coordinator",readonly=True,default=lambda self: self.env.user)

    amount = fields.Monetary(string="Amount",default=lambda self: self._context.get('amount'))
    request_date = fields.Date(string="Date",default=datetime.today())
    sfc_id = fields.Many2one('student.faculty',string="SFC ID",default = lambda self: self._context.get('sfc_id'))
    description = fields.Text(string="Description")
    account_name = fields.Char(string="Account Name",default = lambda self: self._context.get('account_name'))
    account_no = fields.Char(string="Account No",default = lambda self: self._context.get('account_no'))
    ifsc_code = fields.Char(string="IFSC Code",default = lambda self: self._context.get('ifsc_code'))
    bank_name = fields.Char(string="Bank Name",default = lambda self: self._context.get('bank_name'))
    bank_branch = fields.Char(string="Bank Branch",default = lambda self: self._context.get('bank_branch'))

    def action_create_payment_request(self):
        sfc_objs = self.env['student.faculty'].search([('id','=',self.sfc_id.id)],limit=1)
        sfc_objs.write({
            'state':'payment_request'
        })
        self.env['payment.request'].sudo().create({
            'source_type':'sfc',
            'sfc_source':self.sfc_id.id,
            'amount':self.amount,
            'description':self.description  ,
            'account_name':self.account_name,
            'account_no':self.account_no,
            'ifsc_code': self.ifsc_code,
            'bank_name':self.bank_name,
            'bank_branch':self.bank_branch,
        })

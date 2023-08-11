from odoo import fields,models,api
from odoo.exceptions import UserError
from datetime import datetime

class StudentFacultyClub(models.Model):
    _name="student.faculty"
    def _compute_name(self):
        for record in self:
            name=""
            if record.student_id.name:
                name += record.student_id.name + " - "
            if record.topic:
                name += record.topic
            record.name=name
    name = fields.Char(string="Name",compute="_compute_name")
    batch_id = fields.Many2one('logic.base.batch',string="Batch",required=True)
    student_id = fields.Many2one('logic.students',string="Student",required=True)
    topic = fields.Char(string="Topic",required=True)
    coordinator = fields.Many2one('res.users',string="Coordinator",readonly=True,default=lambda self: self.env.user)
    students_count = fields.Integer(string="No of Participants")
    session_type = fields.Selection(selection=[('question','Questions'),('lecture','Lecture')],string="Session Type",default='lecture')
    questions_no = fields.Integer(string="No of Questions")
    lecture_topic = fields.Char(string="Lecture Topic")
    start_datetime = fields.Datetime(string="Start Datetime")
    @api.onchange('start_datetime')
    def _set_end_date_as_start_date(self):
        if self.start_datetime:
            self.end_datetime = datetime(
                year = self.start_datetime.year,
                month = self.start_datetime.month,
                day = self.start_datetime.day,
                minute = self.end_datetime.minute if self.end_datetime else self.start_datetime.minute ,
                hour = self.end_datetime.hour if self.end_datetime else self.start_datetime.hour,
            )
    end_datetime = fields.Datetime(string="End Datetime")
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
    @api.depends('start_datetime','end_datetime')
    def _compute_hours(self):
        for record in self:
            if record.end_datetime and record.start_datetime:
                record.hours =  round((record.end_datetime-record.start_datetime).seconds/3600,2)
            else:
                record.hours = 0
    hours = fields.Float(string="Total Hours",store=True,compute="_compute_hours")
    photo_show = fields.Boolean(string="Show/Hide Photo",default=False)
    photo = fields.Binary(string="Photo")
    def _compute_amount_total(self):
        for record in self:
            record.amount_total = record.hours * record.payment_rate
    amount_total = fields.Monetary(string="Total Amount",compute="_compute_amount_total")
    state = fields.Selection(string="State",selection=[('draft','Draft'),('confirm','Confirmed'),('payment_request','Payment Requested'),('paid','Paid'),('reject','Rejected')],tracking=True)
    account_name = fields.Char(string="Account Name")
    account_no = fields.Char(string="Account No")
    ifsc_code = fields.Char(string="IFSC Code")
    bank_name = fields.Char(string="Bank Name")
    bank_branch = fields.Char(string="Bank Branch")
    payment_request = fields.Many2one('payment.request',string="Payment Request")
    def _get_default_payment_rate(self):
        payment_rate = self.env['student.faculty.rate'].search([],limit=1)
        if payment_rate:
            return payment_rate[0].rate
        else:
            return False
    payment_rate = fields.Monetary(string="Rate Per Hour",default=_get_default_payment_rate)


    @api.model
    def create(self, vals):
        vals['state'] = 'draft'
        result = super(StudentFacultyClub, self).create(vals)
        return result

    def confirm_sfc(self):
        if not self.start_datetime or not self.end_datetime:
            raise UserError('Datetimes cannot be empty when confirming the record')
        self.write({
            'state':'confirm'
        })

    def reset_to_draft(self):
        self.write({
            'state':'draft',
        })
    
    def show_hide_photo(self):
        self.write({
            'photo_show': not self.photo_show,
        })

    def request_payment(self):
        # Display a popup with the entered details
        return {
            'type': 'ir.actions.act_window',
            'name': 'Request Payment',
            'res_model': 'student.faculty.pay.request.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'amount': self.amount_total,
                'sfc_id':self.id,
                'account_name':self.account_name,
                'account_no': self.account_no,
                'ifsc_code':self.ifsc_code,
                'bank_name':self.bank_name,
                'bank_branch':self.bank_branch,
                'partner_type':'student',
                }
        }
    def reject_payment(self):
        self.state = 'reject'


class StudentFacultyRate(models.Model):
    _name="student.faculty.rate"
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
    rate = fields.Monetary(string="Rate Per Hour")
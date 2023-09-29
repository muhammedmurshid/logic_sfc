from odoo import fields,models,api
from odoo.exceptions import UserError
from datetime import datetime

class StudentFacultyClub(models.Model):
    _name="student.faculty"
    _description="Student Faculty"
    _inherit = ['mail.thread', 'mail.activity.mixin']
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
    student_id = fields.Many2one('logic.students',string="Student Faculty",required=True)
    topic = fields.Char(string="Topic",required=True)
    coordinator = fields.Many2one('res.users',string="Coordinator",readonly=True,default=lambda self: self.env.user)
    # students_count = fields.Integer(string="No of Participants")
    session_type = fields.Selection(selection=[('question','Questions'),('lecture','Lecture')],string="Session Type",default='lecture')
    questions_no = fields.Integer(string="No of Questions")
    lecture_topic = fields.Char(string="Lecture Topic",store=True)
    total_students = fields.Integer(string="Total Strength",compute="get_total_students" ,readonly=True)
    coordinator_head = fields.Many2one('res.users',string="Coordinator's Head", default=lambda self: self.env.user.employee_id.parent_id.user_id.id)
    is_coordinator_head = fields.Boolean(compute="_compute_is_coordinator_head")
    hide_payment_request_btn = fields.Boolean(compute="_compute_hide_payment_request_btn")
    average_attendance = fields.Float(string="Average Attendance",compute="_compute_average_attendance")

    def _compute_average_attendance(self):
        for record in self:
            record.average_attendance = 0
            if record.sessions:
                average_attendance = 0
                for session in record.sessions:
                    average_attendance += session.students_count
                average_attendance = round(average_attendance/len(record.sessions),2)
                record.average_attendance = average_attendance

    @api.onchange('is_coordinator_head')
    def _compute_hide_payment_request_btn(self):
        for record in self:
            
            if record.state in ('confirm','approved') and (record.is_coordinator_head or not record.coordinator_head):
                record.hide_payment_request_btn = False
            elif record.state=='approved' and not record.is_coordinator_head:
                record.hide_payment_request_btn = False
            else:
                record.hide_payment_request_btn = True

    def _compute_is_coordinator_head(self):
        for record in self:
            if self.env.user.id==record.coordinator_head.id:
                record.is_coordinator_head = True
            else:
                record.is_coordinator_head = False

    @api.depends('batch_id')
    def get_total_students(self):
        # for record in self:
        if self.batch_id:
            self.total_students = self.env['logic.students'].search_count([('batch_id','=',self.batch_id.id)])
        else:
            self.total_students = 0
    date = fields.Date(string="Date",required=True)
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
    @api.depends('sessions')
    def _compute_hours(self):
        for record in self:
            record.hours = 0
            for session in record.sessions:
                if session.end_datetime and session.start_datetime:
                    record.hours +=  round((session.end_datetime-session.start_datetime).seconds/3600,2)

    @api.onchange('student_id')
    def get_bank_details(self):
        self.account_name = self.student_id.holder_name 
        self.account_no = self.student_id.account_number
        self.ifsc_code = self.student_id.ifsc_code
        self.bank_name = self.student_id.bank_name
        self.bank_branch = self.student_id.branch

    hours = fields.Float(string="Total Hours",store=True,compute="_compute_hours")
    photo_show = fields.Boolean(string="Show/Hide Photo",default=False)
    photo = fields.Binary(string="Photo")
    def _compute_amount_total(self):
        for record in self:
            record.amount_total = record.hours * record.payment_rate
    amount_total = fields.Monetary(string="Total Amount",compute="_compute_amount_total")
    state = fields.Selection(string="State",selection=[('draft','Draft'),('confirm','Confirmed'),('sent_to_approve','Sent for Head Approval'),('approved','Head Approved'),('payment_request','Payment Requested'),('paid','Paid'),('reject','Rejected'),('cancel','Cancelled)')],tracking=True)
    account_name = fields.Char(string="Account Name")
    account_no = fields.Char(string="Account No")
    ifsc_code = fields.Char(string="IFSC Code")
    bank_name = fields.Char(string="Bank Name")
    bank_branch = fields.Char(string="Bank Branch")
    payment_request = fields.Many2one('payment.request',string="Payment Request")
    sessions = fields.One2many('sfc.session','sfc_id',string="Sessions")
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
        if not self.sessions:
            raise UserError('Sessions cannot be empty when confirming the record')
        self.write({
            'state':'confirm'
        })

    def action_sent_head_approval(self):
        self.activity_schedule('logic_sfc.mail_activity_type_sfc', user_id=self.coordinator_head.id,
                summary=f'To Approve: SFC from {self.coordinator.name}')
        self.write({
            'state':'sent_to_approve',
        })

    def action_head_approve(self):
        self.activity_ids.unlink()
        self.message_post(body=f"SFC Approved by {self.coordinator_head.name}")
        self.write({
            'state':'approved',
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
    
    def action_reject(self):
        self.activity_ids.unlink()
        self.write({
            'state' : 'reject',
        })   
    def reject_payment(self):
        self.write({
            'state' : 'reject',
        })


class StudentFacultyRate(models.Model):
    _name="student.faculty.rate"
    name = fields.Char(string="Name",compute="_compute_name")
    def _compute_name(self):
        for record in self:
            record.name = "SFC Rate " + str(record.id)
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
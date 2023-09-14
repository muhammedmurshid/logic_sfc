from odoo import models, api, fields
from datetime import datetime
from odoo.exceptions import UserError

class SfcSession(models.Model):
    _name = "sfc.session"
    start_datetime = fields.Datetime(string="Start Time")
    end_datetime = fields.Datetime(string="End Time")
    sfc_id = fields.Many2one('student.faculty')
    session_type = fields.Selection(related="sfc_id.session_type",string="Session Type")
    students_count = fields.Integer(string="Participants")
    hours = fields.Float(string="Total Hours")

    lecture_topic = fields.Char(string="Lecture Topic")
    questions_no = fields.Integer(string="No of Questions")


    @api.onchange('start_datetime')
    def _set_end_date_as_start_date(self):
        if self.start_datetime:
            self.end_datetime = datetime(
                year = self.start_datetime.year,
                month = self.start_datetime.month,
                day = self.start_datetime.day,
                minute = self.end_datetime.minute if self.end_datetime else self.start_datetime.minute ,
                hour = self.end_datetime.hour if self.end_datetime else self.start_datetime.hour,
                second = self.end_datetime.second if self.end_datetime else self.start_datetime.second,

            )
    @api.depends('start_datetime','end_datetime')
    def _compute_hours(self):
        for record in self:
            if record.end_datetime and record.start_datetime:
                record.hours =  round((record.end_datetime-record.start_datetime).seconds/3600,2)
            else:
                record.hours = 0
    hours = fields.Float(string="Total Hours",store=True,compute="_compute_hours")
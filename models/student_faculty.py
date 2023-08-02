from odoo import fields,models,api

class StudentFacultyClub(models.Model):
    _name="student.faculty"
    batch_id = fields.Many2one('logic.base.batch',string="Batch")
    student_id = fields.Many2one('logic.students',string="Student Faculty",domain=[('batch_id','=',batch_id)])
    topic = fields.Char(string="Topic")
    coordinator = fields.Many2one('res.users',string="Coordinator",readonly=True,default=lambda self: self.env.user)
    students_count = fields.Integer(string="No of Participants")
    start_datetime = fields.Datetime(string="Start Datetime")
    end_datetime = fields.Datetime(string="End Datetime")
    @api.depends('start_datetime','end_datetime')
    def _compute_hours(self):
        for record in self:
            if record.end_datetime and record.start_datetime:
                record.hours =  round((record.end_datetime-record.start_datetime).seconds/3600,2)
            else:
                record.hours = 0
    hours = fields.Float(string="Total Hours",store=True,compute="_compute_hours")
    photo = fields.Binary(string="Photo")
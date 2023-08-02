{
    'name': "Student Faculty Club",
    'version': "14.0.1.0",
    'sequence': "0",
    'depends': ['base', 'faculty','logic_base'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/pay_wizard_view.xml',
        'views/student_faculty_club.xml',
        'data/payment_rate_data.xml',
    ],
    'demo': [],
    'summary': "Student Faculty Club",
    'description': "",
    'installable': True,
    'auto_install': False,
    'license': "LGPL-3",
    'application': True
}
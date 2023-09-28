{
    'name': "Student Faculty Club",
    'author': 'Rizwaan',
    'version': "14.0.1.0",
    'sequence': "0",
    'depends': ['base','logic_base',],
    'data': [
        'data/activity.xml',
        'security/record_rules.xml',
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
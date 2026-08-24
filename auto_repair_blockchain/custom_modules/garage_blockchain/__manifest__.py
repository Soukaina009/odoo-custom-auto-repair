{
    'name': "Mécanicien V2",
    'version': "1.0.0",
    'category': "Services",
    'summary': "Gestion avancée des mécaniciens, voitures et réparations (héritage RH)",
    'author': "Votre Nom",
    'license': "LGPL-3",
    'depends': ['base', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee_views.xml',
        'views/voiture_views.xml',
        'views/reparation_views.xml',
        'views/menu.xml',
        'demo/demo_data.xml',
    ],
    'installable': True,
    'application': True,

}

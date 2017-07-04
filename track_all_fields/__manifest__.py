# -*- coding: utf-8 -*-
{
    'name': "Track all fields",
    'version': '1.0.0',
    'license': 'LGPL-3',
    'category': 'Mail',
    'description': """
 It will track all the fields in mail chatter box for seleted models.

 How to use?
 1. Go to models views (Settings > Data Structure > Models)
 2. click on model and enable "Track all fields".

Tested on Odoo 10.0 d8083b42704b3a5eb7f21ccd743a8265787f6caa
    """,
    'author': "Ronak Baxi",
    'depends': ['mail'],
    'data': [
        'views/views.xml',
    ],
}

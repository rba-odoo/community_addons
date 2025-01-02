# -*- coding: utf-8 -*-

{
    'name': 'Encrypted Field Type For Odoo',
    'version': '15.0',
    'category': 'Security',
    'author': "Ronak Baxi (rba-odoo)",
    "description": """
        Added Custom Field - Encrypted
        To Create An Encrypted Fields
        field_name = fields.Encrypted()
        In View Added Widget:
        widget="Encrypted"

        Added aes_encryption_key = 16 Digits Of Your Encryption Key in your odoo config file.
    """,
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'data': [
    ],
    'assets': {
        'web.assets_backend': [
            'rb_encrypted_field/static/src/js/basic_fields.js',
            'rb_encrypted_field/static/src/js/field_utils_format.js'
        ]
    },
    "external_dependencies": {
        "python": [
            "pycryptodome",
        ],
    },
}

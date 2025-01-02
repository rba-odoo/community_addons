# -*- coding: utf-8 -*-
# © 2015-TODAY LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Encrypted Field Type For Odoo',
    'version': '14.0',
    'category': 'Security',
    'author': "Heartfulness Team",
    "description": """
        Added Custom Field - Encrypted
        To Create An Encrypted Fields
        field_name = fields.Encrypted()
        In View Added Widget:
        widget="Encrypted"

        Added aes_encryption_key = 16 Digits Of Your Encryption Key
    """,
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'data': [
        'views/assets.xml',
    ],
    "external_dependencies": {
        "python": [
            "pycryptodome",
        ],
    },
}

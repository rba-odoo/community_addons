    # -*- coding: utf-8 -*-
# © 2015-TODAY LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields
import base64
from Crypto.Cipher import AES
from Crypto import Random
import hashlib
import logging
logger = logging.getLogger(__name__)
from odoo.tools import config

def monkey_patch(cls):
    """ Return a method decorator to monkey-patch the given class. """
    def decorate(func):
        name = func.__name__
        func.super = getattr(cls, name, None)
        setattr(cls, name, func)
        return func
    return decorate

#
# Implement encrypt fields by monkey-patching fields.Field
#

fields.Field.__doc__ += """

        .. _field-encrypted:

        .. rubric:: Encrypted fields

        ...

        :param encrypt: the name of the field where encrypted the value of this
         field must be stored.
"""

@monkey_patch(fields.Field)
def _get_attrs(self, model, name):
    attrs = _get_attrs.super(self, model, name)
    if attrs.get('encrypt'):
        # by default, encrypt fields are not stored and not copied
        attrs['copy'] = attrs.get('copy', False)
        attrs['compute'] = self._compute_encrypt
        if not attrs.get('readonly'):
            attrs['inverse'] = self._inverse_encrypt
    return attrs


@monkey_patch(fields.Field)
def _compute_encrypt(self, records):
    for record in records:
        values = record[self.encrypt] or {}
        record[self.name] = values.get(self.name)
    if self.relational:
        for record in records:
            record[self.name] = record[self.name].exists()


@monkey_patch(fields.Field)
def _inverse_encrypt(self, records):
    for record in records:
        values = record[self.encrypt] or {}
        value = self.convert_to_read(
            record[self.name], record,
            use_name_get=False
        )
        if value:
            if values.get(self.name) != value:
                values[self.name] = value
                record[self.encrypt] = values
        else:
            if self.name in values:
                values.pop(self.name)
                record[self.encrypt] = values


#
# Definition and implementation of encrypted fields
#

class Encrypted(fields.Field):
    """
    Identical to fields.Text, except encrypted in the database

    :param translate: whether the value of this field can be translated
    """
    type = 'encrypted'
    bs = 16
    column_type = ('text', 'text')
    prefetch = False
    KEY = config.options.get('aes_encryption_key')

    key = hashlib.sha256(KEY.encode()).digest()
    
    def _encrypt(self, raw):
        if raw:
            raw = self._pad(raw)
            iv = Random.new().read(AES.block_size)
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            return "AES" + str(base64.urlsafe_b64encode(iv + cipher.encrypt(raw.encode('utf-8'))), 'utf-8')
        else:
            return raw

    def _decrypt(self, enc):
        try:
            if not enc:
                return
            if enc.startswith("AES"):
                enc = enc[3:]
            elif enc.endswith("=="):
                return str(base64.b64decode(enc), 'utf-8')
            else:
                return enc
            enc = base64.urlsafe_b64decode(enc)
            iv = enc[:AES.block_size]
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')
        except Exception as e:
            logger.error("Failed to decrypt - %s", e)
            return enc

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s) - 1:])]

    def convert_to_column(self, value, record, values=None, validate=True):
        return self._encrypt(value)

    def convert_to_cache(self, value, record, validate=True):
        """
        Convert ``value`` to the cache level in ``env``; ``value`` may come
        from an assignment, or have the format of methods
        :meth:`BaseModel.read` or :meth:`BaseModel.write`

        Params:
            value: str
            record: the target record for the assignment,
                or an empty recordset
            validate: bool when True, field-specific validation of
                ``value`` will be performed
        """
        return self._encrypt(value)

    def convert_to_read(self, value, record, use_name_get=True):
        """
        Convert ``value`` from the cache to a value as returned by method
        :meth:`BaseModel.read`

        Params:
            value: str
            use_name_get: bool when True, value's diplay name will
                    be computed using :meth:`BaseModel.name_get`, if relevant
                    for the field
        """
        return False if value is None else self._decrypt(value)

    def convert_to_write(self, value, target=None, fnames=None):
        """
        Convert ``value`` from the cache to a valid value for method
        :meth:`BaseModel.write`.

        Params:
            value: str
            target: optional, the record to be modified with this value
            fnames: for relational fields only, an optional collection
                of field names to convert
        """
        return self._decrypt(value)

    def convert_to_export(self, value, record):
        """
        Convert ``value`` from the cache to a valid value for export. The
        parameter ``env`` is given for managing translations.

        Params:
            value: str
        """
        if not value:
            return ''
        return self._decrypt(value)

    def convert_to_record(self, value, record):
        return False if value is None else self._decrypt(value)
        
fields.Encrypted = Encrypted

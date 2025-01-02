from odoo import fields, tools
import base64
from Crypto.Cipher import AES
from Crypto import Random
import hashlib
import logging

logger = logging.getLogger(__name__)

KEY = tools.config.get('aes_encryption_key', 'default_key')
KEY_HASH = hashlib.sha256(KEY.encode()).digest()


def monkey_patch(cls):
    """ Return a method decorator to monkey-patch the given class. """
    def decorate(func):
        name = func.__name__
        func.super = getattr(cls, name, None)
        setattr(cls, name, func)
        return func
    return decorate


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


class Encrypted(fields.Field):
    type = 'encrypted'
    column_type = ('text', 'text')
    bs = 16
    key = KEY_HASH

    def _encrypt(self, raw):
        if raw:
            raw = self._pad(raw)
            iv = Random.new().read(AES.block_size)
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            return "AES" + str(base64.urlsafe_b64encode(iv + cipher.encrypt(raw.encode('utf-8'))), 'utf-8')
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
        return self._encrypt(value)

    def convert_to_read(self, value, record, use_name_get=True):
        return False if value is None else self._decrypt(value)

    def convert_to_write(self, value, target=None, fnames=None):
        return self._decrypt(value)

    def convert_to_export(self, value, record):
        if not value:
            return ''
        return self._decrypt(value)

    def convert_to_record(self, value, record):
        return False if value is None else self._decrypt(value)


fields.Encrypted = Encrypted

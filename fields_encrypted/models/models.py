from odoo import models, fields, api, _
from odoo.exceptions import UserError
from collections import defaultdict
class Base(models.AbstractModel):
    _inherit = 'base'

    def _valid_field_parameter(self, field, name):
        return name == 'encrypt' or super()._valid_field_parameter(field, name)


class IrModelFields(models.Model):
    _inherit = 'ir.model.fields'

    ttype = fields.Selection(selection_add=[('encrypted', 'encrypted')],ondelete={'encrypted': 'cascade'})
    encryption_field_id = fields.Many2one(
        comodel_name='ir.model.fields',
        string='Encryption Field',
        ondelete='cascade',
        domain="[('ttype','=','encrypted'), ('model_id', '=', model_id)]",
        help="If set, this field will be stored encrypted in encryption field,"
             "instead of having its own database column. "
             "This cannot be changed after creation.",
    )

    def write(self, vals):
        # Limitation: renaming a encrypted field or changing the storing system is
        # currently not allowed
        if 'encryption_field_id' in vals or 'name' in vals:
            for field in self:
                if 'encryption_field_id' in vals and field.encryption_field_id.id != vals['encryption_field_id']:
                    raise UserError(_('Changing the storing system for field "%s" is not allowed.', field.name))
                if field.encryption_field_id and (field.name != vals['name']):
                    raise UserError(_('Renaming encrypted field "%s" is not allowed', field.name))

        return super(IrModelFields, self).write(vals)

    def _reflect_field_params(self, field, model_id):
        params = super(IrModelFields, self)._reflect_field_params(field,model_id)

        params['encryption_field_id'] = None
        if getattr(field, 'encrypt', None):
            model = self.env[field.model_name]
            encryption_field = model._fields.get(field.encrypt)
            if encryption_field is None:
                raise UserError(_(
                    "Encryption field `%s` not found for encrypt"
                    "field `%s`!") % (field.encrypt, field.name))
            encryption_record = self._reflect_field(encryption_field)
            params['encryption_field_id'] = encryption_record.id

        return params

    def _instanciate_attrs(self, field_data):
        attrs = super(IrModelFields, self)._instanciate_attrs(field_data)
        if field_data.get('encryption_field_id'):
            encryption_record = self.browse(field_data['encryption_field_id'])
            attrs['encrypt'] = encryption_record.name
        return attrs

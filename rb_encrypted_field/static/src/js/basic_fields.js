odoo.define('encrypted_field.basic_fields', function (require) {
    "use strict";
    var field_registry = require('web.field_registry');
    var basic_fields = require('web.basic_fields');
    var FieldText = basic_fields.FieldText;

    var FieldEncrypted = FieldText.extend({

        // formatType is used to determine which format (and parse) functions
        /**
         * to override to indicate which field types are supported by the widget
         *
         * @type Array<String>
         */
        supportedFieldTypes: ['text'],
    });

    field_registry.add('Encrypted', FieldEncrypted);
    return {
        FieldEncrypted: FieldEncrypted
    };
});


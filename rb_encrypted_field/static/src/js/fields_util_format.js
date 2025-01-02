odoo.define('percent_field.field_utils_format', function (require) {
    "use strict";
    var field_utils = require('web.field_utils');
    var basic_controller = require('web.BasicController');
    var _t = require('web.core')._t;
    var error_val;
    /**
 * Returns a string representing a char.  If the value is false, then we return
 * an empty string.
 *
 * @param {string|false} value
 * @param {Object} [field]
 *        a description of the field (note: this parameter is ignored)
 * @param {Object} [options] additional options
 * @param {boolean} [options.escape=false] if true, escapes the formatted value
 * @param {boolean} [options.isPassword=false] if true, returns '********'
 *   instead of the formatted value
 * @returns {string}
 */
    function formatEncrypted(value, field, options) {
        value = typeof value === 'string' ? value : '';
        if (options && options.isPassword) {
            return _.str.repeat('*', value ? value.length : 0);
        }
        if (options && options.escape) {
            value = _.escape(value);
        }
        return value;
    }
    /**
     * Parse a String 
     *
     * @param {string} value
     *                
     */
     function parseEncrypted(value, field, options) {
        var parsed = value;
        return parsed;
    }
    field_utils['format']['Encrypted'] = formatEncrypted;
    field_utils['parse']['Encrypted'] = parseEncrypted;
});


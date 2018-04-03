protected static boolean isString(Object o) {

/*
 *  The Apache Software License, Version 1.1
 *
 *  Copyright (c) 1999-2003 The Apache Software Foundation.  All rights
 *  reserved.
 *
 *  Redistribution and use in source and binary forms, with or without
 *  modification, are permitted provided that the following conditions
 *  are met:
 *
 *  1. Redistributions of source code must retain the above copyright
 *  notice, this list of conditions and the following disclaimer.
 *
 *  2. Redistributions in binary form must reproduce the above copyright
 *  notice, this list of conditions and the following disclaimer in
 *  the documentation and/or other materials provided with the
 *  distribution.
 *
 *  3. The end-user documentation included with the redistribution, if
 *  any, must include the following acknowlegement:
 *  "This product includes software developed by the
 *  Apache Software Foundation (http://www.apache.org/)."
 *  Alternately, this acknowlegement may appear in the software itself,
 *  if and wherever such third-party acknowlegements normally appear.
 *
 *  4. The names "The Jakarta Project", "Struts", and "Apache Software
 *  Foundation" must not be used to endorse or promote products derived
 *  from this software without prior written permission. For written
 *  permission, please contact apache@apache.org.
 *
 *  5. Products derived from this software may not be called "Apache"
 *  nor may "Apache" appear in their names without prior written
 *  permission of the Apache Group.
 *
 *  THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESSED OR IMPLIED
 *  WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
 *  OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 *  DISCLAIMED.  IN NO EVENT SHALL THE APACHE SOFTWARE FOUNDATION OR
 *  ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 *  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 *  LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
 *  USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 *  ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
 *  OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
 *  OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
 *  SUCH DAMAGE.
 *  ====================================================================
 *
 *  This software consists of voluntary contributions made by many
 *  individuals on behalf of the Apache Software Foundation.  For more
 *  information on the Apache Software Foundation, please see
 *  <http://www.apache.org/>.
 */

package org.apache.struts.validator;

import java.io.Serializable;
import java.util.Date;
import java.util.Locale;
import javax.servlet.http.HttpServletRequest;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.apache.commons.validator.Field;
import org.apache.commons.validator.GenericTypeValidator;
import org.apache.commons.validator.GenericValidator;
import org.apache.commons.validator.ValidatorAction;
import org.apache.commons.validator.ValidatorUtil;
import org.apache.struts.action.ActionErrors;

/**
 *  <p>
 *
 *  This class contains the default validations that are used in the validator-rules.xml
 *  file.</p>
 *
 * In general passing in a null or blank will return a null Object or a false
 * boolean. However, nulls and blanks do not result in an error being added to the
 * errors.
 *
 *@author     David Winterfeldt
 *@author     James Turner
 *@author     Rob Leland
 *@since      Struts 1.1
 */
public class FieldChecks implements Serializable {

    /**
     *  Commons Logging instance.
     */
    private static Log LOG = LogFactory.getLog(FieldChecks.class);

    public final static String FIELD_TEST_NULL = "NULL";
    public final static String FIELD_TEST_NOTNULL = "NOTNULL";
    public final static String FIELD_TEST_EQUAL = "EQUAL";


    /**
     *  <p>
     *
     *  Checks if the field isn't null and length of the field is greater than zero
     *  not including whitespace.</p>
     *
     *@param  bean     The bean validation is being performed on.
     *@param  va       The <code>ValidatorAction</code> that is currently being performed.
     *@param  field    The <code>Field</code> object associated with the current
     *      field being validated.
     *@param  errors   The <code>ActionErrors</code> object to add errors to if any
     *      validation errors occur.
     *@param  request  Current request object.
     *@return          True if meets stated requirements, False otherwise
     */
    public static boolean validateRequired(Object bean,
                                           ValidatorAction va, Field field,
                                           ActionErrors errors,
                                           HttpServletRequest request) {

        String value = null;
        if (isString(bean)) {
            value = (String) bean;
        } else {
            value = ValidatorUtil.getValueAsString(bean, field.getProperty());
        }
        if (GenericValidator.isBlankOrNull(value)) {
            errors.add(field.getKey(),
                                 Resources.getActionError(request, va, field));

            return false;
        } else {
            return true;
        }

    }


    /**
     *  <p>
     *  Checks if the field isn't null based on the values of other fields.
     *  </p>
     *
     *@param  bean     The bean validation is being performed on.
     *@param  va       The <code>ValidatorAction</code> that is currently being performed.
     *@param  field    The <code>Field</code> object associated with the current
     *      field being validated.
     *@param  errors   The <code>ActionErrors</code> object to add errors to if any
     *      validation errors occur.
     *@param  validator The <code>Validator</code> instance, used to access other field values.
     *@param  request  Current request object.
     *@return          True if meets stated requirements, False otherwise
     */
    public static boolean validateRequiredIf(Object bean,
                                             ValidatorAction va, Field field,
                                             ActionErrors errors,
                                             org.apache.commons.validator.Validator validator,
                                             HttpServletRequest request) {
        Object form = validator.getResource(org.apache.commons.validator.Validator.BEAN_KEY);
        String value = null;
        boolean required = false;
        if (isString(bean)) {
            value = (String) bean;
        } else {
            value = ValidatorUtil.getValueAsString(bean, field.getProperty());
        }
        int i = 0;
        String fieldJoin = "AND";
        if (!GenericValidator.isBlankOrNull(field.getVarValue("field-join"))) {
            fieldJoin = field.getVarValue("field-join");
        }
        if (fieldJoin.equalsIgnoreCase("AND")) {
            required = true;
        }
        while (!GenericValidator.isBlankOrNull(field.getVarValue("field[" + i + "]"))) {
            String dependProp = field.getVarValue("field[" + i + "]");
            String dependTest = field.getVarValue("field-test[" + i + "]");
            String dependTestValue = field.getVarValue("field-value[" + i + "]");
            String dependIndexed = field.getVarValue("field-indexed[" + i + "]");
            if (dependIndexed == null)
                dependIndexed = "false";
            String dependVal = null;
            boolean this_required = false;
            if (field.isIndexed() && dependIndexed.equalsIgnoreCase("true")) {
                String key = field.getKey();
                if ((key.indexOf("[") > -1) &&
                                     (key.indexOf("]") > -1)) {
                    String ind = key.substring(0, key.indexOf(".") + 1);
                    dependProp = ind + dependProp;
                }
            }
            dependVal = ValidatorUtil.getValueAsString(form, dependProp);
            if (dependTest.equals(FIELD_TEST_NULL)) {
                if ((dependVal != null) && (dependVal.length() > 0)) {
                    this_required = false;
                } else {
                    this_required = true;
                }
            }
            if (dependTest.equals(FIELD_TEST_NOTNULL)) {
                if ((dependVal != null) && (dependVal.length() > 0)) {
                    this_required = true;
                } else {
                    this_required = false;
                }
            }
            if (dependTest.equals(FIELD_TEST_EQUAL)) {
                this_required = dependTestValue.equalsIgnoreCase(dependVal);
            }
            if (fieldJoin.equalsIgnoreCase("AND")) {
                required = required && this_required;
            } else {
                required = required || this_required;
            }
            i++;
        }
        if (required) {
            if ((value != null) && (value.length() > 0)) {
                return true;
            } else {
                errors.add(field.getKey(), Resources.getActionError(request, va, field));
                return false;
            }
        }
        return true;
    }

    /**
     *  <p>
     *
     *  Checks if the field matches the regular expression in the field's mask attribute.
     *  </p>
     *
     *@param  bean     The bean validation is being performed on.
     *@param  va       The <code>ValidatorAction</code> that is currently being performed.
     *@param  field    The <code>Field</code> object associated with the current
     *      field being validated.
     *@param  errors   The <code>ActionErrors</code> object to add errors to if any
     *      validation errors occur.
     *@param  request  Current request object.
     *@return          True if field matches mask, false otherwise.
     */
    public static boolean validateMask(Object bean,
                                       ValidatorAction va, Field field,
                                       ActionErrors errors,
                                       HttpServletRequest request) {

        String mask = field.getVarValue("mask");
        String value = null;
        if (isString(bean)) {
            value = (String) bean;
        } else {
            value = ValidatorUtil.getValueAsString(bean,
                                 field.getProperty());
        }
        try {
            if (!GenericValidator.isBlankOrNull(value) &&
                                 !GenericValidator.matchRegexp(value, mask)) {
                errors.add(field.getKey(),
                                     Resources.getActionError(request, va,
                                                          field));

                return false;
            } else {
                return true;
            }
        } catch (Exception e) {
            LOG.error(e.getMessage(), e);
        }
        return true;
    }


    /**
     *  <p>
     *
     *  Checks if the field can safely be converted to a byte primitive.</p>
     *
     *@param  bean     The bean validation is being performed on.
     *@param  va       The <code>ValidatorAction</code> that is currently being performed.
     *@param  field    The <code>Field</code> object associated with the current
     *      field being validated.
     *@param  errors   The <code>ActionErrors</code> object to add errors to if any
     *      validation errors occur.
     *@param  request  Current request object.
     *@return          A Byte if valid, a null otherwise.
     */
    public static Byte validateByte(Object bean,
                                    ValidatorAction va, Field field,
                                    ActionErrors errors,
                                    HttpServletRequest request) {

        Byte result = null;
        String value = null;
        if (isString(bean)) {
            value = (String) bean;
        } else {
            value = ValidatorUtil.getValueAsString(bean, field.getProperty());
        }

        if (!GenericValidator.isBlankOrNull(value)) {
            result = GenericTypeValidator.formatByte(value);

            if (result == null) {
                errors.add(field.getKey(), Resources.getActionError(request, va, field));
            }
        }

        return result;
    }


    /**
     *  <p>
     *
     *  Checks if the field can safely be converted to a short primitive.</p>
     *
     *@param  bean     The bean validation is being performed on.
     *@param  va       The <code>ValidatorAction</code> that is currently being performed.
     *@param  field    The <code>Field</code> object associated with the current
     *      field being validated.
     *@param  errors   The <code>ActionErrors</code> object to add errors to if any
     *      validation errors occur.
     *@param  request  Current request object.
     *@return          A Short if valid, otherwise a null.
     */
    public static Short validateShort(Object bean,
                                      ValidatorAction va, Field field,
                                      ActionErrors errors,
                                      HttpServletRequest request) {
        Short result = null;
        String value = null;
        if (isString(bean)) {
            value = (String) bean;
        } else {
            value = ValidatorUtil.getValueAsString(bean, field.getProperty());
        }

        if (!GenericValidator.isBlankOrNull(value)) {
            result = GenericTypeValidator.formatShort(value);

            if (result == null) {
                errors.add(field.getKey(), Resources.getActionError(request, va, field));
            }
        }

        return result;
    }


    /**
     *  <p>
     *
     *  Checks if the field can safely be converted to an int primitive.</p>
     *
     *@param  bean     The bean validation is being performed on.
     *@param  va       The <code>ValidatorAction</code> that is currently being performed.
     *@param  field    The <code>Field</code> object associated with the current
     *      field being validated.
     *@param  errors   The <code>ActionErrors</code> object to add errors to if any
     *      validation errors occur.
     *@param  request  Current request object.
     *@return          An Integer if valid, a null otherwise.
     */
    public static Integer validateInteger(Object bean,
                                          ValidatorAction va, Field field,
                                          ActionErrors errors,
                                          HttpServletRequest request) {
        Integer result = null;
        String value = null;
        if (isString(bean)) {
            value = (String) bean;
        } else {
            value = ValidatorUtil.getValueAsString(bean, field.getProperty());
        }

        if (!GenericValidator.isBlankOrNull(value)) {
            result = GenericTypeValidator.formatInt(value);

            if (result == null) {
                errors.add(field.getKey(), Resources.getActionError(request, va, field));
            }
        }

        return result;
    }


    /**
     *  <p>
     *
     *  Checks if the field can safely be converted to a long primitive.</p>
     *
     *@param  bean     The bean validation is being performed on.
     *@param  va       The <code>ValidatorAction</code> that is currently being performed.
     *@param  field    The <code>Field</code> object associated with the current
     *      field being validated.
     *@param  errors   The <code>ActionErrors</code> object to add errors to if any
     *      validation errors occur.
     *@param  request  Current request object.
     *@return          A Long if valid, a null otherwise.
     */
    public static Long validateLong(Object bean,
                                    ValidatorAction va, Field field,
                                    ActionErrors errors,
                                    HttpServletRequest request) {
        Long result = null;
        String value = null;
        if (isString(bean)) {
            value = (String) bean;
        } else {
            value = ValidatorUtil.getValueAsString(bean, field.getProperty());
        }

        if (!GenericValidator.isBlankOrNull(value)) {
            result = GenericTypeValidator.formatLong(value);

            if (result == null) {
                errors.add(field.getKey(), Resources.getActionError(request, va, field));
            }
        }

        return result;
    }


    /**
     *  <p>
     *
     *  Checks if the field can safely be converted to a float primitive.</p>
     *
     *@param  bean     The bean validation is being performed on.
     *@param  va       The <code>ValidatorAction</code> that is currently being performed.
     *@param  field    The <code>Field</code> object associated with the current
     *      field being validated.
     *@param  errors   The <code>ActionErrors</code> object to add errors to if any
     *      validation errors occur.
     *@param  request  Current request object.
     *@return          A Float if valid, a null otherwise.
     */
    public static Float validateFloat(Object bean,
                                      ValidatorAction va, Field field,
                                      ActionErrors errors,
                                      HttpServletRequest request) {
        Float result = null;
        String value = null;
        if (isString(bean)) {
            value = (String) bean;
        } else {
            value = ValidatorUtil.getValueAsString(bean, field.getProperty());
        }

        if (!GenericValidator.isBlankOrNull(value)) {
            result = GenericTypeValidator.formatFloat(value);

            if (result == null) {
                errors.add(field.getKey(), Resources.getActionError(request, va, field));
            }
        }

        return result;
    }


    /**
     *  <p>
     *
     *  Checks if the field can safely be converted to a double primitive.</p>
     *
     *@param  bean     The bean validation is being performed on.
     *@param  va       The <code>ValidatorAction</code> that is currently being performed.
     *@param  field    The <code>Field</code> object associated with the current
     *      field being validated.
     *@param  errors   The <code>ActionErrors</code> object to add errors to if any
     *      validation errors occur.
     *@param  request  Current request object.
     *@return          A Double if valid, a null otherwise.
     */
    public static Double validateDouble(Object bean,
                                        ValidatorAction va, Field field,
                                        ActionErrors errors,
                                        HttpServletRequest request) {
        Double result = null;
        String value = null;
        if (isString(bean)) {
            value = (String) bean;
        } else {
            value = ValidatorUtil.getValueAsString(bean, field.getProperty());
        }

        if (!GenericValidator.isBlankOrNull(value)) {
            result = GenericTypeValidator.formatDouble(value);

            if (result == null) {
                errors.add(field.getKey(), Resources.getActionError(request, va, field));
            }
        }

        return result;
    }


    /**
     *  <p>
     *
     *  Checks if the field is a valid date. If the field has a datePattern variable,
     *  that will be used to format <code>java.text.SimpleDateFormat</code>. If the
     *  field has a datePatternStrict variable, that will be used to format <code>java.text.SimpleDateFormat</code>
     *  and the length will be checked so '2/12/1999' will not pass validation with
     *  the format 'MM/dd/yyyy' because the month isn't two digits. If no datePattern
     *  variable is specified, then the field gets the DateFormat.SHORT format for
     *  the locale. The setLenient method is set to <code>false</code> for all variations.
     *  </p>
     *
     *@param  bean     The bean validation is being performed on.
     *@param  va       The <code>ValidatorAction</code> that is currently being performed.
     *@param  field    The <code>Field</code> object associated with the current
     *      field being validated.
     *@param  errors   The <code>ActionErrors</code> object to add errors to if any
     *      validation errors occur.
     *@param  request  Current request object.
     *@return          A Date if valid, a null if blank or invalid.
     */
    public static Date validateDate(Object bean,
                                    ValidatorAction va, Field field,
                                    ActionErrors errors,
                                    HttpServletRequest request) {

        Date result = null;
        String value = null;
        if (isString(bean)) {
            value = (String) bean;
        } else {
            value = ValidatorUtil.getValueAsString(bean, field.getProperty());
        }
        String datePattern = field.getVarValue("datePattern");
        String datePatternStrict = field.getVarValue("datePatternStrict");
        Locale locale = Resources.getLocale(request);

        if (!GenericValidator.isBlankOrNull(value)) {
            try {
                if (datePattern != null && datePattern.length() > 0) {
                    result = GenericTypeValidator.formatDate(value, datePattern, false);
                } else if (datePatternStrict != null && datePatternStrict.length() > 0) {
                    result = GenericTypeValidator.formatDate(value, datePatternStrict, true);
                } else {
                    result = GenericTypeValidator.formatDate(value, locale);
                }
            } catch (Exception e) {
                LOG.error(e.getMessage(), e);
            }

            if (result == null) {
                errors.add(field.getKey(), Resources.getActionError(request, va, field));
            }
        }

        return result;
    }

    /**
     *  <p>
     *
     *  Checks if a fields value is within a range (min &amp; max specified in the
     *  vars attribute).</p>
     *@deprecated  As of Struts 1.1b3, replaced by {@link #validateIntRange(java.lang.Object,org.apache.commons.validator.ValidatorAction,org.apache.commons.validator.Field,org.apache.struts.action.ActionErrors,javax.servlet.http.HttpServletRequest)}
     *@param  bean     The bean validation is being performed on.
     *@param  va       The <code>ValidatorAction</code> that is currently being performed.
     *@param  field    The <code>Field</code> object associated with the current
     *      field being validated.
     *@param  errors   The <code>ActionErrors</code> object to add errors to if any
     *      validation errors occur.
     *@param  request  Current request object.
     *@return          True if in range, false otherwise.
     */
    public static boolean validateRange(Object bean,
                                        ValidatorAction va, Field field,
                                        ActionErrors errors,
                                        HttpServletRequest request) {
        return validateIntRange(bean, va, field, errors, request);
    }

    /**
     *  <p>
     *
     *  Checks if a fields value is within a range (min &amp; max specified in the
     *  vars attribute).</p>
     *
     *@param  bean     The bean validation is being performed on.
     *@param  va       The <code>ValidatorAction</code> that is currently being performed.
     *@param  field    The <code>Field</code> object associated with the current
     *      field being validated.
     *@param  errors   The <code>ActionErrors</code> object to add errors to if any
     *      validation errors occur.
     *@param  request  Current request object.
     *@return          True if in range, false otherwise.
     */
    public static boolean validateIntRange(Object bean,
                                           ValidatorAction va, Field field,
                                           ActionErrors errors,
                                           HttpServletRequest request) {

        String value = null;
        if (isString(bean)) {
            value = (String) bean;
        } else {
            value = ValidatorUtil.getValueAsString(bean, field.getProperty());
        }
        String sMin = field.getVarValue("min");
        String sMax = field.getVarValue("max");

        if (!GenericValidator.isBlankOrNull(value)) {
            try {
                int iValue = Integer.parseInt(value);
                int min = Integer.parseInt(sMin);
                int max = Integer.parseInt(sMax);

                if (!GenericValidator.isInRange(iValue, min, max)) {
                    errors.add(field.getKey(), Resources.getActionError(request, va, field));

                    return false;
                }
            } catch (Exception e) {
                errors.add(field.getKey(), Resources.getActionError(request, va, field));
                return false;
            }
        }

        return true;
    }

    /**
     *  <p>
     *
     *  Checks if a fields value is within a range (min &amp; max specified in the
     *  vars attribute).</p>
     *
     *@param  bean     The bean validation is being performed on.
     *@param  va       The <code>ValidatorAction</code> that is currently being performed.
     *@param  field    The <code>Field</code> object associated with the current
     *      field being validated.
     *@param  errors   The <code>ActionErrors</code> object to add errors to if any
     *      validation errors occur.
     *@param  request  Current request object.
     *@return          True if in range, false otherwise.
     */
    public static boolean validateDoubleRange(Object bean,
                                              ValidatorAction va, Field field,
                                              ActionErrors errors,
                                              HttpServletRequest request) {

        String value = null;
        if (isString(bean)) {
            value = (String) bean;
        } else {
            value = ValidatorUtil.getValueAsString(bean, field.getProperty());
        }
        String sMin = field.getVarValue("min");
        String sMax = field.getVarValue("max");

        if (!GenericValidator.isBlankOrNull(value)) {
            try {
                double dValue = Double.parseDouble(value);
                double min = Double.parseDouble(sMin);
                double max = Double.parseDouble(sMax);

                if (!GenericValidator.isInRange(dValue, min, max)) {
                    errors.add(field.getKey(), Resources.getActionError(request, va, field));

                    return false;
                }
            } catch (Exception e) {
                errors.add(field.getKey(), Resources.getActionError(request, va, field));
                return false;
            }
        }

        return true;
    }

    /**
     *  <p>
     *
     *  Checks if a fields value is within a range (min &amp; max specified in the
     *  vars attribute).</p>
     *
     *@param  bean     The bean validation is being performed on.
     *@param  va       The <code>ValidatorAction</code> that is currently being performed.
     *@param  field    The <code>Field</code> object associated with the current
     *      field being validated.
     *@param  errors   The <code>ActionErrors</code> object to add errors to if any
     *      validation errors occur.
     *@param  request  Current request object.
     *@return          True if in range, false otherwise.
     */
    public static boolean validateFloatRange(Object bean,
                                             ValidatorAction va, Field field,
                                             ActionErrors errors,
                                             HttpServletRequest request) {

        String value = null;
        if (isString(bean)) {
            value = (String) bean;
        } else {
            value = ValidatorUtil.getValueAsString(bean, field.getProperty());
        }
        String sMin = field.getVarValue("min");
        String sMax = field.getVarValue("max");

        if (!GenericValidator.isBlankOrNull(value)) {
            try {
                float fValue = Float.parseFloat(value);
                float min = Float.parseFloat(sMin);
                float max = Float.parseFloat(sMax);

                if (!GenericValidator.isInRange(fValue, min, max)) {
                    errors.add(field.getKey(), Resources.getActionError(request, va, field));

                    return false;
                }
            } catch (Exception e) {
                errors.add(field.getKey(), Resources.getActionError(request, va, field));
                return false;
            }
        }

        return true;
    }


    /**
     *  <p>
     *
     *  Checks if the field is a valid credit card number.</p> <p>
     *
     *  Translated to Java by Ted Husted (<a href="mailto:husted@apache.org">husted@apache.org
     *  </a>).<br>
     *  &nbsp;&nbsp;&nbsp; Reference Sean M. Burke's script at http://www.ling.nwu.edu/~sburke/pub/luhn_lib.pl
     *  </p>
     *
     *@param  bean     The bean validation is being performed on.
     *@param  va       The <code>ValidatorAction</code> that is currently being performed.
     *@param  field    The <code>Field</code> object associated with the current
     *      field being validated.
     *@param  errors   The <code>ActionErrors</code> object to add errors to if any
     *      validation errors occur.
     *@param  request  Current request object.
     *@return          The credit card as a Long, a null if invalid, blank, or null.
     */
    public static Long validateCreditCard(Object bean,
                                          ValidatorAction va, Field field,
                                          ActionErrors errors,
                                          HttpServletRequest request) {

        Long result = null;
        String value = null;
        if (isString(bean)) {
            value = (String) bean;
        } else {
            value = ValidatorUtil.getValueAsString(bean, field.getProperty());
        }

        if (!GenericValidator.isBlankOrNull(value)) {
            result = GenericTypeValidator.formatCreditCard(value);

            if (result == null) {
                errors.add(field.getKey(), Resources.getActionError(request, va, field));
            }
        }

        return result;
    }


    /**
     *  <p>
     *
     *  Checks if a field has a valid e-mail address.</p> <p>
     *
     *  Based on a script by Sandeep V. Tamhankar (stamhankar@hotmail.com), http://javascript.internet.com
     *  </p>
     *
     *@param  bean     The bean validation is being performed on.
     *@param  va       The <code>ValidatorAction</code> that is currently being performed.
     *@param  field    The <code>Field</code> object associated with the current
     *      field being validated.
     *@param  errors   The <code>ActionErrors</code> object to add errors to if any
     *      validation errors occur.
     *@param  request  Current request object.
     *@return          True if valid, false otherwise.
     */
    public static boolean validateEmail(Object bean,
                                        ValidatorAction va, Field field,
                                        ActionErrors errors,
                                        HttpServletRequest request) {

        String value = null;
        if (isString(bean)) {
            value = (String) bean;
        } else {
            value = ValidatorUtil.getValueAsString(bean, field.getProperty());
        }

        if (!GenericValidator.isBlankOrNull(value) && !GenericValidator.isEmail(value)) {
            errors.add(field.getKey(), Resources.getActionError(request, va, field));
            return false;
        } else {
            return true;
        }
    }


    /**
     *  <p>
     *
     *  Checks if the field's length is less than or equal to the maximum value.
     *  A <code>Null</code> will be considered an error.</p>
     *
     *@param  bean     The bean validation is being performed on.
     *@param  va       The <code>ValidatorAction</code> that is currently being performed.
     *@param  field    The <code>Field</code> object associated with the current
     *      field being validated.
     *@param  errors   The <code>ActionErrors</code> object to add errors to if any
     *      validation errors occur.
     *@param  request  Current request object.
     *@return          True if stated conditions met.
     */
    public static boolean validateMaxLength(Object bean,
                                            ValidatorAction va, Field field,
                                            ActionErrors errors,
                                            HttpServletRequest request) {

        String value = null;
        if (isString(bean)) {
            value = (String) bean;
        } else {
            value = ValidatorUtil.getValueAsString(bean, field.getProperty());
        }
        String sMaxLength = field.getVarValue("maxlength");

        if (value != null) {
            try {
                int max = Integer.parseInt(sMaxLength);

                if (!GenericValidator.maxLength(value, max)) {
                    errors.add(field.getKey(), Resources.getActionError(request, va, field));

                    return false;
                }
            } catch (Exception e) {
                errors.add(field.getKey(), Resources.getActionError(request, va, field));
                return false;
            }
        }

        return true;
    }


    /**
     *  <p>
     *
     *  Checks if the field's length is greater than or equal to the minimum value.
     *  A <code>Null</code> will be considered an error.</p>
     *
     *@param  bean     The bean validation is being performed on.
     *@param  va       The <code>ValidatorAction</code> that is currently being performed.
     *@param  field    The <code>Field</code> object associated with the current
     *      field being validated.
     *@param  errors   The <code>ActionErrors</code> object to add errors to if any
     *      validation errors occur.
     *@param  request  Current request object.
     *@return          True if stated conditions met.
     */
    public static boolean validateMinLength(Object bean,
                                            ValidatorAction va, Field field,
                                            ActionErrors errors,
                                            HttpServletRequest request) {

        String value = null;
        if (isString(bean)) {
            value = (String) bean;
        } else {
            value = ValidatorUtil.getValueAsString(bean, field.getProperty());
        }
        String sMinLength = field.getVarValue("minlength");

        if (value != null) {
            try {
                int min = Integer.parseInt(sMinLength);

                if (!GenericValidator.minLength(value, min)) {
                    errors.add(field.getKey(), Resources.getActionError(request, va, field));

                    return false;
                }
            } catch (Exception e) {
                errors.add(field.getKey(), Resources.getActionError(request, va, field));
                return false;
            }
        }

        return true;
    }


    /**
     *  <p>
     *
     *  Return <code>true</code> if the specified object is a String or a <code>null</code>
     *  value.</p>
     *
     *@param  o  Object to be tested
     *@return    The string value
     */
    public static boolean isString(Object o) {

        if (o == null) {
            return (true);
        }
        return (String.class.isInstance(o));
    }

}
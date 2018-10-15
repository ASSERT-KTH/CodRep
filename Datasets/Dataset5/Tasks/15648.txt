package org.apache.xerces.impl.dv.xs;

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 1999, 2000 The Apache Software Foundation.  All rights
 * reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in
 *    the documentation and/or other materials provided with the
 *    distribution.
 *
 * 3. The end-user documentation included with the redistribution,
 *    if any, must include the following acknowledgment:
 *       "This product includes software developed by the
 *        Apache Software Foundation (http://www.apache.org/)."
 *    Alternately, this acknowledgment may appear in the software itself,
 *    if and wherever such third-party acknowledgments normally appear.
 *
 * 4. The names "Xerces" and "Apache Software Foundation" must
 *    not be used to endorse or promote products derived from this
 *    software without prior written permission. For written
 *    permission, please contact apache@apache.org.
 *
 * 5. Products derived from this software may not be called "Apache",
 *    nor may "Apache" appear in their name, without prior written
 *    permission of the Apache Software Foundation.
 *
 * THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESSED OR IMPLIED
 * WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
 * OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED.  IN NO EVENT SHALL THE APACHE SOFTWARE FOUNDATION OR
 * ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
 * USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
 * OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
 * OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
 * SUCH DAMAGE.
 * ====================================================================
 *
 * This software consists of voluntary contributions made by many
 * individuals on behalf of the Apache Software Foundation and was
 * originally based on software copyright (c) 1999, International
 * Business Machines, Inc., http://www.apache.org.  For more
 * information on the Apache Software Foundation, please see
 * <http://www.apache.org/>.
 */

package org.apache.xerces.impl.v2.datatypes;

import java.util.ListResourceBundle;
import java.util.Locale;
import java.util.ResourceBundle;
import java.util.MissingResourceException;
import org.apache.xerces.util.MessageFormatter;



/**
 *
 * @author Jeffrey Rodriguez
 * @version $Id$
 */
public class DatatypeMessageProvider implements MessageFormatter {
    /**
     * The domain of messages concerning the XML Schema: Datatypes specification.
     */
    public static final String DATATYPE_DOMAIN = "http://www.w3.org/TR/xml-schema-2";

    /**
     * Set the locale used for error messages
     *
     * @param locale the new locale
     */
    public void setLocale(Locale locale) {
        fLocale = locale;
    }
    /**
     * get the local used for error messages
     *
     * @return the locale
     */
    public Locale getLocale() {
        return fLocale;
    }

    //
    // MessageFormatter methods
    //

    /**
     * Formats a message with the specified arguments using the given
     * locale information.
     * 
     * @param locale    The locale of the message.
     * @param key       The message key.
     * @param arguments The message replacement text arguments. The order
     *                  of the arguments must match that of the placeholders
     *                  in the actual message.
     * 
     * @return Returns the formatted message.
     *
     * @throws MissingResourceException Thrown if the message with the
     *                                  specified key cannot be found.
     */
    public String formatMessage(Locale locale, String key, Object[] args)
        throws MissingResourceException {
        boolean throwex = false;
        if ( fResourceBundle == null || locale != fLocale ) {
            if ( locale != null )
                fResourceBundle = ListResourceBundle.getBundle("org.apache.xerces.impl.msg.DatatypeMessages", locale);
            if ( fResourceBundle == null )
                fResourceBundle = ListResourceBundle.getBundle("org.apache.xerces.impl.msg.DatatypeMessages");
        }
        int majorCode = -1;
        for (int i = 0; i < fgMessageKeys.length; i++) {
            if (fgMessageKeys[i].equals(key)) {
                majorCode = i;
                break;
            }
        }
        if (majorCode == -1) {
            majorCode = MSG_BAD_MAJORCODE;
            throwex = true;
        }
        String msgKey = fgMessageKeys[majorCode];
        String msg = fResourceBundle.getString(msgKey);
        if ( args != null ) {
            try {
                msg = java.text.MessageFormat.format(msg, args);
            }
            catch ( Exception e ) {
                msg = fResourceBundle.getString(fgMessageKeys[MSG_FORMAT_FAILURE]);
                msg += " " + fResourceBundle.getString(msgKey);
            }
        }

        if ( throwex ) {
            throw new RuntimeException(msg);
        }
        return msg;
    }
    //
    //
    //
    private Locale fLocale = null;
    private ResourceBundle fResourceBundle = null;
    //
    // Major Codes
    //
    private static int counter = 0;
    public static final int
    MSG_BAD_MAJORCODE  = counter++,              //  majorCode parameter to createMessage was out of bounds
    MSG_FORMAT_FAILURE = counter++,             //  exception thrown during messageFormat call
    NOT_BOOLEAN        = counter++,
    NOT_DECIMAL        = counter++,
    NOT_FLOAT          = counter++,
    NOT_DOUBLE         = counter++,
    INVALID_ENUM_VALUE = counter++,
    OUT_OF_BOUNDS      = counter++,
    NOT_ENUM_VALUE      = counter++,
    FRACTION_GREATER_TOTALDIGITS   = counter++,
    FRACTION_EXCEEDED      = counter++,
    TOTALDIGITS_EXCEEDED   = counter++,
    ILLEGAL_FACET_VALUE    = counter++,
    ILLEGAL_ANYURI_FACET   = counter++,
    ILLEGAL_BOOLEAN_FACET  = counter++,
    ILLEGAL_BASE64_FACET   = counter++,
    ILLEGAL_DATETIME_FACET = counter++,
    ILLEGAL_DECIMAL_FACET  = counter++,
    ILLEGAL_DOUBLE_FACET   = counter++,
    ILLEGAL_FLOAT_FACET    = counter++,
    ILLEGAL_HEXBINARY_FACET  = counter++,
    ILLEGAL_NOTATION_FACET   = counter++,
    ILLEGAL_QNAME_FACET      = counter++,
    ILLEGAL_STRING_FACET     = counter++,
    ILLEGAL_LIST_FACET       = counter++,
    ILLEGAL_UNION_FACET      = counter++,
    ILLEGAL_ANYSIMPLETYPE_FACET  = counter++,

    MSG_MAX_CODE = counter;

    //
    // Minor Codes
    //
    public static final int
    MSG_NONE = 0;

    public static final String[] fgMessageKeys = {
        "BadMajorCode",
        "FormatFailed",
        "NotBoolean",
        "NotDecimal",
        "NotFloat",
        "NotDouble",
        "InvalidEnumValue",
        "OutOfBounds",
        "NotAnEnumValue",
        "FractionDigitsLargerThanTotalDigits",
        "FractionDigitsExceeded",
        "TotalDigitsExceeded",
        "IllegalFacetValue",
        "IllegalAnyURIFacet",
        "IllegalBooleanFacet",
        "IllegalBase64Facet",
        "IllegalDateTimeFacet",
        "IllegalDecimalFacet",
        "IllegalDoubleFacet",
        "IllegalFloatFacet",
        "IllegalHexBinaryFacet",
        "IllegalNotationFacet",
        "IllegalQNameFacet",
        "IllegalStringFacet",
        "IllegalListFacet",
        "IllegalUnionFacet",
        "IllegalAnySimpleTypeFacet"
    };
}
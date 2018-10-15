"GroupContentRestricted",       //  14, "Error: {0} content must be one of choice, all or sequence.  Saw {1}"

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 2000 The Apache Software Foundation.  All rights 
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

package org.apache.xerces.validators.schema;

import org.apache.xerces.utils.XMLMessageProvider;
import java.util.ResourceBundle;
import java.util.ListResourceBundle;
import java.util.Locale;

/**
 * SchemaMessageProvider implements an XMLMessageProvider that
 * provides localizable error messages for the W3C XML Schema Language
 *
 */
public class SchemaMessageProvider implements XMLMessageProvider {
    /**
     * The domain of messages concerning the XML Schema: Structures specification.
     */
    public static final String SCHEMA_DOMAIN = "http://www.w3.org/TR/xml-schema-1";

    /**
     *
     */
    public void setLocale(Locale locale) {
        fLocale = locale;
    }
    /**
     *
     */
    public Locale getLocale() {
        return fLocale;
    }

    /**
     * Creates a message from the specified key and replacement
     * arguments, localized to the given locale.
     *
     * @param locale    The requested locale of the message to be
     *                  created.
     * @param key       The key for the message text.
     * @param args      The arguments to be used as replacement text
     *                  in the message created.
     */
    public String createMessage(Locale locale, int majorCode, int minorCode, Object args[]) {
        boolean throwex = false;
        if (fResourceBundle == null || locale != fLocale) {
            if (locale != null)
                fResourceBundle = ListResourceBundle.getBundle("org.apache.xerces.msg.SchemaMessages", locale);
            if (fResourceBundle == null)
                fResourceBundle = ListResourceBundle.getBundle("org.apache.xerces.msg.SchemaMessages");
        }
        if (majorCode < 0 || majorCode >= fgMessageKeys.length) {
            majorCode = MSG_BAD_MAJORCODE;
            throwex = true;
        }
        String msgKey = fgMessageKeys[majorCode];
        String msg = fResourceBundle.getString(msgKey);
        if (args != null) {
            try {
                msg = java.text.MessageFormat.format(msg, args);
            } catch (Exception e) {
                msg = fResourceBundle.getString(fgMessageKeys[MSG_FORMAT_FAILURE]);
                msg += " " + fResourceBundle.getString(msgKey);
            }
        }

        if (throwex) {
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
    // Major codes
    //
    public static final int 
        MSG_BAD_MAJORCODE = 0,              //  majorCode parameter to createMessage was out of bounds
        MSG_FORMAT_FAILURE = 1,             //  exception thrown during messageFormat call
        NoValidatorFor = 2,
        IncorrectDatatype = 3,
        AttMissingType = 4,
        NotADatatype = 5,
        TextOnlyContentWithType = 6,
        FeatureUnsupported = 7,
        NestedOnlyInElemOnly = 8,
        EltRefOnlyInMixedElemOnly = 9,
        OnlyInEltContent = 10,
        OrderIsAll = 11,
        DatatypeWithType = 12,
        DatatypeQualUnsupported = 13,
        GroupContentRestricted = 14,
        UnknownBaseDatatype = 15,
        BadAttWithRef = 16,
        NoContentForRef = 17,
        IncorrectDefaultType = 18,
        IllegalAttContent = 19,
        ValueNotInteger = 20,
        DatatypeError = 21,
		TypeAlreadySet = 22,
		GenericError = 23,
		UnclassifiedError = 24,
        ContentError = 25,
        AnnotationError = 26,
        ListUnionRestrictionError = 27,
        ProhibitedAttributePresent = 28,
        // identity constaints
        UniqueNotEnoughValues = 29,
        KeyNotEnoughValues = 30,
        KeyRefNotEnoughValues = 31,
        DuplicateField = 32,
        DuplicateUnique = 33,
        DuplicateKey = 34,
        KeyNotFound = 35,
        UnknownField = 36,
        // ...
        MSG_MAX_CODE = 37;
    //
    // Minor Codes
    //
    public static final int
        MSG_NONE = 0;

    public static final String[] fgMessageKeys = {
        "BadMajorCode",                 //   0, "The majorCode parameter to createMessage was out of bounds."
        "FormatFailed",                 //   1, "An internal error occurred while formatting the following message:"
        "NoValidatorFor",               //   2, "No validator for datatype {0}"
        "IncorrectDatatype",            //   3, "Incorrect datatype: {0}" 
        "AttMissingType",               //   4, "The {0} attribute must appear with a type attribute."
        "NotADatatype",                 //   5, "{0} is not a datatype."
        "TextOnlyContentWithType",      //   6, "The content attribute must be 'textOnly' if you specify a type attribute." 
        "FeatureUnsupported",           //   7, "{0} is unsupported"
        "NestedOnlyInElemOnly",         //   8, "Nested Element decls only allowed in elemOnly content"
        "EltRefOnlyInMixedElemOnly",    //   9, "Element references only allowed in mixed or elemOnly content"
        "OnlyInEltContent",             //  10, "{0} only allowed in elemOnly content."
        "OrderIsAll",                   //  11, "{0} not allowed if the order is all."
        "DatatypeWithType",             //  12, "Datatype qualifiers can only be used if you specify a type attribute."},
        "DatatypeQualUnsupported",      //  13, "The datatype qualifier {0} is not supported."
        "GroupContentRestricted",       //  14, "Error: {0} content must be one of element, group, modelGroupRef.  Saw {1}"
        "UnknownBaseDatatype",          //  15, "Unknown base type {0} for type {1}." },
        "BadAttWithRef",          //  16, "ref cannot appear with any of type, abstract, block, final, nullable, default or fixed"},
        "NoContentForRef",              //  17, "Cannot have child content for an element declaration that has a ref attribute"
        "IncorrectDefaultType",         //  18, "Incorrect type for {0}'s default value: {1}"
        "IllegalAttContent",            //  19, "Illegal content {0} in attribute group"
        "ValueNotInteger",              //  20, "Value of {0} is not an integer"
        "DatatypeError",                //  21, "Datatype error {0}." 
		"TypeAlreadySet",				//	22,	"The type of the element has already been declared."
		"GenericError",					//	23, "Schema error: {0}."
		"UnclassifiedError",			//	24,	"Unclassified error."
        "ContentError",                 //  25, "Content (annotation?,..) is incorrect for type {0}"
        "AnnotationError",                //  26, "Annotation can only appear once: type {0}"
        "ListUnionRestrictionError",       //  27, "List | Union | Restriction content is invalid for type {0}"
        "ProhibitedAttributePresent",	    		// 	28,	attribue dcld prohibited is present
        // identity constraint keys
        "UniqueNotEnoughValues",
        "KeyNotEnoughValues",
        "KeyRefNotEnoughValues",
        "DuplicateField",
        "DuplicateUnique",
        "DuplicateKey",
        "KeyNotFound",
        "UnknownField",
        // END
    };
}
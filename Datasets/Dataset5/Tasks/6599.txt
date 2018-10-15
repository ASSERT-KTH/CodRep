{"MinMaxOnGroupChild", "Error:  The child ''{1}'' of the named group definition ''{0}'' must not specify either the minOccurs or maxOccurs attribute."},

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 1999,2000 The Apache Software Foundation.  All rights
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

package org.apache.xerces.msg;

import java.util.ListResourceBundle;

/**
 * This file contains error and warning messages for the Schema validator
 * The messages are arranged in key and value tuples in a ListResourceBundle.
 *
 * @version $Id$
 */
public class SchemaMessages extends ListResourceBundle {
    /** The list resource bundle contents. */
    public static final Object CONTENTS[][] = {
// Internal message formatter messages
        { "BadMajorCode", "The majorCode parameter to createMessage was out of bounds." },
        { "FormatFailed", "An internal error occurred while formatting the following message:\n  " },
        { "NoValidatorFor", "No validator for datatype {0}" },
        { "IncorrectDatatype", "Incorrect datatype: {0}" },
        { "NotADatatype", "{0} is not a datatype." },
        { "TextOnlyContentWithType", "The content attribute must be 'textOnly' if you specify a type attribute." },
        { "FeatureUnsupported", "{0} is unsupported" },
        { "NestedOnlyInElemOnly", "Nested Element decls only allowed in elementOnly content" },
        { "EltRefOnlyInMixedElemOnly", "Element references only allowed in mixed or elementOnly content"},
        { "OnlyInEltContent", "{0} only allowed in elementOnly content."},
        { "OrderIsAll", "{0} not allowed if the order is all."},
        { "DatatypeWithType", "Datatype qualifiers can only be used if you specify a type attribute."},
        { "DatatypeQualUnsupported", "The datatype qualifier {0} is not supported."},
        { "GroupContentRestricted", "Error: {0} content must be one of choice, all or sequence.  Saw {1}."},
        { "UnknownBaseDatatype", "Unknown base type {0} for type {1}." },
        { "BadAttWithRef", "cannot use ref with any of type, block, final, abstract, nillable, default or fixed."},
        { "NoContentForRef", "Cannot have child content for an element declaration that has a ref attribute" },
        { "IncorrectDefaultType", "Incorrect type for {0}'s default value: {1}" },
        { "IllegalAttContent", "Illegal content {0} in attribute group" },
        { "ValueNotInteger", "Value of {0} is not an integer." },
        { "DatatypeError", "Datatype error: {0}." },
        { "TypeAlreadySet", "The type of the element has already been declared." },
        { "GenericError", "Schema error: {0}." },
        { "UnexpectedError", "UnexpectedError" },
        {"ContentError", "Content (annotation?,..) is incorrect for type {0}"},
        {"AnnotationError", "Annotation can only appear once: type {0}"},
        {"ListUnionRestrictionError","List | Union | Restriction content is invalid for type {0}"},
        { "ProhibitedAttributePresent", "An attribute declared \"prohibited\" is present in this element definition." },
        // identity constraints
        { "UniqueNotEnoughValues", "Not enough values specified for <unique> identity constraint specified for element \"{0}\"." },
        { "KeyNotEnoughValues", "Not enough values specified for <key name=\"{1}\"> identity constraint specified for element \"{0}\"." },
        { "KeyRefNotEnoughValues", "Not enough values specified for <keyref name=\"{1}\"> identity constraint specified for element \"{0}\"." },
        { "DuplicateField", "Duplicate match in scope for field \"{0}\"." },
        { "DuplicateUnique", "Duplicate unique value [{0}] declared for identity constraint of element \"{1}\"." },
        { "DuplicateKey", "Duplicate key value [{0}] declared for identity constraint of element \"{1}\"." },
        { "KeyNotFound", "Key with value [{0}] not found for identity constraint of element \"{1}\"." },
        { "UnknownField", "Internal identity constraint error; unknown field \"{0}\"." },
        { "KeyRefReferNotFound", "Key reference declaration \"{0}\" refers to unknown key with name \"{1}\"." },
        { "FixedDiffersFromActual", "The content of this element is not equivalent to the value of the \"fixed\" attribute in the element's declaration in the schema."},
        // simpleType
        {"InvalidBaseType", "itemType \"{0}\" must have a variety of atomic or union"},
        {"FieldMultipleMatch", "Identity constraint error:  field \"{0}\" matches more than one value within the scope of its selector; fields must match unique values"},
        {"KeyRefOutOfScope", "Identity Constraint error:  identity constraint \"{0}\" has a keyref which refers to a key or unique that is out of scope."},
        {"AbsentKeyValue", "Identity Constraint error (cvc-identity-constraint.4.2.1):  element \"{0}\" has a key with no value."},
        {"KeyMatchesNillable", "Identity Constraint error (cvc-identity-constraint.4.2.3):  element \"{0}\" has a key which matches an element which has nillable set to true."},
        {"BadMinMaxForAllElem", "cos-all-limited.2:  The {0} attribute of an element in an all schema component must have the value zero or one.  The value \"{1}\" is incorrect."},
        {"BadMinMaxForGroupWithAll", "Error:  cos-all-limited.1.2:  The {0} attribute in a reference to a named model group whose content model is \"all\" must have the value one.  The value \"{1}\" is incorrect."},
        {"SeqChoiceContentRestricted", "Error:  {0} content must be zero or more of element, group, choice, sequence or any.  Saw \"{1}\"."},
        {"AllContentRestricted", "Error:  The content of all is restricted to zero or more elements.  Saw \"{0}\"."},
        {"AllContentLimited", "Error:  cos-all-limited.1.2: A group whose content is \"all\" must only appear as the content type of a complex type definition.  Saw group in \"{0}\"."},
        {"MinMaxOnGroupChild", "Error:  The child of a model group definition must not specify either the minOccurs or maxOccurs attribute."},
        {"BadMinMaxForAllGp", "Error:  cos-all-limited.1.2:  The {0} attribute of a model group with \"all\" compositor that is part of a pair that is the content type of a complex type definition must have the value one.  The value \"{1}\" is incorrect."},
        {"SchemaLocation", "Value \"{0}\" is not valid 'schemaLocation' syntax. anyURI must be followed by schema file"},
        {"UniqueParticleAttribution", "Error: cos-nonambig: ({0}) and ({1}) violate the \"Unique Particle Attribution\" rule."},
        {"Con3X3ElementAppearance", "Error: constraint 3.x.3: Element ''{0}'' cannot appear here."},
        {"Con3X3AttributeAppearance", "Error: constraint 3.x.3: Attribute ''{1}'' cannot appear in element ''{0}''."},
        {"Con3X3AttributeMustAppear", "Error: constraint 3.x.3: Attribute ''{1}'' must appear in element ''{0}''."},
        {"Con3X3AttributeInvalidValue", "Error: constraint 3.x.3: Invalid attribute value for ''{1}'' in element ''{0}'': {2}."},
    };

    /** Returns the list resource bundle contents. */
    public Object[][] getContents() {
        return CONTENTS;
    }

}
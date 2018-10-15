return fDeclaration.fType.getTypeName();

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 2000,2001 The Apache Software Foundation.  
 * All rights reserved.
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
 * originally based on software copyright (c) 2001, International
 * Business Machines, Inc., http://www.apache.org.  For more
 * information on the Apache Software Foundation, please see
 * <http://www.apache.org/>.
 */

package org.apache.xerces.impl.xs;

import org.apache.xerces.impl.xs.XSElementDecl;
import org.apache.xerces.impl.xs.XSNotationDecl;
import org.apache.xerces.xni.QName;
import org.apache.xerces.xni.psvi.ElementPSVI;

import java.util.Vector;


/**
 * Element PSV infoset augmentations implementation.
 * The following information will be available at the startElement call:
 * name, namespace, type, notation, default(?), validation context
 * 
 * The following information will be available at the endElement call:
 * nil, specified, normalized value, member type, validity, error codes
 * 
 * @author Elena Litani IBM
 */
public class ElementPSVImpl implements ElementPSVI {


    protected XSElementDecl fDeclaration = null;
    protected XSNotationDecl fNotation = null;
    // should be simpleType decl
    protected XSTypeDecl fMemberType = null;
    protected short fValidationAttempted = ElementPSVI.NO_VALIDATION;
    protected short fValidity = ElementPSVI.UNKNOWN_VALIDITY;
    protected Vector fErrorCodes = new Vector(10);
    protected String fValidationContext = null;
    protected String fTargetNS = null;

    //
    // ElementPSVI methods
    //

    /**
     * [member type definition anonymous]
     * @ see http://www.w3.org/TR/xmlschema-1/#e-member_type_definition_anonymous
     * @return true if the {name} of the actual member type definition is absent, 
     *         otherwise false.
     */
    public boolean  isMemberTypeAnonymous() {
        // REVISIT: implement
        return false;

    }

    /**
     * [member type definition name]
     * @see http://www.w3.org/TR/xmlschema-1/#e-member_type_definition_name
     * @return The {name} of the actual member type definition, if it is not absent.
     *         If it is absent, schema processors may, but need not, provide a
     *         value unique to the definition.
     */
    public String   getMemberTypeName() {
        // REVISIT: implement
        return null;
    }

    /**
     * [member type definition namespace]
     * @see http://www.w3.org/TR/xmlschema-1/#e-member_type_definition_namespace
     * @return The {target namespace} of the actual member type definition.
     */
    public String   getMemberTypeNamespace() {

        // REVISIT: implement
        return null;
    }

    /**
     * [schema default]
     * 
     * @return The canonical lexical representation of the declaration's {value constraint} value.
     * @see http://www.w3.org/TR/xmlschema-1/#e-schema_default
     */
    public String   schemaDefault() {
        Object dValue = null;
        if (fDeclaration !=null) {
            dValue = fDeclaration.fDefault;
        }
        return(dValue !=null)?dValue.toString():null;
    }

    /**
     * [schema normalized value] 
     * 
     * 
     * @see http://www.w3.org/TR/xmlschema-1/#e-schema_normalized_value
     * @return 
     */
    public String schemaNormalizedValue() {

        // REVISIT: implement
        return null;
    }

    /**
     * [schema specified] 
     * @see http://www.w3.org/TR/xmlschema-1/#e-schema_specified
     * @return 
     */
    public boolean schemaSpecified() {
        if (fDeclaration !=null) {
            return(fDeclaration.getConstraintType() != fDeclaration.NO_CONSTRAINT);
        }
        return false;
    }


    /**
     * [type definition anonymous]
     * @see http://www.w3.org/TR/xmlschema-1/#e-type_definition_anonymous
     * @return true if the {name} of the type definition is absent, otherwise false.
     */
    public boolean isTypeAnonymous() {

        // REVISIT: implement
        //return fDeclaration.fType().isAnonymous();
        return false;
    }

    /**
     * [type definition name]
     * @see http://www.w3.org/TR/xmlschema-1/#e-type_definition_name
     * @return The {name} of the type definition, if it is not absent.
     *         If it is absent, schema processors may, but need not,
     *         provide a value unique to the definition.
     */
    public String getTypeName() {

        if (fDeclaration !=null && fDeclaration.fType !=null) {
            return fDeclaration.fType.getXSTypeName();
        }
        return null;
    }

    /**
     * [type definition namespace]
     * @see http://www.w3.org/TR/xmlschema-1/#e-member_type_definition_namespace
     * @return The {target namespace} of the type definition.
     */
    public String getTypeNamespace() {

        // REVISIT: implement
        //return fDeclaration.fType.getTargetNS();
        return null;

    }

    /**
     * [type definition type] 
     * 
     *  @see http://www.w3.org/TR/xmlschema-1/#a-type_definition_type
     *  @see http://www.w3.org/TR/xmlschema-1/#e-type_definition_type
     *  @return simple or complex, depending on the type definition. 
     */
    public short getTypeDefinitionType() {
        if (fDeclaration !=null && fDeclaration.fType !=null) {
            return fDeclaration.fType.getXSType();    
        }
        // if there was an error and element declaration was not provided
        // application should not rely on any information available via PSVI
        return XSTypeDecl.COMPLEX_TYPE;
    }

    /**
     * Determines the extent to which the document has been validated
     * 
     * @return return the [validation attempted] property. The possible values are 
     *         NO_VALIDATION, PARTIAL_VALIDATION and FULL_VALIDATION
     */
    public short getValidationAttempted() {
        return fValidationAttempted;
    }

    /**
     * Determine the validity of the node with respect 
     * to the validation being attempted
     * 
     * @return return the [validity] property. Possible values are: 
     *         UNKNOWN_VALIDITY, INVALID_VALIDITY, VALID_VALIDITY
     */
    public short getValidity() {
        return fValidity;
    }

    /**
     * A list of error codes generated from validation attempts. 
     * Need to find all the possible subclause reports that need reporting
     * 
     * @return Array of error codes
     */
    public String[] getErrorCodes() {

        // REVISIT: how should we internally store errors
        int size = fErrorCodes.size();
        if (size<=0) {
            return null;
        }
        String[] errors = new String[size];
        fErrorCodes.copyInto(errors);
        return errors;

    }


    // This is the only information we can provide in a pipeline.
    public String getValidationContext() {
        return fValidationContext;
    }

    /**
     * [nil] 
     * @see http://www.w3.org/TR/xmlschema-1/#e-nil
     * @return true if clause 3.2 of Element Locally Valid (Element) (3.3.4) above is satisfied, otherwise false 
     */
    public boolean isNil() {
        return false;
    }

    /**
     * [notation public] 
     * @see http://www.w3.org/TR/xmlschema-1/#e-notation_public
     * @see http://www.w3.org/TR/xmlschema-1/#e-notation
     * @return The value of the {public identifier} of that notation declaration. 
     */
    public String getNotationPublicId() {
        return(fNotation!=null)?fNotation.fPublicId:null;
    }

    /**
     * [notation system] 
     * 
     * @see http://www.w3.org/TR/xmlschema-1/#e-notation_system
     * @return The value of the {system identifier} of that notation declaration. 
     */
    public String getNotationSystemId() {
        return(fNotation!=null)?fNotation.fSystemId:null;
    }

    /**
     * [schema namespace] 
     * @see http://www.w3.org/TR/xmlschema-1/#nsi-schema_namespace
     * @see http://www.w3.org/TR/xmlschema-1/#e-schema_information
     * @return A namespace name or absent. 
     */
    public String getSchemaNamespace() {
        return fTargetNS;
    }


    /**
     * Reset() should be called in validator startElement(..) method.
     */
    public void reset() {

        fDeclaration = null;
        fNotation = null;
        // should be simpleType decl
        fMemberType = null;
        fValidationAttempted = ElementPSVI.NO_VALIDATION;
        fValidity = ElementPSVI.UNKNOWN_VALIDITY;
        fErrorCodes.setSize(0);
        fValidationContext = null;
        fTargetNS = null;
    }

    //
    // setter methods
    // 

    public void setErrorCode (String error) {
        // REVISIT: how should we internally store errors
        fErrorCodes.addElement(error);
    }
}
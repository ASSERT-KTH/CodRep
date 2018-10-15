public static final short VALIDITY_NOTKNOWN               = 0;

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 2000-2002 The Apache Software Foundation.  
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

package org.apache.xerces.xni.psvi;

import org.apache.xerces.impl.xs.psvi.*;

/**
 * Represent a PSVI item for one element or one attribute information item.
 *
 * @author Elena Litani, IBM
 * @version $Id$
 */

public interface ItemPSVI {

    /** Validity value indicating that validation has either not 
    been performed or that a strict assessment of validity could 
    not be performed  
    */
    public static final short VALIDITY_UNKNOWN               = 0;

    /** Validity value indicating that validation has been strictly
     assessed and the element in question is invalid according to the 
     rules of schema validation.
    */
    public static final short VALIDITY_INVALID               = 1;

    /** Validity value indicating that validation has been strictly 
     assessed and the element in question is valid according to the rules 
     of schema validation.
     */
    public static final short VALIDITY_VALID                 = 2;

    /** Validation status indicating that schema validation has been 
     performed and the element in question has specifically been skipped.   
     */
    public static final short VALIDATION_NONE                = 0;

    /** Validation status indicating that schema validation has been 
    performed on the element in question under the rules of lax validation.
    */
    public static final short VALIDATION_PARTIAL             = 1;

    /**  Validation status indicating that full schema validation has been 
    performed on the element.  */
    public static final short VALIDATION_FULL                = 2;

    /**
     * [validation context]
     * // REVISIT: what the return type should be?
     *             Should we return QName/XPath/ or element info item..?
     * 
     * @return The nearest ancestor element information item with a [schema information] property
     *         (or this element item itself if it has such a property)
     * @see <a href="http://www.w3.org/TR/xmlschema-1/#e-validation_context">XML Schema Part 1: Structures [validation context]</a>
     */
    public String getValidationContext();

    /**
     * Determine the validity of the node with respect 
     * to the validation being attempted
     * 
     * @return return the [validity] property. Possible values are: 
     *         VALIDITY_UNKNOWN, VALIDITY_INVALID, VALIDITY_VALID
     */
    public short getValidity();

    /**
     * Determines the extent to which the document has been validated
     * 
     * @return return the [validation attempted] property. The possible values are 
     *         VALIDATION_NONE, VALIDATION_PARTIAL and VALIDATION_FULL
     */
    public short getValidationAttempted();

    /**
     * A list of error codes generated from validation attempts. 
     * Need to find all the possible subclause reports that need reporting
     * 
     * @return list of error codes
     */
    public StringList getErrorCodes();
    
    /**
     * [schema normalized value] 
     * 
     * @see <a href="http://www.w3.org/TR/xmlschema-1/#e-schema_normalized_value">XML Schema Part 1: Structures [schema normalized value]</a>
     * @return the normalized value of this item after validation
     */
    public String getSchemaNormalizedValue();

    /**
     * An item isomorphic to the type definition used to validate this element.
     * 
     * @return  a type declaration
     */
    public XSTypeDefinition getTypeDefinition();
    
    /**
     * If and only if that type definition is a simple type definition
     * with {variety} union, or a complex type definition whose {content type}
     * is a simple thype definition with {variety} union, then an item isomorphic
     * to that member of the union's {member type definitions} which actually
     * validated the element item's normalized value.
     * 
     * @return  a simple type declaration
     */
    public XSSimpleTypeDefinition getMemberTypeDefinition();
    
    /**
     * [schema default]
     * 
     * @return The canonical lexical representation of the declaration's {value constraint} value.
     * @see <a href="http://www.w3.org/TR/xmlschema-1/#e-schema_default">XML Schema Part 1: Structures [schema default]</a>
     */
    public String getSchemaDefault();

    /**
     * [schema specified] 
     * @see <a href="http://www.w3.org/TR/xmlschema-1/#e-schema_specified">XML Schema Part 1: Structures [schema specified]</a>
     * @return true - value was specified in schema, false - value comes from the infoset
     */
    public boolean getIsSchemaSpecified();

}
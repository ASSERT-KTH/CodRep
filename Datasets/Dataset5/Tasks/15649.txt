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
 * originally based on software copyright (c) 2001, International
 * Business Machines, Inc., http://www.apache.org.  For more
 * information on the Apache Software Foundation, please see
 * <http://www.apache.org/>.
 */

package org.apache.xerces.impl.v2.datatypes;

import org.apache.xerces.impl.XMLErrorReporter;
import org.apache.xerces.impl.validation.EntityState;
import org.apache.xerces.impl.validation.ValidationContext;


import java.util.Hashtable;
/**
 * <P>[Definition:]   ENTITY represents the ENTITY attribute type from 
 * [XML 1.0 (Second Edition)]. The value space of ENTITY is the set of 
 * all strings that match the NCName production in [Namespaces in XML] 
 * and have been declared as an unparsed entity in a document type definition. 
 * The lexical space of ENTITY is the set of all strings that match the 
 * NCName production in [Namespaces in XML]. The base type of ENTITY is NCName. 
 * 
 * </P>
 * 
 * @author Elena Litani, IBM
 */
public class EntityDatatypeValidator extends StringDatatypeValidator {


    public EntityDatatypeValidator () {
        this( null, null, false, null );
    }

    public EntityDatatypeValidator ( DatatypeValidator base, Hashtable facets,
                                     boolean derivedByList, XMLErrorReporter reporter  ) {

        super (base, facets, derivedByList, reporter);
        fErrorReporter = reporter;
        fBaseValidator = base;
    }


    public short getWSFacet() {
        return COLLAPSE;
    }
    /**
     * <P>The following constrain is checked: ENTITY values must match an unparsed entity
     * name that is declared in the schema.</P>
     * 
     * @param content a string containing the content to be validated
     * @param state   EntityState that provides query methods
     * @return Entity name
     * @exception throws InvalidDatatypeException if the content is
     *                   invalid according to the rules for the validators
     * @exception InvalidDatatypeValueException
     */
    public Object validate(String content, ValidationContext state ) throws InvalidDatatypeValueException{
                

        super.validate(content, state);
        if (state == null) {
            throw new InvalidDatatypeValueException("EntityState is not intialized");
        }
        if (state == null) {
            return content;
        }
        if (state.isEntityDeclared(content)) {
            if (!state.isEntityUnparsed(content)){
                throw new InvalidDatatypeValueException ("Entity is not unparsed: "+content); 
            }
        }
        else {

            throw new InvalidDatatypeValueException ("Entity is not declared: "+content); 
        }
        return content;
    }


    public int compare( String  content1, String content2) {
        return (content1.equals(content2))?0:-1;
    }


    public Object clone() throws CloneNotSupportedException {
        throw new CloneNotSupportedException("clone() is not supported in "+this.getClass().getName());
    }


}
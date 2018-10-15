public Object validate(String content, ValidationContext state) throws InvalidDatatypeValueException {


/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 1999, 2000, 2001 The Apache Software Foundation.  All rights
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


import java.util.Enumeration;
import java.util.Hashtable;
import java.util.Vector;
import java.io.IOException;
import org.apache.xerces.impl.v2.SchemaSymbols;
import org.apache.xerces.impl.v2.util.regex.RegularExpression;

import org.apache.xerces.impl.XMLErrorReporter;
import org.apache.xerces.impl.v2.XSMessageFormatter;
/**
 * AbstractNumericValidator is a base class of decimal, double, and float 
 * schema datatypes
 * 
 * @author Elena Litani
 * @version $Id$
 */

public abstract class AbstractNumericValidator extends AbstractNumericFacetValidator {

    public  AbstractNumericValidator ()   {
        super( null, null, false , null); // Native, No Facets defined, Restriction
    }

    public AbstractNumericValidator ( DatatypeValidator base, 
                                      Hashtable facets, 
                                      boolean derivedByList, XMLErrorReporter reporter) {
        super (base, facets, derivedByList, reporter);
    }


    /**
     * Validate string against lexical space of datatype
     * 
     * @param content A string containing the content to be validated
     * @param state
     * @return 
     * @exception throws InvalidDatatypeException if the content is
     *                   is not a W3C decimal type
     * @exception InvalidDatatypeValueException
     */
    public Object validate(String content, Object state) throws InvalidDatatypeValueException {
        //REVISIT: should we pass state?
        checkContent(content, state, null, false);
        return null;
    }

    public Object clone() throws CloneNotSupportedException {
        throw new CloneNotSupportedException("clone() is not supported in "+this.getClass().getName());
    }

    /**
    * validate if the content is valid against base datatype and facets (if any)
    * this function might be called directly from UnionDatatype or ListDatatype
    *
    * @param content A string containing the content to be validated
    * @param enumeration A vector with enumeration strings
    * @exception throws InvalidDatatypeException if the content is
    *  is not a W3C decimal type;
    * @exception throws InvalidDatatypeFacetException if enumeration is not BigDecimal
    */
    protected void checkContentEnum(String content, Object state, Vector enumeration)
    throws InvalidDatatypeValueException {
        checkContent(content, state, enumeration, false);
    }


    //
    // content - string value to be evaluated
    //
    abstract protected void checkContent( String content, Object State, Vector enum, boolean asBase)
                              throws InvalidDatatypeValueException;


    /*
     * check that a facet is in range, assumes that facets are compatible -- compatibility ensured by setFacets
     */
    protected void boundsCheck(Object d) throws InvalidDatatypeValueException {

        boolean minOk = true;
        boolean maxOk = true;
        String  upperBound="";

        String  lowerBound="";
        String  lowerBoundIndicator = "";
        String  upperBoundIndicator = "";
        int compare;
        if ( (fFacetsDefined & DatatypeValidator.FACET_MAXINCLUSIVE) != 0 ) {
            compare = compareValues(d, fMaxInclusive);
            maxOk=(compare==1)?false:true;
            upperBound   = getMaxInclusive(false);
            if ( upperBound != null ) {
                upperBoundIndicator = "<=";
            }
            else {
                upperBound="";
            }
        }
        if ( (fFacetsDefined & DatatypeValidator.FACET_MAXEXCLUSIVE) != 0 ) {
            compare = compareValues(d, fMaxExclusive );
            maxOk = (compare==-1)?true:false;
            upperBound = getMaxExclusive (false);
            if ( upperBound != null ) {
                upperBoundIndicator = "<";
            }
            else {
                upperBound = "";
            }
        }

        if ( (fFacetsDefined & DatatypeValidator.FACET_MININCLUSIVE) != 0 ) {
            compare = compareValues(d, fMinInclusive);
            minOk = (compare==-1)?false:true;
            lowerBound = getMinInclusive (false);
            if ( lowerBound != null ) {
                lowerBoundIndicator = "<=";
            }
            else {
                lowerBound = "";
            }
        }
        if ( (fFacetsDefined & DatatypeValidator.FACET_MINEXCLUSIVE) != 0 ) {
            compare = compareValues(d, fMinExclusive);
            minOk = (compare==1)?true:false;
            lowerBound = getMinExclusive (false );
            if ( lowerBound != null ) {
                lowerBoundIndicator = "<";
            }
            else {
                lowerBound = "";
            }
        }

        if ( !(minOk && maxOk) ){
        
            String msg = getErrorString(
                DatatypeMessageProvider.fgMessageKeys[DatatypeMessageProvider.OUT_OF_BOUNDS],
                new Object [] { d.toString(), lowerBound, upperBound, lowerBoundIndicator, upperBoundIndicator});
            throw new InvalidDatatypeValueException(msg);
        }
    }



}
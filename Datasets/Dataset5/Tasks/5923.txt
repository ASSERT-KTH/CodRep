protected void checkContent(String content, ValidationContext state, Vector enumeration, boolean asBase)

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

import java.util.Enumeration;
import java.util.Hashtable;
import java.util.Vector;
import org.apache.xerces.impl.v2.SchemaSymbols;
import org.apache.xerces.impl.v2.util.regex.RegularExpression;
import java.util.StringTokenizer;
import java.util.NoSuchElementException;

import org.apache.xerces.impl.XMLErrorReporter;
import org.apache.xerces.impl.v2.XSMessageFormatter;
import org.apache.xerces.impl.validation.ValidationContext;

/**
 *
 * @author  Elena Litani
 * @author Ted Leung
 * @author Jeffrey Rodriguez
 * @author Mark Swinkles - List Validation refactoring
 * @version  $Id$
 */

public class FloatDatatypeValidator extends AbstractNumericValidator {

    public FloatDatatypeValidator ()  {
        this( null, null, false, null ); // Native, No Facets defined, Restriction
    }

    public FloatDatatypeValidator ( DatatypeValidator base, Hashtable facets,
                                    boolean derivedByList, XMLErrorReporter reporter) {
        // Set base type
        super (base, facets, derivedByList, reporter);
    }
    
   public int compare( String value1, String value2) {
        try {
            float f1 = fValueOf(value1).floatValue();
            float f2 = fValueOf(value2).floatValue();
            return compareFloats(f1, f2);
        }
        catch ( NumberFormatException e ) {
            //REVISIT: should we throw exception??
            return -1;
        }
    }

    protected void assignAdditionalFacets(String key,  Hashtable facets ) throws InvalidDatatypeFacetException{        
        String msg = "float datatype, facet "+key+" with value "+(String)facets.get(key);
        throw new InvalidDatatypeFacetException(msg);
    }

    protected int compareValues (Object value1, Object value2) {

        float f1 = ((Float)value1).floatValue();
        float f2 = ((Float)value2).floatValue();
        return compareFloats(f1, f2);
    }
    
    protected void setMaxInclusive (String value) {
        fMaxInclusive = fValueOf(value);
    }
    protected void setMinInclusive (String value) {
        fMinInclusive = fValueOf(value);

    }
    protected void setMaxExclusive (String value) {
        fMaxExclusive = fValueOf(value);

    }
    protected void setMinExclusive (String value) {
        fMinExclusive = fValueOf(value);

    }
    protected void setEnumeration (Vector enumeration) throws InvalidDatatypeValueException{
        if ( enumeration != null ) {
            fEnumeration = new Float[enumeration.size()];
            Object[] baseEnum=null;
            for ( int i = 0; i < enumeration.size(); i++ ){
                    fEnumeration[i] = fValueOf((String) enumeration.elementAt(i));
                    ((FloatDatatypeValidator)fBaseValidator).validate((String)enumeration.elementAt(i), null);
            }
        }
    }


    protected String getMaxInclusive (boolean isBase) {
        return(isBase)?(((FloatDatatypeValidator)fBaseValidator).fMaxInclusive.toString())
        :((Float)fMaxInclusive).toString();
    }
    protected String getMinInclusive (boolean isBase) {
        return(isBase)?(((FloatDatatypeValidator)fBaseValidator).fMinInclusive.toString())
        :((Float)fMinInclusive).toString();
    }
    protected String getMaxExclusive (boolean isBase) {
        return(isBase)?(((FloatDatatypeValidator)fBaseValidator).fMaxExclusive.toString())
        :((Float)fMaxExclusive).toString();
    }
    protected String getMinExclusive (boolean isBase) {
        return(isBase)?(((FloatDatatypeValidator)fBaseValidator).fMinExclusive.toString())
        :((Float)fMinExclusive).toString();
    }

    /**
    * validate if the content is valid against base datatype and facets (if any)
    * this function might be called directly from UnionDatatype or ListDatatype
    *
    * @param content A string containing the content to be validated
    * @param enumeration A vector with enumeration strings
    * @exception throws InvalidDatatypeException if the content is
    *  is not a W3C float type;
    * @exception throws InvalidDatatypeFacetException if enumeration is not float
    */

    protected void checkContent(String content, Object state, Vector enumeration, boolean asBase)
    throws InvalidDatatypeValueException {
        // validate against parent type if any
        if ( this.fBaseValidator != null && !(fBaseValidator instanceof AnySimpleType)) {
            // validate content as a base type
            ((FloatDatatypeValidator)fBaseValidator).checkContent(content, state, enumeration, true);
        }

        // we check pattern first
        if ( (fFacetsDefined & DatatypeValidator.FACET_PATTERN ) != 0 ) {
            if ( fRegex == null || fRegex.matches( content) == false )
                throw new InvalidDatatypeValueException("Value'"+content+
                                                        "does not match regular expression facet" + fPattern );
        }

        // if this is a base validator, we only need to check pattern facet
        // all other facet were inherited by the derived type
        if ( asBase )
            return;

        Float f = null;
        try {
            f = fValueOf(content);
        }
        catch ( NumberFormatException nfe ) {
            String msg = getErrorString(
                DatatypeMessageProvider.fgMessageKeys[DatatypeMessageProvider.NOT_FLOAT],
                new Object [] {content });
            throw new InvalidDatatypeValueException(msg);
        }

        //enumeration is passed from List or Union datatypes
        if ( enumeration != null ) {
            int size =  enumeration.size();
            Float[]     enumFloats = new Float[size];
            int i=0;
            try {
                for ( ; i < size; i++ )
                    enumFloats[i] = fValueOf((String) enumeration.elementAt(i));

            }
            catch ( NumberFormatException nfe ) {
                String msg = getErrorString(
                    DatatypeMessageProvider.fgMessageKeys[DatatypeMessageProvider.INVALID_ENUM_VALUE],
                    new Object [] { enumeration.elementAt(i) });
                throw new InvalidDatatypeValueException(msg);
            }
            enumCheck(f.floatValue(), enumFloats);
        }

        boundsCheck(f);

        if ( ((fFacetsDefined & DatatypeValidator.FACET_ENUMERATION ) != 0 &&
              (fEnumeration != null) ) ) {
               enumCheck(f.floatValue(), (Float[])fEnumeration);
        }
    }

    protected int getInvalidFacetMsg (){
        return DatatypeMessageProvider.ILLEGAL_FLOAT_FACET;
    }  

    private void enumCheck(float v, Float[] enumFloats) throws InvalidDatatypeValueException {
        for ( int i = 0; i < enumFloats.length; i++ ) {
            if ( v == ((Float)enumFloats[i]).floatValue() ) return;
        }
        String msg = getErrorString(
            DatatypeMessageProvider.fgMessageKeys[DatatypeMessageProvider.NOT_ENUM_VALUE],
            new Object [] { new Float(v) });
        throw new InvalidDatatypeValueException(msg);
    }


    private static Float fValueOf(String s) throws NumberFormatException {
        Float f=null;
        try {
            f = Float.valueOf(s);
        }
        catch ( NumberFormatException nfe ) {
            if ( s.equals("INF") ) {
                f = new Float(Float.POSITIVE_INFINITY);
            }
            else if ( s.equals("-INF") ) {
                f = new Float (Float.NEGATIVE_INFINITY);
            }
            else if ( s.equals("NaN" ) ) {
                f = new Float (Float.NaN);
            }
            else {
                throw nfe;
            }
        }
        return f;
    }

    private int compareFloats( float f1, float f2){
        int f1V = Float.floatToIntBits(f1);
        int f2V = Float.floatToIntBits(f2);
        if ( f1 > f2 ) {
            return 1;
        }
        if ( f1 < f2 ) {
            return -1;
        }
        if ( f1V==f2V ) {
            return 0;
        }
        //REVISIT: NaN values comparison..
        return(f1V < f2V) ? -1 : 1;
    }
}
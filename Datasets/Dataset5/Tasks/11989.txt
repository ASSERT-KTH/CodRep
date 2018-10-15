import org.apache.xerces.impl.v2.util.regex.RegularExpression;

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

import java.util.Hashtable;
import java.util.Vector;
import java.util.Enumeration;
import java.util.StringTokenizer;
import java.util.NoSuchElementException;
import org.apache.xerces.impl.v2.SchemaSymbols;
import org.apache.xerces.impl.v1.util.regex.RegularExpression;



/**
 * @author Jeffrey Rodriguez
 * @author Elena Litani
 * UnionValidator validates that XML content is a W3C string type.
 * Implements the September 22 XML Schema datatype Union Datatype type
 */
public class UnionDatatypeValidator extends AbstractDatatypeValidator {
    
    private Vector  fBaseValidators   = null; // union collection of validators
    private int fValidatorsSize = 0;
    private Vector     fEnumeration      = null;
    private StringBuffer errorMsg = null;   


    public  UnionDatatypeValidator () throws InvalidDatatypeFacetException{
        this( null, null, false ); // Native, No Facets defined, Restriction

    }


    public UnionDatatypeValidator ( DatatypeValidator base, Hashtable facets, boolean derivedBy ) throws InvalidDatatypeFacetException {
        fBaseValidator = base;  
        //facets allowed are: pattern & enumeration
        if ( facets != null ) {
            for ( Enumeration e = facets.keys(); e.hasMoreElements(); ) {
                String key = (String) e.nextElement();
                if ( key.equals(SchemaSymbols.ELT_ENUMERATION) ) {
                    fFacetsDefined |= DatatypeValidator.FACET_ENUMERATION;
                    fEnumeration    = (Vector)facets.get(key);
                }
                else if ( key.equals(SchemaSymbols.ELT_PATTERN) ) {
                    fFacetsDefined |= DatatypeValidator.FACET_PATTERN;
                    fPattern = (String)facets.get(key);
                    fRegex   = new RegularExpression(fPattern, "X");


                }
                else {
                    String msg = getErrorString(
                        DatatypeMessageProvider.fgMessageKeys[DatatypeMessageProvider.ILLEGAL_UNION_FACET],
                        new Object[] { key });
                    throw new InvalidDatatypeFacetException(msg);                }
            } //end for

            // check 4.3.5.c0 must: enumeration values from the value space of base
            if ( base != null &&
                (fFacetsDefined & DatatypeValidator.FACET_ENUMERATION) != 0 &&
                (fEnumeration != null) ) {
                int i = 0;
                try {
                    for (; i < fEnumeration.size(); i++) {
                        base.validate ((String)fEnumeration.elementAt(i), null);
                    }
                } catch ( Exception idve ){
                    throw new InvalidDatatypeFacetException( "Value of enumeration = '" + fEnumeration.elementAt(i) +
                                                             "' must be from the value space of base.");
                }
            }
        }// End of Facets Setting

    }

    public UnionDatatypeValidator ( Vector base)  {

        if ( base !=null ) {
            fValidatorsSize = base.size();
            fBaseValidators = new Vector(fValidatorsSize);
            fBaseValidators = base;

        }

    }



    /**
     * validate that a string is a W3C string type
     * 
     * @param content A string containing the content to be validated
     * @param list
     * @exception throws InvalidDatatypeException if the content is
     *                   not a W3C string type
     * @exception InvalidDatatypeValueException
     */
    public Object validate(String content, Object state)  throws InvalidDatatypeValueException
    {
        if ( content == null && state != null ) {
            this.fBaseValidator.validate( content, state );//Passthrough setup information
            //for state validators
        }
        else {
            checkContentEnum( content, state, false , null );
        }
        return(null);
    }


    /**
     * 
     * @return A Hashtable containing the facets
     *         for this datatype.
     */
    public Hashtable getFacets(){
        return(null);
    }

    public int compare( String value1, String value2 ){
        if (fBaseValidator != null) {
            return this.fBaseValidator.compare(value1, value2);
        }
        //union datatype
        int index=-1;
        DatatypeValidator currentDV;
        while ( ++index < fValidatorsSize ) {  
            currentDV =  (DatatypeValidator)this.fBaseValidators.elementAt(index);
            if (currentDV.compare(value1, value2) == 0) {
                return  0;
            }
        }
        //REVISIT: what does it mean for UNION1 to be <less than> or <greater than> UNION2 ?
        return -1;
    }

    /**
   * Returns a copy of this object.
   */
    public Object clone() throws CloneNotSupportedException  {
        UnionDatatypeValidator newObj = null;
        try {
            newObj = new UnionDatatypeValidator();
            newObj.fLocale           =  this.fLocale;
            newObj.fBaseValidator    =  this.fBaseValidator;
            newObj.fBaseValidators   =  (Vector)this.fBaseValidators.clone();  
            newObj.fPattern          =  this.fPattern;
            newObj.fEnumeration      =  this.fEnumeration;
            newObj.fFacetsDefined    =  this.fFacetsDefined;
        }
        catch ( InvalidDatatypeFacetException ex ) {
            ex.printStackTrace();
        }
        return(newObj);

    }

    // returns the fBaseValidators Vector; added so that
    // 2.2.4 of SchemaStructures spec section 3.14.6 can be implemented.
    public Vector getBaseValidators() {
        return fBaseValidators;
    }

    /**
    * check if enum is subset of fEnumeration
    * enum 1: <enumeration value="1 2"/>
    * enum 2: <enumeration value="1.0 2"/>
    *
    * @param enumeration facet
    *
    * @returns true if enumeration is subset of fEnumeration, false otherwise
    */
    private boolean verifyEnum (Vector enum){
        /* REVISIT: won't work for list datatypes in some cases: */
        if ((fFacetsDefined & DatatypeValidator.FACET_ENUMERATION ) != 0) {
            for (Enumeration e = enum.elements() ; e.hasMoreElements() ;) {
                if (fEnumeration.contains(e.nextElement()) == false) {
                    return false;                             
                }
            }
        }
        return true;
    }

    /**
     * validate if the content is valid against base datatype and facets (if any) 
     * 
     * @param content A string containing the content to be validated
     * @param pattern: true if pattern facet was applied, false otherwise
     * @param enumeration enumeration facet
     * @exception throws InvalidDatatypeException if the content is not valid
     */
    private void checkContentEnum( String content,  Object state, boolean pattern, Vector enumeration ) throws InvalidDatatypeValueException
    {
        // for UnionDatatype we have to wait till the union baseValidators are known, thus
        // if the content is valid "against" ListDatatype, but pattern was applied - report an error. To do so we pass @param pattern;
        // pass @param enumeration so that when base Datatype is known, we would validate enumeration/content
        // against value space as well
        int index = -1; //number of validators
        boolean valid=false; 
        DatatypeValidator currentDV = null;
        if (fBaseValidator !=null) {  //restriction  of union datatype
            if ( (fFacetsDefined & DatatypeValidator.FACET_PATTERN ) != 0 ) {
                if ( fRegex == null || fRegex.matches( content) == false )
                    throw new InvalidDatatypeValueException("Value '"+content+
                    "' does not match regular expression facet '" + fPattern + "'." );
                pattern = true;
            }

            if (enumeration!=null) {
                if (!verifyEnum(enumeration)) {
                    throw new InvalidDatatypeValueException("Enumeration '" +enumeration+"' for value '" +content+
                    "' is based on enumeration '"+fEnumeration+"'");
                }
            }
            else {
                enumeration = (fEnumeration!=null) ? fEnumeration : null;
            }
            ((UnionDatatypeValidator)this.fBaseValidator).checkContentEnum( content, state, pattern, enumeration  );
            return;
        }
        // native union type
        while ( ++index < fValidatorsSize) {  
            // check content against each base validator in Union
            // report an error only in case content is not valid against all base datatypes.
            currentDV =  (DatatypeValidator)this.fBaseValidators.elementAt(index);
            if ( valid ) break;
            try {
                if ( currentDV instanceof ListDatatypeValidator ) {
                    if ( pattern ) {
                        throw new InvalidDatatypeValueException("Facet \"Pattern\" can not be applied to a list datatype" );  
                    }
                    ((ListDatatypeValidator)currentDV).checkContentEnum( content, state, enumeration );
                }
                else if ( currentDV instanceof UnionDatatypeValidator ) {
                    ((UnionDatatypeValidator)currentDV).checkContentEnum( content, state, pattern, enumeration );
                }
                else {
                    if (enumeration!=null) {
                        // check enumeration against value space of double, decimal and float
                        if (currentDV instanceof AbstractNumericValidator) {
                            ((AbstractNumericValidator)currentDV).checkContentEnum(content, state, enumeration);
                        }
                        else {
                            if (enumeration.contains( content ) == false) {
                                throw new InvalidDatatypeValueException("Value '"+content+ "' must be one of "+ enumeration);
                            }
                            ((DatatypeValidator)currentDV).validate( content, state );
                        }   
                    }
                    else {
                        ((DatatypeValidator)currentDV).validate( content, state );
                    }
                }
                valid=true;

            }
            catch ( InvalidDatatypeValueException e ) {
            }
        }
        if ( !valid ) {
            throw new InvalidDatatypeValueException( "Content '"+content+"' does not match any union types" );  
        }
    }

}


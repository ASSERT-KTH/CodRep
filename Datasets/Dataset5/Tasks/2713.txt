currentDV =  (DatatypeValidator)this.fBaseValidators.elementAt(index);

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

package org.apache.xerces.validators.datatype;

import java.util.Hashtable;
import java.util.Vector;
import java.util.Enumeration;
import java.util.Locale;
import java.text.Collator;
import java.util.Enumeration;
import java.util.StringTokenizer;
import java.util.NoSuchElementException;
import org.apache.xerces.validators.schema.SchemaSymbols;
import org.apache.xerces.utils.regex.RegularExpression;



/**
 * @author Jeffrey Rodriguez
 * @author Elena Litani
 * UnionValidator validates that XML content is a W3C string type.
 * Implements the September 22 XML Schema datatype Union Datatype type
 */
public class UnionDatatypeValidator extends AbstractDatatypeValidator {
    private Locale     fLocale          = null;
    private Vector  fBaseValidators   = null;             // union collection of validators
    private DatatypeValidator  fBaseValidator   = null;   // Native datatypes have null
    private int fValidatorsSize = 0;
    private String     fPattern          = null;
    private Vector     fEnumeration      = null;
    private int        fFacetsDefined    = 0;
    private boolean    fDerivedByUnion    = false; //default

    private StringBuffer errorMsg = null;   
    private RegularExpression fRegex         = null;


    public  UnionDatatypeValidator () throws InvalidDatatypeFacetException{
        this( null, null, false ); // Native, No Facets defined, Restriction

    }

    public UnionDatatypeValidator ( DatatypeValidator base, Hashtable facets, 
                                    boolean derivedBy ) throws InvalidDatatypeFacetException {
        setBasetype( base ); // Set base type 
        fDerivedByUnion = derivedBy;  // always false - derived datatype

        //facets allowed are: pattern & enumeration
        if ( facets != null ) {
            for ( Enumeration e = facets.keys(); e.hasMoreElements(); ) {
                String key = (String) e.nextElement();
                if ( key.equals(SchemaSymbols.ELT_ENUMERATION) ) {
                    fFacetsDefined += DatatypeValidator.FACET_ENUMERATION;
                    fEnumeration    = (Vector)facets.get(key);
                } else if ( key.equals(SchemaSymbols.ELT_PATTERN) ) {
                    fFacetsDefined += DatatypeValidator.FACET_PATTERN;
                    fPattern = (String)facets.get(key);
                    fRegex   = new RegularExpression(fPattern, "X");


                } else {
                    throw new InvalidDatatypeFacetException("invalid facet tag : " + key);
                }
            } //end for

        }// End of Facets Setting

    }

    public UnionDatatypeValidator ( Vector base)  {

        if ( base !=null ) {
            fValidatorsSize = base.size();
            fBaseValidators = new Vector(fValidatorsSize);
            fDerivedByUnion = true;  //native union decl
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
        } else {
            checkContent( content, state);
        }
        return(null);
    }


    /**
     * set the locate to be used for error messages
     */
    public void setLocale(Locale locale) {
        fLocale = locale;
    }


    /**
     * 
     * @return                          A Hashtable containing the facets
     *         for this datatype.
     */
    public Hashtable getFacets(){
        return(null);
    }

    public int compare( String content, String facetValue ){
        // if derive by list then this should iterate through
        // the tokens in each string and compare using the base type
        // compare function.
        // if not derived by list just pass the compare down to the
        // base type.
        return(0);
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
            newObj.fDerivedByUnion   =  this.fDerivedByUnion;
        } catch ( InvalidDatatypeFacetException ex ) {
            ex.printStackTrace();
        }
        return(newObj);

    }

    // Private methods


    private void checkContent( String content,  Object state ) throws InvalidDatatypeValueException
    {
        //Facet pattern can be checked here
        //Facet enumeration requires to know if valiadation occurs against ListDatatype
        if ( (fFacetsDefined & DatatypeValidator.FACET_PATTERN ) != 0 ) {
            if ( fRegex == null || fRegex.matches( content) == false )
                throw new InvalidDatatypeValueException("Value '"+content+
                                                        "' does not match regular expression facet '" + fPattern + "'." );
        }

        //validate against parent type
        if ( this.fBaseValidator != null ) {
            ((UnionDatatypeValidator)this.fBaseValidator).checkContent( content, state , fPattern, fEnumeration );
        }
    }


    private void checkContent( String content,  Object state, String pattern, Vector enum ) throws InvalidDatatypeValueException
    {
        int index = -1; //number of validators
        boolean valid=false; 
        DatatypeValidator currentDV = null;
        while ( (fValidatorsSize-1) > index++ ) {  //check content against each validator in Union     
            currentDV =  (DatatypeValidator)this.fBaseValidators.get(index);
            if ( valid ) {//content is valid
                break;
            }
            try {
                if ( currentDV instanceof ListDatatypeValidator ) {
                    if ( pattern != null ) {
                        throw new InvalidDatatypeValueException("Facet \"Pattern\" can not be applied to a list datatype" );  
                    } else if ( enum != null ) {  //Check each token against enumeration  
                        StringTokenizer parsedList = new StringTokenizer( content );
                        String token = null;
                        while ( parsedList.hasMoreTokens() ) {       //Check each token in list against base type
                            token = parsedList.nextToken();
                            if ( enum.contains( token ) == false ) {
                                throw new InvalidDatatypeValueException("Value '"+
                                                                        content+"' must be one of "+enum);
                            }
                        }
                    }
                    ((ListDatatypeValidator)currentDV).validate( content, state );
                }

                else if ( currentDV instanceof UnionDatatypeValidator ) {
                    ((UnionDatatypeValidator)currentDV).checkContent( content, state, pattern, enum );
                } else {
                    if ( enum != null ) {
                        if ( enum.contains( content ) == false )
                            throw new InvalidDatatypeValueException("Value '"+
                                                                    content+"' must be one of " 
                                                                    + enum);

                    }
                    ((DatatypeValidator)currentDV).validate( content, state );
                }
                valid=true;

            } catch ( InvalidDatatypeValueException e ) {
                //REVIST: is it the right way to record error messages?
                if ( errorMsg == null ) {
                    errorMsg = new StringBuffer();
                }
                errorMsg.append('\n');
                errorMsg.append(e.getMessage());
                valid=false;
            }
        }
        if ( !valid ) {
            throw new InvalidDatatypeValueException( this.errorMsg.toString());  
        }
    }




    private void setBasetype( DatatypeValidator base) {
        fBaseValidator = base;
    }

}


if ( fMinLength > fMaxLength ) {

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
 * StringValidator validates that XML content is a W3C string type.
 * @author Ted Leung
 * @author Kito D. Mann, Virtua Communications Corp.
 * @author Jeffrey Rodriguez
 * @version $Id$
 */
public class StringDatatypeValidator extends AbstractDatatypeValidator{
    private Locale     fLocale          = null;
    DatatypeValidator  fBaseValidator   = null; // Native datatypes have null

    private int        fLength           = 0;
    private int        fMaxLength        = Integer.MAX_VALUE;
    private int        fMinLength        = 0;
    private String     fPattern          = null;
    private Vector     fEnumeration      = null;
    private String     fMaxInclusive     = null;
    private String     fMaxExclusive     = null;
    private String     fMinInclusive     = null;
    private String     fMinExclusive     = null;
    private int        fFacetsDefined    = 0;
    private boolean    fDerivedByList    = false;//default

    private boolean isMaxExclusiveDefined = false;
    private boolean isMaxInclusiveDefined = false;
    private boolean isMinExclusiveDefined = false;
    private boolean isMinInclusiveDefined = false;




    public  StringDatatypeValidator () throws InvalidDatatypeFacetException{
        this( null, null, false ); // Native, No Facets defined, Restriction

    }

    public StringDatatypeValidator ( DatatypeValidator base, Hashtable facets, 
                                     boolean derivedByList ) throws InvalidDatatypeFacetException {

        setBasetype( base ); // Set base type 

        // Set Facets if any defined

        //fFacetsDefined = 0;
        if ( facets != null  ){
            if ( derivedByList == false) {
                for (Enumeration e = facets.keys(); e.hasMoreElements();) {
                    String key = (String) e.nextElement();

                    if ( key.equals(SchemaSymbols.ELT_LENGTH) ) {
                        fFacetsDefined += DatatypeValidator.FACET_LENGTH;
                        String lengthValue = (String)facets.get(key);
                        try {
                            fLength     = Integer.parseInt( lengthValue );
                        } catch (NumberFormatException nfe) {
                            throw new InvalidDatatypeFacetException("Length value '"+lengthValue+"' is invalid.");
                        }
                        if ( fLength < 0 )
                            throw new InvalidDatatypeFacetException("Length value '"+lengthValue+"'  must be a nonNegativeInteger.");

                    } else if (key.equals(SchemaSymbols.ELT_MINLENGTH) ) {
                        fFacetsDefined += DatatypeValidator.FACET_MINLENGTH;
                        String minLengthValue = (String)facets.get(key);
                        try {
                            fMinLength     = Integer.parseInt( minLengthValue );
                        } catch (NumberFormatException nfe) {
                            throw new InvalidDatatypeFacetException("minLength value '"+minLengthValue+"' is invalid.");
                        }
                    } else if (key.equals(SchemaSymbols.ELT_MAXLENGTH) ) {
                        fFacetsDefined += DatatypeValidator.FACET_MAXLENGTH;
                        String maxLengthValue = (String)facets.get(key);
                        try {
                            fMaxLength     = Integer.parseInt( maxLengthValue );
                        } catch (NumberFormatException nfe) {
                            throw new InvalidDatatypeFacetException("maxLength value '"+maxLengthValue+"' is invalid.");
                        }
                    } else if (key.equals(SchemaSymbols.ELT_PATTERN)) {
                        fFacetsDefined += DatatypeValidator.FACET_PATTERN;
                        fPattern = (String)facets.get(key);
                    } else if (key.equals(SchemaSymbols.ELT_ENUMERATION)) {
                        fFacetsDefined += DatatypeValidator.FACET_ENUMERATION;
                        fEnumeration = (Vector)facets.get(key);
                    } else if (key.equals(SchemaSymbols.ELT_MAXINCLUSIVE)) {
                        fFacetsDefined += DatatypeValidator.FACET_MAXINCLUSIVE;
                        fMaxInclusive = (String)facets.get(key);
                    } else if (key.equals(SchemaSymbols.ELT_MAXEXCLUSIVE)) {
                        fFacetsDefined += DatatypeValidator.FACET_MAXEXCLUSIVE;
                        fMaxExclusive = (String)facets.get(key);
                    } else if (key.equals(SchemaSymbols.ELT_MININCLUSIVE)) {
                        fFacetsDefined += DatatypeValidator.FACET_MININCLUSIVE;
                        fMinInclusive = (String)facets.get(key);
                    } else if (key.equals(SchemaSymbols.ELT_MINEXCLUSIVE)) {
                        fFacetsDefined += DatatypeValidator.FACET_MININCLUSIVE;
                        fMinExclusive = (String)facets.get(key);
                    } else {
                        throw new InvalidDatatypeFacetException("invalid facet tag : " + key);
                    }
                }

                if (((fFacetsDefined & DatatypeValidator.FACET_LENGTH ) != 0 ) ) {
                    if (((fFacetsDefined & DatatypeValidator.FACET_MAXLENGTH ) != 0 ) ) {
                        throw new InvalidDatatypeFacetException(
                                                               "It is an error for both length and maxLength to be members of facets." );  
                    } else if (((fFacetsDefined & DatatypeValidator.FACET_MINLENGTH ) != 0 ) ) {
                        throw new InvalidDatatypeFacetException(
                                "It is an error for both length and minLength to be members of facets." );
                    }
                }

                if ( ( (fFacetsDefined & ( DatatypeValidator.FACET_MINLENGTH |
                                           DatatypeValidator.FACET_MAXLENGTH) ) != 0 ) ) {
                    if ( fMinLength > fMaxLength ) {
                        throw new InvalidDatatypeFacetException( "Value of minLength = '" + fMinLength +
                            "'must be less than the value of maxLength = '" + fMaxLength + "'.");
                    }
                }

                isMaxExclusiveDefined = ((fFacetsDefined & 
                                          DatatypeValidator.FACET_MAXEXCLUSIVE ) != 0 )?true:false;
                isMaxInclusiveDefined = ((fFacetsDefined & 
                                          DatatypeValidator.FACET_MAXINCLUSIVE ) != 0 )?true:false;
                isMinExclusiveDefined = ((fFacetsDefined &
                                          DatatypeValidator.FACET_MINEXCLUSIVE ) != 0 )?true:false;
                isMinInclusiveDefined = ((fFacetsDefined &
                                          DatatypeValidator.FACET_MININCLUSIVE ) != 0 )?true:false;

                if ( isMaxExclusiveDefined && isMaxInclusiveDefined ) {
                    throw new InvalidDatatypeFacetException(
                                                           "It is an error for both maxInclusive and maxExclusive to be specified for the same datatype." ); 
                }
                if ( isMinExclusiveDefined && isMinInclusiveDefined ) {
                    throw new InvalidDatatypeFacetException(
                                                           "It is an error for both minInclusive and minExclusive to be specified for the same datatype." ); 
                }
            } else { //derived by list
                fDerivedByList = true;
                for (Enumeration e = facets.keys(); e.hasMoreElements();) {
                    String key = (String) e.nextElement();
                    if ( key.equals(SchemaSymbols.ELT_LENGTH) ) {
                        fFacetsDefined += DatatypeValidator.FACET_LENGTH;
                        String lengthValue = (String)facets.get(key);
                        try {
                            fLength     = Integer.parseInt( lengthValue );
                        } catch (NumberFormatException nfe) {
                            throw new InvalidDatatypeFacetException("Length value '"+lengthValue+"' is invalid.");
                        }
                        if ( fLength < 0 )
                            throw new InvalidDatatypeFacetException("Length value '"+lengthValue+"'  must be a nonNegativeInteger.");

                    } else if (key.equals(SchemaSymbols.ELT_MINLENGTH) ) {
                        fFacetsDefined += DatatypeValidator.FACET_MINLENGTH;
                        String minLengthValue = (String)facets.get(key);
                        try {
                            fMinLength     = Integer.parseInt( minLengthValue );
                        } catch (NumberFormatException nfe) {
                            throw new InvalidDatatypeFacetException("maxLength value '"+minLengthValue+"' is invalid.");
                        }
                    } else if (key.equals(SchemaSymbols.ELT_MAXLENGTH) ) {
                        fFacetsDefined += DatatypeValidator.FACET_MAXLENGTH;
                        String maxLengthValue = (String)facets.get(key);
                        try {
                            fMaxLength     = Integer.parseInt( maxLengthValue );
                        } catch (NumberFormatException nfe) {
                            throw new InvalidDatatypeFacetException("maxLength value '"+maxLengthValue+"' is invalid.");
                        }
                    } else if (key.equals(SchemaSymbols.ELT_ENUMERATION)) {
                        fFacetsDefined += DatatypeValidator.FACET_ENUMERATION;
                        fEnumeration    = (Vector)facets.get(key);
                    } else {
                        throw new InvalidDatatypeFacetException("invalid facet tag : " + key);
                    }
                }
                if (((fFacetsDefined & DatatypeValidator.FACET_LENGTH ) != 0 ) ) {
                    if (((fFacetsDefined & DatatypeValidator.FACET_MAXLENGTH ) != 0 ) ) {
                        throw new InvalidDatatypeFacetException(
                                                               "It is an error for both length and maxLength to be members of facets." );  
                    } else if (((fFacetsDefined & DatatypeValidator.FACET_MINLENGTH ) != 0 ) ) {
                        throw new InvalidDatatypeFacetException(
                                                               "It is an error for both length and minLength to be members of facets." );
                    }
                }

                if ( ( (fFacetsDefined & ( DatatypeValidator.FACET_MINLENGTH |
                                           DatatypeValidator.FACET_MAXLENGTH) ) != 0 ) ) {
                    if ( fMinLength < fMaxLength ) {
                        throw new InvalidDatatypeFacetException( "Value of minLength = " + fMinLength +
                                                                 "must be greater that the value of maxLength" + fMaxLength );
                    }
                }
            }
        }// End of Facets Setting
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
        if ( fFacetsDefined == 0 )// No Facets to validate
            return null;

        if ( fDerivedByList == false  ) {
            checkContent( content );
        } else { //derived by list 
            StringTokenizer parsedList = new StringTokenizer( content );
            try {
                while ( parsedList.hasMoreTokens() ) {
                    checkContentList( parsedList.nextToken() );
                }
            } catch ( NoSuchElementException e ) {
                e.printStackTrace();
            }
        }
        return null;
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
        return null;
    }

    private void checkContent( String content )throws InvalidDatatypeValueException
    {
        if ( (fFacetsDefined & DatatypeValidator.FACET_MAXLENGTH) != 0 ) {
            if ( content.length() > fMaxLength ) {
                throw new InvalidDatatypeValueException("Value '"+content+
                                                        "' with length '"+content.length()+
                                          "' exceeds maximum length facet of '"+fMaxLength+"'.");
            }
        }
        if ( (fFacetsDefined & DatatypeValidator.FACET_MINLENGTH) != 0 ) {
            if ( content.length() < fMinLength ) {
                throw new InvalidDatatypeValueException("Value '"+content+
                                                    "' with length '"+content.length()+
                                    "' is less than minimum length facet of '"+fMinLength+"'." );
            }
        }

        if ( (fFacetsDefined & DatatypeValidator.FACET_LENGTH) != 0 ) {
                    if ( content.length() != fLength ) {
                        throw new InvalidDatatypeValueException("Value '"+content+
                                                         "' with length '"+content.length()+
                                               "' is not equal to length facet '"+fLength+"'.");
                    }
                }



        if ( (fFacetsDefined & DatatypeValidator.FACET_ENUMERATION) != 0 ) {
            if ( fEnumeration.contains( content ) == false )
                throw new InvalidDatatypeValueException("Value '"+content+"' must be one of "+fEnumeration);
        }

        if ( isMaxExclusiveDefined == true ) {
            int comparisonResult;
            comparisonResult  = compare( content, fMaxExclusive );
            if ( comparisonResult > 0 ) {
                throw new InvalidDatatypeValueException( "Value '"+content+ "'  must be" +
                                                         "lexicographically less than" + fMaxExclusive );

            }

        }
        if ( isMaxInclusiveDefined == true ) {
            int comparisonResult;
            comparisonResult  = compare( content, fMaxInclusive );
            if ( comparisonResult >= 0 )
                throw new InvalidDatatypeValueException( "Value '"+content+ "' must be" +
                                                         "lexicographically less or equal than" + fMaxInclusive );
        }

        if ( isMinExclusiveDefined == true ) {
            int comparisonResult;
            comparisonResult  = compare( content, fMinExclusive );
            if ( comparisonResult < 0 )
                throw new InvalidDatatypeValueException( "Value '"+content+ "' must be" +
                                                         "lexicographically greater than" + fMinExclusive );
        }
        if ( isMinInclusiveDefined == true ) {
            int comparisonResult;
            comparisonResult = compare( content, fMinInclusive );
            if ( comparisonResult <= 0 )
                throw new InvalidDatatypeValueException( "Value '"+content+ "' must be" +
                                                         "lexicographically greater or equal than" + fMinInclusive );
        }


        if ( (fFacetsDefined & DatatypeValidator.FACET_PATTERN ) != 0 ) {
            RegularExpression regex = new RegularExpression(fPattern, "X" );
            if ( regex.matches( content) == false )
                throw new InvalidDatatypeValueException("Value'"+content+
                                                        "does not match regular expression facet" + fPattern );
        }

    }
    public int compare( String content, String facetValue ){
        Locale    loc       = Locale.getDefault();
        Collator  collator  = Collator.getInstance( loc );
        return collator.compare( content, facetValue );
    }

    /**
   * Returns a copy of this object.
   */
    public Object clone() throws CloneNotSupportedException  {
        StringDatatypeValidator newObj = null;
        try {
            newObj = new StringDatatypeValidator();

            newObj.fLocale           =  this.fLocale;
            newObj.fBaseValidator    =  this.fBaseValidator;
            newObj.fLength           =  this.fLength;
            newObj.fMaxLength        =  this.fMaxLength;
            newObj.fMinLength        =  this.fMinLength;
            newObj.fPattern          =  this.fPattern;
            newObj.fEnumeration      =  this.fEnumeration;
            newObj.fMaxInclusive     =  this.fMaxInclusive;
            newObj.fMaxExclusive     =  this.fMaxExclusive;
            newObj.fMinInclusive     =  this.fMinInclusive;
            newObj.fMinExclusive     =  this.fMinExclusive;
            newObj.fFacetsDefined    =  this.fFacetsDefined;
            newObj.fDerivedByList    =  this.fDerivedByList;
            newObj.isMaxExclusiveDefined = this.isMaxExclusiveDefined;
            newObj.isMaxInclusiveDefined = this.isMaxInclusiveDefined;
            newObj.isMinExclusiveDefined = this.isMinExclusiveDefined;
            newObj.isMinInclusiveDefined = this.isMinInclusiveDefined;
        } catch ( InvalidDatatypeFacetException ex) {
            ex.printStackTrace();
        }
        return newObj;
    }

    // Private methods
    private void checkContentList( String content )throws InvalidDatatypeValueException
    {
        //Revisit
    }

    private void setBasetype( DatatypeValidator base) {
        fBaseValidator = base;
    }

}

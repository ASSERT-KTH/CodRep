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
 * StringValidator validates that XML content is a W3C string type.
 * @author  Elena Litani
 * @author Jeffrey Rodriguez
 * @author Mark Swinkles - List Validation refactoring
 * @version $Id$
 */
public class ListDatatypeValidator extends AbstractDatatypeValidator{
    
    private int        fLength           = 0;
    private int        fMaxLength        = Integer.MAX_VALUE;
    private int        fMinLength        = 0;
    private Vector     fEnumeration      = null;

    public  ListDatatypeValidator () throws InvalidDatatypeFacetException{
        this( null, null, false ); // Native, No Facets defined, Restriction

    }

    public ListDatatypeValidator ( DatatypeValidator base, Hashtable facets, 
    boolean derivedByList ) throws InvalidDatatypeFacetException {

        fBaseValidator = base; // Set base type 

        if ( facets != null  ){
            for (Enumeration e = facets.keys(); e.hasMoreElements();) {
                String key = (String) e.nextElement();
                if ( key.equals(SchemaSymbols.ELT_LENGTH) ) {
                    fFacetsDefined |= DatatypeValidator.FACET_LENGTH;
                    String lengthValue = (String)facets.get(key);
                    try {
                        fLength     = Integer.parseInt( lengthValue );
                    } catch (NumberFormatException nfe) {
                        throw new InvalidDatatypeFacetException("Length value '"+lengthValue+"' is invalid.");
                    }
                    if ( fLength < 0 )
                        throw new InvalidDatatypeFacetException("Length value '"+lengthValue+"'  must be a nonNegativeInteger.");

                } 
                else if (key.equals(SchemaSymbols.ELT_MINLENGTH) ) {
                    fFacetsDefined |= DatatypeValidator.FACET_MINLENGTH;
                    String minLengthValue = (String)facets.get(key);
                    try {
                        fMinLength     = Integer.parseInt( minLengthValue );
                    } catch (NumberFormatException nfe) {
                        throw new InvalidDatatypeFacetException("maxLength value '"+minLengthValue+"' is invalid.");
                    }
                } 
                else if (key.equals(SchemaSymbols.ELT_MAXLENGTH) ) {
                    fFacetsDefined |= DatatypeValidator.FACET_MAXLENGTH;
                    String maxLengthValue = (String)facets.get(key);
                    try {
                        fMaxLength     = Integer.parseInt( maxLengthValue );
                    } catch (NumberFormatException nfe) {
                        throw new InvalidDatatypeFacetException("maxLength value '"+maxLengthValue+"' is invalid.");
                    }
                } 
                else if (key.equals(SchemaSymbols.ELT_ENUMERATION)) {
                    fFacetsDefined |= DatatypeValidator.FACET_ENUMERATION;
                    fEnumeration    = (Vector)facets.get(key);
                }
                else if ( key.equals(SchemaSymbols.ELT_PATTERN) ) {
                    fFacetsDefined |= DatatypeValidator.FACET_PATTERN;
                    fPattern = (String)facets.get(key);
                    if ( fPattern != null )
                        fRegex = new RegularExpression(fPattern, "X");
                }            
               else {
                   String msg = getErrorString(
                       DatatypeMessageProvider.fgMessageKeys[DatatypeMessageProvider.ILLEGAL_LIST_FACET],
                       new Object[] { key });
                   throw new InvalidDatatypeFacetException();
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
                    throw new InvalidDatatypeFacetException( "Value of minLength = " + fMinLength +
                    "must be greater that the value of maxLength" + fMaxLength );
                }
            }

            // check 4.3.5.c0 must: enumeration values from the value space of base
            //REVISIT: we should try either to delay it till validate() or
            //         store enumeration values in _value_space 
            //         otherwise we end up creating and throwing objects  
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
            checkContentEnum( content, state , null); 
        }
        return null;
    }


    /**
     * 
     * @return                          A Hashtable containing the facets
     *         for this datatype.
     */
    public Hashtable getFacets(){
        return null;
    }

    public int compare( String value1, String value2 ){
        if (fBaseValidator instanceof ListDatatypeValidator) { //derived by restriction
          return ((ListDatatypeValidator)this.fBaseValidator).compare( value1, value2 );
        }
        // <list> datatype
        StringTokenizer pList1 = new StringTokenizer( value1 );
        StringTokenizer pList2 = new StringTokenizer( value2 );
        int numberOfTokens = pList1.countTokens();         
        if (numberOfTokens < pList2.countTokens()) {
            return -1; 
        }
        else if (numberOfTokens > pList2.countTokens()) {
            return 1;
        }
        else { //compare each token
            int i=0;
            while(i++<numberOfTokens) {
                if ( this.fBaseValidator != null ) {
                    int returnValue = this.fBaseValidator.compare( pList1.nextToken(), pList2.nextToken());
                    if (returnValue!=0) {
                        return returnValue; //REVISIT: does it make sense to return -1 or +1..?
                    }
                }
                
            }
            return 0;
        }
    }

    /**
   * Returns a copy of this object.
   */
    public Object clone() throws CloneNotSupportedException  {
        ListDatatypeValidator newObj = null;
        try {
            newObj = new ListDatatypeValidator();

            newObj.fLocale           =  this.fLocale;
            newObj.fBaseValidator    =  this.fBaseValidator;
            newObj.fLength           =  this.fLength;
            newObj.fMaxLength        =  this.fMaxLength;
            newObj.fMinLength        =  this.fMinLength;
            newObj.fPattern          =  this.fPattern;
            newObj.fEnumeration      =  this.fEnumeration;
            newObj.fFacetsDefined    =  this.fFacetsDefined;
        } catch ( InvalidDatatypeFacetException ex) {
            ex.printStackTrace();
        }
        return newObj;
    }

    /**
     * validate that a content is valid against base datatype and facets (if any) 
     * 
     * @param content A string containing the content to be validated
     * @param state used with IDREF(s) datatypes
     * @param enumeration enumeration facet
     * @exception throws InvalidDatatypeException if the content is not valid
     * @exception InvalidDatatypeValueException
     */
     protected void checkContentEnum( String content,  Object state, Vector enumeration )
                                throws InvalidDatatypeValueException {
            
            //REVISIT: attemt to make enumeration to be validated against value space.
            //a redesign of Datatypes might help to reduce complexity of this validation
        
         StringTokenizer parsedList = new StringTokenizer( content );
         int numberOfTokens = parsedList.countTokens();         
         if (fBaseValidator instanceof ListDatatypeValidator) { 
            //<simpleType name="fRestriction"><restriction base="fList">...</restriction></simpleType>
            try {
                if ( (fFacetsDefined & DatatypeValidator.FACET_MAXLENGTH) != 0 ) {
                    if ( numberOfTokens > fMaxLength ) {
                        throw new InvalidDatatypeValueException("Value '"+content+
                        "' with length ='"+  numberOfTokens + "' tokens"+
                        "' exceeds maximum length facet of '"+fMaxLength+"' tokens.");
                    }
                }
                if ( (fFacetsDefined & DatatypeValidator.FACET_MINLENGTH) != 0 ) {
                    if ( numberOfTokens < fMinLength ) {
                        throw new InvalidDatatypeValueException("Value '"+content+
                        "' with length ='"+ numberOfTokens+ "' tokens" +
                        "' is less than minimum length facet of '"+fMinLength+"' tokens." );
                    }
                }

                if ( (fFacetsDefined & DatatypeValidator.FACET_LENGTH) != 0 ) {
                    if ( numberOfTokens != fLength ) {
                        throw new InvalidDatatypeValueException("Value '"+content+
                        "' with length ='"+ numberOfTokens+ "' tokens" +
                        "' is not equal to length facet of '"+fLength+"' tokens.");
                    }
                }
                if (enumeration!=null) {
                    if (!verifyEnum(enumeration)) {
                        String msg = getErrorString(
                            DatatypeMessageProvider.fgMessageKeys[DatatypeMessageProvider.NOT_ENUM_VALUE],
                            new Object [] { enumeration });
                        throw new InvalidDatatypeValueException(msg);
                    }
                }else {
                    enumeration = (fEnumeration!=null) ? fEnumeration : null;
                }
                                      
                // enumeration must be passed till we know what "itemType" is
                // to be able to validate against value space
                ((ListDatatypeValidator)this.fBaseValidator).checkContentEnum( content, state, enumeration );
            } catch ( NoSuchElementException e ) {
                e.printStackTrace();
            }
        } 
        else { 
            //the case:
            //<simpleType name="fList"><list itemType="float"/></simpleType>
            
            if (enumeration !=null) {
                StringTokenizer eTokens = null; //temporary list of enumeration tokens 
                StringTokenizer cTokens = null; //list of content tokens
                String token= null;  //content token
                String eToken= null; //enumeration token
                boolean valid = true;

                int eSize = enumeration.size(); 
                Vector enumTemp = new Vector(); //temporary vector to store enumeration token
                enumTemp.setSize(1);
                String currentEnumeration = null; //enum value: <enumeration value="1 2 3"/>
                
                for (int i=0;i<eSize;i++) { //loop through each enumeration
                    currentEnumeration = (String)enumeration.elementAt(i);
                    eTokens = new StringTokenizer (currentEnumeration);
                    valid = true;

                    cTokens = (i==0)?parsedList:new StringTokenizer( content );
                    
                    if (numberOfTokens == eTokens.countTokens()) {
                        try {
                            //try string comparison first
                            if (currentEnumeration.equals(content)) {
                                for (int k=0; k<numberOfTokens;k++) { //validate against base type each token
                                    if ( this.fBaseValidator != null ) {
                                        this.fBaseValidator.validate( cTokens.nextToken(), state );
                                    }
                                }
                            } else  { //content="1.0 2" ; enumeration = "1 2"
                                for (int j=0;j<numberOfTokens;j++) {
                                    token = cTokens.nextToken();
                                    eToken = eTokens.nextToken();
                                    enumTemp.setElementAt(eToken,0);
                                    //REVISIT: date/time enumeration support
                                    if (fBaseValidator instanceof AbstractNumericValidator) {
                                        ((AbstractNumericValidator)fBaseValidator).checkContentEnum(token, state, enumTemp);
                                    } else { 
                                        if (!token.equals(eToken)) { //validate enumeration for all other types
                                            throw new InvalidDatatypeValueException("Value '"+content+ "' must be one of "+enumeration);
                                        }
                                        this.fBaseValidator.validate( token, state );
                                    }
                                }
                            }
                        } catch (InvalidDatatypeValueException e) {
                            valid = false;
                        }
                    } else //numOfTokens in enumeration != numOfTokens in content
                        valid = false;
                    if (valid) break;
                } //end for loop
                if (!valid) {
                    throw new InvalidDatatypeValueException("Value '"+content+ "' does not match list type");
                }
            }//enumeration != null
            else {   //no enumeration
                for (int k=0; k<numberOfTokens;k++) {
                    if ( this.fBaseValidator != null ) {//validate against parent type if any
                        this.fBaseValidator.validate( parsedList.nextToken(), state );
                    }
                }
            }

        } //end native list type

    } //end checkContentEnum



    // Private methods
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


}

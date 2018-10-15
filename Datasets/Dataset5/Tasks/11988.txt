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
import java.util.Locale;
import java.text.Collator;
import org.apache.xerces.impl.v2.SchemaSymbols;
import org.apache.xerces.impl.v1.util.regex.RegularExpression;

/**
 * StringValidator validates that XML content is a W3C string type.
 * @author Ted Leung
 * @author Kito D. Mann, Virtua Communications Corp.
 * @author Jeffrey Rodriguez
 * @author Mark Swinkles - List Validation refactoring
 * @version $Id$
 */
public class StringDatatypeValidator extends AbstractStringValidator {

    private short      fWhiteSpace;

    public  StringDatatypeValidator () throws InvalidDatatypeFacetException{
        this ( null, null, false ); // Native, No Facets defined, Restriction

    }
    public StringDatatypeValidator ( DatatypeValidator base, Hashtable facets,
                                     boolean derivedByList ) throws InvalidDatatypeFacetException {

        super (base, facets, derivedByList); 
       
    }


    protected void assignAdditionalFacets(String key, Hashtable facets)  throws InvalidDatatypeFacetException{
        fWhiteSpace = DatatypeValidator.PRESERVE;
        if ( key.equals(SchemaSymbols.ELT_WHITESPACE) ) {
            fFacetsDefined |= DatatypeValidator.FACET_WHITESPACE;
            String ws = (String)facets.get(key);
            // check 4.3.6.c0 must:
            // whiteSpace = preserve || whiteSpace = replace || whiteSpace = collapse
            if ( ws.equals(SchemaSymbols.ATTVAL_PRESERVE) ) {
                fWhiteSpace = DatatypeValidator.PRESERVE;
            }
            else if ( ws.equals(SchemaSymbols.ATTVAL_REPLACE) ) {
                
                fWhiteSpace = DatatypeValidator.REPLACE;
            }
            else if ( ws.equals(SchemaSymbols.ATTVAL_COLLAPSE) ) {
                fWhiteSpace = DatatypeValidator.COLLAPSE;
            }
            else {
                throw new InvalidDatatypeFacetException("whiteSpace value '" + ws +
                                                        "' must be one of 'preserve', 'replace', 'collapse'.");
            }
        }
        else {
            String msg = getErrorString(
                    DatatypeMessageProvider.fgMessageKeys[DatatypeMessageProvider.ILLEGAL_STRING_FACET],
                    new Object[] { key });
                throw new InvalidDatatypeFacetException(msg);
        }
    }


    protected void inheritAdditionalFacets() {
        // inherit whiteSpace
        if ( (fFacetsDefined & DatatypeValidator.FACET_WHITESPACE) == 0 &&
             (((StringDatatypeValidator)fBaseValidator).fFacetsDefined & DatatypeValidator.FACET_WHITESPACE) != 0 ) {
            fFacetsDefined |= DatatypeValidator.FACET_WHITESPACE;
            fWhiteSpace = ((StringDatatypeValidator)fBaseValidator).fWhiteSpace;
        }
    }

    //
    // string needs to check constraints on whiteSpace
    // check is done against fBaseValidator
    //
    protected void checkBaseFacetConstraints() throws InvalidDatatypeFacetException {
        // check 4.3.6.c1 error:
        // (whiteSpace = preserve || whiteSpace = replace) && base.whiteSpace = collapese or
        // whiteSpace = preserve && base.whiteSpace = replace
        
        if ( (fFacetsDefined & DatatypeValidator.FACET_WHITESPACE) != 0 &&
             (((StringDatatypeValidator)fBaseValidator).fFacetsDefined & DatatypeValidator.FACET_WHITESPACE) != 0 ) {
                        if ( (((StringDatatypeValidator)fBaseValidator).fFlags & DatatypeValidator.FACET_WHITESPACE) != 0 &&
                         fWhiteSpace != ((StringDatatypeValidator)fBaseValidator).fWhiteSpace ) {
                        throw new InvalidDatatypeFacetException( "whiteSpace value = '" + whiteSpaceValue(fWhiteSpace) + 
                                                                 "' must be equal to base.whiteSpace value = '" +
                                                                 whiteSpaceValue(((StringDatatypeValidator)fBaseValidator).fWhiteSpace) + "' with attribute {fixed} = true" );
            }
            if ( (fWhiteSpace == DatatypeValidator.PRESERVE ||
                  fWhiteSpace == DatatypeValidator.REPLACE) &&
                 ((StringDatatypeValidator)fBaseValidator).fWhiteSpace == DatatypeValidator.COLLAPSE ){
                throw new InvalidDatatypeFacetException( "It is an error if whiteSpace = 'preserve' or 'replace' and base.whiteSpace = 'collapse'.");
            }
            if ( fWhiteSpace == DatatypeValidator.PRESERVE &&
                 ((StringDatatypeValidator)fBaseValidator).fWhiteSpace == DatatypeValidator.REPLACE )
                throw new InvalidDatatypeFacetException( "It is an error if whiteSpace = 'preserve' and base.whiteSpace = 'replace'.");
        }
    }


    /**
     * return value of whiteSpace facet
     */
    public short getWSFacet() {
        return fWhiteSpace;
    }


    public int compare( String value1, String value2 ) {
        Locale    loc       = Locale.getDefault();
        Collator  collator  = Collator.getInstance( loc );
        return collator.compare( value1, value2 );
    }

    private String whiteSpaceValue (short ws){
       return (ws != DatatypeValidator.PRESERVE)? 
              (ws == DatatypeValidator.REPLACE)?"replace":"collapse":"preserve";
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
            newObj.fWhiteSpace       =  this.fWhiteSpace;
            newObj.fEnumeration      =  this.fEnumeration;
            newObj.fFacetsDefined    =  this.fFacetsDefined;
        }
        catch ( InvalidDatatypeFacetException ex ) {
            ex.printStackTrace();
        }
        return newObj;
    }

}

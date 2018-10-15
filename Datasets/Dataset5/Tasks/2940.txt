if (state !=null && (fFacetsDefined & DatatypeValidator.FACET_ENUMERATION) != 0 &&

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
import org.apache.xerces.impl.XMLErrorReporter;
import org.apache.xerces.impl.v2.XSMessageFormatter;
import org.apache.xerces.impl.validation.ValidationContext;


/**
 * NOTATIONValidator defines the interface that data type validators must obey.
 * These validators can be supplied by the application writer and may be useful as
 * standalone code as well as plugins to the validator architecture.
 *
 * @author Elena Litani
 * @author Jeffrey Rodriguez-
 * @author Mark Swinkles - List Validation refactoring
 * @version $Id$
 */
public class NOTATIONDatatypeValidator extends AbstractStringValidator {
    

    // for the QName validator
    /*
    private static StringDatatypeValidator fgStrValidator  = null;
    private static AnyURIDatatypeValidator fgURIValidator  = null;
    */

    public NOTATIONDatatypeValidator ()   {
        this ( null, null, false, null ); // Native, No Facets defined, Restriction
    }

    public NOTATIONDatatypeValidator ( DatatypeValidator base, Hashtable facets,
         boolean derivedByList, XMLErrorReporter reporter) {

        super (base, facets, derivedByList, reporter);
        // make a string validator for NCName and anyURI

        // REVISIT: do we really need to validate against value space..?
        /*
        if ( fgStrValidator == null) {
            Hashtable strFacets = new Hashtable();
            strFacets.put(SchemaSymbols.ELT_WHITESPACE, SchemaSymbols.ATT_COLLAPSE);
            strFacets.put(SchemaSymbols.ELT_PATTERN , "[\\i-[:]][\\c-[:]]*"  );
            fgStrValidator = new StringDatatypeValidator (null, strFacets, false);
            fgURIValidator = new AnyURIDatatypeValidator (null, null, false);
        }
        */
        
    }

    protected void assignAdditionalFacets(String key, Hashtable facets)  throws InvalidDatatypeFacetException{
        String msg = getErrorString(
            DatatypeMessageProvider.fgMessageKeys[DatatypeMessageProvider.ILLEGAL_STRING_FACET],
            new Object[] { key });
        throw new InvalidDatatypeFacetException(msg);
    }


    public Object validate(String content, ValidationContext state)  throws InvalidDatatypeValueException {
        checkContent( content, state, false );
        return null;
    }

    private void checkContent( String content, ValidationContext state, boolean asBase )
    throws InvalidDatatypeValueException {
        // validate against parent type if any
        if (fBaseValidator instanceof NOTATIONDatatypeValidator) {
            // validate content as a base type
            ((NOTATIONDatatypeValidator)fBaseValidator).checkContent(content, state, true);
        }

        // we check pattern first
        if ((fFacetsDefined & DatatypeValidator.FACET_PATTERN ) != 0) {
            if (fRegex == null || fRegex.matches( content) == false)
                throw new InvalidDatatypeValueException("Value '"+content+
                                                        "' does not match regular expression facet '" + fPattern + "'." );
        }

        // validate special kinds of token, in place of old pattern matching
        if (fTokenType != SPECIAL_TOKEN_NONE) {
            validateToken(fTokenType, content);
        }

        // if this is a base validator, we only need to check pattern facet
        // all other facet were inherited by the derived type
        if (asBase)
            return;

        // REVISIT: see comments in checkValueSpace
        // checkValueSpace (content);
        int length = getLength(content);
        // REVISIT: XML Schema group does not clearly specify how QNames should be 
        // compared against length, minLength, maxLength we don't do any comparison
        //
        if ((fFacetsDefined & DatatypeValidator.FACET_ENUMERATION) != 0 &&
            (fEnumeration != null)) {
            String prefix = state.getSymbol("");
            String localpart = content;
            int colonptr = content.indexOf(":");
            if (colonptr > 0) {
                prefix = content.substring(0,colonptr);
                localpart = content.substring(colonptr+1);

            }
            String uriStr = state.getURI(state.getSymbol(prefix));
            String fullName =  (uriStr!=null)?(uriStr+","+localpart):localpart;                      
            if (fEnumeration.contains( fullName ) == false)
                throw new InvalidDatatypeValueException("Value '"+content+"' must be one of "+fEnumeration);
        }
    }

    protected void checkValueSpace (String content) throws InvalidDatatypeValueException {
        
        // REVISIT: do we need to check 3.2.19: "anyURI:NCName"?        
        /*
        try {
            int posColon = content.lastIndexOf(':');
            if (posColon >= 0)
                fgURIValidator.validate(content.substring(0,posColon), null);
            fgStrValidator.validate(content.substring(posColon+1), null);
        } catch (InvalidDatatypeValueException idve) {
            throw new InvalidDatatypeValueException("Value '"+content+"' is not a valid NOTATION");
        }
        */
    
    }    

    public int compare( String  content1, String content2){
        return content1.equals(content2)?0:-1;
    }
}
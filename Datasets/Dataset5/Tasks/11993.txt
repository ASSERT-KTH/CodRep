public static void setNCNameValidator (DatatypeValidator dv) {

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 2000 The Apache Software Foundation.  All rights
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
import java.util.Locale;
import java.text.Collator;
import org.apache.xerces.impl.v2.SchemaSymbols;

/**
 * QName Validator validates a QName type.
 * QName represents XML qualified names. The value
 * space of QName is the set of tuples
 * {namespace name, local part}, where namespace
 * name is a anyURI and local part is an NCName.
 * The lexical space of QName is the set of strings
 * that match the QName production of [Namespaces in
 * XML].
 *
 * @author Jeffrey Rodriguez
 * @author Mark Swinkles - List Validation refactoring
 * @version $Id$
 */
public class QNameDatatypeValidator extends  AbstractStringValidator {


    // for the NCName validator
    // REVISIT: synch issues?
    private static DatatypeValidator  fgStrValidator  = null;

    public QNameDatatypeValidator () throws InvalidDatatypeFacetException {
        this ( null, null, false ); // Native, No Facets defined, Restriction
    }

    public QNameDatatypeValidator ( DatatypeValidator base, Hashtable facets,
                                    boolean derivedByList ) throws InvalidDatatypeFacetException  {

        super (base, facets, derivedByList);
    }

    protected void assignAdditionalFacets(String key, Hashtable facets)  throws InvalidDatatypeFacetException{
        String msg = getErrorString(
            DatatypeMessageProvider.fgMessageKeys[DatatypeMessageProvider.ILLEGAL_STRING_FACET],
            new Object[] { key });
        throw new InvalidDatatypeFacetException(msg);       
    }


    protected void checkValueSpace (String content) throws InvalidDatatypeValueException {

        // check 3.2.18.c0 must: "NCName:NCName"
        try {
            int posColon = content.indexOf(':');
            if (posColon >= 0)
                fgStrValidator.validate(content.substring(0,posColon), null);
            fgStrValidator.validate(content.substring(posColon+1), null);
        } catch (InvalidDatatypeValueException idve) {
            throw new InvalidDatatypeValueException("Value '"+content+"' is not a valid QName");
        }
    }

    public int compare( String content, String facetValue ){
        Locale    loc       = Locale.getDefault();
        Collator  collator  = Collator.getInstance( loc );
        return collator.compare( content, facetValue );
    }

    protected static void setNCNameValidator (DatatypeValidator dv) {
        // make a string validator for NCName
        if ( fgStrValidator == null) {
            fgStrValidator = dv;
        }
    }
}
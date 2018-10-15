protected void checkContent( String content, boolean asBase )

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
import java.util.Enumeration;
import org.apache.xerces.impl.v2.SchemaSymbols;
import org.apache.xerces.impl.v2.util.regex.RegularExpression;
import org.apache.xerces.impl.v2.SchemaSymbols;

import org.apache.xerces.impl.XMLErrorReporter;
import org.apache.xerces.impl.v2.XSMessageFormatter;
import org.apache.xerces.impl.validation.ValidationContext;
/**
 *
 * BooleanValidator validates that content satisfies the W3C XML Datatype for Boolean
 *
 * @author Ted Leung
 * @author Jeffrey Rodriguez
 * @author Mark Swinkles - List Validation refactoring
 * @version  $Id$
 */

public class BooleanDatatypeValidator extends AbstractDatatypeValidator {

    private static  final String    fValueSpace[]    = { "false", "true", "0", "1"};

    public BooleanDatatypeValidator () {
        this( null, null, false, null ); // Native, No Facets defined, Restriction
    }

    public BooleanDatatypeValidator ( DatatypeValidator base, Hashtable facets,
                                      boolean derivedByList, XMLErrorReporter reporter) {
        fErrorReporter = reporter;
        fBaseValidator = base; // Set base type

        // list types are handled by ListDatatypeValidator, we do nothing here.
        if (derivedByList)
            return;

        // Set Facets if any defined
        if (facets != null) {
            for (Enumeration e = facets.keys(); e.hasMoreElements();) {
                String key = (String) e.nextElement();

                if (key.equals(SchemaSymbols.ELT_PATTERN)) {
                    fFacetsDefined |= DatatypeValidator.FACET_PATTERN;
                    fPattern = (String)facets.get(key);
                    if (fPattern != null)
                        fRegex = new RegularExpression(fPattern, "X" );
                }
                else {
                    String msg = getErrorString(
                                               DatatypeMessageProvider.fgMessageKeys[DatatypeMessageProvider.ILLEGAL_BOOLEAN_FACET],
                                               new Object[] { key});

                    if (fErrorReporter == null) {
                        throw new RuntimeException("InternalDatatype error BDV.");
                    }
                    fErrorReporter.reportError(XSMessageFormatter.SCHEMA_DOMAIN,
                                               "DatatypeFacetError", new Object [] { msg},
                                               XMLErrorReporter.SEVERITY_ERROR);                    
                }
            }
        }// End of facet setting
    }

    /**
     * validate that a string matches the boolean datatype
     * @param content A string containing the content to be validated
     *
     * @exception throws InvalidDatatypeException if the content is
     * is not valid.
     */

    public Object validate(String content, ValidationContext state) throws InvalidDatatypeValueException {
        checkContent( content, false );
        return null;
    }


    /**
     * Compare two boolean data types
     *
     * @param content1
     * @param content2
     * @return  0 if equal, 1 if not equal
     */
    public int compare( String content1, String content2) {
        if (content1.equals(content2)) {
            return 0;
        }
        Boolean b1 = Boolean.valueOf(content1);
        Boolean b2 = Boolean.valueOf(content2);

        return(b1.equals(b2))?0:1;
    }

    /**
     * Return a Hashtable that contains facet information
     *
     * @return Hashtable
     */

    public Hashtable getFacets() {
        return null;
    }

    //Begin private method definitions

    /**
      * Returns a copy of this object.
      */
    public Object clone() throws CloneNotSupportedException {
        throw new CloneNotSupportedException("clone() is not supported in "+this.getClass().getName());
    }


    /**
     * Checks content for validity.
     *
     * @param content
     * @exception InvalidDatatypeValueException
     */
    private void checkContent( String content, boolean asBase )
    throws InvalidDatatypeValueException {
        // validate against parent type if any
        // REVISIT: fast fix to avoid class cast exception
        if (this.fBaseValidator != null && !(fBaseValidator instanceof AnySimpleType)) {
            // validate content as a base type
            ((BooleanDatatypeValidator)fBaseValidator).checkContent(content, true);
        }

        // we check pattern first
        if ((fFacetsDefined & DatatypeValidator.FACET_PATTERN ) != 0) {
            if (fRegex == null || fRegex.matches( content) == false)
                throw new InvalidDatatypeValueException("Value'"+content+
                                                        "does not match regular expression facet" + fPattern );
        }

        // if this is a base validator, we only need to check pattern facet
        // all other facet were inherited by the derived type
        if (asBase)
            return;

        boolean  isContentInDomain = false;
        for (int i = 0;i<fValueSpace.length;i++) {
            if (content.equals(fValueSpace[i] ))
                isContentInDomain = true;
        }
        if (isContentInDomain == false) {
            String msg = getErrorString(
                                       DatatypeMessageProvider.fgMessageKeys[DatatypeMessageProvider.NOT_BOOLEAN],
                                       new Object[] { content});
            throw new InvalidDatatypeValueException(msg);
        }
    }
}
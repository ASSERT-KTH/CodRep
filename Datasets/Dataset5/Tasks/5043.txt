public Object validate(String content, ValidationContext state )

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

/**
 * AnySimpleType is the base of all simple types.
 * @author Sandy Gao
 * @version $Id$
 */
public class AnySimpleType extends AbstractDatatypeValidator {
    public  AnySimpleType() {
    }

    public AnySimpleType(DatatypeValidator base, Hashtable facets, boolean derivedByList, 
                         XMLErrorReporter reporter) {

        fBaseValidator = base;
        fErrorReporter = reporter;

        if (facets != null && facets.size() != 0) {
            String msg = getErrorString(
                                       DatatypeMessageProvider.fgMessageKeys[DatatypeMessageProvider.ILLEGAL_ANYSIMPLETYPE_FACET],
                                       new Object[] { facets.toString()});

            if (fErrorReporter == null) {
                throw new RuntimeException("InternalDatatype error AST.");
            }
            fErrorReporter.reportError(XSMessageFormatter.SCHEMA_DOMAIN,
                                       "DatatypeFacetError", new Object[]{msg},
                                       XMLErrorReporter.SEVERITY_ERROR);                    

        }
    }

    public Object validate(String content, Object state )
    throws InvalidDatatypeValueException {
        return null;
    }

    public int compare( String value1, String value2 ) {
        return -1;
    }


    public Object clone() throws CloneNotSupportedException  {
        throw new CloneNotSupportedException("clone() is not supported in "+this.getClass().getName());
    }

    public short getWSFacet () {
        return DatatypeValidator.PRESERVE;
    }
}
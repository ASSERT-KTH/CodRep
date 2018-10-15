fLocale = locale;

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 1999 The Apache Software Foundation.  All rights 
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
import java.util.Locale;

/**
 *
 * BooleanValidator validates that content satisfies the W3C XML Datatype for Boolean
 *
 * @author Ted Leung 
 * @version
 */

public class BooleanValidator implements InternalDatatypeValidator {
    private Locale fLocale = null;
	private DatatypeMessageProvider fMessageProvider = new DatatypeMessageProvider();
	/**
     * validate that a string matches the boolean datatype
     *
     * validate returns true or false depending on whether the string content is a
     * W3C integer type.
     * 
     * @param content A string containing the content to be validated
     *
     * @exception throws InvalidDatatypeException if the content is
     *  is not a W3C integer type
     */

	public void validate(String content) throws InvalidDatatypeValueException {
        if (!content.equals("true") && !content.equals("false"))
            throw new InvalidDatatypeValueException(
				getErrorString(DatatypeMessageProvider.NotBoolean,
							   DatatypeMessageProvider.MSG_NONE,
							   new Object[] { content }));
	}
	
	public void validate(int contentIndex) throws InvalidDatatypeValueException {
	}
	
	public void setFacets(Hashtable facets) throws UnknownFacetException, IllegalFacetException, IllegalFacetValueException {
	    throw new IllegalFacetException(); // boolean supports no facets
	}
	
	public void setFacets(int facets[]) throws UnknownFacetException, IllegalFacetException, IllegalFacetValueException {
	    throw new IllegalFacetException(); // boolean supports no facets
	}
	
	public void setBasetype(DatatypeValidator base) {
	}
	
    /**
     * set the locate to be used for error messages
     */
    public void setLocale(Locale locale) {
        // REVISIT when error handling is settled
    }

    private String getErrorString(int major, int minor, Object args[]) {
         try {
             return fMessageProvider.createMessage(fLocale, major, minor, args);
         } catch (Exception e) {
             return "Illegal Errorcode "+minor;
         }
    }
}
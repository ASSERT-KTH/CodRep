return HexBin.getDecodedDataLength(content.getBytes());

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
import org.apache.xerces.validators.schema.SchemaSymbols;
import org.apache.xerces.utils.regex.RegularExpression;
import org.apache.xerces.utils.HexBin;

/**
 * HexBinaryValidator validates that XML content is a W3C string type.
 * @author Ted Leung
 * @author Kito D. Mann, Virtua Communications Corp.
 * @author Jeffrey Rodriguez
 * @author Mark Swinkles - List Validation refactoring
 * @version $Id$
 */
public class HexBinaryDatatypeValidator extends AbstractStringValidator{
    

    public  HexBinaryDatatypeValidator () throws InvalidDatatypeFacetException{
        super ( null, null, false ); // Native, No Facets defined, Restriction

    }

    public HexBinaryDatatypeValidator ( DatatypeValidator base, Hashtable facets,
                                        boolean derivedByList ) throws InvalidDatatypeFacetException {

        super (base, facets, derivedByList); 
    }

    protected void assignAdditionalFacets(String key, Hashtable facets)  throws InvalidDatatypeFacetException{
        throw new InvalidDatatypeFacetException( getErrorString(DatatypeMessageProvider.ILLEGAL_STRING_FACET,
                                                        DatatypeMessageProvider.MSG_NONE, new Object[] { key }));
    }


    protected void checkValueSpace (String content) throws InvalidDatatypeValueException {
        if (getLength(content) <= 0) {
            throw new InvalidDatatypeValueException( "Value '"+content+"' is not encoded in Hex" );
        }
    }
    
    protected int getLength( String content) {
        return HexBin.getDataLength(content.getBytes());
    }


    public Object clone() throws CloneNotSupportedException  {
        HexBinaryDatatypeValidator newObj = null;
        try {
            newObj = new HexBinaryDatatypeValidator();

            newObj.fLocale           =  fLocale;
            newObj.fBaseValidator    =  fBaseValidator;
            newObj.fLength           =  fLength;
            newObj.fMaxLength        =  fMaxLength;
            newObj.fMinLength        =  fMinLength;
            newObj.fPattern          =  fPattern;
            newObj.fRegex            =  fRegex;
            newObj.fEnumeration      =  fEnumeration;
            newObj.fFacetsDefined    =  fFacetsDefined;
        } catch ( InvalidDatatypeFacetException ex) {
            ex.printStackTrace();
        }
        return newObj;
    }


}

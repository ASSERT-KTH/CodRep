import org.apache.xerces.impl.v2.util.regex.RegularExpression;

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 1999, 2000, 2001 The Apache Software Foundation.  All rights
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
 * originally based on software copyright (c) 2001, International
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
import org.apache.xerces.util.XMLChar;

/**
 * AbstractStringValidator is a base class for anyURI, string,
 * hexBinary, base64Binary, QName and Notation datatypes.
 *
 * @author Elena Litani
 * @version $Id$
 */
public abstract class AbstractStringValidator extends AbstractDatatypeValidator {

    protected int        fLength          = 0;
    protected int        fMaxLength       = Integer.MAX_VALUE;
    protected int        fMinLength       = 0;
    protected Vector     fEnumeration     = null;

    // _dummy_ facet for which special token parser to use
    public static final String FACET_SPECIAL_TOKEN       = "specialToken";
    public static final String SPECIAL_TOKEN_NONE        = "NONE";
    public static final String SPECIAL_TOKEN_NMTOKEN     = "NMTOKEN";
    public static final String SPECIAL_TOKEN_NAME        = "Name";
    public static final String SPECIAL_TOKEN_IDNAME      = "ID";
    public static final String SPECIAL_TOKEN_IDREFNAME   = "IDREF";
    public static final String SPECIAL_TOKEN_NCNAME      = "NCName";
    public static final String SPECIAL_TOKEN_IDNCNAME    = "ID";
    public static final String SPECIAL_TOKEN_IDREFNCNAME = "IDREF";
    public static final String SPECIAL_TOKEN_ENTITY      = "ENTITY";

    protected String fTokenType = SPECIAL_TOKEN_NONE; //flags special token parser

    public  AbstractStringValidator () throws InvalidDatatypeFacetException{
        this( null, null, false ); // Native, No Facets defined, Restriction

    }

    public AbstractStringValidator ( DatatypeValidator base, Hashtable facets,
                                     boolean derivedByList ) throws InvalidDatatypeFacetException {

        // Set base type
        fBaseValidator = base;

        if ( derivationList(derivedByList) )
            return;
        // Set Facets if any defined
        if ( facets != null ) {
            for ( Enumeration e = facets.keys(); e.hasMoreElements(); ) {
                String key = (String) e.nextElement();

                if ( key.equals(SchemaSymbols.ELT_LENGTH) ) {
                    fFacetsDefined |= DatatypeValidator.FACET_LENGTH;
                    String lengthValue = (String)facets.get(key);
                    try {
                        fLength     = Integer.parseInt( lengthValue );
                    }
                    catch ( NumberFormatException nfe ) {
                        throw new InvalidDatatypeFacetException("Length value '"+lengthValue+"' is invalid.");
                    }
                    // check 4.3.1.c0 must: length >= 0
                    if ( fLength < 0 )
                        throw new InvalidDatatypeFacetException("Length value '"+lengthValue+"'  must be a nonNegativeInteger.");

                }
                else if ( key.equals(SchemaSymbols.ELT_MINLENGTH) ) {
                    fFacetsDefined |= DatatypeValidator.FACET_MINLENGTH;
                    String minLengthValue = (String)facets.get(key);
                    try {
                        fMinLength     = Integer.parseInt( minLengthValue );
                    }
                    catch ( NumberFormatException nfe ) {
                        throw new InvalidDatatypeFacetException("minLength value '"+minLengthValue+"' is invalid.");
                    }
                    // check 4.3.2.c0 must: minLength >= 0
                    if ( fMinLength < 0 )
                        throw new InvalidDatatypeFacetException("minLength value '"+minLengthValue+"'  must be a nonNegativeInteger.");

                }
                else if ( key.equals(SchemaSymbols.ELT_MAXLENGTH) ) {
                    fFacetsDefined |= DatatypeValidator.FACET_MAXLENGTH;
                    String maxLengthValue = (String)facets.get(key);
                    try {
                        fMaxLength     = Integer.parseInt( maxLengthValue );
                    }
                    catch ( NumberFormatException nfe ) {
                        throw new InvalidDatatypeFacetException("maxLength value '"+maxLengthValue+"' is invalid.");
                    }
                    // check 4.3.3.c0 must: maxLength >= 0
                    if ( fMaxLength < 0 )
                        throw new InvalidDatatypeFacetException("maxLength value '"+maxLengthValue+"'  must be a nonNegativeInteger.");
                }
                else if ( key.equals(SchemaSymbols.ELT_PATTERN) ) {
                    fFacetsDefined |= DatatypeValidator.FACET_PATTERN;
                    fPattern = (String)facets.get(key);
                    if ( fPattern != null )
                        fRegex = new RegularExpression(fPattern, "X");
                }
                else if ( key.equals(SchemaSymbols.ELT_ENUMERATION) ) {
                    fEnumeration = (Vector)facets.get(key);
                    fFacetsDefined |= DatatypeValidator.FACET_ENUMERATION;
                }
                else if ( key.equals(DatatypeValidator.FACET_FIXED) ) {// fixed flags
                    fFlags = ((Short)facets.get(key)).shortValue();
                }
                else if ( key == FACET_SPECIAL_TOKEN ) {// special token parser
                    setTokenType((String)facets.get(key));
                }
                else {
                    assignAdditionalFacets(key, facets);
                }
            }

            if ( base != null ) {
                // check 4.3.5.c0 must: enumeration values from the value space of base
                //REVISIT: we should try either to delay it till validate() or
                //         store enumeration values in _value_space
                //         otherwise we end up creating and throwing objects
                if ( (fFacetsDefined & DatatypeValidator.FACET_ENUMERATION) != 0 &&
                     (fEnumeration != null) ) {
                    int i = 0;
                    try {
                        for ( ; i < fEnumeration.size(); i++ ) {
                            ((AbstractStringValidator)base).checkContent ((String)fEnumeration.elementAt(i), null, false);
                        }
                    }
                    catch ( Exception idve ) {
                        throw new InvalidDatatypeFacetException( "Value of enumeration = '" + fEnumeration.elementAt(i) +
                                                                 "' must be from the value space of base.");
                    }
                }
            }

            // check 4.3.1.c1 error: length & (maxLength | minLength)
            if ( ((fFacetsDefined & DatatypeValidator.FACET_LENGTH ) != 0 ) ) {
                if ( ((fFacetsDefined & DatatypeValidator.FACET_MAXLENGTH ) != 0 ) ) {
                    throw new InvalidDatatypeFacetException("It is an error for both length and maxLength to be members of facets." );
                }
                else if ( ((fFacetsDefined & DatatypeValidator.FACET_MINLENGTH ) != 0 ) ) {
                    throw new InvalidDatatypeFacetException("It is an error for both length and minLength to be members of facets." );
                }
            }

            // check 4.3.2.c1 must: minLength <= maxLength
            if ( ( (fFacetsDefined & ( DatatypeValidator.FACET_MINLENGTH |
                                       DatatypeValidator.FACET_MAXLENGTH) ) != 0 ) ) {
                if ( fMinLength > fMaxLength ) {
                    throw new InvalidDatatypeFacetException( "Value of minLength = '" + fMinLength +
                                                             "'must be <= the value of maxLength = '" + fMaxLength + "'.");
                }
            }

            // if base type is string, check facets against base.facets, and inherit facets from base
            if ( base != null ) {
                AbstractStringValidator strBase = (AbstractStringValidator)base;

                // check 4.3.1.c1 error: length & (base.maxLength | base.minLength)
                if ( ((fFacetsDefined & DatatypeValidator.FACET_LENGTH ) != 0 ) ) {
                    if ( ((strBase.fFacetsDefined & DatatypeValidator.FACET_MAXLENGTH ) != 0 ) ) {
                        throw new InvalidDatatypeFacetException("It is an error for both length and maxLength to be members of facets." );
                    }
                    else if ( ((strBase.fFacetsDefined & DatatypeValidator.FACET_MINLENGTH ) != 0 ) ) {
                        throw new InvalidDatatypeFacetException("It is an error for both length and minLength to be members of facets." );
                    }
                    else if ( (strBase.fFacetsDefined & DatatypeValidator.FACET_LENGTH) != 0 ) {
                        // check 4.3.1.c2 error: length != base.length
                        if ( fLength != strBase.fLength )
                            throw new InvalidDatatypeFacetException( "Value of length = '" + fLength +
                                                                     "' must be = the value of base.length = '" + strBase.fLength + "'.");
                    }
                }

                // check 4.3.1.c1 error: base.length & (maxLength | minLength)
                if ( ((strBase.fFacetsDefined & DatatypeValidator.FACET_LENGTH ) != 0 ) ) {
                    if ( ((fFacetsDefined & DatatypeValidator.FACET_MAXLENGTH ) != 0 ) ) {
                        throw new InvalidDatatypeFacetException("It is an error for both length and maxLength to be members of facets." );
                    }
                    else if ( ((fFacetsDefined & DatatypeValidator.FACET_MINLENGTH ) != 0 ) ) {
                        throw new InvalidDatatypeFacetException("It is an error for both length and minLength to be members of facets." );
                    }
                }

                // check 4.3.2.c1 must: minLength <= base.maxLength
                if ( ((fFacetsDefined & DatatypeValidator.FACET_MINLENGTH ) != 0 ) ) {
                    if ( (strBase.fFacetsDefined & DatatypeValidator.FACET_MAXLENGTH ) != 0 ) {
                        if ( fMinLength > strBase.fMaxLength ) {
                            throw new InvalidDatatypeFacetException( "Value of minLength = '" + fMinLength +
                                                                     "'must be <= the value of maxLength = '" + fMaxLength + "'.");
                        }
                    }
                    else if ( (strBase.fFacetsDefined & DatatypeValidator.FACET_MINLENGTH) != 0 ) {
                        if ( (strBase.fFlags & DatatypeValidator.FACET_MINLENGTH) != 0 &&
                             fMinLength != strBase.fMinLength ) {
                            throw new InvalidDatatypeFacetException( "minLength value = '" + fMinLength +
                                                                     "' must be equal to base.minLength value = '" +
                                                                     strBase.fMinLength + "' with attribute {fixed} = true" );
                        }
                        // check 4.3.2.c2 error: minLength < base.minLength
                        if ( fMinLength < strBase.fMinLength ) {
                            throw new InvalidDatatypeFacetException( "Value of minLength = '" + fMinLength +
                                                                     "' must be >= the value of base.minLength = '" + strBase.fMinLength + "'.");
                        }
                    }
                }


                // check 4.3.2.c1 must: base.minLength <= maxLength
                if ( ((strBase.fFacetsDefined & DatatypeValidator.FACET_MINLENGTH ) != 0 ) &&
                     ((fFacetsDefined & DatatypeValidator.FACET_MAXLENGTH ) != 0 ) ) {
                    if ( strBase.fMinLength > fMaxLength ) {
                        throw new InvalidDatatypeFacetException( "Value of minLength = '" + fMinLength +
                                                                 "'must be <= the value of maxLength = '" + fMaxLength + "'.");
                    }
                }

                // check 4.3.3.c1 error: maxLength > base.maxLength
                if ( (fFacetsDefined & DatatypeValidator.FACET_MAXLENGTH) != 0 ) {
                    if ( (strBase.fFlags & DatatypeValidator.FACET_MAXLENGTH) != 0 &&
                         fMaxLength != strBase.fMaxLength ) {
                        throw new InvalidDatatypeFacetException( "maxLength value = '" + fMaxLength +
                                                                 "' must be equal to base.maxLength value = '" +
                                                                 strBase.fMaxLength + "' with attribute {fixed} = true" );
                    }
                    if ( (strBase.fFacetsDefined & DatatypeValidator.FACET_MAXLENGTH) != 0 ) {
                        if ( fMaxLength > strBase.fMaxLength ) {

                            throw new InvalidDatatypeFacetException( "Value of maxLength = '" + fMaxLength +
                                                                     "' must be <= the value of base.maxLength = '" + strBase.fMaxLength + "'.");
                        }
                    }
                }


                checkBaseFacetConstraints();

                // inherit length
                if ( (strBase.fFacetsDefined & DatatypeValidator.FACET_LENGTH) != 0 ) {
                    if ( (fFacetsDefined & DatatypeValidator.FACET_LENGTH) == 0 ) {
                        fFacetsDefined |= DatatypeValidator.FACET_LENGTH;
                        fLength = strBase.fLength;
                    }
                }
                // inherit minLength
                if ( (strBase.fFacetsDefined & DatatypeValidator.FACET_MINLENGTH) != 0 ) {
                    if ( (fFacetsDefined & DatatypeValidator.FACET_MINLENGTH) == 0 ) {
                        fFacetsDefined |= DatatypeValidator.FACET_MINLENGTH;
                        fMinLength = strBase.fMinLength;
                    }
                }
                // inherit maxLength
                if ( (strBase.fFacetsDefined & DatatypeValidator.FACET_MAXLENGTH) != 0 ) {
                    if ( (fFacetsDefined & DatatypeValidator.FACET_MAXLENGTH) == 0 ) {
                        fFacetsDefined |= DatatypeValidator.FACET_MAXLENGTH;
                        fMaxLength = strBase.fMaxLength;
                    }
                }
                // inherit enumeration
                if ( (fFacetsDefined & DatatypeValidator.FACET_ENUMERATION) == 0 &&
                     (strBase.fFacetsDefined & DatatypeValidator.FACET_ENUMERATION) != 0 ) {
                    fFacetsDefined |= DatatypeValidator.FACET_ENUMERATION;
                    fEnumeration = strBase.fEnumeration;
                }
                inheritAdditionalFacets();

                //inherit fixed values
                fFlags |= strBase.fFlags;
            }
        }// End of Facets Setting
    }

    //
    // string has whiteSpace facet
    // all other datatypes will throw InvalidDatatypeFacetException
    //
    abstract protected void assignAdditionalFacets(String key, Hashtable facets)
    throws InvalidDatatypeFacetException;

    //
    // string has additional whiteSpace facet
    //
    protected void inheritAdditionalFacets() {
    }

    //
    // string needs to check constraints on whiteSpace
    // check is done against fBaseValidator
    //
    protected void checkBaseFacetConstraints() throws InvalidDatatypeFacetException {}

    protected boolean derivationList (boolean derivedByList) {
        // list types are handled by ListDatatypeValidator, we do nothing here.
        return derivedByList;
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
    public Object validate(String content, Object state)  throws InvalidDatatypeValueException {
        checkContent( content, state, false );
        return null;
    }


    private void checkContent( String content, Object state, boolean asBase )
    throws InvalidDatatypeValueException {
        // validate against parent type if any
        if ( fBaseValidator instanceof AbstractStringValidator ) {
            // validate content as a base type
            ((AbstractStringValidator)fBaseValidator).checkContent(content, state, true);
        }

        // we check pattern first
        if ( (fFacetsDefined & DatatypeValidator.FACET_PATTERN ) != 0 ) {
            if ( fRegex == null || fRegex.matches( content) == false )
                throw new InvalidDatatypeValueException("Value '"+content+
                                                        "' does not match regular expression facet '" + fPattern + "'." );
        }

        // validate special kinds of token, in place of old pattern matching
        if (fTokenType != SPECIAL_TOKEN_NONE) {
            validateToken(fTokenType, content);
        }

        // if this is a base validator, we only need to check pattern facet
        // all other facet were inherited by the derived type
        if ( asBase )
            return;

        checkValueSpace (content);
        int length = getLength(content);

        if ( (fFacetsDefined & DatatypeValidator.FACET_MAXLENGTH) != 0 ) {
            if ( length > fMaxLength ) {
                throw new InvalidDatatypeValueException("Value '"+content+
                                                        "' with length '"+length+
                                                        "' exceeds maximum length facet of '"+fMaxLength+"'.");
            }
        }
        if ( (fFacetsDefined & DatatypeValidator.FACET_MINLENGTH) != 0 ) {
            if ( length < fMinLength ) {
                throw new InvalidDatatypeValueException("Value '"+content+
                                                        "' with length '"+length+
                                                        "' is less than minimum length facet of '"+fMinLength+"'." );
            }
        }

        if ( (fFacetsDefined & DatatypeValidator.FACET_LENGTH) != 0 ) {
            if ( length != fLength ) {
                throw new InvalidDatatypeValueException("Value '"+content+
                                                        "' with length '"+length+
                                                        "' is not equal to length facet '"+fLength+"'.");
            }
        }

        if ( (fFacetsDefined & DatatypeValidator.FACET_ENUMERATION) != 0 &&
             (fEnumeration != null) ) {
            if ( fEnumeration.contains( content ) == false )
                throw new InvalidDatatypeValueException("Value '"+content+"' must be one of "+fEnumeration);
        }
    }
    protected int getLength( String content) {
        return content.length();
    }

    protected void checkValueSpace (String content) throws InvalidDatatypeValueException {}

    /**
     * Returns a copy of this object.
     *
     * @return
     * @exception CloneNotSupportedException
     */
    public Object clone() throws CloneNotSupportedException  {
        throw new CloneNotSupportedException("clone() is not supported in "+this.getClass().getName());
    }

    public void setTokenType (String tokenType) {
        fTokenType = tokenType;
    }


    protected static void validateToken(String tokenType, String content) throws InvalidDatatypeValueException {
        int len;
        if (content == null || (len = content.length()) == 0) {
            throw new InvalidDatatypeValueException(
                           "The length of the content must be greater than 0");
        }
        boolean seenErr = false;
        if (tokenType == SPECIAL_TOKEN_NMTOKEN) {
            // PATTERN "\\c+"
            seenErr = !XMLChar.isValidNmtoken(content);
        }
        else if (tokenType == SPECIAL_TOKEN_NAME ||
                   tokenType == SPECIAL_TOKEN_IDNAME ||
                   tokenType == SPECIAL_TOKEN_IDREFNAME) {
            // PATTERN "\\i\\c*"
            seenErr = !XMLChar.isValidName(content);
        } else if (tokenType == SPECIAL_TOKEN_NCNAME ||
                   tokenType == SPECIAL_TOKEN_IDNCNAME ||
                   tokenType == SPECIAL_TOKEN_IDREFNCNAME ||
                   tokenType == SPECIAL_TOKEN_ENTITY) {
            // PATTERN "[\\i-[:]][\\c-[:]]*"
            // REVISIT: !!!NOT IMPLEMENTED in XMLChar
            seenErr = !XMLChar.isValidNCName(content);
        }
        if (seenErr) {
            throw new InvalidDatatypeValueException(
                            "Value '"+content+"' is not a valid " + tokenType);
        }
    }
}
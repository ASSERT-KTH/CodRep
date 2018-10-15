if (fBaseValidator instanceof DecimalDatatypeValidator) {

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

import java.math.BigDecimal;
import java.util.Enumeration;
import java.util.Hashtable;
import java.util.Vector;
import java.io.IOException;
import org.apache.xerces.impl.v2.SchemaSymbols;
import org.apache.xerces.impl.v1.util.regex.RegularExpression;

/**
 *
 * DecimalDatatypeValidator validates that content satisfies the W3C XML Datatype for decimal
 *
 * @author  Elena Litani
 * @author Ted Leung
 * @author Jeffrey Rodriguez
 * @author Mark Swinkles - List Validation refactoring
 * @version $Id$
 */

public class DecimalDatatypeValidator extends AbstractNumericValidator {

    protected int                 fTotalDigits;
    protected int                 fFractionDigits;

    public DecimalDatatypeValidator () throws InvalidDatatypeFacetException {
        this( null, null, false ); // Native, No Facets defined, Restriction
    }

    public DecimalDatatypeValidator ( DatatypeValidator base, Hashtable facets,
                                      boolean derivedByList ) throws InvalidDatatypeFacetException {
        super (base, facets, derivedByList);
    }

    public int compare( String value1, String value2) {
        try {
            BigDecimal d1 = new BigDecimal(stripPlusIfPresent(value1));
            BigDecimal d2 = new BigDecimal(stripPlusIfPresent(value2));
            return d1.compareTo(d2);
        }
        catch (NumberFormatException e) {
            //REVISIT: should we throw exception??
            return -1;
        }
        catch (Exception e) {
            return -1;
        }
    }

    protected void inheritAdditionalFacets() {

        // inherit totalDigits
        if ((( ((DecimalDatatypeValidator)fBaseValidator).fFacetsDefined & DatatypeValidator.FACET_TOTALDIGITS) != 0) &&
            !((fFacetsDefined & DatatypeValidator.FACET_TOTALDIGITS) != 0)) {
            fFacetsDefined |= FACET_TOTALDIGITS;
            fTotalDigits = ((DecimalDatatypeValidator)fBaseValidator).fTotalDigits;
        }
        // inherit fractionDigits
        if ((( ((DecimalDatatypeValidator)fBaseValidator).fFacetsDefined & DatatypeValidator.FACET_FRACTIONDIGITS) != 0)
            && !((fFacetsDefined & DatatypeValidator.FACET_FRACTIONDIGITS) != 0)) {
            fFacetsDefined |= FACET_FRACTIONDIGITS;
            fFractionDigits = ((DecimalDatatypeValidator)fBaseValidator).fFractionDigits;
        }
    }

    protected void checkFacetConstraints() throws InvalidDatatypeFacetException{
        // check 4.3.12.c1 must: fractionDigits <= totalDigits
        if (((fFacetsDefined & DatatypeValidator.FACET_FRACTIONDIGITS) != 0) &&
            ((fFacetsDefined & DatatypeValidator.FACET_TOTALDIGITS) != 0)) {
            if (fFractionDigits > fTotalDigits)
                throw new InvalidDatatypeFacetException( "fractionDigits value ='" + this.fFractionDigits + "'must be <= totalDigits value ='" +
                                                         this.fTotalDigits + "'. " );
        }
    }

    protected void checkBaseFacetConstraints() throws InvalidDatatypeFacetException{

        // check 4.3.11.c1 error: totalDigits > base.totalDigits
        if (((fFacetsDefined & DatatypeValidator.FACET_TOTALDIGITS) != 0)) {
            if ((( ((DecimalDatatypeValidator)fBaseValidator).fFacetsDefined & DatatypeValidator.FACET_TOTALDIGITS) != 0)) {
                if ((((DecimalDatatypeValidator)fBaseValidator).fFlags & DatatypeValidator.FACET_TOTALDIGITS) != 0 &&
                    fTotalDigits != ((DecimalDatatypeValidator)fBaseValidator).fTotalDigits) {
                    throw new InvalidDatatypeFacetException("totalDigits value = '" + fTotalDigits +
                                                            "' must be equal to base.totalDigits value = '" +
                                                            ((DecimalDatatypeValidator)fBaseValidator).fTotalDigits +
                                                            "' with attribute {fixed} = true" );
                }
                if (fTotalDigits > ((DecimalDatatypeValidator)fBaseValidator).fTotalDigits) {
                    throw new InvalidDatatypeFacetException( "totalDigits value ='" + fTotalDigits + "' must be <= base.totalDigits value ='" +
                                                             ((DecimalDatatypeValidator)fBaseValidator).fTotalDigits + "'." );
                }
            }
        }
        // check fixed value for fractionDigits
        if (((fFacetsDefined & DatatypeValidator.FACET_FRACTIONDIGITS) != 0)) {
            if ((( ((DecimalDatatypeValidator)fBaseValidator).fFacetsDefined & DatatypeValidator.FACET_FRACTIONDIGITS) != 0)) {
                if ((((DecimalDatatypeValidator)fBaseValidator).fFlags & DatatypeValidator.FACET_FRACTIONDIGITS) != 0 &&
                    fFractionDigits != ((DecimalDatatypeValidator)fBaseValidator).fFractionDigits) {
                    throw new InvalidDatatypeFacetException("fractionDigits value = '" + fFractionDigits +
                                                            "' must be equal to base.fractionDigits value = '" +
                                                            ((DecimalDatatypeValidator)fBaseValidator).fFractionDigits +
                                                            "' with attribute {fixed} = true" );
                }
            }
        }
    }

    protected void assignAdditionalFacets(String key,  Hashtable facets ) throws InvalidDatatypeFacetException{

        String value = null;
        try {
            if (key.equals(SchemaSymbols.ELT_TOTALDIGITS)) {
                value = ((String) facets.get(key ));
                fFacetsDefined |= DatatypeValidator.FACET_TOTALDIGITS;
                fTotalDigits      = Integer.parseInt(value );
                // check 4.3.11.c0 must: totalDigits > 0
                if (fTotalDigits <= 0)
                    throw new InvalidDatatypeFacetException("totalDigits value '"+fTotalDigits+"' must be a positiveInteger.");
            }
            else if (key.equals(SchemaSymbols.ELT_FRACTIONDIGITS)) {
                value = ((String) facets.get(key ));
                fFacetsDefined |= DatatypeValidator.FACET_FRACTIONDIGITS;
                fFractionDigits          = Integer.parseInt( value );
                // check 4.3.12.c0 must: fractionDigits > 0
                if (fFractionDigits < 0)
                    throw new InvalidDatatypeFacetException("fractionDigits value '"+fFractionDigits+"' must be a positiveInteger.");
            }
            else {
                String msg = getErrorString(
                                           DatatypeMessageProvider.fgMessageKeys[DatatypeMessageProvider.ILLEGAL_DECIMAL_FACET],
                                           new Object [] { value, key});
                throw new InvalidDatatypeFacetException(msg);
            }
        }
        catch (Exception ex) {
            String msg = getErrorString(
                                       DatatypeMessageProvider.fgMessageKeys[DatatypeMessageProvider.ILLEGAL_FACET_VALUE],
                                       new Object [] { value, key});
            throw new InvalidDatatypeFacetException(msg);
        }
    }

    protected int compareValues (Object value1, Object value2) {
        return((BigDecimal)value1).compareTo((BigDecimal)value2);
    }

    protected void setMaxInclusive (String value) {
        fMaxInclusive = new BigDecimal(stripPlusIfPresent(value));
    }
    protected void setMinInclusive (String value) {
        fMinInclusive = new BigDecimal(stripPlusIfPresent(value));

    }
    protected void setMaxExclusive (String value) {
        fMaxExclusive = new BigDecimal(stripPlusIfPresent(value));

    }
    protected void setMinExclusive (String value) {
        fMinExclusive = new BigDecimal(stripPlusIfPresent(value));

    }
    protected void setEnumeration (Vector enumeration) throws InvalidDatatypeValueException{
        if (enumeration != null) {
            fEnumeration = new BigDecimal[enumeration.size()];
            Object baseEnum=null;
            try {

                for (int i = 0; i < enumeration.size(); i++) {
                    fEnumeration[i] = new BigDecimal( stripPlusIfPresent(((String) enumeration.elementAt(i))));;
                    ((DecimalDatatypeValidator)fBaseValidator).validate((String)enumeration.elementAt(i), null);
                }
            }
            catch (Exception e) {
                throw new InvalidDatatypeValueException(e.getMessage());
            }
        }
    }


    protected String getMaxInclusive (boolean isBase) {
        return(isBase)?(((DecimalDatatypeValidator)fBaseValidator).fMaxInclusive.toString())
        :((BigDecimal)fMaxInclusive).toString();
    }
    protected String getMinInclusive (boolean isBase) {
        return(isBase)?(((DecimalDatatypeValidator)fBaseValidator).fMinInclusive.toString())
        :((BigDecimal)fMinInclusive).toString();
    }
    protected String getMaxExclusive (boolean isBase) {
        return(isBase)?(((DecimalDatatypeValidator)fBaseValidator).fMaxExclusive.toString())
        :((BigDecimal)fMaxExclusive).toString();
    }
    protected String getMinExclusive (boolean isBase) {
        return(isBase)?(((DecimalDatatypeValidator)fBaseValidator).fMinExclusive.toString())
        :((BigDecimal)fMinExclusive).toString();
    }



    protected void checkContent(String content, Object state, Vector enumeration, boolean asBase)
    throws InvalidDatatypeValueException {
        // validate against parent type if any
        if (this.fBaseValidator != null) {
            // validate content as a base type
            ((DecimalDatatypeValidator)fBaseValidator).checkContent(content, state, enumeration, true);
        }

        // we check pattern first
        if ((fFacetsDefined & DatatypeValidator.FACET_PATTERN ) != 0) {
            if (fRegex == null || fRegex.matches( content) == false)
                throw new InvalidDatatypeValueException("Value'"+content+
                                                        "' does not match regular expression facet " + fRegex.getPattern() );
        }

        // if this is a base validator, we only need to check pattern facet
        // all other facet were inherited by the derived type
        if (asBase)
            return;

        BigDecimal d = null; // Is content a Decimal
        try {
            d = new BigDecimal( stripPlusIfPresent( content));
        }
        catch (Exception nfe) {
            String msg = getErrorString(
                                       DatatypeMessageProvider.fgMessageKeys[DatatypeMessageProvider.NOT_DECIMAL],
                                       new Object[] { "'" + content +"'"});
            throw new InvalidDatatypeValueException(msg);
        }

        if (enumeration != null) { //the call was made from List or Union
            int size= enumeration.size();
            BigDecimal[]     enumDecimal  = new BigDecimal[size];
            int i = 0;
            try {
                for (; i < size; i++)
                    enumDecimal[i] = new BigDecimal( stripPlusIfPresent(((String) enumeration.elementAt(i))));
            }
            catch (NumberFormatException nfe) {
                String msg = getErrorString(
                                           DatatypeMessageProvider.fgMessageKeys[DatatypeMessageProvider.INVALID_ENUM_VALUE],
                                           new Object [] { enumeration.elementAt(i)});
                throw new InvalidDatatypeValueException(msg);
            }enumCheck(d, enumDecimal);
        }

        if ((fFacetsDefined & DatatypeValidator.FACET_FRACTIONDIGITS)!=0) {
            if (d.scale() > fFractionDigits) {
                String msg = getErrorString(
                                           DatatypeMessageProvider.fgMessageKeys[DatatypeMessageProvider.FRACTION_EXCEEDED],
                                           new Object[] { 
                                               "'" + content + "'" + " with fractionDigits = '"+ d.scale() +"'", 
                                               "'" + fFractionDigits + "'"
                                           });
                throw new InvalidDatatypeValueException(msg);
            }
        }
        if ((fFacetsDefined & DatatypeValidator.FACET_TOTALDIGITS)!=0) {
            int totalDigits = d.movePointRight(d.scale()).toString().length() -
                              ((d.signum() < 0) ? 1 : 0); // account for minus sign
            if (totalDigits > fTotalDigits) {

                String msg = getErrorString(
                                           DatatypeMessageProvider.fgMessageKeys[DatatypeMessageProvider.TOTALDIGITS_EXCEEDED],
                                           new Object[] { 
                                               "'" + content + "'" + " with totalDigits = '"+ totalDigits +"'", 
                                               "'" + fTotalDigits + "'"
                                           });
                throw new InvalidDatatypeValueException(msg);
            }
        }
        boundsCheck(d);
        if (fEnumeration != null)
            enumCheck(d, (BigDecimal[]) fEnumeration);

        return;

    }

    /**
     * This class deals with a bug in BigDecimal class
     * present up to version 1.1.2. 1.1.3 knows how
     * to deal with the + sign.
     *
     * This method strips the first '+' if it found
     * alone such as.
     * +33434.344
     *
     * If we find +- then nothing happens we just
     * return the string passed
     *
     * @param value
     * @return
     */
    static private String stripPlusIfPresent( String value ) {
        String strippedPlus = value;

        if (value.length() >= 2 && value.charAt(0) == '+' && value.charAt(1) != '-') {
            strippedPlus = value.substring(1);
        }
        return strippedPlus;
    }

    private void enumCheck(BigDecimal v, BigDecimal[] enum) throws InvalidDatatypeValueException {
        for (int i = 0; i < enum.length; i++) {
            if (v.equals(enum[i] )) {
                return;
            }
        }
        String msg = getErrorString(
                                   DatatypeMessageProvider.fgMessageKeys[DatatypeMessageProvider.NOT_ENUM_VALUE],
                                   new Object [] { v});
        throw new InvalidDatatypeValueException(msg);}

}
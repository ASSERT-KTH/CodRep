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


import java.util.Enumeration;
import java.util.Hashtable;
import java.util.Vector;
import java.io.IOException;
import org.apache.xerces.impl.v2.SchemaSymbols;
import org.apache.xerces.impl.v1.util.regex.RegularExpression;

/**
 * AbstractNumericFacetValidator is a base class for decimal, double, float,
 * and all date/time datatype validators. It implements evaluation of common facets - 
 * minInclusive, maxInclusive, minExclusive, maxExclusive according to schema specs.
 * 
 * @author Elena Litani
 * @version $Id$
 */

public abstract class AbstractNumericFacetValidator extends AbstractDatatypeValidator {

    protected Object[]            fEnumeration            = null;
    protected Object              fMaxInclusive           = null;
    protected Object              fMaxExclusive           = null;
    protected Object              fMinInclusive           = null;
    protected Object              fMinExclusive           = null;

    protected static final short INDETERMINATE=2;

    public  AbstractNumericFacetValidator () throws InvalidDatatypeFacetException {
        this( null, null, false ); // Native, No Facets defined, Restriction
    }

    public AbstractNumericFacetValidator ( DatatypeValidator base, 
                                           Hashtable facets, 
                                           boolean derivedByList) throws InvalidDatatypeFacetException {         
        fBaseValidator = base;

        // list types are handled by ListDatatypeValidator, we do nothing here.
        if (derivedByList)
            return;
        initializeValues();
        // Set Facets if any defined
        if (facets != null) {
            int result; // result of comparison
            Vector enumeration = null;
            for (Enumeration e = facets.keys(); e.hasMoreElements();) {
                String key   = (String) e.nextElement();
                String value = null;
                try {
                    if (key.equals(SchemaSymbols.ELT_PATTERN)) {
                        fFacetsDefined |= DatatypeValidator.FACET_PATTERN;
                        fPattern = (String) facets.get(key);
                        if (fPattern != null)
                            fRegex = new RegularExpression(fPattern, "X" );
                    }
                    else if (key.equals(SchemaSymbols.ELT_ENUMERATION)) {
                        enumeration     = (Vector)facets.get(key);
                        fFacetsDefined |= DatatypeValidator.FACET_ENUMERATION;
                    }
                    else if (key.equals(SchemaSymbols.ELT_MAXINCLUSIVE)) {
                        value = ((String) facets.get(key ));
                        fFacetsDefined |= DatatypeValidator.FACET_MAXINCLUSIVE;
                        setMaxInclusive(value);
                    }
                    else if (key.equals(SchemaSymbols.ELT_MAXEXCLUSIVE)) {
                        value = ((String) facets.get(key ));
                        fFacetsDefined |= DatatypeValidator.FACET_MAXEXCLUSIVE;
                        setMaxExclusive(value);
                    }
                    else if (key.equals(SchemaSymbols.ELT_MININCLUSIVE)) {
                        value = ((String) facets.get(key ));
                        fFacetsDefined |= DatatypeValidator.FACET_MININCLUSIVE;
                        setMinInclusive(value);
                    }
                    else if (key.equals(SchemaSymbols.ELT_MINEXCLUSIVE)) {
                        value = ((String) facets.get(key ));
                        fFacetsDefined |= DatatypeValidator.FACET_MINEXCLUSIVE;
                        setMinExclusive(value);
                    }
                    else if (key.equals(DatatypeValidator.FACET_FIXED)) {// fixed flags
                        fFlags = ((Short)facets.get(key)).shortValue();
                    }
                    else {
                        assignAdditionalFacets(key, facets);
                    }
                }
                catch (Exception ex) {
                    if (value == null) {
                        //invalid facet error
                        throw new InvalidDatatypeFacetException( ex.getMessage());
                    }
                    else {
                        String msg = getErrorString(
                                                   DatatypeMessageProvider.fgMessageKeys[DatatypeMessageProvider.ILLEGAL_FACET_VALUE], 
                                                   new Object [] { value, key});
                        throw new InvalidDatatypeFacetException(msg);
                    }
                }
            }

            if (fFacetsDefined != 0) {
                // check 4.3.8.c1 error: maxInclusive + maxExclusive
                if (((fFacetsDefined & DatatypeValidator.FACET_MAXEXCLUSIVE) != 0) && 
                    ((fFacetsDefined & DatatypeValidator.FACET_MAXINCLUSIVE) != 0)) {
                    throw new InvalidDatatypeFacetException( "It is an error for both maxInclusive and maxExclusive to be specified for the same datatype." );
                }
                // check 4.3.9.c1 error: minInclusive + minExclusive
                if (((fFacetsDefined & DatatypeValidator.FACET_MINEXCLUSIVE) != 0) && 
                    ((fFacetsDefined & DatatypeValidator.FACET_MININCLUSIVE) != 0)) {
                    throw new InvalidDatatypeFacetException( "It is an error for both minInclusive and minExclusive to be specified for the same datatype." );
                }

                // check 4.3.7.c1 must: minInclusive <= maxInclusive
                if (((fFacetsDefined & DatatypeValidator.FACET_MAXINCLUSIVE) != 0) && 
                    ((fFacetsDefined & DatatypeValidator.FACET_MININCLUSIVE) != 0)) {
                    result =  compareValues(fMinInclusive, fMaxInclusive);
                    if (result == 1 || result == INDETERMINATE)
                        throw new InvalidDatatypeFacetException( "minInclusive value ='" + getMinInclusive(false) + "'must be <= maxInclusive value ='" +
                                                                 getMaxInclusive(false) + "'. " );
                }
                // check 4.3.8.c2 must: minExclusive <= maxExclusive ??? minExclusive < maxExclusive
                if (((fFacetsDefined & DatatypeValidator.FACET_MAXEXCLUSIVE) != 0) && ((fFacetsDefined & DatatypeValidator.FACET_MINEXCLUSIVE) != 0)) {
                    result =compareValues(fMinExclusive, fMaxExclusive); 
                    if (result == 1 || result == INDETERMINATE)
                        throw new InvalidDatatypeFacetException( "minExclusive value ='" + getMinExclusive(false) + "'must be <= maxExclusive value ='" +
                                                                 getMaxExclusive(false) + "'. " );
                }
                // check 4.3.9.c2 must: minExclusive < maxInclusive
                if (((fFacetsDefined & DatatypeValidator.FACET_MAXINCLUSIVE) != 0) && ((fFacetsDefined & DatatypeValidator.FACET_MINEXCLUSIVE) != 0)) {
                    if (compareValues(fMinExclusive, fMaxInclusive) != -1)
                        throw new InvalidDatatypeFacetException( "minExclusive value ='" + getMinExclusive(false) + "'must be > maxInclusive value ='" +
                                                                 getMaxInclusive(false) + "'. " );
                }
                // check 4.3.10.c1 must: minInclusive < maxExclusive
                if (((fFacetsDefined & DatatypeValidator.FACET_MAXEXCLUSIVE) != 0) && ((fFacetsDefined & DatatypeValidator.FACET_MININCLUSIVE) != 0)) {
                    if (compareValues(fMinInclusive, fMaxExclusive) != -1)
                        throw new InvalidDatatypeFacetException( "minInclusive value ='" + getMinInclusive(false) + "'must be < maxExclusive value ='" +
                                                                 getMaxExclusive(false) + "'. " );
                }
                checkFacetConstraints();

            }

            if (base != null) {
                AbstractNumericFacetValidator numBase = (AbstractNumericFacetValidator)base;
                if (fFacetsDefined != 0) {

                    // check 4.3.7.c2 error:
                    // maxInclusive > base.maxInclusive
                    // maxInclusive >= base.maxExclusive
                    // maxInclusive < base.minInclusive
                    // maxInclusive <= base.minExclusive

                    if (((fFacetsDefined & DatatypeValidator.FACET_MAXINCLUSIVE) != 0)) {
                        if (((numBase.fFacetsDefined & DatatypeValidator.FACET_MAXINCLUSIVE) != 0)) {
                            result = compareValues(fMaxInclusive, numBase.fMaxInclusive); 
                            if ((numBase.fFlags & DatatypeValidator.FACET_MAXINCLUSIVE) != 0 &&
                                result != 0) {
                                throw new InvalidDatatypeFacetException( "maxInclusive value = '" + getMaxInclusive(false) + 
                                                                         "' must be equal to base.maxInclusive value = '" +
                                                                         getMaxInclusive(true) + "' with attribute {fixed} = true" );
                            }
                            if (result == 1 || result == INDETERMINATE) {
                                throw new InvalidDatatypeFacetException( "maxInclusive value ='" + getMaxInclusive(false) + "' must be <= base.maxInclusive value ='" +
                                                                         getMaxInclusive(true) + "'." );
                            }
                        }
                        if (((numBase.fFacetsDefined & DatatypeValidator.FACET_MAXEXCLUSIVE) != 0) &&
                            compareValues(fMaxInclusive, numBase.fMaxExclusive) != -1)
                            throw new InvalidDatatypeFacetException(
                                                                   "maxInclusive value ='" + getMaxInclusive(false) + "' must be < base.maxExclusive value ='" +
                                                                   getMaxExclusive(true) + "'." );
                        if ((( numBase.fFacetsDefined & DatatypeValidator.FACET_MININCLUSIVE) != 0)) {
                            result = compareValues(fMaxInclusive, numBase.fMinInclusive);
                            if (result == -1 || result == INDETERMINATE) {
                                throw new InvalidDatatypeFacetException( "maxInclusive value ='" + getMaxInclusive(false) + "' must be >= base.minInclusive value ='" +
                                                                         getMinInclusive(true) + "'." );
                            }
                        }
                        if ((( numBase.fFacetsDefined & DatatypeValidator.FACET_MINEXCLUSIVE) != 0) &&
                            compareValues(fMaxInclusive, numBase.fMinExclusive ) != 1)
                            throw new InvalidDatatypeFacetException(
                                                                   "maxInclusive value ='" + getMaxInclusive(false) + "' must be > base.minExclusive value ='" +
                                                                   getMinExclusive(true) + "'." );
                    }

                    // check 4.3.8.c3 error:
                    // maxExclusive > base.maxExclusive
                    // maxExclusive > base.maxInclusive
                    // maxExclusive <= base.minInclusive
                    // maxExclusive <= base.minExclusive
                    if (((fFacetsDefined & DatatypeValidator.FACET_MAXEXCLUSIVE) != 0)) {
                        if ((( numBase.fFacetsDefined & DatatypeValidator.FACET_MAXEXCLUSIVE) != 0)) {
                            result= compareValues(fMaxExclusive, numBase.fMaxExclusive);
                            if ((numBase.fFlags & DatatypeValidator.FACET_MAXEXCLUSIVE) != 0 &&
                                result != 0) {
                                throw new InvalidDatatypeFacetException( "maxExclusive value = '" + getMaxExclusive(false) + 
                                                                         "' must be equal to base.maxExclusive value = '" +
                                                                         getMaxExclusive(true) + "' with attribute {fixed} = true" );
                            }
                            if (result == 1 || result == INDETERMINATE) {
                                throw new InvalidDatatypeFacetException( "maxExclusive value ='" + getMaxExclusive(false) + "' must be < base.maxExclusive value ='" +
                                                                         getMaxExclusive(true) + "'." );
                            }
                        }
                        if ((( numBase.fFacetsDefined & DatatypeValidator.FACET_MAXINCLUSIVE) != 0)) {
                            result= compareValues(fMaxExclusive, numBase.fMaxInclusive);
                            if (result == 1 || result == INDETERMINATE) {
                                throw new InvalidDatatypeFacetException( "maxExclusive value ='" + getMaxExclusive(false) + "' must be <= base.maxInclusive value ='" +
                                                                         getMaxInclusive(true) + "'." );
                            }
                        }
                        if ((( numBase.fFacetsDefined & DatatypeValidator.FACET_MINEXCLUSIVE) != 0) &&
                            compareValues(fMaxExclusive, numBase.fMinExclusive ) != 1)
                            throw new InvalidDatatypeFacetException( "maxExclusive value ='" + getMaxExclusive(false) + "' must be > base.minExclusive value ='" +
                                                                     getMinExclusive(true) + "'." );
                        if ((( numBase.fFacetsDefined & DatatypeValidator.FACET_MININCLUSIVE) != 0) &&
                            compareValues(fMaxExclusive, numBase.fMinInclusive) != 1)
                            throw new InvalidDatatypeFacetException( "maxExclusive value ='" + getMaxExclusive(false) + "' must be > base.minInclusive value ='" +
                                                                     getMinInclusive(true) + "'." );
                    }

                    // check 4.3.9.c3 error:
                    // minExclusive < base.minExclusive
                    // minExclusive > base.maxInclusive ??? minExclusive >= base.maxInclusive
                    // minExclusive < base.minInclusive
                    // minExclusive >= base.maxExclusive
                    if (((fFacetsDefined & DatatypeValidator.FACET_MINEXCLUSIVE) != 0)) {
                        if ((( numBase.fFacetsDefined & DatatypeValidator.FACET_MINEXCLUSIVE) != 0)) {
                            result= compareValues(fMinExclusive, numBase.fMinExclusive);
                            if ((numBase.fFlags & DatatypeValidator.FACET_MINEXCLUSIVE) != 0 &&
                                result != 0) {
                                throw new InvalidDatatypeFacetException( "minExclusive value = '" + getMinExclusive(false) + 
                                                                         "' must be equal to base.minExclusive value = '" +
                                                                         getMinExclusive(true) + "' with attribute {fixed} = true" );
                            }
                            if (result == -1 || result == INDETERMINATE) {
                                throw new InvalidDatatypeFacetException( "minExclusive value ='" + getMinExclusive(false) + "' must be >= base.minExclusive value ='" +
                                                                         getMinExclusive(true) + "'." );
                            }
                        }
                        if ((( numBase.fFacetsDefined & DatatypeValidator.FACET_MAXINCLUSIVE) != 0)) {
                            result=compareValues(fMinExclusive, numBase.fMaxInclusive);
                            if (result == 1 || result == INDETERMINATE) {
                                throw new InvalidDatatypeFacetException(
                                                                       "minExclusive value ='" + getMinExclusive(false) + "' must be <= base.maxInclusive value ='" +
                                                                       getMaxInclusive(true) + "'." );
                            }
                        }
                        if ((( numBase.fFacetsDefined & DatatypeValidator.FACET_MININCLUSIVE) != 0)) {
                            result = compareValues(fMinExclusive, numBase.fMinInclusive);
                            if (result == -1 || result == INDETERMINATE) {
                                throw new InvalidDatatypeFacetException(
                                                                       "minExclusive value ='" + getMinExclusive(false) + "' must be >= base.minInclusive value ='" +
                                                                       getMinInclusive(true) + "'." );
                            }
                        }
                        if ((( numBase.fFacetsDefined & DatatypeValidator.FACET_MAXEXCLUSIVE) != 0) &&
                            compareValues(fMinExclusive, numBase.fMaxExclusive) != -1)
                            throw new InvalidDatatypeFacetException( "minExclusive value ='" + getMinExclusive(false) + "' must be < base.maxExclusive value ='" +
                                                                     getMaxExclusive(true) + "'." );
                    }

                    // check 4.3.10.c2 error:
                    // minInclusive < base.minInclusive
                    // minInclusive > base.maxInclusive
                    // minInclusive <= base.minExclusive
                    // minInclusive >= base.maxExclusive
                    if (((fFacetsDefined & DatatypeValidator.FACET_MININCLUSIVE) != 0)) {
                        if (((numBase.fFacetsDefined & DatatypeValidator.FACET_MININCLUSIVE) != 0)) {
                            result = compareValues(fMinInclusive, numBase.fMinInclusive); 
                            if ((numBase.fFlags & DatatypeValidator.FACET_MININCLUSIVE) != 0 &&
                                result != 0) {
                                throw new InvalidDatatypeFacetException( "minInclusive value = '" + getMinInclusive(false) + 
                                                                         "' must be equal to base.minInclusive value = '" +
                                                                         getMinInclusive(true) + "' with attribute {fixed} = true" );
                            }
                            if (result == -1 || result == INDETERMINATE) {
                                throw new InvalidDatatypeFacetException( "minInclusive value ='" + getMinInclusive(false) + "' must be >= base.minInclusive value ='" +
                                                                         getMinInclusive(true) + "'." );
                            }
                        }
                        if ((( numBase.fFacetsDefined & DatatypeValidator.FACET_MAXINCLUSIVE) != 0)) {
                            result=compareValues(fMinInclusive, numBase.fMaxInclusive);
                            if (result == 1 || result == INDETERMINATE) {
                                throw new InvalidDatatypeFacetException( "minInclusive value ='" + getMinInclusive(false) + "' must be <= base.maxInclusive value ='" +
                                                                         getMaxInclusive(true) + "'." );
                            }
                        }
                        if ((( numBase.fFacetsDefined & DatatypeValidator.FACET_MINEXCLUSIVE) != 0) &&
                            compareValues(fMinInclusive, numBase.fMinExclusive ) != 1)
                            throw new InvalidDatatypeFacetException( "minInclusive value ='" + getMinInclusive(false) + "' must be > base.minExclusive value ='" +
                                                                     getMinExclusive(true) + "'." );
                        if ((( numBase.fFacetsDefined & DatatypeValidator.FACET_MAXEXCLUSIVE) != 0) &&
                            compareValues(fMinInclusive, numBase.fMaxExclusive) != -1)
                            throw new InvalidDatatypeFacetException( "minInclusive value ='" + getMinInclusive(false) + "' must be < base.maxExclusive value ='" +
                                                                     getMaxExclusive(true) + "'." );
                    }
                    checkBaseFacetConstraints();

                }
                // check question error: fractionDigits > base.fractionDigits ???
                // check question error: fractionDigits > base.totalDigits ???
                // check question error: totalDigits conflicts with bounds ???

                // inherit enumeration
                if ((fFacetsDefined & DatatypeValidator.FACET_ENUMERATION) == 0 &&
                    (numBase.fFacetsDefined & DatatypeValidator.FACET_ENUMERATION) != 0) {
                    fFacetsDefined |= DatatypeValidator.FACET_ENUMERATION;
                    fEnumeration = numBase.fEnumeration;
                }
                // inherit maxExclusive
                if ((( numBase.fFacetsDefined & DatatypeValidator.FACET_MAXEXCLUSIVE) != 0) &&
                    !((fFacetsDefined & DatatypeValidator.FACET_MAXEXCLUSIVE) != 0) && !((fFacetsDefined & DatatypeValidator.FACET_MAXINCLUSIVE) != 0)) {
                    fFacetsDefined |= FACET_MAXEXCLUSIVE;
                    fMaxExclusive = numBase.fMaxExclusive;
                }
                // inherit maxInclusive
                if ((( numBase.fFacetsDefined & DatatypeValidator.FACET_MAXINCLUSIVE) != 0) &&
                    !((fFacetsDefined & DatatypeValidator.FACET_MAXEXCLUSIVE) != 0) && !((fFacetsDefined & DatatypeValidator.FACET_MAXINCLUSIVE) != 0)) {
                    fFacetsDefined |= FACET_MAXINCLUSIVE;
                    fMaxInclusive = numBase.fMaxInclusive;
                }
                // inherit minExclusive
                if ((( numBase.fFacetsDefined & DatatypeValidator.FACET_MINEXCLUSIVE) != 0) &&
                    !((fFacetsDefined & DatatypeValidator.FACET_MINEXCLUSIVE) != 0) && !((fFacetsDefined & DatatypeValidator.FACET_MININCLUSIVE) != 0)) {
                    fFacetsDefined |= FACET_MINEXCLUSIVE;
                    fMinExclusive = numBase.fMinExclusive;
                }
                // inherit minExclusive
                if ((( numBase.fFacetsDefined & DatatypeValidator.FACET_MININCLUSIVE) != 0) &&
                    !((fFacetsDefined & DatatypeValidator.FACET_MINEXCLUSIVE) != 0) && !((fFacetsDefined & DatatypeValidator.FACET_MININCLUSIVE) != 0)) {
                    fFacetsDefined |= FACET_MININCLUSIVE;
                    fMinInclusive = numBase.fMinInclusive;
                }

                inheritAdditionalFacets();

                //inherit fixed values
                fFlags |= numBase.fFlags;

                // check 4.3.5.c0 must: enumeration values from the value space of base
                if ((fFacetsDefined & DatatypeValidator.FACET_ENUMERATION) != 0) {
                    if (enumeration != null) {
                        try {
                            setEnumeration(enumeration);
                        }
                        catch (Exception idve) {
                            throw new InvalidDatatypeFacetException( idve.getMessage());
                        }
                    }

                }
            }
        }//End of Facet setup
    }


    //
    // Compares values in value space of give datatype    
    //
    abstract protected int compareValues (Object value1, Object value2);            

    //
    // set* functions used to set facets values
    //
    abstract protected void setMaxInclusive (String value);
    abstract protected void setMinInclusive (String value);
    abstract protected void setMaxExclusive (String value);
    abstract protected void setMinExclusive (String value);    
    abstract protected void setEnumeration (Vector enumeration) 
    throws InvalidDatatypeValueException;

    //
    // get* functions used to output error messages
    //
    abstract protected String getMaxInclusive (boolean isBase);
    abstract protected String getMinInclusive (boolean isBase);
    abstract protected String getMaxExclusive (boolean isBase);
    abstract protected String getMinExclusive (boolean isBase);

    //
    // date/times need to initialize structure objects
    //
    protected void initializeValues() {
    }

    //
    // decimal has fractionDigits and totalDigits facets
    // all other datatypes will throw InvalidDatatypeFacetException
    //
    abstract protected void assignAdditionalFacets(String key, Hashtable facets) 
    throws InvalidDatatypeFacetException;

    //
    // decimal needs to inherit totalDigits and fractionDigits
    //
    protected void inheritAdditionalFacets() {
    }

    //
    // decimal needs to check constraints on totalDigits and fractionDigits
    // check is done against fBaseValidator
    //
    protected void checkBaseFacetConstraints() throws InvalidDatatypeFacetException {}

    //
    // decimal needs to check constraints on totalDigits and fractionDigits
    //
    protected void checkFacetConstraints() throws InvalidDatatypeFacetException {}

}
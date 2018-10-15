package org.apache.xerces.impl.dv.xs;

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 2001 The Apache Software Foundation.  All rights
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

package org.apache.xerces.impl.dv.xs_new;

import org.apache.xerces.impl.dv.InvalidDatatypeValueException;
import org.apache.xerces.impl.validation.ValidationContext;
import java.math.BigDecimal;

/**
 * Represent the schema type "decimal"
 *
 * @author Neeraj Bajaj, Sun Microsystems, inc.
 * @author Sandy Gao, IBM
 *
 * @version $Id$
 */
public class DecimalDV extends TypeValidator {

    public short getAllowedFacets(){
        return ( XSSimpleTypeDecl.FACET_PATTERN | XSSimpleTypeDecl.FACET_WHITESPACE | XSSimpleTypeDecl.FACET_ENUMERATION |XSSimpleTypeDecl.FACET_MAXINCLUSIVE |XSSimpleTypeDecl.FACET_MININCLUSIVE | XSSimpleTypeDecl.FACET_MAXEXCLUSIVE  | XSSimpleTypeDecl.FACET_MINEXCLUSIVE | XSSimpleTypeDecl.FACET_TOTALDIGITS | XSSimpleTypeDecl.FACET_FRACTIONDIGITS);
    }

    public Object getActualValue(String content, ValidationContext context) throws InvalidDatatypeValueException {
        try {
            return new BigDecimal( stripPlusIfPresent( content));
        } catch (Exception nfe) {
            throw new InvalidDatatypeValueException("cvc-datatype-valid.1.2.1", new Object[]{content, "decimal"});
        }
    } //getActualValue()

    public boolean isEqual(Object value1, Object value2) {
        if (!(value1 instanceof BigDecimal) || !(value2 instanceof BigDecimal))
            return false;
        return ((BigDecimal)value1).compareTo((BigDecimal)value2) == 0;
    }

    public int compare(Object value1, Object value2){
        return ((BigDecimal)value1).compareTo((BigDecimal)value2);
    }

    public int getTotalDigits(Object value){
        return ((BigDecimal)value).movePointRight(((BigDecimal)value).scale()).toString().length() -
                ((((BigDecimal)value).signum() < 0) ? 1 : 0); // account for minus sign
    }

    public int getFractionDigits(Object value){
        return ((BigDecimal)value).scale();
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
    static private String stripPlusIfPresent(String value) {
        String strippedPlus = value;

        if (value.length() >= 2 && value.charAt(0) == '+' && value.charAt(1) != '-') {
            strippedPlus = value.substring(1);
        }
        return strippedPlus;
    }//getStripPlusIfPresent()

} // class DecimalDV
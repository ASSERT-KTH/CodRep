import org.apache.xerces.impl.dv.ValidationContext;

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 2001, 2002 The Apache Software Foundation.  All rights
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

package org.apache.xerces.impl.dv.xs;

import org.apache.xerces.impl.dv.InvalidDatatypeValueException;
import org.apache.xerces.impl.validation.ValidationContext;
import java.math.BigDecimal;
import java.math.BigInteger;

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

        int len = content.length();
        if (len == 0)
            throw new InvalidDatatypeValueException("cvc-datatype-valid.1.2.1", new Object[]{content, "decimal"});
        
        // these 4 variables are used to indicate where the integre/fraction
        // parts start/end.
        int intStart = 0, intEnd = 0, fracStart = 0, fracEnd = 0;

        // Deal with leading sign symbol if present
        if (content.charAt(0) == '+') {
            // skip '+', so intStart should be 1
            intStart = intEnd = 1;
        }
        else if (content.charAt(0) == '-') {
            // keep '-', so intStart is stil 0
            intEnd = 1;
        }

        // Find the ending position of the integer part
        while (intEnd < len && isDigit(content.charAt(intEnd)))
            intEnd++;
        
        // Not reached the end yet
        if (intEnd < len) {
            // the remaining part is not ".DDD", error
            if (content.charAt(intEnd) != '.')
                throw new InvalidDatatypeValueException("cvc-datatype-valid.1.2.1", new Object[]{content, "decimal"});

            // fraction part starts after '.', and ends at the end of the input
            fracStart = intEnd + 1;
            fracEnd = len;
        }
        
        // no integer part, no fraction part, error.
        if (intStart == intEnd && fracStart == fracEnd)
            throw new InvalidDatatypeValueException("cvc-datatype-valid.1.2.1", new Object[]{content, "decimal"});

        // count leading zeroes in integer part
        int actualIntStart = content.charAt(intStart) == '-' ? intStart + 1 : intStart;
        while (actualIntStart < intEnd && content.charAt(actualIntStart) == '0') {
            actualIntStart++;
        }
        
        // ignore trailing zeroes in fraction part
        while (fracEnd > fracStart && content.charAt(fracEnd-1) == '0') {
            fracEnd--;
        }
        
        // check whether there is non-digit characters in the fraction part
        for (int fracPos = fracStart; fracPos < fracEnd; fracPos++) {
            if (!isDigit(content.charAt(fracPos)))
                throw new InvalidDatatypeValueException("cvc-datatype-valid.1.2.1", new Object[]{content, "decimal"});
        }
        
        int fracNum = fracEnd - fracStart;
        
        // concatenate the two parts to one integer string
        String intString = null;
        if (intEnd > intStart) {
            intString = content.substring(intStart, intEnd);
            if (fracNum > 0)
                intString += content.substring(fracStart, fracEnd);
        }
        else {
            if (fracNum > 0)
                intString = content.substring(fracStart, fracEnd);
            else
                // ".00", treat it as "0"
                intString = "0";
        }
        
        try {
            // create a BigInteger using the integer string
            BigInteger intVal = new BigInteger(intString);
            // carete a MyDecimal using the BigInteger and scale
            return new XDecimal(intVal, intEnd - actualIntStart, fracNum);
        } catch (Exception nfe) {
            throw new InvalidDatatypeValueException("cvc-datatype-valid.1.2.1", new Object[]{content, "decimal"});
        }
    }

    public boolean isEqual(Object value1, Object value2) {
        if (!(value1 instanceof BigDecimal) || !(value2 instanceof BigDecimal))
            return false;
        return ((BigDecimal)value1).compareTo((BigDecimal)value2) == 0;
    }

    public int compare(Object value1, Object value2){
        return ((BigDecimal)value1).compareTo((BigDecimal)value2);
    }

    public int getTotalDigits(Object value){
        return ((XDecimal)value).totalDigits;
    }

    public int getFractionDigits(Object value){
        return ((BigDecimal)value).scale();
    }
    
} // class DecimalDV

// store total digits in this class
class XDecimal extends java.math.BigDecimal {
    int totalDigits = 0;
    XDecimal(BigInteger intVal, int intNum, int fracNum) {
        super(intVal, fracNum);
        // the canonical form of decimal requires at least one digit
        // on both sides of the decimal point
        totalDigits = (intNum == 0 ? 1 : intNum) + fracNum;
    }
}
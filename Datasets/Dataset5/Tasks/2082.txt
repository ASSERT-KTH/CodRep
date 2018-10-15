package org.apache.xerces.impl.dv.xs;

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
 * originally based on software copyright (c) 2001, International
 * Business Machines, Inc., http://www.apache.org.  For more
 * information on the Apache Software Foundation, please see
 * <http://www.apache.org/>.
 */

package org.apache.xerces.impl.dv.xs_new;

import org.apache.xerces.impl.dv.InvalidDatatypeValueException;
import org.apache.xerces.impl.validation.ValidationContext;

/**
 * Validator for <gMonth> datatype (W3C Schema Datatypes)
 *
 * @author Elena Litani
 * @author Gopal Sharma, SUN Microsystem Inc.
 *
 * @version $Id$
 */

public class MonthDV extends AbstractDateTimeDV {

    /**
     * Convert a string to a compiled form
     *
     * @param  content The lexical representation of gMonth
     * @return a valid and normalized gMonth object
     */
    public Object getActualValue(String content, ValidationContext context) throws InvalidDatatypeValueException{
        try{
            return parse(content, null);
        } catch(Exception ex){
            throw new InvalidDatatypeValueException("cvc-datatype-valid.1.2.1", new Object[]{content, "gMonth"});
        }
    }

    /**
     * Parses, validates and computes normalized version of gMonth object
     *
     * @param str    The lexical representation of gMonth object --MM--
     *               with possible time zone Z or (-),(+)hh:mm
     * @param date   uninitialized date object
     * @return normalized date representation
     * @exception Exception Invalid lexical representation
     */
    protected int[] parse(String str, int[] date) throws SchemaDateTimeException{

        //REVISIT: change --MM-- to --MM
        resetBuffer(str);

        //create structure to hold an object
        if ( date== null ) {
            date=new int[TOTAL_SIZE];
        }
        resetDateObj(date);

        //set constants
        date[CY]=YEAR;
        date[D]=DAY;
        if (fBuffer.charAt(0)!='-' || fBuffer.charAt(1)!='-') {
            throw new SchemaDateTimeException("Invalid format for gMonth: "+str);
        }
        int stop = fStart +4;
        date[M]=parseInt(fStart+2,stop);

        if (fBuffer.charAt(stop++)!='-' || fBuffer.charAt(stop)!='-') {
            throw new SchemaDateTimeException("Invalid format for gMonth: "+str);
        }
        if ( MONTH_SIZE<fEnd ) {
            int sign = findUTCSign(MONTH_SIZE, fEnd);
            if ( sign<0 ) {
                throw new SchemaDateTimeException ("Error in month parsing: "+str);
            }
            else {
                getTimeZone(date, sign);
            }
        }
        //validate and normalize
        validateDateTime(date);

        if ( date[utc]!=0 && date[utc]!='Z' ) {
            normalize(date);
        }
        return date;
    }

    /**
     * Overwrite compare algorithm to optimize month comparison
     *
     * REVISIT: this one is lack of the third parameter: boolean strict, so it
     *          doesn't override the method in the base. But maybe this method
     *          is not correctly implemented, and I did encounter errors when
     *          trying to add the extra parameter. I'm leaving it as is. -SG
     *
     * @param date1
     * @param date2
     * @return
     */
    protected  short compareDates(int[] date1, int[] date2) {

        if ( date1[utc]==date2[utc] ) {
            return (short)((date1[M]>=date2[M])?(date1[M]>date2[M])?1:0:-1);
        }

        if ( date1[utc]=='Z' || date2[utc]=='Z' ) {

            if ( date1[M]==date2[M] ) {
                //--05--Z and --05--
                return INDETERMINATE;
            }
            if ( (date1[M]+1 == date2[M] || date1[M]-1 == date2[M]) ) {
                //--05--Z and (--04-- or --05--)
                //REVISIT: should this case be less than or equal?
                //         maxExclusive should fail but what about maxInclusive
                //
                return INDETERMINATE;
            }
        }

        if ( date1[M]<date2[M] ) {
            return -1;
        }
        else {
            return 1;
        }

    }

    /**
     * Converts month object representation to String
     *
     * @param date   month object
     * @return lexical representation of month: --MM-- with an optional time zone sign
     */
    protected String dateToString(int[] date) {

        message.setLength(0);
        message.append('-');
        message.append('-');
        message.append(date[M]);
        message.append('-');
        message.append('-');
        message.append((char)date[utc]);
        return message.toString();
    }

}
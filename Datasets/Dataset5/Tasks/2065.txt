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

/**
 * This is the base class of all date/time datatype validators.
 * It implements common code for parsing, validating and comparing datatypes.
 * Classes that extend this class, must implement parse() method.
 *
 * REVISIT: There are many instance variables, which would cause problems
 *          when we support grammar caching. A grammar is possibly used by
 *          two parser instances at the same time, then the same simple type
 *          decl object can be used to validate two strings at the same time.
 *          -SG
 *
 * @author Elena Litani
 * @author Len Berman
 * @author Gopal Sharma, SUN Microsystems Inc.
 *
 * @version $Id$
 */
public abstract class AbstractDateTimeDV extends TypeValidator {

    //debugging
    private static final boolean DEBUG=false;

    //define shared variables for date/time

    //define constants
    protected final static int CY = 0,  M = 1, D = 2, h = 3,
    m = 4, s = 5, ms = 6, utc=7, hh=0, mm=1;

    //size for all objects must have the same fields:
    //CCYY, MM, DD, h, m, s, ms + timeZone
    protected final static int TOTAL_SIZE = 8;

    //date obj size for gMonth datatype (without time zone): --09--
    protected final static int MONTH_SIZE = 6;

    //date obj must have at least 6 chars after year (without time zone): "-MM-DD"
    private final static int YEARMONTH_SIZE = 7;

    //define constants to be used in assigning default values for
    //all date/time excluding duration
    protected final static int YEAR=2001;
    protected final static int MONTH=01;
    protected final static int DAY = 15;

    //obj to store timeZone for date/time object excluding duration
    protected int[] timeZone;

    //size of enumeration if any
    protected int  fEnumSize;

    //size of string buffer
    protected int fEnd;
    protected int fStart;

    //storage for string value of date/time object
    protected StringBuffer fBuffer;

    //obj to store all date/time objects with fields:
    // {CY, M, D, h, m, s, ms, utc}
    protected int[] fDateValue;
    private int[] fTempDate;

    //error message buffer
    protected StringBuffer message;

    public AbstractDateTimeDV(){
        initializeValues();
    }

    protected void initializeValues(){
        fDateValue = new int[TOTAL_SIZE];
        fTempDate = new int[TOTAL_SIZE];
        fEnd = 30;
        fStart = 0;
        message = new StringBuffer(TOTAL_SIZE);
        fBuffer = new StringBuffer(fEnd);
        timeZone = new int[2];
    }

    public short getAllowedFacets(){
        return ( XSSimpleTypeDecl.FACET_PATTERN | XSSimpleTypeDecl.FACET_WHITESPACE | XSSimpleTypeDecl.FACET_ENUMERATION |XSSimpleTypeDecl.FACET_MAXINCLUSIVE |XSSimpleTypeDecl.FACET_MININCLUSIVE | XSSimpleTypeDecl.FACET_MAXEXCLUSIVE  | XSSimpleTypeDecl.FACET_MINEXCLUSIVE  );
    }//getAllowedFacets()


    // the parameters are in compiled form (from getActualValue)
    public boolean isEqual(Object value1, Object value2){
        if (!(value1 instanceof int[]) || !(value2 instanceof int[]))
            return false;
        return compareDates((int[])value1,(int[])value2, true)==0;
    }//IsEqual()

    // the parameters are in compiled form (from getActualValue)
    public int compare (Object value1, Object value2) {
        return compareDates((int[])value1, (int[])value2, true);
    }//compare()

    /**
     * Implemented by each subtype, calling appropriate function to parse
     * given date/time
     *
     * @param content String value of the date/time
     * @param date    Storage to represent date/time object.
     *                If null - new object will be created, otherwise
     *                date will be reset and reused
     * @return updated date/time object
     * @exception Exception
     */
     abstract protected int[] parse (String content, int[] date) throws SchemaDateTimeException;

     /**
     * Compare algorithm described in dateDime (3.2.7).
     * Duration datatype overwrites this method
     *
     * @param date1  normalized date representation of the first value
     * @param date2  normalized date representation of the second value
     * @param strict
     * @return less, greater, less_equal, greater_equal, equal
     */
    protected short compareDates(int[] date1, int[] date2, boolean strict) {
        if ( date1[utc]==date2[utc] ) {
            return compareOrder(date1, date2);
        }
        short c1, c2;

        if ( date1[utc]=='Z' ) {

            //compare date1<=date1<=(date2 with time zone -14)
            //
            cloneDate(date2); //clones date1 value to global temporary storage: fTempDate
            timeZone[hh]=14;
            timeZone[mm]=0;
            fTempDate[utc]='+';
            normalize(fTempDate);
            c1 = compareOrder(date1, fTempDate);

            //compare date1>=(date2 with time zone +14)
            //
            cloneDate(date2); //clones date1 value to global temporary storage: fTempDate
            timeZone[hh]=14;
            timeZone[mm]=0;
            fTempDate[utc]='-';
            normalize(fTempDate);
            c2 = compareOrder(date1, fTempDate);

            if ( (c1 < 0 && c2 > 0) ||
                 (c1 == 0 && c2 == 0) ) {
                return INDETERMINATE;
            }
            //REVISIT: wait for clarification on this case from schema
            return(c1!=INDETERMINATE)?c1:c2;
        }
        else if ( date2[utc]=='Z' ) {

            //compare (date1 with time zone -14)<=date2
            //
            cloneDate(date1); //clones date1 value to global temporary storage: fTempDate
            timeZone[hh]=14;
            timeZone[mm]=0;

            fTempDate[utc]='-';
            if (DEBUG) {
               System.out.println("fTempDate=" + dateToString(fTempDate));
            }
            normalize(fTempDate);
            c1 = compareOrder(fTempDate, date2);
            if (DEBUG) {
                System.out.println("date=" + dateToString(date2));
                System.out.println("fTempDate=" + dateToString(fTempDate));
            }
            //compare (date1 with time zone +14)<=date2
            //
            cloneDate(date1); //clones date1 value to global temporary storage: fTempDate
            timeZone[hh]=14;
            timeZone[mm]=0;
            fTempDate[utc]='+';
            normalize(fTempDate);
            c2 = compareOrder(fTempDate, date2);
            if (DEBUG) {
               System.out.println("fTempDate=" + dateToString(fTempDate));
            }
            if ( (c1 < 0 && c2 > 0) ||
                 (c1 == 0 && c2 == 0) ) {
                return INDETERMINATE;
            }
            //REVISIT: wait for clarification on this case from schema
            return(c1!=INDETERMINATE)?c1:c2;
        }
        return INDETERMINATE;

    }

    /**
     * Given normalized values, determines order-relation
     * between give date/time objects.
     *
     * @param date1  date/time object
     * @param date2  date/time object
     * @return
     */
    protected short compareOrder (int[] date1, int[] date2) {

        for ( int i=0;i<TOTAL_SIZE;i++ ) {
            if ( date1[i]<date2[i] ) {
                return -1;
            }
            else if ( date1[i]>date2[i] ) {
                return 1;
            }
        }
        return 0;
    }

    /**
     * Parses time hh:mm:ss.sss and time zone if any
     *
     * @param start
     * @param end
     * @param data
     * @return
     * @exception Exception
     */
    protected  void getTime (int start, int end, int[] data) throws RuntimeException{

        int stop = start+2;

        //get hours (hh)
        data[h]=parseInt(start,stop);

        //get minutes (mm)

        if (fBuffer.charAt(stop++)!=':') {
                throw new RuntimeException("Error in parsing time zone" );
        }
        start = stop;
        stop = stop+2;
        data[m]=parseInt(start,stop);

        //get seconds (ss)
        if (fBuffer.charAt(stop++)!=':') {
                throw new RuntimeException("Error in parsing time zone" );
        }
        start = stop;
        stop = stop+2;
        data[s]=parseInt(start,stop);

        //get miliseconds (ms)
        int milisec = indexOf(start, end, '.');

        //find UTC sign if any
        int sign = findUTCSign((milisec!=-1)?milisec:start, end);

        //parse miliseconds
        if ( milisec != -1 ) {

            if ( sign<0 ) {

                //get all digits after "."
                data[ms]=parseInt(milisec+1,fEnd);
            }
            else {

                //get ms before UTC sign
                data[ms]=parseInt(milisec+1,sign);
            }

        }

        //parse UTC time zone (hh:mm)
        if ( sign>0 ) {
            getTimeZone(data,sign);
        }
    }

    /**
     * Parses date CCYY-MM-DD
     *
     * @param start
     * @param end
     * @param data
     * @return
     * @exception Exception
     */
    protected void getDate (int start, int end, int[] date) throws RuntimeException{

        getYearMonth(start, end, date);

        if (fBuffer.charAt(fStart++) !='-') {
            throw new RuntimeException("CCYY-MM must be followed by '-' sign");
        }
        int stop = fStart + 2;
        date[D]=parseInt(fStart, stop);
        fStart = stop;  //fStart points right after the Day
    }

    /**
     * Parses date CCYY-MM
     *
     * @param start
     * @param end
     * @param data
     * @return
     * @exception Exception
     */
    protected void getYearMonth (int start, int end, int[] date) throws RuntimeException{

        if ( fBuffer.charAt(0)=='-' ) {
            // REVISIT: date starts with preceding '-' sign
            //          do we have to do anything with it?
            //
            start++;
        }
        int i = indexOf(start, end, '-');
        if ( i==-1 ) throw new RuntimeException("Year separator is missing or misplaced");
        int length = i-start;
        if (length<4) {
            throw new RuntimeException("Year must have 'CCYY' format");
        }
        else if (length > 4 && fBuffer.charAt(start)=='0'){
            throw new RuntimeException("Leading zeros are required if the year value would otherwise have fewer than four digits; otherwise they are forbidden");
        }
        date[CY]= parseIntYear(i);
        if (fBuffer.charAt(i)!='-') {
            throw new RuntimeException("CCYY must be followed by '-' sign");
        }
        start = ++i;
        i = start +2;
        date[M]=parseInt(start, i);
        fStart = i; //fStart points right after the MONTH
    }

    /**
     * Shared code from Date and YearMonth datatypes.
     * Finds if time zone sign is present
     *
     * @param end
     * @param date
     * @return
     * @exception Exception
     */
    protected void parseTimeZone (int end, int[] date) throws RuntimeException{

        //fStart points right after the date

        if ( fStart<fEnd ) {
            int sign = findUTCSign(fStart, fEnd);
            if ( sign<0 ) {
                throw new RuntimeException ("Error in month parsing");
            }
            else {
                getTimeZone(date, sign);
            }
        }
    }

    /**
     * Parses time zone: 'Z' or {+,-} followed by  hh:mm
     *
     * @param data
     * @param sign
     * @return
     */
    protected void getTimeZone (int[] data, int sign) throws RuntimeException{
        data[utc]=fBuffer.charAt(sign);

        if ( fBuffer.charAt(sign) == 'Z' ) {
            if (fEnd>(++sign)) {
                throw new RuntimeException("Error in parsing time zone");
            }
            return;
        }
        if ( sign<=(fEnd-6) ) {

            //parse [hh]
            int stop = ++sign+2;
            timeZone[hh]=parseInt(sign, stop);
            if (fBuffer.charAt(stop++)!=':') {
                throw new RuntimeException("Error in parsing time zone" );
            }

            //parse [ss]
            timeZone[mm]=parseInt(stop, stop+2);

            if ( stop+2!=fEnd ) {
                throw new RuntimeException("Error in parsing time zone");
            }

        }
        else {
            throw new RuntimeException("Error in parsing time zone");
        }
        if ( DEBUG ) {
            System.out.println("time[hh]="+timeZone[hh] + " time[mm]=" +timeZone[mm]);
        }
    }

    /**
     * Computes index of given char within StringBuffer
     *
     * @param start
     * @param end
     * @param ch     character to look for in StringBuffer
     * @return index of ch within StringBuffer
     */
    protected  int indexOf (int start, int end, char ch) {
        for ( int i=start;i<end;i++ ) {
            if ( fBuffer.charAt(i) == ch ) {
                return i;
            }
        }
        return -1;
    }

    /**
     * Validates given date/time object accoring to W3C PR Schema
     * [D.1 ISO 8601 Conventions]
     *
     * @param data
     * @return
     */
    protected void validateDateTime (int[]  data) {

        //REVISIT: should we throw an exception for not valid dates
        //          or reporting an error message should be sufficient?
        if ( data[CY]==0 ) {
            throw new RuntimeException("The year \"0000\" is an illegal year value");

        }

        if ( data[M]<1 || data[M]>12 ) {
            throw new RuntimeException("The month must have values 1 to 12");

        }

        //validate days
        if ( data[D]>maxDayInMonthFor(data[CY], data[M]) || data[D]<1 ) {
            throw new RuntimeException("The day must have values 1 to 31");
        }

        //validate hours
        if ( data[h]>23 || data[h]<0 ) {
            throw new RuntimeException("Hour must have values 0-23");
        }

        //validate
        if ( data[m]>59 || data[m]<0 ) {
            throw new RuntimeException("Minute must have values 0-59");
        }

        //validate
        if ( data[s]>60 || data[s]<0 ) {
            throw new RuntimeException("Second must have values 0-60");

        }

        //validate
        if ( timeZone[hh]>14 || timeZone[hh]<-14 ) {
            throw new RuntimeException("Time zone should have range -14..+14");
        }

        //validate
        if ( timeZone[mm]>59 || timeZone[mm]<-59 ) {
            throw new RuntimeException("Minute must have values 0-59");
        }
    }

    /**
     * Return index of UTC char: 'Z', '+', '-'
     *
     * @param start
     * @param end
     * @return
     */
    protected int findUTCSign (int start, int end) {
        int c;
        for ( int i=start;i<end;i++ ) {
            c=fBuffer.charAt(i);
            if ( c == 'Z' || c=='+' || c=='-' ) {
                return i;
            }

        }
        return -1;
    }

    /**
     * Given start and end position, parses string value
     *
     * @param value  string to parse
     * @param start  Start position
     * @param end    end position
     * @return  return integer representation of characters
     */
    protected  int parseInt (int start, int end)
    throws NumberFormatException{
        //REVISIT: more testing on this parsing needs to be done.
        int radix=10;
        int result = 0;
        int digit=0;
        int limit = -Integer.MAX_VALUE;
        int multmin = limit / radix;
        int i = start;
        do {
            digit = Character.digit(fBuffer.charAt(i),radix);
            if ( digit < 0 ) throw new NumberFormatException("'"+fBuffer.toString()+"' has wrong format");
            if ( result < multmin ) throw new NumberFormatException("'"+fBuffer.toString()+"' has wrong format");
            result *= radix;
            if ( result < limit + digit ) throw new NumberFormatException("'"+fBuffer.toString()+"' has wrong format");
            result -= digit;

        }while ( ++i < end );
        return -result;
    }

    // parse Year differently to support negative value.
    protected int parseIntYear (int end){
        int radix=10;
        int result = 0;
        boolean negative = false;
        int i=0;
        int limit;
        int multmin;
        int digit=0;

        if (fBuffer.charAt(0) == '-'){
            negative = true;
            limit = Integer.MIN_VALUE;
            i++;

        }
        else{
            limit = -Integer.MAX_VALUE;
        }
        multmin = limit / radix;
        while (i < end)
        {
            digit = Character.digit(fBuffer.charAt(i++),radix);
            if (digit < 0) throw new NumberFormatException("'"+fBuffer.toString()+"' has wrong format");
            if (result < multmin) throw new NumberFormatException("'"+fBuffer.toString()+"' has wrong format");
            result *= radix;
            if (result < limit + digit) throw new NumberFormatException("'"+fBuffer.toString()+"' has wrong format");
            result -= digit;
        }

        if (negative)
        {
            if (i > 1) return result;
            else throw new NumberFormatException("'"+fBuffer.toString()+"' has wrong format");
        }
        return -result;

    }

    /**
     * If timezone present - normalize dateTime  [E Adding durations to dateTimes]
     *
     * @param date   CCYY-MM-DDThh:mm:ss+03
     * @return CCYY-MM-DDThh:mm:ssZ
     */
    protected  void normalize (int[] date) {

        // REVISIT: we have common code in addDuration() for durations
        //          should consider reorganizing it.
        //

        //add minutes (from time zone)
        int negate = 1;
        if (date[utc]=='+') {
            negate = -1;
        }
        if ( DEBUG ) {
            System.out.println("==>date[m]"+date[m]);
            System.out.println("==>timeZone[mm]" +timeZone[mm]);
        }
        int temp = date[m] + negate*timeZone[mm];
        int carry = fQuotient (temp, 60);
        date[m]= mod(temp, 60, carry);

        if ( DEBUG ) {
            System.out.println("==>carry: " + carry);
        }
        //add hours
        temp = date[h] + negate*timeZone[hh] + carry;
        carry = fQuotient(temp, 24);
        date[h]=mod(temp, 24, carry);
        if ( DEBUG ) {
            System.out.println("==>date[h]"+date[h]);
            System.out.println("==>carry: " + carry);
        }

        date[D]=date[D]+carry;

        while ( true ) {
            temp=maxDayInMonthFor(date[CY], date[M]);
            if (date[D]<1) {
                date[D] = date[D] + maxDayInMonthFor(date[CY], date[M]-1);
                carry=-1;
            }
            else if ( date[D]>temp ) {
                date[D]=date[D]-temp;
                carry=1;
            }
            else {
                break;
            }
            temp=date[M]+carry;
            date[M]=modulo(temp, 1, 13);
            date[CY]=date[CY]+fQuotient(temp, 1, 13);
        }
        date[utc]='Z';
    }


    /**
     * Resets fBuffer to store string representation of
     * date/time
     *
     * @param str    Lexical representation of date/time
     */
    protected void resetBuffer (String str) {
        fBuffer.setLength(0);
        fStart=fEnd=0;
        timeZone[hh]=timeZone[mm]=0;
        fBuffer.append(str);
        fEnd = fBuffer.length();

    }

    /**
     * Resets object representation of date/time
     *
     * @param data   date/time object
     */
    protected void resetDateObj (int[] data) {
        for ( int i=0;i<TOTAL_SIZE;i++ ) {
            data[i]=0;
        }
    }

    /**
     * Given {year,month} computes maximum
     * number of days for given month
     *
     * @param year
     * @param month
     * @return
     */
    protected int maxDayInMonthFor(int year, int month) {
        //validate days
        if ( month==4 || month==6 || month==9 || month==11 ) {
            return 30;
        }
        else if ( month==2 ) {
            if ( isLeapYear(year) ) {
                return 29;
            }
            else {
                return 28;
            }
        }
        else {
            return 31;
        }
    }

    private boolean isLeapYear(int year) {

        //REVISIT: should we take care about Julian calendar?
        return((year%4 == 0) && ((year%100 != 0) || (year%400 == 0)));
    }

    //
    // help function described in W3C PR Schema [E Adding durations to dateTimes]
    //
    protected int mod (int a, int b, int quotient) {
        //modulo(a, b) = a - fQuotient(a,b)*b
        return (a - quotient*b) ;
    }

    //
    // help function described in W3C PR Schema [E Adding durations to dateTimes]
    //
    protected int fQuotient (int a, int b) {

        //fQuotient(a, b) = the greatest integer less than or equal to a/b
        return (int)Math.floor((float)a/b);
    }

    //
    // help function described in W3C PR Schema [E Adding durations to dateTimes]
    //
    protected int modulo (int temp, int low, int high) {
        //modulo(a - low, high - low) + low
        int a = temp - low;
        int b = high - low;
        return (mod (a, b, fQuotient(a, b)) + low) ;
    }

    //
    // help function described in W3C PR Schema [E Adding durations to dateTimes]
    //
    protected int fQuotient (int temp, int low, int high) {
        //fQuotient(a - low, high - low)

        return fQuotient(temp - low, high - low);
    }


    protected String dateToString(int[] date) {
        message.setLength(0);
        message.append(date[CY]);
        message.append('-');
        message.append(date[M]);
        message.append('-');
        message.append(date[D]);
        message.append('T');
        message.append(date[h]);
        message.append(':');
        message.append(date[m]);
        message.append(':');
        message.append(date[s]);
        message.append('.');
        message.append(date[ms]);
        message.append((char)date[utc]);
        return message.toString();
    }


    /**
     * Use this function to report errors in constructor
     *
     * @param msg
     * @param value
     */
    protected void reportError(String msg, String value) {
        System.err.println("[Error]: " +msg+": Value  '"+value+"' is not legal for current datatype");
    }


    //
    //Private help functions
    //

    private void cloneDate (int[] finalValue) {
        resetDateObj(fTempDate);
        for ( int i=0;i<TOTAL_SIZE;i++ ) {
            fTempDate[i]=finalValue[i];
        }
    }

}
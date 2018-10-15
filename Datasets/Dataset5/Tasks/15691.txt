DateTimeData date = new DateTimeData(str, this);

/*
 * Copyright 1999-2002,2004 The Apache Software Foundation.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package org.apache.xerces.impl.dv.xs;

import org.apache.xerces.impl.dv.InvalidDatatypeValueException;
import org.apache.xerces.impl.dv.ValidationContext;

/**
 * Validator for &lt;time&gt; datatype (W3C Schema Datatypes)
 * 
 * @xerces.internal 
 *
 * @author Elena Litani
 * @author Gopal Sharma, SUN Microsystem Inc.
 *
 * @version $Id$
 */
public class TimeDV extends AbstractDateTimeDV {

    /**
     * Convert a string to a compiled form
     *
     * @param  content The lexical representation of time
     * @return a valid and normalized time object
     */
    public Object getActualValue(String content, ValidationContext context) throws InvalidDatatypeValueException{
        try{
            return parse(content);
        } catch(Exception ex){
            throw new InvalidDatatypeValueException("cvc-datatype-valid.1.2.1", new Object[]{content, "time"});
        }
    }

    /**
     * Parses, validates and computes normalized version of time object
     *
     * @param str    The lexical representation of time object hh:mm:ss.sss
     *               with possible time zone Z or (-),(+)hh:mm
     *               Pattern: "(\\d\\d):(\\d\\d):(\\d\\d)(\\.(\\d)*)?(Z|(([-+])(\\d\\d)(:(\\d\\d))?))?")
     * @return normalized time representation
     * @exception SchemaDateTimeException Invalid lexical representation
     */
    protected DateTimeData parse(String str) throws SchemaDateTimeException{
        DateTimeData date = new DateTimeData(this);
        int len = str.length();

        // time
        // initialize to default values
        date.year=YEAR;
        date.month=MONTH;
        date.day=15;
        getTime(str, 0, len, date);

        //validate and normalize

        validateDateTime(date);

        if ( date.utc!=0 ) {
            normalize(date);
        }
        date.position = 2;
        return date;
    }

    /**
     * Converts time object representation to String
     *
     * @param date   time object
     * @return lexical representation of time: hh:mm:ss.sss with an optional time zone sign
     */
    protected String dateToString(DateTimeData date) {
        StringBuffer message = new StringBuffer(16);
        append(message, date.hour, 2);
        message.append(':');
        append(message, date.minute, 2);
        message.append(':');
        append(message, date.second);

        append(message, (char)date.utc, 0);
        return message.toString();
    }

	/* (non-Javadoc)
	 * @see org.apache.xerces.impl.dv.xs.AbstractDateTimeDV#compareOrder2(org.apache.xerces.impl.dv.xs.AbstractDateTimeDV.DateTimeData, org.apache.xerces.impl.dv.xs.AbstractDateTimeDV.DateTimeData)
	 */
	protected short compareOrder2(DateTimeData date1, DateTimeData date2) {
        if (date1.hour < date2.hour)
            return -1;
        if (date1.hour > date2.hour)
            return 1;
        if (date1.minute < date2.minute)
            return -1;
        if (date1.minute > date2.minute)
            return 1;
        if (date1.second < date2.second)
            return -1;
        if (date1.second > date2.second)
            return 1;
        return 0;
	}

}
new Object [] { new Long(f),"","","",""}));//Revisit

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
import java.util.Locale;
import java.util.Calendar;
import java.util.GregorianCalendar;
import java.text.ParseException;
import org.apache.xerces.utils.regex.RegularExpression;
import org.apache.xerces.validators.schema.SchemaSymbols;

/**
 *
 *
 *
 * @author Ted Leung, George Joseph, Jeffrey Rodriguez,  
 * @version $Id$
 */

public class RecurringDurationDatatypeValidator extends AbstractDatatypeValidator {

    private static final boolean   fDbug        = false;
    private Locale    fLocale           = null;
    DatatypeValidator fBaseValidator    = null; // A Native datatype is null
    String            fPattern          = null;
    long              fMaxInclusive     = Long.MAX_VALUE;
    long              fMaxExclusive     = Long.MAX_VALUE-1;
    long              fMinInclusive     = 1L;
    long              fMinExclusive     = 0L;
    long              fDuration         = 0L;
    long              fPeriod           = 0L;
    long[]            fEnumrecurringduration = null; // Time duration is represented internally as longs
    boolean           isMaxExclusiveDefined = false;
    boolean           isMaxInclusiveDefined = false;
    boolean           isMinExclusiveDefined = false;
    boolean           isMinInclusiveDefined = false;
    boolean           isBaseTypeTimePeriod  = false;
    int               fFacetsDefined        = 0;
    boolean           fDerivedByList        = false;
    Hashtable         fFacets        = null;



    private DatatypeMessageProvider fMessageProvider = new DatatypeMessageProvider();



    public  RecurringDurationDatatypeValidator () throws InvalidDatatypeFacetException {
        this( null, null, false ); // Native, No Facets defined, Restriction
    }

    public  RecurringDurationDatatypeValidator ( DatatypeValidator base, Hashtable facets, 
                                                 boolean derivedByList ) throws InvalidDatatypeFacetException {

        fDerivedByList = derivedByList;

        if ( base != null )
        {
            setBasetype( base ); // Set base type 
            fFacets = facets;
        }

        // Set Facets if any defined

        if ( facets != null  )  {
            if ( fDerivedByList == false ) { // Restriction

                for (Enumeration e = facets.keys(); e.hasMoreElements();) {

                    String key = (String) e.nextElement();

                    if (key.equals(SchemaSymbols.ELT_PATTERN)) {
                        fFacetsDefined += DatatypeValidator.FACET_PATTERN;
                        fPattern = (String)facets.get(key);
                    } else if (key.equals(SchemaSymbols.ELT_ENUMERATION)) {
                        fFacetsDefined += DatatypeValidator.FACET_ENUMERATION;
                        continue; //Treat the enumeration after this for loop
                    } else if (key.equals(SchemaSymbols.ELT_MAXINCLUSIVE)) {
                        fFacetsDefined += DatatypeValidator.FACET_MAXINCLUSIVE;
                        String value = null;
                        try {
                            value         = ((String)facets.get(key));


                            fMaxInclusive = normalizeRecurringDuration( value.toCharArray(), 0) ;
                        } catch ( InvalidDatatypeValueException nfe ){
                            throw new InvalidDatatypeFacetException( getErrorString(
                                                                                   DatatypeMessageProvider.IllegalFacetValue,
                                                                                   DatatypeMessageProvider.MSG_NONE,
                                                                                   new Object [] { value, key}));
                        }
                    } else if (key.equals(SchemaSymbols.ELT_MAXEXCLUSIVE)) {
                        fFacetsDefined += DatatypeValidator.FACET_MAXEXCLUSIVE;
                        String value = null;
                        try {
                            value         = ((String)facets.get(key));
                            fMaxExclusive = normalizeRecurringDuration( value.toCharArray(), 0 );
                        } catch ( InvalidDatatypeValueException nfe ){
                            throw new InvalidDatatypeFacetException( getErrorString(
                                                                                   DatatypeMessageProvider.IllegalFacetValue,
                                                                                   DatatypeMessageProvider.MSG_NONE,
                                                                                   new Object [] { value, key}));
                        }
                    } else if (key.equals(SchemaSymbols.ELT_MININCLUSIVE)) {
                        fFacetsDefined += DatatypeValidator.FACET_MININCLUSIVE;
                        String value = null;
                        try {
                            value         = ((String)facets.get(key));
                            fMinInclusive = normalizeRecurringDuration( value.toCharArray(), 0 );
                        } catch ( InvalidDatatypeValueException nfe ){
                            throw new InvalidDatatypeFacetException( getErrorString(
                                                                                   DatatypeMessageProvider.IllegalFacetValue,
                                                                                   DatatypeMessageProvider.MSG_NONE,
                                                                                   new Object [] { value, key}));
                        }
                    } else if (key.equals(SchemaSymbols.ELT_MINEXCLUSIVE)) {
                        fFacetsDefined += DatatypeValidator.FACET_MININCLUSIVE;
                        String value = null;
                        try {
                            value         = ((String)facets.get(key));
                            fMinExclusive = normalizeRecurringDuration( value.toCharArray(), 0 ); 
                        } catch ( InvalidDatatypeValueException nfe ) {
                            throw new InvalidDatatypeFacetException( getErrorString(
                                                                                   DatatypeMessageProvider.IllegalFacetValue,
                                                                                   DatatypeMessageProvider.MSG_NONE,
                                                                                   new Object [] { value, key}));
                        }
                    } else if (key.equals(SchemaSymbols.ELT_PERIOD  )) {
                        fFacetsDefined += DatatypeValidator.FACET_PERIOD;
                        String value = null;
                        try {
                            value         = ((String)facets.get(key));
                            fPeriod   = normalizeRecurringDuration( value.toCharArray(), 0 ); 
                            if ( fDbug == true ){
                                System.out.println( "value = " + value );
                                System.out.println("fPeriod = " + fPeriod );
                            }
                        } catch ( InvalidDatatypeValueException nfe ) {
                            throw new InvalidDatatypeFacetException( getErrorString(
                                                                                   DatatypeMessageProvider.IllegalFacetValue,
                                                                                   DatatypeMessageProvider.MSG_NONE,
                                                                                   new Object [] { value, key}));
                        }
                    } else if (key.equals(SchemaSymbols.ELT_DURATION )) {
                        fFacetsDefined += DatatypeValidator.FACET_DURATION;
                        String value = null;
                        try {
                            value         = ((String)facets.get(key));
                            fDuration     = normalizeRecurringDuration( value.toCharArray(), 0 ); 
                            if ( fDbug == true ){
                                System.out.println("fDuration = " + fDuration );
                            }
                        } catch ( InvalidDatatypeValueException nfe ) {
                            throw new InvalidDatatypeFacetException( getErrorString(
                                                                                   DatatypeMessageProvider.IllegalFacetValue,
                                                                                   DatatypeMessageProvider.MSG_NONE,
                                                                                   new Object [] { value, key}));
                        }


                    } else {
                        throw new InvalidDatatypeFacetException( getErrorString(  DatatypeMessageProvider.MSG_FORMAT_FAILURE,
                                                                                  DatatypeMessageProvider.MSG_NONE,
                                                                                  null));
                    }
                }

                isMaxExclusiveDefined = ((fFacetsDefined & 
                                          DatatypeValidator.FACET_MAXEXCLUSIVE ) != 0 )?true:false;
                isMaxInclusiveDefined = ((fFacetsDefined & 
                                          DatatypeValidator.FACET_MAXINCLUSIVE ) != 0 )?true:false;
                isMinExclusiveDefined = ((fFacetsDefined &
                                          DatatypeValidator.FACET_MINEXCLUSIVE ) != 0 )?true:false;
                isMinInclusiveDefined = ((fFacetsDefined &
                                          DatatypeValidator.FACET_MININCLUSIVE ) != 0 )?true:false;


                if ( isMaxExclusiveDefined && isMaxInclusiveDefined ) {
                    throw new InvalidDatatypeFacetException(
                                                           "It is an error for both maxInclusive and maxExclusive to be specified for the same datatype." ); 
                }
                if ( isMinExclusiveDefined && isMinInclusiveDefined ) {
                    throw new InvalidDatatypeFacetException(
                                                           "It is an error for both minInclusive and minExclusive to be specified for the same datatype." ); 
                }

                if ( (fFacetsDefined & DatatypeValidator.FACET_ENUMERATION ) != 0 ) {
                    Vector v = (Vector) facets.get(SchemaSymbols.ELT_ENUMERATION);    
                    if (v != null) {
                        fEnumrecurringduration = new long[v.size()];
                        int     i     = 0;
                        String  value = null;
                        try {
                            for (; i < v.size(); i++){
                                value = (String)v.elementAt(i);
                                fEnumrecurringduration[i] = 
                                normalizeRecurringDuration( value.toCharArray(), 0 );
                                boundsCheck( fEnumrecurringduration[i] ); // Check against max,min Inclusive, Exclusives
                            }
                            if ( fDbug == true ){
                                System.out.println( "The enumeration vectory is " + value );
                                for ( int enumCounter = 0;
                                    enumCounter < this.fEnumrecurringduration.length; enumCounter++ ) {
                                    System.out.println( "fEnumrecurringduration[" + enumCounter + "]" );
                                }
                            }
                        } catch (InvalidDatatypeValueException idve) {
                            throw new InvalidDatatypeFacetException(
                                                                   getErrorString(DatatypeMessageProvider.InvalidEnumValue,
                                                                                  DatatypeMessageProvider.MSG_NONE,
                                                                                  new Object [] { v.elementAt(i)}));
                        }
                    }
                }
            
             if( fBaseValidator != null ) { // Check if basetype of Period id null
                        String value        = null;
                        long   baseTypePeriod;
                        try {
                            Hashtable  baseValidatorFacet = fBaseValidator.getFacets();
                            if( baseValidatorFacet != null ) {
                                 value         = ((String)baseValidatorFacet.get(SchemaSymbols.ELT_PERIOD ));
                                 if( value != null ) {
                                      fPeriod       = normalizeRecurringDuration( value.toCharArray(), 0 ); 
                                      if( fPeriod == 0 ){
                                          isBaseTypeTimePeriod = true;
                                      }
                                      if ( fDbug == true ){
                                          System.out.println( "value = " + value );
                                          System.out.println("fPeriod = " + fPeriod );
                                      }
                                 }
                            }
                        } catch ( InvalidDatatypeValueException nfe ) {
                            throw new InvalidDatatypeFacetException( getErrorString(
                                                                                   DatatypeMessageProvider.IllegalFacetValue,
                                                                                   DatatypeMessageProvider.MSG_NONE,
                                                                                   new Object [] { value, SchemaSymbols.ELT_PERIOD}));
                        }
             }



            } else { //Derived by List TODO 

            }
        }// End Facet definition
    }


    /**
     * validates a String to be a Lexical representation
     * of a recurringduration Datatype.
     * 
     * @param content A string containing the content to be validated
     * @param state
     * @return 
     * @exception InvalidDatatypeValueException
     *                   If String is does not represent a
     *                   valid recurringduration datatype.
     */
    public Object validate(String content, Object state) throws InvalidDatatypeValueException{
        long normalizedValue;

        if ( fDerivedByList == false  ) { //derived by constraint


            if( fDbug == true ) {
                 System.out.println( "Write fFacetsDefined = " + fFacetsDefined );
                 if ( ( fFacetsDefined & DatatypeValidator.FACET_DURATION ) != 0 ){
                     System.out.println( "Duration = " + this.fDuration );
                 }
                 if ( ( fFacetsDefined & DatatypeValidator.FACET_PERIOD ) != 0 ){
                     System.out.println( "Period = " + this.fPeriod );
                 }
                 System.out.println("datatype = " + this.fBaseValidator );
            }



            if ( fPattern != null ) {
                RegularExpression regex = new RegularExpression(fPattern, "X" );
                if ( regex.matches( content) == false )
                    throw new InvalidDatatypeValueException("Value'"+content+
                                                            "does not match regular expression facet" + fPattern );
            }



            //normalizeRecurringDuration(content.toCharArray(), 0 );

            //Calendar cal = normalizeInstant(content.toCharArray(), 0, content.length() ); 

            //System.out.println( "cal = " + cal.toString() );
            //try {
            //boundsCheck( normalizedValue );
            // } catch( InvalidDatatypeFacetException ex ){
            //   throw new InvalidDatatypeValueException( "Boundary error:" );
            //}

            //if ( fEnumrecurringduration != null )
            //  enumCheck( normalizedValue );

        } else { //derived by list 
        }
        return null;
    }


    /**
     * set the base type for this datatype
     *
     * @param base the validator for this type's base type
     *
     */
    public void setBasetype(DatatypeValidator base) {
        fBaseValidator = base;
    }


    /**
    * set the locate to be used for error messages
    */
    public void setLocale(Locale locale) {
    }


    public int compare( String content1, String content2) {
        return -1;
    }

    public Hashtable getFacets(){
        return fFacets;
    }

    // Here start private methods
    // Work in Progress ------- 

    private static long normalizeRecurringDuration(char[] value, int start ) 
        throws InvalidDatatypeValueException {
        long   normalizedDuration = 0L;

        //System.out.println("value to normalize = " + value );
        //This method will convert the Lexical representation of re
        //CCYY-MM-DDThh:mm:ss.sss 
        //


        return normalizedDuration;
    }

    public static Calendar normalizeInstant(char[] value, int start,
                                            int length) throws InvalidDatatypeValueException
    {
        boolean negative=false;
        boolean tznegative=false;
        int     tzoffset=0;
        int     tzhh=0,tzmm=0;
        int     i=start,j=0,k=0,l=0,m=0;
        final char[]ms={'0','0','0'};
        final   Calendar cal = new GregorianCalendar();
        final   int endindex = (start+length)-1;

        try
        {
            if (length < 16) throw new ParseException("Value is too short.",0);
            cal.clear();
            cal.setLenient(false);
//     If there's a leading sign, set the appropriate Era.
            if (value[i]=='-'||value[i]=='+')
            {
                cal.set(Calendar.ERA, (value[i]=='-'?GregorianCalendar.BC:GregorianCalendar.AD));
                i++;
            }
//     Grab the year (might be > 9999), month, day, hour and minute fields       
            j=indexOf(value,i,'-',i+5);
            if (j==-1 || j>endindex)throw new ParseException("Year separator is missing or misplaced.", i);
            cal.set(Calendar.YEAR, parseInt(value,i,j-i));
            i=j+1;
            cal.set(Calendar.MONTH, parseInt(value,i,2)-1);
            i+=2;
            if (value[i]!='-')throw new ParseException("Month separator is missing or misplaced.",i);
            cal.set(Calendar.DAY_OF_MONTH, parseInt(value,i+1,2));
            i+=3;
            if (value[i]!='T')throw new ParseException("Time separator is missing or misplaced.",i);
            cal.set(Calendar.HOUR_OF_DAY, parseInt(value,i+1,2));
            i+=3;
            if (value[i]!=':')throw new ParseException("Hour separator is missing or misplaced.",i);
            cal.set(Calendar.MINUTE, parseInt(value,i+1,2));
            i+=3;
//     Seconds are optional
            if ((endindex-i)>1 && (value[i]==':'))
            {
                cal.set(Calendar.SECOND, parseInt(value,i+1,2));
                i+=3;
// Grab optional fractional seconds to 3 decimal places.
                if (i<endindex && value[i]=='.')
                {
                    i++;k=0;
                    while ((i <= endindex) && (k<3) && Character.isDigit(value[i]))
                        ms[k++]=value[i++];

                    cal.set(Calendar.MILLISECOND, parseInt(ms,0,3));
                }
//     Eat any remaining digits.
                while (i<=endindex && Character.isDigit(value[i]))  i++;
            }
//     Check for timezone.
            if (i<=endindex)
            {
                if (value[i]=='Z')
                {
                    cal.set(Calendar.ZONE_OFFSET, 0);
                }
//                      else if ((endindex-i)==2 || (endindex-i)==5)
                else if (value[i]=='-' || value[i]=='+')
                {
                    tznegative = (value[i]=='-');
                    tzhh=parseInt(value,i+1,2);
                    if ((endindex-i)==5)
                    {
                        if (value[i+3] != ':')throw new ParseException("time zone must be 'hh:mm'.",i);
                        tzmm=parseInt(value,i+4,2);
                    }
                    tzoffset=((tzhh*3600000)+(tzmm*60000));
                    cal.set(Calendar.ZONE_OFFSET, (tznegative?-tzoffset:tzoffset));
                } else throw new ParseException("Unrecognized time zone.",i);
            }
            return(cal);
        } catch (Exception e)
        {
            if ( fDbug ){
                e.printStackTrace();
                return null;
            } else  {
                throw new InvalidDatatypeValueException("Unable to parse timeInstant "+e.toString());
            }
        }
    }


    /**
       * Returns a copy of this object.
       */
    public Object clone() throws CloneNotSupportedException {
        throw new CloneNotSupportedException("clone() is not supported in "+this.getClass().getName());
    }




    /*
     * check that a facet is in range, assumes that facets are compatible -- compatibility ensured by setFacets
     */
    private void boundsCheck(long f) throws InvalidDatatypeFacetException {
        boolean inUpperBound = false;
        boolean inLowerBound = false;

        if ( isMaxInclusiveDefined ) {
            inUpperBound = ( f <= fMaxInclusive );
        } else if ( isMaxExclusiveDefined ) {
            inUpperBound = ( f <  fMaxExclusive );
        }

        if ( isMinInclusiveDefined ) {
            inLowerBound = ( f >= fMinInclusive );
        } else if ( isMinExclusiveDefined ) {
            inLowerBound = ( f >  fMinExclusive );
        }

        if ( inUpperBound == false  || inLowerBound == false ) { // within bounds ?
            throw new InvalidDatatypeFacetException(
                                                   getErrorString(DatatypeMessageProvider.OutOfBounds,
                                                                  DatatypeMessageProvider.MSG_NONE,
                                                                  new Object [] { new Long(f)}));
        }
    }

    private void enumCheck(long d) throws InvalidDatatypeValueException {
        for (int i = 0; i < this.fEnumrecurringduration.length; i++) {
            if (d == fEnumrecurringduration[i]) return;
        }
        throw new InvalidDatatypeValueException(
                                               getErrorString(DatatypeMessageProvider.NotAnEnumValue,
                                                              DatatypeMessageProvider.MSG_NONE,
                                                              new Object [] { new Long(d )}));
    }

    private String getErrorString(int major, int minor, Object args[]) {
        try {
            return fMessageProvider.createMessage(fLocale, major, minor, args);
        } catch (Exception e) {
            return "Illegal Errorcode "+minor;
        }
    }

    private static final int indexOf(char[] value, int start, char s)
    {
        return(indexOf(value,start,s,value.length-1));
    }
    private static final int indexOf(char[] value, int start, char s, int max)
    {
        for (int i=start;i<=max;i++)if (value[i]==s) return(i);
        return(-1);
    }
    private static final int indexOneOf(char[] value, int start, String s)
    {
        return(indexOneOf(value,start,s,value.length-1));
    }
    private static final int indexOneOf(char[] value, int start, String s, int max)
    {
        for (int i=start;i<max;i++)
            for (int j=0;j<s.length();j++) if (value[i] == s.charAt(j))return(i);
        return(-1);
    }
//     parseInt is a copy of the Integer.parseInt method, modified to accept
// a character array.
    private static final int parseInt(char[] s, int start, int length)     throws NumberFormatException
    {
        if (s == null) throw new NumberFormatException("null");
        int radix=10;
        int result = 0;
        boolean negative = false;
        int i= start;
        int limit;
        int multmin;
        int digit=0;

        if (length <= 0) throw new NumberFormatException(new String(s,start,length));
        if (s[i] == '-')
        {
            negative = true;
            limit = Integer.MIN_VALUE;
            i++;
        } else if (s[i]=='+')
        {
            negative = false;
            limit = -Integer.MAX_VALUE;
            i++;
        } else
        {
            limit = -Integer.MAX_VALUE;
        }
        multmin = limit / radix;
        if (i < (start+length))
        {
            digit = Character.digit(s[i++],radix);
            if (digit < 0) throw new NumberFormatException(new String(s,start,length));
            else result = -digit;
        }
        while (i < (start+length))
        {
            digit = Character.digit(s[i++],radix);
            if (digit < 0) throw new NumberFormatException(new String(s,start,length));
            if (result < multmin) throw new NumberFormatException(new String(s,start,length));
            result *= radix;
            if (result < limit + digit) throw new NumberFormatException(new String(s,start,length));
            result -= digit;
        }

        if (negative)
        {
            if (i > 1) return result;
            else throw new NumberFormatException(new String(s,start,length));
        }
        return -result;



    }

}

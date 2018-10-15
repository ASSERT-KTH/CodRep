new Object [] { new Long(f),"","","",""}));//REVISIT

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
 * TimeDurationValidator validates that XML content is a W3C timeDuration.
 *
 * @author Ted Leung, George Joseph
 * @version $Id$
 */

public class TimeDurationDatatypeValidator extends AbstractDatatypeValidator {

   private Locale            fLocale           = null;
   private DatatypeValidator fBaseValidator    = null; // A Native datatype is null
   private String            fPattern          = null;
   private long              fMaxInclusive     = 0L;
   private long              fMaxExclusive     = 0L;
   private long              fMinInclusive     = 0L;
   private long              fMinExclusive     = 0L;
   private long              fDuration         = 0L;
   private long              fPeriod           = 0L;


   private boolean           isMaxExclusiveDefined = false;
   private boolean           isMaxInclusiveDefined = false;
   private boolean           isMinExclusiveDefined = false;
   private boolean           isMinInclusiveDefined = false;

   private int               fFacetsDefined        = 0;

   private boolean           fDerivedByList        = false;


   private long[]            fEnumTimeDuration = null; // Time duration is represented internally as longs

   private DatatypeMessageProvider fMessageProvider = new DatatypeMessageProvider();


    public  TimeDurationDatatypeValidator () throws InvalidDatatypeFacetException {
        this( null, null, false ); // Native, No Facets defined, Restriction
    }

    public  TimeDurationDatatypeValidator ( DatatypeValidator base, Hashtable facets, 
                  boolean derivedByList ) throws InvalidDatatypeFacetException {
        if ( base != null )
            setBasetype( base ); // Set base type 


        fDerivedByList = derivedByList;
        // Set Facets if any defined

        if ( facets != null  )  {
            if ( fDerivedByList == false ) { // Restriction
                if (fBaseValidator != null)
                    //if (!fBaseValidator.ensureFacetsAreConsistent(facets))
                      //  throw new InvalidDatatypeFacetException(
                        //                                       getErrorString( DatatypeMessageProvider.FacetsInconsistent,
                          //                                                     DatatypeMessageProvider.MSG_NONE, null));

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
                            fMaxInclusive = normalizeDuration( value.toCharArray(), 0 ); 
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
                            fMaxExclusive = normalizeDuration( value.toCharArray(), 0 );
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
                            fMinInclusive = normalizeDuration( value.toCharArray(), 0 );
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
                            fMinExclusive = normalizeDuration( value.toCharArray(), 0 ); 

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
                        fEnumTimeDuration = new long[v.size()];
                        int     i     = 0;
                        String  value = null;
                        try {
                            for (; i < v.size(); i++){
                                value = (String)v.elementAt(i);
                                fEnumTimeDuration[i] = 
                                normalizeDuration( value.toCharArray(),0 );
                                boundsCheck(fEnumTimeDuration[i]); // Check against max,min Inclusive, Exclusives
                            }
                        } catch (InvalidDatatypeValueException idve) {
                            throw new InvalidDatatypeFacetException(
                                                                   getErrorString(DatatypeMessageProvider.InvalidEnumValue,
                                                                                  DatatypeMessageProvider.MSG_NONE,
                                                                                  new Object [] { v.elementAt(i)}));
                        }
                    }
                }
            } else { //Derived by List TODO 

            }
        }// End Facet definition
    }


    /**
     * validates a String to be a Lexical representation
     * of a TimeDuration Datatype.
     * 
     * @param content A string containing the content to be validated
     * @param state
     * @return 
     * @exception InvalidDatatypeValueException
     *                   If String is does not represent a
     *                   valid TimeDuration datatype.
     */
    public Object validate(String content, Object state) 
                                       throws InvalidDatatypeValueException{
        long normalizedValue;

        if ( fDerivedByList == false  ) { //derived by constraint
             if ( fPattern != null ) {
                 RegularExpression regex = new RegularExpression(fPattern, "X" );
                 if ( regex.matches( content) == false )
                     throw new InvalidDatatypeValueException("Value'"+content+
                                  "does not match regular expression facet" + fPattern );
             }

             normalizedValue = normalizeDuration(content.toCharArray(), 0 ); 
             try {
                 boundsCheck( normalizedValue );
             } catch( InvalidDatatypeFacetException ex ){
                 throw new InvalidDatatypeValueException( "Boundary Exception" );
             }

             if( fEnumTimeDuration != null )
                 enumCheck( normalizedValue );

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
        return null;
    }

    public static long normalizeDuration(char[] value, int start ) 
    throws InvalidDatatypeValueException
    {
        int i=0, j=0, k=0, l=0, m=0;
        int sepindex  = 0;
        int index     = start;
        int lindex    = 0;
        int endindex  = (start+ value.length)-1;
        int pendindex = endindex;

        final char[] dseps = {'Y','M','D'};
        final char[] tseps = {'H','M','S'};
        final char[] msc = {'0','0','0'};

        final int[] buckets = new int[Calendar.FIELD_COUNT];
        for (i=0;i<buckets.length;i++)
            buckets[i]=0;

        boolean intime           = false;
        boolean fixed            = false;
        boolean p1negative       = false;
        boolean p2negative       = false;
        boolean p1specified      = false;
        boolean p2specified      = false;
        GregorianCalendar cstart = null;
        GregorianCalendar cend   = null;

        //Start phase 1: capture start and/or end instant.
        try
        {
            if (value[index]=='-')
            {
                p1negative=true;
            }
            //Look for the forward slash.
            int ix = indexOf(value, start, '/');

            if (ix > -1 && ix < endindex)
            {
                if (value[ix+1]=='-')
                {
                    p2negative=true;
                }
                //If the first term starts with a 'P', pin it for later parsing 
                if (value[(p1negative?index+1:index)]=='P')
                {
                    if (p1negative)
                        index++;
                    p1specified = true;
                    pendindex   = ix-1;
                }
                //Otherwise parse it for a timeInstant
                else
                {
                    cstart = (GregorianCalendar) normalizeInstant(value, index, ix-index);
                }
                //If the second term starts with a 'P', pin it for later parsing 
                if (value[(p2negative?(ix+2):(ix+1))]=='P')
                {
                    p2specified=true;
                    index=(p2negative?(ix+2):(ix+1));
                }
                //Otherwise parse it for a timeInstant
                else
                {
                    ix++;
                    cend = (GregorianCalendar)  normalizeInstant(value,ix,(endindex-ix)+1);
                }
            }
            //Only one term specified.
            else
            {
                index=(p1negative?(start+1):(start));
            }
            //If both terms are instants, return the millisecond difference
            if (cstart != null && cend != null)
            {
                return((cend.getTime().getTime() - cstart.getTime().getTime()));
            }
            //If both terms are 'P', error.
            if (p1specified && p2specified)
                throw new ParseException("Period cannot be expressed as 2 durations.", 0);

            if (p1specified && value[index] != 'P')
            {
                throw new ParseException("Invalid start character for timeDuration:"+value[index], index);
            }
            if (p2specified && value[index] != 'P')
            {
                throw new ParseException("Invalid start character for timeDuration:"+value[index], index);
            }
        } catch (Exception e)
        {
            throw new InvalidDatatypeValueException(e.toString());
        }
        //Second phase....parse 'P' term
        try
        {

            lindex=index+1;
            for (i=index+1;i<=pendindex;i++)
            {
                //Accumulate digits.
                if (Character.isDigit(value[i]) || value[i]=='.')
                {
                    if (value[i]=='.')fixed=true;
                    continue;
                }
                if (value[i]=='T')
                {
                    intime=true;
                    sepindex=0;
                    lindex=i+1;
                    continue;
                }
                //If you get a separator, it must be appropriate for the section.
                sepindex = indexOf((intime?tseps:dseps), sepindex, value[i]);
                if (sepindex == -1)
                    throw new ParseException("Illegal or misplaced separator.", i);
                sepindex++;
                //Fractional digits are allowed only for seconds.
                if (fixed && value[i]!='S')
                    throw new ParseException("Fractional digits allowed only for 'seconds'.", i);

                j=0;
                switch (value[i])
                {
                case('Y'):
                    {
                        if (intime)throw new ParseException("Year must be specified before 'T' separator.", i);
                        buckets[Calendar.YEAR]= parseInt(value, lindex, i-lindex);
                        break;
                    }
                case('D'):
                    {
                        if (intime)throw new ParseException("Days must be specified before 'T' separator.", i);
                        buckets[Calendar.DAY_OF_MONTH]= parseInt(value, lindex, i-lindex);
                        break;
                    }
                case('H'):
                    {
                        if (!intime)throw new ParseException("Hours must be specified after 'T' separator.", i);
                        buckets[Calendar.HOUR_OF_DAY]= parseInt(value, lindex, i-lindex);
                        break;
                    }
                case('M'):
                    {
                        buckets[(intime?Calendar.MINUTE:Calendar.MONTH)]= parseInt(value, lindex, i-lindex);
                        break;
                    }
                case('S'):
                    {
                        if (!intime)throw new ParseException("Seconds must be specified after 'T' separator.", i);
                        if (!fixed)buckets[Calendar.SECOND]= parseInt(value, lindex, i-lindex);
                        else
                        {
                            int ps = indexOf(value, lindex, '.');
                            buckets[Calendar.SECOND]= parseInt(value, lindex, ps-lindex);
                            ps++;k=0;
                            while ((ps <= pendindex) && (k<3) && Character.isDigit(value[ps]))
                                msc[k++]=value[ps++];
                            buckets[Calendar.MILLISECOND]= parseInt(msc, 0, 3);
                            fixed=false;
                        }
                        break;
                    }
                default:
                    {
                        throw new ParseException("Illegal 'picture' character: "+value[i], i);
                    }
                }
                lindex=i+1;
            }
        } catch (Exception e)
        {
            throw new InvalidDatatypeValueException(e.toString());
        }
        //Third phase, make the calculations.
        try
        {
            //Roll the start calendar forward and return difference.
            if (cstart !=null)
            {
                long st = cstart.getTime().getTime();
                for (k=0;k<buckets.length;k++)
                    if (buckets[k]!=0)cstart.add(k, (p2negative?-buckets[k]:buckets[k]));
                long ms = cstart.getTime().getTime();
                return((ms-st));
            }
            //Roll the end calendar backward and return difference.
            if (cend !=null)
            {
                long st = cend.getTime().getTime();
                for (k=0;k<buckets.length;k++)
                    if (buckets[k]>0) cend.add(k, (p1negative?buckets[k]:-buckets[k]));
                long ms = cend.getTime().getTime();
                return((ms-st));
            }
            //Otherwise roll the relative specification forward and reverse the sing as appropriate.	
            long r=(((long)(( (buckets[Calendar.YEAR]*31104000L)+
                              (buckets[Calendar.MONTH]*2592000L)+
                              (buckets[Calendar.DAY_OF_MONTH]*86400L)+
                              (buckets[Calendar.HOUR_OF_DAY]*3600L)+
                              (buckets[Calendar.MINUTE]*60L)+
                              (buckets[Calendar.SECOND]))*1000L)+
                     (buckets[Calendar.MILLISECOND])));

            return((p1negative?-r:r));
        } catch (Exception e)
        {
            throw new InvalidDatatypeValueException(e.toString());
        }
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
//	If there's a leading sign, set the appropriate Era.
            if (value[i]=='-'||value[i]=='+')
            {
                cal.set(Calendar.ERA, (value[i]=='-'?GregorianCalendar.BC:GregorianCalendar.AD));
                i++;
            }
//	Grab the year (might be > 9999), month, day, hour and minute fields  	
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
//	Seconds are optional
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
//	Eat any remaining digits.
                while (i<=endindex && Character.isDigit(value[i]))  i++;
            }
//	Check for timezone.
            if (i<=endindex)
            {
                if (value[i]=='Z')
                {
                    cal.set(Calendar.ZONE_OFFSET, 0);
                }
//  				else if ((endindex-i)==2 || (endindex-i)==5)
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
            e.printStackTrace();
            throw new InvalidDatatypeValueException("Unable to parse timeInstant "+e.toString());
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
        for (int i = 0; i < this.fEnumTimeDuration.length; i++) {
            if (d == fEnumTimeDuration[i]) return;
        }
        throw new InvalidDatatypeValueException(
			getErrorString(DatatypeMessageProvider.NotAnEnumValue,
				       	   DatatypeMessageProvider.MSG_NONE,
				       	   new Object [] { new Long( d ) }));
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

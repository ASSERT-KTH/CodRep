new Object [] { new Double(d), "","","","" }); //REVISIT

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

import java.util.Enumeration;
import java.util.Hashtable;
import java.util.Locale;
import java.util.Vector;
import org.apache.xerces.validators.schema.SchemaSymbols;
import org.apache.xerces.utils.regex.RegularExpression;

/**
 *
 * @author Ted Leung
 * @author Jeffrey Rodriguez
 * @version $Id$
 */

public class DoubleDatatypeValidator extends AbstractDatatypeValidator {
    private Locale            fLocale           = null;
    private DatatypeValidator fBaseValidator    = null; // Null means a native datatype
    private boolean           fDerivedByList = false; //Derived by restriction is defaul
    private double[]          fEnumDoubles      = null;
    private String            fPattern          = null;
    private double            fMaxInclusive     = Double.MAX_VALUE;
    private double            fMaxExclusive     = Double.MAX_VALUE;
    private double            fMinInclusive     = Double.MIN_VALUE;
    private double            fMinExclusive     = Double.MIN_VALUE;
    private int               fFacetsDefined    = 0;

    private boolean           isMaxExclusiveDefined = false;
    private boolean           isMaxInclusiveDefined = false;
    private boolean           isMinExclusiveDefined = false;
    private boolean           isMinInclusiveDefined = false;
    private RegularExpression      fRegex           = null;

    private DatatypeMessageProvider fMessageProvider = new DatatypeMessageProvider();



    public DoubleDatatypeValidator () throws InvalidDatatypeFacetException {
        this( null, null, false ); // Native, No Facets defined, Restriction
    }

    public DoubleDatatypeValidator ( DatatypeValidator base, Hashtable facets,
                                     boolean derivedByList ) throws InvalidDatatypeFacetException  {
        if ( base != null )
            setBasetype( base ); // Set base type 


        fDerivedByList = derivedByList;

        if ( facets != null ) {   // Set Facet
            if ( fDerivedByList == false ) { 
                for (Enumeration e = facets.keys(); e.hasMoreElements();) {
                    String key = (String) e.nextElement();
                    if (key.equals(SchemaSymbols.ELT_PATTERN)) {
                        fFacetsDefined += DatatypeValidator.FACET_PATTERN;
                        fPattern = (String)facets.get(key);
                        if ( fPattern != null )
                            fRegex = new RegularExpression(fPattern, "X" );

                    } else if (key.equals(SchemaSymbols.ELT_ENUMERATION)) {
                        fFacetsDefined += DatatypeValidator.FACET_ENUMERATION;
                        continue; //Treat the enumaration after this for loop
                    } else if (key.equals(SchemaSymbols.ELT_MAXINCLUSIVE)) {
                        fFacetsDefined += DatatypeValidator.FACET_MAXINCLUSIVE;
                        String value = null;
                        try {
                            value  = ((String)facets.get(key));
                            fMaxInclusive = Double.valueOf(value).doubleValue();
                        } catch (NumberFormatException ex ) {
                            throw new InvalidDatatypeFacetException( getErrorString(
                                                                                   DatatypeMessageProvider.IllegalFacetValue, 
                                                                                   DatatypeMessageProvider.MSG_NONE, new Object [] { value, key}));
                        }
                    } else if (key.equals(SchemaSymbols.ELT_MAXEXCLUSIVE)) {
                        fFacetsDefined += DatatypeValidator.FACET_MAXEXCLUSIVE;
                        String value = null;
                        try {
                            value  = ((String)facets.get(key));
                            fMaxExclusive = Double.valueOf(value).doubleValue();
                        } catch (NumberFormatException ex ) {
                            throw new InvalidDatatypeFacetException( getErrorString(
                                                                                   DatatypeMessageProvider.IllegalFacetValue, 
                                                                                   DatatypeMessageProvider.MSG_NONE, new Object [] { value, key}));
                        }
                    } else if (key.equals(SchemaSymbols.ELT_MININCLUSIVE)) {
                        fFacetsDefined += DatatypeValidator.FACET_MININCLUSIVE;
                        String value = null;
                        try {
                            value  = ((String)facets.get(key));
                            fMinInclusive  = Double.valueOf(value).doubleValue();
                        } catch (NumberFormatException ex ) {
                            throw new InvalidDatatypeFacetException( getErrorString(
                                                                                   DatatypeMessageProvider.IllegalFacetValue, 
                                                                                   DatatypeMessageProvider.MSG_NONE, new Object [] { value, key}));
                        }
                    } else if (key.equals(SchemaSymbols.ELT_MINEXCLUSIVE)) {
                        fFacetsDefined += DatatypeValidator.FACET_MININCLUSIVE;
                        String value = null;
                        try {
                            value  = ((String)facets.get(key));
                            fMinExclusive  = Double.valueOf(value).doubleValue();
                        } catch (NumberFormatException ex ) {
                            throw new InvalidDatatypeFacetException( getErrorString(
                                                                                   DatatypeMessageProvider.IllegalFacetValue, 
                                                                                   DatatypeMessageProvider.MSG_NONE, new Object [] { value, key}));
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
                        fEnumDoubles = new double[v.size()];
                        for (int i = 0; i < v.size(); i++)
                            try {
                                fEnumDoubles[i] = Double.valueOf((String) v.elementAt(i)).doubleValue();
                                boundsCheck(fEnumDoubles[i]); // Check against max,min Inclusive, Exclusives
                            } catch (InvalidDatatypeValueException idve) {
                                throw new InvalidDatatypeFacetException(
                                                                       getErrorString(DatatypeMessageProvider.InvalidEnumValue,
                                                                                      DatatypeMessageProvider.MSG_NONE,
                                                                                      new Object [] { v.elementAt(i)}));
                            } catch (NumberFormatException nfe) {
                                System.out.println("Internal Error parsing enumerated values for real type");
                            }
                    }
                }
            } else {
                //WORK TO DO -  Add derivation by list Double type
            }
        }// End of facet setting
    }




    /**
     * validate that a string matches the real datatype
     * @param content A string containing the content to be validated
     * @exception throws InvalidDatatypeException if the content is
     *  is not a W3C real type
     */

    public Object validate(String content, Object state) 
    throws InvalidDatatypeValueException {
        if ( fDerivedByList == false ) { //derived by restriction
            if ( (fFacetsDefined & DatatypeValidator.FACET_PATTERN ) != 0 ) {
                if ( fRegex == null || fRegex.matches( content) == false )
                    throw new InvalidDatatypeValueException("Value'"+content+
                                                            "does not match regular expression facet" + fPattern );
            }


            double d = 0.0;
            try {
                d = Double.valueOf(content).doubleValue();
            } catch (NumberFormatException nfe) {
                throw new InvalidDatatypeValueException(
                                                       getErrorString(DatatypeMessageProvider.NotReal,
                                                                      DatatypeMessageProvider.MSG_NONE,
                                                                      new Object [] { content}));
            }
            boundsCheck(d);

            if (((fFacetsDefined & DatatypeValidator.FACET_ENUMERATION ) != 0 ) )
                enumCheck(d);

        } else {
            ;// TODO Derived by list validation
        }
        return null;
    }

    // Private Methods start here


    /*
     * check that a facet is in range, assumes that facets are compatible -- compatibility ensured by setFacets
     */
    private void boundsCheck(double d) throws InvalidDatatypeValueException {
        boolean inUpperBound = false;
        boolean inLowerBound = false;

        if ( isMaxInclusiveDefined ) {
            inUpperBound = ( d <= fMaxInclusive );
        } else if ( isMaxExclusiveDefined ) {
            inUpperBound = ( d <  fMaxExclusive );
        }

        if ( isMinInclusiveDefined ) {
            inLowerBound = ( d >= fMinInclusive );
        } else if ( isMinExclusiveDefined ) {
            inLowerBound = ( d >  fMinExclusive );
        }

        if ( inUpperBound == false  || inLowerBound == false ) { // within bounds ?
            getErrorString(DatatypeMessageProvider.OutOfBounds,
                           DatatypeMessageProvider.MSG_NONE,
                           new Object [] { new Double(d)});
        }
    }

    private void enumCheck(double v) throws InvalidDatatypeValueException {
        for (int i = 0; i < fEnumDoubles.length; i++) {
            if (v == fEnumDoubles[i]) return;
        }
        throw new InvalidDatatypeValueException(
                                               getErrorString(DatatypeMessageProvider.NotAnEnumValue,
                                                              DatatypeMessageProvider.MSG_NONE,
                                                              new Object [] { new Double(v)}));
    }

    /**
     * Compare two Double datatype. Comparison is
     * in Space value.
     * 
     * @param content1
     * @param content2
     * @return 
     */
    public int compare( String content1, String content2){
        return 0;
    }


    /**
     * Returns a Hashtable containing facet information.
     * 
     * @return 
     */
    public Hashtable getFacets(){
        return null;
    }
    /**
       * Returns a copy of this object.
       */
    public Object clone() throws CloneNotSupportedException {
        throw new CloneNotSupportedException("clone() is not supported in "+this.getClass().getName());
    }



    private String getErrorString(int major, int minor, Object args[]) {
        try {
            return fMessageProvider.createMessage(fLocale, major, minor, args);
        } catch (Exception e) {
            return "Illegal Errorcode "+minor;
        }
    }


    private void setBasetype(DatatypeValidator base) {
        fBaseValidator =  base;
    }

}
facets.put(SchemaSymbols.ELT_MININCLUSIVE, "1" );

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 2000 The Apache Software Foundation.  All rights 
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
import java.lang.reflect.*;
import org.apache.xerces.validators.datatype.*;
import org.apache.xerces.validators.schema.SchemaSymbols;
import org.apache.xerces.validators.datatype.DatatypeValidatorFactory;
import org.apache.xerces.validators.datatype.InvalidDatatypeFacetException;




/**
 * @version $Id$
 * @author  Jeffrey Rodriguez
 */

public class DatatypeValidatorFactoryImpl implements DatatypeValidatorFactory {
    private static final boolean fDebug = false;
    private static DatatypeValidatorFactoryImpl _instance = new DatatypeValidatorFactoryImpl();
    private Hashtable fRegistry = new Hashtable();


    private DatatypeValidatorFactoryImpl() {
        initializeRegistry();
    }

    /**
     * Initializes registry with primitive and derived
     * Simple types.
     */
    void initializeRegistry() {
        DatatypeValidator  v = null;

        //Register Primitive Datatypes 

        try {
            fRegistry.put("string",            new StringDatatypeValidator() );
            fRegistry.put("boolean",           new BooleanDatatypeValidator()  );
            fRegistry.put("float",             new FloatDatatypeValidator());
            fRegistry.put("double",            new DoubleDatatypeValidator());
            fRegistry.put("decimal",           new DecimalDatatypeValidator());
            fRegistry.put("timeDuration",      new TimeDurationDatatypeValidator());
            fRegistry.put("recurringDuration", new RecurringDurationDatatypeValidator());
            fRegistry.put("binary",            new BinaryDatatypeValidator());
            fRegistry.put("uriReference",      new URIReferenceDatatypeValidator());
            fRegistry.put("ID",                new IDDatatypeValidator());
            fRegistry.put("IDREF",             new IDREFDatatypeValidator());
            fRegistry.put("ENTITY",            new ENTITYDatatypeValidator());
            fRegistry.put("NOTATION",          new NOTATIONDatatypeValidator());
            fRegistry.put("QName",             new QNameDatatypeValidator()); 


            Hashtable facets = new Hashtable();
            facets.put(SchemaSymbols.ELT_PATTERN , "([a-zA-Z]{2}|[iI]-[a-zA-Z]+|[xX]-[a-zA-Z]+)(-[a-zA-Z]+)*" );
            
            createDatatypeValidator("language", new StringDatatypeValidator() , facets,
                                                 false );

            createDatatypeValidator( "IDREFS", new IDREFDatatypeValidator(), null , true );

            createDatatypeValidator( "ENTITIES", new ENTITYDatatypeValidator(),  null, true );

            facets = new Hashtable();
            facets.put(SchemaSymbols.ELT_PATTERN , "\\c+" );
            createDatatypeValidator("NMTOKEN", new StringDatatypeValidator(), facets, false );

            createDatatypeValidator("NMTOKENS",  
                                                 getDatatypeValidator( "NMTOKEN" ), null, true );


            facets = new Hashtable();
            facets.put(SchemaSymbols.ELT_PATTERN , "\\i\\c*" );
            createDatatypeValidator("Name", new StringDatatypeValidator(), facets, false );

            facets = new Hashtable();
            facets.put(SchemaSymbols.ELT_PATTERN , "[\\i-[:]][\\c-[:]]*"  );
            createDatatypeValidator("NCName", new StringDatatypeValidator(), facets, false );

            facets = new Hashtable();
            facets.put(SchemaSymbols.ELT_SCALE, "0");
            createDatatypeValidator("integer", new DecimalDatatypeValidator(), facets, false);


            facets = new Hashtable();
            facets.put(SchemaSymbols.ELT_MAXINCLUSIVE , "0" );
            createDatatypeValidator("nonPositiveInteger", 
                                                 getDatatypeValidator("integer"), facets, false );


            facets = new Hashtable();
            facets.put(SchemaSymbols.ELT_MAXINCLUSIVE , "-1" );
            createDatatypeValidator("negativeInteger", 
                                                 getDatatypeValidator( "nonPositiveInteger"), facets, false );

            facets = new Hashtable();
            facets.put(SchemaSymbols.ELT_MAXINCLUSIVE , "9223372036854775807");
            facets.put(SchemaSymbols.ELT_MININCLUSIVE,  "-9223372036854775808");
            createDatatypeValidator("long", getDatatypeValidator( "integer"), facets, false );

            facets = new Hashtable();
            facets.put(SchemaSymbols.ELT_MAXINCLUSIVE , "2147483647");
            facets.put(SchemaSymbols.ELT_MININCLUSIVE,  "-2147483648");
            createDatatypeValidator("int", getDatatypeValidator( "long"), facets,false );

            facets = new Hashtable();
            facets.put(SchemaSymbols.ELT_MAXINCLUSIVE , "32767");
            facets.put(SchemaSymbols.ELT_MININCLUSIVE,  "-32768");
            createDatatypeValidator("short", getDatatypeValidator( "int"), facets, false );

            facets = new Hashtable();
            facets.put(SchemaSymbols.ELT_MAXINCLUSIVE , "127");
            facets.put(SchemaSymbols.ELT_MININCLUSIVE,  "-128");
            createDatatypeValidator("byte",
                                        getDatatypeValidator( "short"), facets, false );

            facets = new Hashtable();
            facets.put(SchemaSymbols.ELT_MININCLUSIVE, "0" );
            createDatatypeValidator("nonNegativeInteger", 
                                          getDatatypeValidator( "integer"), facets, false );

            facets = new Hashtable();
            facets.put(SchemaSymbols.ELT_MAXINCLUSIVE, "18446744073709551615" );
            createDatatypeValidator("unsignedLong",
                                                 getDatatypeValidator( "nonNegativeInteger"), facets, false );


            facets = new Hashtable();
            facets.put(SchemaSymbols.ELT_MAXINCLUSIVE, "4294967295" );
            createDatatypeValidator("unsignedInt",
                                                 getDatatypeValidator( "unsignedLong"), facets, false );


            facets = new Hashtable();
            facets.put(SchemaSymbols.ELT_MAXINCLUSIVE, "65535" );
            createDatatypeValidator("unsignedShort", 
                                                 getDatatypeValidator( "unsignedInt"), facets, false );


            facets = new Hashtable();
            facets.put(SchemaSymbols.ELT_MAXINCLUSIVE, "255" );
            createDatatypeValidator("unsignedByte",
                                                 getDatatypeValidator( "unsignedShort"), facets, false );

            facets = new Hashtable();
            facets.put(SchemaSymbols.ELT_MAXINCLUSIVE, "255" );
            createDatatypeValidator("positiveInteger",
                                                 getDatatypeValidator( "nonNegativeInteger"), facets, false );


            facets = new Hashtable();
            facets.put(SchemaSymbols.ELT_DURATION, "P0Y" );
            facets.put(SchemaSymbols.ELT_PERIOD,   "P0Y" );
            createDatatypeValidator("timeInstant", 
                                                 getDatatypeValidator( "recurringDuration"),facets, false );

            facets = new Hashtable();
            facets.put(SchemaSymbols.ELT_DURATION, "P0Y" );
//            facets.put(SchemaSymbols.ELT_PERIOD,   "PY24H" ); Bug -- WORK TODO
            createDatatypeValidator("time", 
                                                 getDatatypeValidator( "recurringDuration"), facets, false );

            facets = new Hashtable();
            facets.put(SchemaSymbols.ELT_PERIOD,   "P0Y" );
            createDatatypeValidator("timePeriod", 
                                                 getDatatypeValidator( "recurringDuration"), facets, false );


            facets = new Hashtable();
            facets.put(SchemaSymbols.ELT_DURATION, "PT24H" );
            createDatatypeValidator("date",
                                                 getDatatypeValidator( "timePeriod"), facets, false );


            facets = new Hashtable();
            facets.put(SchemaSymbols.ELT_DURATION, "P1M" );
            createDatatypeValidator("month",
                                                 getDatatypeValidator( "timePeriod"), facets, false );

            facets = new Hashtable();
            facets.put(SchemaSymbols.ELT_DURATION, "P1Y" );
            createDatatypeValidator("year", 
                                                 getDatatypeValidator( "timePeriod"), facets, false );

            facets = new Hashtable();
            facets.put(SchemaSymbols.ELT_DURATION, "P100Y" );
            createDatatypeValidator("century", 
                                                 getDatatypeValidator( "timePeriod"), facets, false );

            facets = new Hashtable();
            facets.put(SchemaSymbols.ELT_PERIOD, "P1Y" );
            facets.put(SchemaSymbols.ELT_DURATION, "PT24H" );
            createDatatypeValidator("recurringDate",
                                                 getDatatypeValidator( "recurringDuration"),facets, false );
        } catch ( InvalidDatatypeFacetException ex ){
            ex.printStackTrace();
        }
    }

    public void resetRegistry(){
        fRegistry.clear();
        initializeRegistry();
    }

    public DatatypeValidator createDatatypeValidator(String typeName, 
            DatatypeValidator base, Hashtable facets, boolean list ) throws InvalidDatatypeFacetException {

        DatatypeValidator simpleType = null;

        if (this.fDebug == true) {
            System.out.println("type name = " + typeName );
        }

        if ( base != null ) {
            try {
                Class validatorDef = base.getClass();

                Class [] validatorArgsClass = new Class[] {  
                    org.apache.xerces.validators.datatype.DatatypeValidator.class,
                    java.util.Hashtable.class,
                    boolean.class};



                Object [] validatorArgs     = new Object[] {
                    base, facets, new Boolean( list )};




                Constructor validatorConstructor =
                validatorDef.getConstructor( validatorArgsClass );


                simpleType = 
                ( DatatypeValidator ) createDatatypeValidator (
                                                 validatorConstructor, validatorArgs );

                if (simpleType != null) {
                    addValidator( typeName, simpleType );//register validator
                }


            } catch (NoSuchMethodException e) {
                e.printStackTrace();
            }

        }
        return simpleType;// return it
    }



    private static Object createDatatypeValidator(Constructor validatorConstructor, 
                   Object[] arguments)  throws  InvalidDatatypeFacetException {
        Object validator = null;
        try {
            validator = validatorConstructor.newInstance(arguments);
            return validator;
        } catch (InstantiationException e) {
            if( fDebug ){
                e.printStackTrace();
            }else {
                return null;
            }
        } catch (IllegalAccessException e) {
            if( fDebug ){
                e.printStackTrace();
            }else {
                return null;
            }
        } catch (IllegalArgumentException e) {
            if( fDebug ){
                e.printStackTrace();
            }else {
                return null;
            }
        } catch (InvocationTargetException e) {
            if ( fDebug ){
                System.out.println("!! The original error message is: " + e.getTargetException().getMessage() );
                e.getTargetException().printStackTrace();
            } else {
                 throw new InvalidDatatypeFacetException( e.getTargetException().getMessage() );
                //System.out.println("Exception: " + e.getTargetException
                //validator = null;
            }
        }
        return validator;
    }


    public DatatypeValidator getDatatypeValidator(String type) {
        AbstractDatatypeValidator simpleType = null;
        if( fDebug ) {
            System.out.println( "type = >" + type +"<");
            System.out.println( "fRegistry = >" + fRegistry +"<" );
            simpleType = (AbstractDatatypeValidator) fRegistry.get(type);
        }
        if ( type != null && fRegistry != null
                          && fRegistry.containsKey( type ) == true ) {
            simpleType = (AbstractDatatypeValidator) fRegistry.get(type);

            // This code is not needed after all.
            // and it is a potential performance hit.
            //if ( simpleType != null ) { // if not registered type to create one
              //  try {
               //     simpleType  = (AbstractDatatypeValidator) simpleType.clone();
                //} catch (CloneNotSupportedException cloneExc) {
                  //  try {
                   //     simpleType = (AbstractDatatypeValidator) simpleType.getClass().newInstance(); 
                   // } catch( InstantiationException e ) {
                    //    e.printStackTrace();
                   // } catch( IllegalAccessException e ) {
                    //    e.printStackTrace();
                    //}
                 //}
            //}
        }
        return (DatatypeValidator) simpleType;
    }

    private void addValidator(String name, DatatypeValidator v) {
        fRegistry.put(name,v);
    }

    static public DatatypeValidatorFactoryImpl getDatatypeRegistry()  {
        return _instance;
    }

    static public void main( String argv[] ){
        DatatypeValidatorFactoryImpl  tstRegistry = DatatypeValidatorFactoryImpl.getDatatypeRegistry();


        DatatypeValidator   tstData1            = tstRegistry.getDatatypeValidator( "NTOKEN" );
        DatatypeValidator   tstData2            = tstRegistry.getDatatypeValidator( "NTOKENS" );

        System.out.println( "NMTOKEN = " + tstData1 );
        System.out.println( "NMTOKENS = " + tstData2 );

    }
}

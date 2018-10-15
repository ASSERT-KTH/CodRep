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

import org.apache.xerces.impl.dv.SchemaDVFactory;
import org.apache.xerces.impl.dv.XSSimpleType;
import org.apache.xerces.impl.dv.XSAtomicSimpleType;
import org.apache.xerces.impl.dv.XSListSimpleType;
import org.apache.xerces.impl.dv.XSUnionSimpleType;
import org.apache.xerces.impl.dv.XSFacets;
import java.util.Hashtable;

/**
 * the factory to create/return built-in schema DVs and create user-defined DVs
 *
 * @author Neeraj Bajaj, Sun Microsystems, inc.
 * @author Sandy Gao, IBM
 *
 * @version $Id$
 */
public class SchemaDVFactoryImpl extends SchemaDVFactory {

    static final String URI_SCHEMAFORSCHEMA = "http://www.w3.org/2001/XMLSchema";

    static Hashtable fBuiltInTypes = null;

    /**
     * Get a built-in simple type of the given name
     * REVISIT: its still not decided within the Schema WG how to define the
     *          ur-types and if all simple types should be derived from a
     *          complex type, so as of now we ignore the fact that anySimpleType
     *          is derived from anyType, and pass 'null' as the base of
     *          anySimpleType. It needs to be changed as per the decision taken.
     *
     * @param name  the name of the datatype
     * @return      the datatype validator of the given name
     */
    public XSSimpleType getBuiltInType(String name) {
        prepareBuiltInTypes();
        return (XSSimpleType)fBuiltInTypes.get(name);
    }

    /**
     * get all built-in simple types, which are stored in a hashtable keyed by
     * the name
     *
     * @return      a hashtable which contains all built-in simple types
     */
    public Hashtable getBuiltInTypes() {
        prepareBuiltInTypes();
        return (Hashtable)fBuiltInTypes.clone();
    }

    /**
     * Create a new simple type which is derived by restriction from another
     * simple type.
     *
     * @param name              name of the new type, could be null
     * @param targetNamespace   target namespace of the new type, could be null
     * @param finalSet          value of "final"
     * @param base              base type of the new type
     * @return                  the newly created simple type
     */
    public XSSimpleType createTypeRestriction(String name, String targetNamespace,
                                              short finalSet, XSSimpleType base) {
        return new XSSimpleTypeDecl((XSSimpleTypeDecl)base, name, targetNamespace, finalSet);
    }

    /**
     * Create a new simple type which is derived by list from another simple
     * type.
     *
     * @param name              name of the new type, could be null
     * @param targetNamespace   target namespace of the new type, could be null
     * @param finalSet          value of "final"
     * @param itemType          item type of the list type
     * @return                  the newly created simple type
     */
    public XSListSimpleType createTypeList(String name, String targetNamespace,
                                           short finalSet, XSSimpleType itemType) {
        prepareBuiltInTypes();
        return new XSSimpleTypeDecl(name, targetNamespace, finalSet, (XSSimpleTypeDecl)itemType);
    }

    /**
     * Create a new simple type which is derived by union from a list of other
     * simple types.
     *
     * @param name              name of the new type, could be null
     * @param targetNamespace   target namespace of the new type, could be null
     * @param finalSet          value of "final"
     * @param base              member types of the union type
     * @return                  the newly created simple type
     */
    public XSUnionSimpleType createTypeUnion(String name, String targetNamespace,
                                             short finalSet, XSSimpleType[] memberTypes) {
        prepareBuiltInTypes();
        int typeNum = memberTypes.length;
        XSSimpleTypeDecl[] mtypes = new XSSimpleTypeDecl[typeNum];
        System.arraycopy(memberTypes, 0, mtypes, 0, typeNum);
        return new XSSimpleTypeDecl(name, targetNamespace, finalSet, mtypes);
    }

    // make sure the built-in types are created
    // the types are supposed to be reused for all factory objects,
    // so we synchorinize on the class object.
    void prepareBuiltInTypes() {
        if (fBuiltInTypes == null) {
            synchronized (this.getClass()) {
                // check again, in case I'm waiting for another thread to create
                // the types.
                if (fBuiltInTypes == null) {
                    createBuiltInTypes();
                }
            }
        }
    }

    // create all built-in types
    // we are assumeing that fBuiltInTypes == null
    void createBuiltInTypes() {

        // all schema simple type names
        final String ANYSIMPLETYPE     = "anySimpleType";
        final String ANYURI            = "anyURI";
        final String BASE64BINARY      = "base64Binary";
        final String BOOLEAN           = "boolean";
        final String BYTE              = "byte";
        final String DATE              = "date";
        final String DATETIME          = "dateTime";
        final String DAY               = "gDay";
        final String DECIMAL           = "decimal";
        final String DOUBLE            = "double";
        final String DURATION          = "duration";
        final String ENTITY            = "ENTITY";
        final String ENTITIES          = "ENTITIES";
        final String FLOAT             = "float";
        final String HEXBINARY         = "hexBinary";
        final String ID                = "ID";
        final String IDREF             = "IDREF";
        final String IDREFS            = "IDREFS";
        final String INT               = "int";
        final String INTEGER           = "integer";
        final String LONG              = "long";
        final String NAME              = "Name";
        final String NEGATIVEINTEGER   = "negativeInteger";
        final String MONTH             = "gMonth";
        final String MONTHDAY          = "gMonthDay";
        final String NCNAME            = "NCName";
        final String NMTOKEN           = "NMTOKEN";
        final String NMTOKENS          = "NMTOKENS";
        final String LANGUAGE          = "language";
        final String NONNEGATIVEINTEGER= "nonNegativeInteger";
        final String NONPOSITIVEINTEGER= "nonPositiveInteger";
        final String NORMALIZEDSTRING  = "normalizedString";
        final String NOTATION          = "NOTATION";
        final String POSITIVEINTEGER   = "positiveInteger";
        final String QNAME             = "QName";
        final String SHORT             = "short";
        final String STRING            = "string";
        final String TIME              = "time";
        final String TOKEN             = "token";
        final String UNSIGNEDBYTE      = "unsignedByte";
        final String UNSIGNEDINT       = "unsignedInt";
        final String UNSIGNEDLONG      = "unsignedLong";
        final String UNSIGNEDSHORT     = "unsignedShort";
        final String YEAR              = "gYear";
        final String YEARMONTH         = "gYearMonth";

        final XSFacets facets = new XSFacets();

        fBuiltInTypes = new Hashtable();
        //REVISIT: passing "anyType" here.
        XSSimpleTypeDecl anySimpleType = XSSimpleTypeDecl.fAnySimpleType;
        fBuiltInTypes.put(ANYSIMPLETYPE, anySimpleType);
        XSSimpleTypeDecl stringDV = new XSSimpleTypeDecl(anySimpleType, STRING, XSSimpleTypeDecl.DV_STRING, XSSimpleType.ORDERED_FALSE, false, XSSimpleType.CARDINALITY_COUNTABLY_INFINITE, false );
        fBuiltInTypes.put(STRING, stringDV);
        fBuiltInTypes.put(BOOLEAN, new XSSimpleTypeDecl(anySimpleType, STRING, XSSimpleTypeDecl.DV_BOOLEAN, XSSimpleType.ORDERED_FALSE, false, XSSimpleType.CARDINALITY_FINITE, false));
        XSSimpleTypeDecl decimalDV = new XSSimpleTypeDecl(anySimpleType, DECIMAL, XSSimpleTypeDecl.DV_DECIMAL, XSSimpleType.ORDERED_TOTAL, false, XSSimpleType.CARDINALITY_COUNTABLY_INFINITE, true);
        fBuiltInTypes.put(DECIMAL, decimalDV);

        fBuiltInTypes.put(ANYURI, new XSSimpleTypeDecl(anySimpleType, ANYURI, XSSimpleTypeDecl.DV_ANYURI, XSSimpleType.ORDERED_FALSE, false, XSSimpleType.CARDINALITY_COUNTABLY_INFINITE, false));
        fBuiltInTypes.put(BASE64BINARY, new XSSimpleTypeDecl(anySimpleType, BASE64BINARY, XSSimpleTypeDecl.DV_BASE64BINARY, XSSimpleType.ORDERED_FALSE, false, XSSimpleType.CARDINALITY_COUNTABLY_INFINITE, false));
        fBuiltInTypes.put(DURATION, new XSSimpleTypeDecl(anySimpleType, DURATION, XSSimpleTypeDecl.DV_DURATION, XSSimpleType.ORDERED_PARTIAL, false, XSSimpleType.CARDINALITY_COUNTABLY_INFINITE, false));
        fBuiltInTypes.put(DATETIME, new XSSimpleTypeDecl(anySimpleType, DATETIME, XSSimpleTypeDecl.DV_DATETIME, XSSimpleType.ORDERED_PARTIAL, false, XSSimpleType.CARDINALITY_COUNTABLY_INFINITE, false));
        fBuiltInTypes.put(TIME, new XSSimpleTypeDecl(anySimpleType, TIME, XSSimpleTypeDecl.DV_TIME, XSSimpleType.ORDERED_PARTIAL, false, XSSimpleType.CARDINALITY_COUNTABLY_INFINITE, false));
        fBuiltInTypes.put(DATE, new XSSimpleTypeDecl(anySimpleType, DATE, XSSimpleTypeDecl.DV_DATE, XSSimpleType.ORDERED_PARTIAL, false, XSSimpleType.CARDINALITY_COUNTABLY_INFINITE, false));
        fBuiltInTypes.put(YEARMONTH, new XSSimpleTypeDecl(anySimpleType, YEARMONTH, XSSimpleTypeDecl.DV_GYEARMONTH, XSSimpleType.ORDERED_PARTIAL, false, XSSimpleType.CARDINALITY_COUNTABLY_INFINITE, false));
        fBuiltInTypes.put(YEAR, new XSSimpleTypeDecl(anySimpleType, YEAR, XSSimpleTypeDecl.DV_GYEAR, XSSimpleType.ORDERED_PARTIAL, false, XSSimpleType.CARDINALITY_COUNTABLY_INFINITE, false));
        fBuiltInTypes.put(MONTHDAY, new XSSimpleTypeDecl(anySimpleType, MONTHDAY, XSSimpleTypeDecl.DV_GMONTHDAY, XSSimpleType.ORDERED_PARTIAL, false, XSSimpleType.CARDINALITY_COUNTABLY_INFINITE, false));
        fBuiltInTypes.put(DAY, new XSSimpleTypeDecl(anySimpleType, DAY, XSSimpleTypeDecl.DV_GDAY, XSSimpleType.ORDERED_PARTIAL, false, XSSimpleType.CARDINALITY_COUNTABLY_INFINITE, false));
        fBuiltInTypes.put(MONTH, new XSSimpleTypeDecl(anySimpleType, MONTH, XSSimpleTypeDecl.DV_GMONTH, XSSimpleType.ORDERED_PARTIAL, false, XSSimpleType.CARDINALITY_COUNTABLY_INFINITE, false));

        facets.fractionDigits = 0;
        XSSimpleTypeDecl integerDV = new XSSimpleTypeDecl(decimalDV, INTEGER, URI_SCHEMAFORSCHEMA, (short)0);
        integerDV.applyFacets1(facets , XSSimpleType.FACET_FRACTIONDIGITS, (short)0);
        fBuiltInTypes.put(INTEGER, integerDV);

        facets.maxInclusive = "0";
        XSSimpleTypeDecl nonPositiveDV = new XSSimpleTypeDecl(integerDV, NONPOSITIVEINTEGER, URI_SCHEMAFORSCHEMA, (short)0);
        nonPositiveDV.applyFacets1(facets , XSSimpleType.FACET_MAXINCLUSIVE, (short)0);
        fBuiltInTypes.put(NONPOSITIVEINTEGER, nonPositiveDV);

        facets.maxInclusive = "-1";
        XSSimpleTypeDecl negativeDV = new XSSimpleTypeDecl(integerDV, NEGATIVEINTEGER, URI_SCHEMAFORSCHEMA, (short)0);
        negativeDV.applyFacets1(facets , XSSimpleType.FACET_MAXINCLUSIVE, (short)0);
        fBuiltInTypes.put(NEGATIVEINTEGER, negativeDV);

        facets.maxInclusive = "9223372036854775807";
        facets.minInclusive = "-9223372036854775808";
        XSSimpleTypeDecl longDV = new XSSimpleTypeDecl(integerDV, LONG, URI_SCHEMAFORSCHEMA, (short)0);
        longDV.applyFacets1(facets , (short)(XSSimpleType.FACET_MAXINCLUSIVE | XSSimpleType.FACET_MININCLUSIVE), (short)0 );
        fBuiltInTypes.put(LONG, longDV);


        facets.maxInclusive = "2147483647";
        facets.minInclusive =  "-2147483648";
        XSSimpleTypeDecl intDV = new XSSimpleTypeDecl(longDV, INT, URI_SCHEMAFORSCHEMA, (short)0);
        intDV.applyFacets1(facets, (short)(XSSimpleType.FACET_MAXINCLUSIVE | XSSimpleType.FACET_MININCLUSIVE), (short)0 );
        fBuiltInTypes.put(INT, intDV);

        facets.maxInclusive = "32767";
        facets.minInclusive = "-32768";
        XSSimpleTypeDecl shortDV = new XSSimpleTypeDecl(intDV, SHORT , URI_SCHEMAFORSCHEMA, (short)0);
        shortDV.applyFacets1(facets, (short)(XSSimpleType.FACET_MAXINCLUSIVE | XSSimpleType.FACET_MININCLUSIVE), (short)0 );
        fBuiltInTypes.put(SHORT, shortDV);

        facets.maxInclusive = "127";
        facets.minInclusive = "-128";
        XSSimpleTypeDecl byteDV = new XSSimpleTypeDecl(shortDV, BYTE , URI_SCHEMAFORSCHEMA, (short)0);
        byteDV.applyFacets1(facets, (short)(XSSimpleType.FACET_MAXINCLUSIVE | XSSimpleType.FACET_MININCLUSIVE), (short)0 );
        fBuiltInTypes.put(BYTE, byteDV);

        facets.minInclusive =  "0" ;
        XSSimpleTypeDecl nonNegativeDV = new XSSimpleTypeDecl(integerDV, NONNEGATIVEINTEGER , URI_SCHEMAFORSCHEMA, (short)0);
        nonNegativeDV.applyFacets1(facets, XSSimpleType.FACET_MININCLUSIVE, (short)0 );
        fBuiltInTypes.put(NONNEGATIVEINTEGER, nonNegativeDV);

        facets.maxInclusive = "18446744073709551615" ;
        XSSimpleTypeDecl unsignedLongDV = new XSSimpleTypeDecl(nonNegativeDV, UNSIGNEDLONG , URI_SCHEMAFORSCHEMA, (short)0);
        unsignedLongDV.applyFacets1(facets, XSSimpleType.FACET_MAXINCLUSIVE, (short)0 );
        fBuiltInTypes.put(UNSIGNEDLONG, unsignedLongDV);

        facets.maxInclusive = "4294967295" ;
        XSSimpleTypeDecl unsignedIntDV = new XSSimpleTypeDecl(unsignedLongDV, UNSIGNEDINT , URI_SCHEMAFORSCHEMA, (short)0);
        unsignedIntDV.applyFacets1(facets, XSSimpleType.FACET_MAXINCLUSIVE, (short)0 );
        fBuiltInTypes.put(UNSIGNEDINT, unsignedIntDV);

        facets.maxInclusive = "65535" ;
        XSSimpleTypeDecl unsignedShortDV = new XSSimpleTypeDecl(unsignedIntDV, UNSIGNEDSHORT , URI_SCHEMAFORSCHEMA, (short)0);
        unsignedShortDV.applyFacets1(facets, XSSimpleType.FACET_MAXINCLUSIVE, (short)0 );
        fBuiltInTypes.put(UNSIGNEDSHORT, unsignedShortDV);

        facets.maxInclusive = "255" ;
        XSSimpleTypeDecl unsignedByteDV = new XSSimpleTypeDecl(unsignedShortDV, UNSIGNEDBYTE , URI_SCHEMAFORSCHEMA, (short)0);
        unsignedByteDV.applyFacets1(facets, XSSimpleType.FACET_MAXINCLUSIVE, (short)0 );
        fBuiltInTypes.put(UNSIGNEDBYTE, unsignedByteDV);

        facets.minInclusive = "1" ;
        XSSimpleTypeDecl positiveIntegerDV = new XSSimpleTypeDecl(nonNegativeDV, POSITIVEINTEGER , URI_SCHEMAFORSCHEMA, (short)0);
        positiveIntegerDV.applyFacets1(facets, XSSimpleType.FACET_MININCLUSIVE, (short)0 );
        fBuiltInTypes.put(POSITIVEINTEGER, positiveIntegerDV);


        fBuiltInTypes.put(FLOAT, new XSSimpleTypeDecl(anySimpleType, FLOAT, XSSimpleTypeDecl.DV_FLOAT, XSSimpleType.ORDERED_TOTAL, true, XSSimpleType.CARDINALITY_FINITE, true));
        fBuiltInTypes.put(DOUBLE, new XSSimpleTypeDecl(anySimpleType, DOUBLE, XSSimpleTypeDecl.DV_DOUBLE, XSSimpleType.ORDERED_TOTAL, true, XSSimpleType.CARDINALITY_FINITE, true));
        fBuiltInTypes.put(HEXBINARY, new XSSimpleTypeDecl(anySimpleType, HEXBINARY, XSSimpleTypeDecl.DV_HEXBINARY, XSSimpleType.ORDERED_FALSE, false, XSSimpleType.CARDINALITY_COUNTABLY_INFINITE, false));
        fBuiltInTypes.put(NOTATION, new XSSimpleTypeDecl(anySimpleType, NOTATION, XSSimpleTypeDecl.DV_NOTATION, XSSimpleType.ORDERED_FALSE, false, XSSimpleType.CARDINALITY_COUNTABLY_INFINITE, false));


        facets.whiteSpace =  XSSimpleType.WS_REPLACE;
        XSSimpleTypeDecl normalizedDV = new XSSimpleTypeDecl(stringDV, NORMALIZEDSTRING , URI_SCHEMAFORSCHEMA, (short)0);
        normalizedDV.applyFacets1(facets, XSSimpleType.FACET_WHITESPACE, (short)0 );
        fBuiltInTypes.put(NORMALIZEDSTRING, normalizedDV);

        facets.whiteSpace = XSSimpleType.WS_COLLAPSE;
        XSSimpleTypeDecl tokenDV = new XSSimpleTypeDecl(normalizedDV, TOKEN , URI_SCHEMAFORSCHEMA, (short)0);
        tokenDV.applyFacets1(facets, XSSimpleType.FACET_WHITESPACE, (short)0 );
        fBuiltInTypes.put(TOKEN, tokenDV);

        facets.whiteSpace = XSSimpleType.WS_COLLAPSE;
        facets.pattern  = "([a-zA-Z]{2}|[iI]-[a-zA-Z]+|[xX]-[a-zA-Z]+)(-[a-zA-Z]+)*";
        XSSimpleTypeDecl languageDV = new XSSimpleTypeDecl(tokenDV, LANGUAGE , URI_SCHEMAFORSCHEMA, (short)0);
        languageDV.applyFacets1(facets, (short)(XSSimpleType.FACET_WHITESPACE | XSSimpleType.FACET_PATTERN) ,(short)0);
        fBuiltInTypes.put(LANGUAGE, languageDV);


        facets.whiteSpace =  XSSimpleType.WS_COLLAPSE;
        XSSimpleTypeDecl nameDV = new XSSimpleTypeDecl(tokenDV, NAME , URI_SCHEMAFORSCHEMA, (short)0);
        nameDV.applyFacets1(facets, XSSimpleType.FACET_WHITESPACE, (short)0, XSSimpleTypeDecl.SPECIAL_TOKEN_NAME);
        fBuiltInTypes.put(NAME, nameDV);

        facets.whiteSpace = XSSimpleType.WS_COLLAPSE;
        XSSimpleTypeDecl ncnameDV = new XSSimpleTypeDecl(nameDV, NCNAME , URI_SCHEMAFORSCHEMA, (short)0) ;
        ncnameDV.applyFacets1(facets, XSSimpleType.FACET_WHITESPACE, (short)0, XSSimpleTypeDecl.SPECIAL_TOKEN_NCNAME);
        fBuiltInTypes.put(NCNAME, ncnameDV);

        fBuiltInTypes.put(QNAME, new XSSimpleTypeDecl(anySimpleType, QNAME, XSSimpleTypeDecl.DV_QNAME, XSSimpleType.ORDERED_FALSE, false, XSSimpleType.CARDINALITY_COUNTABLY_INFINITE, false));

        fBuiltInTypes.put(ID, new XSSimpleTypeDecl(ncnameDV,  ID, XSSimpleTypeDecl.DV_ID, XSSimpleType.ORDERED_FALSE, false, XSSimpleType.CARDINALITY_COUNTABLY_INFINITE, false ));
        XSSimpleTypeDecl idrefDV = new XSSimpleTypeDecl(ncnameDV,  IDREF , XSSimpleTypeDecl.DV_IDREF, XSSimpleType.ORDERED_FALSE, false, XSSimpleType.CARDINALITY_COUNTABLY_INFINITE, false);
        fBuiltInTypes.put(IDREF, idrefDV);

        facets.minLength = 1;
        XSSimpleTypeDecl tempDV = new XSSimpleTypeDecl(null, URI_SCHEMAFORSCHEMA, (short)0, idrefDV);
        XSSimpleTypeDecl idrefsDV = new XSSimpleTypeDecl(tempDV, IDREFS, URI_SCHEMAFORSCHEMA, (short)0);
        idrefsDV.applyFacets1(facets, XSSimpleType.FACET_MINLENGTH, (short)0);
        fBuiltInTypes.put(IDREFS, idrefsDV);

        XSSimpleTypeDecl entityDV = new XSSimpleTypeDecl(ncnameDV, ENTITY , XSSimpleTypeDecl.DV_ENTITY, XSSimpleType.ORDERED_FALSE, false, XSSimpleType.CARDINALITY_COUNTABLY_INFINITE, false);
        fBuiltInTypes.put(ENTITY, entityDV);

        facets.minLength = 1;
        tempDV = new XSSimpleTypeDecl(null, URI_SCHEMAFORSCHEMA, (short)0, entityDV);
        XSSimpleTypeDecl entitiesDV = new XSSimpleTypeDecl(tempDV, ENTITIES, URI_SCHEMAFORSCHEMA, (short)0);
        entitiesDV.applyFacets1(facets, XSSimpleType.FACET_MINLENGTH, (short)0);
        fBuiltInTypes.put(ENTITIES, entitiesDV);


        facets.whiteSpace  = XSSimpleType.WS_COLLAPSE;
        XSSimpleTypeDecl nmtokenDV = new XSSimpleTypeDecl(tokenDV, NMTOKEN, URI_SCHEMAFORSCHEMA, (short)0);
        nmtokenDV.applyFacets1(facets, XSSimpleType.FACET_WHITESPACE, (short)0, XSSimpleTypeDecl.SPECIAL_TOKEN_NMTOKEN);
        fBuiltInTypes.put(NMTOKEN, nmtokenDV);

        facets.minLength = 1;
        tempDV = new XSSimpleTypeDecl(null, URI_SCHEMAFORSCHEMA, (short)0, nmtokenDV);
        XSSimpleTypeDecl nmtokensDV = new XSSimpleTypeDecl(tempDV, NMTOKENS, URI_SCHEMAFORSCHEMA, (short)0);
        nmtokensDV.applyFacets1(facets, XSSimpleType.FACET_MINLENGTH, (short)0);
        fBuiltInTypes.put(NMTOKENS, nmtokensDV);

    }//createBuiltInTypes()

}//SchemaDVFactory
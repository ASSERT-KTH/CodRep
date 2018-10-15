fXSTypeCount = fullSet?FULLSET_COUNT:BASICSET_COUNT;

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

package org.apache.xerces.impl.v2;

import org.apache.xerces.impl.v2.datatypes.*;
import org.apache.xerces.util.SymbolTable;
import org.apache.xerces.xni.QName;
import org.apache.xerces.impl.validation.ContentModelValidator;

import java.lang.Integer;
import java.util.Hashtable;
import java.util.Vector;
/**
 * @version $Id$
 */

public class SchemaGrammar {

    /** Chunk shift (8). */
    private static final int CHUNK_SHIFT = 8; // 2^8 = 256

    /** Chunk size (1 << CHUNK_SHIFT). */
    private static final int CHUNK_SIZE = 1 << CHUNK_SHIFT;

    /** Chunk mask (CHUNK_SIZE - 1). */
    private static final int CHUNK_MASK = CHUNK_SIZE - 1;

    /** Initial chunk count (). */
    private static final int INITIAL_CHUNK_COUNT = (1 << (10 - CHUNK_SHIFT)); // 2^10 = 1k

    /** Symbol table. */
    private SymbolTable fSymbolTable;

    /** Target namespace of grammar. */
    private String fTargetNamespace;

    // decl count: element, attribute, notation, particle, type
    private int fElementDeclCount = 0;
    private int fAttributeDeclCount = 0 ;
    private int fNotationCount = 0;
    private int fParticleCount = 0;
    private int fXSTypeCount = 0;

    /** Element declaration contents. */
    private QName fElementDeclName[][];
    private String fElementDeclTypeNS[][];
    private int fElementDeclTypeDecl[][];
    private short fElementDeclMiscFlags[][];
    private int fElementDeclBlockSet[][];
    private int fElementDeclFinalSet[][];
    private String fElementDeclDefault[][];
    private int fElementDeclSubGroupNS[][];
    private int fElementDeclSubGroupIdx[][];
    private Vector fElementDeclUnique[][];
    private Vector fElementDeclKey[][];
    private Vector fElementDeclKeyRef[][];

    // attribute declarations
    private QName fAttributeDeclName[][];
    private String fAttributeDeclTypeNS[][];
    private int fAttributeDeclType[][];
    private short fAttributeDeclConstraintType[][];
    private String fAttributeDeclDefault[][];

    // particles
    private short fParticleType[][];
    private String fParticleUri[][];
    private int fParticleValue[][];
    private String fParticleOtherUri[][];
    private int fParticleOtherValue[][];
    private int fParticleMinOccurs[][];
    private int fParticleMaxOccurs[][];

    // notations
    private String fNotationName[][];
    private String fNotationPublicId[][];
    private String fNotationSystemId[][];

    //REVISIT: as temporary solution store complexTypes/simpleTypes as objects
    // Add XML Schema datatypes 
    private QName fTypeDeclQName[][];
    private XSType fTypeDeclType[][];

    // other information

    // global decls
    Hashtable topLevelGroupDecls = new Hashtable();
    Hashtable topLevelNotationDecls = new Hashtable();
    Hashtable topLevelAttrDecls  = new Hashtable();
    Hashtable topLevelAttrGrpDecls = new Hashtable();
    Hashtable topLevelElemDecls = new Hashtable();
    Hashtable topLevelTypeDecls = new Hashtable();

    // REVISIT: do we need the option?
    // Set if we check Unique Particle Attribution
    // This one onle takes effect when deferContentSpecExpansion is set
    private boolean checkUniqueParticleAttribution = false;
    private boolean checkingUPA = false;

    //
    // Constructors
    //

    /** Default constructor. */
    public SchemaGrammar(SymbolTable symbolTable) {
        fSymbolTable = symbolTable;

        // element decl
        fElementDeclName = new QName[INITIAL_CHUNK_COUNT][];
        fElementDeclTypeNS = new String[INITIAL_CHUNK_COUNT][];
        fElementDeclTypeDecl = new int[INITIAL_CHUNK_COUNT][];
        fElementDeclMiscFlags = new short[INITIAL_CHUNK_COUNT][];
        fElementDeclBlockSet = new int[INITIAL_CHUNK_COUNT][];
        fElementDeclFinalSet = new int[INITIAL_CHUNK_COUNT][];
        fElementDeclDefault = new String[INITIAL_CHUNK_COUNT][];
        fElementDeclSubGroupNS = new int[INITIAL_CHUNK_COUNT][];
        fElementDeclSubGroupIdx = new int[INITIAL_CHUNK_COUNT][];
        fElementDeclUnique = new Vector[INITIAL_CHUNK_COUNT][];
        fElementDeclKey = new Vector[INITIAL_CHUNK_COUNT][];
        fElementDeclKeyRef = new Vector[INITIAL_CHUNK_COUNT][];

        // attribute declarations
        fAttributeDeclName = new QName[INITIAL_CHUNK_COUNT][];
        fAttributeDeclTypeNS = new String[INITIAL_CHUNK_COUNT][];
        fAttributeDeclType = new int[INITIAL_CHUNK_COUNT][];
        fAttributeDeclConstraintType = new short[INITIAL_CHUNK_COUNT][];
        fAttributeDeclDefault = new String[INITIAL_CHUNK_COUNT][];

        // particles
        fParticleType = new short[INITIAL_CHUNK_COUNT][];
        fParticleUri = new String[INITIAL_CHUNK_COUNT][];
        fParticleValue = new int[INITIAL_CHUNK_COUNT][];
        fParticleOtherUri = new String[INITIAL_CHUNK_COUNT][];
        fParticleOtherValue = new int[INITIAL_CHUNK_COUNT][];
        fParticleMinOccurs = new int[INITIAL_CHUNK_COUNT][];
        fParticleMaxOccurs = new int[INITIAL_CHUNK_COUNT][];

        // notations
        fNotationName = new String[INITIAL_CHUNK_COUNT][];
        fNotationPublicId = new String[INITIAL_CHUNK_COUNT][];
        fNotationSystemId = new String[INITIAL_CHUNK_COUNT][];

        //REVISIT: as temporary solution store complexTypes/simpleTypes as objects
        // Add XML Schema datatypes 
        fTypeDeclQName = new QName[INITIAL_CHUNK_COUNT][];
        fTypeDeclType = new XSType[INITIAL_CHUNK_COUNT][];

    } // <init>(SymbolTable)

    private static final int BASICSET_COUNT = 29;
    private static final int FULLSET_COUNT  = 46;

    /** Constructor for schema for schemas. */
    private SchemaGrammar(SymbolTable symbolTable, boolean fullSet) {
        fSymbolTable = symbolTable;

        fXSTypeCount = fullSet?BASICSET_COUNT:FULLSET_COUNT;
        fTypeDeclType = new XSType[1][fXSTypeCount];
        topLevelTypeDecls = new Hashtable();

        try {
            int typeIndex = 0;
            XSComplexTypeDecl anyType = new XSComplexTypeDecl();
            fTypeDeclType[0][typeIndex] = anyType;
            topLevelTypeDecls.put(SchemaSymbols.ATTVAL_ANYTYPE, new Integer(typeIndex++));
            //REVISIT: make anyType the base of anySimpleType
            //DatatypeValidator anySimpleType = new AnySimpleType(anyType, null, false);
            DatatypeValidator anySimpleType = new AnySimpleType(null, null, false);
            fTypeDeclType[0][typeIndex] = anySimpleType;
            topLevelTypeDecls.put(SchemaSymbols.ATTVAL_ANYSIMPLETYPE, new Integer(typeIndex++));
            DatatypeValidator stringDV = new StringDatatypeValidator(anySimpleType, null, false);
            fTypeDeclType[0][typeIndex] = stringDV;
            topLevelTypeDecls.put(SchemaSymbols.ATTVAL_STRING, new Integer(typeIndex++));
            fTypeDeclType[0][typeIndex] = new BooleanDatatypeValidator(anySimpleType, null, false);
            topLevelTypeDecls.put(SchemaSymbols.ATTVAL_BOOLEAN, new Integer(typeIndex++));
            DatatypeValidator decimalDV = new DecimalDatatypeValidator(anySimpleType, null, false);
            fTypeDeclType[0][typeIndex] = decimalDV;
            topLevelTypeDecls.put(SchemaSymbols.ATTVAL_DECIMAL, new Integer(typeIndex++));
            fTypeDeclType[0][typeIndex] = new AnyURIDatatypeValidator(anySimpleType, null, false);
            topLevelTypeDecls.put(SchemaSymbols.ATTVAL_ANYURI, new Integer(typeIndex++));
            fTypeDeclType[0][typeIndex] = new Base64BinaryDatatypeValidator(anySimpleType, null, false);
            topLevelTypeDecls.put(SchemaSymbols.ATTVAL_BASE64BINARY, new Integer(typeIndex++));
            fTypeDeclType[0][typeIndex] = new DurationDatatypeValidator(anySimpleType, null, false);
            topLevelTypeDecls.put(SchemaSymbols.ATTVAL_DURATION, new Integer(typeIndex++));
            fTypeDeclType[0][typeIndex] = new DateTimeDatatypeValidator(anySimpleType, null, false);
            topLevelTypeDecls.put(SchemaSymbols.ATTVAL_DATETIME, new Integer(typeIndex++));
            fTypeDeclType[0][typeIndex] = new TimeDatatypeValidator(anySimpleType, null, false);
            topLevelTypeDecls.put(SchemaSymbols.ATTVAL_TIME, new Integer(typeIndex++));
            fTypeDeclType[0][typeIndex] = new DateDatatypeValidator(anySimpleType, null, false);
            topLevelTypeDecls.put(SchemaSymbols.ATTVAL_DATE, new Integer(typeIndex++));
            fTypeDeclType[0][typeIndex] = new YearMonthDatatypeValidator(anySimpleType, null, false);
            topLevelTypeDecls.put(SchemaSymbols.ATTVAL_YEARMONTH, new Integer(typeIndex++));
            fTypeDeclType[0][typeIndex] = new YearDatatypeValidator(anySimpleType, null, false);
            topLevelTypeDecls.put(SchemaSymbols.ATTVAL_YEAR, new Integer(typeIndex++));
            fTypeDeclType[0][typeIndex] = new MonthDayDatatypeValidator(anySimpleType, null, false);
            topLevelTypeDecls.put(SchemaSymbols.ATTVAL_MONTHDAY, new Integer(typeIndex++));
            fTypeDeclType[0][typeIndex] = new DayDatatypeValidator(anySimpleType, null, false);
            topLevelTypeDecls.put(SchemaSymbols.ATTVAL_DAY, new Integer(typeIndex++));
            fTypeDeclType[0][typeIndex] = new MonthDatatypeValidator(anySimpleType, null, false);
            topLevelTypeDecls.put(SchemaSymbols.ATTVAL_MONTH, new Integer(typeIndex++));
    
            Hashtable facets = new Hashtable(2);
            facets.put(SchemaSymbols.ELT_FRACTIONDIGITS, "0");
            DatatypeValidator integerDV = new DecimalDatatypeValidator(decimalDV, facets, false);
            fTypeDeclType[0][typeIndex] = integerDV;
            topLevelTypeDecls.put(SchemaSymbols.ATTVAL_INTEGER, new Integer(typeIndex++));
            facets.clear();
            facets.put(SchemaSymbols.ELT_MAXINCLUSIVE , "0" );
            DatatypeValidator nonPositiveDV = new DecimalDatatypeValidator(integerDV, facets, false);
            fTypeDeclType[0][typeIndex] = nonPositiveDV;
            topLevelTypeDecls.put(SchemaSymbols.ATTVAL_NONPOSITIVEINTEGER, new Integer(typeIndex++));
            facets.clear();
            facets.put(SchemaSymbols.ELT_MAXINCLUSIVE , "-1" );
            fTypeDeclType[0][typeIndex] = new DecimalDatatypeValidator(nonPositiveDV, facets, false);
            topLevelTypeDecls.put(SchemaSymbols.ATTVAL_NEGATIVEINTEGER, new Integer(typeIndex++));
            facets.clear();
            facets.put(SchemaSymbols.ELT_MAXINCLUSIVE , "9223372036854775807");
            facets.put(SchemaSymbols.ELT_MININCLUSIVE,  "-9223372036854775808");
            DatatypeValidator longDV = new DecimalDatatypeValidator(integerDV, facets, false);
            fTypeDeclType[0][typeIndex] = longDV;
            topLevelTypeDecls.put(SchemaSymbols.ATTVAL_LONG, new Integer(typeIndex++));
            facets.clear();
            facets.put(SchemaSymbols.ELT_MAXINCLUSIVE , "2147483647");
            facets.put(SchemaSymbols.ELT_MININCLUSIVE,  "-2147483648");
            DatatypeValidator intDV = new DecimalDatatypeValidator(longDV, facets, false);
            fTypeDeclType[0][typeIndex] = intDV;
            topLevelTypeDecls.put(SchemaSymbols.ATTVAL_INT, new Integer(typeIndex++));
            facets.clear();
            facets.put(SchemaSymbols.ELT_MAXINCLUSIVE , "32767");
            facets.put(SchemaSymbols.ELT_MININCLUSIVE,  "-32768");
            DatatypeValidator shortDV = new DecimalDatatypeValidator(intDV, facets, false);
            fTypeDeclType[0][typeIndex] = shortDV;
            topLevelTypeDecls.put(SchemaSymbols.ATTVAL_SHORT, new Integer(typeIndex++));
            facets.clear();
            facets.put(SchemaSymbols.ELT_MAXINCLUSIVE , "127");
            facets.put(SchemaSymbols.ELT_MININCLUSIVE,  "-128");
            fTypeDeclType[0][typeIndex] = new DecimalDatatypeValidator(shortDV, facets, false);
            topLevelTypeDecls.put(SchemaSymbols.ATTVAL_BYTE, new Integer(typeIndex++));
            facets.clear();
            facets.put(SchemaSymbols.ELT_MININCLUSIVE, "0" );
            DatatypeValidator nonNegativeDV = new DecimalDatatypeValidator(integerDV, facets, false);
            fTypeDeclType[0][typeIndex] = nonNegativeDV;
            topLevelTypeDecls.put(SchemaSymbols.ATTVAL_NONNEGATIVEINTEGER, new Integer(typeIndex++));
            facets.clear();
            facets.put(SchemaSymbols.ELT_MAXINCLUSIVE, "18446744073709551615" );
            DatatypeValidator unsignedLongDV = new DecimalDatatypeValidator(nonNegativeDV, facets, false);
            fTypeDeclType[0][typeIndex] = unsignedLongDV;
            topLevelTypeDecls.put(SchemaSymbols.ATTVAL_UNSIGNEDLONG, new Integer(typeIndex++));
            facets.clear();
            facets.put(SchemaSymbols.ELT_MAXINCLUSIVE, "4294967295" );
            DatatypeValidator unsignedIntDV = new DecimalDatatypeValidator(unsignedLongDV, facets, false);
            fTypeDeclType[0][typeIndex] = unsignedIntDV;
            topLevelTypeDecls.put(SchemaSymbols.ATTVAL_UNSIGNEDINT, new Integer(typeIndex++));
            facets.clear();
            facets.put(SchemaSymbols.ELT_MAXINCLUSIVE, "65535" );
            DatatypeValidator unsignedShortDV = new DecimalDatatypeValidator(unsignedIntDV, facets, false);
            fTypeDeclType[0][typeIndex] = unsignedShortDV;
            topLevelTypeDecls.put(SchemaSymbols.ATTVAL_UNSIGNEDSHORT, new Integer(typeIndex++));
            facets.clear();
            facets.put(SchemaSymbols.ELT_MAXINCLUSIVE, "255" );
            fTypeDeclType[0][typeIndex] = new DecimalDatatypeValidator(unsignedShortDV, facets, false);
            topLevelTypeDecls.put(SchemaSymbols.ATTVAL_UNSIGNEDBYTE, new Integer(typeIndex++));
            facets.clear();
            facets.put(SchemaSymbols.ELT_MININCLUSIVE, "1" );
            fTypeDeclType[0][typeIndex] = new DecimalDatatypeValidator(nonNegativeDV, facets, false);
            topLevelTypeDecls.put(SchemaSymbols.ATTVAL_POSITIVEINTEGER, new Integer(typeIndex++));
    
            if (!fullSet)
                return;
    
            fTypeDeclType[0][typeIndex] = new FloatDatatypeValidator(anySimpleType, null, false);
            topLevelTypeDecls.put(SchemaSymbols.ATTVAL_FLOAT, new Integer(typeIndex++));
            fTypeDeclType[0][typeIndex] = new DoubleDatatypeValidator(anySimpleType, null, false);
            topLevelTypeDecls.put(SchemaSymbols.ATTVAL_DOUBLE, new Integer(typeIndex++));
            fTypeDeclType[0][typeIndex] = new HexBinaryDatatypeValidator(anySimpleType, null, false);
            topLevelTypeDecls.put(SchemaSymbols.ATTVAL_HEXBINARY, new Integer(typeIndex++));
            fTypeDeclType[0][typeIndex] = new NOTATIONDatatypeValidator(anySimpleType, null, false);
            topLevelTypeDecls.put(SchemaSymbols.ATTVAL_NOTATION, new Integer(typeIndex++));
            fTypeDeclType[0][typeIndex] = new QNameDatatypeValidator(anySimpleType, null, false);
            topLevelTypeDecls.put(SchemaSymbols.ATTVAL_QNAME, new Integer(typeIndex++));
            
            facets.clear();
            facets.put(SchemaSymbols.ELT_WHITESPACE, SchemaSymbols.ATTVAL_REPLACE);
            DatatypeValidator normalizedDV = new StringDatatypeValidator(stringDV, facets, false);
            fTypeDeclType[0][typeIndex] = normalizedDV;
            topLevelTypeDecls.put(SchemaSymbols.ATTVAL_NORMALIZEDSTRING, new Integer(typeIndex++));
            facets.clear();
            facets.put(SchemaSymbols.ELT_WHITESPACE, SchemaSymbols.ATTVAL_COLLAPSE);
            DatatypeValidator tokenDV = new StringDatatypeValidator(normalizedDV, facets, false);
            fTypeDeclType[0][typeIndex] = tokenDV;
            topLevelTypeDecls.put(SchemaSymbols.ATTVAL_TOKEN, new Integer(typeIndex++));
            facets.clear();
            facets.put(SchemaSymbols.ELT_WHITESPACE, SchemaSymbols.ATTVAL_COLLAPSE);
            facets.put(SchemaSymbols.ELT_PATTERN , "([a-zA-Z]{2}|[iI]-[a-zA-Z]+|[xX]-[a-zA-Z]+)(-[a-zA-Z]+)*" );
            fTypeDeclType[0][typeIndex] = new StringDatatypeValidator(tokenDV, facets, false);
            topLevelTypeDecls.put(SchemaSymbols.ATTVAL_LANGUAGE, new Integer(typeIndex++));
            facets.clear();
            facets.put(SchemaSymbols.ELT_WHITESPACE, SchemaSymbols.ATTVAL_COLLAPSE);
            facets.put(AbstractStringValidator.FACET_SPECIAL_TOKEN, AbstractStringValidator.SPECIAL_TOKEN_NAME);
            DatatypeValidator nameDV = new StringDatatypeValidator(tokenDV, facets, false);
            fTypeDeclType[0][typeIndex] = nameDV;
            topLevelTypeDecls.put(SchemaSymbols.ATTVAL_NAME, new Integer(typeIndex++));
            facets.clear();
            facets.put(SchemaSymbols.ELT_WHITESPACE, SchemaSymbols.ATTVAL_COLLAPSE);
            facets.put(AbstractStringValidator.FACET_SPECIAL_TOKEN, AbstractStringValidator.SPECIAL_TOKEN_NCNAME);
            DatatypeValidator ncnameDV = new StringDatatypeValidator(nameDV, facets, false);
            fTypeDeclType[0][typeIndex] = ncnameDV;
            topLevelTypeDecls.put(SchemaSymbols.ATTVAL_NCNAME, new Integer(typeIndex++));
            fTypeDeclType[0][typeIndex] = new IDDatatypeValidator(ncnameDV, null, false);
            topLevelTypeDecls.put(SchemaSymbols.ATTVAL_ID, new Integer(typeIndex++));
            DatatypeValidator idrefDV = new IDREFDatatypeValidator(ncnameDV, null, false);
            fTypeDeclType[0][typeIndex] = idrefDV;
            topLevelTypeDecls.put(SchemaSymbols.ATTVAL_IDREF, new Integer(typeIndex++));
            fTypeDeclType[0][typeIndex] = new ListDatatypeValidator(idrefDV, null, true);
            topLevelTypeDecls.put(SchemaSymbols.ATTVAL_IDREFS, new Integer(typeIndex++));
            //REVISIT: entity validators
            //DatatypeValidator entityDV = new ENTITYDatatypeValidator(ncnameDV, null, false);
            DatatypeValidator entityDV = new StringDatatypeValidator(ncnameDV, null, false);
            fTypeDeclType[0][typeIndex] = entityDV;
            topLevelTypeDecls.put(SchemaSymbols.ATTVAL_ENTITY, new Integer(typeIndex++));
            //REVISIT: entity validators
            //fTypeDeclType[0][typeIndex] = new ListDatatypeValidator(entityDV, null, true);
            fTypeDeclType[0][typeIndex] = new StringDatatypeValidator(entityDV, null, true);
            topLevelTypeDecls.put(SchemaSymbols.ATTVAL_ENTITIES, new Integer(typeIndex++));
            facets.clear();
            facets.put(SchemaSymbols.ELT_WHITESPACE, SchemaSymbols.ATTVAL_COLLAPSE);
            facets.put(AbstractStringValidator.FACET_SPECIAL_TOKEN, AbstractStringValidator.SPECIAL_TOKEN_NMTOKEN);
            DatatypeValidator nmtokenDV = new StringDatatypeValidator(tokenDV, facets, false);
            fTypeDeclType[0][typeIndex] = nmtokenDV;
            topLevelTypeDecls.put(SchemaSymbols.ATTVAL_NMTOKEN, new Integer(typeIndex++));
            fTypeDeclType[0][typeIndex] = new ListDatatypeValidator(nmtokenDV, null, true);
            topLevelTypeDecls.put(SchemaSymbols.ATTVAL_NMTOKENS, new Integer(typeIndex++));
        } catch (InvalidDatatypeFacetException idf) {
            System.err.println("Internal error");
        }
    } // <init>(SymbolTable)

    /** Returns the symbol table. */
    public SymbolTable getSymbolTable() {
        return fSymbolTable;
    } // getSymbolTable():SymbolTable

    /** Returns this grammar's target namespace. */
    public String getTargetNamespace() {
        return fTargetNamespace;
    } // getTargetNamespace():String


    /**
     * getElementIndex
     * 
     * @param elementName
     * 
     * @return REVISIT: previously if failed returned false 
     */
    public int getElementIndex(String elementName) {
        Integer elementIndex = (Integer)topLevelElemDecls.get(elementName);
        return elementIndex == null ? -1 : elementIndex.intValue();
    } // getElementDecl(int,XSElementDecl):XSElementDecl


    /**
     * addElementDecl
     * 
     * @param name
     * @param element
     * 
     * @return index
     */
    public int addElementDecl(XSElementDecl element) {
        //REVISIT
        //ensureCapacityElement();
        int elementIndex = fElementDeclCount++;
        int chunk = elementIndex >> CHUNK_SHIFT;
        int index = elementIndex & CHUNK_MASK;
        fElementDeclName[chunk][index].setValues(element.fQName);
        //REVISIT: other fields
        
        topLevelElemDecls.put(element.fQName.localpart, new Integer(elementIndex));
        
        return elementIndex;
    }

    /**
     * getElementDecl
     * 
     * @param elementDeclIndex 
     * @param elementDecl The values of this structure are set by this call.
     * 
     * @return REVISIT: previously if failed returned false 
     */
    public XSElementDecl getElementDecl(int elementDeclIndex, 
                                        XSElementDecl elementDecl) {

        if (elementDeclIndex < 0 || elementDeclIndex >= fElementDeclCount) {
            return null;
        }

        int chunk = elementDeclIndex >> CHUNK_SHIFT;
        int index = elementDeclIndex &  CHUNK_MASK;

        elementDecl.fQName.setValues(fElementDeclName[chunk][index]);

        // REVISIT: 
        // add code

        return elementDecl;
    } // getElementDecl(int,XSElementDecl):XSElementDecl


    /**
     * getElementDecl
     * 
     * @param elementName
     * @param elementDecl The values of this structure are set by this call.
     * 
     * @return REVISIT: previously if failed returned false 
     */
    public XSElementDecl getElementDecl(String elementName, 
                                        XSElementDecl elementDecl) {

        int elementIndex = getElementIndex(elementName);
        return getElementDecl(elementIndex, elementDecl);
    } // getElementDecl(int,XSElementDecl):XSElementDecl


    /**
     * getAttributeDecl
     * 
     * @param attributeDeclIndex 
     * @param attributeDecl The values of this structure are set by this call.
     * 
     * @return REVISIT: previously if failed returned false
     */
    public XSAttributeDecl getAttributeDecl(int attributeDeclIndex, XSAttributeDecl attributeDecl) {
        if (attributeDeclIndex < 0 || attributeDeclIndex >= fAttributeDeclCount) {
            return null;
        }
        
        int chunk = attributeDeclIndex >> CHUNK_SHIFT;
        int index = attributeDeclIndex & CHUNK_MASK;

        attributeDecl.fQName.setValues(fAttributeDeclName[chunk][index]);
        //REVISIT: add code

        return attributeDecl;
    } // getAttributeDecl

    /**
     * getNotationDecl
     * 
     * @param notationDeclIndex 
     * @param notationDecl 
     * 
     * @return 
     */
    /*public XSNotationDecl getNotationDecl(int notationDeclIndex, XSNotationDecl notationDecl) {
        if (notationDeclIndex < 0 || notationDeclIndex >= fNotationCount) {
            return false;
        }
        int chunk = notationDeclIndex >> CHUNK_SHIFT;
        int index = notationDeclIndex & CHUNK_MASK;

        notationDecl.setValues(fNotationName[chunk][index], 
                               fNotationPublicId[chunk][index],
                               fNotationSystemId[chunk][index]);

        return true;

    } */
    // getNotationDecl


    /**
     * getParticleDecl
     * 
     * @param particleIndex 
     * @param particle
     * 
     * @return REVISIT: previously if failed returned false
     */
    public XSParticleDecl getParticleDecl(int particleIndex, XSParticleDecl particle) {
        if (particleIndex < 0 || particleIndex >= fParticleCount )
            return null;

        int chunk = particleIndex >> CHUNK_SHIFT;
        int index = particleIndex & CHUNK_MASK;

        particle.type = fParticleType[chunk][index];

        // REVISIT: 
        // add code
        
        return particle;
    }

    /**
     * addTypeDecl
     * 
     * @param name
     * @param type
     * 
     * @return index
     */
    public int addTypeDecl(XSType type) {
        //REVISIT
        //ensureCapacityType();
        int typeIndex = fXSTypeCount++;
        int chunk = typeIndex >> CHUNK_SHIFT;
        int index = typeIndex & CHUNK_MASK;
        fTypeDeclType[chunk][index] = type;

        //REVISIT: type name
        //topLevelTypeDecls.put(typename, new Integer(typeIndex));
        
        return typeIndex;
    }

    /**
     * getTypeIndex
     * 
     * @param typeName
     * 
     * @return REVISIT: previously if failed returned false
     */
    public int getTypeIndex(String typeName) {
        Integer typeIndex = (Integer)topLevelTypeDecls.get(typeName);
        return typeIndex == null ? -1 : typeIndex.intValue();
    }

    /**
     * getTypeDecl
     * 
     * @param typeIndex 
     * 
     * @return REVISIT: previously if failed returned false
     */
    public XSType getTypeDecl(int typeIndex) {
        if (typeIndex < 0 || typeIndex >= fXSTypeCount )
            return null;

        int chunk = typeIndex >> CHUNK_SHIFT;
        int index = typeIndex & CHUNK_MASK;

        return fTypeDeclType[chunk][index];
    }

    /**
     * getTypeDecl
     * 
     * @param typeName
     * 
     * @return REVISIT: previously if failed returned false
     */
    public XSType getTypeDecl(String typeName) {
        int typeIndex = getTypeIndex(typeName);
        return getTypeDecl(typeIndex);
    }

    static SchemaGrammar SG_SchemaNS = new SchemaGrammar(null, true);
    static SchemaGrammar SG_SchemaBasicSet = new SchemaGrammar(null, false);
    
} // class SchemaGrammar
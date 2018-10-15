public final XSNotationDecl getNotationDecl(String declName) {

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
import org.apache.xerces.impl.v2.identity.IdentityConstraint;
import org.apache.xerces.util.SymbolTable;

import java.util.Hashtable;

/**
 * This class is to hold all schema component declaration that are declared
 * within one namespace.
 *
 * @author Sandy Gao, IBM
 * @author Elena Litani, IBM
 *
 * @version $Id$
 */

public class SchemaGrammar {

    /** Symbol table. */
    private SymbolTable fSymbolTable;

    // the target namespace of grammar
    private String fTargetNamespace;

    // global decls: map from decl name to decl object
    Hashtable fGlobalAttrDecls;
    Hashtable fGlobalAttrGrpDecls;
    Hashtable fGlobalElemDecls;
    Hashtable fGlobalGroupDecls;
    Hashtable fGlobalNotationDecls;
    Hashtable fGlobalTypeDecls;
    Hashtable fGlobalIDConstraintDecls;

    //
    // Constructors
    //

    /**
     * Default constructor.
     *
     * @param symbolTable
     * @param targetNamespace
     */
    public SchemaGrammar(SymbolTable symbolTable, String targetNamespace) {
        fSymbolTable = symbolTable;
        fTargetNamespace = targetNamespace;

        // REVISIT: do we know the numbers of the following global decls
        // when creating this grammar? If so, we can pass the numbers in,
        // and use that number to initialize the following hashtables.
        fGlobalAttrDecls  = new Hashtable();
        fGlobalAttrGrpDecls = new Hashtable();
        fGlobalElemDecls = new Hashtable();
        fGlobalGroupDecls = new Hashtable();
        fGlobalNotationDecls = new Hashtable();
        fGlobalTypeDecls = new Hashtable();
        fGlobalIDConstraintDecls = new Hashtable();
    } // <init>(SymbolTable, String)

    // number of built-in XSTypes we need to create for base and full
    // datatype set
    private static final int BASICSET_COUNT = 29;
    private static final int FULLSET_COUNT  = 46;

    /**
     * Special constructor to create the grammar for the schema namespace
     *
     * @param symbolTable
     * @param fullSet
     */
    private SchemaGrammar(SymbolTable symbolTable, boolean fullSet) {
        fSymbolTable = symbolTable;
        fTargetNamespace = SchemaSymbols.URI_SCHEMAFORSCHEMA;

        // set the size of type hashtable to double the number of types need
        // to be created. which should be the most effecient number.
        fGlobalTypeDecls = new Hashtable((fullSet?FULLSET_COUNT:BASICSET_COUNT)*2);

        try {
            // REVISIT: use XSSimpleTypeDecl instead
            XSComplexTypeDecl anyType = new XSComplexTypeDecl();
            anyType.fName = SchemaSymbols.ATTVAL_ANYTYPE;
            anyType.fTargetNamespace = SchemaSymbols.URI_SCHEMAFORSCHEMA;
            addGlobalTypeDecl(anyType);
            //REVISIT: make anyType the base of anySimpleType
            //DatatypeValidator anySimpleType = new AnySimpleType(anyType, null, false);
            DatatypeValidator anySimpleType = new AnySimpleType(null, null, false);
            addGlobalTypeDecl(anySimpleType);
            DatatypeValidator stringDV = new StringDatatypeValidator(anySimpleType, null, false);
            addGlobalTypeDecl(stringDV);
            addGlobalTypeDecl(new BooleanDatatypeValidator(anySimpleType, null, false));
            DatatypeValidator decimalDV = new DecimalDatatypeValidator(anySimpleType, null, false);
            addGlobalTypeDecl(decimalDV);
            addGlobalTypeDecl(new AnyURIDatatypeValidator(anySimpleType, null, false));
            addGlobalTypeDecl(new Base64BinaryDatatypeValidator(anySimpleType, null, false));
            addGlobalTypeDecl(new DurationDatatypeValidator(anySimpleType, null, false));
            addGlobalTypeDecl(new DateTimeDatatypeValidator(anySimpleType, null, false));
            addGlobalTypeDecl(new TimeDatatypeValidator(anySimpleType, null, false));
            addGlobalTypeDecl(new DateDatatypeValidator(anySimpleType, null, false));
            addGlobalTypeDecl(new YearMonthDatatypeValidator(anySimpleType, null, false));
            addGlobalTypeDecl(new YearDatatypeValidator(anySimpleType, null, false));
            addGlobalTypeDecl(new MonthDayDatatypeValidator(anySimpleType, null, false));
            addGlobalTypeDecl(new DayDatatypeValidator(anySimpleType, null, false));
            addGlobalTypeDecl(new MonthDatatypeValidator(anySimpleType, null, false));

            Hashtable facets = new Hashtable(2);
            facets.put(SchemaSymbols.ELT_FRACTIONDIGITS, "0");
            DatatypeValidator integerDV = new DecimalDatatypeValidator(decimalDV, facets, false);
            addGlobalTypeDecl(integerDV);
            facets.clear();
            facets.put(SchemaSymbols.ELT_MAXINCLUSIVE , "0" );
            DatatypeValidator nonPositiveDV = new DecimalDatatypeValidator(integerDV, facets, false);
            addGlobalTypeDecl(nonPositiveDV);
            facets.clear();
            facets.put(SchemaSymbols.ELT_MAXINCLUSIVE , "-1" );
            addGlobalTypeDecl(new DecimalDatatypeValidator(nonPositiveDV, facets, false));
            facets.clear();
            facets.put(SchemaSymbols.ELT_MAXINCLUSIVE , "9223372036854775807");
            facets.put(SchemaSymbols.ELT_MININCLUSIVE,  "-9223372036854775808");
            DatatypeValidator longDV = new DecimalDatatypeValidator(integerDV, facets, false);
            addGlobalTypeDecl(longDV);
            facets.clear();
            facets.put(SchemaSymbols.ELT_MAXINCLUSIVE , "2147483647");
            facets.put(SchemaSymbols.ELT_MININCLUSIVE,  "-2147483648");
            DatatypeValidator intDV = new DecimalDatatypeValidator(longDV, facets, false);
            addGlobalTypeDecl(intDV);
            facets.clear();
            facets.put(SchemaSymbols.ELT_MAXINCLUSIVE , "32767");
            facets.put(SchemaSymbols.ELT_MININCLUSIVE,  "-32768");
            DatatypeValidator shortDV = new DecimalDatatypeValidator(intDV, facets, false);
            addGlobalTypeDecl(shortDV);
            facets.clear();
            facets.put(SchemaSymbols.ELT_MAXINCLUSIVE , "127");
            facets.put(SchemaSymbols.ELT_MININCLUSIVE,  "-128");
            addGlobalTypeDecl(new DecimalDatatypeValidator(shortDV, facets, false));
            facets.clear();
            facets.put(SchemaSymbols.ELT_MININCLUSIVE, "0" );
            DatatypeValidator nonNegativeDV = new DecimalDatatypeValidator(integerDV, facets, false);
            addGlobalTypeDecl(nonNegativeDV);
            facets.clear();
            facets.put(SchemaSymbols.ELT_MAXINCLUSIVE, "18446744073709551615" );
            DatatypeValidator unsignedLongDV = new DecimalDatatypeValidator(nonNegativeDV, facets, false);
            addGlobalTypeDecl(unsignedLongDV);
            facets.clear();
            facets.put(SchemaSymbols.ELT_MAXINCLUSIVE, "4294967295" );
            DatatypeValidator unsignedIntDV = new DecimalDatatypeValidator(unsignedLongDV, facets, false);
            addGlobalTypeDecl(unsignedIntDV);
            facets.clear();
            facets.put(SchemaSymbols.ELT_MAXINCLUSIVE, "65535" );
            DatatypeValidator unsignedShortDV = new DecimalDatatypeValidator(unsignedIntDV, facets, false);
            addGlobalTypeDecl(unsignedShortDV);
            facets.clear();
            facets.put(SchemaSymbols.ELT_MAXINCLUSIVE, "255" );
            addGlobalTypeDecl(new DecimalDatatypeValidator(unsignedShortDV, facets, false));
            facets.clear();
            facets.put(SchemaSymbols.ELT_MININCLUSIVE, "1" );
            addGlobalTypeDecl(new DecimalDatatypeValidator(nonNegativeDV, facets, false));

            if (!fullSet)
                return;

            addGlobalTypeDecl(new FloatDatatypeValidator(anySimpleType, null, false));
            addGlobalTypeDecl(new DoubleDatatypeValidator(anySimpleType, null, false));
            addGlobalTypeDecl(new HexBinaryDatatypeValidator(anySimpleType, null, false));
            addGlobalTypeDecl(new NOTATIONDatatypeValidator(anySimpleType, null, false));

            facets.clear();
            facets.put(SchemaSymbols.ELT_WHITESPACE, SchemaSymbols.ATTVAL_REPLACE);
            DatatypeValidator normalizedDV = new StringDatatypeValidator(stringDV, facets, false);
            addGlobalTypeDecl(normalizedDV);
            facets.clear();
            facets.put(SchemaSymbols.ELT_WHITESPACE, SchemaSymbols.ATTVAL_COLLAPSE);
            DatatypeValidator tokenDV = new StringDatatypeValidator(normalizedDV, facets, false);
            addGlobalTypeDecl(tokenDV);
            facets.clear();
            facets.put(SchemaSymbols.ELT_WHITESPACE, SchemaSymbols.ATTVAL_COLLAPSE);
            //REVISIT: won't run: regexparser, locale, resource bundle
            //facets.put(SchemaSymbols.ELT_PATTERN , "([a-zA-Z]{2}|[iI]-[a-zA-Z]+|[xX]-[a-zA-Z]+)(-[a-zA-Z]+)*");
            addGlobalTypeDecl(new StringDatatypeValidator(tokenDV, facets, false));
            facets.clear();
            facets.put(SchemaSymbols.ELT_WHITESPACE, SchemaSymbols.ATTVAL_COLLAPSE);
            facets.put(AbstractStringValidator.FACET_SPECIAL_TOKEN, AbstractStringValidator.SPECIAL_TOKEN_NAME);
            DatatypeValidator nameDV = new StringDatatypeValidator(tokenDV, facets, false);
            addGlobalTypeDecl(nameDV);
            facets.clear();
            facets.put(SchemaSymbols.ELT_WHITESPACE, SchemaSymbols.ATTVAL_COLLAPSE);
            facets.put(AbstractStringValidator.FACET_SPECIAL_TOKEN, AbstractStringValidator.SPECIAL_TOKEN_NCNAME);
            DatatypeValidator ncnameDV = new StringDatatypeValidator(nameDV, facets, false);
            addGlobalTypeDecl(ncnameDV);
            DatatypeValidator qnameDV = new QNameDatatypeValidator(anySimpleType, null, false);
            ((QNameDatatypeValidator)qnameDV).setNCNameValidator(ncnameDV);
            addGlobalTypeDecl(qnameDV);
            addGlobalTypeDecl(new IDDatatypeValidator(ncnameDV, null, false));
            DatatypeValidator idrefDV = new IDREFDatatypeValidator(ncnameDV, null, false);
            addGlobalTypeDecl(idrefDV);
            addGlobalTypeDecl(new ListDatatypeValidator(idrefDV, null, true));
            //REVISIT: entity validators
            //DatatypeValidator entityDV = new ENTITYDatatypeValidator(ncnameDV, null, false);
            DatatypeValidator entityDV = new StringDatatypeValidator(ncnameDV, null, false);
            addGlobalTypeDecl(entityDV);
            //REVISIT: entity validators
            //fTypeDeclType[0][typeIndex] = new ListDatatypeValidator(entityDV, null, true);
            addGlobalTypeDecl(new StringDatatypeValidator(entityDV, null, true));
            facets.clear();
            facets.put(SchemaSymbols.ELT_WHITESPACE, SchemaSymbols.ATTVAL_COLLAPSE);
            facets.put(AbstractStringValidator.FACET_SPECIAL_TOKEN, AbstractStringValidator.SPECIAL_TOKEN_NMTOKEN);
            DatatypeValidator nmtokenDV = new StringDatatypeValidator(tokenDV, facets, false);
            addGlobalTypeDecl(nmtokenDV);
            addGlobalTypeDecl(new ListDatatypeValidator(nmtokenDV, null, true));
        } catch (InvalidDatatypeFacetException idf) {
            // should never reach here
            // REVISIT: report internal error
        }
    } // <init>(SymbolTable, boolean)

    /**
     * Returns this grammar's target namespace.
     */
    public final String getTargetNamespace() {
        return fTargetNamespace;
    } // getTargetNamespace():String

    /**
     * register one global attribute
     */
    public final void addGlobalAttributeDecl(XSAttributeDecl decl) {
        fGlobalAttrDecls.put(decl.fName, decl);
    }

    /**
     * register one global attribute group
     */
    public final void addGlobalAttributeGroupDecl(XSAttributeGroupDecl decl) {
        fGlobalAttrGrpDecls.put(decl.fName, decl);
    }

    /**
     * register one global element
     */
    public final void addGlobalElementDecl(XSElementDecl decl) {
        fGlobalElemDecls.put(decl.fName, decl);
    }

    /**
     * register one global group
     */
    public final void addGlobalGroupDecl(XSGroupDecl decl) {
        fGlobalGroupDecls.put(decl.fName, decl);
    }

    /**
     * register one global notation
     */
    public final void addGlobalNotationDecl(XSNotationDecl decl) {
        fGlobalNotationDecls.put(decl.fName, decl);
    }

    /**
     * register one global type
     */
    public final void addGlobalTypeDecl(XSTypeDecl decl) {
        fGlobalTypeDecls.put(decl.getXSTypeName(), decl);
    }

    /**
     * register one identity constraint
     */
    public final void addIDConstraintDecl(XSElementDecl elmDecl, IdentityConstraint decl) {
        elmDecl.addIDConstaint(decl);
        fGlobalIDConstraintDecls.put(decl.getIdentityConstraintName(), decl);
    }

    /**
     * get one global attribute
     */
    public final XSAttributeDecl getGlobalAttributeDecl(String declName) {
        return (XSAttributeDecl)fGlobalAttrDecls.get(declName);
    }

    /**
     * get one global attribute group
     */
    public final XSAttributeGroupDecl getGlobalAttributeGroupDecl(String declName) {
        return (XSAttributeGroupDecl)fGlobalAttrGrpDecls.get(declName);
    }

    /**
     * get one global element
     */
    public final XSElementDecl getGlobalElementDecl(String declName) {
        return (XSElementDecl)fGlobalElemDecls.get(declName);
    }

    /**
     * get one global group
     */
    public final XSGroupDecl getGlobalGroupDecl(String declName) {
        return (XSGroupDecl)fGlobalGroupDecls.get(declName);
    }

    /**
     * get one global notation
     */
    public final XSNotationDecl getGlobalNotationDecl(String declName) {
        return (XSNotationDecl)fGlobalNotationDecls.get(declName);
    }

    /**
     * get one global type
     */
    public final XSTypeDecl getGlobalTypeDecl(String declName) {
        return (XSTypeDecl)fGlobalTypeDecls.get(declName);
    }

    /**
     * get one identity constraint
     */
    public final IdentityConstraint getIDConstraintDecl(String declName) {
        return (IdentityConstraint)fGlobalIDConstraintDecls.get(declName);
    }

    // the grammars to hold built-in types
    final static SchemaGrammar SG_SchemaNS = new SchemaGrammar(null, true);
    final static SchemaGrammar SG_SchemaBasicSet = new SchemaGrammar(null, false);

} // class SchemaGrammar
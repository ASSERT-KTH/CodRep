public static final String ATTVAL_NAME              = "Name";

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

package org.apache.xerces.impl.v2;

import org.apache.xerces.util.SymbolTable;

/**
 * Collection of symbols used to parse a Schema Grammar.
 *
 * @author jeffrey rodriguez
 * @version $Id$
 */
public final class SchemaSymbols {

    // strings that's not added to the schema symbol table, because they
    // are not symbols in the schema document.
    // the validator can choose to add them by itself.

    // the following strings (xsi:, xsd) will be added into the
    // symbol table that comes with the parser

    // xmlns attributes
    public static final String O_XMLNS                         = "xmlns";
    // xsi attributes: in validator
    public static final String URI_XSI                        = "http://www.w3.org/2001/XMLSchema-instance";
    public static final String OXSI_SCHEMALOCATION            = "schemaLocation";
    public static final String OXSI_NONAMESPACESCHEMALOCATION = "noNamespaceSchemaLocation";
    public static final String OXSI_TYPE                       = "type";
    public static final String OXSI_NIL                        = "nil";

    // schema namespace
    public static final String OURI_SCHEMAFORSCHEMA            = "http://www.w3.org/2001/XMLSchema";

    // the schema symbol table that holds all schema symbols.
    // these are used within schema traversers (including XSDHandler).
    // when a new DOM parser is created to parse schema document,
    // XSDHandler is responsible for passing this symbol table to that parser.
    public static final SymbolTable fSymbolTable = new SymbolTable();

    // xmlns and schema namespace is also added to the schema symbol table
    public static final String XMLNS                    = fSymbolTable.addSymbol(O_XMLNS);
    public static final String URI_SCHEMAFORSCHEMA      = fSymbolTable.addSymbol(OURI_SCHEMAFORSCHEMA);

    // all possible schema element names
    public static final String ELT_ALL                  = fSymbolTable.addSymbol("all");
    public static final String ELT_ANNOTATION           = fSymbolTable.addSymbol("annotation");
    public static final String ELT_ANY                  = fSymbolTable.addSymbol("any");
    public static final String ELT_ANYATTRIBUTE         = fSymbolTable.addSymbol("anyAttribute");
    public static final String ELT_APPINFO              = fSymbolTable.addSymbol("appinfo");
    public static final String ELT_ATTRIBUTE            = fSymbolTable.addSymbol("attribute");
    public static final String ELT_ATTRIBUTEGROUP       = fSymbolTable.addSymbol("attributeGroup");
    public static final String ELT_CHOICE               = fSymbolTable.addSymbol("choice");
    public static final String ELT_COMPLEXCONTENT       = fSymbolTable.addSymbol("complexContent");
    public static final String ELT_COMPLEXTYPE          = fSymbolTable.addSymbol("complexType");
    public static final String ELT_DOCUMENTATION        = fSymbolTable.addSymbol("documentation");
    public static final String ELT_ELEMENT              = fSymbolTable.addSymbol("element");
    public static final String ELT_ENUMERATION          = fSymbolTable.addSymbol("enumeration");
    public static final String ELT_EXTENSION            = fSymbolTable.addSymbol("extension");
    public static final String ELT_FIELD                = fSymbolTable.addSymbol("field");
    public static final String ELT_FRACTIONDIGITS       = fSymbolTable.addSymbol("fractionDigits");
    public static final String ELT_GROUP                = fSymbolTable.addSymbol("group");
    public static final String ELT_IMPORT               = fSymbolTable.addSymbol("import");
    public static final String ELT_INCLUDE              = fSymbolTable.addSymbol("include");
    public static final String ELT_KEY                  = fSymbolTable.addSymbol("key");
    public static final String ELT_KEYREF               = fSymbolTable.addSymbol("keyref");
    public static final String ELT_LENGTH               = fSymbolTable.addSymbol("length");
    public static final String ELT_LIST                 = fSymbolTable.addSymbol("list");
    public static final String ELT_MAXEXCLUSIVE         = fSymbolTable.addSymbol("maxExclusive");
    public static final String ELT_MAXINCLUSIVE         = fSymbolTable.addSymbol("maxInclusive");
    public static final String ELT_MAXLENGTH            = fSymbolTable.addSymbol("maxLength");
    public static final String ELT_MINEXCLUSIVE         = fSymbolTable.addSymbol("minExclusive");
    public static final String ELT_MININCLUSIVE         = fSymbolTable.addSymbol("minInclusive");
    public static final String ELT_MINLENGTH            = fSymbolTable.addSymbol("minLength");
    public static final String ELT_NOTATION             = fSymbolTable.addSymbol("notation");
    public static final String ELT_PATTERN              = fSymbolTable.addSymbol("pattern");
    public static final String ELT_REDEFINE             = fSymbolTable.addSymbol("redefine");
    public static final String ELT_RESTRICTION          = fSymbolTable.addSymbol("restriction");
    public static final String ELT_SCHEMA               = fSymbolTable.addSymbol("schema");
    public static final String ELT_SELECTOR             = fSymbolTable.addSymbol("selector");
    public static final String ELT_SEQUENCE             = fSymbolTable.addSymbol("sequence");
    public static final String ELT_SIMPLECONTENT        = fSymbolTable.addSymbol("simpleContent");
    public static final String ELT_SIMPLETYPE           = fSymbolTable.addSymbol("simpleType");
    public static final String ELT_TOTALDIGITS          = fSymbolTable.addSymbol("totalDigits");
    public static final String ELT_UNION                = fSymbolTable.addSymbol("union");
    public static final String ELT_UNIQUE               = fSymbolTable.addSymbol("unique");
    public static final String ELT_WHITESPACE           = fSymbolTable.addSymbol("whiteSpace");

    // all possible schema attribute names
    public static final String ATT_ABSTRACT             = fSymbolTable.addSymbol("abstract");
    public static final String ATT_ATTRIBUTEFORMDEFAULT = fSymbolTable.addSymbol("attributeFormDefault");
    public static final String ATT_BASE                 = fSymbolTable.addSymbol("base");
    public static final String ATT_BLOCK                = fSymbolTable.addSymbol("block");
    public static final String ATT_BLOCKDEFAULT         = fSymbolTable.addSymbol("blockDefault");
    public static final String ATT_DEFAULT              = fSymbolTable.addSymbol("default");
    public static final String ATT_ELEMENTFORMDEFAULT   = fSymbolTable.addSymbol("elementFormDefault");
    public static final String ATT_FINAL                = fSymbolTable.addSymbol("final");
    public static final String ATT_FINALDEFAULT         = fSymbolTable.addSymbol("finalDefault");
    public static final String ATT_FIXED                = fSymbolTable.addSymbol("fixed");
    public static final String ATT_FORM                 = fSymbolTable.addSymbol("form");
    public static final String ATT_ID                   = fSymbolTable.addSymbol("id");
    public static final String ATT_ITEMTYPE             = fSymbolTable.addSymbol("itemType");
    public static final String ATT_MAXOCCURS            = fSymbolTable.addSymbol("maxOccurs");
    public static final String ATT_MEMBERTYPES          = fSymbolTable.addSymbol("memberTypes");
    public static final String ATT_MINOCCURS            = fSymbolTable.addSymbol("minOccurs");
    public static final String ATT_MIXED                = fSymbolTable.addSymbol("mixed");
    public static final String ATT_NAME                 = fSymbolTable.addSymbol("name");
    public static final String ATT_NAMESPACE            = fSymbolTable.addSymbol("namespace");
    public static final String ATT_NILLABLE             = fSymbolTable.addSymbol("nillable");
    public static final String ATT_PROCESSCONTENTS      = fSymbolTable.addSymbol("processContents");
    public static final String ATT_REF                  = fSymbolTable.addSymbol("ref");
    public static final String ATT_REFER                = fSymbolTable.addSymbol("refer");
    public static final String ATT_SCHEMALOCATION       = fSymbolTable.addSymbol("schemaLocation");
    public static final String ATT_SOURCE               = fSymbolTable.addSymbol("source");
    public static final String ATT_SUBSTITUTIONGROUP    = fSymbolTable.addSymbol("substitutionGroup");
    public static final String ATT_SYSTEM               = fSymbolTable.addSymbol("system");
    public static final String ATT_PUBLIC               = fSymbolTable.addSymbol("public");
    public static final String ATT_TARGETNAMESPACE      = fSymbolTable.addSymbol("targetNamespace");
    public static final String ATT_TYPE                 = fSymbolTable.addSymbol("type");
    public static final String ATT_USE                  = fSymbolTable.addSymbol("use");
    public static final String ATT_VALUE                = fSymbolTable.addSymbol("value");
    public static final String ATT_VERSION              = fSymbolTable.addSymbol("version");
    public static final String ATT_XPATH                = fSymbolTable.addSymbol("xpath");

    // all possible schema attribute values
    public static final String ATTVAL_TWOPOUNDANY       = "##any";
    public static final String ATTVAL_TWOPOUNDLOCAL     = "##local";
    public static final String ATTVAL_TWOPOUNDOTHER     = "##other";
    public static final String ATTVAL_TWOPOUNDTARGETNS  = "##targetNamespace";
    public static final String ATTVAL_POUNDALL          = "#all";
    public static final String ATTVAL_FALSE_0           = "0";
    public static final String ATTVAL_TRUE_1            = "1";
    public static final String ATTVAL_ANYSIMPLETYPE     = "anySimpleType";
    public static final String ATTVAL_ANYTYPE           = "anyType";
    public static final String ATTVAL_ANYURI            = "anyURI";
    public static final String ATTVAL_BASE64BINARY      = "base64Binary";
    public static final String ATTVAL_BOOLEAN           = "boolean";
    public static final String ATTVAL_BYTE              = "byte";
    public static final String ATTVAL_COLLAPSE          = "collapse";
    public static final String ATTVAL_DATE              = "date";
    public static final String ATTVAL_DATETIME          = "dateTime";
    public static final String ATTVAL_DAY               = "gDay";
    public static final String ATTVAL_DECIMAL           = "decimal";
    public static final String ATTVAL_DOUBLE            = "double";
    public static final String ATTVAL_DURATION          = "duration";
    public static final String ATTVAL_ENTITY            = "ENTITY";
    public static final String ATTVAL_ENTITIES          = "ENTITIES";
    public static final String ATTVAL_EXTENSION         = "extension";
    public static final String ATTVAL_FALSE             = "false";
    public static final String ATTVAL_FLOAT             = "float";
    public static final String ATTVAL_HEXBINARY         = "hexBinary";
    public static final String ATTVAL_ID                = "ID";
    public static final String ATTVAL_IDREF             = "IDREF";
    public static final String ATTVAL_IDREFS            = "IDREFS";
    public static final String ATTVAL_INT               = "int";
    public static final String ATTVAL_INTEGER           = "integer";
    public static final String ATTVAL_LANGUAGE          = "language";
    public static final String ATTVAL_LAX               = "lax";
    public static final String ATTVAL_LIST              = "list";
    public static final String ATTVAL_LONG              = "long";
    public static final String ATTVAL_NAME              = "name";
    public static final String ATTVAL_NEGATIVEINTEGER   = "negativeInteger";
    public static final String ATTVAL_MONTH             = "gMonth";
    public static final String ATTVAL_MONTHDAY          = "gMonthDay";
    public static final String ATTVAL_NCNAME            = "NCName";
    public static final String ATTVAL_NMTOKEN           = "NMTOKEN";
    public static final String ATTVAL_NMTOKENS          = "NMTOKENS";
    public static final String ATTVAL_NONNEGATIVEINTEGER= "nonNegativeInteger";
    public static final String ATTVAL_NONPOSITIVEINTEGER= "nonPositiveInteger";
    public static final String ATTVAL_NORMALIZEDSTRING  = "normalizedString";
    public static final String ATTVAL_NOTATION          = "NOTATION";
    public static final String ATTVAL_OPTIONAL          = "optional";
    public static final String ATTVAL_POSITIVEINTEGER   = "positiveInteger";
    public static final String ATTVAL_PRESERVE          = "preserve";
    public static final String ATTVAL_PROHIBITED        = "prohibited";
    public static final String ATTVAL_QNAME             = "QName";
    public static final String ATTVAL_QUALIFIED         = "qualified";
    public static final String ATTVAL_REPLACE           = "replace";
    public static final String ATTVAL_REQUIRED          = "required";
    public static final String ATTVAL_RESTRICTION       = "restriction";
    public static final String ATTVAL_SHORT             = "short";
    public static final String ATTVAL_SKIP              = "skip";
    public static final String ATTVAL_STRICT            = "strict";
    public static final String ATTVAL_STRING            = "string";
    public static final String ATTVAL_SUBSTITUTION      = "substitution";
    public static final String ATTVAL_TIME              = "time";
    public static final String ATTVAL_TOKEN             = "token";
    public static final String ATTVAL_TRUE              = "true";
    public static final String ATTVAL_UNBOUNDED         = "unbounded";
    public static final String ATTVAL_UNION             = "union";
    public static final String ATTVAL_UNQUALIFIED       = "unqualified";
    public static final String ATTVAL_UNSIGNEDBYTE      = "unsignedByte";
    public static final String ATTVAL_UNSIGNEDINT       = "unsignedInt";
    public static final String ATTVAL_UNSIGNEDLONG      = "unsignedLong";
    public static final String ATTVAL_UNSIGNEDSHORT     = "unsignedShort";
    public static final String ATTVAL_YEAR              = "gYear";
    public static final String ATTVAL_YEARMONTH         = "gYearMonth";

    // block/final values
    public static final short EMPTY_SET    = 0;
    public static final short EXTENSION    = 1;
    public static final short RESTRICTION  = 2;
    public static final short UNION        = 4;
    public static final short LIST         = 8;
    public static final short ENUMERATION  = 16;
    public static final short SUBSTITUTION = 32;

    // form qualified/unqualified
    public static final short FORM_UNQUALIFIED = 0;
    public static final short FORM_QUALIFIED   = 1;

    // any: processContents
    public static final short ANY_STRICT = 0;
    public static final short ANY_LAX    = 1;
    public static final short ANY_SKIP   = 2;

    // attribute use
    public static final short USE_OPTIONAL   = 0;
    public static final short USE_REQUIRED   = 1;
    public static final short USE_PROHIBITED = 2;

    // whiteSpace
    public static final short WS_PRESERVE = 0;
    public static final short WS_REPLACE  = 1;
    public static final short WS_COLLAPSE = 2;

    // maxOccurs = "unbounded"
   public static final int OCCURRENCE_UNBOUNDED = -1;


    /**
     * Shadowed symbol table. For schema document use.
     *
     * @author Andy Clark, IBM
     */
    public static final class SchemaSymbolTable extends SymbolTable {

        //
        // Data
        //

        /** Main symbol table. */
        protected SymbolTable fSymbolTable = SchemaSymbols.fSymbolTable;

        //
        // Constructors
        //

        //
        // SymbolTable methods
        //

        /**
         * Adds the specified symbol to the symbol table and returns a
         * reference to the unique symbol. If the symbol already exists,
         * the previous symbol reference is returned instead, in order
         * guarantee that symbol references remain unique.
         *
         * @param symbol The new symbol.
         */
        public String addSymbol(String symbol) {

            if (fSymbolTable.containsSymbol(symbol)) {
                return fSymbolTable.addSymbol(symbol);
            }
            return super.addSymbol(symbol);

        } // addSymbol(String)

        /**
         * Adds the specified symbol to the symbol table and returns a
         * reference to the unique symbol. If the symbol already exists,
         * the previous symbol reference is returned instead, in order
         * guarantee that symbol references remain unique.
         *
         * @param buffer The buffer containing the new symbol.
         * @param offset The offset into the buffer of the new symbol.
         * @param length The length of the new symbol in the buffer.
         */
        public String addSymbol(char[] buffer, int offset, int length) {

            if (fSymbolTable.containsSymbol(buffer, offset, length)) {
                return fSymbolTable.addSymbol(buffer, offset, length);
            }
            return super.addSymbol(buffer, offset, length);

        } // addSymbol(char[],int,int):String

        /**
         * Returns a hashcode value for the specified symbol. The value
         * returned by this method must be identical to the value returned
         * by the <code>hash(char[],int,int)</code> method when called
         * with the character array that comprises the symbol string.
         *
         * @param symbol The symbol to hash.
         */
        public int hash(String symbol) {
            return fSymbolTable.hash(symbol);
        } // hash(String):int

        /**
         * Returns a hashcode value for the specified symbol information.
         * The value returned by this method must be identical to the value
         * returned by the <code>hash(String)</code> method when called
         * with the string object created from the symbol information.
         *
         * @param buffer The character buffer containing the symbol.
         * @param offset The offset into the character buffer of the start
         *               of the symbol.
         * @param length The length of the symbol.
         */
        public int hash(char[] buffer, int offset, int length) {
            return fSymbolTable.hash(buffer, offset, length);
        } // hash(char[],int,int):int

    } // class ShadowedSymbolTable

}
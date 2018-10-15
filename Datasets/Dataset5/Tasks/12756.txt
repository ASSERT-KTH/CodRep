DatatypeValidator dv = (DatatypeValidator)sGrammar.getTypeDecl(tempAttrDecl.fTypeIdx);

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

import java.util.*;
import org.w3c.dom.*;
import org.apache.xerces.impl.v2.datatypes.*;
import org.apache.xerces.impl.XMLErrorReporter;
import org.apache.xerces.util.DOMUtil;
import org.apache.xerces.xni.QName;
/*import org.apache.xerces.validators.common.XMLAttributeDecl;
import org.apache.xerces.validators.common.GrammarResolver;
import org.apache.xerces.validators.common.Grammar;
*/

/**
 * Class <code>XSAttributeCheck</code> is used to check the validity of attributes
 * appearing in the schema document. It
 * - reports an error for invalid element (invalid namespace, invalid name)
 * - reports an error for invalid attribute (invalid namespace, invalid name)
 * - reports an error for invalid attribute value
 * - return compiled values for attriute values
 * - provide default value for missing optional attributes
 * - provide default value for incorrect attribute values
 *
 * But it's the caller's responsibility to check whether a required attribute
 * is present.
 *
 * Things need revisiting:
 * - Whether to return non-schema attributes/values
 * - We need NamespaceScope to generate QName
 * - Do we need to update NamespaceScope and ErrorReporter when reset()?
 * - Should have the datatype validators return compiled value
 * - Should return compiled form for wildcard namespace
 *
 * @version $Id$
 */

public class XSAttributeChecker {

    public static       int ATTIDX_COUNT           = 0;
    public static final int ATTIDX_ABSTRACT        = ATTIDX_COUNT++;
    public static final int ATTIDX_AFORMDEFAULT    = ATTIDX_COUNT++;
    public static final int ATTIDX_BASE            = ATTIDX_COUNT++;
    public static final int ATTIDX_BLOCK           = ATTIDX_COUNT++;
    public static final int ATTIDX_BLOCKDEFAULT    = ATTIDX_COUNT++;
    public static final int ATTIDX_DEFAULT         = ATTIDX_COUNT++;
    public static final int ATTIDX_EFORMDEFAULT    = ATTIDX_COUNT++;
    public static final int ATTIDX_FINAL           = ATTIDX_COUNT++;
    public static final int ATTIDX_FINALDEFAULT    = ATTIDX_COUNT++;
    public static final int ATTIDX_FIXED           = ATTIDX_COUNT++;
    public static final int ATTIDX_FORM            = ATTIDX_COUNT++;
    public static final int ATTIDX_ID              = ATTIDX_COUNT++;
    public static final int ATTIDX_ITEMTYPE        = ATTIDX_COUNT++;
    public static final int ATTIDX_MAXOCCURS       = ATTIDX_COUNT++;
    public static final int ATTIDX_MEMBERTYPES     = ATTIDX_COUNT++;
    public static final int ATTIDX_MINOCCURS       = ATTIDX_COUNT++;
    public static final int ATTIDX_MIXED           = ATTIDX_COUNT++;
    public static final int ATTIDX_NAME            = ATTIDX_COUNT++;
    public static final int ATTIDX_NAMESPACE       = ATTIDX_COUNT++;
    public static final int ATTIDX_NILLABLE        = ATTIDX_COUNT++;
    public static final int ATTIDX_PROCESSCONTENTS = ATTIDX_COUNT++;
    public static final int ATTIDX_PUBLIC          = ATTIDX_COUNT++;
    public static final int ATTIDX_REF             = ATTIDX_COUNT++;
    public static final int ATTIDX_REFER           = ATTIDX_COUNT++;
    public static final int ATTIDX_SCHEMALOCATION  = ATTIDX_COUNT++;
    public static final int ATTIDX_SOURCE          = ATTIDX_COUNT++;
    public static final int ATTIDX_SUBSGROUP       = ATTIDX_COUNT++;
    public static final int ATTIDX_SYSTEM          = ATTIDX_COUNT++;
    public static final int ATTIDX_TARGETNAMESPACE = ATTIDX_COUNT++;
    public static final int ATTIDX_TYPE            = ATTIDX_COUNT++;
    public static final int ATTIDX_USE             = ATTIDX_COUNT++;
    public static final int ATTIDX_VALUE           = ATTIDX_COUNT++;
    public static final int ATTIDX_VERSION         = ATTIDX_COUNT++;
    public static final int ATTIDX_XPATH           = ATTIDX_COUNT++;
    public static final int ATTIDX_FROMDEFAULT     = ATTIDX_COUNT++;
    //public static final int ATTIDX_OTHERVALUES     = ATTIDX_COUNT++;
    public static final int ATTIDX_ISRETURNED      = ATTIDX_COUNT++;

    // constants to return
    private static Integer[] INT_CONSTANTS    = {new Integer(0),
                                                 new Integer(1),
                                                 new Integer(2)};
    private static Integer INT_ZERO           = INT_CONSTANTS[0];
    private static Integer INT_ONE            = INT_CONSTANTS[1];
    private static Integer INT_QUALIFIED      = INT_CONSTANTS[SchemaSymbols.FORM_QUALIFIED];
    private static Integer INT_UNQUALIFIED    = INT_CONSTANTS[SchemaSymbols.FORM_UNQUALIFIED];
    private static Integer INT_EMPTY_SET      = INT_CONSTANTS[SchemaSymbols.EMPTY_SET];
    private static Integer INT_ANY_STRICT     = INT_CONSTANTS[SchemaSymbols.ANY_STRICT];
    private static Integer INT_ANY_LAX        = INT_CONSTANTS[SchemaSymbols.ANY_LAX];
    private static Integer INT_ANY_SKIP       = INT_CONSTANTS[SchemaSymbols.ANY_SKIP];
    private static Integer INT_USE_OPTIONAL   = INT_CONSTANTS[SchemaSymbols.USE_OPTIONAL];
    private static Integer INT_USE_REQUIRED   = INT_CONSTANTS[SchemaSymbols.USE_REQUIRED];
    private static Integer INT_USE_PROHIBITED = INT_CONSTANTS[SchemaSymbols.USE_PROHIBITED];
    private static Integer INT_WS_PRESERVE    = INT_CONSTANTS[SchemaSymbols.WS_PRESERVE];
    private static Integer INT_WS_REPLACE     = INT_CONSTANTS[SchemaSymbols.WS_REPLACE];
    private static Integer INT_WS_COLLAPSE    = INT_CONSTANTS[SchemaSymbols.WS_COLLAPSE];
    private static Integer INT_UNBOUNDED      = new Integer(SchemaSymbols.OCCURRENCE_UNBOUNDED);

    // the prefix to distinguish gloval vs. local; name vs. ref
    protected static String PRE_GLOBAL      = "G_";
    protected static String PRE_LOC_NAME    = "LN_";
    protected static String PRE_LOC_REF     = "LR_";

    // used to store the map from element name to attribute list
    protected static Hashtable fEleAttrsMap = new Hashtable();

    // used to initialize fEleAttrsMap
    // step 1: all possible data types
    // DT_??? >= 0 : validate using a validator, which is initialized staticly
    // DT_??? <  0 : validate directly, which is done in "validate()"

    protected static final int DT_ANYURI           = 0;
    protected static final int DT_BOOLEAN          = 1;
    protected static final int DT_ID               = 2;
    protected static final int DT_NONNEGINT        = 3;
    protected static final int DT_QNAME            = 4;
    protected static final int DT_STRING           = 5;
    protected static final int DT_TOKEN            = 6;
    protected static final int DT_NCNAME           = 7;
    protected static final int DT_XPATH            = 8;
    protected static final int DT_XPATH1           = 9;

    // used to store extra datatype validators
    protected static final int DT_COUNT            = DT_XPATH1 + 1;
    protected static DatatypeValidator[] fExtraDVs = new DatatypeValidator[DT_COUNT];
    static {
        // step 5: register all datatype validators for new types
        SchemaGrammar grammar = SchemaGrammar.SG_SchemaNS;
        // anyURI
        fExtraDVs[DT_ANYURI] = (DatatypeValidator)grammar.getTypeDecl(SchemaSymbols.ATTVAL_ANYURI);
        // boolean
        fExtraDVs[DT_BOOLEAN] = (DatatypeValidator)grammar.getTypeDecl(SchemaSymbols.ATTVAL_BOOLEAN);
        // ID
        fExtraDVs[DT_ID] = (DatatypeValidator)grammar.getTypeDecl(SchemaSymbols.ATTVAL_ID);
        // nonNegtiveInteger
        fExtraDVs[DT_NONNEGINT] = (DatatypeValidator)grammar.getTypeDecl(SchemaSymbols.ATTVAL_NONNEGATIVEINTEGER);
        // QName
        fExtraDVs[DT_QNAME] = (DatatypeValidator)grammar.getTypeDecl(SchemaSymbols.ATTVAL_QNAME);
        // string
        fExtraDVs[DT_STRING] = (DatatypeValidator)grammar.getTypeDecl(SchemaSymbols.ATTVAL_STRING);
        // token
        fExtraDVs[DT_TOKEN] = (DatatypeValidator)grammar.getTypeDecl(SchemaSymbols.ATTVAL_TOKEN);
        // NCName
        fExtraDVs[DT_NCNAME] = (DatatypeValidator)grammar.getTypeDecl(SchemaSymbols.ATTVAL_NCNAME);
        // xpath = a subset of XPath expression
        fExtraDVs[DT_XPATH] = fExtraDVs[DT_STRING];
        // xpath = a subset of XPath expression
        fExtraDVs[DT_XPATH] = fExtraDVs[DT_STRING];
    }

    protected static final int DT_BLOCK            = -1;
    protected static final int DT_BLOCK1           = -2;
    protected static final int DT_FINAL            = -3;
    protected static final int DT_FINAL1           = -4;
    protected static final int DT_FORM             = -5;
    protected static final int DT_MAXOCCURS        = -6;
    protected static final int DT_MAXOCCURS1       = -7;
    protected static final int DT_MEMBERTYPES      = -8;
    protected static final int DT_MINOCCURS1       = -9;
    protected static final int DT_NAMESPACE        = -10;
    protected static final int DT_PROCESSCONTENTS  = -11;
    protected static final int DT_PUBLIC           = -12;
    protected static final int DT_USE              = -13;
    protected static final int DT_WHITESPACE       = -14;

    static {
        // step 2: all possible attributes for all elements
        int attCount = 0;
        int ATT_ABSTRACT_D          = attCount++;
        int ATT_ATTRIBUTE_FD_D      = attCount++;
        int ATT_BASE_R              = attCount++;
        int ATT_BASE_N              = attCount++;
        int ATT_BLOCK_N             = attCount++;
        int ATT_BLOCK1_N            = attCount++;
        int ATT_BLOCK_D_D           = attCount++;
        int ATT_DEFAULT_N           = attCount++;
        int ATT_ELEMENT_FD_D        = attCount++;
        int ATT_FINAL_N             = attCount++;
        int ATT_FINAL1_N            = attCount++;
        int ATT_FINAL_D_D           = attCount++;
        int ATT_FIXED_N             = attCount++;
        int ATT_FIXED_D             = attCount++;
        int ATT_FORM_N              = attCount++;
        int ATT_ID_N                = attCount++;
        int ATT_ITEMTYPE_N          = attCount++;
        int ATT_MAXOCCURS_D         = attCount++;
        int ATT_MAXOCCURS1_D        = attCount++;
        int ATT_MEMBER_T_N          = attCount++;
        int ATT_MINOCCURS_D         = attCount++;
        int ATT_MINOCCURS1_D        = attCount++;
        int ATT_MIXED_D             = attCount++;
        int ATT_MIXED_N             = attCount++;
        int ATT_NAME_R              = attCount++;
        int ATT_NAMESPACE_D         = attCount++;
        int ATT_NAMESPACE_N         = attCount++;
        int ATT_NILLABLE_D          = attCount++;
        int ATT_PROCESS_C_D         = attCount++;
        int ATT_PUBLIC_R            = attCount++;
        int ATT_REF_R               = attCount++;
        int ATT_REFER_R             = attCount++;
        int ATT_SCHEMA_L_R          = attCount++;
        int ATT_SCHEMA_L_N          = attCount++;
        int ATT_SOURCE_N            = attCount++;
        int ATT_SUBSTITUTION_G_N    = attCount++;
        int ATT_SYSTEM_N            = attCount++;
        int ATT_TARGET_N_N          = attCount++;
        int ATT_TYPE_N              = attCount++;
        int ATT_USE_D               = attCount++;
        int ATT_VALUE_NNI_N         = attCount++;
        int ATT_VALUE_STR_N         = attCount++;
        int ATT_VALUE_WS_N          = attCount++;
        int ATT_VERSION_N           = attCount++;
        int ATT_XPATH_R             = attCount++;
        int ATT_XPATH1_R            = attCount++;

        // step 3: store all these attributes in an array
        OneAttr[] allAttrs = new OneAttr[attCount];
        allAttrs[ATT_ABSTRACT_D]        =   new OneAttr(SchemaSymbols.ATT_ABSTRACT,
                                                        DT_BOOLEAN,
                                                        ATTIDX_ABSTRACT,
                                                        Boolean.FALSE);
        allAttrs[ATT_ATTRIBUTE_FD_D]    =   new OneAttr(SchemaSymbols.ATT_ATTRIBUTEFORMDEFAULT,
                                                        DT_FORM,
                                                        ATTIDX_AFORMDEFAULT,
                                                        INT_UNQUALIFIED);
        allAttrs[ATT_BASE_R]            =   new OneAttr(SchemaSymbols.ATT_BASE,
                                                        DT_QNAME,
                                                        ATTIDX_BASE,
                                                        null);
        allAttrs[ATT_BASE_N]            =   new OneAttr(SchemaSymbols.ATT_BASE,
                                                        DT_QNAME,
                                                        ATTIDX_BASE,
                                                        null);
        allAttrs[ATT_BLOCK_N]           =   new OneAttr(SchemaSymbols.ATT_BLOCK,
                                                        DT_BLOCK,
                                                        ATTIDX_BLOCK,
                                                        null);
        allAttrs[ATT_BLOCK1_N]          =   new OneAttr(SchemaSymbols.ATT_BLOCK,
                                                        DT_BLOCK1,
                                                        ATTIDX_BLOCK,
                                                        null);
        allAttrs[ATT_BLOCK_D_D]         =   new OneAttr(SchemaSymbols.ATT_BLOCKDEFAULT,
                                                        DT_BLOCK,
                                                        ATTIDX_BLOCKDEFAULT,
                                                        INT_EMPTY_SET);
        allAttrs[ATT_DEFAULT_N]         =   new OneAttr(SchemaSymbols.ATT_DEFAULT,
                                                        DT_STRING,
                                                        ATTIDX_DEFAULT,
                                                        null);
        allAttrs[ATT_ELEMENT_FD_D]      =   new OneAttr(SchemaSymbols.ATT_ELEMENTFORMDEFAULT,
                                                        DT_FORM,
                                                        ATTIDX_EFORMDEFAULT,
                                                        INT_UNQUALIFIED);
        allAttrs[ATT_FINAL_N]           =   new OneAttr(SchemaSymbols.ATT_FINAL,
                                                        DT_FINAL,
                                                        ATTIDX_FINAL,
                                                        null);
        allAttrs[ATT_FINAL1_N]          =   new OneAttr(SchemaSymbols.ATT_FINAL,
                                                        DT_FINAL1,
                                                        ATTIDX_FINAL,
                                                        null);
        allAttrs[ATT_FINAL_D_D]         =   new OneAttr(SchemaSymbols.ATT_FINALDEFAULT,
                                                        DT_FINAL,
                                                        ATTIDX_FINALDEFAULT,
                                                        INT_EMPTY_SET);
        allAttrs[ATT_FIXED_N]           =   new OneAttr(SchemaSymbols.ATT_FIXED,
                                                        DT_STRING,
                                                        ATTIDX_FIXED,
                                                        null);
        allAttrs[ATT_FIXED_D]           =   new OneAttr(SchemaSymbols.ATT_FIXED,
                                                        DT_BOOLEAN,
                                                        ATTIDX_FIXED,
                                                        Boolean.FALSE);
        allAttrs[ATT_FORM_N]            =   new OneAttr(SchemaSymbols.ATT_FORM,
                                                        DT_FORM,
                                                        ATTIDX_FORM,
                                                        null);
        allAttrs[ATT_ID_N]              =   new OneAttr(SchemaSymbols.ATT_ID,
                                                        DT_ID,
                                                        ATTIDX_ID,
                                                        null);
        allAttrs[ATT_ITEMTYPE_N]        =   new OneAttr(SchemaSymbols.ATT_ITEMTYPE,
                                                        DT_QNAME,
                                                        ATTIDX_ITEMTYPE,
                                                        null);
        allAttrs[ATT_MAXOCCURS_D]       =   new OneAttr(SchemaSymbols.ATT_MAXOCCURS,
                                                        DT_MAXOCCURS,
                                                        ATTIDX_MAXOCCURS,
                                                        INT_ONE);
        allAttrs[ATT_MAXOCCURS1_D]      =   new OneAttr(SchemaSymbols.ATT_MAXOCCURS,
                                                        DT_MAXOCCURS1,
                                                        ATTIDX_MAXOCCURS,
                                                        INT_ONE);
        allAttrs[ATT_MEMBER_T_N]        =   new OneAttr(SchemaSymbols.ATT_MEMBERTYPES,
                                                        DT_MEMBERTYPES,
                                                        ATTIDX_MEMBERTYPES,
                                                        null);
        allAttrs[ATT_MINOCCURS_D]       =   new OneAttr(SchemaSymbols.ATT_MINOCCURS,
                                                        DT_NONNEGINT,
                                                        ATTIDX_MINOCCURS,
                                                        INT_ONE);
        allAttrs[ATT_MINOCCURS1_D]      =   new OneAttr(SchemaSymbols.ATT_MINOCCURS,
                                                        DT_MINOCCURS1,
                                                        ATTIDX_MINOCCURS,
                                                        INT_ONE);
        allAttrs[ATT_MIXED_D]           =   new OneAttr(SchemaSymbols.ATT_MIXED,
                                                        DT_BOOLEAN,
                                                        ATTIDX_MIXED,
                                                        Boolean.FALSE);
        allAttrs[ATT_MIXED_N]           =   new OneAttr(SchemaSymbols.ATT_MIXED,
                                                        DT_BOOLEAN,
                                                        ATTIDX_MIXED,
                                                        null);
        allAttrs[ATT_NAME_R]            =   new OneAttr(SchemaSymbols.ATT_NAME,
                                                        DT_NCNAME,
                                                        ATTIDX_NAME,
                                                        null);
        allAttrs[ATT_NAMESPACE_D]       =   new OneAttr(SchemaSymbols.ATT_NAMESPACE,
                                                        DT_NAMESPACE,
                                                        ATTIDX_NAMESPACE,
                                                        SchemaSymbols.ATTVAL_TWOPOUNDANY);
        allAttrs[ATT_NAMESPACE_N]       =   new OneAttr(SchemaSymbols.ATT_NAMESPACE,
                                                        DT_ANYURI,
                                                        ATTIDX_NAMESPACE,
                                                        null);
        allAttrs[ATT_NILLABLE_D]        =   new OneAttr(SchemaSymbols.ATT_NILLABLE,
                                                        DT_BOOLEAN,
                                                        ATTIDX_NILLABLE,
                                                        Boolean.FALSE);
        allAttrs[ATT_PROCESS_C_D]       =   new OneAttr(SchemaSymbols.ATT_PROCESSCONTENTS,
                                                        DT_PROCESSCONTENTS,
                                                        ATTIDX_PROCESSCONTENTS,
                                                        INT_ANY_STRICT);
        allAttrs[ATT_PUBLIC_R]          =   new OneAttr(SchemaSymbols.ATT_PUBLIC,
                                                        DT_PUBLIC,
                                                        ATTIDX_PUBLIC,
                                                        null);
        allAttrs[ATT_REF_R]             =   new OneAttr(SchemaSymbols.ATT_REF,
                                                        DT_QNAME,
                                                        ATTIDX_REF,
                                                        null);
        allAttrs[ATT_REFER_R]           =   new OneAttr(SchemaSymbols.ATT_REFER,
                                                        DT_QNAME,
                                                        ATTIDX_REFER,
                                                        null);
        allAttrs[ATT_SCHEMA_L_R]        =   new OneAttr(SchemaSymbols.ATT_SCHEMALOCATION,
                                                        DT_ANYURI,
                                                        ATTIDX_SCHEMALOCATION,
                                                        null);
        allAttrs[ATT_SCHEMA_L_N]        =   new OneAttr(SchemaSymbols.ATT_SCHEMALOCATION,
                                                        DT_ANYURI,
                                                        ATTIDX_SCHEMALOCATION,
                                                        null);
        allAttrs[ATT_SOURCE_N]          =   new OneAttr(SchemaSymbols.ATT_SOURCE,
                                                        DT_ANYURI,
                                                        ATTIDX_SOURCE,
                                                        null);
        allAttrs[ATT_SUBSTITUTION_G_N]  =   new OneAttr(SchemaSymbols.ATT_SUBSTITUTIONGROUP,
                                                        DT_QNAME,
                                                        ATTIDX_SUBSGROUP,
                                                        null);
        allAttrs[ATT_SYSTEM_N]          =   new OneAttr(SchemaSymbols.ATT_SYSTEM,
                                                        DT_ANYURI,
                                                        ATTIDX_SYSTEM,
                                                        null);
        allAttrs[ATT_TARGET_N_N]        =   new OneAttr(SchemaSymbols.ATT_TARGETNAMESPACE,
                                                        DT_ANYURI,
                                                        ATTIDX_TARGETNAMESPACE,
                                                        null);
        allAttrs[ATT_TYPE_N]            =   new OneAttr(SchemaSymbols.ATT_TYPE,
                                                        DT_QNAME,
                                                        ATTIDX_TYPE,
                                                        null);
        allAttrs[ATT_USE_D]             =   new OneAttr(SchemaSymbols.ATT_USE,
                                                        DT_USE,
                                                        ATTIDX_USE,
                                                        INT_USE_OPTIONAL);
        allAttrs[ATT_VALUE_NNI_N]       =   new OneAttr(SchemaSymbols.ATT_VALUE,
                                                        DT_NONNEGINT,
                                                        ATTIDX_VALUE,
                                                        null);
        allAttrs[ATT_VALUE_STR_N]       =   new OneAttr(SchemaSymbols.ATT_VALUE,
                                                        DT_STRING,
                                                        ATTIDX_VALUE,
                                                        null);
        allAttrs[ATT_VALUE_WS_N]        =   new OneAttr(SchemaSymbols.ATT_VALUE,
                                                        DT_WHITESPACE,
                                                        ATTIDX_VALUE,
                                                        null);
        allAttrs[ATT_VERSION_N]         =   new OneAttr(SchemaSymbols.ATT_VERSION,
                                                        DT_TOKEN,
                                                        ATTIDX_VERSION,
                                                        null);
        allAttrs[ATT_XPATH_R]           =   new OneAttr(SchemaSymbols.ATT_XPATH,
                                                        DT_XPATH,
                                                        ATTIDX_XPATH,
                                                        null);
        allAttrs[ATT_XPATH1_R]          =   new OneAttr(SchemaSymbols.ATT_XPATH,
                                                        DT_XPATH1,
                                                        ATTIDX_XPATH,
                                                        null);

        // step 4: for each element, make a list of possible attributes
        Hashtable attrList;
        OneElement oneEle;

        // for element "attribute" - global
        attrList = new Hashtable();
        // default = string
        attrList.put(SchemaSymbols.ATT_DEFAULT, allAttrs[ATT_DEFAULT_N]);
        // fixed = string
        attrList.put(SchemaSymbols.ATT_FIXED, allAttrs[ATT_FIXED_N]);
        // id = ID
        attrList.put(SchemaSymbols.ATT_ID, allAttrs[ATT_ID_N]);
        // name = NCName
        attrList.put(SchemaSymbols.ATT_NAME, allAttrs[ATT_NAME_R]);
        // type = QName
        attrList.put(SchemaSymbols.ATT_TYPE, allAttrs[ATT_TYPE_N]);
        oneEle = new OneElement (attrList);
        fEleAttrsMap.put(PRE_GLOBAL+SchemaSymbols.ELT_ATTRIBUTE, oneEle);

        // for element "attribute" - local name
        attrList = new Hashtable();
        // default = string
        attrList.put(SchemaSymbols.ATT_DEFAULT, allAttrs[ATT_DEFAULT_N]);
        // fixed = string
        attrList.put(SchemaSymbols.ATT_FIXED, allAttrs[ATT_FIXED_N]);
        // form = (qualified | unqualified)
        attrList.put(SchemaSymbols.ATT_FORM, allAttrs[ATT_FORM_N]);
        // id = ID
        attrList.put(SchemaSymbols.ATT_ID, allAttrs[ATT_ID_N]);
        // name = NCName
        attrList.put(SchemaSymbols.ATT_NAME, allAttrs[ATT_NAME_R]);
        // type = QName
        attrList.put(SchemaSymbols.ATT_TYPE, allAttrs[ATT_TYPE_N]);
        // use = (optional | prohibited | required) : optional
        attrList.put(SchemaSymbols.ATT_USE, allAttrs[ATT_USE_D]);
        oneEle = new OneElement (attrList);
        fEleAttrsMap.put(PRE_LOC_NAME+SchemaSymbols.ELT_ATTRIBUTE, oneEle);

        // for element "attribute" - local ref
        attrList = new Hashtable();
        // default = string
        attrList.put(SchemaSymbols.ATT_DEFAULT, allAttrs[ATT_DEFAULT_N]);
        // fixed = string
        attrList.put(SchemaSymbols.ATT_FIXED, allAttrs[ATT_FIXED_N]);
        // id = ID
        attrList.put(SchemaSymbols.ATT_ID, allAttrs[ATT_ID_N]);
        // ref = QName
        attrList.put(SchemaSymbols.ATT_REF, allAttrs[ATT_REF_R]);
        // use = (optional | prohibited | required) : optional
        attrList.put(SchemaSymbols.ATT_USE, allAttrs[ATT_USE_D]);
        oneEle = new OneElement (attrList);
        fEleAttrsMap.put(PRE_LOC_REF+SchemaSymbols.ELT_ATTRIBUTE, oneEle);

        // for element "element" - global
        attrList = new Hashtable();
        // abstract = boolean : false
        attrList.put(SchemaSymbols.ATT_ABSTRACT, allAttrs[ATT_ABSTRACT_D]);
        // block = (#all | List of (substitution | extension | restriction | list | union))
        attrList.put(SchemaSymbols.ATT_BLOCK, allAttrs[ATT_BLOCK_N]);
        // default = string
        attrList.put(SchemaSymbols.ATT_DEFAULT, allAttrs[ATT_DEFAULT_N]);
        // final = (#all | List of (extension | restriction))
        attrList.put(SchemaSymbols.ATT_FINAL, allAttrs[ATT_FINAL_N]);
        // fixed = string
        attrList.put(SchemaSymbols.ATT_FIXED, allAttrs[ATT_FIXED_N]);
        // id = ID
        attrList.put(SchemaSymbols.ATT_ID, allAttrs[ATT_ID_N]);
        // name = NCName
        attrList.put(SchemaSymbols.ATT_NAME, allAttrs[ATT_NAME_R]);
        // nillable = boolean : false
        attrList.put(SchemaSymbols.ATT_NILLABLE, allAttrs[ATT_NILLABLE_D]);
        // substitutionGroup = QName
        attrList.put(SchemaSymbols.ATT_SUBSTITUTIONGROUP, allAttrs[ATT_SUBSTITUTION_G_N]);
        // type = QName
        attrList.put(SchemaSymbols.ATT_TYPE, allAttrs[ATT_TYPE_N]);
        oneEle = new OneElement (attrList);
        fEleAttrsMap.put(PRE_GLOBAL+SchemaSymbols.ELT_ELEMENT, oneEle);

        // for element "element" - local name
        attrList = new Hashtable();
        // block = (#all | List of (substitution | extension | restriction | list | union))
        attrList.put(SchemaSymbols.ATT_BLOCK, allAttrs[ATT_BLOCK_N]);
        // default = string
        attrList.put(SchemaSymbols.ATT_DEFAULT, allAttrs[ATT_DEFAULT_N]);
        // fixed = string
        attrList.put(SchemaSymbols.ATT_FIXED, allAttrs[ATT_FIXED_N]);
        // form = (qualified | unqualified)
        attrList.put(SchemaSymbols.ATT_FORM, allAttrs[ATT_FORM_N]);
        // id = ID
        attrList.put(SchemaSymbols.ATT_ID, allAttrs[ATT_ID_N]);
        // maxOccurs = (nonNegativeInteger | unbounded)  : 1
        attrList.put(SchemaSymbols.ATT_MAXOCCURS, allAttrs[ATT_MAXOCCURS_D]);
        // minOccurs = nonNegativeInteger : 1
        attrList.put(SchemaSymbols.ATT_MINOCCURS, allAttrs[ATT_MINOCCURS_D]);
        // name = NCName
        attrList.put(SchemaSymbols.ATT_NAME, allAttrs[ATT_NAME_R]);
        // nillable = boolean : false
        attrList.put(SchemaSymbols.ATT_NILLABLE, allAttrs[ATT_NILLABLE_D]);
        // type = QName
        attrList.put(SchemaSymbols.ATT_TYPE, allAttrs[ATT_TYPE_N]);
        oneEle = new OneElement (attrList);
        fEleAttrsMap.put(PRE_LOC_NAME+SchemaSymbols.ELT_ELEMENT, oneEle);

        // for element "element" - local ref
        attrList = new Hashtable();
        // id = ID
        attrList.put(SchemaSymbols.ATT_ID, allAttrs[ATT_ID_N]);
        // maxOccurs = (nonNegativeInteger | unbounded)  : 1
        attrList.put(SchemaSymbols.ATT_MAXOCCURS, allAttrs[ATT_MAXOCCURS_D]);
        // minOccurs = nonNegativeInteger : 1
        attrList.put(SchemaSymbols.ATT_MINOCCURS, allAttrs[ATT_MINOCCURS_D]);
        // ref = QName
        attrList.put(SchemaSymbols.ATT_REF, allAttrs[ATT_REF_R]);
        oneEle = new OneElement (attrList);
        fEleAttrsMap.put(PRE_LOC_REF+SchemaSymbols.ELT_ELEMENT, oneEle);

        // for element "complexType" - global
        attrList = new Hashtable();
        // abstract = boolean : false
        attrList.put(SchemaSymbols.ATT_ABSTRACT, allAttrs[ATT_ABSTRACT_D]);
        // block = (#all | List of (extension | restriction))
        attrList.put(SchemaSymbols.ATT_BLOCK, allAttrs[ATT_BLOCK1_N]);
        // final = (#all | List of (extension | restriction))
        attrList.put(SchemaSymbols.ATT_FINAL, allAttrs[ATT_FINAL_N]);
        // id = ID
        attrList.put(SchemaSymbols.ATT_ID, allAttrs[ATT_ID_N]);
        // mixed = boolean : false
        attrList.put(SchemaSymbols.ATT_MIXED, allAttrs[ATT_MIXED_D]);
        // name = NCName
        attrList.put(SchemaSymbols.ATT_NAME, allAttrs[ATT_NAME_R]);
        oneEle = new OneElement (attrList);
        fEleAttrsMap.put(PRE_GLOBAL+SchemaSymbols.ELT_COMPLEXTYPE, oneEle);

        // for element "complexType" - local name
        attrList = new Hashtable();
        // id = ID
        attrList.put(SchemaSymbols.ATT_ID, allAttrs[ATT_ID_N]);
        // mixed = boolean : false
        attrList.put(SchemaSymbols.ATT_MIXED, allAttrs[ATT_MIXED_D]);
        oneEle = new OneElement (attrList);
        fEleAttrsMap.put(PRE_LOC_NAME+SchemaSymbols.ELT_COMPLEXTYPE, oneEle);

        // for element "simpleContent" - local name
        attrList = new Hashtable();
        // id = ID
        attrList.put(SchemaSymbols.ATT_ID, allAttrs[ATT_ID_N]);
        oneEle = new OneElement (attrList);
        fEleAttrsMap.put(PRE_LOC_NAME+SchemaSymbols.ELT_SIMPLECONTENT, oneEle);

        // for element "restriction" - local name
        attrList = new Hashtable();
        // base = QName
        attrList.put(SchemaSymbols.ATT_BASE, allAttrs[ATT_BASE_N]);
        // id = ID
        attrList.put(SchemaSymbols.ATT_ID, allAttrs[ATT_ID_N]);
        oneEle = new OneElement (attrList);
        fEleAttrsMap.put(PRE_LOC_NAME+SchemaSymbols.ELT_RESTRICTION, oneEle);

        // for element "extension" - local name
        attrList = new Hashtable();
        // base = QName
        attrList.put(SchemaSymbols.ATT_BASE, allAttrs[ATT_BASE_R]);
        // id = ID
        attrList.put(SchemaSymbols.ATT_ID, allAttrs[ATT_ID_N]);
        oneEle = new OneElement (attrList);
        fEleAttrsMap.put(PRE_LOC_NAME+SchemaSymbols.ELT_EXTENSION, oneEle);

        // for element "attributeGroup" - local ref
        attrList = new Hashtable();
        // id = ID
        attrList.put(SchemaSymbols.ATT_ID, allAttrs[ATT_ID_N]);
        // ref = QName
        attrList.put(SchemaSymbols.ATT_REF, allAttrs[ATT_REF_R]);
        oneEle = new OneElement (attrList);
        fEleAttrsMap.put(PRE_LOC_REF+SchemaSymbols.ELT_ATTRIBUTEGROUP, oneEle);

        // for element "anyAttribute" - local name
        attrList = new Hashtable();
        // id = ID
        attrList.put(SchemaSymbols.ATT_ID, allAttrs[ATT_ID_N]);
        // namespace = ((##any | ##other) | List of (anyURI | (##targetNamespace | ##local)) )  : ##any
        attrList.put(SchemaSymbols.ATT_NAMESPACE, allAttrs[ATT_NAMESPACE_D]);
        // processContents = (lax | skip | strict) : strict
        attrList.put(SchemaSymbols.ATT_PROCESSCONTENTS, allAttrs[ATT_PROCESS_C_D]);
        oneEle = new OneElement (attrList);
        fEleAttrsMap.put(PRE_LOC_NAME+SchemaSymbols.ELT_ANYATTRIBUTE, oneEle);

        // for element "complexContent" - local name
        attrList = new Hashtable();
        // id = ID
        attrList.put(SchemaSymbols.ATT_ID, allAttrs[ATT_ID_N]);
        // mixed = boolean
        attrList.put(SchemaSymbols.ATT_MIXED, allAttrs[ATT_MIXED_N]);
        oneEle = new OneElement (attrList);
        fEleAttrsMap.put(PRE_LOC_NAME+SchemaSymbols.ELT_COMPLEXCONTENT, oneEle);

        // for element "attributeGroup" - global
        attrList = new Hashtable();
        // id = ID
        attrList.put(SchemaSymbols.ATT_ID, allAttrs[ATT_ID_N]);
        // name = NCName
        attrList.put(SchemaSymbols.ATT_NAME, allAttrs[ATT_NAME_R]);
        oneEle = new OneElement (attrList);
        fEleAttrsMap.put(PRE_GLOBAL+SchemaSymbols.ELT_ATTRIBUTEGROUP, oneEle);

        // for element "group" - global
        attrList = new Hashtable();
        // id = ID
        attrList.put(SchemaSymbols.ATT_ID, allAttrs[ATT_ID_N]);
        // name = NCName
        attrList.put(SchemaSymbols.ATT_NAME, allAttrs[ATT_NAME_R]);
        oneEle = new OneElement (attrList);
        fEleAttrsMap.put(PRE_GLOBAL+SchemaSymbols.ELT_GROUP, oneEle);

        // for element "group" - local ref
        attrList = new Hashtable();
        // id = ID
        attrList.put(SchemaSymbols.ATT_ID, allAttrs[ATT_ID_N]);
        // maxOccurs = (nonNegativeInteger | unbounded)  : 1
        attrList.put(SchemaSymbols.ATT_MAXOCCURS, allAttrs[ATT_MAXOCCURS_D]);
        // minOccurs = nonNegativeInteger : 1
        attrList.put(SchemaSymbols.ATT_MINOCCURS, allAttrs[ATT_MINOCCURS_D]);
        // ref = QName
        attrList.put(SchemaSymbols.ATT_REF, allAttrs[ATT_REF_R]);
        oneEle = new OneElement (attrList);
        fEleAttrsMap.put(PRE_LOC_REF+SchemaSymbols.ELT_GROUP, oneEle);

        // for element "all" - local name
        attrList = new Hashtable();
        // id = ID
        attrList.put(SchemaSymbols.ATT_ID, allAttrs[ATT_ID_N]);
        // maxOccurs = 1 : 1
        attrList.put(SchemaSymbols.ATT_MAXOCCURS, allAttrs[ATT_MAXOCCURS1_D]);
        // minOccurs = (0 | 1) : 1
        attrList.put(SchemaSymbols.ATT_MINOCCURS, allAttrs[ATT_MINOCCURS1_D]);
        oneEle = new OneElement (attrList);
        fEleAttrsMap.put(PRE_LOC_NAME+SchemaSymbols.ELT_ALL, oneEle);

        // for element "choice" - local name
        attrList = new Hashtable();
        // id = ID
        attrList.put(SchemaSymbols.ATT_ID, allAttrs[ATT_ID_N]);
        // maxOccurs = (nonNegativeInteger | unbounded)  : 1
        attrList.put(SchemaSymbols.ATT_MAXOCCURS, allAttrs[ATT_MAXOCCURS_D]);
        // minOccurs = nonNegativeInteger : 1
        attrList.put(SchemaSymbols.ATT_MINOCCURS, allAttrs[ATT_MINOCCURS_D]);
        oneEle = new OneElement (attrList);
        fEleAttrsMap.put(PRE_LOC_NAME+SchemaSymbols.ELT_CHOICE, oneEle);
        // for element "sequence" - local name
        fEleAttrsMap.put(PRE_LOC_NAME+SchemaSymbols.ELT_SEQUENCE, oneEle);

        // for element "any" - local name
        attrList = new Hashtable();
        // id = ID
        attrList.put(SchemaSymbols.ATT_ID, allAttrs[ATT_ID_N]);
        // maxOccurs = (nonNegativeInteger | unbounded)  : 1
        attrList.put(SchemaSymbols.ATT_MAXOCCURS, allAttrs[ATT_MAXOCCURS_D]);
        // minOccurs = nonNegativeInteger : 1
        attrList.put(SchemaSymbols.ATT_MINOCCURS, allAttrs[ATT_MINOCCURS_D]);
        // namespace = ((##any | ##other) | List of (anyURI | (##targetNamespace | ##local)) )  : ##any
        attrList.put(SchemaSymbols.ATT_NAMESPACE, allAttrs[ATT_NAMESPACE_D]);
        // processContents = (lax | skip | strict) : strict
        attrList.put(SchemaSymbols.ATT_PROCESSCONTENTS, allAttrs[ATT_PROCESS_C_D]);
        oneEle = new OneElement (attrList);
        fEleAttrsMap.put(PRE_LOC_NAME+SchemaSymbols.ELT_ANY, oneEle);

        // for element "unique" - local name
        attrList = new Hashtable();
        // id = ID
        attrList.put(SchemaSymbols.ATT_ID, allAttrs[ATT_ID_N]);
        // name = NCName
        attrList.put(SchemaSymbols.ATT_NAME, allAttrs[ATT_NAME_R]);
        oneEle = new OneElement (attrList);
        fEleAttrsMap.put(PRE_LOC_NAME+SchemaSymbols.ELT_UNIQUE, oneEle);
        // for element "key" - local name
        fEleAttrsMap.put(PRE_LOC_NAME+SchemaSymbols.ELT_KEY, oneEle);

        // for element "keyref" - local name
        attrList = new Hashtable();
        // id = ID
        attrList.put(SchemaSymbols.ATT_ID, allAttrs[ATT_ID_N]);
        // name = NCName
        attrList.put(SchemaSymbols.ATT_NAME, allAttrs[ATT_NAME_R]);
        // refer = QName
        attrList.put(SchemaSymbols.ATT_REFER, allAttrs[ATT_REFER_R]);
        oneEle = new OneElement (attrList);
        fEleAttrsMap.put(PRE_LOC_NAME+SchemaSymbols.ELT_KEYREF, oneEle);

        // for element "selector" - local name
        attrList = new Hashtable();
        // id = ID
        attrList.put(SchemaSymbols.ATT_ID, allAttrs[ATT_ID_N]);
        // xpath = a subset of XPath expression
        attrList.put(SchemaSymbols.ATT_XPATH, allAttrs[ATT_XPATH_R]);
        oneEle = new OneElement (attrList);
        fEleAttrsMap.put(PRE_LOC_NAME+SchemaSymbols.ELT_SELECTOR, oneEle);

        // for element "field" - local name
        attrList = new Hashtable();
        // id = ID
        attrList.put(SchemaSymbols.ATT_ID, allAttrs[ATT_ID_N]);
        // xpath = a subset of XPath expression
        attrList.put(SchemaSymbols.ATT_XPATH, allAttrs[ATT_XPATH1_R]);
        oneEle = new OneElement (attrList);
        fEleAttrsMap.put(PRE_LOC_NAME+SchemaSymbols.ELT_FIELD, oneEle);

        // for element "notation" - local name
        attrList = new Hashtable();
        // id = ID
        attrList.put(SchemaSymbols.ATT_ID, allAttrs[ATT_ID_N]);
        // name = NCName
        attrList.put(SchemaSymbols.ATT_NAME, allAttrs[ATT_NAME_R]);
        // public = A public identifier, per ISO 8879
        attrList.put(SchemaSymbols.ATT_PUBLIC, allAttrs[ATT_PUBLIC_R]);
        // system = anyURI
        attrList.put(SchemaSymbols.ATT_SYSTEM, allAttrs[ATT_SYSTEM_N]);
        oneEle = new OneElement (attrList);
        fEleAttrsMap.put(PRE_LOC_NAME+SchemaSymbols.ELT_NOTATION, oneEle);

        // for element "annotation" - global
        attrList = new Hashtable();
        // id = ID
        attrList.put(SchemaSymbols.ATT_ID, allAttrs[ATT_ID_N]);
        oneEle = new OneElement (attrList);
        fEleAttrsMap.put(PRE_GLOBAL+SchemaSymbols.ELT_ANNOTATION, oneEle);
        // for element "annotation" - local name
        fEleAttrsMap.put(PRE_LOC_NAME+SchemaSymbols.ELT_ANNOTATION, oneEle);

        // for element "appinfo" - local name
        attrList = new Hashtable();
        // source = anyURI
        attrList.put(SchemaSymbols.ATT_SOURCE, allAttrs[ATT_SOURCE_N]);
        oneEle = new OneElement (attrList, false);
        fEleAttrsMap.put(PRE_LOC_NAME+SchemaSymbols.ELT_APPINFO, oneEle);

        // for element "documentation" - local name
        attrList = new Hashtable();
        // source = anyURI
        attrList.put(SchemaSymbols.ATT_SOURCE, allAttrs[ATT_SOURCE_N]);
        // xml:lang = language ???
        oneEle = new OneElement (attrList, false);
        fEleAttrsMap.put(PRE_LOC_NAME+SchemaSymbols.ELT_DOCUMENTATION, oneEle);

        // for element "simpleType" - global
        attrList = new Hashtable();
        // final = (#all | (list | union | restriction))
        attrList.put(SchemaSymbols.ATT_FINAL, allAttrs[ATT_FINAL1_N]);
        // id = ID
        attrList.put(SchemaSymbols.ATT_ID, allAttrs[ATT_ID_N]);
        // name = NCName
        attrList.put(SchemaSymbols.ATT_NAME, allAttrs[ATT_NAME_R]);
        oneEle = new OneElement (attrList);
        fEleAttrsMap.put(PRE_GLOBAL+SchemaSymbols.ELT_SIMPLETYPE, oneEle);

        // for element "simpleType" - local name
        attrList = new Hashtable();
        // final = (#all | (list | union | restriction))
        attrList.put(SchemaSymbols.ATT_FINAL, allAttrs[ATT_FINAL1_N]);
        // id = ID
        attrList.put(SchemaSymbols.ATT_ID, allAttrs[ATT_ID_N]);
        oneEle = new OneElement (attrList);
        fEleAttrsMap.put(PRE_LOC_NAME+SchemaSymbols.ELT_SIMPLETYPE, oneEle);

        // for element "restriction" - local name
        // already registered for complexType

        // for element "list" - local name
        attrList = new Hashtable();
        // id = ID
        attrList.put(SchemaSymbols.ATT_ID, allAttrs[ATT_ID_N]);
        // itemType = QName
        attrList.put(SchemaSymbols.ATT_ITEMTYPE, allAttrs[ATT_ITEMTYPE_N]);
        oneEle = new OneElement (attrList);
        fEleAttrsMap.put(PRE_LOC_NAME+SchemaSymbols.ELT_LIST, oneEle);

        // for element "union" - local name
        attrList = new Hashtable();
        // id = ID
        attrList.put(SchemaSymbols.ATT_ID, allAttrs[ATT_ID_N]);
        // memberTypes = List of QName
        attrList.put(SchemaSymbols.ATT_MEMBERTYPES, allAttrs[ATT_MEMBER_T_N]);
        oneEle = new OneElement (attrList);
        fEleAttrsMap.put(PRE_LOC_NAME+SchemaSymbols.ELT_UNION, oneEle);

        // for element "schema" - global
        attrList = new Hashtable();
        // attributeFormDefault = (qualified | unqualified) : unqualified
        attrList.put(SchemaSymbols.ATT_ATTRIBUTEFORMDEFAULT, allAttrs[ATT_ATTRIBUTE_FD_D]);
        // blockDefault = (#all | List of (substitution | extension | restriction | list | union))  : ''
        attrList.put(SchemaSymbols.ATT_BLOCKDEFAULT, allAttrs[ATT_BLOCK_D_D]);
        // elementFormDefault = (qualified | unqualified) : unqualified
        attrList.put(SchemaSymbols.ATT_ELEMENTFORMDEFAULT, allAttrs[ATT_ELEMENT_FD_D]);
        // finalDefault = (#all | List of (extension | restriction))  : ''
        attrList.put(SchemaSymbols.ATT_FINALDEFAULT, allAttrs[ATT_FINAL_D_D]);
        // id = ID
        attrList.put(SchemaSymbols.ATT_ID, allAttrs[ATT_ID_N]);
        // targetNamespace = anyURI
        attrList.put(SchemaSymbols.ATT_TARGETNAMESPACE, allAttrs[ATT_TARGET_N_N]);
        // version = token
        attrList.put(SchemaSymbols.ATT_VERSION, allAttrs[ATT_VERSION_N]);
        // xml:lang = language ???
        oneEle = new OneElement (attrList);
        fEleAttrsMap.put(PRE_GLOBAL+SchemaSymbols.ELT_SCHEMA, oneEle);

        // for element "include" - global
        attrList = new Hashtable();
        // id = ID
        attrList.put(SchemaSymbols.ATT_ID, allAttrs[ATT_ID_N]);
        // schemaLocation = anyURI
        attrList.put(SchemaSymbols.ATT_SCHEMALOCATION, allAttrs[ATT_SCHEMA_L_R]);
        oneEle = new OneElement (attrList);
        fEleAttrsMap.put(PRE_GLOBAL+SchemaSymbols.ELT_INCLUDE, oneEle);
        // for element "redefine" - global
        fEleAttrsMap.put(PRE_GLOBAL+SchemaSymbols.ELT_REDEFINE, oneEle);

        // for element "import" - global
        attrList = new Hashtable();
        // id = ID
        attrList.put(SchemaSymbols.ATT_ID, allAttrs[ATT_ID_N]);
        // namespace = anyURI
        attrList.put(SchemaSymbols.ATT_NAMESPACE, allAttrs[ATT_NAMESPACE_N]);
        // schemaLocation = anyURI
        attrList.put(SchemaSymbols.ATT_SCHEMALOCATION, allAttrs[ATT_SCHEMA_L_N]);
        oneEle = new OneElement (attrList);
        fEleAttrsMap.put(PRE_GLOBAL+SchemaSymbols.ELT_IMPORT, oneEle);

        // for element "length" - local name
        attrList = new Hashtable();
        // id = ID
        attrList.put(SchemaSymbols.ATT_ID, allAttrs[ATT_ID_N]);
        // value = nonNegativeInteger
        attrList.put(SchemaSymbols.ATT_VALUE, allAttrs[ATT_VALUE_NNI_N]);
        // fixed = boolean : false
        attrList.put(SchemaSymbols.ATT_FIXED, allAttrs[ATT_FIXED_D]);
        oneEle = new OneElement (attrList);
        fEleAttrsMap.put(PRE_LOC_NAME+SchemaSymbols.ELT_LENGTH, oneEle);
        // for element "minLength" - local name
        fEleAttrsMap.put(PRE_LOC_NAME+SchemaSymbols.ELT_MINLENGTH, oneEle);
        // for element "maxLength" - local name
        fEleAttrsMap.put(PRE_LOC_NAME+SchemaSymbols.ELT_MAXLENGTH, oneEle);
        // for element "totalDigits" - local name
        fEleAttrsMap.put(PRE_LOC_NAME+SchemaSymbols.ELT_TOTALDIGITS, oneEle);
        // for element "fractionDigits" - local name
        fEleAttrsMap.put(PRE_LOC_NAME+SchemaSymbols.ELT_FRACTIONDIGITS, oneEle);

        // for element "pattern" - local name
        attrList = new Hashtable();
        // id = ID
        attrList.put(SchemaSymbols.ATT_ID, allAttrs[ATT_ID_N]);
        // value = string
        attrList.put(SchemaSymbols.ATT_VALUE, allAttrs[ATT_VALUE_STR_N]);
        oneEle = new OneElement (attrList);
        fEleAttrsMap.put(PRE_LOC_NAME+SchemaSymbols.ELT_PATTERN, oneEle);

        // for element "enumeration" - local name
        attrList = new Hashtable();
        // id = ID
        attrList.put(SchemaSymbols.ATT_ID, allAttrs[ATT_ID_N]);
        // value = anySimpleType
        attrList.put(SchemaSymbols.ATT_VALUE, allAttrs[ATT_VALUE_STR_N]);
        oneEle = new OneElement (attrList);
        fEleAttrsMap.put(PRE_LOC_NAME+SchemaSymbols.ELT_ENUMERATION, oneEle);

        // for element "whiteSpace" - local name
        attrList = new Hashtable();
        // id = ID
        attrList.put(SchemaSymbols.ATT_ID, allAttrs[ATT_ID_N]);
        // value = preserve | replace | collapse
        attrList.put(SchemaSymbols.ATT_VALUE, allAttrs[ATT_VALUE_WS_N]);
        // fixed = boolean : false
        attrList.put(SchemaSymbols.ATT_FIXED, allAttrs[ATT_FIXED_D]);
        oneEle = new OneElement (attrList);
        fEleAttrsMap.put(PRE_LOC_NAME+SchemaSymbols.ELT_WHITESPACE, oneEle);

        // for element "maxInclusive" - local name
        attrList = new Hashtable();
        // id = ID
        attrList.put(SchemaSymbols.ATT_ID, allAttrs[ATT_ID_N]);
        // value = anySimpleType
        attrList.put(SchemaSymbols.ATT_VALUE, allAttrs[ATT_VALUE_STR_N]);
        // fixed = boolean : false
        attrList.put(SchemaSymbols.ATT_FIXED, allAttrs[ATT_FIXED_D]);
        oneEle = new OneElement (attrList);
        fEleAttrsMap.put(PRE_LOC_NAME+SchemaSymbols.ELT_MAXINCLUSIVE, oneEle);
        // for element "maxExclusive" - local name
        fEleAttrsMap.put(PRE_LOC_NAME+SchemaSymbols.ELT_MAXEXCLUSIVE, oneEle);
        // for element "minInclusive" - local name
        fEleAttrsMap.put(PRE_LOC_NAME+SchemaSymbols.ELT_MININCLUSIVE, oneEle);
        // for element "minExclusive" - local name
        fEleAttrsMap.put(PRE_LOC_NAME+SchemaSymbols.ELT_MINEXCLUSIVE, oneEle);
    }

    // used to store all seen ID values, and to check duplicate ID values
    private Hashtable fIdDefs = new Hashtable();

    // used to resolver namespace prefixes
    protected XSDHandler fSchemaHandler = null;

    // used to store utility reference: error reproter. set via constructor.
    protected XMLErrorReporter fErrorReporter = null;

    // used to store the mapping from processed element to attributes
    protected Hashtable fNonSchemaAttrs = new Hashtable();

    // constructor. Sets fErrorReproter and get datatype validators
    public XSAttributeChecker (XSDHandler schemaHandler,
                               XMLErrorReporter er) {
        fSchemaHandler = schemaHandler;
        fErrorReporter = er;
    }

    public void reset() {
        fIdDefs.clear();
        // REVISIT: set new error reporter?
        //???fErrorReporter = null;
        fNonSchemaAttrs.clear();
    }

    /**
     * check whether the specified element conforms to the attributes restriction
     * an array of attribute values is returned. the caller must call
     * <code>returnAttrArray</code> to return that array.
     * 
     * @param: element    - which element to check
     * @param: isGlobal   - whether a child of <schema> or <redefine>
     * @return: Hashtable - list of attributes and values
     */
    public Object[] checkAttributes(Element element, boolean isGlobal) {
        if (element == null)
            return null;

        String uri = DOMUtil.getNamespaceURI(element);
        String elName = DOMUtil.getLocalName(element), name;

        if (uri == null || !uri.equals(SchemaSymbols.URI_SCHEMAFORSCHEMA)) {
            reportSchemaError("Con3X3ElementSchemaURI", new Object[] {elName});
        }

        // Get the proper name:
        // G_ for global;
        // LN_ for local + name;
        // LR_ for local + ref;
        if (isGlobal) {
            name = PRE_GLOBAL + elName;
        }
        else {
            if (DOMUtil.getAttr(element, SchemaSymbols.ATT_REF) == null)
                name = PRE_LOC_NAME + elName;
            else
                name = PRE_LOC_REF + elName;
        }

        // get desired attribute list of this element
        OneElement oneEle = (OneElement)fEleAttrsMap.get(name);
        if (oneEle == null) {
            reportSchemaError ("Con3X3ElementAppearance",
                               new Object[] {elName});
            return null;
        }

        //Hashtable attrValues = new Hashtable();
        Object[] attrValues = getAvailableArray();
        //Hashtable otherValues = new Hashtable();
        long fromDefault = 0;
        Hashtable attrList = oneEle.attrList;

        // traverse all attributes
        Attr[] attrs = DOMUtil.getAttrs(element);
        Attr sattr = null;
        for (int i = 0; i < attrs.length; i++) {
            sattr = attrs[i++];
            // get the attribute name/value
            //String attrName = DOMUtil.getLocalName(sattr);
            String attrName = sattr.getName();
            String attrVal = DOMUtil.getValue(sattr);

            // skip anything starts with x/X m/M l/L
            // simply put their values in the return hashtable
            if (attrName.toLowerCase().startsWith("xml")) {
                //attrValues.put(attrName, attrVal);
                //otherValues.put(attrName, attrVal);
                continue;
            }

            // for attributes with namespace prefix
            //
            String attrURI = DOMUtil.getNamespaceURI(sattr);
            if (attrURI != null && attrURI.length() != 0) {
                // attributes with schema namespace are not allowed
                // and not allowed on "document" and "appInfo"
                if (attrURI.equals(SchemaSymbols.URI_SCHEMAFORSCHEMA) ||
                    !oneEle.allowNonSchemaAttr) {
                    reportSchemaError ("Con3X3AttributeAppearance",
                                       new Object[] {elName, attrName});
                }
                else {
                    // for attributes from other namespace
                    // store them in a list, and TRY to validate them after
                    // schema traversal (because it's "lax")
                    //otherValues.put(attrName, attrVal);
                    String attrRName = attrURI + "," + attrName;
                    Vector values = (Vector)fNonSchemaAttrs.get(attrRName);
                    if (values == null) {
                        values = new Vector();
                        values.addElement(attrName);
                        values.addElement(elName);
                        values.addElement(attrVal);
                        fNonSchemaAttrs.put(attrRName, values);
                    }
                    else {
                        values.addElement(elName);
                        values.addElement(attrVal);
                    }
                }
                continue;
            }

            // check whether this attribute is allowed
            OneAttr oneAttr = (OneAttr)attrList.get(attrName);
            if (oneAttr == null) {
                reportSchemaError ("Con3X3AttributeAppearance",
                                   new Object[] {elName, attrName});
                continue;
            }

            // check the value against the datatype
            try {
                Object retValue = null;

                // no checking on string needs to be done here.
                // no checking on xpath needs to be done here.
                // xpath values are validated in xpath parser
                if (oneAttr.dvIndex >= 0) {
                    if (oneAttr.dvIndex != DT_STRING &&
                        oneAttr.dvIndex != DT_XPATH &&
                        oneAttr.dvIndex != DT_XPATH1) {
                        DatatypeValidator dv = fExtraDVs[oneAttr.dvIndex];
                        if (dv instanceof IDDatatypeValidator) {
                            retValue = dv.validate( attrVal, fIdDefs );
                        }
                        else {
                            retValue = dv.validate( attrVal, null);
                        }
                    }
                    // REVISIT: should have the datatype validators return
                    // the object representation of the value.
                    switch (oneAttr.dvIndex) {
                    case DT_BOOLEAN:
                        retValue = attrVal.equals(SchemaSymbols.ATTVAL_TRUE) ||
                                   attrVal.equals(SchemaSymbols.ATTVAL_TRUE_1) ?
                                   Boolean.TRUE : Boolean.FALSE;
                        break;
                    case DT_NONNEGINT:
                        retValue = new Integer(attrVal);
                        break;
                    case DT_QNAME:
                        retValue = resolveQName(attrVal);
                        break;
                    default:
                        retValue = attrVal;
                        break;
                    }
                    //attrValues.put(attrName, retValue);
                    attrValues[oneAttr.valueIndex] = retValue;
                }
                else {
                    retValue = validate(attrName, attrVal, oneAttr.dvIndex);
                    //attrValues.put(attrName, retValue);
                    attrValues[oneAttr.valueIndex] = retValue;
                }
            }
            catch (InvalidDatatypeValueException ide) {
                reportSchemaError ("Con3X3AttributeInvalidValue",
                                   new Object[] {elName, attrName, ide.getLocalizedMessage()});
                if (oneAttr.dfltValue != null)
                    //attrValues.put(attrName, oneAttr.dfltValue);
                    attrValues[oneAttr.valueIndex] = oneAttr.dfltValue;
                    fromDefault |= (1<<oneAttr.valueIndex);
            }
        }

        // traverse all required attributes
        OneAttr[] reqAttrs = oneEle.attrArray;
        for (int i = 0; i < reqAttrs.length; i++) {
            OneAttr oneAttr = reqAttrs[i];

            // if the attribute didn't apprear, and
            // if the attribute is optional with default value, apply it
            if (oneAttr.dfltValue != null &&
                DOMUtil.getAttr(element, oneAttr.name) == null) {
                //attrValues.put(oneAttr.name, oneAttr.dfltValue);
                attrValues[oneAttr.valueIndex] = oneAttr.dfltValue;
                fromDefault |= (1<<oneAttr.valueIndex);
            }
        }

        attrValues[ATTIDX_FROMDEFAULT] = new Long(fromDefault);
        //attrValues[ATTIDX_OTHERVALUES] = otherValues;

        return attrValues;
    }

    private Object validate(String attr, String value, int dvIndex) throws InvalidDatatypeValueException {
        if (value == null)
            return null;

        Object retValue = value;
        Vector memberType;
        int choice;

        switch (dvIndex) {
        case DT_BLOCK:
            // block = (#all | List of (substitution | extension | restriction | list | union))
            choice = 0;
            if (value.equals (SchemaSymbols.ATTVAL_POUNDALL)) {
                choice = SchemaSymbols.SUBSTITUTION|SchemaSymbols.EXTENSION|
                         SchemaSymbols.RESTRICTION|SchemaSymbols.LIST|
                         SchemaSymbols.UNION;
            }
            else {
                StringTokenizer t = new StringTokenizer (value, " ");
                while (t.hasMoreTokens()) {
                    String token = t.nextToken ();

                    if (token.equals (SchemaSymbols.ATTVAL_SUBSTITUTION)) {
                        choice |= SchemaSymbols.SUBSTITUTION;
                    }
                    else if (token.equals (SchemaSymbols.ATTVAL_EXTENSION)) {
                        choice |= SchemaSymbols.EXTENSION;
                    }
                    else if (token.equals (SchemaSymbols.ATTVAL_RESTRICTION)) {
                        choice |= SchemaSymbols.RESTRICTION;
                    }
                    else if (token.equals (SchemaSymbols.ATTVAL_LIST)) {
                        choice |= SchemaSymbols.LIST;
                    }
                    else if (token.equals (SchemaSymbols.ATTVAL_UNION)) {
                        choice |= SchemaSymbols.RESTRICTION;
                    }
                    else {
                        throw new InvalidDatatypeValueException("the value '"+value+"' must match (#all | List of (substitution | extension | restriction | list | union))");
                    }
                }
            }
            retValue = new Integer(choice);
            break;
        case DT_BLOCK1:
        case DT_FINAL:
            // block = (#all | List of (extension | restriction))
            // final = (#all | List of (extension | restriction))
            choice = 0;
            if (value.equals (SchemaSymbols.ATTVAL_POUNDALL)) {
                choice = SchemaSymbols.EXTENSION|SchemaSymbols.RESTRICTION;
            }
            else {
                StringTokenizer t = new StringTokenizer (value, " ");
                while (t.hasMoreTokens()) {
                    String token = t.nextToken ();

                    if (token.equals (SchemaSymbols.ATTVAL_EXTENSION)) {
                        choice |= SchemaSymbols.EXTENSION;
                    }
                    else if (token.equals (SchemaSymbols.ATTVAL_RESTRICTION)) {
                        choice |= SchemaSymbols.RESTRICTION;
                    }
                    else {
                        throw new InvalidDatatypeValueException("the value '"+value+"' must match (#all | List of (extension | restriction))");
                    }
                }
            }
            retValue = new Integer(choice);
            break;
        case DT_FINAL1:
            // final = (#all | (list | union | restriction))
            choice = 0;
            if (value.equals (SchemaSymbols.ATTVAL_POUNDALL)) {
                choice = SchemaSymbols.RESTRICTION|SchemaSymbols.LIST|
                         SchemaSymbols.UNION;
            }
            else if (value.equals (SchemaSymbols.ATTVAL_LIST)) {
                choice = SchemaSymbols.LIST;
            }
            else if (value.equals (SchemaSymbols.ATTVAL_UNION)) {
                choice = SchemaSymbols.UNION;
            }
            else if (value.equals (SchemaSymbols.ATTVAL_RESTRICTION)) {
                choice = SchemaSymbols.RESTRICTION;
            }
            else {
                throw new InvalidDatatypeValueException("the value '"+value+"' must match (#all | (list | union | restriction))");
            }
            retValue = new Integer(choice);
            break;
        case DT_FORM:
            // form = (qualified | unqualified)
            if (value.equals (SchemaSymbols.ATTVAL_QUALIFIED))
                retValue = INT_QUALIFIED;
            else if (value.equals (SchemaSymbols.ATTVAL_UNQUALIFIED))
                retValue = INT_UNQUALIFIED;
            else
                throw new InvalidDatatypeValueException("the value '"+value+"' must match (qualified | unqualified)");
            break;
        case DT_MAXOCCURS:
            // maxOccurs = (nonNegativeInteger | unbounded)
            if (value.equals(SchemaSymbols.ATTVAL_UNBOUNDED)) {
                retValue = INT_UNBOUNDED;
            } else {
                try {
                    retValue = fExtraDVs[DT_NONNEGINT].validate(value, null);
                    // REVISIT: should have the datatype validators return
                    // the object representation of the value.
                    retValue = new Integer(value);
                }
                catch (InvalidDatatypeValueException ide) {
                    throw new InvalidDatatypeValueException("the value '"+value+"' must match (nonNegativeInteger | unbounded)");
                }
            }
            break;
        case DT_MAXOCCURS1:
            // maxOccurs = 1
            if (value.equals("1"))
                retValue = INT_ONE;
            else
                throw new InvalidDatatypeValueException("the value '"+value+"' must be '1'");
            break;
        case DT_MEMBERTYPES:
            // memberTypes = List of QName
            memberType = new Vector();
            try {
                StringTokenizer t = new StringTokenizer (value, " ");
                while (t.hasMoreTokens()) {
                    String token = t.nextToken ();
                    retValue = fExtraDVs[DT_QNAME].validate(token, null);
                    // REVISIT: should have the datatype validators return
                    // the object representation of the value.
                    retValue = resolveQName(token);
                    memberType.addElement(retValue);
                }
                retValue = memberType;
            }
            catch (InvalidDatatypeValueException ide) {
                throw new InvalidDatatypeValueException("the value '"+value+"' must match (List of QName)");
            }
            break;
        case DT_MINOCCURS1:
            // minOccurs = (0 | 1)
            if (value.equals("0"))
                retValue = INT_ZERO;
            else if (value.equals("1"))
                retValue = INT_ONE;
            else
                throw new InvalidDatatypeValueException("the value '"+value+"' must be '0' or '1'");
            break;
        case DT_NAMESPACE:
            // namespace = ((##any | ##other) | List of (anyURI | (##targetNamespace | ##local)) )
            if (!value.equals(SchemaSymbols.ATTVAL_TWOPOUNDANY) &&
                !value.equals(SchemaSymbols.ATTVAL_TWOPOUNDOTHER)) {
                StringTokenizer t = new StringTokenizer (value, " ");
                try {
                    while (t.hasMoreTokens()) {
                        String token = t.nextToken ();
                        if (!token.equals(SchemaSymbols.ATTVAL_TWOPOUNDTARGETNS) &&
                            !token.equals(SchemaSymbols.ATTVAL_TWOPOUNDLOCAL)) {
                            fExtraDVs[DT_ANYURI].validate(token, null);
                        }
                    }
                    //REVISIT: what to return? a vector?
                }
                catch (InvalidDatatypeValueException ide) {
                    throw new InvalidDatatypeValueException("the value '"+value+"' must match ((##any | ##other) | List of (anyURI | (##targetNamespace | ##local)) )");
                }
            }
            break;
        case DT_PROCESSCONTENTS:
            // processContents = (lax | skip | strict)
            if (value.equals (SchemaSymbols.ATTVAL_STRICT))
                retValue = INT_ANY_STRICT;
            else if (value.equals (SchemaSymbols.ATTVAL_LAX))
                retValue = INT_ANY_LAX;
            else if (value.equals (SchemaSymbols.ATTVAL_SKIP))
                retValue = INT_ANY_SKIP;
            else
                throw new InvalidDatatypeValueException("the value '"+value+"' must match (lax | skip | strict)");
            break;
        case DT_PUBLIC:
            // public = A public identifier, per ISO 8879
            // REVISIT: how to validate "public"???
            fExtraDVs[DT_TOKEN].validate(value, null);
            break;
        case DT_USE:
            // use = (optional | prohibited | required)
            if (value.equals (SchemaSymbols.ATTVAL_OPTIONAL))
                retValue = INT_USE_OPTIONAL;
            else if (value.equals (SchemaSymbols.ATTVAL_REQUIRED))
                retValue = INT_USE_REQUIRED;
            else if (value.equals (SchemaSymbols.ATTVAL_PROHIBITED))
                retValue = INT_USE_PROHIBITED;
            else
                throw new InvalidDatatypeValueException("the value '"+value+"' must match (optional | prohibited | required)");
            break;
        case DT_WHITESPACE:
            // value = preserve | replace | collapse
            if (value.equals (SchemaSymbols.ATTVAL_PRESERVE))
                retValue = INT_WS_PRESERVE;
            else if (value.equals (SchemaSymbols.ATTVAL_REPLACE))
                retValue = INT_WS_REPLACE;
            else if (value.equals (SchemaSymbols.ATTVAL_COLLAPSE))
                retValue = INT_WS_COLLAPSE;
            else
                throw new InvalidDatatypeValueException("the value '"+value+"' must match (preserve | replace | collapse)");
            break;
        }

        return retValue;
    }

    // report an error. copied from TraverseSchema
    private void reportSchemaError(String key, Object args[]) {
        if (fErrorReporter == null) {
            System.out.println("__TraverseSchemaError__ : " + key);
            for (int i=0; i< args.length ; i++) {
                System.out.println((String)args[i]);
            }
        }
        else {
            fErrorReporter.reportError(XSMessageFormatter.SCHEMA_DOMAIN,
                                       key,
                                       args,
                                       XMLErrorReporter.SEVERITY_ERROR);
        }
    }

    // validate attriubtes from non-schema namespaces
    public void checkNonSchemaAttributes(XSGrammarResolver grammarResolver) throws Exception {
        // for all attributes
        Enumeration enum = fNonSchemaAttrs.keys();
        XSAttributeDecl tempAttrDecl = new XSAttributeDecl();
        while (enum.hasMoreElements()) {
            // get name, uri, localpart
            String attrRName = (String)enum.nextElement();
            String attrURI = attrRName.substring(0,attrRName.indexOf(','));
            String attrLocal = attrRName.substring(attrRName.indexOf(',')+1);
            // find associated grammar
            SchemaGrammar sGrammar = grammarResolver.getGrammar(attrURI);
            if (sGrammar == null)
                continue;
            // and get the datatype validator, if there is one
            tempAttrDecl = sGrammar.getAttributeDecl(attrLocal, tempAttrDecl);
            if (tempAttrDecl == null)
                continue;
            sGrammar = grammarResolver.getGrammar(tempAttrDecl.fTypeNS);
            if (sGrammar == null)
                continue;
            DatatypeValidator dv = (DatatypeValidator)sGrammar.getTypeDecl(tempAttrDecl.fType);
            if (dv == null)
                continue;

            // get all values appeared with this attribute name
            Vector values = (Vector)fNonSchemaAttrs.get(attrRName);
            String elName, attrVal;
            String attrName = (String)values.elementAt(0);
            // for each of the values
            int count = values.size();
            for (int i = 1; i < count; i += 2) {
                // normalize it according to the whiteSpace facet
                elName = (String)values.elementAt(i);
                attrVal = normalize((String)values.elementAt(i+1), dv.getWSFacet());
                try {
                    // and validate it using the DatatypeValidator
                    dv.validate(attrVal,null);
                } catch(InvalidDatatypeValueException ide) {
                    reportSchemaError ("Con3X3AttributeInvalidValue",
                                       new Object[] {elName, attrName, ide.getLocalizedMessage()});
                }
            }
        }
    }

    // normalize the string according to the whiteSpace facet
    // REVISIT: should move this to a util class/method
    public static String normalize(String content, short ws) {
        int len = content == null ? 0 : content.length();
        if (len == 0 || ws == DatatypeValidator.PRESERVE)
            return content;

        StringBuffer sb = new StringBuffer();
        if (ws == DatatypeValidator.REPLACE) {
            char ch;
            // when it's replace, just replace #x9, #xa, #xd by #x20
            for (int i = 0; i < len; i++) {
                ch = content.charAt(i);
                if (ch != 0x9 && ch != 0xa && ch != 0xd)
                    sb.append(ch);
                else
                    sb.append((char)0x20);
            }
        }
        else {
            char ch;
            int i;
            boolean isLeading = true;
            // when it's collapse
            for (i = 0; i < len; i++) {
                ch = content.charAt(i);
                // append real characters, so we passed leading ws
                if (ch != 0x9 && ch != 0xa && ch != 0xd && ch != 0x20) {
                    sb.append(ch);
                    isLeading = false;
                }
                else {
                    // for whitespaces, we skip all following ws
                    for (; i < len-1; i++) {
                        ch = content.charAt(i+1);
                        if (ch != 0x9 && ch != 0xa && ch != 0xd && ch != 0x20)
                            break;
                    }
                    // if it's not a leading or tailing ws, then append a space
                    if (i < len - 1 && !isLeading)
                        sb.append((char)0x20);
                }
            }
        }

        return sb.toString();
    }

    //REVISIT: how to resolver qname?
    protected QName resolveQName (String attrVal) {
        String prefix = "";
        String localpart = attrVal;
        int colonptr = attrVal.indexOf(":");
        if ( colonptr > 0) {
            prefix = attrVal.substring(0,colonptr);
            localpart = attrVal.substring(colonptr+1);
        }
        String uri = fSchemaHandler.resolvePrefixToURI(prefix);
        //REVISIT: how to resolve prefix to uri
        uri = SchemaSymbols.URI_SCHEMAFORSCHEMA;
        return new QName(prefix, localpart, attrVal, uri);
    }

    // the following part implements an attribute-value-array pool.
    // when checkAttribute is called, it calls getAvailableArray to get
    // an array from the pool; when the caller is done with the array,
    // it calls returnAttrArray to return that array to the pool.
    
    // initial size of the array pool. 10 is big enough
    static final int INIT_POOL_SIZE = 10;
    // the incremental size of the array pool
    static final int INC_POOL_SIZE  = 10;
    // the array pool
    Object[][] fArrayPool = new Object[INIT_POOL_SIZE][ATTIDX_COUNT];
    // current position of the array pool (# of arrays not returned)
    int fPoolPos = 0;
    
    // get the next available array
    protected Object[] getAvailableArray() {
        // if no array left in the pool, increase the pool size
        if (fArrayPool.length == fPoolPos) {
            // increase size
            fArrayPool = new Object[fPoolPos+INC_POOL_SIZE][];
            // initialize each *new* array
            for (int i = fPoolPos; i < fArrayPool.length; i++)
                fArrayPool[i] = new Object[ATTIDX_COUNT];
        }
        // get the next available one
        Object[] retArray = fArrayPool[fPoolPos];
        // clear it from the pool. this is for GC: if a caller forget to
        // return the array, we want that array to be GCed.
        fArrayPool[fPoolPos++] = null;
        // to make sure that one array is not returned twice, we use
        // the last entry to indicate whether an array is already returned
        // now set it to false.
        retArray[ATTIDX_ISRETURNED] = Boolean.FALSE;
        
        return retArray;
    }
    
    // return an array back to the pool
    public void returnAttrArray (Object[] attrArray) {
        // if 1. the pool is full; 2. the array is null;
        // 3. the array is of wrong size; 4. the array is already returned
        // then we can't accept this array to be returned
        if (fPoolPos == 0 ||
            attrArray == null ||
            attrArray.length != ATTIDX_COUNT ||
            ((Boolean)attrArray[ATTIDX_ISRETURNED]).booleanValue()) {
            return;
        }
        
        // mark this array as returned
        attrArray[ATTIDX_ISRETURNED] = Boolean.TRUE;
        // and put it into the pool
        fArrayPool[--fPoolPos] = attrArray;
    }
}

class OneAttr {
    // name of the attribute
    public String name;
    // index of the datatype validator
    public int dvIndex;
    // whether it's optional, and has default value
    public int valueIndex;
    // the default value of this attribute
    public Object dfltValue;

    public OneAttr(String name, int dvIndex, int valueIndex, Object dfltValue) {
        this.name = name;
        this.dvIndex = dvIndex;
        this.valueIndex = valueIndex;
        this.dfltValue = dfltValue;
    }
}

class OneElement {
    // the list of attributes that can appear in one element
    public Hashtable attrList;
    // the array of attributes that can appear in one element
    public OneAttr[] attrArray;
    // does this element allow attributes from non-schema namespace
    public boolean allowNonSchemaAttr;

    public OneElement (Hashtable attrList) {
        this(attrList, true);
    }

    public OneElement (Hashtable attrList, boolean allowNonSchemaAttr) {
        this.attrList = attrList;

        int count = attrList.size();
        this.attrArray = new OneAttr[count];
        Enumeration enum = attrList.elements();
        for (int i = 0; i < count; i++)
            this.attrArray[i] = (OneAttr)enum.nextElement();

        this.allowNonSchemaAttr = allowNonSchemaAttr;
    }
}
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

import org.apache.xerces.impl.dv.XSSimpleType;
import org.apache.xerces.impl.dv.XSAtomicSimpleType;
import org.apache.xerces.impl.dv.XSListSimpleType;
import org.apache.xerces.impl.dv.XSUnionSimpleType;
import org.apache.xerces.impl.dv.XSFacets;
import org.apache.xerces.impl.dv.InvalidDatatypeValueException;
import org.apache.xerces.impl.dv.InvalidDatatypeFacetException;
import org.apache.xerces.impl.dv.ValidatedInfo;
import org.apache.xerces.impl.validation.ValidationContext;
import org.apache.xerces.impl.xs.XSTypeDecl;
import org.apache.xerces.util.XMLChar;
import org.apache.xerces.impl.xpath.regex.RegularExpression;
import org.apache.xerces.xni.NamespaceContext;
import java.util.Vector;
import java.util.StringTokenizer;

/**
 * @author Sandy Gao, IBM
 * @author Neeraj Bajaj, Sun Microsystems, inc.
 *
 * @version $Id$
 */
class XSSimpleTypeDecl implements XSAtomicSimpleType, XSListSimpleType, XSUnionSimpleType {

    static final short DV_STRING        = PRIMITIVE_STRING;
    static final short DV_BOOLEAN       = PRIMITIVE_BOOLEAN;
    static final short DV_DECIMAL       = PRIMITIVE_DECIMAL;
    static final short DV_FLOAT         = PRIMITIVE_FLOAT;
    static final short DV_DOUBLE        = PRIMITIVE_DOUBLE;
    static final short DV_DURATION      = PRIMITIVE_DURATION;
    static final short DV_DATETIME      = PRIMITIVE_DATETIME;
    static final short DV_TIME          = PRIMITIVE_TIME;
    static final short DV_DATE          = PRIMITIVE_DATE;
    static final short DV_GYEARMONTH    = PRIMITIVE_GYEARMONTH;
    static final short DV_GYEAR         = PRIMITIVE_GYEAR;
    static final short DV_GMONTHDAY     = PRIMITIVE_GMONTHDAY;
    static final short DV_GDAY          = PRIMITIVE_GDAY;
    static final short DV_GMONTH        = PRIMITIVE_GMONTH;
    static final short DV_HEXBINARY     = PRIMITIVE_HEXBINARY;
    static final short DV_BASE64BINARY  = PRIMITIVE_BASE64BINARY;
    static final short DV_ANYURI        = PRIMITIVE_ANYURI;
    static final short DV_QNAME         = PRIMITIVE_QNAME;
    static final short DV_NOTATION      = PRIMITIVE_NOTATION;

    static final short DV_ANYSIMPLETYPE = 0;
    static final short DV_ID            = DV_NOTATION + 1;
    static final short DV_IDREF         = DV_NOTATION + 2;
    static final short DV_ENTITY        = DV_NOTATION + 3;
    static final short DV_LIST          = DV_NOTATION + 4;
    static final short DV_UNION         = DV_NOTATION + 5;

    static final TypeValidator[] fDVs = {
        new AnySimpleDV(),
        new StringDV(),
        new BooleanDV(),
        new DecimalDV(),
        new FloatDV(),
        new DoubleDV(),
        new DurationDV(),
        new DateTimeDV(),
        new TimeDV(),
        new DateDV(),
        new YearMonthDV(),
        new YearDV(),
        new MonthDayDV(),
        new DayDV(),
        new MonthDV(),
        new HexBinaryDV(),
        new Base64BinaryDV(),
        new AnyURIDV(),
        new QNameDV(),
        new QNameDV(),   // notation use the same one as qname
        new IDDV(),
        new IDREFDV(),
        new EntityDV(),
        new ListDV(),
        new UnionDV()
    };

    static final short SPECIAL_TOKEN_NONE        = 0;
    static final short SPECIAL_TOKEN_NMTOKEN     = 1;
    static final short SPECIAL_TOKEN_NAME        = 2;
    static final short SPECIAL_TOKEN_NCNAME      = 3;

    static final String[] SPECIAL_TOKEN_STRING   = {
        "NONE", "NMTOKEN", "Name", "NCName",
    };

    static final String[] WS_FACET_STRING = {
        "preserve", "collapse", "replace",
    };

    private XSSimpleTypeDecl fItemType;
    private XSSimpleTypeDecl[] fMemberTypes;

    private String fTypeName;
    private String fTargetNamespace;
    private short fFinalSet = 0;
    private XSSimpleTypeDecl fBase;
    private short fVariety = -1;
    private short fValidationDV = -1;

    private short fFacetsDefined = 0;
    private short fFixedFacet = 0;

    //for constraining facets
    private short fWhiteSpace = 0;
    private int fLength = -1;
    private int fMinLength = -1;
    private int fMaxLength = -1;
    private int fTotalDigits = -1;
    private int fFractionDigits = -1;
    private Vector fPattern;
    private Vector fEnumeration;
    private Object fMaxInclusive;
    private Object fMaxExclusive;
    private Object fMinExclusive;
    private Object fMinInclusive;

    private short fTokenType = SPECIAL_TOKEN_NONE;

    // for fundamental facets
    private short fOrdered;
    private short fCardinality;
    private boolean fBounded;
    private boolean fNumeric;

    private ValidatedInfo fTempInfo = new ValidatedInfo();

    //Create a new built-in primitive types (and id/idref/entity)
    protected XSSimpleTypeDecl(XSSimpleTypeDecl base, String name, short validateDV,
                               short ordered, boolean bounded,
                               short cardinality, boolean numeric) {
        fBase = base;
        fTypeName = name;
        fTargetNamespace = SchemaDVFactoryImpl.URI_SCHEMAFORSCHEMA;
        // To simplify the code for anySimpleType, we treat it as an atomic type
        fVariety = VARIETY_ATOMIC;
        fValidationDV = validateDV;
        fFacetsDefined = FACET_WHITESPACE;
        if (validateDV == DV_STRING) {
            fWhiteSpace = WS_PRESERVE;
        } else {
            fWhiteSpace = WS_COLLAPSE;
            fFixedFacet = FACET_WHITESPACE;
        }
    }

    //Create a new simple type for restriction.
    protected XSSimpleTypeDecl(XSSimpleTypeDecl base, String name, String uri, short finalSet) {
        fBase = base;
        fTypeName = name;
        fTargetNamespace = uri;
        fFinalSet = finalSet;

        fVariety = fBase.fVariety;
        fValidationDV = fBase.fValidationDV;
        switch (fVariety) {
        case VARIETY_ATOMIC:
            break;
        case VARIETY_LIST:
            fItemType = fBase.fItemType;
            break;
        case VARIETY_UNION:
            fMemberTypes = fBase.fMemberTypes;
            break;
        }

        // always inherit facets from the base.
        // in case a type is created, but applyFacets is not called
        fLength = fBase.fLength;
        fMinLength = fBase.fMinLength;
        fMaxLength = fBase.fMaxLength;
        fPattern = fBase.fPattern;
        fEnumeration = fBase.fEnumeration;
        fWhiteSpace = fBase.fWhiteSpace;
        fMaxExclusive = fBase.fMaxExclusive;
        fMaxInclusive = fBase.fMaxInclusive;
        fMinExclusive = fBase.fMinExclusive;
        fMinInclusive = fBase.fMinInclusive;
        fTotalDigits = fBase.fTotalDigits;
        fFractionDigits = fBase.fFractionDigits;
        fTokenType = fBase.fTokenType;
        fFixedFacet = fBase.fFixedFacet;
        fFacetsDefined = fBase.fFacetsDefined;

        //we also set fundamental facets information in case applyFacets is not called.
        caclFundamentalFacets();
    }

    //Create a new simple type for list.
    protected XSSimpleTypeDecl(String name, String uri, short finalSet, XSSimpleTypeDecl itemType) {
        fBase = fAnySimpleType;
        fTypeName = name;
        fTargetNamespace = uri;
        fFinalSet = finalSet;

        fVariety = VARIETY_LIST;
        fItemType = (XSSimpleTypeDecl)itemType;
        fValidationDV = DV_LIST;
        fFacetsDefined = FACET_WHITESPACE;
        fFixedFacet = FACET_WHITESPACE;
        fWhiteSpace = WS_COLLAPSE;

        //setting fundamental facets
        caclFundamentalFacets();
    }

    //Create a new simple type for union.
    protected XSSimpleTypeDecl(String name, String uri, short finalSet, XSSimpleTypeDecl[] memberTypes) {
        fBase = fAnySimpleType;
        fTypeName = name;
        fTargetNamespace = uri;
        fFinalSet = finalSet;

        fVariety = VARIETY_UNION;
        fMemberTypes = memberTypes;
        fValidationDV = DV_UNION;
        // even for union, we set whitespace to something
        // this will never be used, but we can use fFacetsDefined to check
        // whether applyFacets() is allwwed: it's not allowed
        // if fFacetsDefined != 0
        fFacetsDefined = FACET_WHITESPACE;
        fWhiteSpace = WS_COLLAPSE;

        //setting fundamental facets
        caclFundamentalFacets();
    }

    public short getXSType () {
        return XSTypeDecl.SIMPLE_TYPE;
    }

    public String getTypeName() {
        return fTypeName;
    }

    public String getTargetNamespace() {
        return fTargetNamespace;
    }

    public short getFinalSet(){
        return fFinalSet;
    }

    public XSTypeDecl getBaseType(){
        return fBase;
    }

    public boolean isAnonymous() {
        return fTypeName == null;
    }

    public short getVariety(){
        // for anySimpleType, return absent variaty
        return fValidationDV == DV_ANYSIMPLETYPE ? VARIETY_ABSENT : fVariety;
    }

    public short getDefinedFacets() {
        return fFacetsDefined;
    }

    public boolean isIDType(){
        return (fValidationDV == DV_ID);
    }

    public short getPrimitiveKind() {
        if (fVariety == VARIETY_ATOMIC && fValidationDV != DV_ANYSIMPLETYPE) {
            if (fVariety == DV_ID || fVariety == DV_IDREF || fVariety == DV_ENTITY)
                return DV_STRING;
            else
                return fValidationDV;
        }
        else {
            // REVISIT: error situation. runtime exception?
            return (short)0;
        }
    }

    public XSSimpleType getPrimitiveType() {
        if (fVariety == VARIETY_ATOMIC && fValidationDV != DV_ANYSIMPLETYPE) {
            XSSimpleTypeDecl pri = this;
            // recursively get base, until we reach anySimpleType
            while (pri.fBase != fAnySimpleType)
                pri = pri.fBase;
            return pri;
        }
        else {
            // REVISIT: error situation. runtime exception?
            return null;
        }
    }

    public XSSimpleType getItemType() {
        if (fVariety == VARIETY_LIST) {
            return fItemType;
        }
        else {
            // REVISIT: error situation. runtime exception?
            return null;
        }
    }

    public XSSimpleType[] getMemberTypes() {
        if (fVariety == VARIETY_UNION) {
            return fMemberTypes;
        }
        else {
            // REVISIT: error situation. runtime exception?
            return null;
        }
    }

    /**
     * If <restriction> is chosen
     */
    public void applyFacets(XSFacets facets, short presentFacet, short fixedFacet, ValidationContext context)
        throws InvalidDatatypeFacetException {
        applyFacets(facets, presentFacet, fixedFacet, (short)0, context);
    }

    /**
     * built-in derived types by restriction
     */
    void applyFacets1(XSFacets facets, short presentFacet, short fixedFacet) {

        try {
            applyFacets(facets, presentFacet, fixedFacet, (short)0, null);
        } catch (InvalidDatatypeFacetException e) {
            // should never gets here, internel error
            throw new RuntimeException("internal error");
        }
    }

    /**
     * built-in derived types by restriction
     */
    void applyFacets1(XSFacets facets, short presentFacet, short fixedFacet, short tokenType) {

        try {
            applyFacets(facets, presentFacet, fixedFacet, tokenType, null);
        } catch (InvalidDatatypeFacetException e) {
            // should never gets here, internel error
            throw new RuntimeException("internal error");
        }
    }

    /**
     * If <restriction> is chosen, or built-in derived types by restriction
     */
    void applyFacets(XSFacets facets, short presentFacet, short fixedFacet, short tokenType, ValidationContext context)
        throws InvalidDatatypeFacetException {

        // clear facets. because we always inherit facets in the constructor
        // REVISIT: in fact, we don't need to clear them.
        // we can convert 5 string values (4 bounds + 1 enum) to actual values,
        // store them somewhere, then do facet checking at once, instead of
        // going through the following steps. (lots of checking are redundant:
        // for example, ((presentFacet & FACET_XXX) != 0))

        fFacetsDefined = 0;
        fFixedFacet = 0;

        int result = 0 ;

        // step 1: parse present facets
        short allowedFacet = fDVs[fValidationDV].getAllowedFacets();

        // length
        if ((presentFacet & FACET_LENGTH) != 0) {
            if ((allowedFacet & FACET_LENGTH) == 0) {
                reportError("cos-applicable-facets", new Object[]{"length"});
            } else {
                fLength = facets.length;
                fFacetsDefined |= FACET_LENGTH;
                if ((fixedFacet & FACET_LENGTH) != 0)
                    fFixedFacet |= FACET_LENGTH;
            }
        }
        // minLength
        if ((presentFacet & FACET_MINLENGTH) != 0) {
            if ((allowedFacet & FACET_MINLENGTH) == 0) {
                reportError("cos-applicable-facets", new Object[]{"minLength"});
            } else {
                fMinLength = facets.minLength;
                fFacetsDefined |= FACET_MINLENGTH;
                if ((fixedFacet & FACET_MINLENGTH) != 0)
                    fFixedFacet |= FACET_MINLENGTH;
            }
        }
        // maxLength
        if ((presentFacet & FACET_MAXLENGTH) != 0) {
            if ((allowedFacet & FACET_MAXLENGTH) == 0) {
                reportError("cos-applicable-facets", new Object[]{"maxLength"});
            } else {
                fMaxLength = facets.maxLength;
                fFacetsDefined |= FACET_MAXLENGTH;
                if ((fixedFacet & FACET_MAXLENGTH) != 0)
                    fFixedFacet |= FACET_MAXLENGTH;
            }
        }
        // pattern
        if ((presentFacet & FACET_PATTERN) != 0) {
            if ((allowedFacet & FACET_PATTERN) == 0) {
                reportError("cos-applicable-facets", new Object[]{"pattern"});
            } else {
                RegularExpression regex = null;
                try {
                    regex = new RegularExpression(facets.pattern, "X");
                } catch (Exception e) {
                    reportError("InvalidRegex", new Object[]{facets.pattern, e.getLocalizedMessage()});
                }
                if (regex != null) {
                    fPattern = new Vector();
                    fPattern.addElement(regex);
                    fFacetsDefined |= FACET_PATTERN;
                    if ((fixedFacet & FACET_PATTERN) != 0)
                        fFixedFacet |= FACET_PATTERN;
                }
            }
        }

        // enumeration
        if ((presentFacet & FACET_ENUMERATION) != 0) {
            if ((allowedFacet & FACET_ENUMERATION) == 0) {
                reportError("cos-applicable-facets", new Object[]{"enumeration"});
            } else {
                fEnumeration = new Vector();
                Vector enumVals = facets.enumeration;
                Vector enumNSDecls = facets.enumNSDecls;
                ValidationContextImpl ctx = new ValidationContextImpl(context);
                for (int i = 0; i < enumVals.size(); i++) {
                    if (enumNSDecls != null)
                        ctx.setNSContext((NamespaceContext)enumNSDecls.elementAt(i));
                    try {
                        // check 4.3.5.c0 must: enumeration values from the value space of base
                        fEnumeration.addElement(this.fBase.validate((String)enumVals.elementAt(i), ctx, fTempInfo));
                    } catch (InvalidDatatypeValueException ide) {
                        reportError("FacetValueFromBase", new Object[]{enumVals.elementAt(i), "enumeration"});
                    }
                }
                fFacetsDefined |= FACET_ENUMERATION;
                if ((fixedFacet & FACET_ENUMERATION) != 0)
                    fFixedFacet |= FACET_ENUMERATION;
            }
        }
        // whiteSpace
        if ((presentFacet & FACET_WHITESPACE) != 0) {
            if ((allowedFacet & FACET_WHITESPACE) == 0) {
                reportError("cos-applicable-facets", new Object[]{"whiteSpace"});
            } else {
                fWhiteSpace = facets.whiteSpace;
                fFacetsDefined |= FACET_WHITESPACE;
                if ((fixedFacet & FACET_WHITESPACE) != 0)
                    fFixedFacet |= FACET_WHITESPACE;
            }
        }
        // maxInclusive
        if ((presentFacet & FACET_MAXINCLUSIVE) != 0) {
            if ((allowedFacet & FACET_MAXINCLUSIVE) == 0) {
                reportError("cos-applicable-facets", new Object[]{"maxInclusive"});
            } else {
                try {
                    fMaxInclusive = getActualValue(facets.maxInclusive, context, fTempInfo);
                    fFacetsDefined |= FACET_MAXINCLUSIVE;
                    if ((fixedFacet & FACET_MAXINCLUSIVE) != 0)
                        fFixedFacet |= FACET_MAXINCLUSIVE;
                } catch (InvalidDatatypeValueException ide) {
                    reportError("FacetValueFromBase", new Object[]{facets.maxInclusive, "maxInclusive"});
                }
            }
        }
        // maxExclusive
        if ((presentFacet & FACET_MAXEXCLUSIVE) != 0) {
            if ((allowedFacet & FACET_MAXEXCLUSIVE) == 0) {
                reportError("cos-applicable-facets", new Object[]{"maxExclusive"});
            } else {
                try {
                    fMaxExclusive = getActualValue(facets.maxExclusive, context, fTempInfo);
                    fFacetsDefined |= FACET_MAXEXCLUSIVE;
                    if ((fixedFacet & FACET_MAXEXCLUSIVE) != 0)
                        fFixedFacet |= FACET_MAXEXCLUSIVE;
                } catch (InvalidDatatypeValueException ide) {
                    reportError("FacetValueFromBase", new Object[]{facets.maxExclusive, "maxExclusive"});
                }
            }
        }
        // minExclusive
        if ((presentFacet & FACET_MINEXCLUSIVE) != 0) {
            if ((allowedFacet & FACET_MINEXCLUSIVE) == 0) {
                reportError("cos-applicable-facets", new Object[]{"minExclusive"});
            } else {
                try {
                    fMinExclusive = getActualValue(facets.minExclusive, context, fTempInfo);
                    fFacetsDefined |= FACET_MINEXCLUSIVE;
                    if ((fixedFacet & FACET_MINEXCLUSIVE) != 0)
                        fFixedFacet |= FACET_MINEXCLUSIVE;
                } catch (InvalidDatatypeValueException ide) {
                    reportError("FacetValueFromBase", new Object[]{facets.minExclusive, "minExclusive"});
                }
            }
        }
        // minInclusive
        if ((presentFacet & FACET_MININCLUSIVE) != 0) {
            if ((allowedFacet & FACET_MININCLUSIVE) == 0) {
                reportError("cos-applicable-facets", new Object[]{"minInclusive"});
            } else {
                try {
                    fMinInclusive = getActualValue(facets.minInclusive, context, fTempInfo);
                    fFacetsDefined |= FACET_MININCLUSIVE;
                    if ((fixedFacet & FACET_MININCLUSIVE) != 0)
                        fFixedFacet |= FACET_MININCLUSIVE;
                } catch (InvalidDatatypeValueException ide) {
                    reportError("FacetValueFromBase", new Object[]{facets.minInclusive, "minInclusive"});
                }
            }
        }
        // totalDigits
        if ((presentFacet & FACET_TOTALDIGITS) != 0) {
            if ((allowedFacet & FACET_TOTALDIGITS) == 0) {
                reportError("cos-applicable-facets", new Object[]{"totalDigits"});
            } else {
                fTotalDigits = facets.totalDigits;
                fFacetsDefined |= FACET_TOTALDIGITS;
                if ((fixedFacet & FACET_TOTALDIGITS) != 0)
                    fFixedFacet |= FACET_TOTALDIGITS;
            }
        }
        // fractionDigits
        if ((presentFacet & FACET_FRACTIONDIGITS) != 0) {
            if ((allowedFacet & FACET_FRACTIONDIGITS) == 0) {
                reportError("cos-applicable-facets", new Object[]{"fractionDigits"});
            } else {
                fFractionDigits = facets.fractionDigits;
                fFacetsDefined |= FACET_FRACTIONDIGITS;
                if ((fixedFacet & FACET_FRACTIONDIGITS) != 0)
                    fFixedFacet |= FACET_FRACTIONDIGITS;
            }
        }

        // token type: internal use, so do less checking
        if (tokenType != SPECIAL_TOKEN_NONE) {
            fTokenType = tokenType;
        }

        // step 2: check facets against each other: length, bounds
        if(fFacetsDefined != 0) {

            // check 4.3.1.c1 error: length & (maxLength | minLength)
            if((fFacetsDefined & FACET_LENGTH) != 0 ){
              if ((fFacetsDefined & FACET_MINLENGTH) != 0 ||
                  (fFacetsDefined & FACET_MAXLENGTH) != 0 ) {
                  reportError("length-minLength-maxLength", null);
              }
            }

            // check 4.3.2.c1 must: minLength <= maxLength
            if(((fFacetsDefined & FACET_MINLENGTH ) != 0 ) && ((fFacetsDefined & FACET_MAXLENGTH) != 0))
            {
              if(fMinLength > fMaxLength)
                reportError("minLength-less-than-equal-to-maxLength", new Object[]{Integer.toString(fMinLength), Integer.toString(fMaxLength)});
            }

            // check 4.3.8.c1 error: maxInclusive + maxExclusive
            if (((fFacetsDefined & FACET_MAXEXCLUSIVE) != 0) && ((fFacetsDefined & FACET_MAXINCLUSIVE) != 0)) {
                reportError( "maxInclusive-maxExclusive", null);
            }

            // check 4.3.9.c1 error: minInclusive + minExclusive
            if (((fFacetsDefined & FACET_MINEXCLUSIVE) != 0) && ((fFacetsDefined & FACET_MININCLUSIVE) != 0)) {
                reportError("minInclusive-minExclusive", null);
            }

            // check 4.3.7.c1 must: minInclusive <= maxInclusive
            if (((fFacetsDefined &  FACET_MAXINCLUSIVE) != 0) && ((fFacetsDefined & FACET_MININCLUSIVE) != 0)) {
              result = fDVs[fValidationDV].compare(fMinInclusive, fMaxInclusive);
              if (result != -1 && result != 0)
                reportError("minInclusive-less-than-equal-to-maxInclusive", new Object[]{getStringValue(fMinInclusive), getStringValue(fMaxInclusive)});
            }

            // check 4.3.8.c2 must: minExclusive <= maxExclusive ??? minExclusive < maxExclusive
            if (((fFacetsDefined & FACET_MAXEXCLUSIVE) != 0) && ((fFacetsDefined & FACET_MINEXCLUSIVE) != 0)) {
              result = fDVs[fValidationDV].compare(fMinExclusive, fMaxExclusive);
              if (result != -1 && result != 0)
                reportError( "minExclusive-less-than-equal-to-maxExclusive", new Object[]{getStringValue(fMinExclusive), getStringValue(fMaxExclusive)});
            }

            // check 4.3.9.c2 must: minExclusive < maxInclusive
            if (((fFacetsDefined & FACET_MAXINCLUSIVE) != 0) && ((fFacetsDefined & FACET_MINEXCLUSIVE) != 0)) {
              if (fDVs[fValidationDV].compare(fMinExclusive, fMaxInclusive) != -1)
                reportError( "minExclusive-less-than-maxInclusive", new Object[]{getStringValue(fMinExclusive), getStringValue(fMaxInclusive)});
            }

            // check 4.3.10.c1 must: minInclusive < maxExclusive
            if (((fFacetsDefined & FACET_MAXEXCLUSIVE) != 0) && ((fFacetsDefined & FACET_MININCLUSIVE) != 0)) {
              if (fDVs[fValidationDV].compare(fMinInclusive, fMaxExclusive) != -1)
                reportError( "minInclusive-less-than-maxExclusive", new Object[]{getStringValue(fMinInclusive), getStringValue(fMaxExclusive)});
            }

            // check 4.3.12.c1 must: fractionDigits <= totalDigits
            if (((fFacetsDefined & FACET_FRACTIONDIGITS) != 0) &&
                ((fFacetsDefined & FACET_TOTALDIGITS) != 0)) {
                if (fFractionDigits > fTotalDigits)
                    reportError( "fractionDigits-totalDigits", new Object[]{Integer.toString(fFractionDigits), Integer.toString(fTotalDigits)});
            }

            // step 3: check facets against base
            // check 4.3.1.c1 error: length & (fBase.maxLength | fBase.minLength)
            if ( ((fFacetsDefined & FACET_LENGTH ) != 0 ) ) {
                if ((fBase.fFacetsDefined & FACET_MAXLENGTH ) != 0 ||
                    (fBase.fFacetsDefined & FACET_MINLENGTH ) != 0 ) {
                    reportError("length-minLength-maxLength", null);
                }
                else if ( (fBase.fFacetsDefined & FACET_LENGTH) != 0 ) {
                    // check 4.3.1.c2 error: length != fBase.length
                    if ( fLength != fBase.fLength )
                        reportError( "length-valid-restriction", new Object[]{Integer.toString(fLength), Integer.toString(fBase.fLength)});
                }
            }

            // check 4.3.1.c1 error: fBase.length & (maxLength | minLength)
            if ( ((fBase.fFacetsDefined & FACET_LENGTH ) != 0 ) ) {
                if ((fFacetsDefined & FACET_MAXLENGTH ) != 0 ||
                    (fFacetsDefined & FACET_MINLENGTH ) != 0 ) {
                    reportError("length-minLength-maxLength", null);
                }
            }

            // check 4.3.2.c1 must: minLength <= fBase.maxLength
            if ( ((fFacetsDefined & FACET_MINLENGTH ) != 0 ) ) {
                if ( (fBase.fFacetsDefined & FACET_MAXLENGTH ) != 0 ) {
                    if ( fMinLength > fBase.fMaxLength ) {
                        reportError("minLength-less-than-equal-to-maxLength", new Object[]{Integer.toString(fMinLength), Integer.toString(fBase.fMaxLength)});
                    }
                }
                else if ( (fBase.fFacetsDefined & FACET_MINLENGTH) != 0 ) {
                    if ( (fBase.fFixedFacet & FACET_MINLENGTH) != 0 && fMinLength != fBase.fMinLength ) {
                        reportError( "FixedFacetValue", new Object[]{"minLength", Integer.toString(fMinLength), Integer.toString(fBase.fMinLength)});
                    }

                    // check 4.3.2.c2 error: minLength < fBase.minLength
                    if ( fMinLength < fBase.fMinLength ) {
                        reportError( "minLength-valid-restriction", new Object[]{Integer.toString(fMinLength), Integer.toString(fBase.fMinLength)});
                    }
                }
            }


            // check 4.3.2.c1 must: maxLength < fBase.minLength
            if ( ((fFacetsDefined & FACET_MAXLENGTH ) != 0 ) && ((fBase.fFacetsDefined & FACET_MINLENGTH ) != 0 )) {
                if ( fMaxLength < fBase.fMinLength) {
                    reportError("minLength-less-than-equal-to-maxLength", new Object[]{Integer.toString(fBase.fMinLength), Integer.toString(fMaxLength)});
                }
            }

            // check 4.3.3.c1 error: maxLength > fBase.maxLength
            if ( (fFacetsDefined & FACET_MAXLENGTH) != 0 ) {
                if ( (fBase.fFacetsDefined & FACET_MAXLENGTH) != 0 ){
                    if(( (fBase.fFixedFacet & FACET_MAXLENGTH) != 0 )&& fMaxLength != fBase.fMaxLength ) {
                        reportError( "FixedFacetValue", new Object[]{"maxLength", Integer.toString(fMaxLength), Integer.toString(fBase.fMaxLength)});
                    }
                    if ( fMaxLength > fBase.fMaxLength ) {
                        reportError( "maxLength-valid-restriction", new Object[]{Integer.toString(fMaxLength), Integer.toString(fBase.fMaxLength)});
                    }
                }
            }


            // check 4.3.7.c2 error:
            // maxInclusive > fBase.maxInclusive
            // maxInclusive >= fBase.maxExclusive
            // maxInclusive < fBase.minInclusive
            // maxInclusive <= fBase.minExclusive

            if (((fFacetsDefined & FACET_MAXINCLUSIVE) != 0)) {
                if (((fBase.fFacetsDefined & FACET_MAXINCLUSIVE) != 0)) {
                    result = fDVs[fValidationDV].compare(fMaxInclusive, fBase.fMaxInclusive);
                    if ((fBase.fFixedFacet & FACET_MAXINCLUSIVE) != 0 && result != 0) {
                        reportError( "FixedFacetValue", new Object[]{"maxInclusive", getStringValue(fMaxInclusive), getStringValue(fBase.fMaxInclusive)});
                    }
                    if (result != -1 && result != 0) {
                        reportError( "maxInclusive-valid-restriction.1", new Object[]{getStringValue(fMaxInclusive), getStringValue(fBase.fMaxInclusive)});
                    }
                }
                if (((fBase.fFacetsDefined & FACET_MAXEXCLUSIVE) != 0) &&
                    fDVs[fValidationDV].compare(fMaxInclusive, fBase.fMaxExclusive) != -1){
                        reportError( "maxInclusive-valid-restriction.1", new Object[]{getStringValue(fMaxInclusive), getStringValue(fBase.fMaxExclusive)});
                }

                if ((( fBase.fFacetsDefined & FACET_MININCLUSIVE) != 0)) {
                    result = fDVs[fValidationDV].compare(fMaxInclusive, fBase.fMinInclusive);
                    if (result != 1 && result != 0) {
                        reportError( "maxInclusive-valid-restriction.1", new Object[]{getStringValue(fMaxInclusive), getStringValue(fBase.fMinInclusive)});
                    }
                }

                if ((( fBase.fFacetsDefined & FACET_MINEXCLUSIVE) != 0) &&
                    fDVs[fValidationDV].compare(fMaxInclusive, fBase.fMinExclusive ) != 1)
                    reportError( "maxInclusive-valid-restriction.1", new Object[]{getStringValue(fMaxInclusive), getStringValue(fBase.fMinExclusive)});
            }

            // check 4.3.8.c3 error:
            // maxExclusive > fBase.maxExclusive
            // maxExclusive > fBase.maxInclusive
            // maxExclusive <= fBase.minInclusive
            // maxExclusive <= fBase.minExclusive
            if (((fFacetsDefined & FACET_MAXEXCLUSIVE) != 0)) {
                if ((( fBase.fFacetsDefined & FACET_MAXEXCLUSIVE) != 0)) {
                    result= fDVs[fValidationDV].compare(fMaxExclusive, fBase.fMaxExclusive);
                    if ((fBase.fFixedFacet & FACET_MAXEXCLUSIVE) != 0 &&  result != 0) {
                        reportError( "FixedFacetValue", new Object[]{"maxExclusive", getStringValue(fMaxExclusive), getStringValue(fBase.fMaxExclusive)});
                    }
                    if (result != -1 && result != 0) {
                        reportError( "maxExclusive-valid-restriction.1", new Object[]{getStringValue(fMaxExclusive), getStringValue(fBase.fMaxExclusive)});
                    }
                }

                if ((( fBase.fFacetsDefined & FACET_MAXINCLUSIVE) != 0)) {
                    result= fDVs[fValidationDV].compare(fMaxExclusive, fBase.fMaxInclusive);
                    if (result != -1 && result != 0) {
                        reportError( "maxExclusive-valid-restriction.2", new Object[]{getStringValue(fMaxExclusive), getStringValue(fBase.fMaxInclusive)});
                    }
                }

                if ((( fBase.fFacetsDefined & FACET_MINEXCLUSIVE) != 0) &&
                    fDVs[fValidationDV].compare(fMaxExclusive, fBase.fMinExclusive ) != 1)
                    reportError( "maxExclusive-valid-restriction.3", new Object[]{getStringValue(fMaxExclusive), getStringValue(fBase.fMinExclusive)});

                if ((( fBase.fFacetsDefined & FACET_MININCLUSIVE) != 0) &&
                    fDVs[fValidationDV].compare(fMaxExclusive, fBase.fMinInclusive) != 1)
                    reportError( "maxExclusive-valid-restriction.4", new Object[]{getStringValue(fMaxExclusive), getStringValue(fBase.fMinInclusive)});
            }

            // check 4.3.9.c3 error:
            // minExclusive < fBase.minExclusive
            // minExclusive > fBase.maxInclusive
            // minExclusive < fBase.minInclusive
            // minExclusive >= fBase.maxExclusive
            if (((fFacetsDefined & FACET_MINEXCLUSIVE) != 0)) {
                if ((( fBase.fFacetsDefined & FACET_MINEXCLUSIVE) != 0)) {
                    result= fDVs[fValidationDV].compare(fMinExclusive, fBase.fMinExclusive);
                    if ((fBase.fFixedFacet & FACET_MINEXCLUSIVE) != 0 && result != 0) {
                        reportError( "FixedFacetValue", new Object[]{"minExclusive", getStringValue(fMinExclusive), getStringValue(fBase.fMinExclusive)});
                    }
                    if (result != 1 && result != 0) {
                        reportError( "minExclusive-valid-restriction.1", new Object[]{getStringValue(fMinExclusive), getStringValue(fBase.fMinExclusive)});
                    }
                }

                if ((( fBase.fFacetsDefined & FACET_MAXINCLUSIVE) != 0)) {
                    result=fDVs[fValidationDV].compare(fMinExclusive, fBase.fMaxInclusive);

                    if (result != -1 && result != 0) {
                        reportError( "minExclusive-valid-restriction.2", new Object[]{getStringValue(fMinExclusive), getStringValue(fBase.fMaxInclusive)});
                    }
                }

                if ((( fBase.fFacetsDefined & FACET_MININCLUSIVE) != 0)) {
                    result = fDVs[fValidationDV].compare(fMinExclusive, fBase.fMinInclusive);

                    if (result != 1 && result != 0) {
                        reportError( "minExclusive-valid-restriction.3", new Object[]{getStringValue(fMinExclusive), getStringValue(fBase.fMinInclusive)});
                    }
                }

                if ((( fBase.fFacetsDefined & FACET_MAXEXCLUSIVE) != 0) &&
                    fDVs[fValidationDV].compare(fMinExclusive, fBase.fMaxExclusive) != -1)
                    reportError( "minExclusive-valid-restriction.4", new Object[]{getStringValue(fMinExclusive), getStringValue(fBase.fMaxExclusive)});
            }

            // check 4.3.10.c2 error:
            // minInclusive < fBase.minInclusive
            // minInclusive > fBase.maxInclusive
            // minInclusive <= fBase.minExclusive
            // minInclusive >= fBase.maxExclusive
            if (((fFacetsDefined & FACET_MININCLUSIVE) != 0)) {
                if (((fBase.fFacetsDefined & FACET_MININCLUSIVE) != 0)) {
                    result = fDVs[fValidationDV].compare(fMinInclusive, fBase.fMinInclusive);

                    if ((fBase.fFixedFacet & FACET_MININCLUSIVE) != 0 && result != 0) {
                        reportError( "FixedFacetValue", new Object[]{"minInclusive", getStringValue(fMinInclusive), getStringValue(fBase.fMinInclusive)});
                    }
                    if (result != 1 && result != 0) {
                        reportError( "minInclusive-valid-restriction.1", new Object[]{getStringValue(fMinInclusive), getStringValue(fBase.fMinInclusive)});
                    }
                }
                if ((( fBase.fFacetsDefined & FACET_MAXINCLUSIVE) != 0)) {
                    result=fDVs[fValidationDV].compare(fMinInclusive, fBase.fMaxInclusive);
                    if (result != -1 && result != 0) {
                        reportError( "minInclusive-valid-restriction.2", new Object[]{getStringValue(fMinInclusive), getStringValue(fBase.fMaxInclusive)});
                    }
                }
                if ((( fBase.fFacetsDefined & FACET_MINEXCLUSIVE) != 0) &&
                    fDVs[fValidationDV].compare(fMinInclusive, fBase.fMinExclusive ) != 1)
                    reportError( "minInclusive-valid-restriction.3", new Object[]{getStringValue(fMinInclusive), getStringValue(fBase.fMinExclusive)});
                if ((( fBase.fFacetsDefined & FACET_MAXEXCLUSIVE) != 0) &&
                    fDVs[fValidationDV].compare(fMinInclusive, fBase.fMaxExclusive) != -1)
                    reportError( "minInclusive-valid-restriction.4", new Object[]{getStringValue(fMinInclusive), getStringValue(fBase.fMaxExclusive)});
            }

            // check 4.3.11.c1 error: totalDigits > fBase.totalDigits
            if (((fFacetsDefined & FACET_TOTALDIGITS) != 0)) {
                if ((( fBase.fFacetsDefined & FACET_TOTALDIGITS) != 0)) {
                    if ((fBase.fFixedFacet & FACET_TOTALDIGITS) != 0 && fTotalDigits != fBase.fTotalDigits) {
                        reportError("FixedFacetValue", new Object[]{"totalDigits", Integer.toString(fTotalDigits), Integer.toString(fBase.fTotalDigits)});
                    }
                    if (fTotalDigits > fBase.fTotalDigits) {
                        reportError( "totalDigits-valid-restriction", new Object[]{Integer.toString(fTotalDigits), Integer.toString(fBase.fTotalDigits)});
                    }
                }
            }

            // check fixed value for fractionDigits
            if (((fFacetsDefined & FACET_FRACTIONDIGITS) != 0)) {
                if ((( fBase.fFacetsDefined & FACET_FRACTIONDIGITS) != 0)) {
                    if ((fBase.fFixedFacet & FACET_FRACTIONDIGITS) != 0 && fFractionDigits != fBase.fFractionDigits) {
                        reportError("FixedFacetValue", new Object[]{"fractionDigits", Integer.toString(fFractionDigits), Integer.toString( fBase.fFractionDigits)});
                    }
                }
            }

            // check 4.3.6.c1 error:
            // (whiteSpace = preserve || whiteSpace = replace) && fBase.whiteSpace = collapese or
            // whiteSpace = preserve && fBase.whiteSpace = replace

            if ( (fFacetsDefined & FACET_WHITESPACE) != 0 && (fBase.fFacetsDefined & FACET_WHITESPACE) != 0 ){
                if ( (fBase.fFixedFacet & FACET_WHITESPACE) != 0 &&  fWhiteSpace != fBase.fWhiteSpace ) {
                    reportError( "FixedFacetValue", new Object[]{"whiteSpace", whiteSpaceValue(fWhiteSpace), whiteSpaceValue(fBase.fWhiteSpace)});
                }

                if ( (fWhiteSpace == WS_PRESERVE || fWhiteSpace == WS_REPLACE) &&  fBase.fWhiteSpace == WS_COLLAPSE ){
                    reportError( "whiteSpace-valid-restriction.1", null);
                }
                if ( fWhiteSpace == WS_PRESERVE &&  fBase.fWhiteSpace == WS_REPLACE ){
                    reportError( "whiteSpace-valid-restriction.2", null);
                }
            }
        }//fFacetsDefined != null

        // step 4: inherit other facets from base (including fTokeyType)

        // inherit length
        if ( (fFacetsDefined & FACET_LENGTH) == 0  && (fBase.fFacetsDefined & FACET_LENGTH) != 0 ) {
            fFacetsDefined |= FACET_LENGTH;
            fLength = fBase.fLength;
        }
        // inherit minLength
        if ( (fFacetsDefined & FACET_MINLENGTH) == 0 && (fBase.fFacetsDefined & FACET_MINLENGTH) != 0 ) {
            fFacetsDefined |= FACET_MINLENGTH;
            fMinLength = fBase.fMinLength;
        }
        // inherit maxLength
        if ((fFacetsDefined & FACET_MAXLENGTH) == 0 &&  (fBase.fFacetsDefined & FACET_MAXLENGTH) != 0 ) {
            fFacetsDefined |= FACET_MAXLENGTH;
            fMaxLength = fBase.fMaxLength;
        }
        // inherit pattern //???
        if ( (fBase.fFacetsDefined & FACET_PATTERN) != 0 ) {
            if ((fFacetsDefined & FACET_PATTERN) == 0) {
                fPattern = new Vector();
                fFacetsDefined |= FACET_PATTERN;
            }
            for (int i = fBase.fPattern.size()-1; i >= 0; i--)
                fPattern.addElement(fBase.fPattern.elementAt(i));

        }
        // inherit whiteSpace
        if ( (fFacetsDefined & FACET_WHITESPACE) == 0 &&  (fBase.fFacetsDefined & FACET_WHITESPACE) != 0 ) {
            fFacetsDefined |= FACET_WHITESPACE;
            fWhiteSpace = fBase.fWhiteSpace;
        }
        // inherit enumeration
        if ((fFacetsDefined & FACET_ENUMERATION) == 0 && (fBase.fFacetsDefined & FACET_ENUMERATION) != 0) {
            fFacetsDefined |= FACET_ENUMERATION;
            fEnumeration = fBase.fEnumeration;
        }
        // inherit maxExclusive
        if ((( fBase.fFacetsDefined & FACET_MAXEXCLUSIVE) != 0) &&
            !((fFacetsDefined & FACET_MAXEXCLUSIVE) != 0) && !((fFacetsDefined & FACET_MAXINCLUSIVE) != 0)) {
            fFacetsDefined |= FACET_MAXEXCLUSIVE;
            fMaxExclusive = fBase.fMaxExclusive;
        }
        // inherit maxInclusive
        if ((( fBase.fFacetsDefined & FACET_MAXINCLUSIVE) != 0) &&
            !((fFacetsDefined & FACET_MAXEXCLUSIVE) != 0) && !((fFacetsDefined & FACET_MAXINCLUSIVE) != 0)) {
            fFacetsDefined |= FACET_MAXINCLUSIVE;
            fMaxInclusive = fBase.fMaxInclusive;
        }
        // inherit minExclusive
        if ((( fBase.fFacetsDefined & FACET_MINEXCLUSIVE) != 0) &&
            !((fFacetsDefined & FACET_MINEXCLUSIVE) != 0) && !((fFacetsDefined & FACET_MININCLUSIVE) != 0)) {
            fFacetsDefined |= FACET_MINEXCLUSIVE;
            fMinExclusive = fBase.fMinExclusive;
        }
        // inherit minExclusive
        if ((( fBase.fFacetsDefined & FACET_MININCLUSIVE) != 0) &&
            !((fFacetsDefined & FACET_MINEXCLUSIVE) != 0) && !((fFacetsDefined & FACET_MININCLUSIVE) != 0)) {
            fFacetsDefined |= FACET_MININCLUSIVE;
            fMinInclusive = fBase.fMinInclusive;
        }
        // inherit totalDigits
        if ((( fBase.fFacetsDefined & FACET_TOTALDIGITS) != 0) &&
            !((fFacetsDefined & FACET_TOTALDIGITS) != 0)) {
            fFacetsDefined |= FACET_TOTALDIGITS;
            fTotalDigits = fBase.fTotalDigits;
        }
        // inherit fractionDigits
        if ((( fBase.fFacetsDefined & FACET_FRACTIONDIGITS) != 0)
            && !((fFacetsDefined & FACET_FRACTIONDIGITS) != 0)) {
            fFacetsDefined |= FACET_FRACTIONDIGITS;
            fFractionDigits = fBase.fFractionDigits;
        }
        //inherit tokeytype
        if ((fTokenType == SPECIAL_TOKEN_NONE ) && (fBase.fTokenType != SPECIAL_TOKEN_NONE)) {
            fTokenType = fBase.fTokenType ;
        }

        // step 5: mark fixed values
        fFixedFacet |= fBase.fFixedFacet;

        //step 6: setting fundamental facets
        caclFundamentalFacets();

    } //applyFacets()

    /**
     * validate a value, and return the compiled form
     */
    public Object validate(String content, ValidationContext context, ValidatedInfo validatedInfo) throws InvalidDatatypeValueException {

        // first normalize string value, and convert it to actual value
        Object ob = getActualValue(content, context, fTempInfo);

        validate(context, fTempInfo);

        if (validatedInfo != null) {
            validatedInfo.actualValue = fTempInfo.actualValue;
            validatedInfo.normalizedValue = fTempInfo.normalizedValue;
            validatedInfo.memberType = fTempInfo.memberType;
            validatedInfo.memberTypes = fTempInfo.memberTypes;
        }

        return ob;

    }

    /**
     * validate an actual value against this DV
     *
     * @param value         the actual value that needs to be validated
     * @param context       the validation context
     * @param validatedInfo used to provide the actual value and member types
     */
    public void validate(ValidationContext context, ValidatedInfo validatedInfo)
        throws InvalidDatatypeValueException {

        // then validate the actual value against the facets
        if (context.needFacetChecking() &&
            (fFacetsDefined != 0 && fFacetsDefined != FACET_WHITESPACE)) {
            checkFacets(validatedInfo);
        }

        // now check extra rules: for ID/IDREF/ENTITY
        if (context.needExtraChecking()) {
            checkExtraRules(context, validatedInfo);
        }

    }

    private void checkFacets(ValidatedInfo validatedInfo) throws InvalidDatatypeValueException {

        Object ob = validatedInfo.actualValue;
        String content = validatedInfo.normalizedValue;

        int length = fDVs[fValidationDV].getDataLength(ob);

        // maxLength
        if ( (fFacetsDefined & FACET_MAXLENGTH) != 0 ) {
            if ( length > fMaxLength ) {
                throw new InvalidDatatypeValueException("cvc-maxLength-valid",
                                                        new Object[]{content, Integer.toString(length), Integer.toString(fMaxLength)});
            }
        }

        //minLength
        if ( (fFacetsDefined & FACET_MINLENGTH) != 0 ) {
            if ( length < fMinLength ) {
                throw new InvalidDatatypeValueException("cvc-minLength-valid",
                                                        new Object[]{content, Integer.toString(length), Integer.toString(fMinLength)});
            }
        }

        //length
        if ( (fFacetsDefined & FACET_LENGTH) != 0 ) {
            if ( length != fLength ) {
                throw new InvalidDatatypeValueException("cvc-length-valid",
                                                        new Object[]{content, Integer.toString(length), Integer.toString(fLength)});
            }
        }

        //enumeration
        if ( ((fFacetsDefined & FACET_ENUMERATION) != 0 ) ) {
            boolean present = false;
            for (int i = 0; i < fEnumeration.size(); i++) {
                if (isEqual(ob, fEnumeration.elementAt(i))) {
                    present = true;
                    break;
                }
            }
            if(!present){
                throw new InvalidDatatypeValueException("cvc-enumeration-valid",
                                                        new Object [] {content, fEnumeration.toString()});
            }
        }

        //fractionDigits
        if ((fFacetsDefined & FACET_FRACTIONDIGITS) != 0) {
            int scale = fDVs[fValidationDV].getFractionDigits(ob);
            if (scale > fFractionDigits) {
                throw new InvalidDatatypeValueException("cvc-fractionDigits-valid",
                                                        new Object[] {content, Integer.toString(scale), Integer.toString(fFractionDigits)});
            }
        }

        //totalDigits
        if ((fFacetsDefined & FACET_TOTALDIGITS)!=0) {
            int totalDigits = fDVs[fValidationDV].getTotalDigits(ob);
            if (totalDigits > fTotalDigits) {
                throw new InvalidDatatypeValueException("cvc-totalDigits-valid",
                                                        new Object[] {content, Integer.toString(totalDigits), Integer.toString(fTotalDigits)});
            }
        }

        int compare;

        //maxinclusive
        if ( (fFacetsDefined & FACET_MAXINCLUSIVE) != 0 ) {
            compare = fDVs[fValidationDV].compare(ob, fMaxInclusive);
            if (compare != -1 && compare != 0) {
                throw new InvalidDatatypeValueException("cvc-maxInclusive-valid",
                                                        new Object[] {content, fMaxInclusive});
            }
        }

        //maxExclusive
        if ( (fFacetsDefined & FACET_MAXEXCLUSIVE) != 0 ) {
            compare = fDVs[fValidationDV].compare(ob, fMaxExclusive );
            if (compare != -1) {
                throw new InvalidDatatypeValueException("cvc-maxExclusive-valid",
                                                        new Object[] {content, fMaxExclusive});
            }
        }

        //minInclusive
        if ( (fFacetsDefined & FACET_MININCLUSIVE) != 0 ) {
            compare = fDVs[fValidationDV].compare(ob, fMinInclusive);
            if (compare != 1 && compare != 0) {
                throw new InvalidDatatypeValueException("cvc-minInclusive-valid",
                                                        new Object[] {content, fMinInclusive});
            }
        }

        //minExclusive
        if ( (fFacetsDefined & FACET_MINEXCLUSIVE) != 0 ) {
            compare = fDVs[fValidationDV].compare(ob, fMinExclusive);
            if (compare != 1) {
                throw new InvalidDatatypeValueException("cvc-minExclusive-valid",
                                                        new Object[] {content, fMinExclusive});
            }
        }

    }

    private void checkExtraRules(ValidationContext context, ValidatedInfo validatedInfo) throws InvalidDatatypeValueException {

        Object ob = validatedInfo.actualValue;

        if (fVariety == VARIETY_ATOMIC) {

            fDVs[fValidationDV].checkExtraRules(ob, context);

        } else if (fVariety == VARIETY_LIST) {

            Object[] values = (Object[])ob;
            if (fItemType.fVariety == VARIETY_UNION) {
                XSSimpleTypeDecl[] memberTypes = (XSSimpleTypeDecl[])validatedInfo.memberTypes;
                XSSimpleType memberType = validatedInfo.memberType;
                for (int i = values.length-1; i >= 0; i--) {
                    validatedInfo.actualValue = values[i];
                    validatedInfo.memberType = memberTypes[i];
                    fItemType.checkExtraRules(context, validatedInfo);
                }
                validatedInfo.memberType = memberType;
            } else { // (fVariety == VARIETY_ATOMIC)
                for (int i = values.length-1; i >= 0; i--) {
                    validatedInfo.actualValue = values[i];
                    fItemType.checkExtraRules(context, validatedInfo);
                }
            }
            validatedInfo.actualValue = values;

        } else { // (fVariety == VARIETY_UNION)

            ((XSSimpleTypeDecl)validatedInfo.memberType).checkExtraRules(context, validatedInfo);

        }

    }// checkExtraRules()

    //we can still return object for internal use.
    private Object getActualValue(String content, ValidationContext context, ValidatedInfo validatedInfo) throws InvalidDatatypeValueException{

        if (fVariety == VARIETY_ATOMIC) {

            String nvalue = normalize(content, fWhiteSpace);

            // validate special kinds of token, in place of old pattern matching
            if (fTokenType != SPECIAL_TOKEN_NONE) {

                boolean seenErr = false;
                if (fTokenType == SPECIAL_TOKEN_NMTOKEN) {
                    // PATTERN "\\c+"
                    seenErr = !XMLChar.isValidNmtoken(nvalue);
                }
                else if (fTokenType == SPECIAL_TOKEN_NAME) {
                    // PATTERN "\\i\\c*"
                    seenErr = !XMLChar.isValidName(nvalue);
                }
                else if (fTokenType == SPECIAL_TOKEN_NCNAME) {
                    // PATTERN "[\\i-[:]][\\c-[:]]*"
                    // REVISIT: !!!NOT IMPLEMENTED in XMLChar
                    seenErr = !XMLChar.isValidNCName(nvalue);
                }
                if (seenErr) {
                    throw new InvalidDatatypeValueException("cvc-datatype-valid.1.2.1",
                                                            new Object[]{nvalue, SPECIAL_TOKEN_STRING[fTokenType]});
                }
            }

            if ( (fFacetsDefined & FACET_PATTERN ) != 0 ) {
                RegularExpression regex;
                for (int idx = fPattern.size()-1; idx >= 0; idx--) {
                    regex = (RegularExpression)fPattern.elementAt(idx);
                    if (!regex.matches(nvalue)){
                        throw new InvalidDatatypeValueException("cvc-pattern-valid",
                                                                new Object[]{content, regex});
                    }
                }
            }

            Object avalue = fDVs[fValidationDV].getActualValue(nvalue, context);

            validatedInfo.actualValue = avalue;
            validatedInfo.normalizedValue = nvalue;

            return avalue;

        } else if (fVariety == VARIETY_LIST) {

            String nvalue = normalize(content, fWhiteSpace);
            StringTokenizer parsedList = new StringTokenizer(nvalue);
            int countOfTokens = parsedList.countTokens() ;
            Object[] avalue = new Object[countOfTokens];
            XSSimpleTypeDecl[] memberTypes = new XSSimpleTypeDecl[countOfTokens];
            for(int i = 0 ; i < countOfTokens ; i ++){
                // we can't call fItemType.validate(), otherwise checkExtraRules()
                // will be called twice: once in fItemType.validate, once in
                // validate method of this type.
                // so we take two steps to get the actual value:
                // 1. fItemType.getActualValue()
                // 2. fItemType.chekcFacets()
                avalue[i] = fItemType.getActualValue(parsedList.nextToken(), context, validatedInfo);
                if (context.needFacetChecking() &&
                    (fItemType.fFacetsDefined != 0 && fItemType.fFacetsDefined != FACET_WHITESPACE)) {
                    fItemType.checkFacets(validatedInfo);
                }
                memberTypes[i] = (XSSimpleTypeDecl)validatedInfo.memberType;
            }

            validatedInfo.actualValue = avalue;
            validatedInfo.normalizedValue = nvalue;
            validatedInfo.memberTypes = memberTypes;

            return avalue;

        } else { // (fVariety == VARIETY_UNION)
            for(int i = 0 ; i < fMemberTypes.length; i++) {
                try {
                    // we can't call fMemberType[i].validate(), otherwise checkExtraRules()
                    // will be called twice: once in fMemberType[i].validate, once in
                    // validate method of this type.
                    // so we take two steps to get the actual value:
                    // 1. fMemberType[i].getActualValue()
                    // 2. fMemberType[i].chekcFacets()
                    Object aValue = fMemberTypes[i].getActualValue(content, context, validatedInfo);
                    if (context.needFacetChecking() &&
                        (fMemberTypes[i].fFacetsDefined != 0 && fMemberTypes[i].fFacetsDefined != FACET_WHITESPACE)) {
                        fMemberTypes[i].checkFacets(validatedInfo);
                    }
                    validatedInfo.memberType = fMemberTypes[i];
                    return aValue;
                } catch(InvalidDatatypeValueException invalidValue) {
                }
            }

            throw new InvalidDatatypeValueException("cvc-datatype-valid.1.2.2",
                                                    new Object[]{content, fTypeName});
        }

    }//getActualValue()


    public boolean isEqual(Object value1, Object value2) {

        if (fVariety == VARIETY_ATOMIC)
            return fDVs[fValidationDV].isEqual(value1,value2);

        else if (fVariety == VARIETY_LIST) {
            if (!(value1 instanceof Object[]) || !(value2 instanceof Object[]))
                return false;

            Object[] v1 = (Object[])value1;
            Object[] v2 = (Object[])value2;

            int count = v1.length;
            if (count != v2.length)
                return false;

            for (int i = 0 ; i < count ; i++) {
                if (!fItemType.isEqual(v1[i], v2[i]))
                    return false;
            }//end of loop

            //everything went fine.
            return true;

        } else if (fVariety == VARIETY_UNION) {
            for (int i = fMemberTypes.length-1; i >= 0; i--) {
                if (fMemberTypes[i].isEqual(value1,value2)){
                    return true;
                }
            }
            return false;
        }

        return false;
    }//isEqual()

    // normalize the string according to the whiteSpace facet
    public static String normalize(String content, short ws) {
        int len = content == null ? 0 : content.length();
        if (len == 0 || ws == WS_PRESERVE)
            return content;

        StringBuffer sb = new StringBuffer();
        if (ws == WS_REPLACE) {
            char ch;
            // when it's replace, just replace #x9, #xa, #xd by #x20
            for (int i = 0; i < len; i++) {
                ch = content.charAt(i);
                if (ch != 0x9 && ch != 0xa && ch != 0xd)
                    sb.append(ch);
                else
                    sb.append((char)0x20);
            }
        } else {
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

    void reportError(String key, Object[] args) throws InvalidDatatypeFacetException {
        throw new InvalidDatatypeFacetException(key, args);
    }


    private String whiteSpaceValue(short ws){
        return WS_FACET_STRING[ws];
    }

    public String getStringValue(Object value){
        if(value != null) {
            if (fDVs[fValidationDV] instanceof AbstractDateTimeDV)
                return ((AbstractDateTimeDV)fDVs[fValidationDV]).dateToString((int[])value);
            else
                return value.toString();
        } else {
            return null;
        }
    }

    public short getOrderedFacet() {
        return fOrdered;
    }

    public boolean isBounded(){
        return fBounded;
    }

    public short getCardinalityFacet(){
        return fCardinality;
    }

    public boolean isNumeric(){
        return fNumeric;
    }

    private void caclFundamentalFacets() {
        setOrdered();
        setNumeric();
        setBounded();
        setCardinality();
    }

    private void setOrdered(){

        // When {variety} is atomic, {value} is inherited from {value} of {base type definition}. For all ·primitive· types {value} is as specified in the table in Fundamental Facets (C.1).
        if(fVariety == VARIETY_ATOMIC){
            this.fOrdered = fBase.fOrdered;
        }

        // When {variety} is list, {value} is false.
        else if(fVariety == VARIETY_LIST){
            this.fOrdered = ORDERED_FALSE;
        }

        // When {variety} is union, the {value} is partial unless one of the following:
        // 1. If every member of {member type definitions} is derived from a common ancestor other than the simple ur-type, then {value} is the same as that ancestor's ordered facet.
        // 2. If every member of {member type definitions} has a {value} of false for the ordered facet, then {value} is false.
        else if(fVariety == VARIETY_UNION){
            int length = fMemberTypes.length;
            // REVISIT: is the length possible to be 0?
            if (length == 0) {
                this.fOrdered = ORDERED_PARTIAL;
                return;
            }
            // we need to process the first member type before entering the loop
            short ancestorId = getPrimitiveDV(fMemberTypes[0].fValidationDV);
            boolean commonAnc = ancestorId != DV_ANYSIMPLETYPE;
            boolean allFalse = fMemberTypes[0].fOrdered == ORDERED_FALSE;
            // for the other member types, check whether the value is false
            // and whether they have the same ancestor as the first one
            for (int i = 1; i < fMemberTypes.length && (commonAnc || allFalse); i++) {
                if (commonAnc)
                    commonAnc = ancestorId == getPrimitiveDV(fMemberTypes[i].fValidationDV);
                if (allFalse)
                    allFalse = fMemberTypes[i].fOrdered == ORDERED_FALSE;
            }
            if (commonAnc) {
                // REVISIT: all member types should have the same ordered value
                //          just use the first one. Can we assume this?
                this.fOrdered = fMemberTypes[0].fOrdered;
            } else if (allFalse) {
                this.fOrdered = ORDERED_FALSE;
            } else {
                this.fOrdered = ORDERED_PARTIAL;
            }
        }

    }//setOrdered

    private void setNumeric(){
        if(fVariety == VARIETY_ATOMIC){
            this.fNumeric = fBase.fNumeric;
        }
        else if(fVariety == VARIETY_LIST){
            this.fNumeric = false;
        }
        else if(fVariety == VARIETY_UNION){
            XSSimpleType [] memberTypes = this.getMemberTypes();
            for(int i = 0 ; i < memberTypes.length ; i++){
                if( ! memberTypes[i].isNumeric() ){
                    this.fNumeric = false;
                    return;
                }
            }
            this.fNumeric = true;
        }

    }//setNumeric

    private void setBounded(){
        if(fVariety == VARIETY_ATOMIC){
            if( (((this.fFacetsDefined & FACET_MININCLUSIVE) != 0)  || ((this.fFacetsDefined & FACET_MINEXCLUSIVE) != 0))
                &&  (((this.fFacetsDefined & FACET_MAXINCLUSIVE) != 0)  || ((this.fFacetsDefined & FACET_MAXEXCLUSIVE) != 0)) ){
                this.fBounded = true;
            }
            else{
                this.fBounded = false;
            }
        }
        else if(fVariety == VARIETY_LIST){
            if( ((this.fFacetsDefined & FACET_LENGTH) != 0 ) || ( ((this.fFacetsDefined & FACET_MINLENGTH) != 0 )
                                                            &&  ((this.fFacetsDefined & FACET_MAXLENGTH) != 0 )) ){
                this.fBounded = true;
            }
            else{
                this.fBounded = false;
            }

        }
        else if(fVariety == VARIETY_UNION){

            XSSimpleTypeDecl [] memberTypes = this.fMemberTypes;
            short ancestorId = 0 ;

            if(memberTypes.length > 0){
                ancestorId = getPrimitiveDV(memberTypes[0].fValidationDV);
            }

            for(int i = 0 ; i < memberTypes.length ; i++){
                if( ! memberTypes[i].isBounded() || (ancestorId != getPrimitiveDV(memberTypes[i].fValidationDV)) ){
                    this.fBounded = false;
                    return;
                }
            }
            this.fBounded = true;
        }

    }//setBounded

    private boolean specialCardinalityCheck(){
        if( (fBase.fValidationDV == XSSimpleTypeDecl.DV_DATE) || (fBase.fValidationDV == XSSimpleTypeDecl.DV_GYEARMONTH)
            || (fBase.fValidationDV == XSSimpleTypeDecl.DV_GYEAR) || (fBase.fValidationDV == XSSimpleTypeDecl.DV_GMONTHDAY)
            || (fBase.fValidationDV == XSSimpleTypeDecl.DV_GDAY) || (fBase.fValidationDV == XSSimpleTypeDecl.DV_GMONTH) ){
            return true;
        }
        return false;

    } //specialCardinalityCheck()

    private void setCardinality(){
        if(fVariety == VARIETY_ATOMIC){
            if(fBase.fCardinality == CARDINALITY_FINITE){
                this.fCardinality = CARDINALITY_FINITE;
            }
            else {// (fBase.fCardinality == CARDINALITY_COUNTABLY_INFINITE)
                if ( ((this.fFacetsDefined & FACET_LENGTH) != 0 ) || ((this.fFacetsDefined & FACET_MAXLENGTH) != 0 )
                     || ((this.fFacetsDefined & FACET_TOTALDIGITS) != 0 ) ){
                    this.fCardinality = CARDINALITY_FINITE;
                }
                else if( (((this.fFacetsDefined & FACET_MININCLUSIVE) != 0 ) || ((this.fFacetsDefined & FACET_MINEXCLUSIVE) != 0 ))
                        && (((this.fFacetsDefined & FACET_MAXINCLUSIVE) != 0 ) || ((this.fFacetsDefined & FACET_MAXEXCLUSIVE) != 0 )) ){
                    if( ((this.fFacetsDefined & FACET_FRACTIONDIGITS) != 0 ) || specialCardinalityCheck()){
                        this.fCardinality = CARDINALITY_FINITE;
                    }
                    else{
                        this.fCardinality = CARDINALITY_COUNTABLY_INFINITE;
                    }
                }
                else{
                    this.fCardinality = CARDINALITY_COUNTABLY_INFINITE;
                }
            }
        }
        else if(fVariety == VARIETY_LIST){
            if( ((this.fFacetsDefined & FACET_LENGTH) != 0 ) || ( ((this.fFacetsDefined & FACET_MINLENGTH) != 0 )
                                                            && ((this.fFacetsDefined & FACET_MAXLENGTH) != 0 )) ){
                this.fCardinality = CARDINALITY_FINITE;
            }
            else{
                this.fCardinality = CARDINALITY_COUNTABLY_INFINITE;
            }

        }
        else if(fVariety == VARIETY_UNION){
            XSSimpleType [] memberTypes = this.getMemberTypes();
            for(int i = 0 ; i < memberTypes.length ; i++){
                if( ! (memberTypes[i].getCardinalityFacet() == CARDINALITY_FINITE) ){
                    this.fCardinality = CARDINALITY_COUNTABLY_INFINITE;
                    return;
                }
            }
            this.fCardinality = CARDINALITY_FINITE;
        }

    }//setCardinality

    private short getPrimitiveDV(short validationDV){

        if (validationDV == DV_ID || validationDV == DV_IDREF || validationDV == DV_ENTITY){
            return DV_STRING;
        }
        else{
            return validationDV;
        }

    }//getPrimitiveDV()

    static final XSSimpleTypeDecl fAnySimpleType = new XSSimpleTypeDecl(null, "anySimpleType", DV_ANYSIMPLETYPE, ORDERED_FALSE, false, CARDINALITY_FINITE, false);

    /**
     * A wrapper of ValidationContext, to provide a way of switching to a
     * different Namespace declaration context.
     */
    class ValidationContextImpl implements ValidationContext {
        ValidationContext fExternal;
        ValidationContextImpl(ValidationContext external) {
            fExternal = external;
        }

        NamespaceContext fNSContext;
        void setNSContext(NamespaceContext nsContext) {
            fNSContext = nsContext;
        }

        public boolean needFacetChecking() {
            return fExternal.needFacetChecking();
        }

        public boolean needExtraChecking() {
            return fExternal.needExtraChecking();
        }

        public boolean isEntityDeclared (String name) {
            return fExternal.isEntityDeclared(name);
        }

        public boolean isEntityUnparsed (String name) {
            return fExternal.isEntityUnparsed(name);
        }

        public boolean isIdDeclared (String name) {
            return fExternal.isIdDeclared(name);
        }

        public void    addId(String name) {
            fExternal.addId(name);
        }

        public void addIdRef(String name) {
            fExternal.addIdRef(name);
        }

        public String getSymbol (String symbol) {
            return fExternal.getSymbol(symbol);
        }

        public String getURI(String prefix) {
            if (fNSContext == null)
                return fExternal.getURI(prefix);
            else
                return fNSContext.getURI(prefix);
        }
    }
} // class XSComplexTypeDecl
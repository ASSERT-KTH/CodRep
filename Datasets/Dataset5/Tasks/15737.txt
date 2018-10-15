if (typeDecl.getTypeCategory() == XSTypeDefinition.SIMPLE_TYPE &&

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 2001, 2002 The Apache Software Foundation.  All rights
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

package org.apache.xerces.impl.xs.traversers;

import java.util.Vector;

import org.apache.xerces.impl.dv.InvalidDatatypeValueException;
import org.apache.xerces.impl.dv.XSFacets;
import org.apache.xerces.impl.dv.XSSimpleType;
import org.apache.xerces.impl.validation.ValidationState;
import org.apache.xerces.impl.xs.SchemaGrammar;
import org.apache.xerces.impl.xs.SchemaSymbols;
import org.apache.xerces.impl.xs.XSAttributeGroupDecl;
import org.apache.xerces.impl.xs.XSAttributeUseImpl;
import org.apache.xerces.impl.xs.XSComplexTypeDecl;
import org.apache.xerces.impl.xs.XSParticleDecl;
import org.apache.xerces.impl.xs.XSWildcardDecl;
import org.apache.xerces.impl.xs.psvi.XSObjectList;
import org.apache.xerces.impl.xs.psvi.XSTypeDefinition;
import org.apache.xerces.impl.xs.util.XInt;
import org.apache.xerces.util.DOMUtil;
import org.apache.xerces.util.NamespaceSupport;
import org.apache.xerces.util.SymbolTable;
import org.apache.xerces.xni.QName;
import org.w3c.dom.Element;

/**
 * Class <code>XSDAbstractTraverser</code> serves as the base class for all
 * other <code>XSD???Traverser</code>s. It holds the common data and provide
 * a unified way to initialize these data.
 *
 * @author Elena Litani, IBM
 * @author Rahul Srivastava, Sun Microsystems Inc.
 * @author Neeraj Bajaj, Sun Microsystems Inc.
 *
 * @version $Id$
 */
abstract class XSDAbstractTraverser {

    protected static final String NO_NAME      = "(no name)";

    // Flags for checkOccurrences to indicate any special
    // restrictions on minOccurs and maxOccurs relating to "all".
    //    NOT_ALL_CONTEXT    - not processing an <all>
    //    PROCESSING_ALL_EL  - processing an <element> in an <all>
    //    GROUP_REF_WITH_ALL - processing <group> reference that contained <all>
    //    CHILD_OF_GROUP     - processing a child of a model group definition
    //    PROCESSING_ALL_GP  - processing an <all> group itself

    protected static final int NOT_ALL_CONTEXT    = 0;
    protected static final int PROCESSING_ALL_EL  = 1;
    protected static final int GROUP_REF_WITH_ALL = 2;
    protected static final int CHILD_OF_GROUP     = 4;
    protected static final int PROCESSING_ALL_GP  = 8;

    //Shared data
    protected XSDHandler            fSchemaHandler = null;
    protected SymbolTable           fSymbolTable = null;
    protected XSAttributeChecker    fAttrChecker = null;

    // used to validate default/fixed attribute values
    ValidationState fValidationState = new ValidationState();

    XSDAbstractTraverser (XSDHandler handler,
                          XSAttributeChecker attrChecker) {
        fSchemaHandler = handler;
        fAttrChecker = attrChecker;
    }

    void reset(SymbolTable symbolTable) {
        fSymbolTable = symbolTable;
        fValidationState.setExtraChecking(false);
        fValidationState.setSymbolTable(symbolTable);
    }

    // traverse the annotation declaration
    // REVISIT: store annotation information for PSVI
    // REVISIT: how to pass the parentAttrs? as DOM attributes?
    //          as name/value pairs (string)? in parsed form?
    // REVISIT: what to return
    void traverseAnnotationDecl(Element annotationDecl, Object[] parentAttrs,
                                boolean isGlobal, XSDocumentInfo schemaDoc) {
        // General Attribute Checking
        Object[] attrValues = fAttrChecker.checkAttributes(annotationDecl, isGlobal, schemaDoc);
        fAttrChecker.returnAttrArray(attrValues, schemaDoc);

        for (Element child = DOMUtil.getFirstChildElement(annotationDecl);
            child != null;
            child = DOMUtil.getNextSiblingElement(child)) {
            String name = DOMUtil.getLocalName(child);

            // the only valid children of "annotation" are
            // "appinfo" and "documentation"
            if (!((name.equals(SchemaSymbols.ELT_APPINFO)) ||
                  (name.equals(SchemaSymbols.ELT_DOCUMENTATION)))) {
                reportSchemaError("src-annotation", null, child);
            }

            // General Attribute Checking
            // There is no difference between global or local appinfo/documentation,
            // so we assume it's always global.
            attrValues = fAttrChecker.checkAttributes(child, true, schemaDoc);
            fAttrChecker.returnAttrArray(attrValues, schemaDoc);
        }

        // REVISIT: an annotation decl should be returned when we support PSVI
    }

    // the QName simple type used to resolve qnames
    private static final XSSimpleType fQNameDV = (XSSimpleType)SchemaGrammar.SG_SchemaNS.getGlobalTypeDecl(SchemaSymbols.ATTVAL_QNAME);
    // Temp data structures to be re-used in traversing facets
    private StringBuffer fPattern = new StringBuffer();
    private final XSFacets xsFacets = new XSFacets();

    class FacetInfo {
        XSFacets facetdata;
        Element nodeAfterFacets;
        short fPresentFacets;
        short fFixedFacets;
    }

    FacetInfo traverseFacets(Element content,
                             XSSimpleType baseValidator,
                             XSDocumentInfo schemaDoc) {

        short facetsPresent = 0 ;
        short facetsFixed = 0; // facets that have fixed="true"

        String facet;
        boolean hasQName = containsQName(baseValidator);
        Vector enumData = new Vector();
        Vector enumNSDecls = hasQName ? new Vector() : null;
        int currentFacet = 0;
        while (content != null) {
            // General Attribute Checking
            Object[] attrs = null;
            facet = DOMUtil.getLocalName(content);
            if (facet.equals(SchemaSymbols.ELT_ENUMERATION)) {
                attrs = fAttrChecker.checkAttributes(content, false, schemaDoc, hasQName);
                String enumVal = (String)attrs[XSAttributeChecker.ATTIDX_VALUE];
                NamespaceSupport nsDecls = (NamespaceSupport)attrs[XSAttributeChecker.ATTIDX_ENUMNSDECLS];

                // for NOTATION types, need to check whether there is a notation
                // declared with the same name as the enumeration value.
                if (baseValidator.getVariety() == XSSimpleType.VARIETY_ATOMIC &&
                    baseValidator.getPrimitiveKind() == XSSimpleType.PRIMITIVE_NOTATION) {
                    // need to use the namespace context returned from checkAttributes
                    schemaDoc.fValidationContext.setNamespaceSupport(nsDecls);
                    try{
                        QName temp = (QName)fQNameDV.validate(enumVal, schemaDoc.fValidationContext, null);
                        // try to get the notation decl. if failed, getGlobalDecl
                        // reports an error, so we don't need to report one again.
                        fSchemaHandler.getGlobalDecl(schemaDoc, XSDHandler.NOTATION_TYPE, temp, content);
                    }catch(InvalidDatatypeValueException ex){
                        reportSchemaError(ex.getKey(), ex.getArgs(), content);
                    }
                    // restore to the normal namespace context
                    schemaDoc.fValidationContext.setNamespaceSupport(schemaDoc.fNamespaceSupport);
                }

                enumData.addElement(enumVal);
                if (hasQName)
                    enumNSDecls.addElement(nsDecls);
                Element child = DOMUtil.getFirstChildElement( content );

                if (child != null) {
                     // traverse annotation if any
                     if (DOMUtil.getLocalName(child).equals(SchemaSymbols.ELT_ANNOTATION)) {
                         traverseAnnotationDecl(child, attrs, false, schemaDoc);
                         child = DOMUtil.getNextSiblingElement(child);
                     }
                     if (child !=null && DOMUtil.getLocalName(child).equals(SchemaSymbols.ELT_ANNOTATION)) {
                         reportSchemaError("s4s-elt-must-match", new Object[]{"enumeration", "(annotation?)"}, child);
                     }
               }
            }
            else if (facet.equals(SchemaSymbols.ELT_PATTERN)) {
                attrs = fAttrChecker.checkAttributes(content, false, schemaDoc);
                if (fPattern.length() == 0) {
                    fPattern.append((String)attrs[XSAttributeChecker.ATTIDX_VALUE]);
                } else {
                    // ---------------------------------------------
                    //datatypes: 5.2.4 pattern: src-multiple-pattern
                    // ---------------------------------------------
                    fPattern.append("|");
                    fPattern.append((String)attrs[XSAttributeChecker.ATTIDX_VALUE]);

                    Element child = DOMUtil.getFirstChildElement( content );
                    if (child != null) {
                         // traverse annotation if any
                         if (DOMUtil.getLocalName(child).equals(SchemaSymbols.ELT_ANNOTATION)) {
                             traverseAnnotationDecl(child, attrs, false, schemaDoc);
                             child = DOMUtil.getNextSiblingElement(child);
                         }
                         if (child !=null && DOMUtil.getLocalName(child).equals(SchemaSymbols.ELT_ANNOTATION)) {
                             reportSchemaError("s4s-elt-must-match", new Object[]{"pattern", "(annotation?)"}, child);
                         }
                   }
                }
            }
            else {
                if (facet.equals(SchemaSymbols.ELT_MINLENGTH)) {
                    currentFacet = XSSimpleType.FACET_MINLENGTH;
                }
                else if (facet.equals(SchemaSymbols.ELT_MAXLENGTH)) {
                    currentFacet = XSSimpleType.FACET_MAXLENGTH;
                }
                else if (facet.equals(SchemaSymbols.ELT_MAXEXCLUSIVE)) {
                    currentFacet = XSSimpleType.FACET_MAXEXCLUSIVE;
                }
                else if (facet.equals(SchemaSymbols.ELT_MAXINCLUSIVE)) {
                    currentFacet = XSSimpleType.FACET_MAXINCLUSIVE;
                }
                else if (facet.equals(SchemaSymbols.ELT_MINEXCLUSIVE)) {
                    currentFacet = XSSimpleType.FACET_MINEXCLUSIVE;
                }
                else if (facet.equals(SchemaSymbols.ELT_MININCLUSIVE)) {
                    currentFacet = XSSimpleType.FACET_MININCLUSIVE;
                }
                else if (facet.equals(SchemaSymbols.ELT_TOTALDIGITS)) {
                    currentFacet = XSSimpleType.FACET_TOTALDIGITS;
                }
                else if (facet.equals(SchemaSymbols.ELT_FRACTIONDIGITS)) {
                    currentFacet = XSSimpleType.FACET_FRACTIONDIGITS;
                }
                else if (facet.equals(SchemaSymbols.ELT_WHITESPACE)) {
                    currentFacet = XSSimpleType.FACET_WHITESPACE;
                }
                else if (facet.equals(SchemaSymbols.ELT_LENGTH)) {
                    currentFacet = XSSimpleType.FACET_LENGTH;
                }
                else {
                    break;   // a non-facet
                }

                attrs = fAttrChecker.checkAttributes(content, false, schemaDoc);

                // check for duplicate facets
                if ((facetsPresent & currentFacet) != 0) {
                    reportSchemaError("src-single-facet-value", new Object[]{facet}, content);
                } else if (attrs[XSAttributeChecker.ATTIDX_VALUE] != null) {
                    facetsPresent |= currentFacet;
                    // check for fixed facet
                    if (((Boolean)attrs[XSAttributeChecker.ATTIDX_FIXED]).booleanValue()) {
                        facetsFixed |= currentFacet;
                    }
                    switch (currentFacet) {
                        case XSSimpleType.FACET_MINLENGTH:
                            xsFacets.minLength = ((XInt)attrs[XSAttributeChecker.ATTIDX_VALUE]).intValue();
                            break;
                        case XSSimpleType.FACET_MAXLENGTH:
                            xsFacets.maxLength = ((XInt)attrs[XSAttributeChecker.ATTIDX_VALUE]).intValue();
                            break;
                        case XSSimpleType.FACET_MAXEXCLUSIVE:
                            xsFacets.maxExclusive = (String)attrs[XSAttributeChecker.ATTIDX_VALUE];
                            break;
                        case XSSimpleType.FACET_MAXINCLUSIVE:
                            xsFacets.maxInclusive = (String)attrs[XSAttributeChecker.ATTIDX_VALUE];
                            break;
                        case XSSimpleType.FACET_MINEXCLUSIVE:
                            xsFacets.minExclusive = (String)attrs[XSAttributeChecker.ATTIDX_VALUE];
                            break;
                        case XSSimpleType.FACET_MININCLUSIVE:
                            xsFacets.minInclusive = (String)attrs[XSAttributeChecker.ATTIDX_VALUE];
                            break;
                        case XSSimpleType.FACET_TOTALDIGITS:
                            xsFacets.totalDigits = ((XInt)attrs[XSAttributeChecker.ATTIDX_VALUE]).intValue();
                            break;
                        case XSSimpleType.FACET_FRACTIONDIGITS:
                            xsFacets.fractionDigits = ((XInt)attrs[XSAttributeChecker.ATTIDX_VALUE]).intValue();
                            break;
                        case XSSimpleType.FACET_WHITESPACE:
                            xsFacets.whiteSpace = ((XInt)attrs[XSAttributeChecker.ATTIDX_VALUE]).shortValue();
                            break;
                        case XSSimpleType.FACET_LENGTH:
                            xsFacets.length = ((XInt)attrs[XSAttributeChecker.ATTIDX_VALUE]).intValue();
                            break;
                    }
                }

                Element child = DOMUtil.getFirstChildElement( content );
                if (child != null) {
                    // traverse annotation if any
                    if (DOMUtil.getLocalName(child).equals(SchemaSymbols.ELT_ANNOTATION)) {
                        traverseAnnotationDecl(child, attrs, false, schemaDoc);
                        child = DOMUtil.getNextSiblingElement(child);
                    }
                    if (child !=null && DOMUtil.getLocalName(child).equals(SchemaSymbols.ELT_ANNOTATION)) {
                        reportSchemaError("s4s-elt-must-match", new Object[]{facet, "(annotation?)"}, child);
                    }
                }
            }
            fAttrChecker.returnAttrArray (attrs, schemaDoc);
            content = DOMUtil.getNextSiblingElement(content);
        }
        if (enumData.size() > 0) {
            facetsPresent |= XSSimpleType.FACET_ENUMERATION;
            xsFacets.enumeration = enumData;
            xsFacets.enumNSDecls = enumNSDecls;
        }
        if (fPattern.length() != 0) {
            facetsPresent |= XSSimpleType.FACET_PATTERN;
            xsFacets.pattern = fPattern.toString();
        }

        fPattern.setLength(0);

        FacetInfo fi = new FacetInfo();
        fi.facetdata = xsFacets;
        fi.nodeAfterFacets = content;
        fi.fPresentFacets = facetsPresent;
        fi.fFixedFacets = facetsFixed;
        return fi;
    }

    // return whether QName/NOTATION is part of the given type
    private boolean containsQName(XSSimpleType type) {
        if (type.getVariety() == XSSimpleType.VARIETY_ATOMIC) {
            short primitive = type.getPrimitiveKind();
            return (primitive == XSSimpleType.PRIMITIVE_QNAME ||
                    primitive == XSSimpleType.PRIMITIVE_NOTATION);
        }
        else if (type.getVariety() == XSSimpleType.VARIETY_LIST) {
            return containsQName((XSSimpleType)type.getItemType());
        }
        else if (type.getVariety() == XSSimpleType.VARIETY_UNION) {
            XSObjectList members = type.getMemberTypes();
            for (int i = 0; i < members.getLength(); i++) {
                if (containsQName((XSSimpleType)members.item(i)))
                    return true;
            }
        }
        return false;
    }

    //
    // Traverse a set of attribute and attribute group elements
    // Needed by complexType and attributeGroup traversal
    // This method will return the first non-attribute/attrgrp found
    //
    Element traverseAttrsAndAttrGrps(Element firstAttr, XSAttributeGroupDecl attrGrp,
                                     XSDocumentInfo schemaDoc, SchemaGrammar grammar,
                                     XSComplexTypeDecl enclosingCT) {

        Element child=null;
        XSAttributeGroupDecl tempAttrGrp = null;
        XSAttributeUseImpl tempAttrUse = null;
        String childName;

        for (child=firstAttr; child!=null; child=DOMUtil.getNextSiblingElement(child)) {
            childName = DOMUtil.getLocalName(child);
            if (childName.equals(SchemaSymbols.ELT_ATTRIBUTE)) {
                tempAttrUse = fSchemaHandler.fAttributeTraverser.traverseLocal(child,
                                                                               schemaDoc,
                                                                               grammar,
                                                                               enclosingCT);
                if (tempAttrUse == null) break;
                if (attrGrp.getAttributeUse(tempAttrUse.fAttrDecl.getNamespace(),
                                            tempAttrUse.fAttrDecl.getName())==null) {
                    String idName = attrGrp.addAttributeUse(tempAttrUse);
                    if (idName != null) {
                        String code = (enclosingCT == null) ? "ag-props-correct.3" : "ct-props-correct.5";
                        String name = (enclosingCT == null) ? attrGrp.fName : enclosingCT.getName();
                        reportSchemaError(code, new Object[]{name, tempAttrUse.fAttrDecl.getName(), idName}, child);
                    }
                }
                else {
                    // REVISIT: what if one of the attribute uses is "prohibited"
                    String code = (enclosingCT == null) ? "ag-props-correct.2" : "ct-props-correct.4";
                    String name = (enclosingCT == null) ? attrGrp.fName : enclosingCT.getName();
                    reportSchemaError(code, new Object[]{name, tempAttrUse.fAttrDecl.getName()}, child);
                }
            }
            else if (childName.equals(SchemaSymbols.ELT_ATTRIBUTEGROUP)) {
                //REVISIT: do we need to save some state at this point??
                tempAttrGrp = fSchemaHandler.fAttributeGroupTraverser.traverseLocal(
                       child, schemaDoc, grammar);
                if(tempAttrGrp == null ) break;
                XSObjectList attrUseS = tempAttrGrp.getAttributeUses();
                XSAttributeUseImpl existingAttrUse = null, oneAttrUse;
                int attrCount = attrUseS.getLength();
                for (int i=0; i<attrCount; i++) {
                    oneAttrUse = (XSAttributeUseImpl)attrUseS.item(i);
                    existingAttrUse = attrGrp.getAttributeUse(oneAttrUse.fAttrDecl.getNamespace(),
                                                              oneAttrUse.fAttrDecl.getName());
                    if (existingAttrUse == null) {
                        String idName = attrGrp.addAttributeUse(oneAttrUse);
                        if (idName != null) {
                            reportSchemaError("cvc-complex-type.5.3", new Object[]{oneAttrUse.fAttrDecl.getName(), idName}, child);
                        }
                    }
                    else {
                        // REVISIT: what if one of the attribute uses is "prohibited"
                        String code = (enclosingCT == null) ? "ag-props-correct.2" : "ct-props-correct.4";
                        String name = (enclosingCT == null) ? attrGrp.fName : enclosingCT.getName();
                        reportSchemaError(code, new Object[]{name, oneAttrUse.fAttrDecl.getName()}, child);
                    }
                }

                if (tempAttrGrp.fAttributeWC != null) {
                    if (attrGrp.fAttributeWC == null) {
                        attrGrp.fAttributeWC = tempAttrGrp.fAttributeWC;
                    }
                    // perform intersection of attribute wildcard
                    else {
                        attrGrp.fAttributeWC = attrGrp.fAttributeWC.
                                               performIntersectionWith(tempAttrGrp.fAttributeWC, attrGrp.fAttributeWC.fProcessContents);
                        if (attrGrp.fAttributeWC == null) {
                            String code = (enclosingCT == null) ? "src-attribute_group.2" : "src-ct.4";
                            String name = (enclosingCT == null) ? attrGrp.fName : enclosingCT.getName();
                            reportSchemaError(code, new Object[]{name}, child);
                        }
                    }
                }
            }
            else
                break;
        } // for

        if (child != null) {
            childName = DOMUtil.getLocalName(child);
            if (childName.equals(SchemaSymbols.ELT_ANYATTRIBUTE)) {
                XSWildcardDecl tempAttrWC = fSchemaHandler.fWildCardTraverser.
                                            traverseAnyAttribute(child, schemaDoc, grammar);
                if (attrGrp.fAttributeWC == null) {
                    attrGrp.fAttributeWC = tempAttrWC;
                }
                // perform intersection of attribute wildcard
                else {
                    attrGrp.fAttributeWC = tempAttrWC.
                                           performIntersectionWith(attrGrp.fAttributeWC, tempAttrWC.fProcessContents);
                    if (attrGrp.fAttributeWC == null) {
                        String code = (enclosingCT == null) ? "src-attribute_group.2" : "src-ct.4";
                        String name = (enclosingCT == null) ? attrGrp.fName : enclosingCT.getName();
                        reportSchemaError(code, new Object[]{name}, child);
                    }
                }
                child = DOMUtil.getNextSiblingElement(child);
            }
        }

        // Success
        return child;

    }

    void reportSchemaError (String key, Object[] args, Element ele) {
        fSchemaHandler.reportSchemaError(key, args, ele);
    }

    /**
     * Element/Attribute traversers call this method to check whether
     * the type is NOTATION without enumeration facet
     */
    void checkNotationType(String refName, XSTypeDefinition typeDecl, Element elem) {
        if (typeDecl.getTypeCategory() == typeDecl.SIMPLE_TYPE &&
            ((XSSimpleType)typeDecl).getVariety() == XSSimpleType.VARIETY_ATOMIC &&
            ((XSSimpleType)typeDecl).getPrimitiveKind() == XSSimpleType.PRIMITIVE_NOTATION) {
            if ((((XSSimpleType)typeDecl).getDefinedFacets() & XSSimpleType.FACET_ENUMERATION) == 0) {
                reportSchemaError("enumeration-required-notation", new Object[]{refName}, elem);
            }
        }
    }

    // Checks constraints for minOccurs, maxOccurs
    protected XSParticleDecl checkOccurrences(XSParticleDecl particle,
                                              String particleName, Element parent,
                                              int allContextFlags,
                                              long defaultVals) {

        int min = particle.fMinOccurs;
        int max = particle.fMaxOccurs;
        boolean defaultMin = (defaultVals & (1 << XSAttributeChecker.ATTIDX_MINOCCURS)) != 0;
        boolean defaultMax = (defaultVals & (1 << XSAttributeChecker.ATTIDX_MAXOCCURS)) != 0;

        boolean processingAllEl = ((allContextFlags & PROCESSING_ALL_EL) != 0);
        boolean processingAllGP = ((allContextFlags & PROCESSING_ALL_GP) != 0);
        boolean groupRefWithAll = ((allContextFlags & GROUP_REF_WITH_ALL) != 0);
        boolean isGroupChild    = ((allContextFlags & CHILD_OF_GROUP) != 0);

        // Neither minOccurs nor maxOccurs may be specified
        // for the child of a model group definition.
        if (isGroupChild) {
            if (!defaultMin) {
                Object[] args = new Object[]{particleName, "minOccurs"};
                reportSchemaError("s4s-att-not-allowed", args, parent);
                min = 1;
            }
            if (!defaultMax) {
                Object[] args = new Object[]{particleName, "maxOccurs"};
                reportSchemaError("s4s-att-not-allowed", args, parent);
                max = 1;
            }
        }

        // If minOccurs=maxOccurs=0, no component is specified
        if (min == 0 && max== 0) {
            particle.fType = XSParticleDecl.PARTICLE_EMPTY;
            return null;
        }

        // For the elements referenced in an <all>, minOccurs attribute
        // must be zero or one, and maxOccurs attribute must be one.
        // For a complex type definition that contains an <all> or a
        // reference a <group> whose model group is an all model group,
        // minOccurs and maxOccurs must be one.
        if (processingAllEl) {
            if (max != 1) {
                reportSchemaError("cos-all-limited.2", null, parent);
                max = 1;
                if (min > 1)
                    min = 1;
            }
        }
        else if (processingAllGP || groupRefWithAll) {
            if (max != 1) {
                reportSchemaError("cos-all-limited.1.2", null, parent);
                if (min > 1)
                    min = 1;
                max = 1;
            }
        }

        particle.fMaxOccurs = min;
        particle.fMaxOccurs = max;

        return particle;
    }
}
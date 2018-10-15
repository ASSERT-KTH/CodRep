reportSchemaError(ex.getKey(), ex.getArgs());

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
package org.apache.xerces.impl.xs.traversers;

import org.apache.xerces.impl.dv.XSSimpleType;
import org.apache.xerces.impl.dv.SchemaDVFactory;
import org.apache.xerces.impl.dv.XSFacets;
import org.apache.xerces.impl.dv.InvalidDatatypeFacetException;
import org.apache.xerces.impl.XMLErrorReporter;
import org.apache.xerces.impl.xs.XSConstraints;
import org.apache.xerces.impl.xs.SchemaGrammar;
import org.apache.xerces.impl.xs.SchemaSymbols;
import org.apache.xerces.impl.xs.XSComplexTypeDecl;
import org.apache.xerces.impl.xs.XSTypeDecl;
import org.apache.xerces.impl.xs.XSAttributeGroupDecl;
import org.apache.xerces.impl.xs.XSAttributeUse;
import org.apache.xerces.impl.xs.XSWildcardDecl;
import org.apache.xerces.impl.xs.XSParticleDecl;
import org.apache.xerces.util.DOMUtil;
import org.apache.xerces.impl.xs.util.XInt;
import org.apache.xerces.impl.xs.util.XIntPool;
import org.apache.xerces.xni.QName;
import org.w3c.dom.Element;
import java.util.Hashtable;

/**
 * A complex type definition schema component traverser.
 *
 * <complexType
 *   abstract = boolean : false
 *   block = (#all | List of (extension | restriction))
 *   final = (#all | List of (extension | restriction))
 *   id = ID
 *   mixed = boolean : false
 *   name = NCName
 *   {any attributes with non-schema namespace . . .}>
 *   Content: (annotation?, (simpleContent | complexContent |
 *            ((group | all | choice | sequence)?,
 *            ((attribute | attributeGroup)*, anyAttribute?))))
 * </complexType>
 * @version $Id$
 */

class  XSDComplexTypeTraverser extends XSDAbstractParticleTraverser {


    XSDComplexTypeTraverser (XSDHandler handler,
                             XSAttributeChecker gAttrCheck) {
        super(handler, gAttrCheck);
    }


    private static final boolean DEBUG=false;

    private static XSParticleDecl fErrorContent=null;
    private SchemaDVFactory schemaFactory = SchemaDVFactory.getInstance();

    private class ComplexTypeRecoverableError extends Exception {

        Object[] errorSubstText=null;
        ComplexTypeRecoverableError() {
            super();
        }
        ComplexTypeRecoverableError(String msgKey) {
            super(msgKey);
        }
        ComplexTypeRecoverableError(String msgKey, Object[] args) {
            super(msgKey);
            errorSubstText=args;
        }

    }

    /**
     * Traverse local complexType declarations
     *
     * @param Element
     * @param XSDocumentInfo
     * @param SchemaGrammar
     * @return XSComplexTypeDecl
     */
    XSComplexTypeDecl traverseLocal(Element complexTypeNode,
                                    XSDocumentInfo schemaDoc,
                                    SchemaGrammar grammar) {


        Object[] attrValues = fAttrChecker.checkAttributes(complexTypeNode, false,
                                                           schemaDoc);
        String complexTypeName = genAnonTypeName(complexTypeNode);
        XSComplexTypeDecl type = traverseComplexTypeDecl (complexTypeNode,
                                                          complexTypeName, attrValues, schemaDoc, grammar);
        // need to add the type to the grammar for later constraint checking
        grammar.addComplexTypeDecl(type);
        type.setIsAnonymous();
        fAttrChecker.returnAttrArray(attrValues, schemaDoc);

        return type;
    }

    /**
     * Traverse global complexType declarations
     *
     * @param Element
     * @param XSDocumentInfo
     * @param SchemaGrammar
     * @return XSComplexTypeDecXSComplexTypeDecl
     */
    XSComplexTypeDecl traverseGlobal (Element complexTypeNode,
                                      XSDocumentInfo schemaDoc,
                                      SchemaGrammar grammar) {

        Object[] attrValues = fAttrChecker.checkAttributes(complexTypeNode, true,
                                                           schemaDoc);
        String complexTypeName = (String)  attrValues[XSAttributeChecker.ATTIDX_NAME];
        XSComplexTypeDecl type = traverseComplexTypeDecl (complexTypeNode,
                                                          complexTypeName, attrValues, schemaDoc, grammar);
        if (complexTypeName == null) {
            reportSchemaError("s4s-att-must-appear", new Object[]{SchemaSymbols.ELT_COMPLEXTYPE, SchemaSymbols.ATT_NAME});
        } else {
            grammar.addGlobalTypeDecl(type);
        }
        // need to add the type to the grammar for later constraint checking
        grammar.addComplexTypeDecl(type);
        fAttrChecker.returnAttrArray(attrValues, schemaDoc);

        return type;
    }


    private XSComplexTypeDecl traverseComplexTypeDecl(Element complexTypeDecl,
                                                      String complexTypeName,
                                                      Object[] attrValues,
                                                      XSDocumentInfo schemaDoc,
                                                      SchemaGrammar grammar) {

        Boolean abstractAtt  = (Boolean) attrValues[XSAttributeChecker.ATTIDX_ABSTRACT];
        XInt    blockAtt     = (XInt)    attrValues[XSAttributeChecker.ATTIDX_BLOCK];
        Boolean mixedAtt     = (Boolean) attrValues[XSAttributeChecker.ATTIDX_MIXED];
        XInt    finalAtt     = (XInt)    attrValues[XSAttributeChecker.ATTIDX_FINAL];

        XSComplexTypeDecl complexType = new XSComplexTypeDecl();
        complexType.fName = complexTypeName;
        complexType.fTargetNamespace = schemaDoc.fTargetNamespace;
        complexType.fBlock = blockAtt == null ?
                             schemaDoc.fBlockDefault : blockAtt.shortValue();
        complexType.fFinal = finalAtt == null ?
                             schemaDoc.fFinalDefault : finalAtt.shortValue();
        if (abstractAtt != null && abstractAtt.booleanValue())
            complexType.setIsAbstractType();


        Element child = null;

        try {
            // ---------------------------------------------------------------
            // First, handle any ANNOTATION declaration and get next child
            // ---------------------------------------------------------------
            child = DOMUtil.getFirstChildElement(complexTypeDecl);

            if (child != null) {
                // traverse annotation if any
                if (DOMUtil.getLocalName(child).equals(SchemaSymbols.ELT_ANNOTATION)) {
                    traverseAnnotationDecl(child, attrValues, false, schemaDoc);
                    child = DOMUtil.getNextSiblingElement(child);
                }
                if (child !=null && DOMUtil.getLocalName(child).equals(SchemaSymbols.ELT_ANNOTATION)) {
                    throw new ComplexTypeRecoverableError("src-ct.0.1",
                           new Object[]{complexType.fName,SchemaSymbols.ELT_ANNOTATION});
                }
            }
            // ---------------------------------------------------------------
            // Process the content of the complex type definition
            // ---------------------------------------------------------------
            if (child==null) {
                //
                // EMPTY complexType with complexContent
                //

                // set the base to the anyType
                complexType.fBaseType = SchemaGrammar.fAnyType;
                processComplexContent(child, complexType, mixedAtt.booleanValue(), false,
                                      schemaDoc, grammar);
            }
            else if (DOMUtil.getLocalName(child).equals
                     (SchemaSymbols.ELT_SIMPLECONTENT)) {
                //
                // SIMPLE CONTENT
                //
                traverseSimpleContent(child, complexType, schemaDoc, grammar);
                if (DOMUtil.getNextSiblingElement(child)!=null) {
                    String siblingName = DOMUtil.getLocalName(DOMUtil.getNextSiblingElement(child));
                    throw new ComplexTypeRecoverableError("src-ct.0.1",
                                                          new Object[]{complexType.fName,siblingName});
                }
            }
            else if (DOMUtil.getLocalName(child).equals
                     (SchemaSymbols.ELT_COMPLEXCONTENT)) {
                traverseComplexContent(child, complexType, mixedAtt.booleanValue(),
                                       schemaDoc, grammar);
                if (DOMUtil.getNextSiblingElement(child)!=null) {
                    String siblingName = DOMUtil.getLocalName(DOMUtil.getNextSiblingElement(child));
                    throw new ComplexTypeRecoverableError("src-ct.0.1",
                                                          new Object[]{complexType.fName,siblingName});
                }
            }
            else {
                //
                // We must have ....
                // GROUP, ALL, SEQUENCE or CHOICE, followed by optional attributes
                // Note that it's possible that only attributes are specified.
                //

                // set the base to the anyType
                complexType.fBaseType = SchemaGrammar.fAnyType;
                processComplexContent(child, complexType, mixedAtt.booleanValue(), false,
                                      schemaDoc, grammar);
            }

        }
        catch (ComplexTypeRecoverableError e) {
            handleComplexTypeError(e.getMessage(),e.errorSubstText, complexType);
        }

        if (DEBUG) {
            System.out.println(complexType.toString());
        }
        return complexType;


    }


    private void traverseSimpleContent(Element simpleContentElement,
                                       XSComplexTypeDecl typeInfo,
                                       XSDocumentInfo schemaDoc,
                                       SchemaGrammar grammar)
    throws ComplexTypeRecoverableError {


        String typeName = typeInfo.fName;
        Object[] attrValues = fAttrChecker.checkAttributes(simpleContentElement, false,
                                                           schemaDoc);

        // -----------------------------------------------------------------------
        // Set content type
        // -----------------------------------------------------------------------
        typeInfo.fContentType = XSComplexTypeDecl.CONTENTTYPE_SIMPLE;
        typeInfo.fParticle = null;

        Element simpleContent = DOMUtil.getFirstChildElement(simpleContentElement);
        if (simpleContent != null) {
            // traverse annotation if any
            if (DOMUtil.getLocalName(simpleContent).equals(SchemaSymbols.ELT_ANNOTATION)) {
                traverseAnnotationDecl(simpleContent, attrValues, false, schemaDoc);
                simpleContent = DOMUtil.getNextSiblingElement(simpleContent);
            }
        }
        fAttrChecker.returnAttrArray(attrValues, schemaDoc);

        // If there are no children, return
        if (simpleContent==null) {
            throw new ComplexTypeRecoverableError("src-ct.0.2",
                            new Object[]{typeInfo.fName,SchemaSymbols.ELT_SIMPLECONTENT});
        }

        // -----------------------------------------------------------------------
        // The content should be either "restriction" or "extension"
        // -----------------------------------------------------------------------
        String simpleContentName = DOMUtil.getLocalName(simpleContent);
        if (simpleContentName.equals(SchemaSymbols.ELT_RESTRICTION))
            typeInfo.fDerivedBy = SchemaSymbols.RESTRICTION;
        else if (simpleContentName.equals(SchemaSymbols.ELT_EXTENSION))
            typeInfo.fDerivedBy = SchemaSymbols.EXTENSION;
        else {
            throw new ComplexTypeRecoverableError("src-ct.0.1",
                            new Object[]{typeInfo.fName,simpleContentName});
        }
        if (DOMUtil.getNextSiblingElement(simpleContent) != null) {
            String siblingName = DOMUtil.getLocalName(DOMUtil.getNextSiblingElement(simpleContent));
            throw new ComplexTypeRecoverableError("src-ct.0.1",
                            new Object[]{typeInfo.fName,siblingName});
        }

        attrValues = fAttrChecker.checkAttributes(simpleContent, false,
                                                  schemaDoc);
        QName baseTypeName = (QName)  attrValues[XSAttributeChecker.ATTIDX_BASE];
        fAttrChecker.returnAttrArray(attrValues, schemaDoc);


        // -----------------------------------------------------------------------
        // Need a base type.
        // -----------------------------------------------------------------------
        if (baseTypeName==null) {
            throw new ComplexTypeRecoverableError("src-ct.0.3",
                            new Object[]{typeInfo.fName});
        }

        XSTypeDecl type = (XSTypeDecl)fSchemaHandler.getGlobalDecl(schemaDoc,
                                      XSDHandler.TYPEDECL_TYPE, baseTypeName);
        if (type==null)
            throw new ComplexTypeRecoverableError();

        typeInfo.fBaseType = type;

        XSSimpleType baseValidator = null;
        XSComplexTypeDecl baseComplexType = null;
        int baseFinalSet = 0;

        // If the base type is complex, it must have simpleContent
        if ((type.getXSType() == XSTypeDecl.COMPLEX_TYPE)) {

            baseComplexType = (XSComplexTypeDecl)type;
            if (baseComplexType.fContentType != XSComplexTypeDecl.CONTENTTYPE_SIMPLE) {
                throw new ComplexTypeRecoverableError("src-ct.2",
                                new Object[]{typeInfo.fName});
            }
            baseFinalSet = baseComplexType.fFinal;
            baseValidator = baseComplexType.fXSSimpleType;
        }
        else {
            baseValidator = (XSSimpleType)type;
            if (typeInfo.fDerivedBy == SchemaSymbols.RESTRICTION) {
                throw new ComplexTypeRecoverableError("src-ct.2",
                                new Object[]{typeInfo.fName});
            }
            baseFinalSet=baseValidator.getFinalSet();
        }

        // -----------------------------------------------------------------------
        // Check that the base permits the derivation
        // -----------------------------------------------------------------------
        if ((baseFinalSet & typeInfo.fDerivedBy)!=0) {
            String errorKey = (typeInfo.fDerivedBy==SchemaSymbols.EXTENSION) ?
                              "cos-ct-extends.1.1" : "derivation-ok-restriction.1";
            throw new ComplexTypeRecoverableError(errorKey,
                                new Object[]{typeInfo.fName});
        }

        // -----------------------------------------------------------------------
        // Skip over any potential annotations
        // -----------------------------------------------------------------------
        simpleContent = DOMUtil.getFirstChildElement(simpleContent);
        if (simpleContent != null) {
            // traverse annotation if any

            if (DOMUtil.getLocalName(simpleContent).equals(SchemaSymbols.ELT_ANNOTATION)) {
                traverseAnnotationDecl(simpleContent, null, false, schemaDoc);
                simpleContent = DOMUtil.getNextSiblingElement(simpleContent);
            }

            if (simpleContent !=null &&
                DOMUtil.getLocalName(simpleContent).equals(SchemaSymbols.ELT_ANNOTATION)){
                throw new ComplexTypeRecoverableError("src-ct.0.1",
                       new Object[]{typeName,SchemaSymbols.ELT_ANNOTATION});
            }
        }

        // -----------------------------------------------------------------------
        // Process a RESTRICTION
        // -----------------------------------------------------------------------
        if (typeInfo.fDerivedBy == SchemaSymbols.RESTRICTION) {

            // -----------------------------------------------------------------------
            // There may be a simple type definition in the restriction element
            // The data type validator will be based on it, if specified
            // -----------------------------------------------------------------------
            if (simpleContent !=null &&
            DOMUtil.getLocalName(simpleContent).equals(SchemaSymbols.ELT_SIMPLETYPE )) {

                XSSimpleType dv = fSchemaHandler.fSimpleTypeTraverser.traverseLocal(
                      simpleContent, schemaDoc, grammar);
                if (dv == null)
                    throw new ComplexTypeRecoverableError();

                //check that this datatype validator is validly derived from the base
                //according to derivation-ok-restriction 5.1.1

                if (!XSConstraints.checkSimpleDerivationOk(dv, baseValidator,
                                                           baseValidator.getFinalSet())) {
                    throw new ComplexTypeRecoverableError("derivation-ok-restriction.5.1.1",
                           new Object[]{typeName});
                }
                baseValidator = dv;
                simpleContent = DOMUtil.getNextSiblingElement(simpleContent);
            }

            // -----------------------------------------------------------------------
            // Traverse any facets
            // -----------------------------------------------------------------------
            Element attrNode = null;
            XSFacets facetData = null;
            short presentFacets = 0 ;
            short fixedFacets = 0 ;

            if (simpleContent!=null) {
                FacetInfo fi = traverseFacets(simpleContent, null, typeName, baseValidator,
                                              schemaDoc, grammar);
                attrNode = fi.nodeAfterFacets;
                facetData = fi.facetdata;
                presentFacets = fi.fPresentFacets;
                fixedFacets = fi.fFixedFacets;
            }

            typeInfo.fXSSimpleType = schemaFactory.createTypeRestriction(null,schemaDoc.fTargetNamespace,(short)0,baseValidator);
            try{
                fValidationState.setNamespaceSupport(schemaDoc.fNamespaceSupport);
                typeInfo.fXSSimpleType.applyFacets(facetData, presentFacets, fixedFacets, fValidationState);
            }catch(InvalidDatatypeFacetException ex){
                reportGenericSchemaError(ex.getLocalizedMessage());
            }

            // -----------------------------------------------------------------------
            // Traverse any attributes
            // -----------------------------------------------------------------------
            if (attrNode != null) {
                if (!isAttrOrAttrGroup(attrNode)) {
                    throw new ComplexTypeRecoverableError("src-ct.0.1",
                             new Object[]{typeInfo.fName,DOMUtil.getLocalName(attrNode)});
                }
                Element node=traverseAttrsAndAttrGrps(attrNode,typeInfo.fAttrGrp,
                                                      schemaDoc,grammar);
                if (node!=null) {
                    throw new ComplexTypeRecoverableError("src-ct.0.1",
                             new Object[]{typeInfo.fName,DOMUtil.getLocalName(node)});
                }
            }

            mergeAttributes(baseComplexType.fAttrGrp, typeInfo.fAttrGrp, typeName, false);
            // Prohibited uses must be removed after merge for RESTRICTION
            typeInfo.fAttrGrp.removeProhibitedAttrs();

            String errorCode=typeInfo.fAttrGrp.validRestrictionOf(baseComplexType.fAttrGrp);
            if (errorCode != null) {
                throw new ComplexTypeRecoverableError(errorCode,
                             new Object[]{typeInfo.fName});
            }

        }
        // -----------------------------------------------------------------------
        // Process a EXTENSION
        // -----------------------------------------------------------------------
        else {
            typeInfo.fXSSimpleType = baseValidator;
            if (simpleContent != null) {
                // -----------------------------------------------------------------------
                // Traverse any attributes
                // -----------------------------------------------------------------------
                Element attrNode = simpleContent;
                if (!isAttrOrAttrGroup(attrNode)) {
                    throw new ComplexTypeRecoverableError("src-ct.0.1",
                                                          new Object[]{typeInfo.fName,DOMUtil.getLocalName(attrNode)});
                }
                Element node=traverseAttrsAndAttrGrps(attrNode,typeInfo.fAttrGrp,
                                                      schemaDoc,grammar);

                if (node!=null) {
                    throw new ComplexTypeRecoverableError("src-ct.0.1",
                                                          new Object[]{typeInfo.fName,DOMUtil.getLocalName(node)});
                }
                // Remove prohibited uses.   Should be done prior to any merge.
                typeInfo.fAttrGrp.removeProhibitedAttrs();
            }

            if (baseComplexType != null) {
                mergeAttributes(baseComplexType.fAttrGrp, typeInfo.fAttrGrp, typeName, true);
            }
        }
    }

    private void traverseComplexContent(Element complexContentElement,
                                        XSComplexTypeDecl typeInfo,
                                        boolean mixedOnType, XSDocumentInfo schemaDoc,
                                        SchemaGrammar grammar)
    throws ComplexTypeRecoverableError {


        String typeName = typeInfo.fName;
        Object[] attrValues = fAttrChecker.checkAttributes(complexContentElement, false,
                                                           schemaDoc);


        // -----------------------------------------------------------------------
        // Determine if this is mixed content
        // -----------------------------------------------------------------------
        boolean mixedContent = mixedOnType;
        Boolean mixedAtt     = (Boolean) attrValues[XSAttributeChecker.ATTIDX_MIXED];
        if (mixedAtt != null) {
            mixedContent = mixedAtt.booleanValue();
        }


        // -----------------------------------------------------------------------
        // Since the type must have complex content, set the simple type validators
        // to null
        // -----------------------------------------------------------------------
        typeInfo.fXSSimpleType = null;

        Element complexContent = DOMUtil.getFirstChildElement(complexContentElement);
        if (complexContent != null) {
            // traverse annotation if any
            if (DOMUtil.getLocalName(complexContent).equals(SchemaSymbols.ELT_ANNOTATION)) {
                traverseAnnotationDecl(complexContent, attrValues, false, schemaDoc);
                complexContent = DOMUtil.getNextSiblingElement(complexContent);
            }
        }

        fAttrChecker.returnAttrArray(attrValues, schemaDoc);
        // If there are no children, return
        if (complexContent==null) {
            throw new ComplexTypeRecoverableError("src-ct.0.2",
                      new Object[]{typeName,SchemaSymbols.ELT_COMPLEXCONTENT});
        }

        // -----------------------------------------------------------------------
        // The content should be either "restriction" or "extension"
        // -----------------------------------------------------------------------
        String complexContentName = DOMUtil.getLocalName(complexContent);
        if (complexContentName.equals(SchemaSymbols.ELT_RESTRICTION))
            typeInfo.fDerivedBy = SchemaSymbols.RESTRICTION;
        else if (complexContentName.equals(SchemaSymbols.ELT_EXTENSION))
            typeInfo.fDerivedBy = SchemaSymbols.EXTENSION;
        else {
            throw new ComplexTypeRecoverableError("src-ct.0.1",
                      new Object[]{typeName, complexContentName});
        }
        if (DOMUtil.getNextSiblingElement(complexContent) != null) {
            String siblingName = DOMUtil.getLocalName(DOMUtil.getNextSiblingElement(complexContent));
            throw new ComplexTypeRecoverableError("src-ct.0.1",
                      new Object[]{typeName, siblingName});
        }

        attrValues = fAttrChecker.checkAttributes(complexContent, false,
                                                  schemaDoc);
        QName baseTypeName = (QName)  attrValues[XSAttributeChecker.ATTIDX_BASE];
        fAttrChecker.returnAttrArray(attrValues, schemaDoc);


        // -----------------------------------------------------------------------
        // Need a base type.  Check that it's a complex type
        // -----------------------------------------------------------------------
        if (baseTypeName==null) {
            throw new ComplexTypeRecoverableError("src-ct.0.3",
                      new Object[]{typeName});
        }

        XSTypeDecl type = (XSTypeDecl)fSchemaHandler.getGlobalDecl(schemaDoc,
                                                                   XSDHandler.TYPEDECL_TYPE, baseTypeName);

        if (type==null)
            throw new ComplexTypeRecoverableError();

        if (! (type instanceof XSComplexTypeDecl)) {
            throw new ComplexTypeRecoverableError("src-ct.1",
                      new Object[]{typeName});
        }
        XSComplexTypeDecl baseType = (XSComplexTypeDecl)type;
        typeInfo.fBaseType = baseType;

        // -----------------------------------------------------------------------
        // Check that the base permits the derivation
        // -----------------------------------------------------------------------
        if ((baseType.fFinal & typeInfo.fDerivedBy)!=0) {
            String errorKey = (typeInfo.fDerivedBy==SchemaSymbols.EXTENSION) ?
                              "cos-ct-extends.1.1" : "derivation-ok-restriction.1";
            throw new ComplexTypeRecoverableError(errorKey,
                                new Object[]{typeInfo.fName});
        }

        // -----------------------------------------------------------------------
        // Skip over any potential annotations
        // -----------------------------------------------------------------------
        complexContent = DOMUtil.getFirstChildElement(complexContent);

        if (complexContent != null) {
            // traverse annotation if any
            if (DOMUtil.getLocalName(complexContent).equals(SchemaSymbols.ELT_ANNOTATION)) {
                traverseAnnotationDecl(complexContent, null, false, schemaDoc);
                complexContent = DOMUtil.getNextSiblingElement(complexContent);
            }
            if (complexContent !=null &&
               DOMUtil.getLocalName(complexContent).equals(SchemaSymbols.ELT_ANNOTATION)){
                throw new ComplexTypeRecoverableError("src-ct.0.1",
                       new Object[]{typeName,SchemaSymbols.ELT_ANNOTATION});
            }
        }
        // -----------------------------------------------------------------------
        // Process the content.  Note:  should I try to catch any complexType errors
        // here in order to return the attr array?
        // -----------------------------------------------------------------------
        processComplexContent(complexContent, typeInfo, mixedContent, true, schemaDoc,
                              grammar);

        // -----------------------------------------------------------------------
        // Compose the final content and attribute uses
        // -----------------------------------------------------------------------
        XSParticleDecl baseContent = baseType.fParticle;
        if (typeInfo.fDerivedBy==SchemaSymbols.RESTRICTION) {

            // This is an RESTRICTION

            if (typeInfo.fParticle==null && (!(baseContent==null ||
                                               baseContent.emptiable()))) {
                throw new ComplexTypeRecoverableError("derivation-ok-restriction.5.2",
                                          new Object[]{typeName});
            }
            if (typeInfo.fParticle!=null && baseContent==null) {
                //REVISIT - need better error msg
                throw new ComplexTypeRecoverableError("derivation-ok-restriction.5.3",
                                          new Object[]{typeName});
            }

            mergeAttributes(baseType.fAttrGrp, typeInfo.fAttrGrp, typeName, false);
            String error = typeInfo.fAttrGrp.validRestrictionOf(baseType.fAttrGrp);
            if (error != null) {
                throw new ComplexTypeRecoverableError(error,
                          new Object[]{typeName});
            }

            // Remove prohibited uses.   Must be done after merge for RESTRICTION.
            typeInfo.fAttrGrp.removeProhibitedAttrs();

        }
        else {

            // This is an EXTENSION

            //
            // Check if the contentType of the base is consistent with the new type
            // cos-ct-extends.1.4.2.2
            if (baseType.fContentType != XSComplexTypeDecl.CONTENTTYPE_EMPTY) {
                if (((baseType.fContentType ==
                      XSComplexTypeDecl.CONTENTTYPE_ELEMENT) &&
                     mixedContent) ||
                    ((baseType.fContentType ==
                      XSComplexTypeDecl.CONTENTTYPE_MIXED) && !mixedContent)) {

                    throw new ComplexTypeRecoverableError("cos-ct-extends.1.4.2.2.2.2.1",
                          new Object[]{typeName});
                }

            }

            // Create the particle
            if (typeInfo.fParticle == null) {
                typeInfo.fParticle = baseContent;
            }
            else if (baseContent==null) {
            }
            else {
                if (typeInfo.fParticle.fType == XSParticleDecl.PARTICLE_ALL ||
                    baseType.fParticle.fType == XSParticleDecl.PARTICLE_ALL) {
                    throw new ComplexTypeRecoverableError("cos-all-limited.1.2",
                          new Object[]{typeName});
                }
                XSParticleDecl temp = new XSParticleDecl();
                temp.fType = XSParticleDecl.PARTICLE_SEQUENCE;
                temp.fValue = baseContent;
                temp.fOtherValue = typeInfo.fParticle;
                typeInfo.fParticle = temp;
            }

            // Set the contentType
            if (mixedContent)
                typeInfo.fContentType = XSComplexTypeDecl.CONTENTTYPE_MIXED;
            else if (typeInfo.fParticle == null)
                typeInfo.fContentType = XSComplexTypeDecl.CONTENTTYPE_EMPTY;
            else
                typeInfo.fContentType = XSComplexTypeDecl.CONTENTTYPE_ELEMENT;

            // Remove prohibited uses.   Must be done before merge for EXTENSION.
            typeInfo.fAttrGrp.removeProhibitedAttrs();
            mergeAttributes(baseType.fAttrGrp, typeInfo.fAttrGrp, typeName, true);

        }

    } // end of traverseComplexContent


    // This method merges attribute uses from the base, into the derived set.
    // The first duplicate attribute, if any, is returned.
    // LM: may want to merge with attributeGroup processing.
    private void mergeAttributes(XSAttributeGroupDecl fromAttrGrp,
                                 XSAttributeGroupDecl toAttrGrp,
                                 String typeName,
                                 boolean extension)
    throws ComplexTypeRecoverableError {

        XSAttributeUse[] attrUseS = fromAttrGrp.getAttributeUses();
        XSAttributeUse existingAttrUse, duplicateAttrUse =  null;
        for (int i=0; i<attrUseS.length; i++) {
            existingAttrUse = toAttrGrp.getAttributeUse(attrUseS[i].fAttrDecl.fTargetNamespace,
                                                        attrUseS[i].fAttrDecl.fName);
            if (existingAttrUse == null) {
                String idName = toAttrGrp.addAttributeUse(attrUseS[i]);
                if (idName != null) {
                    throw new ComplexTypeRecoverableError("ct-props-correct.5",
                          new Object[]{typeName, idName, attrUseS[i].fAttrDecl.fName});
                }
            }
            else {
                if (extension) {
                    throw new ComplexTypeRecoverableError("ct-props-correct.4",
                          new Object[]{typeName, existingAttrUse.fAttrDecl.fName});
                }
            }
        }

        // For extension, the wildcard must be formed by doing a union of the wildcards
        if (extension) {
            if (toAttrGrp.fAttributeWC==null) {
                toAttrGrp.fAttributeWC = fromAttrGrp.fAttributeWC;
            }
            else if (fromAttrGrp.fAttributeWC != null) {
                toAttrGrp.fAttributeWC = toAttrGrp.fAttributeWC.performUnionWith(fromAttrGrp.fAttributeWC, toAttrGrp.fAttributeWC.fProcessContents);
            }

        }
    }



    private void processComplexContent(Element complexContentChild,
                                       XSComplexTypeDecl typeInfo,
                                       boolean isMixed, boolean isDerivation,
                                       XSDocumentInfo schemaDoc, SchemaGrammar grammar)
    throws ComplexTypeRecoverableError {

        Element attrNode = null;
        XSParticleDecl particle = null;
        String typeName = typeInfo.fName;

        if (complexContentChild != null) {
            // -------------------------------------------------------------
            // GROUP, ALL, SEQUENCE or CHOICE, followed by attributes, if specified.
            // Note that it's possible that only attributes are specified.
            // -------------------------------------------------------------


            String childName = DOMUtil.getLocalName(complexContentChild);

            if (childName.equals(SchemaSymbols.ELT_GROUP)) {

                particle = fSchemaHandler.fGroupTraverser.traverseLocal(complexContentChild,
                                                                        schemaDoc, grammar);
                attrNode = DOMUtil.getNextSiblingElement(complexContentChild);
            }
            else if (childName.equals(SchemaSymbols.ELT_SEQUENCE)) {
                particle = traverseSequence(complexContentChild,schemaDoc,grammar,
                                            NOT_ALL_CONTEXT);
                attrNode = DOMUtil.getNextSiblingElement(complexContentChild);
            }
            else if (childName.equals(SchemaSymbols.ELT_CHOICE)) {
                particle = traverseChoice(complexContentChild,schemaDoc,grammar,
                                          NOT_ALL_CONTEXT);
                attrNode = DOMUtil.getNextSiblingElement(complexContentChild);
            }
            else if (childName.equals(SchemaSymbols.ELT_ALL)) {
                particle = traverseAll(complexContentChild,schemaDoc,grammar,
                                       PROCESSING_ALL_GP);
                attrNode = DOMUtil.getNextSiblingElement(complexContentChild);
            }
            else {
                // Should be attributes here - will check below...
                attrNode = complexContentChild;
            }
        }

        typeInfo.fParticle = particle;

        // -----------------------------------------------------------------------
        // Set the content type
        // -----------------------------------------------------------------------

        if (isMixed) {
            typeInfo.fContentType = XSComplexTypeDecl.CONTENTTYPE_MIXED;
        }
        else if (typeInfo.fParticle == null)
            typeInfo.fContentType = XSComplexTypeDecl.CONTENTTYPE_EMPTY;
        else
            typeInfo.fContentType = XSComplexTypeDecl.CONTENTTYPE_ELEMENT;


        // -------------------------------------------------------------
        // Now, process attributes
        // -------------------------------------------------------------
        if (attrNode != null) {
            if (!isAttrOrAttrGroup(attrNode)) {
                throw new ComplexTypeRecoverableError("src-ct.0.1",
                                                      new Object[]{typeInfo.fName,DOMUtil.getLocalName(attrNode)});
            }
            Element node =
            traverseAttrsAndAttrGrps(attrNode,typeInfo.fAttrGrp,schemaDoc,grammar);
            if (node!=null) {
                throw new ComplexTypeRecoverableError("src-ct.0.1",
                                                      new Object[]{typeInfo.fName,DOMUtil.getLocalName(node)});
            }
            // Only remove prohibited attribute uses if this isn't a derived type
            // Derivation-specific code worries about this elsewhere
            if (!isDerivation) {
                typeInfo.fAttrGrp.removeProhibitedAttrs();
            }
        }



    } // end processComplexContent


    private boolean isAttrOrAttrGroup(Element e) {
        String elementName = DOMUtil.getLocalName(e);

        if (elementName.equals(SchemaSymbols.ELT_ATTRIBUTE) ||
            elementName.equals(SchemaSymbols.ELT_ATTRIBUTEGROUP) ||
            elementName.equals(SchemaSymbols.ELT_ANYATTRIBUTE))
            return true;
        else
            return false;
    }

    private void traverseSimpleContentDecl(Element simpleContentDecl,
                                           XSComplexTypeDecl typeInfo) {
    }

    private void traverseComplexContentDecl(Element complexContentDecl,
                                            XSComplexTypeDecl typeInfo,
                                            boolean mixedOnComplexTypeDecl) {
    }

    /*
     * Generate a name for an anonymous type
     */
    private String genAnonTypeName(Element complexTypeDecl) {

        // Generate a unique name for the anonymous type by concatenating together the
        // names of parent nodes
        // The name is quite good for debugging/error purposes, but we may want to
        // revisit how this is done for performance reasons (LM).
        String typeName;
        Element node = DOMUtil.getParent(complexTypeDecl);
        typeName="#AnonType_";
        while (node != null && (node != DOMUtil.getRoot(DOMUtil.getDocument(node)))) {
            typeName = typeName+node.getAttribute(SchemaSymbols.ATT_NAME);
            node = DOMUtil.getParent(node);
        }
        return typeName;
    }


    private void handleComplexTypeError(String messageId,Object[] args,
                                        XSComplexTypeDecl typeInfo) {

        if (messageId!=null) {
            reportSchemaError(messageId, args);
        }

        //
        //  Mock up the typeInfo structure so that there won't be problems during
        //  validation
        //
        typeInfo.fContentType = XSComplexTypeDecl.CONTENTTYPE_MIXED;
        typeInfo.fParticle = getErrorContent();

        return;

    }

    private static XSParticleDecl getErrorContent() {
        if (fErrorContent==null) {
            fErrorContent = new XSParticleDecl();
            fErrorContent.fType = XSParticleDecl.PARTICLE_SEQUENCE;
            XSParticleDecl particle = new XSParticleDecl();
            XSWildcardDecl wildcard = new XSWildcardDecl();
            wildcard.fProcessContents = XSWildcardDecl.WILDCARD_SKIP;
            particle.fType = XSParticleDecl.PARTICLE_WILDCARD;
            particle.fValue = wildcard;
            particle.fMinOccurs = 0;
            particle.fMaxOccurs = SchemaSymbols.OCCURRENCE_UNBOUNDED;
            fErrorContent.fValue = particle;
            fErrorContent.fOtherValue = null;
        }
        return fErrorContent;
    }
}
if (newDV != null && isGlobal) {

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

import org.apache.xerces.impl.XMLErrorReporter;
import org.apache.xerces.util.DOMUtil;
import org.apache.xerces.util.XInt;
import org.apache.xerces.util.XIntPool;
import org.apache.xerces.impl.v2.datatypes.*;
import org.apache.xerces.xni.QName;
import org.apache.xerces.util.NamespaceSupport;


import org.w3c.dom.Element;
import org.w3c.dom.Attr;
import org.w3c.dom.Node;

import java.lang.reflect.*;
import java.util.Stack;
import java.util.Hashtable;
import java.util.Vector;
import java.util.StringTokenizer;

/**
 * The simple type definition schema component traverser.
 *
 * <simpleType
 *   final = (#all | (list | union | restriction))
 *   id = ID
 *   name = NCName
 *   {any attributes with non-schema namespace . . .}>
 *   Content: (annotation?, (restriction | list | union))
 * </simpleType>
 *
 * <restriction
 *   base = QName
 *   id = ID
 *   {any attributes with non-schema namespace . . .}>
 *   Content: (annotation?, (simpleType?, (minExclusive | minInclusive | maxExclusive | maxInclusive | totalDigits | fractionDigits | length | minLength | maxLength | enumeration | whiteSpace | pattern)*))
 * </restriction>
 *
 * <list
 *   id = ID
 *   itemType = QName
 *   {any attributes with non-schema namespace . . .}>
 *   Content: (annotation?, (simpleType?))
 * </list>
 *
 * <union
 *   id = ID
 *   memberTypes = List of QName
 *   {any attributes with non-schema namespace . . .}>
 *   Content: (annotation?, (simpleType*))
 * </union>
 *
 * @author Elena Litani, IBM
 * @version $Id$
 */
class XSDSimpleTypeTraverser extends XSDAbstractTraverser {

    //private data
    private String fListName = "";

    private XSDocumentInfo fSchemaDoc = null;
    private SchemaGrammar fGrammar = null;
    private int fSimpleTypeAnonCount = 0;
    private final QName fQName = new QName();

    XSDSimpleTypeTraverser (XSDHandler handler,
                            XSAttributeChecker gAttrCheck) {
        super(handler, gAttrCheck);
    }

    //return qualified name of simpleType or empty string if error occured
    DatatypeValidator traverseGlobal(Element elmNode,
                                     XSDocumentInfo schemaDoc,
                                     SchemaGrammar grammar) {
        // General Attribute Checking
        fSchemaDoc = schemaDoc;
        fGrammar = grammar;
        Object[] attrValues = fAttrChecker.checkAttributes(elmNode, true, schemaDoc);
        String nameAtt = (String)attrValues[XSAttributeChecker.ATTIDX_NAME];
        DatatypeValidator type = traverseSimpleTypeDecl(elmNode, attrValues, schemaDoc, true);
        fAttrChecker.returnAttrArray(attrValues, schemaDoc);

        return type;
    }

    DatatypeValidator traverseLocal(Element elmNode,
                                    XSDocumentInfo schemaDoc,
                                    SchemaGrammar grammar) {
        fSchemaDoc = schemaDoc;
        fGrammar = grammar;

        Object[] attrValues = fAttrChecker.checkAttributes(elmNode, false, schemaDoc);
        DatatypeValidator type = traverseSimpleTypeDecl (elmNode, attrValues, schemaDoc, false);
        fAttrChecker.returnAttrArray(attrValues, schemaDoc);

        return type;
    }

    private DatatypeValidator traverseSimpleTypeDecl(Element simpleTypeDecl, Object[] attrValues,
                                                     XSDocumentInfo schemaDoc, boolean isGlobal) {

        String nameProperty  = (String)attrValues[XSAttributeChecker.ATTIDX_NAME];
        String qualifiedName = nameProperty;
        Hashtable fFacetData = null;

        //---------------------------------------------------
        // set qualified name
        //---------------------------------------------------
        if (nameProperty == null) { // anonymous simpleType
            qualifiedName = fSchemaDoc.fTargetNamespace == null?
                ",#s#"+(fSimpleTypeAnonCount++):
                fSchemaDoc.fTargetNamespace+",#S#"+(fSimpleTypeAnonCount++);
            //REVISIT:
            // add to symbol table?
        }
        else {
            qualifiedName = fSchemaDoc.fTargetNamespace == null?
                ","+nameProperty:
                fSchemaDoc.fTargetNamespace+","+nameProperty;
            //REVISIT:
            // add to symbol table?

        }

        //----------------------------------------------------------
        // REVISIT!
        // update _final_ registry
        //----------------------------------------------------------
        XInt finalAttr = (XInt)attrValues[XSAttributeChecker.ATTIDX_FINAL];
        int finalProperty = finalAttr == null ? schemaDoc.fFinalDefault : finalAttr.intValue();

        //----------------------------------------------------------------------
        //annotation?,(list|restriction|union)
        //----------------------------------------------------------------------
        Element content = DOMUtil.getFirstChildElement(simpleTypeDecl);
        content = checkContent(content, attrValues, schemaDoc);
        if (content == null) {
            reportGenericSchemaError("no child element found for simpleType '"+ nameProperty+"'");
            return null;
        }

        // General Attribute Checking
        Object[] contentAttrs = fAttrChecker.checkAttributes(content, false, schemaDoc);
        // REVISIT: when to return the array
        fAttrChecker.returnAttrArray(contentAttrs, schemaDoc);

        //----------------------------------------------------------------------
        //use content.getLocalName for the cases there "xsd:" is a prefix, ei. "xsd:list"
        //----------------------------------------------------------------------
        String varietyProperty =  DOMUtil.getLocalName(content);  //content.getLocalName();
        QName baseTypeName = null;
        Vector memberTypes = null;
        Vector dTValidators = null;
        int size = 0;
        boolean list = false;
        boolean union = false;
        boolean restriction = false;
        int numOfTypes = 0; //list/restriction = 1, union = "+"

        if (varietyProperty.equals(SchemaSymbols.ELT_LIST)) { //traverse List
            baseTypeName = (QName)contentAttrs[XSAttributeChecker.ATTIDX_ITEMTYPE];
            list = true;
            if (fListName.length() != 0) { // parent is <list> datatype
                reportCosListOfAtomic();
                return null;
            }
            else {
                fListName = qualifiedName;
            }
        }
        else if (varietyProperty.equals(SchemaSymbols.ELT_RESTRICTION)) { //traverse Restriction
            baseTypeName = (QName)contentAttrs[XSAttributeChecker.ATTIDX_BASE];
            //content.getAttribute( SchemaSymbols.ATT_BASE );
            restriction= true;
        }
        else if (varietyProperty.equals(SchemaSymbols.ELT_UNION)) { //traverse union
            union = true;
            memberTypes = (Vector)contentAttrs[XSAttributeChecker.ATTIDX_MEMBERTYPES];
            //content.getAttribute( SchemaSymbols.ATT_MEMBERTYPES);
            if (memberTypes != null) {
                size = memberTypes.size();
            }
            else {
                size = 1; //at least one must be seen as <simpleType> decl
            }
            dTValidators = new Vector (size, 2);
        }
        else {
            Object[] args = { varietyProperty};
            fErrorReporter.reportError(XSMessageFormatter.SCHEMA_DOMAIN,
                                       "FeatureUnsupported",
                                       args, XMLErrorReporter.SEVERITY_ERROR);
        }
        if (DOMUtil.getNextSiblingElement(content) != null) {
            // REVISIT: Localize
            reportGenericSchemaError("error in content of simpleType");
        }

        DatatypeValidator baseValidator = null;
        if (baseTypeName == null && memberTypes == null) {
            //---------------------------
            //must 'see' <simpleType>
            //---------------------------

            //content = {annotation?,simpleType?...}
            content = DOMUtil.getFirstChildElement(content);

            //check content (annotation?, ...)
            content = checkContent(content, contentAttrs, schemaDoc);
            if (content == null) {
                reportGenericSchemaError("no child element found for simpleType '"+ nameProperty+"'");
                return null;
            }
            if (DOMUtil.getLocalName(content).equals( SchemaSymbols.ELT_SIMPLETYPE )) {
                baseValidator = traverseLocal(content, fSchemaDoc, fGrammar);
                if (baseValidator != null && union) {
                    dTValidators.addElement((DatatypeValidator)baseValidator);
                }
                if (baseValidator == null) {
                    Object[] args = {content.getAttribute( SchemaSymbols.ATT_BASE )};
                    fErrorReporter.reportError(XSMessageFormatter.SCHEMA_DOMAIN,
                                               "UnknownBaseDatatype",
                                               args,
                                               XMLErrorReporter.SEVERITY_ERROR);
                    return null;
                }
            }
            else {
                Object[] args = { simpleTypeDecl.getAttribute( SchemaSymbols.ATT_NAME )};
                fErrorReporter.reportError(XSMessageFormatter.SCHEMA_DOMAIN,
                                           "ListUnionRestrictionError",
                                           args,
                                           XMLErrorReporter.SEVERITY_ERROR);
                return null;
            }
        } //end - must see simpleType?
        else {
            //-----------------------------
            //base was provided - get proper validator.
            //-----------------------------
            numOfTypes = 1;
            if (union) {
                numOfTypes= size;
            }
            //--------------------------------------------------------------------
            // this loop is also where we need to find out whether the type being used as
            // a base (or itemType or whatever) allows such things.
            //--------------------------------------------------------------------
            int baseRefContext = (restriction? SchemaSymbols.RESTRICTION:0);
            baseRefContext = baseRefContext | (union? SchemaSymbols.UNION:0);
            baseRefContext = baseRefContext | (list ? SchemaSymbols.LIST:0);
            for (int i=0; i<numOfTypes; i++) {  //find all validators
                if (union) {
                    baseTypeName = (QName)memberTypes.elementAt(i);
                }
                baseValidator = findDTValidator ( simpleTypeDecl, baseTypeName, baseRefContext);
                if (baseValidator == null) {
                    reportGenericSchemaError("base type not found: '"+baseTypeName.uri+","+baseTypeName.localpart+"'");
                    baseValidator = (DatatypeValidator)SchemaGrammar.SG_SchemaNS.getGlobalTypeDecl(SchemaSymbols.ATTVAL_STRING);
                }
                // ------------------------------
                // (variety is list)cos-list-of-atomic
                // ------------------------------
                if (fListName.length() != 0) {
                    if (baseValidator instanceof ListDatatypeValidator) {
                        reportCosListOfAtomic();
                        return null;
                    }
                    //-----------------------------------------------------
                    // if baseValidator is of type (union) need to look
                    // at Union validators to make sure that List is not one of them
                    //-----------------------------------------------------
                    if (isListDatatype(baseValidator)) {
                        reportCosListOfAtomic();
                        return null;

                    }

                }
                if (union) {
                    dTValidators.addElement((DatatypeValidator)baseValidator); //add validator to structure
                }
            }
        } //end - base is available


        // ------------------------------------------
        // move to next child
        // <base==empty)->[simpleType]->[facets]  OR
        // <base!=empty)->[facets]
        // ------------------------------------------
        if (baseTypeName == null) {
            content = DOMUtil.getNextSiblingElement( content );
        }
        else {
            content = DOMUtil.getFirstChildElement(content);
        }

        // ------------------------------------------
        //get more types for union if any
        // ------------------------------------------
        if (union) {
            int index=size;
            if (memberTypes != null) {
                content = checkContent(content, contentAttrs, schemaDoc);
            }
            while (content!=null) {
                baseValidator = traverseLocal(content, fSchemaDoc, fGrammar);
                if (baseValidator != null) {
                    if (fListName.length() != 0 && baseValidator instanceof ListDatatypeValidator) {
                        reportCosListOfAtomic();
                        return null;
                    }
                    dTValidators.addElement((DatatypeValidator)baseValidator);
                }
                if (baseValidator == null) {
                    Object[] args = { simpleTypeDecl.getAttribute( SchemaSymbols.ATT_BASE ), simpleTypeDecl.getAttribute(SchemaSymbols.ATT_NAME)};
                    fErrorReporter.reportError(XSMessageFormatter.SCHEMA_DOMAIN,
                                               "UnknownBaseDatatype",
                                               args,
                                               XMLErrorReporter.SEVERITY_ERROR);
                    baseValidator = (DatatypeValidator)SchemaGrammar.SG_SchemaNS.getGlobalTypeDecl(SchemaSymbols.ATTVAL_STRING);
                }
                content   = DOMUtil.getNextSiblingElement( content );
            }
        } // end - traverse Union

        if (fListName.length() != 0) {
            // reset fListName, meaning that we are done with
            // traversing <list> and its itemType resolves to atomic value
            if (fListName.equals(qualifiedName)) {
                fListName = fSchemaHandler.EMPTY_STRING;
            }
        }

        if (restriction && content != null) {
            fFacetInfo fi = traverseFacets(content, contentAttrs,nameProperty, baseValidator, schemaDoc, fGrammar);
            fFacetData = fi.facetdata;
        }

        DatatypeValidator newDV = null;
        if (list) {
            try {
                newDV = new ListDatatypeValidator(baseValidator, fFacetData, true);
            } catch (InvalidDatatypeFacetException e) {
                reportGenericSchemaError(e.getMessage());
            }
        }
        else if (restriction) {
            newDV = createRestrictedValidator(baseValidator, fFacetData); 
        }
        else { //union
            newDV = new UnionDatatypeValidator(dTValidators);
        }

        if (newDV != null) {
            newDV.setFinalSet(finalProperty);
            ((AbstractDatatypeValidator)newDV).fLocalName = nameProperty;
            fGrammar.addGlobalTypeDecl(newDV);
        }

        return newDV;
    }


    private void reportCosListOfAtomic () {
        reportGenericSchemaError("cos-list-of-atomic: The itemType must have a {variety} of atomic or union (in which case all the {member type definitions} must be atomic)");
        fListName=fSchemaHandler.EMPTY_STRING;
    }

    //@param: elm - top element
    //@param: baseTypeStr - type (base/itemType/memberTypes)
    //@param: baseRefContext:  whether the caller is using this type as a base for restriction, union or list
    //return DatatypeValidator available for the baseTypeStr, null if not found or disallowed.
    // also throws an error if the base type won't allow itself to be used in this context.
    // REVISIT: can this code be re-used?
    private DatatypeValidator findDTValidator (Element elm, QName baseTypeStr, int baseRefContext ) {
        if (baseTypeStr.uri.equals(SchemaSymbols.URI_SCHEMAFORSCHEMA) &&
            baseTypeStr.localpart.equals(SchemaSymbols.ATTVAL_ANYSIMPLETYPE) &&
            baseRefContext == SchemaSymbols.RESTRICTION) {
            //REVISIT
            //reportSchemaError(SchemaMessageProvider.UnknownBaseDatatype,
            //                  new Object [] { DOMUtil.getAttrValue(elm, SchemaSymbols.ATT_BASE),
            //                      DOMUtil.getAttrValue(elm, SchemaSymbols.ATT_NAME)});
            return null;
        }
        DatatypeValidator baseValidator = null;
        baseValidator = (DatatypeValidator)fSchemaHandler.getGlobalDecl(fSchemaDoc, fSchemaHandler.TYPEDECL_TYPE, baseTypeStr);
        if (baseValidator != null) {
            if ((baseValidator.getFinalSet() & baseRefContext) != 0) {
                reportGenericSchemaError("the base type " + baseTypeStr.rawname + " does not allow itself to be used as the base for a restriction and/or as a type in a list and/or union");
            }
        }
        return baseValidator;
    }

    // find if union datatype validator has list datatype member.
    private boolean isListDatatype (DatatypeValidator validator) {
        if (validator instanceof UnionDatatypeValidator) {
            Vector temp = ((UnionDatatypeValidator)validator).getBaseValidators();
            for (int i=0;i<temp.size();i++) {
                if (temp.elementAt(i) instanceof ListDatatypeValidator) {
                    return true;
                }
                if (temp.elementAt(i) instanceof UnionDatatypeValidator) {
                    if (isListDatatype((DatatypeValidator)temp.elementAt(i))) {
                        return true;
                    }
                }
            }
        }
        return false;
    }

}
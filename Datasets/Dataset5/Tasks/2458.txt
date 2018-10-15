if (isGlobal && nameAtt != null)

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

import org.apache.xerces.impl.dv.xs.*;
import org.apache.xerces.impl.xs.SchemaGrammar;
import org.apache.xerces.impl.xs.SchemaSymbols;
import org.apache.xerces.impl.xs.XSAttributeDecl;
import org.apache.xerces.impl.xs.XSAttributeUse;
import org.apache.xerces.impl.xs.XSElementDecl;
import org.apache.xerces.impl.xs.XSTypeDecl;
import org.apache.xerces.xni.QName;
import org.apache.xerces.impl.XMLErrorReporter;
import org.apache.xerces.util.DOMUtil;
import org.apache.xerces.impl.xs.util.XInt;
import org.w3c.dom.Element;

/**
 * The attribute declaration schema component traverser.
 *
 * <attribute
 *   default = string
 *   fixed = string
 *   form = (qualified | unqualified)
 *   id = ID
 *   name = NCName
 *   ref = QName
 *   type = QName
 *   use = (optional | prohibited | required) : optional
 *   {any attributes with non-schema namespace . . .}>
 *   Content: (annotation?, (simpleType?))
 * </attribute>
 *
 * @author Sandy Gao, IBM
 *
 * @version $Id$
 */
class XSDAttributeTraverser extends XSDAbstractTraverser {

    public XSDAttributeTraverser (XSDHandler handler,
                                  XSAttributeChecker gAttrCheck) {
        super(handler, gAttrCheck);
    }

    protected XSAttributeUse traverseLocal(Element attrDecl,
                                           XSDocumentInfo schemaDoc,
                                           SchemaGrammar grammar) {

        // General Attribute Checking
        Object[] attrValues = fAttrChecker.checkAttributes(attrDecl, false, schemaDoc);

        String defaultAtt = (String) attrValues[XSAttributeChecker.ATTIDX_DEFAULT];
        String fixedAtt   = (String) attrValues[XSAttributeChecker.ATTIDX_FIXED];
        String nameAtt    = (String) attrValues[XSAttributeChecker.ATTIDX_NAME];
        QName  refAtt     = (QName)  attrValues[XSAttributeChecker.ATTIDX_REF];
        XInt   useAtt     = (XInt)   attrValues[XSAttributeChecker.ATTIDX_USE];

        // get 'attribute declaration'
        XSAttributeDecl attribute = null;
        if (refAtt != null) {
            attribute = (XSAttributeDecl)fSchemaHandler.getGlobalDecl(schemaDoc, XSDHandler.ATTRIBUTE_TYPE, refAtt);

            Element child = DOMUtil.getFirstChildElement(attrDecl);
            if(child != null && DOMUtil.getLocalName(child).equals(SchemaSymbols.ELT_ANNOTATION)) {
                traverseAnnotationDecl(child, attrValues, false, schemaDoc);
                child = DOMUtil.getNextSiblingElement(child);
            }

            if (child != null) {
                reportSchemaError("src-attribute.3.2", new Object[]{refAtt});
            }
            // for error reporting
            nameAtt = refAtt.localpart;
        } else {
            attribute = traverseNamedAttr(attrDecl, attrValues, schemaDoc, grammar, false);
        }

        // get 'value constraint'
        short consType = XSAttributeDecl.NO_CONSTRAINT;
        if (defaultAtt != null) {
            consType = XSAttributeDecl.DEFAULT_VALUE;
        } else if (fixedAtt != null) {
            consType = XSAttributeDecl.FIXED_VALUE;
            defaultAtt = fixedAtt;
            fixedAtt = null;
        }

        XSAttributeUse attrUse = null;
        if (attribute != null) {
            attrUse = new XSAttributeUse();
            attrUse.fAttrDecl = attribute;
            attrUse.fUse = useAtt.shortValue();
            attrUse.fConstraintType = consType;
            attrUse.fDefault = defaultAtt;
        }
        fAttrChecker.returnAttrArray(attrValues, schemaDoc);

        //src-attribute

        // 1 default and fixed must not both be present.
        if (defaultAtt != null && fixedAtt != null) {
            reportSchemaError("src-attribute.1", new Object[]{nameAtt});
        }

        // 2 If default and use are both present, use must have the ·actual value· optional.
        if (consType == XSAttributeDecl.DEFAULT_VALUE &&
            useAtt != null && useAtt.intValue() != SchemaSymbols.USE_OPTIONAL) {
            reportSchemaError("src-attribute.2", new Object[]{nameAtt});
        }

        // a-props-correct

        if (defaultAtt != null && attrUse != null) {
            // 2 if there is a {value constraint}, the canonical lexical representation of its value must be ·valid· with respect to the {type definition} as defined in String Valid (§3.14.4).
            if (!checkDefaultValid(attrUse)) {
                reportSchemaError ("a-props-correct.2", new Object[]{nameAtt, defaultAtt});
            }

            // 3 If the {type definition} is or is derived from ID then there must not be a {value constraint}.
            if (attribute.fType instanceof IDDatatypeValidator) {
                reportSchemaError ("a-props-correct.3", new Object[]{nameAtt});
            }

            // check 3.5.6 constraint
            // Attribute Use Correct
            // 2 If the {attribute declaration} has a fixed {value constraint}, then if the attribute use itself has a {value constraint}, it must also be fixed and its value must match that of the {attribute declaration}'s {value constraint}.
            if (attrUse.fAttrDecl.fConstraintType == XSAttributeDecl.FIXED_VALUE &&
                attrUse.fConstraintType != XSAttributeDecl.NO_CONSTRAINT) {
                if (attrUse.fConstraintType != XSAttributeDecl.FIXED_VALUE ||
                    attrUse.fAttrDecl.fType.compare((String)attrUse.fAttrDecl.fDefault,
                                                    (String)attrUse.fDefault) != 0) {
                    reportSchemaError ("au-props-correct.2", new Object[]{nameAtt});
                }
            }
        }

        return attrUse;
    }

    protected XSAttributeDecl traverseGlobal(Element attrDecl,
                                             XSDocumentInfo schemaDoc,
                                             SchemaGrammar grammar) {

        // General Attribute Checking
        Object[] attrValues = fAttrChecker.checkAttributes(attrDecl, true, schemaDoc);
        XSAttributeDecl attribute = traverseNamedAttr(attrDecl, attrValues, schemaDoc, grammar, true);
        fAttrChecker.returnAttrArray(attrValues, schemaDoc);

        return attribute;
    }

    /**
     * Traverse a globally declared attribute.
     *
     * @param  attrDecl
     * @param  attrValues
     * @param  schemaDoc
     * @param  grammar
     * @param  isGlobal
     * @return the attribute declaration index
     */
    XSAttributeDecl traverseNamedAttr(Element attrDecl,
                                      Object[] attrValues,
                                      XSDocumentInfo schemaDoc,
                                      SchemaGrammar grammar,
                                      boolean isGlobal) {

        String  defaultAtt = (String) attrValues[XSAttributeChecker.ATTIDX_DEFAULT];
        String  fixedAtt   = (String) attrValues[XSAttributeChecker.ATTIDX_FIXED];
        XInt    formAtt    = (XInt)   attrValues[XSAttributeChecker.ATTIDX_FORM];
        String  nameAtt    = (String) attrValues[XSAttributeChecker.ATTIDX_NAME];
        QName   typeAtt    = (QName)  attrValues[XSAttributeChecker.ATTIDX_TYPE];

        // Step 1: get declaration information
        XSAttributeDecl attribute = new XSAttributeDecl();

        // get 'name'
        if (nameAtt != null)
            attribute.fName = fSymbolTable.addSymbol(nameAtt);

        // get 'target namespace'
        if (isGlobal) {
            attribute.fTargetNamespace = schemaDoc.fTargetNamespace;
        }
        else if (formAtt != null) {
            if (formAtt.intValue() == SchemaSymbols.FORM_QUALIFIED)
                attribute.fTargetNamespace = schemaDoc.fTargetNamespace;
            else
                attribute.fTargetNamespace = null;
        } else if (schemaDoc.fAreLocalAttributesQualified) {
            attribute.fTargetNamespace = schemaDoc.fTargetNamespace;
        } else {
            attribute.fTargetNamespace = null;
        }

        // get 'value constraint'
        // for local named attribute, value constraint is absent
        if (isGlobal) {
            if (fixedAtt != null) {
                attribute.fDefault = fixedAtt;
                attribute.fConstraintType = XSElementDecl.FIXED_VALUE;
            } else if (defaultAtt != null) {
                attribute.fDefault = defaultAtt;
                attribute.fConstraintType = XSElementDecl.DEFAULT_VALUE;
            } else {
                attribute.fConstraintType = XSElementDecl.NO_CONSTRAINT;
            }
        }

        // get 'annotation'
        Element child = DOMUtil.getFirstChildElement(attrDecl);
        if(child != null && DOMUtil.getLocalName(child).equals(SchemaSymbols.ELT_ANNOTATION)) {
            traverseAnnotationDecl(child, attrValues, false, schemaDoc);
            child = DOMUtil.getNextSiblingElement(child);
        }

        // get 'type definition'
        DatatypeValidator attrType = null;
        boolean haveAnonType = false;

        // Handle Anonymous type if there is one
        if (child != null) {
            String childName = DOMUtil.getLocalName(child);

            if (childName.equals(SchemaSymbols.ELT_SIMPLETYPE)) {
                attrType = fSchemaHandler.fSimpleTypeTraverser.traverseLocal(child, schemaDoc, grammar);
                haveAnonType = true;
                child = DOMUtil.getNextSiblingElement(child);
            }
        }

        // Handler type attribute
        if (attrType == null && typeAtt != null) {
            XSTypeDecl type = (XSTypeDecl)fSchemaHandler.getGlobalDecl(schemaDoc, XSDHandler.TYPEDECL_TYPE, typeAtt);
            if (type instanceof DatatypeValidator)
                attrType = (DatatypeValidator)type;
            else
                // REVISIT: what should be the error code here
                reportGenericSchemaError("the type for attribute '"+nameAtt+"' must be a simpleType");
        }

        if (attrType == null) {
            attrType = SchemaGrammar.fAnySimpleType;
        }

        attribute.fType = attrType;

        // Step 2: register attribute decl to the grammar
        if (nameAtt != null)
            grammar.addGlobalAttributeDecl(attribute);

        // Step 3: check against schema for schemas

        // required attributes
        if (nameAtt == null) {
            if (isGlobal)
                reportSchemaError("s4s-att-must-appear", new Object[]{NO_NAME, SchemaSymbols.ATT_NAME});
            else
                reportSchemaError("src-attribute.3.1", null);
            nameAtt = NO_NAME;
        }

        // element
        if (child != null) {
            reportSchemaError("s4s-elt-must-match", new Object[]{nameAtt, "(annotation?, (simpleType?))"});
        }

        // Step 4: check 3.2.3 constraints

        // src-attribute

        // 1 default and fixed must not both be present.
        if (defaultAtt != null && fixedAtt != null) {
            reportSchemaError("src-attribute.1", new Object[]{nameAtt});
        }

        // 2 If default and use are both present, use must have the ·actual value· optional.
        // This is checked in "traverse" method

        // 3 If the item's parent is not <schema>, then all of the following must be true:
        // 3.1 One of ref or name must be present, but not both.
        // This is checked in XSAttributeChecker

        // 3.2 If ref is present, then all of <simpleType>, form and type must be absent.
        // Attributes are checked in XSAttributeChecker, elements are checked in "traverse" method

        // 4 type and <simpleType> must not both be present.
        if (haveAnonType && (typeAtt != null)) {
            reportSchemaError( "src-attribute.4", new Object[]{nameAtt});
        }

        // Step 5: check 3.2.6 constraints
        // check for NOTATION type
        checkNotationType(nameAtt, attrType);

        // a-props-correct

        // 2 if there is a {value constraint}, the canonical lexical representation of its value must be ·valid· with respect to the {type definition} as defined in String Valid (§3.14.4).
        if (attribute.fDefault != null) {
            if (!checkDefaultValid(attribute)) {
                reportSchemaError ("a-props-correct.2", new Object[]{nameAtt, defaultAtt});
            }
        }

        // 3 If the {type definition} is or is derived from ID then there must not be a {value constraint}.
        if (attribute.fDefault != null) {
            if (attrType instanceof IDDatatypeValidator) {
                reportSchemaError ("a-props-correct.3", new Object[]{nameAtt});
            }
        }

        // no-xmlns

        // The {name} of an attribute declaration must not match xmlns.
        if (nameAtt != null && nameAtt.equals(SchemaSymbols.XMLNS)) {
            reportSchemaError("no-xmlns", null);
        }

        // no-xsi

        // The {target namespace} of an attribute declaration, whether local or top-level, must not match http://www.w3.org/2001/XMLSchema-instance (unless it is one of the four built-in declarations given in the next section).
        if (attribute.fTargetNamespace != null && attribute.fTargetNamespace.equals(SchemaSymbols.URI_XSI)) {
            reportSchemaError("no-xsi", new Object[]{SchemaSymbols.URI_XSI});
        }

        return attribute;
    }

    // return whether the constraint value is valid for the given type
    boolean checkDefaultValid(XSAttributeDecl attribute) {

        boolean ret = true;

        try {

            //REVISIT:  Our validators don't return Objects yet, instead  return null
            //
            //attribute.fDefault = attribute.fType.validate((String)attribute.fDefault, null);
            attribute.fType.validate((String)attribute.fDefault, null);
        } catch (InvalidDatatypeValueException ide) {
            ret = false;
        }

        return ret;
    }

    // return whether the constraint value is valid for the given type
    boolean checkDefaultValid(XSAttributeUse attrUse) {

        boolean ret = true;

        try {

            //REVISIT:  Our validators don't return Objects yet, instead  return null
            //
            //attrUse.fDefault = attrUse.fAttrDecl.fType.validate((String)attrUse.fDefault, null);
            attrUse.fAttrDecl.fType.validate((String)attrUse.fDefault, null);
        } catch (InvalidDatatypeValueException ide) {
            ret = false;
        }

        return ret;
    }

}
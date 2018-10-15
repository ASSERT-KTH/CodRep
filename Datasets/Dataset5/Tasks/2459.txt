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
import org.apache.xerces.impl.XMLErrorReporter;
import org.apache.xerces.impl.xs.XSConstraints;
import org.apache.xerces.impl.xs.SubstitutionGroupHandler;
import org.apache.xerces.impl.xs.SchemaGrammar;
import org.apache.xerces.impl.xs.SchemaSymbols;
import org.apache.xerces.impl.xs.XSElementDecl;
import org.apache.xerces.impl.xs.XSParticleDecl;
import org.apache.xerces.impl.xs.XSComplexTypeDecl;
import org.apache.xerces.impl.xs.XSTypeDecl;
import org.apache.xerces.util.DOMUtil;
import org.apache.xerces.impl.xs.util.XInt;
import org.apache.xerces.impl.xs.util.XIntPool;
import org.apache.xerces.util.SymbolTable;
import org.apache.xerces.xni.QName;
import  org.w3c.dom.Element;

/**
 * The element declaration schema component traverser.
 * <element
 *   abstract = boolean : false
 *   block = (#all | List of (extension | restriction | substitution))
 *   default = string
 *   final = (#all | List of (extension | restriction))
 *   fixed = string
 *   form = (qualified | unqualified)
 *   id = ID
 *   maxOccurs = (nonNegativeInteger | unbounded)  : 1
 *   minOccurs = nonNegativeInteger : 1
 *   name = NCName
 *   nillable = boolean : false
 *   ref = QName
 *   substitutionGroup = QName
 *   type = QName
 *   {any attributes with non-schema namespace . . .}>
 *   Content: (annotation?, ((simpleType | complexType)?, (unique | key | keyref)*))
 * </element>
 *
 * @author Sandy Gao, IBM
 *
 * @version $Id$
 */
class XSDElementTraverser extends XSDAbstractTraverser {

    protected XSElementDecl  fTempElementDecl  = new XSElementDecl();
    protected XSParticleDecl fTempParticleDecl = new XSParticleDecl();

    SubstitutionGroupHandler fSubGroupHandler;

    // this controls what happens when a local element is encountered.
    // We may not encounter all local elements when first parsing.
    boolean fDeferTraversingLocalElements;

    XSDElementTraverser (XSDHandler handler,
                         XSAttributeChecker gAttrCheck,
                         SubstitutionGroupHandler subGroupHandler) {
        super(handler, gAttrCheck);
        fSubGroupHandler = subGroupHandler;
    }

    /**
     * Traverse a locally declared element (or an element reference).
     *
     * To handle the recursive cases efficiently, we delay the traversal
     * and return an empty particle node. We'll fill in this particle node
     * later after we've done with all the global declarations.
     * This method causes a number of data structures in the schema handler to be filled in.
     *
     * @param  elmDecl
     * @param  schemaDoc
     * @param  grammar
     * @return the particle
     */
    XSParticleDecl traverseLocal(Element elmDecl,
                                 XSDocumentInfo schemaDoc,
                                 SchemaGrammar grammar,
                                 int allContextFlags) {

        XSParticleDecl particle = new XSParticleDecl();

        if(fDeferTraversingLocalElements) {
            fSchemaHandler.fillInLocalElemInfo(elmDecl, schemaDoc, allContextFlags, particle);
        } else {
            traverseLocal(particle, elmDecl, schemaDoc, grammar, allContextFlags);
        }

        return particle;
    }

    /**
     * Traverse a locally declared element (or an element reference).
     *
     * This is the real traversal method. It's called after we've done with
     * all the global declarations.
     *
     * @param  index
     */
    protected void traverseLocal(XSParticleDecl particle, Element elmDecl,
                               XSDocumentInfo schemaDoc,
                               SchemaGrammar grammar,
                               int allContextFlags) {

        // General Attribute Checking
        Object[] attrValues = fAttrChecker.checkAttributes(elmDecl, false, schemaDoc);

        QName refAtt = (QName) attrValues[XSAttributeChecker.ATTIDX_REF];
        XInt  minAtt = (XInt)  attrValues[XSAttributeChecker.ATTIDX_MINOCCURS];
        XInt  maxAtt = (XInt)  attrValues[XSAttributeChecker.ATTIDX_MAXOCCURS];

        XSElementDecl element = null;
        if (refAtt != null) {
            element = (XSElementDecl)fSchemaHandler.getGlobalDecl(schemaDoc, XSDHandler.ELEMENT_TYPE, refAtt);

            Element child = DOMUtil.getFirstChildElement(elmDecl);
            if (child != null && DOMUtil.getLocalName(child).equals(SchemaSymbols.ELT_ANNOTATION)) {
                traverseAnnotationDecl(child, attrValues, false, schemaDoc);
                child = DOMUtil.getNextSiblingElement(child);
            }

            // Element Declaration Representation OK
            // 2 If the item's parent is not <schema>, then all of the following must be true:
            // 2.1 One of ref or name must be present, but not both.
            // 2.2 If ref is present, then all of <complexType>, <simpleType>, <key>, <keyref>, <unique>, nillable, default, fixed, form, block and type must be absent, i.e. only minOccurs, maxOccurs, id are allowed in addition to ref, along with <annotation>.
            if (child != null) {
                reportSchemaError("src-element.2.2", new Object[]{refAtt});
            }
        } else {
            element = traverseNamedElement(elmDecl, attrValues, schemaDoc, grammar, false);
        }

        particle.fMinOccurs = minAtt.intValue();
        particle.fMaxOccurs = maxAtt.intValue();
        if (element != null) {
            particle.fType = XSParticleDecl.PARTICLE_ELEMENT;
            particle.fValue = element;
        }
        Long defaultVals = (Long)attrValues[XSAttributeChecker.ATTIDX_FROMDEFAULT];
        checkOccurrences(particle, SchemaSymbols.ELT_ELEMENT,
                         (Element)elmDecl.getParentNode(), allContextFlags,
                         defaultVals.longValue());

        fAttrChecker.returnAttrArray(attrValues, schemaDoc);
    }

    /**
     * Traverse a globally declared element.
     *
     * @param  elmDecl
     * @param  schemaDoc
     * @param  grammar
     * @return the element declaration
     */
    XSElementDecl traverseGlobal(Element elmDecl,
                                 XSDocumentInfo schemaDoc,
                                 SchemaGrammar grammar) {

        // General Attribute Checking
        Object[] attrValues = fAttrChecker.checkAttributes(elmDecl, true, schemaDoc);
        XSElementDecl element = traverseNamedElement(elmDecl, attrValues, schemaDoc, grammar, true);
        fAttrChecker.returnAttrArray(attrValues, schemaDoc);

        return element;
    }

    /**
     * Traverse a globally declared element.
     *
     * @param  elmDecl
     * @param  attrValues
     * @param  schemaDoc
     * @param  grammar
     * @param  isGlobal
     * @return the element declaration
     */
    XSElementDecl traverseNamedElement(Element elmDecl,
                                       Object[] attrValues,
                                       XSDocumentInfo schemaDoc,
                                       SchemaGrammar grammar,
                                       boolean isGlobal) {

        Boolean abstractAtt  = (Boolean) attrValues[XSAttributeChecker.ATTIDX_ABSTRACT];
        XInt    blockAtt     = (XInt)    attrValues[XSAttributeChecker.ATTIDX_BLOCK];
        String  defaultAtt   = (String)  attrValues[XSAttributeChecker.ATTIDX_DEFAULT];
        XInt    finalAtt     = (XInt)    attrValues[XSAttributeChecker.ATTIDX_FINAL];
        String  fixedAtt     = (String)  attrValues[XSAttributeChecker.ATTIDX_FIXED];
        XInt    formAtt      = (XInt)    attrValues[XSAttributeChecker.ATTIDX_FORM];
        String  nameAtt      = (String)  attrValues[XSAttributeChecker.ATTIDX_NAME];
        Boolean nillableAtt  = (Boolean) attrValues[XSAttributeChecker.ATTIDX_NILLABLE];
        QName   subGroupAtt  = (QName)   attrValues[XSAttributeChecker.ATTIDX_SUBSGROUP];
        QName   typeAtt      = (QName)   attrValues[XSAttributeChecker.ATTIDX_TYPE];

        // Step 1: get declaration information
        XSElementDecl element = new XSElementDecl();

        // get 'name'
        if (nameAtt != null)
            element.fName = fSymbolTable.addSymbol(nameAtt);

        // get 'target namespace'
        if (isGlobal) {
            element.fTargetNamespace = schemaDoc.fTargetNamespace;
        }
        else if (formAtt != null) {
            if (formAtt.intValue() == SchemaSymbols.FORM_QUALIFIED)
                element.fTargetNamespace = schemaDoc.fTargetNamespace;
            else
                element.fTargetNamespace = null;
        } else if (schemaDoc.fAreLocalElementsQualified) {
            element.fTargetNamespace = schemaDoc.fTargetNamespace;
        } else {
            element.fTargetNamespace = null;
        }

        // get 'block', 'final', 'nillable', 'abstract'
        element.fBlock = blockAtt == null ? schemaDoc.fBlockDefault : blockAtt.shortValue();
        element.fFinal = finalAtt == null ? schemaDoc.fFinalDefault : finalAtt.shortValue();
        if (nillableAtt.booleanValue())
            element.setIsNillable();
        if (abstractAtt != null && abstractAtt.booleanValue())
            element.setIsAbstract();

        // get 'value constraint'
        if (fixedAtt != null) {
            element.fDefault = fixedAtt;
            element.setConstraintType(XSElementDecl.FIXED_VALUE);
        } else if (defaultAtt != null) {
            element.fDefault = defaultAtt;
            element.setConstraintType(XSElementDecl.DEFAULT_VALUE);
        } else {
            element.setConstraintType(XSElementDecl.NO_CONSTRAINT);
        }

        // get 'substitutionGroup affiliation'
        // REVISIT: allow mutual-substitution
        //          we need to back-patch both fSubGroup and fType
        //          if there is no type attribute and no anonymous type
        if (subGroupAtt != null) {
            element.fSubGroup = (XSElementDecl)fSchemaHandler.getGlobalDecl(schemaDoc, XSDHandler.ELEMENT_TYPE, subGroupAtt);
        }

        // get 'annotation'
        Element child = DOMUtil.getFirstChildElement(elmDecl);
        if(child != null && DOMUtil.getLocalName(child).equals(SchemaSymbols.ELT_ANNOTATION)) {
            traverseAnnotationDecl(child, attrValues, false, schemaDoc);
            child = DOMUtil.getNextSiblingElement(child);
        }

        // get 'type definition'
        XSTypeDecl elementType = null;
        boolean haveAnonType = false;

        // Handle Anonymous type if there is one
        if (child != null) {
            String childName = DOMUtil.getLocalName(child);

            if (childName.equals(SchemaSymbols.ELT_COMPLEXTYPE)) {
                elementType = fSchemaHandler.fComplexTypeTraverser.traverseLocal(child, schemaDoc, grammar);
                haveAnonType = true;
                child = DOMUtil.getNextSiblingElement(child);
            }
            else if (childName.equals(SchemaSymbols.ELT_SIMPLETYPE)) {
                elementType = fSchemaHandler.fSimpleTypeTraverser.traverseLocal(child, schemaDoc, grammar);
                haveAnonType = true;
                child = DOMUtil.getNextSiblingElement(child);
            }
        }

        // Handler type attribute
        if (elementType == null && typeAtt != null) {
            elementType = (XSTypeDecl)fSchemaHandler.getGlobalDecl(schemaDoc, XSDHandler.TYPEDECL_TYPE, typeAtt);
        }

        // Get it from the substitutionGroup declaration
        if (elementType == null && element.fSubGroup != null) {
            elementType = element.fSubGroup.fType;
        }

        if (elementType == null) {
            elementType = SchemaGrammar.fAnyType;
        }

        element.fType = elementType;

        // get 'identity constraint'

        // see if there's something here; it had better be key, keyref or unique.
        if (child != null) {
            String childName = DOMUtil.getLocalName(child);
            while (child != null &&
                   (childName.equals(SchemaSymbols.ELT_KEY) ||
                    childName.equals(SchemaSymbols.ELT_KEYREF) ||
                    childName.equals(SchemaSymbols.ELT_UNIQUE))) {

                if (childName.equals(SchemaSymbols.ELT_KEY) ||
                        childName.equals(SchemaSymbols.ELT_UNIQUE)) {
                    fSchemaHandler.fUniqueOrKeyTraverser.traverse(child, element, schemaDoc, grammar);
                    if(DOMUtil.getAttrValue(child, SchemaSymbols.ATT_NAME).length() != 0 ) {
                        fSchemaHandler.checkForDuplicateNames(
                            (schemaDoc.fTargetNamespace == null) ? ","+DOMUtil.getAttrValue(child, SchemaSymbols.ATT_NAME)
                            : schemaDoc.fTargetNamespace+","+ DOMUtil.getAttrValue(child, SchemaSymbols.ATT_NAME),
                            fSchemaHandler.getIDRegistry(),
                            child, schemaDoc);
                    }
                } else if (childName.equals(SchemaSymbols.ELT_KEYREF)) {
                    fSchemaHandler.storeKeyRef(child, schemaDoc, element);
                }
                child = DOMUtil.getNextSiblingElement(child);
                if (child != null) {
                    childName = DOMUtil.getLocalName(child);
                }
            }
        }

        // Step 2: register the element decl to the grammar
        if (nameAtt != null)
            grammar.addGlobalElementDecl(element);

        // Step 3: check against schema for schemas

        // required attributes
        if (nameAtt == null) {
            if (isGlobal)
                reportSchemaError("s4s-att-must-appear", new Object[]{NO_NAME, SchemaSymbols.ATT_NAME});
            else
                reportSchemaError("src-element.2.1", null);
            nameAtt = NO_NAME;
        }

        // element
        if (child != null) {
            reportSchemaError("s4s-elt-must-match", new Object[]{nameAtt, "(annotation?, (simpleType | complexType)?, (unique | key | keyref)*))"});
        }

        // Step 4: check 3.3.3 constraints

        // src-element

        // 1 default and fixed must not both be present.
        if (defaultAtt != null && fixedAtt != null) {
            reportSchemaError("src-element.1", new Object[]{nameAtt});
        }

        // 2 If the item's parent is not <schema>, then all of the following must be true:
        // 2.1 One of ref or name must be present, but not both.
        // This is checked in XSAttributeChecker

        // 2.2 If ref is present, then all of <complexType>, <simpleType>, <key>, <keyref>, <unique>, nillable, default, fixed, form, block and type must be absent, i.e. only minOccurs, maxOccurs, id are allowed in addition to ref, along with <annotation>.
        // Attributes are checked in XSAttributeChecker, elements are checked in "traverse" method

        // 3 type and either <simpleType> or <complexType> are mutually exclusive.
        if (haveAnonType && (typeAtt != null)) {
            reportSchemaError("src-element.3", new Object[]{nameAtt});
        }

        // Step 5: check 3.3.6 constraints
        // check for NOTATION type
        checkNotationType(nameAtt, elementType);

        // e-props-correct

        // 2 If there is a {value constraint}, the canonical lexical representation of its value must be ·valid· with respect to the {type definition} as defined in Element Default Valid (Immediate) (§3.3.6).
        if (element.fDefault != null) {
            if (!checkDefaultValid(element)) {
                reportSchemaError ("e-props-correct.2", new Object[]{nameAtt, element.fDefault});
            }
        }

        // 3 If there is an {substitution group affiliation}, the {type definition} of the element declaration must be validly derived from the {type definition} of the {substitution group affiliation}, given the value of the {substitution group exclusions} of the {substitution group affiliation}, as defined in Type Derivation OK (Complex) (§3.4.6) (if the {type definition} is complex) or as defined in Type Derivation OK (Simple) (§3.14.6) (if the {type definition} is simple).
        if (element.fSubGroup != null) {
           if (!XSConstraints.checkTypeDerivationOk(element.fType, element.fSubGroup.fType, element.fSubGroup.fFinal)) {
                reportSchemaError ("e-props-correct.3", new Object[]{nameAtt, subGroupAtt.prefix+":"+subGroupAtt.localpart});
           }
        }

        // 4 If the {type definition} or {type definition}'s {content type} is or is derived from ID then there must not be a {value constraint}.
        if (element.fDefault != null) {
            if (elementType instanceof IDDatatypeValidator ||
                elementType instanceof XSComplexTypeDecl &&
                ((XSComplexTypeDecl)elementType).containsTypeID()) {
                reportSchemaError ("e-props-correct.4", new Object[]{element.fName});
            }
        }

        // Step 6: add substitutionGroup information to the handler
        if (element.fSubGroup != null) {
            fSubGroupHandler.addSubstitutionGroup(element);
        }

        return element;
    }

    //private help functions

    // return whether the constraint value is valid for the given type
    boolean checkDefaultValid(XSElementDecl element) {

        DatatypeValidator dv = null;

        // e-props-correct
        // For a string to be a valid default with respect to a type definition the appropriate case among the following must be true:
        // 1 If the type definition is a simple type definition, then the string must be ·valid· with respect to that definition as defined by String Valid (§3.14.4).
        if (element.fType instanceof DatatypeValidator) {
            dv = (DatatypeValidator)element.fType;
        }

        // 2 If the type definition is a complex type definition, then all of the following must be true:
        else {
            // 2.1 its {content type} must be a simple type definition or mixed.
            XSComplexTypeDecl ctype = (XSComplexTypeDecl)element.fType;
            // 2.2 The appropriate case among the following must be true:
            // 2.2.1 If the {content type} is a simple type definition, then the string must be ·valid· with respect to that simple type definition as defined by String Valid (§3.14.4).
            if (ctype.fContentType == XSComplexTypeDecl.CONTENTTYPE_SIMPLE) {
                dv = ctype.fDatatypeValidator;
            }
            // 2.2.2 If the {content type} is mixed, then the {content type}'s particle must be ·emptiable· as defined by Particle Emptiable (§3.9.6).
            else if (ctype.fContentType == XSComplexTypeDecl.CONTENTTYPE_MIXED) {
                if (!ctype.fParticle.emptiable())
                    reportSchemaError ("cos-valid-default.2.2.2", new Object[]{element.fName});
            }
            else {
                reportSchemaError ("cos-valid-default.2.1", new Object[]{element.fName});
            }
        }

        // get the simple type declaration, and validate
        boolean ret = true;
        if (dv != null) {
            try {
                // REVISIT:  we'll be able to do this once he datatype redesign is implemented
                //element.fDefault = dv.validate((String)element.fDefault, null);
                dv.validate((String)element.fDefault, null);
            } catch (InvalidDatatypeValueException ide) {
                ret = false;
            }
        }

        return ret;
    }

    void reset(XMLErrorReporter reporter, SymbolTable symbolTable) {
        super.reset(reporter, symbolTable);
        fDeferTraversingLocalElements = true;
    } // reset()

}
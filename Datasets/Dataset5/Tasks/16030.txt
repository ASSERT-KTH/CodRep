if (strNameAttr != null) {

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

import org.apache.xerces.impl.xs.SchemaGrammar;
import org.apache.xerces.impl.xs.SchemaSymbols;
import org.apache.xerces.impl.xs.XSParticleDecl;
import org.apache.xerces.impl.xs.XSGroupDecl;
import org.apache.xerces.impl.xs.XSMessageFormatter;
import org.apache.xerces.util.DOMUtil;
import org.apache.xerces.impl.xs.util.XInt;
import org.apache.xerces.xni.QName;
import org.w3c.dom.Element;

/**
 * The model group schema component traverser.
 *
 * <group
 *   name = NCName>
 *   Content: (annotation?, (all | choice | sequence))
 * </group>
 *
 * @author Rahul Srivastava, Sun Microsystems Inc.
 * @author Elena Litani, IBM
 * @author Lisa Martin,  IBM
 * @version $Id$
 */
class  XSDGroupTraverser extends XSDAbstractParticleTraverser {

    XSDGroupTraverser (XSDHandler handler,
                       XSAttributeChecker gAttrCheck) {

        super(handler, gAttrCheck);
    }

    XSParticleDecl traverseLocal(Element elmNode,
                                 XSDocumentInfo schemaDoc,
                                 SchemaGrammar grammar) {

        // General Attribute Checking for elmNode declared locally
        Object[] attrValues = fAttrChecker.checkAttributes(elmNode, false,
                              schemaDoc);
        QName refAttr = (QName) attrValues[XSAttributeChecker.ATTIDX_REF];
        XInt  minAttr = (XInt)  attrValues[XSAttributeChecker.ATTIDX_MINOCCURS];
        XInt  maxAttr = (XInt)  attrValues[XSAttributeChecker.ATTIDX_MAXOCCURS];

        XSGroupDecl group = null;

        // ref should be here.
        if (refAttr == null) {
            reportSchemaError("s4s-att-must-appear", new Object[]{"group (local)", "ref"}, elmNode);
        } else {
            // get global decl
            // index is a particle index.
            group = (XSGroupDecl)fSchemaHandler.getGlobalDecl(schemaDoc, XSDHandler.GROUP_TYPE, refAttr, elmNode);
        }

        // no children are allowed
        if (DOMUtil.getFirstChildElement(elmNode) != null) {
            reportSchemaError("s4s-elt-must-match", new Object[]{"group (local)", "(annotation?)"}, elmNode);
        }

        int minOccurs = minAttr.intValue();
        int maxOccurs = maxAttr.intValue();

        XSParticleDecl particle = null;

        if (group != null) {
            // empty particle
            if (minOccurs == 0 && maxOccurs == 0) {
            } else if (minOccurs == 1 && maxOccurs == 1) {
                particle = group.fParticle;
            }
            else if (!( minOccurs == 1 && maxOccurs == 1)) {
                // if minOccurs==maxOccurs==1 we don't need to create new particle
                // create new particle in the grammar if minOccurs<maxOccurs
                particle = new XSParticleDecl();
                particle.fType = group.fParticle.fType;
                particle.fValue = group.fParticle;
                particle.fMinOccurs = minOccurs;
                particle.fMaxOccurs = maxOccurs;
            }
        }

        fAttrChecker.returnAttrArray(attrValues, schemaDoc);

        return particle;

    } // traverseLocal

    XSGroupDecl traverseGlobal(Element elmNode,
                               XSDocumentInfo schemaDoc,
                               SchemaGrammar grammar) {

        // General Attribute Checking for elmNode declared globally
        Object[] attrValues = fAttrChecker.checkAttributes(elmNode, true,
                              schemaDoc);
        String  strNameAttr = (String)  attrValues[XSAttributeChecker.ATTIDX_NAME];

        // must have a name
        if (strNameAttr == null) {
            reportSchemaError("s4s-att-must-appear", new Object[]{"group (global)", "name"}, elmNode);
        }

        XSGroupDecl group = null;
        XSParticleDecl particle = null;

        // must have at least one child
        Element l_elmChild = DOMUtil.getFirstChildElement(elmNode);
        if (l_elmChild == null) {
            reportSchemaError("s4s-elt-must-match", new Object[]{"group (global)", "(annotation?, (all | choice | sequence))"}, elmNode);
        } else {
            String childName = l_elmChild.getLocalName();
            if (childName.equals(SchemaSymbols.ELT_ANNOTATION)) {
                traverseAnnotationDecl(l_elmChild, attrValues, true, schemaDoc);
                l_elmChild = DOMUtil.getNextSiblingElement(l_elmChild);
                if (l_elmChild != null)
                    childName = l_elmChild.getLocalName();
            }

            if (l_elmChild == null) {
                reportSchemaError("s4s-elt-must-match", new Object[]{"group (global)", "(annotation?, (all | choice | sequence))"}, elmNode);
            } else if (childName.equals(SchemaSymbols.ELT_ALL)) {
                particle = traverseAll(l_elmChild, schemaDoc, grammar, CHILD_OF_GROUP);
            } else if (childName.equals(SchemaSymbols.ELT_CHOICE)) {
                particle = traverseChoice(l_elmChild, schemaDoc, grammar, CHILD_OF_GROUP);
            } else if (childName.equals(SchemaSymbols.ELT_SEQUENCE)) {
                particle = traverseSequence(l_elmChild, schemaDoc, grammar, CHILD_OF_GROUP);
            } else {
                Object[] args = new Object [] { "group", childName};
                reportSchemaError("GroupContentRestricted", args, l_elmChild);
            }

            if (l_elmChild != null &&
                DOMUtil.getNextSiblingElement(l_elmChild) != null) {
                Object[] args = new Object [] { "group", childName};
                reportSchemaError("GroupContentRestricted", args, l_elmChild);
            }

            // add global group declaration to the grammar
            if (particle != null && strNameAttr != null) {
                group = new XSGroupDecl();
                group.fName = strNameAttr;
                group.fTargetNamespace = schemaDoc.fTargetNamespace;
                group.fParticle = particle;
                grammar.addGlobalGroupDecl(group);
            }
        }
        if(group != null) { 
            // store groups redefined by restriction in the grammar so
            // that we can get at them at full-schema-checking time.
            Object redefinedGrp = fSchemaHandler.getGrpOrAttrGrpRedefinedByRestriction(XSDHandler.GROUP_TYPE,
                new QName(fSchemaHandler.EMPTY_STRING, strNameAttr, strNameAttr, schemaDoc.fTargetNamespace),
                schemaDoc, elmNode);
            if(redefinedGrp != null) {
                // store in grammar
                grammar.addRedefinedGroupDecl(group, (XSGroupDecl)redefinedGrp);
            }
        }

        fAttrChecker.returnAttrArray(attrValues, schemaDoc);

        return group;

    } // traverseGlobal
}
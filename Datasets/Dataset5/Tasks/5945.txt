reportSchemaError("PublicSystemOnNotation", null, elmNode);

/*
 * Copyright 2001-2004 The Apache Software Foundation.
 * 
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * 
 *      http://www.apache.org/licenses/LICENSE-2.0
 * 
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package org.apache.xerces.impl.xs.traversers;

import org.apache.xerces.impl.xs.SchemaGrammar;
import org.apache.xerces.impl.xs.SchemaSymbols;
import org.apache.xerces.impl.xs.XSAnnotationImpl;
import org.apache.xerces.impl.xs.XSNotationDecl;
import org.apache.xerces.util.DOMUtil;
import org.w3c.dom.Element;

/**
 * The notation declaration schema component traverser.
 *
 * <notation
 *   id = ID
 *   name = NCName
 *   public = anyURI
 *   system = anyURI
 *   {any attributes with non-schema namespace . . .}>
 *   Content: (annotation?)
 * </notation>
 *
 * @author Rahul Srivastava, Sun Microsystems Inc.
 * @author Elena Litani, IBM
 * @version $Id$
 */
class  XSDNotationTraverser extends XSDAbstractTraverser {

    XSDNotationTraverser (XSDHandler handler,
                          XSAttributeChecker gAttrCheck) {
        super(handler, gAttrCheck);
    }

    XSNotationDecl traverse(Element elmNode,
                            XSDocumentInfo schemaDoc,
                            SchemaGrammar grammar) {

        // General Attribute Checking for elmNode
        Object[] attrValues = fAttrChecker.checkAttributes(elmNode, true, schemaDoc);
        //get attributes
        String  nameAttr   = (String) attrValues[XSAttributeChecker.ATTIDX_NAME];

        String  publicAttr = (String) attrValues[XSAttributeChecker.ATTIDX_PUBLIC];
        String  systemAttr = (String) attrValues[XSAttributeChecker.ATTIDX_SYSTEM];
        if (nameAttr == null) {
            reportSchemaError("s4s-att-must-appear", new Object[]{SchemaSymbols.ELT_NOTATION, SchemaSymbols.ATT_NAME}, elmNode);
            fAttrChecker.returnAttrArray(attrValues, schemaDoc);
            return null;
        }
		
		if (systemAttr == null && publicAttr == null)
			reportSchemaError("s4s-att-must-appear", new Object[]{SchemaSymbols.ELT_NOTATION, "system or public"}, elmNode);

        XSNotationDecl notation = new XSNotationDecl();
        notation.fName = nameAttr;
        notation.fTargetNamespace = schemaDoc.fTargetNamespace;
        notation.fPublicId = publicAttr;
        notation.fSystemId = systemAttr;

        //check content
        Element content = DOMUtil.getFirstChildElement(elmNode);
        XSAnnotationImpl annotation = null;

        if (content != null) {
            // traverse annotation if any
            if (DOMUtil.getLocalName(content).equals(SchemaSymbols.ELT_ANNOTATION)) {
                annotation = traverseAnnotationDecl(content, attrValues, false, schemaDoc);
                content = DOMUtil.getNextSiblingElement(content);
            }
        }
        notation.fAnnotation = annotation;
        if (content!=null){
             Object[] args = new Object [] {SchemaSymbols.ELT_NOTATION, "(annotation?)", DOMUtil.getLocalName(content)};
             reportSchemaError("s4s-elt-must-match.1", args, content);

        }
        grammar.addGlobalNotationDecl(notation);
        fAttrChecker.returnAttrArray(attrValues, schemaDoc);

        return notation;
    }
}
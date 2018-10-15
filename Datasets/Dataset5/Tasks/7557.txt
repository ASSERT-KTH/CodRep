while (node != null && (node != DOMUtil.getRoot(DOMUtil.getDocument(node)))) {

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
import org.apache.xerces.xni.QName;
import org.w3c.dom.Element;

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


    private class ComplexTypeRecoverableError extends Exception {
      ComplexTypeRecoverableError() {super();}
      ComplexTypeRecoverableError(String s) {super(s);}
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
                        SchemaGrammar grammar){

        Object[] attrValues = fAttrChecker.checkAttributes(complexTypeNode, true,
                              schemaDoc);
        String complexTypeName = (String)  attrValues[XSAttributeChecker.ATTIDX_NAME];
        XSComplexTypeDecl type = traverseComplexTypeDecl (complexTypeNode,
                                 complexTypeName, attrValues, schemaDoc, grammar);
        grammar.addGlobalTypeDecl(type);
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
            child = checkContent(complexTypeDecl,
                    DOMUtil.getFirstChildElement(complexTypeDecl), true);

            // ---------------------------------------------------------------
            // Process the content of the complex type definition
            // ---------------------------------------------------------------
            if (child==null) {
              //
              // EMPTY complexType with complexContent
              //
              processComplexContent(child, complexType, null, mixedAtt.booleanValue(),
                                    schemaDoc, grammar);
            }
            else if (DOMUtil.getLocalName(child).equals
                    (SchemaSymbols.ELT_SIMPLECONTENT)) {
              //
              // SIMPLE CONTENT - to be done
              //
            }
            else if (DOMUtil.getLocalName(child).equals
                    (SchemaSymbols.ELT_COMPLEXCONTENT)) {
              //
              // EXPLICIT COMPLEX CONTENT - to be done
              //
            }
            else {
              //
              // We must have ....
              // GROUP, ALL, SEQUENCE or CHOICE, followed by optional attributes
              // Note that it's possible that only attributes are specified.
              //
              processComplexContent(child, complexType, null, mixedAtt.booleanValue(),
                                    schemaDoc, grammar);
            }
       }
       catch (ComplexTypeRecoverableError e) {
         String message = e.getMessage();
         System.out.println(message);
         //handleComplexTypeError(message,typeNameIndex,typeInfo);
       }

       return complexType;


    }

    private void processComplexContent(Element complexContentChild,
                                 XSComplexTypeDecl typeInfo, QName baseName,
                                 boolean isMixed,
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


          String childName = complexContentChild.getLocalName();

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
           else if (isAttrOrAttrGroup(complexContentChild)) {
               attrNode = complexContentChild;
           }
           else {
               throw new ComplexTypeRecoverableError(
                "Invalid child '"+ childName +"' in the complex type");
           }
       }

       typeInfo.fParticle = particle;

       // -----------------------------------------------------------------------
       // Merge in information from base, if it exists - TO BE DONE
       // -----------------------------------------------------------------------

       // -----------------------------------------------------------------------
       // Set the content type
       // -----------------------------------------------------------------------

       if (isMixed) {

           // if there are no children, detect an error
           // See the definition of content type in Structures 3.4.1
           // This is commented out for now, until I get a clarification from schema WG
           // LM.

           if (typeInfo.fParticle == null) {
             //throw new ComplexTypeRecoverableError("Type '" + typeName + "': The content of a mixed complexType must not be empty");

             // for "mixed" complex type with empty content
             // we add an optional leaf node to the content model
             // with empty namespace and -1 name (which won't match any element)
             // so that the result content model is emptible and only match
             // with cdata

             // TO BE DONE

           }

           else
             typeInfo.fContentType = XSComplexTypeDecl.CONTENTTYPE_MIXED;
       }
       else if (typeInfo.fParticle == null)
           typeInfo.fContentType = XSComplexTypeDecl.CONTENTTYPE_EMPTY;
       else
           typeInfo.fContentType = XSComplexTypeDecl.CONTENTTYPE_ELEMENT;


       // -------------------------------------------------------------
       // REVISIT - to we need to add a template element for the type?
       // -------------------------------------------------------------

       // -------------------------------------------------------------
       // Now, check attributes and handle - TO BE DONE
       // -------------------------------------------------------------


    } // end processComplexContent


    private boolean isAttrOrAttrGroup(Element child) {
       // REVISIT - TO BE DONE
       return false;
    }

    private void traverseSimpleContentDecl(Element simpleContentDecl,
                                           XSComplexTypeDecl typeInfo) {
    }

    private void traverseComplexContentDecl(Element complexContentDecl,
                                            XSComplexTypeDecl typeInfo,
                                            boolean mixedOnComplexTypeDecl){
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
        while (node != null) {
          typeName = typeName+node.getAttribute(SchemaSymbols.ATT_NAME);
          node = DOMUtil.getParent(node);
        }
        return typeName;
    }


    // HELP FUNCTIONS:
    //
    // 1. processAttributes
    // 2. processBasetTypeInfo
    // 3. AWildCardIntersection
    // 4. parseBlockSet - should be here or in SchemaHandler??
    // 5. parseFinalSet - also used by traverseSimpleType, thus should be in SchemaHandler
    // 6. handleComplexTypeError
    // and more...

/*
    REVISIT: something done in AttriubteTraverser in Xerces1. Should be done
             here in complexTypeTraverser.

        // add attribute to attr decl pool in fSchemaGrammar,
        if (typeInfo != null) {

            // check that there aren't duplicate attributes
            int temp = fSchemaGrammar.getAttributeDeclIndex(typeInfo.templateElementIndex, attQName);
            if (temp > -1) {
              reportGenericSchemaError("ct-props-correct.4:  Duplicate attribute " +
              fStringPool.toString(attQName.rawname) + " in type definition");
            }

            // check that there aren't multiple attributes with type derived from ID
            if (dvIsDerivedFromID) {
               if (typeInfo.containsAttrTypeID())  {
                 reportGenericSchemaError("ct-props-correct.5: More than one attribute derived from type ID cannot appear in the same complex type definition.");
               }
               typeInfo.setContainsAttrTypeID();
            }
            fSchemaGrammar.addAttDeDecl(typeInfo.templateElementIndex,
                                        attQName, attType,
                                        dataTypeSymbol, attValueAndUseType,
                                        fStringPool.toString( attValueConstraint), dv, attIsList);
        }
*/
}
String contentType[] = {"EMPTY", "SIMPLE", "ELEMENT", "MIXED"};

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

package org.apache.xerces.impl.xs;

import org.apache.xerces.impl.dv.XSSimpleType;
import org.apache.xerces.impl.xs.psvi.*;
import org.apache.xerces.impl.xs.models.XSCMValidator;
import org.apache.xerces.impl.xs.models.CMBuilder;

/**
 * The XML representation for a complexType
 * schema component is a <complexType> element information item
 *
 * @author Elena Litani, IBM
 * @author Sandy Gao, IBM
 * @version $Id$
 */
public class XSComplexTypeDecl implements XSTypeDecl, XSComplexTypeDefinition {

    // name of the complexType
    String fName = null;

    // target namespace of the complexType
    String fTargetNamespace = null;

    // base type of the complexType
    XSTypeDecl fBaseType = null;

    // derivation method of the complexType
    short fDerivedBy = XSConstants.DERIVATION_RESTRICTION;

    // final set of the complexType
    short fFinal = XSConstants.DERIVATION_NONE;

    // block set (prohibited substitution) of the complexType
    short fBlock = XSConstants.DERIVATION_NONE;

    // flags: whether is abstract; whether contains ID type;
    //        whether it's an anonymous tpye
    short fMiscFlags = 0;

    // the attribute group that holds the attribute uses and attribute wildcard
    XSAttributeGroupDecl fAttrGrp = null;

    // the content type of the complexType
    short fContentType = CONTENTTYPE_EMPTY;

    // if the content type is simple, then the corresponding simpleType
    XSSimpleType fXSSimpleType = null;

    // if the content type is element or mixed, the particle
    XSParticleDecl fParticle = null;

    // if there is a particle, the content model corresponding to that particle
    XSCMValidator fCMValidator = null;

    public XSComplexTypeDecl() {
        // do-nothing constructor for now.
    }

    public void setValues(String name, String targetNamespace,
            XSTypeDecl baseType, short derivedBy, short schemaFinal, 
            short block, short contentType,
            boolean isAbstract, XSAttributeGroupDecl attrGrp, 
            XSSimpleType simpleType, XSParticleDecl particle) {
        fTargetNamespace = targetNamespace;
        fBaseType = baseType;
        fDerivedBy = derivedBy;
        fFinal = schemaFinal;
        fBlock = block;
        fContentType = contentType;
        if(isAbstract)
            fMiscFlags |= CT_IS_ABSTRACT;
        fAttrGrp = attrGrp;
        fXSSimpleType = simpleType;
        fParticle = particle;
   }

   public void setName(String name) {
        fName = name;
   }

    public short getTypeCategory() {
        return COMPLEX_TYPE;
    }

    public String getTypeName() {
        return fName;
    }

    public short getFinalSet(){
        return fFinal;
    }

    public String getTargetNamespace(){
        return fTargetNamespace;
    }

    // flags for the misc flag
    private static final short CT_IS_ABSTRACT = 1;
    private static final short CT_HAS_TYPE_ID = 2;
    private static final short CT_IS_ANONYMOUS = 4;

    // methods to get/set misc flag

    public boolean containsTypeID () {
        return((fMiscFlags & CT_HAS_TYPE_ID) != 0);
    }

    public void setIsAbstractType() {
        fMiscFlags |= CT_IS_ABSTRACT;
    }
    public void setContainsTypeID() {
        fMiscFlags |= CT_HAS_TYPE_ID;
    }
    public void setIsAnonymous() {
        fMiscFlags |= CT_IS_ANONYMOUS;
    }

    public synchronized XSCMValidator getContentModel(CMBuilder cmBuilder) {
        if (fCMValidator == null)
            fCMValidator = cmBuilder.getContentModel(this);

        return fCMValidator;
    }

    // some utility methods:

    // return the attribute group for this complex type
    public XSAttributeGroupDecl getAttrGrp() {
        return fAttrGrp;
    }

    public String toString() {
        StringBuffer str = new StringBuffer();
        appendTypeInfo(str);
        return str.toString();
    }

    void appendTypeInfo(StringBuffer str) {
        String contentType[] = {"EMPTY", "SIMPLE", "MIXED", "ELEMENT"};
        String derivedBy[] = {"EMPTY", "EXTENSION", "RESTRICTION"};

        str.append("Complex type name='" + fTargetNamespace + "," + getTypeName() + "', ");
        if (fBaseType != null)
            str.append(" base type name='" + fBaseType.getName() + "', ");

        str.append(" content type='" + contentType[fContentType] + "', ");
        str.append(" isAbstract='" + getIsAbstract() + "', ");
        str.append(" hasTypeId='" + containsTypeID() + "', ");
        str.append(" final='" + fFinal + "', ");
        str.append(" block='" + fBlock + "', ");
        if (fParticle != null)
            str.append(" particle='" + fParticle.toString() + "', ");
        str.append(" derivedBy='" + derivedBy[fDerivedBy] + "'. ");

    }

    public boolean derivedFrom(XSTypeDefinition ancestor) {
        // ancestor is null, retur false
        if (ancestor == null)
            return false;
        // ancestor is anyType, return true
        if (ancestor == SchemaGrammar.fAnyType)
            return true;
        // recursively get base, and compare it with ancestor
        XSTypeDefinition type = this;
        while (type != ancestor &&                      // compare with ancestor
               type != SchemaGrammar.fAnySimpleType &&  // reached anySimpleType
               type != SchemaGrammar.fAnyType) {        // reached anyType
            type = type.getBaseType();
        }

        return type == ancestor;
    }

    public boolean derivedFrom(String ancestorNS, String ancestorName) {
        // ancestor is null, retur false
        if (ancestorName == null)
            return false;
        // ancestor is anyType, return true
        if (ancestorNS != null &&
            ancestorNS.equals(SchemaSymbols.URI_SCHEMAFORSCHEMA) &&
            ancestorName.equals(SchemaSymbols.ATTVAL_ANYTYPE)) {
            return true;
        }

        // recursively get base, and compare it with ancestor
        XSTypeDecl type = this;
        while (!(ancestorName.equals(type.getName()) &&
                 ((ancestorNS == null && type.getNamespace() == null) ||
                  (ancestorNS != null && ancestorNS.equals(type.getNamespace())))) &&   // compare with ancestor
               type != SchemaGrammar.fAnySimpleType &&  // reached anySimpleType
               type != SchemaGrammar.fAnyType) {        // reached anyType
            type = (XSTypeDecl)type.getBaseType();
        }

        return type != SchemaGrammar.fAnySimpleType &&
        type != SchemaGrammar.fAnyType;
    }

    public void reset(){
        fName = null;
        fTargetNamespace = null;
        fBaseType = null;
        fDerivedBy = XSConstants.DERIVATION_RESTRICTION;
        fFinal = XSConstants.DERIVATION_NONE;
        fBlock = XSConstants.DERIVATION_NONE;

        fMiscFlags = 0;

        // reset attribute group
        fAttrGrp.reset();
        fContentType = CONTENTTYPE_EMPTY;
        fXSSimpleType = null;
        fParticle = null;
        fCMValidator = null;
    }

    /**
     * Get the type of the object, i.e ELEMENT_DECLARATION.
     */
    public short getType() {
        return XSConstants.TYPE_DEFINITION;
    }

    /**
     * The <code>name</code> of this <code>XSObject</code> depending on the
     * <code>XSObject</code> type.
     */
    public String getName() {
        return getIsAnonymous() ? null : fName;
    }

    /**
     * A boolean that specifies if the type definition is anonymous.
     * Convenience attribute. This is a field is not part of
     * XML Schema component model.
     */
    public boolean getIsAnonymous() {
        return((fMiscFlags & CT_IS_ANONYMOUS) != 0);
    }

    /**
     * The namespace URI of this node, or <code>null</code> if it is
     * unspecified.  defines how a namespace URI is attached to schema
     * components.
     */
    public String getNamespace() {
        return fTargetNamespace;
    }

    /**
     * {base type definition} Either a simple type definition or a complex
     * type definition.
     */
    public XSTypeDefinition getBaseType() {
        return fBaseType;
    }

    /**
     * {derivation method} Either extension or restriction. The valid constant
     * value for this <code>XSConstants</code> EXTENTION, RESTRICTION.
     */
    public short getDerivationMethod() {
        return fDerivedBy;
    }

    /**
     * {final} For complex type definition it is a subset of {extension,
     * restriction}. For simple type definition it is a subset of
     * {extension, list, restriction, union}.
     * @param derivation  Extension, restriction, list, union constants
     *   (defined in <code>XSConstants</code>).
     * @return True if derivation is in the final set, otherwise false.
     */
    public boolean getIsFinal(short derivation) {
        return (fFinal & derivation) != 0;
    }

    /**
     * {final} For complex type definition it is a subset of {extension, restriction}.
     *
     * @return A bit flag that represents:
     *         {extension, restriction) or none for complexTypes;
     *         {extension, list, restriction, union} or none for simpleTypes;
     */
    public short getFinal() {
        return fFinal;
    }

    /**
     * {abstract} A boolean. Complex types for which {abstract} is true must
     * not be used as the {type definition} for the validation of element
     * information items.
     */
    public boolean getIsAbstract() {
        return((fMiscFlags & CT_IS_ABSTRACT) != 0);
    }

    /**
     *  {attribute uses} A set of attribute uses.
     */
    public XSObjectList getAttributeUses() {
        return fAttrGrp.getAttributeUses();
    }

    /**
     * {attribute wildcard} Optional. A wildcard.
     */
    public XSWildcard getAttributeWildcard() {
        return fAttrGrp.getAttributeWildcard();
    }

    /**
     * {content type} One of empty, a simple type definition (see
     * <code>simpleType</code>, or mixed, element-only (see
     * <code>cmParticle</code>).
     */
    public short getContentType() {
        return fContentType;
    }

    /**
     * A simple type definition corresponding to simple content model,
     * otherwise <code>null</code>
     */
    public XSSimpleTypeDefinition getSimpleType() {
        return fXSSimpleType;
    }

    /**
     * A particle for mixed or element-only content model, otherwise
     * <code>null</code>
     */
    public XSParticle getParticle() {
        return fParticle;
    }

    /**
     * {prohibited substitutions} A subset of {extension, restriction}.
     * @param prohibited  extention or restriction constants (defined in
     *   <code>XSConstants</code>).
     * @return True if prohibited is a prohibited substitution, otherwise
     *   false.
     */
    public boolean getIsProhibitedSubstitution(short prohibited) {
        return (fBlock & prohibited) != 0;
    }

    /**
     * {prohibited substitutions}
     *
     * @return A bit flag corresponding to prohibited substitutions
     */
    public short getProhibitedSubstitutions() {
        return fBlock;
    }

    /**
     * Optional. Annotation.
     */
    public XSObjectList getAnnotations() {
        // REVISIT: SCAPI: to implement
        return null;
    }
    
} // class XSComplexTypeDecl
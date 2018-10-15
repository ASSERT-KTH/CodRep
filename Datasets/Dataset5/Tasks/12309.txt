fRedefinedGroupDecls = resize(fRedefinedGroupDecls, fRGCount << 1);

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

package org.apache.xerces.impl.xs; 

import org.apache.xerces.impl.dv.SchemaDVFactory;
import org.apache.xerces.impl.dv.XSSimpleType;
import org.apache.xerces.impl.xs.identity.IdentityConstraint;
import org.apache.xerces.util.SymbolTable;
import org.apache.xerces.util.SymbolHash;

import org.apache.xerces.impl.validation.Grammar;

import java.util.Hashtable;

/**
 * This class is to hold all schema component declaration that are declared
 * within one namespace.
 *
 * The Grammar class this class extends contains what little
 * commonality there is between XML Schema and DTD grammars.  It's
 * useful to distinguish grammar objects from other kinds of object
 * when they exist in pools or caches.
 *
 * @author Sandy Gao, IBM
 * @author Elena Litani, IBM
 *
 * @version $Id$
 */

public class SchemaGrammar  extends Grammar {

    /** Symbol table. */
    private SymbolTable fSymbolTable;

    // the target namespace of grammar
    public String fTargetNamespace;

    // global decls: map from decl name to decl object
    SymbolHash fGlobalAttrDecls;
    SymbolHash fGlobalAttrGrpDecls;
    SymbolHash fGlobalElemDecls;
    SymbolHash fGlobalGroupDecls;
    SymbolHash fGlobalNotationDecls;
    SymbolHash fGlobalIDConstraintDecls;
    //REVISIT: still need to decide on it.
    Hashtable fGlobalTypeDecls;

    //
    // Constructors
    //

    /**
     * Default constructor.
     *
     * @param symbolTable
     * @param targetNamespace
     */
    public SchemaGrammar(SymbolTable symbolTable, String targetNamespace) {
        fSymbolTable = symbolTable;
        fTargetNamespace = targetNamespace;

        // REVISIT: do we know the numbers of the following global decls
        // when creating this grammar? If so, we can pass the numbers in,
        // and use that number to initialize the following hashtables.
        fGlobalAttrDecls  = new SymbolHash();
        fGlobalAttrGrpDecls = new SymbolHash();
        fGlobalElemDecls = new SymbolHash();
        fGlobalGroupDecls = new SymbolHash();
        fGlobalNotationDecls = new SymbolHash();
        fGlobalTypeDecls = new Hashtable();
        fGlobalIDConstraintDecls = new SymbolHash();
    } // <init>(SymbolTable, String)

    // number of built-in XSTypes we need to create for base and full
    // datatype set
    private static final int BASICSET_COUNT = 29;
    private static final int FULLSET_COUNT  = 46;

    /**
     * Special constructor to create the grammar for the schema namespace
     *
     * @param symbolTable
     * @param fullSet
     */
    protected SchemaGrammar(SymbolTable symbolTable) {
        fSymbolTable = symbolTable;
        fTargetNamespace = SchemaSymbols.URI_SCHEMAFORSCHEMA;

        fGlobalAttrDecls  = new SymbolHash(1);
        fGlobalAttrGrpDecls = new SymbolHash(1);
        fGlobalElemDecls = new SymbolHash(1);
        fGlobalGroupDecls = new SymbolHash(1);
        fGlobalNotationDecls = new SymbolHash(1);
        fGlobalIDConstraintDecls = new SymbolHash(1);

        SchemaDVFactory schemaFactory = SchemaDVFactory.getInstance();
        fGlobalTypeDecls = schemaFactory.getBuiltInTypes();
        addGlobalTypeDecl(fAnyType);

    } // <init>(SymbolTable, boolean)

    // DTDGrammar methods
    public boolean isNamespaceAware () {
        return true;
    } // isNamespaceAware():boolean

    /**
     * Returns this grammar's target namespace.
     */
    public final String getTargetNamespace() {
        return fTargetNamespace;
    } // getTargetNamespace():String

    /**
     * register one global attribute
     */
    public final void addGlobalAttributeDecl(XSAttributeDecl decl) {
        fGlobalAttrDecls.put(decl.fName, decl);
    }

    /**
     * register one global attribute group
     */
    public final void addGlobalAttributeGroupDecl(XSAttributeGroupDecl decl) {
        fGlobalAttrGrpDecls.put(decl.fName, decl);
    }

    /**
     * register one global element
     */
    public final void addGlobalElementDecl(XSElementDecl decl) {
        fGlobalElemDecls.put(decl.fName, decl);

        // if there is a substitution group affiliation, store in an array,
        // for further constraint checking: UPA, PD, EDC
        if (decl.fSubGroup != null) {
            if (fSubGroupCount == fSubGroups.length)
                fSubGroups = resize(fSubGroups, fSubGroupCount+INC_SIZE);
            fSubGroups[fSubGroupCount++] = decl;
        }
    }

    /**
     * register one global group
     */
    public final void addGlobalGroupDecl(XSGroupDecl decl) {
        fGlobalGroupDecls.put(decl.fName, decl);
    }

    /**
     * register one global notation
     */
    public final void addGlobalNotationDecl(XSNotationDecl decl) {
        fGlobalNotationDecls.put(decl.fName, decl);
    }

    /**
     * register one global type
     */
    public final void addGlobalTypeDecl(XSTypeDecl decl) {
        fGlobalTypeDecls.put(decl.getTypeName(), decl);
    }

    /**
     * register one identity constraint
     */
    public final void addIDConstraintDecl(XSElementDecl elmDecl, IdentityConstraint decl) {
        elmDecl.addIDConstaint(decl);
        fGlobalIDConstraintDecls.put(decl.getIdentityConstraintName(), decl);
    }

    /**
     * get one global attribute
     */
    public final XSAttributeDecl getGlobalAttributeDecl(String declName) {
        return(XSAttributeDecl)fGlobalAttrDecls.get(declName);
    }

    /**
     * get one global attribute group
     */
    public final XSAttributeGroupDecl getGlobalAttributeGroupDecl(String declName) {
        return(XSAttributeGroupDecl)fGlobalAttrGrpDecls.get(declName);
    }

    /**
     * get one global element
     */
    public final XSElementDecl getGlobalElementDecl(String declName) {
        return(XSElementDecl)fGlobalElemDecls.get(declName);
    }

    /**
     * get one global group
     */
    public final XSGroupDecl getGlobalGroupDecl(String declName) {
        return(XSGroupDecl)fGlobalGroupDecls.get(declName);
    }

    /**
     * get one global notation
     */
    public final XSNotationDecl getNotationDecl(String declName) {
        return(XSNotationDecl)fGlobalNotationDecls.get(declName);
    }

    /**
     * get one global type
     */
    public final XSTypeDecl getGlobalTypeDecl(String declName) {
        return(XSTypeDecl)fGlobalTypeDecls.get(declName);
    }

    /**
     * get one identity constraint
     */
    public final IdentityConstraint getIDConstraintDecl(String declName) {
        return(IdentityConstraint)fGlobalIDConstraintDecls.get(declName);
    }

    // array to store complex type decls
    private static final int INITIAL_SIZE = 16;
    private static final int INC_SIZE     = 16;

    private int fCTCount = 0;
    private XSComplexTypeDecl[] fComplexTypeDecls = new XSComplexTypeDecl[INITIAL_SIZE];

    // an array to store groups being redefined by restriction
    // even-numbered elements are the derived groups, odd-numbered ones their bases
    private static final int REDEFINED_GROUP_INIT_SIZE = 2; 
    private int fRGCount = 0;
    private XSGroupDecl[] fRedefinedGroupDecls = new XSGroupDecl[REDEFINED_GROUP_INIT_SIZE];

    // a flag to indicate whether we have checked the 3 constraints on this
    // grammar.
    boolean fFullChecked = false;

    /**
     * add one complex type decl: for later constraint checking
     */
    public final void addComplexTypeDecl(XSComplexTypeDecl decl) {
        if (fCTCount == fComplexTypeDecls.length)
            fComplexTypeDecls = resize(fComplexTypeDecls, fCTCount+INC_SIZE);
        fComplexTypeDecls[fCTCount++] = decl;
    }

    /**
     * add a group redefined by restriction: for later constraint checking
     */
    public final void addRedefinedGroupDecl(XSGroupDecl derived, XSGroupDecl base) {
        if (fRGCount == fRedefinedGroupDecls.length)
            // double array size each time.
            fRedefinedGroupDecls = resize(fRedefinedGroupDecls, fRGCount << 2);
        fRedefinedGroupDecls[fRGCount++] = derived;
        fRedefinedGroupDecls[fRGCount++] = base;
    }

    /**
     * get all complex type decls: for later constraint checking
     */
    final XSComplexTypeDecl[] getUncheckedComplexTypeDecls() {
        if (fCTCount < fComplexTypeDecls.length)
            fComplexTypeDecls = resize(fComplexTypeDecls, fCTCount);
        return fComplexTypeDecls;
    }

    /**
     * get all redefined groups: for later constraint checking
     */
    final XSGroupDecl[] getRedefinedGroupDecls() {
        if (fRGCount < fRedefinedGroupDecls.length)
            fRedefinedGroupDecls = resize(fRedefinedGroupDecls, fRGCount);
        return fRedefinedGroupDecls;
    }


    /**
     * after the first-round checking, some types don't need to be checked
     * against UPA again. here we trim the array to the proper size.
     */
    final void setUncheckedTypeNum(int newSize) {
        fCTCount = newSize;
        fComplexTypeDecls = resize(fComplexTypeDecls, fCTCount);
    }

    // used to store all substitution group information declared in
    // this namespace
    private int fSubGroupCount = 0;
    private XSElementDecl[] fSubGroups = new XSElementDecl[INITIAL_SIZE];

    /**
     * get all substitution group information: for the 3 constraint checking
     */
    final XSElementDecl[] getSubstitutionGroups() {
        if (fSubGroupCount < fSubGroups.length)
            fSubGroups = resize(fSubGroups, fSubGroupCount);
        return fSubGroups;
    }

    // anyType and anySimpleType: because there are so many places where
    // we need direct access to these two types
    public final static XSComplexTypeDecl fAnyType;
    static {
        fAnyType = new XSComplexTypeDecl();
        fAnyType.fName = SchemaSymbols.ATTVAL_ANYTYPE;
        fAnyType.fTargetNamespace = SchemaSymbols.URI_SCHEMAFORSCHEMA;
        fAnyType.fBaseType = fAnyType;
        fAnyType.fDerivedBy = SchemaSymbols.RESTRICTION;
        fAnyType.fContentType = XSComplexTypeDecl.CONTENTTYPE_MIXED;
        XSWildcardDecl wildcard = new XSWildcardDecl();
        XSParticleDecl particle = new XSParticleDecl();
        particle.fMinOccurs = 0;
        particle.fMaxOccurs = SchemaSymbols.OCCURRENCE_UNBOUNDED;
        particle.fType = XSParticleDecl.PARTICLE_WILDCARD;
        particle.fValue = wildcard;
        fAnyType.fParticle = particle;
        fAnyType.fAttrGrp.fAttributeWC = wildcard;
    }

    // the grammars to hold built-in types
    public final static SchemaGrammar SG_SchemaNS = new SchemaGrammar(null);

    public final static XSSimpleType fAnySimpleType = (XSSimpleType)SG_SchemaNS.getGlobalTypeDecl(SchemaSymbols.ATTVAL_ANYSIMPLETYPE);

    static final XSComplexTypeDecl[] resize(XSComplexTypeDecl[] oldArray, int newSize) {
        XSComplexTypeDecl[] newArray = new XSComplexTypeDecl[newSize];
        System.arraycopy(oldArray, 0, newArray, 0, Math.min(oldArray.length, newSize));
        return newArray;
    }

    static final XSGroupDecl[] resize(XSGroupDecl[] oldArray, int newSize) {
        XSGroupDecl[] newArray = new XSGroupDecl[newSize];
        System.arraycopy(oldArray, 0, newArray, 0, Math.min(oldArray.length, newSize));
        return newArray;
    }

    static final XSElementDecl[] resize(XSElementDecl[] oldArray, int newSize) {
        XSElementDecl[] newArray = new XSElementDecl[newSize];
        System.arraycopy(oldArray, 0, newArray, 0, Math.min(oldArray.length, newSize));
        return newArray;
    }

} // class SchemaGrammar
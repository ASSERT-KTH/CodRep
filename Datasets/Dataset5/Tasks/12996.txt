public static final short FIXED    = 4;

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

import java.util.Vector;
import org.apache.xerces.xni.QName;


/**
 * The XML representation for an element declaration schema component is an <element> element information item
 * @version $Id$
 */
public class XSElementDecl {

    
    // REVISIT: should element decl have contentSpec information
    // like EMPTY/MIXED, CHILDREN etc..?
    // This information will be accessable via type info object..
    //
    public static final short NILLABLE = 1;
    public static final short ABSTRACT = 2;
    public static final short FIXED    = 3;

    public final QName fQName = new QName();

    // index to the type registry: simpleType or complexType
    public int fXSTypeDecl;

    // nillable/abstract/final
    public short fElementMiscFlags;

    public String fBlock;
    public String fFinal;
    public String fDefault;

    // REVISIT: should we store Substitution group names?
    //
    public String fSubstitutionGroupName;

    // REVISIT: should we expose more type information:
    // datatypeValidators or contentSpecIndex
    // 

    // REVISIT: should we expose specified or it can wait till PSVI?
    // false if element value was provided by the schema
    // true otherwise
    
    // identity constraints

    public final Vector fUnique = new Vector();

    public final Vector fKey = new Vector();

    public final Vector fKeyRef = new Vector();


    
    //
    // Constructors
    //

    public XSElementDecl() {
        clear();
    }

    public XSElementDecl(XSElementDecl elementDecl) {
        setValues(elementDecl);
    }

    //
    // Public methods
    //

    public void clear() {
        fQName.clear();
        fXSTypeDecl = - 1;
        fUnique.removeAllElements();
        fKey.removeAllElements();
        fKeyRef.removeAllElements();
    }

    public void setValues(XSElementDecl elementDecl) {
        fQName.setValues(elementDecl.fQName);
        fXSTypeDecl = elementDecl.fXSTypeDecl;
        copyIdentityConstraints(elementDecl.fUnique,elementDecl.fKey, elementDecl.fKeyRef);
    }


    public void copyIdentityConstraints (Vector unique, Vector key, Vector keyRef){
        //REVISIT: IMPLEMENT!
    }

} // class XMLElementDecl
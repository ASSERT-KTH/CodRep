public int fParticleIndex = -1;


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

import org.apache.xerces.impl.v2.datatypes.DatatypeValidator;

/**
 * 
 * @version $Id$
 */
public class XSComplexTypeDecl implements XSType {


    private static final short CT_IS_ABSTRACT=1;
    private static final short CT_CONTAINS_ATTR_TYPE_ID=2;
    private static final short CT_DECL_SEEN=3;    // indicates that the declaration was
    // traversed as opposed to processed due
    // to a forward reference

    public String fTypeName;

    public DatatypeValidator fBaseDTValidator;
    public XSComplexTypeDecl fBaseCTInfo;

    public int fDerivedBy = 0;
    public String fBlockSet;
    public String fFinalSet;

    public short fMiscFlags=0;

    public int fContentType;
    public int fContentSpecHandle = -1;
    public int fTemplateElmIndex = -1;
    public int fAttlistHead = -1;
    public DatatypeValidator fDatatypeValidator;

    public short getXSType () {
        return COMPLEX_TYPE;
    }
    public boolean isAbstractType() {
        return((fMiscFlags & CT_IS_ABSTRACT)!=0);
    }
    public boolean containsAttrTypeID () {
        return((fMiscFlags & CT_CONTAINS_ATTR_TYPE_ID)!=0);
    }
    public boolean declSeen () {
        return((fMiscFlags & CT_DECL_SEEN)!=0);
    }

    public void setIsAbstractType() {
        fMiscFlags |= CT_IS_ABSTRACT;
    }
    public void setContainsAttrTypeID() {
        fMiscFlags |= CT_CONTAINS_ATTR_TYPE_ID;
    }
    public void setDeclSeen() {
        fMiscFlags |= CT_DECL_SEEN;
    }




} // class XSComplexTypeDecl
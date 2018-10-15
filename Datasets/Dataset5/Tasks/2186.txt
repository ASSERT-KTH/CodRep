if (namespaceURI == null || prefix.indexOf(':') >=0) {

/* $Id$ */
/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 1999 The Apache Software Foundation.  All rights 
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
 * originally based on software copyright (c) 1999, International
 * Business Machines, Inc., http://www.apache.org.  For more
 * information on the Apache Software Foundation, please see
 * <http://www.apache.org/>.
 */

package org.apache.xerces.dom;

import org.w3c.dom.DOMException;


/**
 * ElementNSImpl inherits from ElementImpl and adds namespace support. 
 * <P>
 * The qualified name is the node name, and we store localName which is also
 * used in all queries. On the other hand we recompute the prefix when
 * necessary.
 */
public class ElementNSImpl
    extends ElementImpl {

    //
    // Constants
    //

    /** Serialization version. */
    static final long serialVersionUID = -9142310625494392642L;
    static final String xmlURI = "http://www.w3.org/XML/1998/namespace";

    //
    // Data
    //

    /** DOM2: Namespace URI. */
    protected String namespaceURI;
  
    /** DOM2: localName. */
    protected String localName;

    
    /**
     * DOM2: Constructor for Namespace implementation.
     */
    protected ElementNSImpl(CoreDocumentImpl ownerDocument, 
			    String namespaceURI,
			    String qualifiedName) 
        throws DOMException
    {
    	super(ownerDocument, qualifiedName);

        int index = qualifiedName.indexOf(':');
        String prefix;
        if (index < 0) {
            prefix = null;
            localName = qualifiedName;
        } 
        else {
            prefix = qualifiedName.substring(0, index); 
            localName = qualifiedName.substring(index+1);
        
            if (ownerDocument.errorChecking) {
                if (namespaceURI == null
                    || (localName.length() == 0)
                    || (localName.indexOf(':') >= 0)) {
                    throw new DOMException(DOMException.NAMESPACE_ERR, 
                                           "DOM003 Namespace error");
                }
                else if (prefix.equals("xml")) {
                    if (!namespaceURI.equals(xmlURI)) {
                        throw new DOMException(DOMException.NAMESPACE_ERR, 
                                               "DOM003 Namespace error");
                    }
                } else if (index == 0) {
                    throw new DOMException(DOMException.NAMESPACE_ERR, 
                                           "DOM003 Namespace error");
                }
            }
        }
	this.namespaceURI = namespaceURI;
    }

    // for DeferredElementImpl
    protected ElementNSImpl(CoreDocumentImpl ownerDocument, 
			    String value) {
	super(ownerDocument, value);
    }

    //
    // Node methods
    //

    
    //
    //DOM2: Namespace methods.
    //
    
    /** 
     * Introduced in DOM Level 2. <p>
     *
     * The namespace URI of this node, or null if it is unspecified.<p>
     *
     * This is not a computed value that is the result of a namespace lookup based on
     * an examination of the namespace declarations in scope. It is merely the
     * namespace URI given at creation time.<p>
     *
     * For nodes created with a DOM Level 1 method, such as createElement
     * from the Document interface, this is null.     
     * @since WD-DOM-Level-2-19990923
     */
    public String getNamespaceURI()
    {
        if (needsSyncData()) {
            synchronizeData();
        }
        return namespaceURI;
    }
    
    /** 
     * Introduced in DOM Level 2. <p>
     *
     * The namespace prefix of this node, or null if it is unspecified. <p>
     *
     * For nodes created with a DOM Level 1 method, such as createElement
     * from the Document interface, this is null. <p>
     *
     * @since WD-DOM-Level-2-19990923
     */
    public String getPrefix()
    {
        if (needsSyncData()) {
            synchronizeData();
        }
        int index = name.indexOf(':');
        return index < 0 ? null : name.substring(0, index); 
    }
    
    /** 
     * Introduced in DOM Level 2. <p>
     *
     * Note that setting this attribute changes the nodeName attribute, which holds the
     * qualified name, as well as the tagName and name attributes of the Element
     * and Attr interfaces, when applicable.<p>
     *
     * @throws INVALID_CHARACTER_ERR Raised if the specified
     * prefix contains an invalid character.     
     *
     * @since WD-DOM-Level-2-19990923
     */
    public void setPrefix(String prefix)
        throws DOMException
    {
        if (needsSyncData()) {
            synchronizeData();
        }
	if (ownerDocument().errorChecking) {
            if (isReadOnly()) {
                throw new DOMException(
                                     DOMException.NO_MODIFICATION_ALLOWED_ERR, 
                                     "DOM001 Modification not allowed");
            }
            if (!CoreDocumentImpl.isXMLName(prefix)) {
                throw new DOMException(DOMException.INVALID_CHARACTER_ERR, 
    	                               "DOM002 Illegal character");
            }
            if (namespaceURI == null) {
                  throw new DOMException(DOMException.NAMESPACE_ERR, 
                                         "DOM003 Namespace error");
            } else if (prefix != null) {
                if (prefix.equals("xml")) {
                    if (!namespaceURI.equals(xmlURI)) {
                        throw new DOMException(DOMException.NAMESPACE_ERR, 
                                               "DOM003 Namespace error");
                    }
                }
            }
        }
        // update node name with new qualifiedName
        name = prefix + ":" + localName;
    }
                                        
    /** 
     * Introduced in DOM Level 2. <p>
     *
     * Returns the local part of the qualified name of this node.
     * @since WD-DOM-Level-2-19990923
     */
    public String             getLocalName()
    {
        if (needsSyncData()) {
            synchronizeData();
        }
        return localName;
    }
}
"DOM001 Modification not allowed");

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

import org.w3c.dom.*;

/**
 * This class represents a Document Type <em>declaraction</em> in
 * the document itself, <em>not</em> a Document Type Definition (DTD).
 * An XML document may (or may not) have such a reference.
 * <P>
 * DocumentType is an Extended DOM feature, used in XML documents but
 * not in HTML.
 * <P>
 * Note that Entities and Notations are no longer children of the
 * DocumentType, but are parentless nodes hung only in their
 * appropriate NamedNodeMaps.
 * <P>
 * This area is UNDERSPECIFIED IN REC-DOM-Level-1-19981001
 * Most notably, absolutely no provision was made for storing
 * and using Element and Attribute information. Nor was the linkage
 * between Entities and Entity References nailed down solidly.
 *
 * @version
 * @since  PR-DOM-Level-1-19980818.
 */
public class DocumentTypeImpl 
    extends NodeContainer
    implements DocumentType {

    //
    // Constants
    //

    /** Serialization version. */
    static final long serialVersionUID = 7751299192316526485L;
    
    //
    // Data
    //

    /** Entities. */
    protected NamedNodeMapImpl entities;
    
    /** Notations. */
    protected NamedNodeMapImpl notations;

    // NON-DOM

    /** Elements. */
    protected NamedNodeMapImpl elements;
    
    // DOM2: support public ID.
    protected String publicID;
    
    // DOM2: support system ID.
    protected String systemID;
    
    // DOM2: support internal subset.
    protected String internalSubset;

    //
    // Constructors
    //

    /** Factory method for creating a document type node. */
    public DocumentTypeImpl(DocumentImpl ownerDocument, String name) {
        super(ownerDocument, name, null);

        // DOM
        entities  = new NamedNodeMapImpl(ownerDocument, null);
        notations = new NamedNodeMapImpl(ownerDocument, null);

        // NON-DOM
        elements = new NamedNodeMapImpl(ownerDocument,null);

    } // <init>(DocumentImpl,String)
  
    /** Factory method for creating a document type node. */
    public DocumentTypeImpl(DocumentImpl ownerDocument, String name, 
                            String publicID, String systemID, String internalSubset) {
        this(ownerDocument, name);
        this.publicID = publicID;
        this.systemID = systemID;
        this.internalSubset = internalSubset;


    } // <init>(DocumentImpl,String)
    
    //
    // DOM2: methods.
    //
    
    /**
     * Introduced in DOM Level 2. <p>
     * 
     * Return the public identifier of this Document type.
     * @since WD-DOM-Level-2-19990923
     */
    public String getPublicId() {
        if (syncData) {
            synchronizeData();
        }
        return publicID;
    }
    /**
     * Introduced in DOM Level 2. <p>
     * 
     * Return the system identifier of this Document type.
     * @since WD-DOM-Level-2-19990923
     */
    public String getSystemId() {
        if (syncData) {
            synchronizeData();
        }
        return systemID;
    }
    
    /**
     * Introduced in DOM Level 2. <p>
     * 
     * Return the internalSubset given as a string.
     * @since WD-DOM-Level-2-19990923
     */
    public String getInternalSubset() {
        if (syncData) {
            synchronizeData();
        }
        return internalSubset;
    }
    
    /**
     * Introduced in DOM Level 2. <p>
     * 
     * Return the internalSubset given as a string.
     * @since WD-DOM-Level-2-19990923
     */
    public void setInternalSubset(String internalSubset) {
        if (syncData) {
            synchronizeData();
        }
        this.internalSubset = internalSubset;
    }
    
   
    //
    // Node methods
    //

    /** 
     * A short integer indicating what type of node this is. The named
     * constants for this value are defined in the org.w3c.dom.Node interface.
     */
    public short getNodeType() {
        return Node.DOCUMENT_TYPE_NODE;
    }
    
    /**
     * DocumentTypes never have a nodeValue.
     * @throws DOMException(NO_MODIFICATION_ALLOWED_ERR)
     */
    public void setNodeValue(String value) throws DOMException {
    	throw new DOMExceptionImpl(
    		DOMException.NO_MODIFICATION_ALLOWED_ERR, 
    		"NO_MODIFICATION_ALLOWED_ERR");
    }

    /** Clones the node. */
    public Node cloneNode(boolean deep) {

    	DocumentTypeImpl newnode = (DocumentTypeImpl)super.cloneNode(deep);

    	// NamedNodeMaps must be cloned explicitly, to avoid sharing them.
    	newnode.entities  = entities.cloneMap();
    	newnode.notations = notations.cloneMap();
    	newnode.elements  = elements.cloneMap();

    	return newnode;

    } // cloneNode(boolean):Node

    //
    // DocumentType methods
    //

    /**
     * Name of this document type. If we loaded from a DTD, this should
     * be the name immediately following the DOCTYPE keyword.
     */
    public String getName() {

        if (syncData) {
            synchronizeData();
        }
    	return name;

    } // getName():String

    /**
     * Access the collection of general Entities, both external and
     * internal, defined in the DTD. For example, in:
     * <p>
     * <pre>
     *   &lt;!doctype example SYSTEM "ex.dtd" [
     *     &lt;!ENTITY foo "foo"&gt;
     *     &lt;!ENTITY bar "bar"&gt;
     *     &lt;!ENTITY % baz "baz"&gt;
     *     ]&gt;
     * </pre>
     * <p>
     * The Entities map includes foo and bar, but not baz. It is promised that
     * only Nodes which are Entities will exist in this NamedNodeMap.
     * <p>
     * For HTML, this will always be null.
     * <p>
     * Note that "built in" entities such as &amp; and &lt; should be
     * converted to their actual characters before being placed in the DOM's
     * contained text, and should be converted back when the DOM is rendered
     * as XML or HTML, and hence DO NOT appear here.
     */
    public NamedNodeMap getEntities() {
        if (syncChildren) {
            synchronizeChildren();
            }
    	return entities;
    }

    /**
     * Access the collection of Notations defined in the DTD.  A
     * notation declares, by name, the format of an XML unparsed entity
     * or is used to formally declare a Processing Instruction target.
     */
    public NamedNodeMap getNotations() {
        if (syncChildren) {
            synchronizeChildren();
            }
    	return notations;
    }

    //
    // Public methods
    //

    /**
     * NON-DOM: Subclassed to flip the entities' and notations' readonly switch
     * as well.
     * @see NodeImpl#setReadOnly
     */
    public void setReadOnly(boolean readOnly, boolean deep) {
    	
        if (syncChildren) {
            synchronizeChildren();
            }
        setReadOnly(readOnly, deep);

        // set read-only property
        elements.setReadOnly(readOnly, true);
        entities.setReadOnly(readOnly, true);
    	notations.setReadOnly(readOnly, true);

    } // setReadOnly(boolean,boolean)
    
    /**
     * NON-DOM: Access the collection of ElementDefinitions.
     * @see ElementDefinitionImpl
     */
    public NamedNodeMap getElements() {
        if (syncChildren) {
            synchronizeChildren();
            }
    	return elements;
    }

} // class DocumentTypeImpl
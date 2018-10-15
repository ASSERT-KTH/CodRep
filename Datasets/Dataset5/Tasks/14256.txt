extends NodeContainer

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

import java.util.Enumeration;
import java.util.Hashtable;
import java.util.Vector;

import org.w3c.dom.*;

import org.w3c.dom.traversal.*;
import org.apache.xerces.dom.traversal.*;
import org.w3c.dom.events.*;
import org.apache.xerces.dom.events.*;

/**
 * The Document interface represents the entire HTML or XML document.
 * Conceptually, it is the root of the document tree, and provides the
 * primary access to the document's data.
 * <P>
 * Since elements, text nodes, comments, processing instructions,
 * etc. cannot exist outside the context of a Document, the Document
 * interface also contains the factory methods needed to create these
 * objects. The Node objects created have a ownerDocument attribute
 * which associates them with the Document within whose context they
 * were created.
 * <p>
 * The DocumentImpl class also implements the DOM Level 2 DocumentTraversal
 * interface. This interface is comprised of factory methods needed to
 * create NodeIterators and TreeWalkers. The process of creating these
 * traversal objects also adds these references to this document.
 * After finishing with the It is important to remove the traversal objects
 * using the remove methods in this implementation. This allows the release of
 * all the references from the traversal objects to the DOM Nodes.
 * <p>
 * <b>Note:</b> When any node in the document is serialized, the
 * entire document is serialized along with it.
 *
 * @version
 * @since  PR-DOM-Level-1-19980818.
 */
public class DocumentImpl
    extends NodeImpl
    implements Document, DocumentTraversal, DocumentEvent {

    //
    // Constants
    //

    /** Serialization version. */
    static final long serialVersionUID = 515687835542616694L;

    //
    // Data
    //

    // document information

    /** Document type. */
    protected DocumentTypeImpl docType;

    /** Document element. */
    protected ElementImpl docElement;

    /** Identifiers. */
    protected Hashtable identifiers;

    /** Iterators */
    // REVISIT: Should this be transient? -Ac
    protected Vector iterators;

    /** Tree walkers */
    // REVISIT: Should this be transient? -Ac
    protected Vector treeWalkers;
	
    // experimental

    /** Allow grammar access. */
    protected boolean allowGrammarAccess;

    /** Bypass error checking. */
    protected boolean errorChecking = true;

    //
    // Constructors
    //

    /**
     * NON-DOM: Actually creating a Document is outside the DOM's spec,
     * since it has to operate in terms of a particular implementation.
     */
    public DocumentImpl() {
        this(false);
    }

    /** Experimental constructor. */
    public DocumentImpl(boolean grammarAccess) {
        super(null,null,null);
        // REVISIT: Documents don't have owner documents. -Ac
        ownerDocument = this;
        allowGrammarAccess = grammarAccess;
    }

    // For DOM2: support. The createDocument factory method is in DOMImplementation.
    public DocumentImpl(DocumentType doctype)
    {
        this(doctype, false);
    }
    
    /** Experimental constructor. */
    public DocumentImpl(DocumentType doctype, boolean grammarAccess) {
        this(grammarAccess);
        this.docType = (DocumentTypeImpl)doctype;
        if (this.docType != null) {
            docType.ownerDocument = this;
            docType.entities.ownerDocument = this;
            docType.notations.ownerDocument = this;
            docType.elements.ownerDocument = this;
        }

    }

    //
    // Node methods
    //

    /** Returns the node type. */
    public short getNodeType() {
        return Node.DOCUMENT_NODE;
    }

    /** Returns the node name. */
    public String getNodeName() {
        return "#document";
    }

    /** Returns the node value. */
    public String getNodeValue() {
        return null;
    }

    /**
     * Deep-clone a document, including fixing ownerDoc for the cloned
     * children. Note that this requires bypassing the WRONG_DOCUMENT_ERR
     * protection. I've chosen to implement it by calling importNode --
     * which is NON-DOM in Level 1, but which anticipates one likely
     * direction the Level 2 DOM might take in solving this.
     *
     * @return org.w3c.dom.Node
     * @param deep boolean, iff true replicate children
     */
    public Node cloneNode(boolean deep) {

        // NOTE: Cloning causing full fluffing. -Ac
        DocumentImpl newdoc = new DocumentImpl();

    	if (deep) {
    		for(NodeImpl n = (NodeImpl)getFirstChild();
                n != null;
                n = n.nextSibling)
                {
    			newdoc.appendChild(newdoc.importNode(n,true));
            }
        }

    	return newdoc;

    } // cloneNode(boolean):Node

    /**
     * Since a Document may contain at most one top-level Element child,
  	 * and at most one DocumentType declaraction, we need to subclass our
  	 * add-children methods to implement this constraint.
	 * Since appendChild() is implemented as insertBefore(,null),
	 * altering the latter fixes both.
  	 * <p>
  	 * While I'm doing so, I've taken advantage of the opportunity to
  	 * cache documentElement and docType so we don't have to
  	 * search for them.
	 */
    public Node insertBefore(Node newChild, Node refChild)
        throws DOMException {

    	// Only one such child permitted
        int type = newChild.getNodeType();
        if (errorChecking) {
            if((type == Node.ELEMENT_NODE && docElement != null) ||
               (type == Node.DOCUMENT_TYPE_NODE && docType != null)) {
                throw new DOMExceptionImpl(DOMException.HIERARCHY_REQUEST_ERR,
                                           "HIERARCHY_REQUEST_ERR");
            }
        }

    	super.insertBefore(newChild,refChild);

    	// If insert succeeded, cache the kid appropriately
        if (type == Node.ELEMENT_NODE) {
    	    docElement = (ElementImpl)newChild;
        }
        else if (type == Node.DOCUMENT_TYPE_NODE) {
    	    docType=(DocumentTypeImpl)newChild;
        }

    	return newChild;

    } // insertBefore(Node,Node):Node

    /**
     * Since insertBefore caches the docElement (and, currently, docType),
	 * removeChild has to know how to undo the cache
     */
    public Node removeChild(Node oldChild)
        throws DOMException {
	    super.removeChild(oldChild);
	
    	// If remove succeeded, un-cache the kid appropriately
        int type = oldChild.getNodeType();
        if(type == Node.ELEMENT_NODE) {
    	    docElement = null;
        }
        else if (type == Node.DOCUMENT_TYPE_NODE) {
    	    docType=null;
        }

    	return oldChild;

    }   // removeChild(Node):Node

    /**
     * Documents never have a nodeValue.
     * @throws DOMException(NO_MODIFICATION_ALLOWED_ERR)
     */
    public void setNodeValue(String x)
        throws DOMException {
    	throw new DOMExceptionImpl(DOMException.NO_MODIFICATION_ALLOWED_ERR, 
    	                           "NO_MODIFICATION_ALLOWED_ERR");
    }

    //
    // Document methods
    //

    // factory methods

    /**
     * Factory method; creates an Attribute having this Document as its
	 * OwnerDoc.
     *
	 * @param name The name of the attribute. Note that the attribute's value
	 * is _not_ established at the factory; remember to set it!
     *
	 * @throws DOMException(INVALID_NAME_ERR) if the attribute name is not
	 * acceptable.
     */
    public Attr createAttribute(String name)
        throws DOMException {

    	if(errorChecking && !isXMLName(name)) {
    		throw new DOMExceptionImpl(DOMException.INVALID_CHARACTER_ERR,
    		                           "INVALID_CHARACTER_ERR");
        }

    	return new AttrImpl(this, name);

    } // createAttribute(String):Attr

    /**
     * Factory method; creates a CDATASection having this Document as
	 * its OwnerDoc.
     *
	 * @param data The initial contents of the CDATA
     *
	 * @throws DOMException(NOT_SUPPORTED_ERR) for HTML documents. (HTML
	 * not yet implemented.)
	 */
    public CDATASection createCDATASection(String data)
	    throws DOMException {
	    return new CDATASectionImpl(this, data);
    }

    /**
     * Factory method; creates a Comment having this Document as its
     * OwnerDoc.
     *
     * @param data The initial contents of the Comment. */
    public Comment createComment(String data) {
	    return new CommentImpl(this, data);
    }

    /**
     * Factory method; creates a DocumentFragment having this Document
	 * as its OwnerDoc.
     */
    public DocumentFragment createDocumentFragment() {
	    return new DocumentFragmentImpl(this);
    }

    /**
     * Factory method; creates an Element having this Document
	 * as its OwnerDoc.
     *
	 * @param tagName The name of the element type to instantiate. For
	 * XML, this is case-sensitive. For HTML, the tagName parameter may
	 * be provided in any case, but it must be mapped to the canonical
	 * uppercase form by the DOM implementation.
     *
	 * @throws DOMException(INVALID_NAME_ERR) if the tag name is not
	 * acceptable.
	 */
    public Element createElement(String tagName)
        throws DOMException {

    	if (errorChecking && !isXMLName(tagName)) {
    		throw new DOMExceptionImpl(DOMException.INVALID_CHARACTER_ERR, 
    		                           "INVALID_CHARACTER_ERR");
        }

    	return new ElementImpl(this, tagName);

    } // createElement(String):Element

    /**
     * Factory method; creates an EntityReference having this Document
     * as its OwnerDoc.
     *
     * @param name The name of the Entity we wish to refer to
     *
     * @throws DOMException(NOT_SUPPORTED_ERR) for HTML documents, where
     * nonstandard entities are not permitted. (HTML not yet
     * implemented.)
     */
    public EntityReference createEntityReference(String name)
        throws DOMException {

    	if (errorChecking && !isXMLName(name)) {
    		throw new DOMExceptionImpl(DOMException.INVALID_CHARACTER_ERR, 
    		                           "INVALID_CHARACTER_ERR");
        }

    	return new EntityReferenceImpl(this, name);

    } // createEntityReference(String):EntityReference

    /**
     * Factory method; creates a ProcessingInstruction having this Document
	 * as its OwnerDoc.
     *
	 * @param target The target "processor channel"
	 * @param data Parameter string to be passed to the target.
     *
	 * @throws DOMException(INVALID_NAME_ERR) if the target name is not
	 * acceptable.
     *
	 * @throws DOMException(NOT_SUPPORTED_ERR) for HTML documents. (HTML
	 * not yet implemented.)
	 */
    public ProcessingInstruction createProcessingInstruction(String target, String data)
        throws DOMException {

    	if(errorChecking && !isXMLName(target)) {
    		throw new DOMExceptionImpl(DOMException.INVALID_CHARACTER_ERR,
    		                           "INVALID_CHARACTER_ERR");
        }

    	return new ProcessingInstructionImpl(this, target, data);

    } // createProcessingInstruction(String,String):ProcessingInstruction

    /**
     * Factory method; creates a Text node having this Document as its
	 * OwnerDoc.
     *
	 * @param data The initial contents of the Text.
     */
    public Text createTextNode(String data) {
        return new TextImpl(this, data);
    }

    // other document methods

    /**
     * For XML, this provides access to the Document Type Definition.
	 * For HTML documents, and XML documents which don't specify a DTD,
	 * it will be null.
	 */
    public DocumentType getDoctype() {
        if (syncChildren) {
            synchronizeChildren();
        }
	    return docType;
    }

    /**
     * Convenience method, allowing direct access to the child node
	 * which is considered the root of the actual document content. For
	 * HTML, where it is legal to have more than one Element at the top
	 * level of the document, we pick the one with the tagName
	 * "HTML". For XML there should be only one top-level
     *
	 * (HTML not yet supported.)
     */
    public Element getDocumentElement() {
        if (syncChildren) {
            synchronizeChildren();
        }
	    return docElement;
    }

    /**
     * Return a <em>live</em> collection of all descendent Elements (not just
	 * immediate children) having the specified tag name.
     *
	 * @param tagname The type of Element we want to gather. "*" will be
	 * taken as a wildcard, meaning "all elements in the document."
     *
	 * @see DeepNodeListImpl
	 */
    public NodeList getElementsByTagName(String tagname) {
	    return new DeepNodeListImpl(this,tagname);
    }

    /**
     * Retrieve information describing the abilities of this particular
	 * DOM implementation. Intended to support applications that may be
	 * using DOMs retrieved from several different sources, potentially
	 * with different underlying representations.
	 */
    public DOMImplementation getImplementation() {
        // Currently implemented as a singleton, since it's hardcoded
        // information anyway.
        return DOMImplementationImpl.getDOMImplementation();
    }

    //
    // Public methods
    //

    // properties

    /** 
     * Sets whether the DOM implementation performs error checking
     * upon operations. Turning off error checking only affects
     * the following DOM checks:
     * <ul>
     * <li>Checking strings to make sure that all characters are
     *     legal XML characters
     * <li>Hierarchy checking such as allowed children, checks for
     *     cycles, etc.
     * </ul>
     * <p>
     * Turning off error checking does <em>not</em> turn off the
     * following checks:
     * <ul>
     * <li>Read only checks
     * <li>Checks related to DOM events
     * </ul>
     */
    public void setErrorChecking(boolean check) {
        errorChecking = check;
    }

    /**
     * Returns true if the DOM implementation performs error checking.
     */
    public boolean getErrorChecking() {
        return errorChecking;
    }

    // non-DOM factory methods
    
    /**
     * NON-DOM
     * Factory method; creates a DocumentType having this Document
     * as its OwnerDoc. (REC-DOM-Level-1-19981001 left the process of building
     * DTD information unspecified.)
     *
     * @param name The name of the Entity we wish to provide a value for.
     *
     * @throws DOMException(NOT_SUPPORTED_ERR) for HTML documents, where
     * DTDs are not permitted. (HTML not yet implemented.)
     */
    public DocumentType createDocumentType(String qualifiedName,
                                           String publicID,
                                           String systemID,
                                           String internalSubset)
        throws DOMException {

    	if (errorChecking && !isXMLName(qualifiedName)) {
    		throw new DOMExceptionImpl(DOMException.INVALID_CHARACTER_ERR, 
    		                           "INVALID_CHARACTER_ERR");
        }

        // REVISIT: What is the right thing to do here? Set the owner doc
        //          as "this"? Provide a setOwnerDocument() method? -Ac
    	return new DocumentTypeImpl(this, qualifiedName, publicID, systemID, internalSubset);

    } // createDocumentType(String):DocumentType

    /**
     * NON-DOM
     * Factory method; creates an Entity having this Document
     * as its OwnerDoc. (REC-DOM-Level-1-19981001 left the process of building
     * DTD information unspecified.)
     *
     * @param name The name of the Entity we wish to provide a value for.
     *
     * @throws DOMException(NOT_SUPPORTED_ERR) for HTML documents, where
     * nonstandard entities are not permitted. (HTML not yet
     * implemented.)
     */
    public Entity createEntity(String name)
        throws DOMException {

        // REVISIT: Should we be checking XML name chars?
        /***
    	if (errorChecking && !isXMLName(name)) {
    		throw new DOMExceptionImpl(DOMException.INVALID_CHARACTER_ERR, 
    		                           "INVALID_CHARACTER_ERR");
        }
        /***/

    	return new EntityImpl(this, name);

    } // createEntity(String):Entity

    /**
     * NON-DOM
     * Factory method; creates a Notation having this Document
     * as its OwnerDoc. (REC-DOM-Level-1-19981001 left the process of building
     * DTD information unspecified.)
     *
     * @param name The name of the Notation we wish to describe
     *
     * @throws DOMException(NOT_SUPPORTED_ERR) for HTML documents, where
     * notations are not permitted. (HTML not yet
     * implemented.)
     */
    public Notation createNotation(String name)
        throws DOMException {

        // REVISIT: Should we be checking XML name chars?
        /***
    	if (errorChecking && !isXMLName(name)) {
    		throw new DOMExceptionImpl(DOMException.INVALID_CHARACTER_ERR, 
    		                           "INVALID_CHARACTER_ERR");
        }
        /***/

    	return new NotationImpl(this, name);

    } // createNotation(String):Notation

    /**
     * NON-DOM Factory method: creates an element definition. Element
     * definitions hold default attribute values.
     */
    public ElementDefinitionImpl createElementDefinition(String name)
        throws DOMException {

        // REVISIT: Should we be checking XML name chars?
        /***
    	if (errorChecking && !isXMLName(name)) {
    		throw new DOMExceptionImpl(DOMException.INVALID_CHARACTER_ERR, 
    		                           "INVALID_CHARACTER_ERR");
        }
        /***/

        return new ElementDefinitionImpl(this, name);

    } // createElementDefinition(String):ElementDefinitionImpl

    // other non-DOM methods

    /**
     * NON-DOM: Copies data from the source node. Unlike cloneNode, this
     * _can_ copy data from another document. If the source document is also
     * based on org.apache.xerces.dom, we will attempt to preserve the domimpl-
     * internal data by doing a clone-and-reparent. If not, we will use
     * the source's public methods, and this document's Factory methods,
     * to copy data defined by the DOM interfaces.
     *
     * Its behavior is otherwise similar to that of cloneNode.
     *
     * Attempting to import a Document into another Document is meaningless --
     * a new Document would not improve matters much, and a DocumentFragment
     * couldn't carry the DocumentType child (if any). Best thing we can do
     * is throw a HIERARCHY_REQUEST_ERR.
     *
     * ????? Should we push some of this down to copy-ctors, so
     * subclassed DOMs have the option of special-casing each other
     * (as we do for ourself)?
     */
    public Node importNode(Node source, boolean deep)
        throws DOMException {

    	NodeImpl newnode=null;

    	// Sigh. This doesn't work; too many nodes have private data that
    	// would have to be manually tweaked. May be able to add local
    	// shortcuts to each nodetype. Consider ?????
    	// if(source instanceof NodeImpl &&
    	//	!(source instanceof DocumentImpl))
    	// {
    	//  // Can't clone DocumentImpl since it invokes us...
    	//	newnode=(NodeImpl)source.cloneNode(false);
    	//	newnode.ownerDocument=this;
    	//}
    	//else
        int type = source.getNodeType();
    	switch (type) {
    		
            case ELEMENT_NODE: {
    			Element newelement = createElement(source.getNodeName());
    			NamedNodeMap srcattr = source.getAttributes();
    			if (srcattr != null) {
    				for(int i = 0; i < srcattr.getLength(); i++) {
    					newelement.setAttributeNode(
    						(AttrImpl)importNode(srcattr.item(i), true));
                    }
                }
    			newnode = (NodeImpl)newelement;
    			break;
            }

            case ATTRIBUTE_NODE: {
    			newnode = (NodeImpl)createAttribute(source.getNodeName());
    			// Kids carry value
    			break;
            }

    		case TEXT_NODE: {
    			newnode = (NodeImpl)createTextNode(source.getNodeValue());
    			break;
            }

    		case CDATA_SECTION_NODE: {
    			newnode = (NodeImpl)createCDATASection(source.getNodeValue());
    			break;
            }

    		case ENTITY_REFERENCE_NODE: {
    			newnode = (NodeImpl)createEntityReference(source.getNodeName());
    			deep = false; // ????? Right Thing?
    			// Value implied by doctype, so we should not copy it
    			// -- instead, refer to local doctype, if any.
    			break;
            }

    		case ENTITY_NODE: {
    			Entity srcentity = (Entity)source;
    			EntityImpl newentity = (EntityImpl)createEntity(source.getNodeName());
    			newentity.setPublicId(srcentity.getPublicId());
    			newentity.setSystemId(srcentity.getSystemId());
    			newentity.setNotationName(srcentity.getNotationName());
    			// Kids carry additional value
    			newnode = newentity;
    			break;
            }

    		case PROCESSING_INSTRUCTION_NODE: {
    			newnode = (ProcessingInstructionImpl)createProcessingInstruction(source.getNodeName(), source.getNodeValue());
    			break;
            }

    		case COMMENT_NODE: {
    			newnode = (NodeImpl)createComment(source.getNodeValue());
    			break;
            }

    		case DOCUMENT_TYPE_NODE: {
    		    DocumentTypeImpl doctype = (DocumentTypeImpl)source;
    			DocumentTypeImpl newdoctype =
    			    (DocumentTypeImpl)createDocumentType(
    			        doctype.getNodeName(),
    			        doctype.getPublicId(), 
    			        doctype.getSystemId(),
    			        doctype.getInternalSubset()
    			        );
    			// Values are on NamedNodeMaps
    			NamedNodeMap smap = ((DocumentType)source).getEntities();
    			NamedNodeMap tmap = newdoctype.getEntities();
    			if(smap != null) {
    				for(int i = 0; i < smap.getLength(); i++) {
    					tmap.setNamedItem((EntityImpl)importNode(smap.item(i), true));
                    }
                }
    			smap = ((DocumentType)source).getNotations();
    			tmap = newdoctype.getNotations();
    			if (smap != null) {
    				for(int i = 0; i < smap.getLength(); i++) {
    					tmap.setNamedItem((NotationImpl)importNode(smap.item(i), true));
                    }
                }
    			// NOTE: At this time, the DOM definition of DocumentType
    			// doesn't cover Elements and their Attributes. domimpl's
    			// extentions in that area will not be preserved, even if
    			// copying from domimpl to domimpl. We could special-case
    			// that here. Arguably we should. Consider. ?????
    		    newnode = newdoctype;
    			break;
            }

    		case DOCUMENT_FRAGMENT_NODE: {
    			newnode = (NodeImpl)createDocumentFragment();
    			// No name, kids carry value
    			break;
            }

    		case NOTATION_NODE: {
    			Notation srcnotation = (Notation)source;
    			NotationImpl newnotation = (NotationImpl)createNotation(source.getNodeName());
    			newnotation.setPublicId(srcnotation.getPublicId());
    			newnotation.setSystemId(srcnotation.getSystemId());
    			// Kids carry additional value
    			newnode = newnotation;
    			// No name, no value
    			break;
            }

    		case DOCUMENT_NODE : // Document can't be child of Document
    		default: {			 // Unknown node type
    			throw new DOMExceptionImpl(DOMException.HIERARCHY_REQUEST_ERR,
    			                           "HIERARCHY_REQUEST_ERR");
            }
        }

    	// If deep, replicate and attach the kids.
    	if (deep) {
    		for (Node srckid = source.getFirstChild();
                 srckid != null;
                 srckid = srckid.getNextSibling()) {
    			newnode.appendChild(importNode(srckid, true));
    		}
        }

    	return newnode;

    } // importNode(Node,boolean):Node

    // identifier maintenence
    /**
     *  Introduced in DOM Level 2 
     *  Returns the Element whose ID is given by elementId. If no such element
     *  exists, returns null. Behavior is not defined if more than one element has this ID.
     *  <p>
     *  Note: The DOM implementation must have information that says which
     *  attributes are of type ID. Attributes with the name "ID" are not of type ID unless
     *  so defined. Implementations that do not know whether attributes are of type ID
     *  or not are expected to return null.
     * @see #getIdentifier
     */
    public Element getElementById(String elementId) {
        return getIdentifier(elementId);
    }

    /**
     * Registers an identifier name with a specified element node.
     * If the identifier is already registered, the new element
     * node replaces the previous node. If the specified element
     * node is null, removeIdentifier() is called.
     *
     * @see #getIdentifier
     * @see #removeIdentifier
     */
    public void putIdentifier(String idName, Element element) {

        if (element == null) {
            removeIdentifier(idName);
        }

        if (syncData) {
            synchronizeData();
        }

        if (identifiers == null) {
            identifiers = new Hashtable();
        }

        identifiers.put(idName, element);

    } // putIdentifier(String,Element)

    /**
     * Returns a previously registered element with the specified
     * identifier name, or null if no element is registered.
     *
     * @see #putIdentifier
     * @see #removeIdentifier
     */
    public Element getIdentifier(String idName) {

        if (syncData) {
            synchronizeData();
        }

        if (identifiers == null) {
            return null;
        }

        return (Element)identifiers.get(idName);

    } // getIdentifier(String):Element

    /**
     * Removes a previously registered element with the specified
     * identifier name.
     *
     * @see #putIdentifier
     * @see #getIdentifier
     */
    public void removeIdentifier(String idName) {

        if (syncData) {
            synchronizeData();
        }

        if (identifiers == null) {
            return;
        }

        identifiers.remove(idName);

    } // removeIdentifier(String)

    /** Returns an enumeration registered of identifier names. */
    public Enumeration getIdentifiers() {

        if (syncData) {
            synchronizeData();
        }

        if (identifiers == null) {
            identifiers = new Hashtable();
        }

        return identifiers.keys();

    } // getIdentifiers():Enumeration

    //
    // DOM2: Namespace methods
    //

    /**
     * Introduced in DOM Level 2. <p>
     * Creates an element of the given qualified name and namespace URI. 
     * If the given namespaceURI is null or an empty string and the 
     * qualifiedName has a prefix that is "xml", the created element 
     * is bound to the predefined namespace
     * "http://www.w3.org/XML/1998/namespace" [Namespaces]. 
     * @param namespaceURI The namespace URI of the element to
     *                     create.
     * @param qualifiedName The qualified name of the element type to
     *                      instantiate.
     * @return Element A new Element object with the following attributes:
     * @throws DOMException INVALID_CHARACTER_ERR: Raised if the specified
                            name contains an invalid character.
     * @throws DOMException NAMESPACE_ERR: Raised if the qualifiedName has a
     *                      prefix that is "xml" and the namespaceURI is 
     *                      neither null nor an empty string nor 
     *                      "http://www.w3.org/XML/1998/namespace", or
     *                      if the qualifiedName has a prefix different 
     *                      from "xml" and the namespaceURI is null or an empty string.
     * @since WD-DOM-Level-2-19990923
     */
    public Element createElementNS(String namespaceURI, String qualifiedName)
        throws DOMException
    {
        return new ElementImpl( this, namespaceURI, qualifiedName);
    }

    /**
     * Introduced in DOM Level 2. <p>
     * Creates an attribute of the given qualified name and namespace URI. 
     * If the given namespaceURI is null or an empty string and the 
     * qualifiedName has a prefix that is "xml", the created element 
     * is bound to the predefined namespace
     * "http://www.w3.org/XML/1998/namespace" [Namespaces]. 
     *
     * @param namespaceURI  The namespace URI of the attribute to
     *                      create. When it is null or an empty string,
     *                      this method behaves like createAttribute.
     * @param qualifiedName The qualified name of the attribute to
     *                      instantiate.
     * @return Attr         A new Attr object.
     * @throws DOMException INVALID_CHARACTER_ERR: Raised if the specified
                            name contains an invalid character.
     * @since WD-DOM-Level-2-19990923
     */
    public Attr createAttributeNS(String namespaceURI, String qualifiedName)
        throws DOMException
    {
        return new AttrImpl( this, namespaceURI, qualifiedName);
    }

    /**
     * Introduced in DOM Level 2. <p>
     * Returns a NodeList of all the Elements with a given local name and
     * namespace URI in the order in which they would be encountered in a preorder
     * traversal of the Document tree.
     * @param namespaceURI  The namespace URI of the elements to match
     *                      on. The special value "*" matches all
     *                      namespaces. When it is null or an empty
     *                      string, this method behaves like
     *                      getElementsByTagName.
     * @param localName     The local name of the elements to match on.
     *                      The special value "*" matches all local names.
     * @return NodeList     A new NodeList object containing all the matched Elements.
     * @since WD-DOM-Level-2-19990923
     */
    public NodeList getElementsByTagNameNS(String namespaceURI, String localName)
    {
	    return new DeepNodeListImpl(this, namespaceURI, localName);
    }

    //
    // DocumentTraversal methods
    //

    /**
     * Introduced in DOM Level 2. Optional. <p>
     * Create and return a NodeIterator. The NodeIterator is
     * added to a list of NodeIterators so that it can be
     * removed to free up the DOM Nodes it references.
     * @see #removeNodeIterator
     * @see #removeNodeIterators
     * @see #getNodeIterators
     *
     * @param root The root of the iterator.
     * @param whatToShow The whatToShow mask.
     * @param filter The NodeFilter installed. Null means no filter.
     * @since WD-DOM-Level-2-19990923
     */
    public NodeIterator createNodeIterator(Node root,
                                           short whatToShow,
                                           NodeFilter filter)
    {                                           
        return createNodeIterator(root,whatToShow,filter,true);
    }    
     
    /** NON-DOM extension:
     * Create and return a NodeIterator. The NodeIterator is
     * added to a list of NodeIterators so that it can be
     * removed to free up the DOM Nodes it references.
     * @see #removeNodeIterator
     * @see #removeNodeIterators
     * @see #getNodeIterators
     *
     * @param root The root of the iterator.
     * @param whatToShow The whatToShow mask.
     * @param filter The NodeFilter installed. Null means no filter.
     * @param entityReferenceExpansion true to expand the contents of EntityReference nodes
     * @since WD-DOM-Level-2-19990923
     */
    public NodeIterator createNodeIterator(Node root,
                                           int whatToShow,
                                           NodeFilter filter,
                                           boolean entityReferenceExpansion)
    {
        NodeIterator iterator = new NodeIteratorImpl(
                                        this,
                                        root,
                                        whatToShow,
                                        filter,
                                        entityReferenceExpansion);
        if (iterators == null) {
            iterators = new Vector();
        }

        iterators.addElement(iterator);

        return iterator;
    }

    /**
     * Introduced in DOM Level 2. Optional. <p>
     * Create and return a TreeWalker. The TreeWalker is
     * added to a list of TreeWalkers so that it can be
     * removed to free up the DOM Nodes it references.
     * @see #removeTreeWalker
     * @see #removeTreeWalkers
     * @see #getTreeWalkers
     *
     * @param root The root of the iterator.
     * @param whatToShow The whatToShow mask.
     * @param filter The NodeFilter installed. Null means no filter.
     * @since WD-DOM-Level-2-19990923
     */
    public TreeWalker createTreeWalker(Node root,
                                       short whatToShow,
                                       NodeFilter filter)
    {
        return createTreeWalker(root,whatToShow,filter,true);
    }
    /**
     * NON-DOM extension:
     * Create and return a TreeWalker. The TreeWalker is
     * added to a list of TreeWalkers so that it can be
     * removed to free up the DOM Nodes it references.
     * @see #removeTreeWalker
     * @see #removeTreeWalkers
     * @see #getTreeWalkers
     *
     * @param root The root of the iterator.
     * @param whatToShow The whatToShow mask.
     * @param filter The NodeFilter installed. Null means no filter.
     * @param entityReferenceExpansion true to expand the contents of EntityReference nodes
     * @since WD-DOM-Level-2-19990923
     */
    public TreeWalker createTreeWalker(Node root,
                                       int whatToShow,
                                       NodeFilter filter,
                                       boolean entityReferenceExpansion)
    {
    	if( root==null) {
    		throw new DOMExceptionImpl(
    			DOMException.NOT_SUPPORTED_ERR, 
    		    "NOT_SUPPORTED_ERR");
        }
        
        TreeWalker treeWalker = new TreeWalkerImpl(root,
                                                   whatToShow,
                                                   filter,
                                                   entityReferenceExpansion);
        if (treeWalkers == null) {
            treeWalkers = new Vector();
        }

        treeWalkers.addElement(treeWalker);

        return treeWalker;
    }

    //
    // Not yet DOM Level 2. Support DocumentTraversal methods.
    //

    /**
     *  Remove a NodeIterator from the list of NodeIterators.
     *  Should be called when finished using a NodeIterator.
     *  Not yet DOM Level 2, but some removal or deregistration
     *  mechanism is needed.
     */
    public void removeNodeIterator(NodeIterator nodeIterator) {

        if (nodeIterator == null) return;
        if (iterators == null) return;

        iterators.removeElement(nodeIterator);
    }

    /** Remove a TreeWalker from the list of TreeWalkers. */
    public void removeTreeWalker(TreeWalker treeWalker) {

        if (treeWalker == null) return;
        if (treeWalkers == null) return;

        treeWalkers.removeElement(treeWalker);
    }

    /** Return an Enumeration of all NodeIterators. */
    public Enumeration getNodeIterators() {
        if (iterators == null) return null;

        return iterators.elements();
    }

    /** Return an Enumeration of all TreeWalkers. */
    public Enumeration getTreeWalkers() {
        if (treeWalkers == null) return null;

        return treeWalkers.elements();
    }

    /** Remove all NodeIterators from the list of NodeIterators */
    public void removeNodeIterators() {

        iterators = null;
    }

    /** Remove all TreeWalkers from the list of TreeWalkers */
    public void removeTreeWalkers() {

        treeWalkers = null;
    }
    
    //
    // DocumentEvent methods
    //

    /**
     * Introduced in DOM Level 2. Optional. <p>
     * Create and return Event objects. 
	 * <p>
	 * @param type The event set name, defined as the interface name 
	 * minus package qualifiers. For example, to create a DOMNodeInserted
	 * event you'd call <code>createEvent("MutationEvent")</code>, 
	 * then use its initMutationEvent() method to configure it properly
	 * as DOMNodeInserted. This parameter is case-sensitive.
	 * @return an uninitialized Event object. Call the appropriate
	 * <code>init...Event()</code> method before dispatching it.
	 * @exception DOMException UNSUPPORTED_EVENT_TYPE if the requested
	 * event set is not supported in this DOM.
     * @since WD-DOM-Level-2-19990923
     */
    public Event createEvent(String type) 
	throws DOMException {
	    if("Event".equals(type))
	        return new EventImpl();
	    if("MutationEvent".equals(type))
	        return new MutationEventImpl();
	    else
	        throw new DOMExceptionImpl(DOMExceptionImpl.UNSUPPORTED_EVENT_TYPE,null);
	}
     


    //
    // Public static methods
    //

    /**
     * Check the string against XML's definition of acceptable names for
     * elements and attributes and so on. From the XML spec:
     * <p>
     * [Definition:] A Name is a token beginning with a letter or one of a
     * few punctuation characters, and continuing with letters, digits,
     * hyphens,underscores, colons, or full stops, together known as name
     * characters.
     * <p>
     * Unfortunately, that spec goes on to say that after the first character,
     * names may use "combining characters" and "extender characters",
     * which are explicitly listed rather than defined in terms of Java's
     * Unicode character types... and which in fact can't be expressed solely
     * in terms of those types.
     * <p>
     * I've empirically derived some tests which are partly based on the
     * Java Unicode space (which simplifies them considerably), but they
     * still wind up having to be further qualified. This may not remain
     * valid if future extensions of Java and/or Unicode introduce other
     * characters having these type numbers.
     * <p>
     * Suggestions for alternative implementations would be welcome.
     */
    public static boolean isXMLName(String s) {

        // REVISIT: Use the parser's character checking code. -Ac

        if (s == null) {
            return false;
        }

    	char [] ca=new char[s.length()];
    	s.getChars(0,s.length(),ca,0);

    	// First character must be letter, underscore, or colon.
    	if (!Character.isLetter(ca[0]) && "_:".indexOf((int)ca[0]) == -1) {
    		return false;
            }

    	// Remaining characters must be letter, digit, underscore,
    	// colon, period, dash, an XML "Combining Character", or an
    	// XML "Extender Character".
    	for (int i = 1; i < s.length(); ++i) {

    		char c = ca[i];
    		int ctype = Character.getType(c);

    		if (!Character.isLetterOrDigit(c) &&
                (".-_:".indexOf(c) == -1) &&
    		
                // Right type
    		    (!(ctype >= 6 && ctype <= 8 &&	
                      // Bad ranges, combined from the three types:
    				  !((c >= 0x06dd && c <= 0x06de) ||
      				  	(c >= 0x20dd && c <= 0x20e0) ||
      				   	 c >= 0x309b
    				   	)
    				  )
    			    ) &&
    		
    			  // XML Extender chars are all type 4 (uppercase) except
    			  // for two which are type 24. (titlecase modifier)

                  // Right type
    		      (!(ctype == 4 &&
                        // Bad ranges
    					!((c >= 0x02d0 && c <= 0x0559) ||
    				      (c >= 0x06e5 && c <= 0x06e6) ||
    					  (c >= 0x309b && c <= 0x309c)
    					 )
    				|| c == 0x00b7 // Type 24
    				|| c == 0x0387 // Type 24
    				))
                  ) {
    		
    		    return false;
            }
    		
    	}

    	// All characters passed the tests.
    	return true;
    	
    } // isXMLName(String):boolean

    //
    // Protected methods
    //

    /**
     * Uses the kidOK lookup table to check whether the proposed
     * tree structure is legal.
     */
    protected boolean isKidOK(Node parent, Node child) {
        if (allowGrammarAccess && parent.getNodeType() == Node.DOCUMENT_TYPE_NODE) {
            return child.getNodeType() == Node.ELEMENT_NODE;
        }
    	return 0 != (kidOK[parent.getNodeType()] & 1 << child.getNodeType());
    }

} // class DocumentImpl
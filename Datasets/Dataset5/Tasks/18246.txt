newattr.setValue(attr.getValue());

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
import org.w3c.dom.ranges.*;
import org.w3c.dom.events.*;
import org.apache.xerces.dom.events.*;
import org.apache.xerces.utils.XMLCharacterProperties;


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
 * create NodeIterators and TreeWalkers. The process of creating NodeIterator
 * objects also adds these references to this document.
 * After finishing with an iterator it is important to remove the object
 * using the remove methods in this implementation. This allows the release of
 * the references from the iterator objects to the DOM Nodes.
 * <p>
 * <b>Note:</b> When any node in the document is serialized, the
 * entire document is serialized along with it.
 *
 * @author Arnaud  Le Hors, IBM
 * @author Joe Kesselman, IBM
 * @author Andy Clark, IBM
 * @author Ralf Pfeiffer, IBM
 * @version
 * @since  PR-DOM-Level-1-19980818.
 */
public class DocumentImpl
    extends ParentNode
    implements Document, DocumentTraversal, DocumentEvent, DocumentRange {

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

    
    /**Experimental DOM Level 3 feature: Document encoding */
    protected String encoding;

    /**Experimental DOM Level 3 feature: Document version */
    protected String version;

    /**Experimental DOM Level 3 feature: Document standalone */
    protected boolean standalone;


    /** Identifiers. */
    protected Hashtable identifiers;

    /** Iterators */
    // REVISIT: Should this be transient? -Ac
    protected Vector iterators;

     /** Ranges */
    // REVISIT: Should this be transient? -Ac
    protected Vector ranges;
    
    /** Table for quick check of child insertion. */
    protected static int[] kidOK;

    /** Table for user data attached to this document nodes. */
    protected Hashtable userData;

    /** Table for event listeners registered to this document nodes. */
    protected Hashtable eventListeners;

    /**
     * Number of alterations made to this document since its creation.
     * Serves as a "dirty bit" so that live objects such as NodeList can
     * recognize when an alteration has been made and discard its cached
     * state information.
     * <p>
     * Any method that alters the tree structure MUST cause or be
     * accompanied by a call to changed(), to inform it that any outstanding
     * NodeLists may have to be updated.
     * <p>
     * (Required because NodeList is simultaneously "live" and integer-
     * indexed -- a bad decision in the DOM's design.)
     * <p>
     * Note that changes which do not affect the tree's structure -- changing
     * the node's name, for example -- do _not_ have to call changed().
     * <p>
     * Alternative implementation would be to use a cryptographic
     * Digest value rather than a count. This would have the advantage that
     * "harmless" changes (those producing equal() trees) would not force
     * NodeList to resynchronize. Disadvantage is that it's slightly more prone
     * to "false negatives", though that's the difference between "wildly
     * unlikely" and "absurdly unlikely". IF we start maintaining digests,
     * we should consider taking advantage of them.
     *
     * Note: This used to be done a node basis, so that we knew what
     * subtree changed. But since only DeepNodeList really use this today,
     * the gain appears to be really small compared to the cost of having
     * an int on every (parent) node plus having to walk up the tree all the
     * way to the root to mark the branch as changed everytime a node is
     * changed.
     * So we now have a single counter global to the document. It means that
     * some objects may flush their cache more often than necessary, but this
     * makes nodes smaller and only the document needs to be marked as changed.
     */
    protected int changes = 0;

    // experimental

    /** Allow grammar access. */
    protected boolean allowGrammarAccess;

    /** Bypass error checking. */
    protected boolean errorChecking = true;

    /** Bypass mutation events firing. */
    protected boolean mutationEvents = false;

    //
    // Static initialization
    //

    static {

        kidOK = new int[13];

        kidOK[DOCUMENT_NODE] =
            1 << ELEMENT_NODE | 1 << PROCESSING_INSTRUCTION_NODE |
            1 << COMMENT_NODE | 1 << DOCUMENT_TYPE_NODE;
			
        kidOK[DOCUMENT_FRAGMENT_NODE] =
        kidOK[ENTITY_NODE] =
        kidOK[ENTITY_REFERENCE_NODE] =
        kidOK[ELEMENT_NODE] =
            1 << ELEMENT_NODE | 1 << PROCESSING_INSTRUCTION_NODE |
            1 << COMMENT_NODE | 1 << TEXT_NODE |
            1 << CDATA_SECTION_NODE | 1 << ENTITY_REFERENCE_NODE ;
			
			
        kidOK[ATTRIBUTE_NODE] =
            1 << TEXT_NODE | 1 << ENTITY_REFERENCE_NODE;
			
        kidOK[DOCUMENT_TYPE_NODE] =
        kidOK[PROCESSING_INSTRUCTION_NODE] =
        kidOK[COMMENT_NODE] =
        kidOK[TEXT_NODE] =
        kidOK[CDATA_SECTION_NODE] =
        kidOK[NOTATION_NODE] =
            0;

    } // static

    //
    // Constructors
    //

    /**
     * NON-DOM: Actually creating a Document is outside the DOM's spec,
     * since it has to operate in terms of a particular implementation.
     */
    public DocumentImpl() {
        this(false);
        // make sure the XMLCharacterProperties class is initilialized
        XMLCharacterProperties.initCharFlags();
    }

    /** Experimental constructor. */
    public DocumentImpl(boolean grammarAccess) {
        super(null);
        ownerDocument = this;
        allowGrammarAccess = grammarAccess;
        // make sure the XMLCharacterProperties class is initilialized
        XMLCharacterProperties.initCharFlags();
    }

    // For DOM2: support.
    // The createDocument factory method is in DOMImplementation.
    public DocumentImpl(DocumentType doctype)
    {
        this(doctype, false);
        // make sure the XMLCharacterProperties class is initilialized
        XMLCharacterProperties.initCharFlags();
    }
    
    /** Experimental constructor. */
    public DocumentImpl(DocumentType doctype, boolean grammarAccess) {
        this(grammarAccess);
        this.docType = (DocumentTypeImpl)doctype;
        if (this.docType != null) {
            docType.ownerDocument = this;
        }
        // make sure the XMLCharacterProperties class is initilialized
        XMLCharacterProperties.initCharFlags();
    }

    //
    // Node methods
    //

    // even though ownerDocument refers to this in this implementation
    // the DOM Level 2 spec says it must be null, so make it appear so
    final public Document getOwnerDocument() {
        return null;
    }

    /** Returns the node type. */
    public short getNodeType() {
        return Node.DOCUMENT_NODE;
    }

    /** Returns the node name. */
    public String getNodeName() {
        return "#document";
    }

    /**
     * Deep-clone a document, including fixing ownerDoc for the cloned
     * children. Note that this requires bypassing the WRONG_DOCUMENT_ERR
     * protection. I've chosen to implement it by calling importNode
     * which is DOM Level 2.
     *
     * @return org.w3c.dom.Node
     * @param deep boolean, iff true replicate children
     */
    public Node cloneNode(boolean deep) {

        // clone the node itself
        DocumentImpl newdoc = new DocumentImpl();

        // then the children by importing them

        if (needsSyncChildren()) {
            synchronizeChildren();
        }

        if (deep) {
            Hashtable reversedIdentifiers = null;

            if (identifiers != null) {
                // Build a reverse mapping from element to identifier.
                reversedIdentifiers = new Hashtable();
                Enumeration elementIds = identifiers.keys();
                while (elementIds.hasMoreElements()) {
                    Object elementId = elementIds.nextElement();
                    reversedIdentifiers.put(identifiers.get(elementId), elementId);
                }
            }

            // Copy children into new document.
            for (ChildNode kid = firstChild; kid != null; kid = kid.nextSibling) {
                newdoc.appendChild(newdoc.importNode(kid, true, reversedIdentifiers));
            }
        }

        // experimental
        newdoc.allowGrammarAccess = allowGrammarAccess;
        newdoc.errorChecking = errorChecking;
        newdoc.mutationEvents = mutationEvents;

        // return new document
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
     *
     * REVISIT: According to the spec it is not allowed to alter neither the
     * document element nor the document type in any way
     */
    public Node insertBefore(Node newChild, Node refChild)
        throws DOMException {

    	// Only one such child permitted
        int type = newChild.getNodeType();
        if (errorChecking) {
            if((type == Node.ELEMENT_NODE && docElement != null) ||
               (type == Node.DOCUMENT_TYPE_NODE && docType != null)) {
                throw new DOMException(DOMException.HIERARCHY_REQUEST_ERR,
                                           "DOM006 Hierarchy request error");
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
     *
     * REVISIT: According to the spec it is not allowed to alter neither the
     * document element nor the document type in any way
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
     * Since we cache the docElement (and, currently, docType),
     * replaceChild has to update the cache
     *
     * REVISIT: According to the spec it is not allowed to alter neither the
     * document element nor the document type in any way
     */
    public Node replaceChild(Node newChild, Node oldChild)
        throws DOMException {
	
        super.replaceChild(newChild, oldChild);

        int type = oldChild.getNodeType();
        if(type == Node.ELEMENT_NODE) {
    	    docElement = (ElementImpl)newChild;
        }
        else if (type == Node.DOCUMENT_TYPE_NODE) {
    	    docType = (DocumentTypeImpl)newChild;
        }
        return oldChild;
    }   // replaceChild(Node,Node):Node

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
    		throw new DOMException(DOMException.INVALID_CHARACTER_ERR,
    		                           "DOM002 Illegal character");
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
            throw new DOMException(DOMException.INVALID_CHARACTER_ERR, 
                                   "DOM002 Illegal character");
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
            throw new DOMException(DOMException.INVALID_CHARACTER_ERR, 
                                   "DOM002 Illegal character");
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
    		throw new DOMException(DOMException.INVALID_CHARACTER_ERR,
    		                           "DOM002 Illegal character");
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
        if (needsSyncChildren()) {
            synchronizeChildren();
        }
        return docType;
    }


   /**
    * DOM Level 3 WD - Experimental.      
    * The encoding of this document (part of XML Declaration)     
    */
    public String getEncoding() {
	return encoding;
    }

    /**
      * DOM Level 3 WD - Experimental.
      * The version of this document (part of XML Declaration)     
      */
    public String getVersion() {
	return version;
    }

     /**
      * DOM Level 3 WD - Experimental.    
      * standalone that specifies whether this document is standalone (part of XML Declaration)     
      */
    public boolean getStandalone() {
        return standalone;
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
        if (needsSyncChildren()) {
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
      * DOM Level 3 WD - Experimental.
      * An attribute specifying, as part of the XML declaration, 
      * the encoding of this document. This is null when unspecified.
      */
    public void setEncoding(String value) {
        encoding = value;
    }

    /**
      * DOM Level 3 WD - Experimental.
      * version - An attribute specifying, as part of the XML declaration, 
      * the version number of this document. This is null when unspecified
      */
    public void setVersion(String value) {
       version = value;    
    }

    /**
      * DOM Level 3 WD - Experimental.
      * standalone - An attribute specifying, as part of the XML declaration, 
      * whether this document is standalone
      */
    public void setStandalone(boolean value) {
        standalone = value;
    } 
    

    /**
     * Returns true if the DOM implementation performs error checking.
     */
    public boolean getErrorChecking() {
        return errorChecking;
    }

    /** 
     * Sets whether the DOM implementation generates mutation events
     * upon operations.
     */
    public void setMutationEvents(boolean set) {
        mutationEvents = set;
    }

    /**
     * Returns true if the DOM implementation generates mutation events.
     */
    public boolean getMutationEvents() {
        return mutationEvents;
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
                                           String systemID)
        throws DOMException {

    	if (errorChecking && !isXMLName(qualifiedName)) {
            throw new DOMException(DOMException.INVALID_CHARACTER_ERR, 
                                   "DOM002 Illegal character");
        }
    	return new DocumentTypeImpl(this, qualifiedName, publicID, systemID);

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

    	if (errorChecking && !isXMLName(name)) {
    		throw new DOMException(DOMException.INVALID_CHARACTER_ERR, 
    		                           "DOM002 Illegal character");
        }
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

    	if (errorChecking && !isXMLName(name)) {
    		throw new DOMException(DOMException.INVALID_CHARACTER_ERR, 
    		                           "DOM002 Illegal character");
        }
    	return new NotationImpl(this, name);

    } // createNotation(String):Notation

    /**
     * NON-DOM Factory method: creates an element definition. Element
     * definitions hold default attribute values.
     */
    public ElementDefinitionImpl createElementDefinition(String name)
        throws DOMException {

    	if (errorChecking && !isXMLName(name)) {
    		throw new DOMException(DOMException.INVALID_CHARACTER_ERR, 
    		                           "DOM002 Illegal character");
        }
        return new ElementDefinitionImpl(this, name);

    } // createElementDefinition(String):ElementDefinitionImpl

    // other non-DOM methods

    /**
     * Copies a node from another document to this document. The new nodes are
     * created using this document's factory methods and are populated with the
     * data from the source's accessor methods defined by the DOM interfaces.
     * Its behavior is otherwise similar to that of cloneNode.
     * <p>
     * According to the DOM specifications, document nodes cannot be imported
     * and a NOT_SUPPORTED_ERR exception is thrown if attempted.
     */
    public Node importNode(Node source, boolean deep)
	throws DOMException {
        return importNode(source, deep, null);
    } // importNode(Node,boolean):Node

    /**
     * Overloaded implementation of DOM's importNode method. This method
     * provides the core functionality for the public importNode and cloneNode
     * methods.
     *
     * The reversedIdentifiers parameter is provided for cloneNode to
     * preserve the document's identifiers. The Hashtable has Elements as the
     * keys and their identifiers as the values. When an element is being
     * imported, a check is done for an associated identifier. If one exists,
     * the identifier is registered with the new, imported element. If
     * reversedIdentifiers is null, the parameter is not applied.
     */
    private Node importNode(Node source, boolean deep, Hashtable reversedIdentifiers)
	throws DOMException {
        Node newnode=null;

        // Sigh. This doesn't work; too many nodes have private data that
        // would have to be manually tweaked. May be able to add local
        // shortcuts to each nodetype. Consider ?????
        // if(source instanceof NodeImpl &&
        //  !(source instanceof DocumentImpl))
        // {
        //  // Can't clone DocumentImpl since it invokes us...
        //  newnode=(NodeImpl)source.cloneNode(false);
        //  newnode.ownerDocument=this;
        // }
        // else

        DOMImplementation  domImplementation     = 
                  source.getOwnerDocument().getImplementation(); // get source implementation
        boolean   domLevel20                     = 
                  domImplementation.hasFeature("XML", "2.0" ); //DOM Level 2.0 implementation


        int type                                 = source.getNodeType();

        switch (type) {
            case ELEMENT_NODE: {
                Element newElement;

                // Create element according to namespace support/qualification.
                if(domLevel20 == false || source.getLocalName() == null)
                    newElement = createElement(source.getNodeName());
                else
                    newElement = createElementNS(source.getNamespaceURI(), source.getNodeName());

                // Copy element's attributes, if any.
                NamedNodeMap sourceAttrs = source.getAttributes();
                if (sourceAttrs != null) {
                    int length = sourceAttrs.getLength();
                    for (int index = 0; index < length; index++) {
                        Attr attr = (Attr)sourceAttrs.item(index);

                        // Copy the attribute only if it is not a default.
                        if (attr.getSpecified()) {
                            Attr newAttr = (Attr)importNode(attr, true, reversedIdentifiers);

                            // Attach attribute according to namespace support/qualification.
                            if(domLevel20 == false || attr.getLocalName() == null)
                                newElement.setAttributeNode(newAttr);
                            else
                                newElement.setAttributeNodeNS(newAttr);
                        }
                    }
                }

                // Register element identifier.
                if (reversedIdentifiers != null) {
                    // Does element have an associated identifier?
                    Object elementId = reversedIdentifiers.get(source);
                    if (elementId != null) {
                        if (identifiers == null)
                            identifiers = new Hashtable();

                        identifiers.put(elementId, newElement);
                    }
                }

                newnode = newElement;
                break;
            }

            case ATTRIBUTE_NODE: {

                if( domLevel20 == true ){
                    if (source.getLocalName() == null) {
         	        newnode = createAttribute(source.getNodeName());
         	    } else {
          	        newnode = createAttributeNS(source.getNamespaceURI(),
                                                    source.getNodeName());
         	    }
                }
                else {
                    newnode = createAttribute(source.getNodeName());
                }
                // if source is an AttrImpl from this very same implementation
                // avoid creating the child nodes if possible
                if (source instanceof AttrImpl) {
                    AttrImpl attr = (AttrImpl) source;
                    if (attr.hasStringValue()) {
                        AttrImpl newattr = (AttrImpl) newnode;
                        newattr.setValue((String) attr.value);
                        deep = false;
                    }
                    else {
                        deep = true;
                    }
                }
                else {
                    // Kids carry value
                    deep = true;
                }
		break;
            }

	    case TEXT_NODE: {
		newnode = createTextNode(source.getNodeValue());
		break;
            }

	    case CDATA_SECTION_NODE: {
		newnode = createCDATASection(source.getNodeValue());
		break;
            }

    	    case ENTITY_REFERENCE_NODE: {
		newnode = createEntityReference(source.getNodeName());
                // allow deep import temporarily
                ((EntityReferenceImpl)newnode).isReadOnly(false);
		break;
            }

    	    case ENTITY_NODE: {
		Entity srcentity = (Entity)source;
		EntityImpl newentity =
		    (EntityImpl)createEntity(source.getNodeName());
		newentity.setPublicId(srcentity.getPublicId());
		newentity.setSystemId(srcentity.getSystemId());
		newentity.setNotationName(srcentity.getNotationName());
		// Kids carry additional value
                newentity.isReadOnly(false); // allow deep import temporarily
		newnode = newentity;
		break;
            }

    	    case PROCESSING_INSTRUCTION_NODE: {
		newnode = createProcessingInstruction(source.getNodeName(),
						      source.getNodeValue());
		break;
            }

    	    case COMMENT_NODE: {
		newnode = createComment(source.getNodeValue());
		break;
            }

            // REVISIT: The DOM specifications say that DocumentType nodes cannot be
            // imported. Is this OK?
    	    case DOCUMENT_TYPE_NODE: {
		DocumentType srcdoctype = (DocumentType)source;
		DocumentTypeImpl newdoctype = (DocumentTypeImpl)
		    createDocumentType(srcdoctype.getNodeName(),
				       srcdoctype.getPublicId(),
				       srcdoctype.getSystemId());
		// Values are on NamedNodeMaps
		NamedNodeMap smap = srcdoctype.getEntities();
		NamedNodeMap tmap = newdoctype.getEntities();
		if(smap != null) {
		    for(int i = 0; i < smap.getLength(); i++) {
			tmap.setNamedItem(importNode(smap.item(i), true, reversedIdentifiers));
                    }
                }
		smap = srcdoctype.getNotations();
		tmap = newdoctype.getNotations();
		if (smap != null) {
		    for(int i = 0; i < smap.getLength(); i++) {
			tmap.setNamedItem(importNode(smap.item(i), true, reversedIdentifiers));
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
		newnode = createDocumentFragment();
		// No name, kids carry value
		break;
            }

    	    case NOTATION_NODE: {
		Notation srcnotation = (Notation)source;
		NotationImpl newnotation =
		    (NotationImpl)createNotation(source.getNodeName());
		newnotation.setPublicId(srcnotation.getPublicId());
		newnotation.setSystemId(srcnotation.getSystemId());
		// Kids carry additional value
		newnode = newnotation;
		// No name, no value
		break;
            }

            case DOCUMENT_NODE : // Can't import document nodes
            default: {           // Unknown node type
                throw new DOMException(
                                       DOMException.NOT_SUPPORTED_ERR,
                                       "Node type being imported is not supported");
            }
        }

    	// If deep, replicate and attach the kids.
    	if (deep) {
	    for (Node srckid = source.getFirstChild();
                 srckid != null;
                 srckid = srckid.getNextSibling()) {
		newnode.appendChild(importNode(srckid, true, reversedIdentifiers));
	    }
        }
        if (newnode.getNodeType() == Node.ENTITY_REFERENCE_NODE
            || newnode.getNodeType() == Node.ENTITY_NODE) {
          ((NodeImpl)newnode).setReadOnly(true, true);
        }
    	return newnode;

    } // importNode(Node,boolean,Hashtable):Node

    /**
     * NON-DOM:
     * Change the node's ownerDocument, and its subtree, to this Document
     *
     * @param source The node to move in to this document.
     * @exception NOT_SUPPORTED_ERR DOMException, raised if the implementation
     * cannot handle the request, such as when the source node comes from a
     * different DOMImplementation
     * @see DocumentImpl.importNode
     **/
    public void adoptNode(Node source) {
	if (!(source instanceof NodeImpl)) {
	    throw new DOMException(DOMException.NOT_SUPPORTED_ERR,
		      "cannot move a node in from another DOM implementation");
	}
	Node parent = source.getParentNode();
	if (parent != null) {
	    parent.removeChild(source);
	}
	((NodeImpl)source).setOwnerDocument(this);
    }

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
            return;
        }

        if (needsSyncData()) {
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

        if (needsSyncData()) {
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

        if (needsSyncData()) {
            synchronizeData();
        }

        if (identifiers == null) {
            return;
        }

        identifiers.remove(idName);

    } // removeIdentifier(String)

    /** Returns an enumeration registered of identifier names. */
    public Enumeration getIdentifiers() {

        if (needsSyncData()) {
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
    	if (errorChecking && !isXMLName(qualifiedName)) {
            throw new DOMException(DOMException.INVALID_CHARACTER_ERR, 
                                   "DOM002 Illegal character");
        }
        return new ElementNSImpl( this, namespaceURI, qualifiedName);
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
    	if (errorChecking && !isXMLName(qualifiedName)) {
            throw new DOMException(DOMException.INVALID_CHARACTER_ERR, 
                                   "DOM002 Illegal character");
        }
        return new AttrNSImpl( this, namespaceURI, qualifiedName);
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
     * NON-DOM extension:
     * Create and return a NodeIterator. The NodeIterator is
     * added to a list of NodeIterators so that it can be
     * removed to free up the DOM Nodes it references.
     * @see #removeNodeIterator
     * @see #removeNodeIterators
     *
     * @param root The root of the iterator.
     * @param whatToShow The whatToShow mask.
     * @param filter The NodeFilter installed. Null means no filter.
     */
    public NodeIterator createNodeIterator(Node root,
                                           short whatToShow,
                                           NodeFilter filter)
    {                                           
        return createNodeIterator(root,whatToShow,filter,true);
    }    
     
    /**
     * Create and return a NodeIterator. The NodeIterator is
     * added to a list of NodeIterators so that it can be
     * removed to free up the DOM Nodes it references.
     * @see #removeNodeIterator
     * @see #removeNodeIterators
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
     * NON-DOM extension:
     * Create and return a TreeWalker.
     *
     * @param root The root of the iterator.
     * @param whatToShow The whatToShow mask.
     * @param filter The NodeFilter installed. Null means no filter.
     */
    public TreeWalker createTreeWalker(Node root,
                                       short whatToShow,
                                       NodeFilter filter)
    {
        return createTreeWalker(root,whatToShow,filter,true);
    }
    /**
     * Create and return a TreeWalker.
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
    	if (root==null) {
            throw new DOMException(
    			DOMException.NOT_SUPPORTED_ERR, 
			"DOM007 Not supported");
        }
        return new TreeWalkerImpl(root, whatToShow, filter,
                                  entityReferenceExpansion);
    }

    //
    // Not DOM Level 2. Support DocumentTraversal methods.
    //

    /** This is not called by the developer client. The 
     *  developer client uses the detach() function on the 
     *  NodeIterator itself. <p>
     *  
     *  This function is called from the NodeIterator#detach().
     */
     void removeNodeIterator(NodeIterator nodeIterator) {

        if (nodeIterator == null) return;
        if (iterators == null) return;

        iterators.removeElement(nodeIterator);
    }

    //
    // DocumentRange methods
    //
    /**
     */
    public Range createRange() {
        
        if (ranges == null) {
            ranges = new Vector();
        }

        Range range = new RangeImpl(this);
        
        ranges.addElement(range);

        return range;
        
    }
    
    /** Not a client function. Called by Range.detach(),
     *  so a Range can remove itself from the list of
     *  Ranges.
     */
    void removeRange(Range range) {

        if (range == null) return;
        if (ranges == null) return;

        ranges.removeElement(range);
    }
    
    /**
     * A method to be called when some text was changed in a text node,
     * so that live objects can be notified.
     */
    void replacedText(Node node) {
        // notify ranges
        if (ranges != null) {
            Enumeration enum = ranges.elements();
            while (enum.hasMoreElements()) {
                ((RangeImpl)enum.nextElement()).receiveReplacedText(node);
            }
        }
    }

    /**
     * A method to be called when some text was deleted from a text node,
     * so that live objects can be notified.
     */
    void deletedText(Node node, int offset, int count) {
        // notify ranges
        if (ranges != null) {
            Enumeration enum = ranges.elements();
            while (enum.hasMoreElements()) {
                ((RangeImpl)enum.nextElement()).receiveDeletedText(node,
                                                                   offset,
                                                                   count);
            }
        }
    }

    /**
     * A method to be called when some text was inserted into a text node,
     * so that live objects can be notified.
     */
    void insertedText(Node node, int offset, int count) {
        // notify ranges
        if (ranges != null) {
            Enumeration enum = ranges.elements();
            while (enum.hasMoreElements()) {
                ((RangeImpl)enum.nextElement()).receiveInsertedText(node,
                                                                    offset,
                                                                    count);
            }
        }
    }

    /**
     * A method to be called when a text node has been split,
     * so that live objects can be notified.
     */
    void splitData(Node node, Node newNode, int offset) {
        // notify ranges
        if (ranges != null) {
            Enumeration enum = ranges.elements();
            while (enum.hasMoreElements()) {
                ((RangeImpl)enum.nextElement()).receiveSplitData(node,
                                                                 newNode,
                                                                 offset);
            }
        }
    }

    /**
     * A method to be called when a node is removed from the tree so that live
     * objects can be notified.
     */
    void removedChildNode(Node oldChild) {

        // notify iterators
        if (iterators != null) {
            Enumeration enum = iterators.elements();
            while (enum.hasMoreElements()) {
                ((NodeIteratorImpl)enum.nextElement()).removeNode(oldChild);
            }
        }
        
        // notify ranges
        if (ranges != null) {
            Enumeration enum = ranges.elements();
            while (enum.hasMoreElements()) {
                ((RangeImpl)enum.nextElement()).removeNode(oldChild);
            }
        }
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
	 * @exception DOMException NOT_SUPPORTED_ERR if the requested
	 * event type is not supported in this DOM.
     * @since WD-DOM-Level-2-19990923
     */
    public Event createEvent(String type) 
	throws DOMException {
	    if("Event".equals(type))
	        return new EventImpl();
	    if("MutationEvent".equals(type))
	        return new MutationEventImpl();
	    else
	        throw new DOMException(DOMException.NOT_SUPPORTED_ERR,
					   "DOM007 Not supported");
	}
     
    //
    // Object methods
    //

    /** Clone. */
    public Object clone() throws CloneNotSupportedException {
        DocumentImpl newdoc = (DocumentImpl)super.clone();
        newdoc.docType = null;
        newdoc.docElement = null;
        return newdoc;
    }

    //
    // Public static methods
    //

    /**
     * Check the string against XML's definition of acceptable names for
     * elements and attributes and so on using the XMLCharacterProperties
     * utility class
     */
    public static boolean isXMLName(String s) {

        if (s == null) {
            return false;
        }
        return XMLCharacterProperties.validName(s);
    	
    } // isXMLName(String):boolean

    /**
     * Store user data related to a given node
     * This is a place where we could use weak references! Indeed, the node
     * here won't be GC'ed as long as some user data is attached to it, since
     * the userData table will have a reference to the node.
     */
    protected void setUserData(NodeImpl n, Object data) {
        if (userData == null) {
            userData = new Hashtable();
        }
        if (data == null) {
            userData.remove(n);
        } else {
            userData.put(n, data);
        }
    }

    /**
     * Retreive user data related to a given node
     */
    protected Object getUserData(NodeImpl n) {
        if (userData == null) {
            return null;
        }
        return userData.get(n);
    }

    /**
     * Store event listener registered on a given node
     * This is another place where we could use weak references! Indeed, the
     * node here won't be GC'ed as long as some listener is registered on it,
     * since the eventsListeners table will have a reference to the node.
     */
    protected void setEventListeners(NodeImpl n, Vector listeners) {
        if (eventListeners == null) {
            eventListeners = new Hashtable();
        }
        if (listeners == null) {
            eventListeners.remove(n);
            if (eventListeners.isEmpty()) {
                // stop firing events when there isn't any listener
                mutationEvents = false;
            }
        } else {
            eventListeners.put(n, listeners);
            // turn mutation events on
            mutationEvents = true;
        }
    }

    /**
     * Retreive event listener registered on a given node
     */
    protected Vector getEventListeners(NodeImpl n) {
        if (eventListeners == null) {
            return null;
        }
        return (Vector) eventListeners.get(n);
    }

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

    /**
     * Denotes that this node has changed.
     */
    protected void changed() {
        changes++;
    }

    /**
     * Returns the number of changes to this node.
     */
    protected int changes() {
        return changes;
    }

} // class DocumentImpl
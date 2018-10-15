protected final static boolean MUTATIONEVENTS=true;

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

import java.io.*;
import java.util.Vector;

import org.w3c.dom.*;

//import org.apache.xerces.domx.events.*;
import org.apache.xerces.dom.events.EventImpl;
import org.apache.xerces.dom.events.MutationEventImpl;
import org.w3c.dom.events.*;

/**
 * Node provides the basic structure of a DOM tree. It is never used
 * directly, but instead is subclassed to add type and data
 * information, and additional methods, appropriate to each node of
 * the tree. Only its subclasses should be instantiated -- and those,
 * with the exception of Document itself, only through a specific
 * Document's factory methods.
 * <P>
 * The Node interface provides shared behaviors such as siblings and
 * children, both for consistancy and so that the most common tree
 * operations may be performed without constantly having to downcast
 * to specific node types. When there is no obvious mapping for one of
 * these queries, it will respond with null.
 * Note that the default behavior is that children are forbidden. To
 * permit them, the subclass ParentNode overrides several methods.
 * <P>
 * NodeImpl also implements NodeList, so it can return itself in
 * response to the getChildNodes() query. This eliminiates the need
 * for a separate ChildNodeList object. Note that this is an
 * IMPLEMENTATION DETAIL; applications should _never_ assume that
 * this identity exists.
 * <P>
 * All nodes in a single document must originate
 * in that document. (Note that this is much tighter than "must be
 * same implementation") Nodes are all aware of their ownerDocument,
 * and attempts to mismatch will throw WRONG_DOCUMENT_ERR.
 * <P>
 * However, to save memory not all nodes always have a direct reference
 * to their ownerDocument. When a node is owned by another node it relies
 * on its owner to store its ownerDocument. Parent nodes always store it
 * though, so there is never more than one level of indirection.
 * And when a node doesn't have an owner, ownerNode refers to its
 * ownerDocument.
 *
 * @version
 * @since  PR-DOM-Level-1-19980818.
 */
public abstract class NodeImpl
    implements Node, NodeList, EventTarget, Cloneable, Serializable {

    //
    // Constants
    //

    /** Serialization version. */
    static final long serialVersionUID = -6316591992167219696L;

    // public

    /** Element definition node type. */
    public static final short ELEMENT_DEFINITION_NODE = -1;

    //
    // Data
    //

    // links

    protected NodeImpl ownerNode; // typically the parent but not always!

    // data

    protected short flags;

    protected final static short READONLY     = 0x1<<0;
    protected final static short SYNCDATA     = 0x1<<1;
    protected final static short SYNCCHILDREN = 0x1<<2;
    protected final static short OWNED        = 0x1<<3;
    protected final static short FIRSTCHILD   = 0x1<<4;
    protected final static short SPECIFIED    = 0x1<<5;
    protected final static short IGNORABLEWS  = 0x1<<6;
    protected final static short SETVALUE     = 0x1<<7;

    //
    // Constructors
    //

    /**
     * No public constructor; only subclasses of Node should be
     * instantiated, and those normally via a Document's factory methods
     * <p>
     * Every Node knows what Document it belongs to.
     */
    protected NodeImpl(DocumentImpl ownerDocument) {
        // as long as we do not have any owner, ownerNode is our ownerDocument
        ownerNode = ownerDocument;
    } // <init>(DocumentImpl)

    /** Constructor for serialization. */
    public NodeImpl() {}

    //
    // Node methods
    //

    /**
     * A short integer indicating what type of node this is. The named
     * constants for this value are defined in the org.w3c.dom.Node interface.
     */
    public abstract short getNodeType();

    /**
     * the name of this node.
     */
    public abstract String getNodeName();
    
    /**
     * Returns the node value.
     */
    public String getNodeValue() {
        return null;            // overridden in some subclasses
    }

    /**
     * Sets the node value.
     * @throws DOMException(NO_MODIFICATION_ALLOWED_ERR)
     */
    public void setNodeValue(String x) 
        throws DOMException {
        // Default behavior is to do nothing, overridden in some subclasses
    }

    /**
     * Adds a child node to the end of the list of children for this node.
     * Convenience shorthand for insertBefore(newChild,null).
     * @see #insertBefore(Node, Node)
     * <P>
     * By default we do not accept any children, ParentNode overrides this.
     * @see ParentNode
     *
     * @returns newChild, in its new state (relocated, or emptied in the
     * case of DocumentNode.)
     *
     * @throws DOMException(HIERARCHY_REQUEST_ERR) if newChild is of a
     * type that shouldn't be a child of this node.
     *
     * @throws DOMException(WRONG_DOCUMENT_ERR) if newChild has a
     * different owner document than we do.
     *
     * @throws DOMException(NO_MODIFICATION_ALLOWED_ERR) if this node is
     * read-only.
     */
    public Node appendChild(Node newChild) throws DOMException {
    	return insertBefore(newChild, null);
    }

    /**
     * Returns a duplicate of a given node. You can consider this a
     * generic "copy constructor" for nodes. The newly returned object should
     * be completely independent of the source object's subtree, so changes
     * in one after the clone has been made will not affect the other.
     * <P>
     * Note: since we never have any children deep is meaningless here,
     * ParentNode overrides this behavior.
     * @see ParentNode
     *
     * <p>
     * Example: Cloning a Text node will copy both the node and the text it
     * contains.
     * <p>
     * Example: Cloning something that has children -- Element or Attr, for
     * example -- will _not_ clone those children unless a "deep clone"
     * has been requested. A shallow clone of an Attr node will yield an
     * empty Attr of the same name.
     * <p>
     * NOTE: Clones will always be read/write, even if the node being cloned
     * is read-only, to permit applications using only the DOM API to obtain
     * editable copies of locked portions of the tree.
     */
    public Node cloneNode(boolean deep) {

        if (needsSyncData()) {
            synchronizeData();
	}
    	
    	NodeImpl newnode;
    	try {
            newnode = (NodeImpl)clone();
    	}
    	catch (CloneNotSupportedException e) {
//      Revisit : don't fail silently - but don't want to tie to parser guts
//            System.out.println("UNEXPECTED "+e);
            return null;
    	}
    	
        // Need to break the association w/ original kids
    	newnode.ownerNode      = ownerDocument();
        newnode.isOwned(false);

        // REVISIT: What to do when readOnly? -Ac
        newnode.isReadOnly(false);

    	return newnode;

    } // cloneNode(boolean):Node

    /**
     * Find the Document that this Node belongs to (the document in
     * whose context the Node was created). The Node may or may not
     * currently be part of that Document's actual contents.
     */
    public Document getOwnerDocument() {
        // if we have an owner simply forward the request
        // otherwise ownerNode is our ownerDocument
        if (isOwned()) {
            return ownerNode.ownerDocument();
        } else {
            return (Document) ownerNode;
        }
    }

    /**
     * same as above but returns internal type and this one is not overridden
     * by DocumentImpl to return null 
     */
    DocumentImpl ownerDocument() {
        // if we have an owner simply forward the request
        // otherwise ownerNode is our ownerDocument
        if (isOwned()) {
            return ownerNode.ownerDocument();
        } else {
            return (DocumentImpl) ownerNode;
        }
    }

    /**
     * NON-DOM
     * set the ownerDocument of this node
     */
    void setOwnerDocument(DocumentImpl doc) {
        if (needsSyncData()) {
            synchronizeData();
        }
        // if we have an owner we rely on it to have it right
        // otherwise ownerNode is our ownerDocument
	if (!isOwned()) {
            ownerNode = doc;
        }
    }

    /**
     * Obtain the DOM-tree parent of this node, or null if it is not
     * currently active in the DOM tree (perhaps because it has just been
     * created or removed). Note that Document, DocumentFragment, and
     * Attribute will never have parents.
     */
    public Node getParentNode() {
        return null;            // overriden by ChildNode
    }

    /*
     * same as above but returns internal type
     */
    NodeImpl parentNode() {
        return null;
    }

    /** The next child of this node's parent, or null if none */
    public Node getNextSibling() {
        return null;            // default behavior, overriden in ChildNode
    }

    /** The previous child of this node's parent, or null if none */
    public Node getPreviousSibling() {
        return null;            // default behavior, overriden in ChildNode
    }

    ChildNode previousSibling() {
        return null;            // default behavior, overriden in ChildNode
    }

    /**
     * Return the collection of attributes associated with this node,
     * or null if none. At this writing, Element is the only type of node
     * which will ever have attributes.
     *
     * @see ElementImpl
     */
    public NamedNodeMap getAttributes() {
    	return null; // overridden in ElementImpl
    }

    /**
     *  Returns whether this node (if it is an element) has any attributes.
     * @return <code>true</code> if this node has any attributes, 
     *   <code>false</code> otherwise.
     * @since DOM Level 2
     * @see ElementImpl
     */
    public boolean hasAttributes() {
        return false;           // overridden in ElementImpl
    }

    /**
     * Test whether this node has any children. Convenience shorthand
     * for (Node.getFirstChild()!=null)
     * <P>
     * By default we do not have any children, ParentNode overrides this.
     * @see ParentNode
     */
    public boolean hasChildNodes() {
        return false;
    }

    /**
     * Obtain a NodeList enumerating all children of this node. If there
     * are none, an (initially) empty NodeList is returned.
     * <p>
     * NodeLists are "live"; as children are added/removed the NodeList
     * will immediately reflect those changes. Also, the NodeList refers
     * to the actual nodes, so changes to those nodes made via the DOM tree
     * will be reflected in the NodeList and vice versa.
     * <p>
     * In this implementation, Nodes implement the NodeList interface and
     * provide their own getChildNodes() support. Other DOMs may solve this
     * differently.
     */
    public NodeList getChildNodes() {
        return this;
    }

    /** The first child of this Node, or null if none.
     * <P>
     * By default we do not have any children, ParentNode overrides this.
     * @see ParentNode
     */
    public Node getFirstChild() {
    	return null;
    }

    /** The first child of this Node, or null if none.
     * <P>
     * By default we do not have any children, ParentNode overrides this.
     * @see ParentNode
     */
    public Node getLastChild() {
	return null;
    }

    /**
     * Move one or more node(s) to our list of children. Note that this
     * implicitly removes them from their previous parent.
     * <P>
     * By default we do not accept any children, ParentNode overrides this.
     * @see ParentNode
     *
     * @param newChild The Node to be moved to our subtree. As a
     * convenience feature, inserting a DocumentNode will instead insert
     * all its children.
     *
     * @param refChild Current child which newChild should be placed
     * immediately before. If refChild is null, the insertion occurs
     * after all existing Nodes, like appendChild().
     *
     * @returns newChild, in its new state (relocated, or emptied in the
     * case of DocumentNode.)
     *
     * @throws DOMException(HIERARCHY_REQUEST_ERR) if newChild is of a
     * type that shouldn't be a child of this node, or if newChild is an
     * ancestor of this node.
     *
     * @throws DOMException(WRONG_DOCUMENT_ERR) if newChild has a
     * different owner document than we do.
     *
     * @throws DOMException(NOT_FOUND_ERR) if refChild is not a child of
     * this node.
     *
     * @throws DOMException(NO_MODIFICATION_ALLOWED_ERR) if this node is
     * read-only.
     */
    public Node insertBefore(Node newChild, Node refChild) 
	throws DOMException {
	throw new DOMExceptionImpl(DOMException.HIERARCHY_REQUEST_ERR, 
				   "DOM006 Hierarchy request error");
    }

    /**
     * Remove a child from this Node. The removed child's subtree
     * remains intact so it may be re-inserted elsewhere.
     * <P>
     * By default we do not have any children, ParentNode overrides this.
     * @see ParentNode
     *
     * @return oldChild, in its new state (removed).
     *
     * @throws DOMException(NOT_FOUND_ERR) if oldChild is not a child of
     * this node.
     *
     * @throws DOMException(NO_MODIFICATION_ALLOWED_ERR) if this node is
     * read-only.
     */
    public Node removeChild(Node oldChild) 
		throws DOMException {
	throw new DOMExceptionImpl(DOMException.NOT_FOUND_ERR, 
				   "DOM008 Not found");
    }

    /**
     * Make newChild occupy the location that oldChild used to
     * have. Note that newChild will first be removed from its previous
     * parent, if any. Equivalent to inserting newChild before oldChild,
     * then removing oldChild.
     * <P>
     * By default we do not have any children, ParentNode overrides this.
     * @see ParentNode
     *
     * @returns oldChild, in its new state (removed).
     *
     * @throws DOMException(HIERARCHY_REQUEST_ERR) if newChild is of a
     * type that shouldn't be a child of this node, or if newChild is
     * one of our ancestors.
     *
     * @throws DOMException(WRONG_DOCUMENT_ERR) if newChild has a
     * different owner document than we do.
     *
     * @throws DOMException(NOT_FOUND_ERR) if oldChild is not a child of
     * this node.
     *
     * @throws DOMException(NO_MODIFICATION_ALLOWED_ERR) if this node is
     * read-only.
     */
    public Node replaceChild(Node newChild, Node oldChild)
        throws DOMException {
	throw new DOMExceptionImpl(DOMException.HIERARCHY_REQUEST_ERR, 
				   "DOM006 Hierarchy request error");
    }

    //
    // NodeList methods
    //

    /**
     * NodeList method: Count the immediate children of this node
     * <P>
     * By default we do not have any children, ParentNode overrides this.
     * @see ParentNode
     *
     * @return int
     */
    public int getLength() {
	return 0;
    }

    /**
     * NodeList method: Return the Nth immediate child of this node, or
     * null if the index is out of bounds.
     * <P>
     * By default we do not have any children, ParentNode overrides this.
     * @see ParentNode
     *
     * @return org.w3c.dom.Node
     * @param Index int
     */
    public Node item(int index) {
	return null;
    }

    //
    // DOM2: methods, getters, setters
    //

    /**
     * Puts all <code>Text</code> nodes in the full depth of the sub-tree 
     * underneath this <code>Node</code>, including attribute nodes, into a 
     * "normal" form where only markup (e.g., tags, comments, processing 
     * instructions, CDATA sections, and entity references) separates 
     * <code>Text</code> nodes, i.e., there are no adjacent <code>Text</code> 
     * nodes.  This can be used to ensure that the DOM view of a document is 
     * the same as if it were saved and re-loaded, and is useful when 
     * operations (such as XPointer lookups) that depend on a particular 
     * document tree structure are to be used.In cases where the document 
     * contains <code>CDATASections</code>, the normalize operation alone may 
     * not be sufficient, since XPointers do not differentiate between 
     * <code>Text</code> nodes and <code>CDATASection</code> nodes.
     * <p>
     * Note that this implementation simply calls normalize() on this Node's
     * children. It is up to implementors or Node to override normalize()
     * to take action.
     */
    public void normalize() {
	/* by default we do not have any children,
	   ParentNode overrides this behavior */
    }

    /**
     * Introduced in DOM Level 2. <p>
     * Tests whether the DOM implementation implements a specific feature and that
     * feature is supported by this node.
     * @param feature       The package name of the feature to test. This is the
     *                      same name as what can be passed to the method
     *                      hasFeature on DOMImplementation.
     * @param version       This is the version number of the package name to
     *                      test. In Level 2, version 1, this is the string "2.0". If
     *                      the version is not specified, supporting any version of
     *                      the feature will cause the method to return true.
     * @return boolean      Returns true if this node defines a subtree within which the
     *                      specified feature is supported, false otherwise.
     * @since WD-DOM-Level-2-19990923
     */
    public boolean supports(String feature, String version)
    {
        return ownerDocument().getImplementation().hasFeature(feature,
                                                              version);
    }

    /**
     * Introduced in DOM Level 2. <p>
     *
     * The namespace URI of this node, or null if it is unspecified. When this node
     * is of any type other than ELEMENT_NODE and ATTRIBUTE_NODE, this is always
     * null and setting it has no effect. <p>
     *
     * This is not a computed value that is the result of a namespace lookup based on
     * an examination of the namespace declarations in scope. It is merely the
     * namespace URI given at creation time.<p>
     *
     * For nodes created with a DOM Level 1 method, such as createElement
     * from the Document interface, this is null.
     * @since WD-DOM-Level-2-19990923
     * @see AttrNSImpl
     * @see ElementNSImpl
     */
    public String getNamespaceURI()
    {
        return null;
    }

    /**
     * Introduced in DOM Level 2. <p>
     *
     * The namespace prefix of this node, or null if it is unspecified. When this
     * node is of any type other than ELEMENT_NODE and ATTRIBUTE_NODE this is
     * always null and setting it has no effect.<p>
     *
     * For nodes created with a DOM Level 1 method, such as createElement
     * from the Document interface, this is null. <p>
     *
     * @since WD-DOM-Level-2-19990923
     * @see AttrNSImpl
     * @see ElementNSImpl
     */
    public String getPrefix()
    {
        return null;
    }

    /**
     *  Introduced in DOM Level 2. <p>
     *
     *  The namespace prefix of this node, or null if it is unspecified. When this
     *  node is of any type other than ELEMENT_NODE and ATTRIBUTE_NODE this is
     *  always null and setting it has no effect.<p>
     *
     *  For nodes created with a DOM Level 1 method, such as createElement
     *  from the Document interface, this is null.<p>
     *
     *  Note that setting this attribute changes the nodeName attribute, which holds the
     *  qualified name, as well as the tagName and name attributes of the Element
     *  and Attr interfaces, when applicable.<p>
     *
     * @throws INVALID_CHARACTER_ERR Raised if the specified
     *  prefix contains an invalid character.
     *
     * @since WD-DOM-Level-2-19990923
     * @see AttrNSImpl
     * @see ElementNSImpl
     */
    public void setPrefix(String prefix)
        throws DOMException
    {
	throw new DOMExceptionImpl(DOMException.NAMESPACE_ERR, 
				   "DOM003 Namespace error");
    }

    /**
     * Introduced in DOM Level 2. <p>
     *
     * Returns the local part of the qualified name of this node.
     * For nodes created with a DOM Level 1 method, such as createElement
     * from the Document interface, and for nodes of any type other than
     * ELEMENT_NODE and ATTRIBUTE_NODE this is the same as the nodeName
     * attribute.
     * @since WD-DOM-Level-2-19990923
     * @see AttrNSImpl
     * @see ElementNSImpl
     */
    public String             getLocalName()
    {
        return null;
    }
    
    
    //
    // EventTarget support (public and internal)
    //
	// Constants
	//
	/** Compile-time flag. If false, disables our code for
	    the DOM Level 2 Events module, perhaps allowing it
	    to be optimized out to save bytecodes.
	*/
	protected final static boolean MUTATIONEVENTS=false;
	
	/** The MUTATION_ values are parameters to the NON-DOM 
	    internalInsertBefore() and internalRemoveChild() operations,
	    allowing us to control which MutationEvents are generated.
	 */
	protected final static int MUTATION_NONE=0x00;
	protected final static int MUTATION_LOCAL=0x01;
	protected final static int MUTATION_AGGREGATE=0x02;
	protected final static int MUTATION_ALL=0xffff;
	/** NON-DOM INTERNAL: EventListeners currently registered at
	 * THIS NODE; preferably null if none.
	 */
    Vector nodeListeners=null;
	
	/* NON-DOM INTERNAL: Class LEntry is just a struct used to represent
	 * event listeners registered with this node. Copies of this object
	 * are hung from the nodeListeners Vector.
	 * <p>
	 * I considered using two vectors -- one for capture,
	 * one for bubble -- but decided that since the list of listeners 
	 * is probably short in most cases, it might not be worth spending
	 * the space. ***** REVISIT WHEN WE HAVE MORE EXPERIENCE.
	 */
	class LEntry
	{
	    String type;
	    EventListener listener;
	    boolean useCapture;
	    
	    /** NON-DOM INTERNAL: Constructor for Listener list Entry 
	     * @param type Event name (NOT event group!) to listen for.
	     * @param listener Who gets called when event is dispatched
	     * @param useCaptue True iff listener is registered on
	     *  capturing phase rather than at-target or bubbling
	     */
	    LEntry(String type,EventListener listener,boolean useCapture)
	    {
	        this.type=type;this.listener=listener;this.useCapture=useCapture;
	    }
	}; // LEntry
	
	/** Introduced in DOM Level 2. <p>
     * Register an event listener with this Node. A listener may be independently
     * registered as both Capturing and Bubbling, but may only be
     * registered once per role; redundant registrations are ignored.
     * @param type Event name (NOT event group!) to listen for.
	 * @param listener Who gets called when event is dispatched
	 * @param useCapture True iff listener is registered on
	 *  capturing phase rather than at-target or bubbling
	 */
	public void addEventListener(String type,EventListener listener,boolean useCapture)
	{
        // We can't dispatch to blank type-name, and of course we need
        // a listener to dispatch to
	    if(type==null || type.equals("") || listener==null)
	        return;

	    // Each listener may be registered only once per type per phase.
	    // Simplest way to code that is to zap the previous entry, if any.
	    removeEventListener(type,listener,useCapture);
	    
	    if(nodeListeners==null) nodeListeners=new Vector();
	    nodeListeners.addElement(new LEntry(type,listener,useCapture));
	    
	    // Record active listener
	    LCount lc=LCount.lookup(type);
	    if(useCapture)
	        ++lc.captures;
	    else
	        ++lc.bubbles;
	} // addEventListener(String,EventListener,boolean) :void
	
	/** Introduced in DOM Level 2. <p>
     * Deregister an event listener previously registered with this Node. 
     * A listener must be independently removed from the 
     * Capturing and Bubbling roles. Redundant removals (of
     * listeners not currently registered for this role) are ignored.
     * @param type Event name (NOT event group!) to listen for.
	 * @param listener Who gets called when event is dispatched
	 * @param useCapture True iff listener is registered on
	 *  capturing phase rather than at-target or bubbling
	 */
	public void removeEventListener(String type,EventListener listener,boolean useCapture)
	{
	    // If this couldn't be a valid listener registration, ignore request
  	    if(nodeListeners==null || type==null || type.equals("") || listener==null)
	        return;

        // Note that addListener has previously ensured that 
	    // each listener may be registered only once per type per phase.
        for(int i=nodeListeners.size()-1;i>=0;--i) // count-down is OK for deletions!
        {
            LEntry le=(LEntry)(nodeListeners.elementAt(i));
            if(le.useCapture==useCapture && le.listener==listener && 
                le.type.equals(type))
            {
                nodeListeners.removeElementAt(i);
                // Storage management: Discard empty listener lists
                if(nodeListeners.size()==0) nodeListeners=null;

	            // Remove active listener
	            LCount lc=LCount.lookup(type);
        	    if(useCapture)
	                --lc.captures;
        	    else
	                --lc.bubbles;
	                
                break;  // Found it; no need to loop farther.
            }
        }
	} // removeEventListener(String,EventListener,boolean) :void
	
	/** NON-DOM INTERNAL:
	    A finalizer has added to NodeImpl in order to correct the event-usage
	    counts of any remaining listeners before discarding the Node.
	    This isn't absolutely required, and finalizers are of dubious
	    reliability and have odd effects on some implementations of GC.
	    But given the expense of event generation and distribution it 
	    seems a worthwhile safety net.
	    ***** RECONSIDER at some future point.
	   */
	protected void finalize() throws Throwable
	{
	    super.finalize();
	    if(nodeListeners!=null)
            for(int i=nodeListeners.size()-1;i>=0;--i) // count-down is OK for deletions!
            {
                LEntry le=(LEntry)(nodeListeners.elementAt(i));
                LCount lc=LCount.lookup(le.type);
           	    if(le.useCapture)
	                --lc.captures;
                else
	                --lc.bubbles;
	        }
	}	

    /**
     * Introduced in DOM Level 2. <p>
     * Distribution engine for DOM Level 2 Events. 
     * <p>
     * Event propagation runs as follows:
     * <ol>
     * <li>Event is dispatched to a particular target node, which invokes
     *   this code. Note that the event's stopPropagation flag is
     *   cleared when dispatch begins; thereafter, if it has 
     *   been set before processing of a node commences, we instead
     *   immediately advance to the DEFAULT phase.
     * <li>The node's ancestors are established as destinations for events.
     *   For capture and bubble purposes, node ancestry is determined at 
     *   the time dispatch starts. If an event handler alters the document 
     *   tree, that does not change which nodes will be informed of the event. 
     * <li>CAPTURING_PHASE: Ancestors are scanned, root to target, for 
     *   Capturing listeners. If found, they are invoked (see below). 
     * <li>AT_TARGET: 
     *   Event is dispatched to NON-CAPTURING listeners on the
     *   target node. Note that capturing listeners on this node are _not_
     *   invoked.
     * <li>BUBBLING_PHASE: Ancestors are scanned, target to root, for
     *   non-capturing listeners. 
     * <li>Default processing: Some DOMs have default behaviors bound to specific
     *   nodes. If this DOM does, and if the event's preventDefault flag has
     *   not been set, we now return to the target node and process its
     *   default handler for this event, if any.
     * </ol>
     * <p>
     * Note that (de)registration of handlers during
     * processing of an event does not take effect during
     * this phase of this event; they will not be called until
     * the next time this node is visited by dispatchEvent.
     * <p>
     * If an event handler itself causes events to be dispatched, they are
     * processed synchronously, before processing resumes
     * on the event which triggered them. Please be aware that this may 
     * result in events arriving at listeners "out of order" relative
     * to the actual sequence of requests.
     * <p>
     * Note that our implementation resets the event's stop/prevent flags
     * when dispatch begins.
     * I believe the DOM's intent is that event objects be redispatchable,
     * though it isn't stated in those terms.
     * @param event the event object to be dispatched to 
     * registered EventListeners
     * @return true if the event's <code>preventDefault()</code>
     * method was invoked by an EventListener; otherwise false.
    */
	public boolean dispatchEvent(Event event)
    {
        if(event==null) return false;
        
        // Can't use anyone else's implementation, since there's no public
        // API for setting the event's processing-state fields.
        EventImpl evt=(EventImpl)event;

        // VALIDATE -- must have been initialized at least once, must have
        // a non-null non-blank name.
        if(!evt.initialized || evt.type==null || evt.type.equals(""))
            throw new DOMExceptionImpl(DOMExceptionImpl.UNSPECIFIED_EVENT_TYPE,
				       "DOM010 Unspecified event type");
        
        // If nobody is listening for this event, discard immediately
        LCount lc=LCount.lookup(evt.getType());
        if(lc.captures+lc.bubbles+lc.defaults==0)
            return evt.preventDefault;

        // INITIALIZE THE EVENT'S DISPATCH STATUS
        // (Note that Event objects are reusable in our implementation;
        // that doesn't seem to be explicitly guaranteed in the DOM, but
        // I believe it is the intent.)
        evt.target=this;
        evt.stopPropagation=false;
        evt.preventDefault=false;
        
        // Capture pre-event parentage chain, not including target;
        // use pre-event-dispatch ancestors even if event handlers mutate
        // document and change the target's context.
        // Note that this is parents ONLY; events do not
        // cross the Attr/Element "blood/brain barrier". 
        // DOMAttrModified. which looks like an exception,
        // is issued to the Element rather than the Attr
        // and causes a _second_ DOMSubtreeModified in the Element's
        // tree.
        Vector pv=new Vector(10,10);
        Node p=this,n=p.getParentNode();
        while(n!=null)
        {
            pv.addElement(n);
            p=n;
            n=n.getParentNode();
        }
        
        //CAPTURING_PHASE:
        if(lc.captures>0)
        {
            evt.eventPhase=Event.CAPTURING_PHASE;
            //Ancestors are scanned, root to target, for 
            //Capturing listeners.
            for(int j=pv.size()-1;j>=0;--j)
            {
                if(evt.stopPropagation)
                    break;  // Someone set the flag. Phase ends.
                    
                // Handle all capturing listeners on this node
                NodeImpl nn=(NodeImpl)pv.elementAt(j);
                evt.currentNode=nn;
                if(nn.nodeListeners!=null)
                {
                    Vector nl=(Vector)(nn.nodeListeners.clone());
                    for(int i=nl.size()-1;i>=0;--i) // count-down more efficient
                    {
	                    LEntry le=(LEntry)(nl.elementAt(i));
                        if(le.useCapture && le.type.equals(evt.type))
                            try
                            {
    	                        le.listener.handleEvent(evt);
	                        }
	                        catch(Exception e)
	                        {
	                            // All exceptions are ignored.
	                        }
	                }
	            }
            }
        }
        
        //Both AT_TARGET and BUBBLE use non-capturing listeners.
        if(lc.bubbles>0)
        {
            //AT_TARGET PHASE: Event is dispatched to NON-CAPTURING listeners
            //on the target node. Note that capturing listeners on the target node 
            //are _not_ invoked, even during the capture phase.
            evt.eventPhase=Event.AT_TARGET;
            evt.currentNode=this;
            if(!evt.stopPropagation && nodeListeners!=null)
            {
                Vector nl=(Vector)nodeListeners.clone();
                for(int i=nl.size()-1;i>=0;--i) // count-down is more efficient
                {
                    LEntry le=(LEntry)nl.elementAt(i);
       	            if(le!=null && !le.useCapture && le.type.equals(evt.type))
   	                    try
   	                    {
                            le.listener.handleEvent(evt);
                        }
                        catch(Exception e)
                        {
                            // All exceptions are ignored.
                        }
	            }
            }
            //BUBBLING_PHASE: Ancestors are scanned, target to root, for
            //non-capturing listeners. If the event's preventBubbling flag has
            //been set before processing of a node commences, we instead
            //immediately advance to the default phase.
            //Note that not all events bubble.
            if(evt.bubbles) 
            {
                evt.eventPhase=Event.BUBBLING_PHASE;
                for(int j=0;j<pv.size();++j)
                {
                    if(evt.stopPropagation)
                        break;  // Someone set the flag. Phase ends.
                    
                    // Handle all bubbling listeners on this node
                    NodeImpl nn=(NodeImpl)pv.elementAt(j);
                    evt.currentNode=nn;
                    if(nn.nodeListeners!=null)
                    {
                        Vector nl=(Vector)(nn.nodeListeners.clone());
                        for(int i=nl.size()-1;i>=0;--i) // count-down more efficient
    	                {
	                        LEntry le=(LEntry)(nl.elementAt(i));
    	                    if(!le.useCapture && le.type.equals(evt.type))
            	                try
            	                {
	                                le.listener.handleEvent(evt);
	                            }
	                            catch(Exception e)
	                            {
	                                // All exceptions are ignored.
	                            }
	                    }
	                }
                }
            }
        }
        
        //DEFAULT PHASE: Some DOMs have default behaviors bound to specific
        //nodes. If this DOM does, and if the event's preventDefault flag has
        //not been set, we now return to the target node and process its
        //default handler for this event, if any.
        // No specific phase value defined, since this is DOM-internal
        if(lc.defaults>0 && (!evt.cancelable || !evt.preventDefault))
        {
            // evt.eventPhase=Event.DEFAULT_PHASE;
            // evt.currentNode=this;
            // DO_DEFAULT_OPERATION
        }

        return evt.preventDefault;        
    } // dispatchEvent(Event) :boolean


    /** NON-DOM INTERNAL: DOMNodeInsertedIntoDocument and ...RemovedFrom...
     * are dispatched to an entire subtree. This is the distribution code
     * therefor. They DO NOT bubble, thanks be, but may be captured.
     * <p>
     * ***** At the moment I'm being sloppy and using the normal
     * capture dispatcher on every node. This could be optimized hugely
     * by writing a capture engine that tracks our position in the tree to
     * update the capture chain without repeated chases up to root.
     * @param n node which was directly inserted or removed
     * @param e event to be sent to that node and its subtree
     */
    void dispatchEventToSubtree(ChildNode n,Event e)
    {
      if(MUTATIONEVENTS)
      {
	    if(nodeListeners==null || n==null)
            return;

	    // ***** Recursive implementation. This is excessively expensive,
	    // and should be replaced in conjunction with optimization
	    // mentioned above.
	    n.dispatchEvent(e);
	    if(n.getNodeType()==Node.ELEMENT_NODE)
	    {
	        NamedNodeMap a=n.getAttributes();
	        for(int i=a.getLength()-1;i>=0;--i)
	            dispatchEventToSubtree(((ChildNode)a.item(i)),e);
	    }
	    dispatchEventToSubtree((ChildNode)n.getFirstChild(),e);
	    dispatchEventToSubtree(n.nextSibling,e);
	  }
	} // dispatchEventToSubtree(NodeImpl,Event) :void

    /** NON-DOM INTERNAL: Return object for getEnclosingAttr. Carries
     * (two values, the Attr node affected (if any) and its previous 
     * string value. Simple struct, no methods.
     */
	class EnclosingAttr
	{
	    AttrImpl node;
	    String oldvalue;
	} //EnclosingAttr
	
	/** NON-DOM INTERNAL: Pre-mutation context check, in
	 * preparation for later generating DOMAttrModified events.
	 * Determines whether this node is within an Attr
	 * @return either a description of that Attr, or Null
	 * if none such. 
	 */
	EnclosingAttr getEnclosingAttr()
	{
      if(MUTATIONEVENTS)
      {
        NodeImpl eventAncestor=this;
        while(true)
        {
            if(eventAncestor==null)
                return null;
            int type=eventAncestor.getNodeType();
            if(type==Node.ATTRIBUTE_NODE)
            {
                EnclosingAttr retval=new EnclosingAttr();
                retval.node=(AttrImpl)eventAncestor;
                retval.oldvalue=retval.node.getNodeValue();
                return retval;
            }    
            else if(type==Node.ENTITY_REFERENCE_NODE)
                eventAncestor=eventAncestor.parentNode();
            else 
                return null;
                // Any other parent means we're not in an Attr
        }
      }
      return null; // Safety net, should never be reached
	} // getEnclosingAttr() :EnclosingAttr 

	
	/** NON-DOM INTERNAL: Convenience wrapper for calling
	 * dispatchAggregateEvents when the context was established
	 * by <code>getEnclosingAttr</code>.
	 * @param ea description of Attr affected by current operation
	 */
	void dispatchAggregateEvents(EnclosingAttr ea)
	{
	    if(ea!=null)
	        dispatchAggregateEvents(ea.node,ea.oldvalue);
        else
	        dispatchAggregateEvents(null,null);
	        
	} // dispatchAggregateEvents(EnclosingAttr) :void

	/** NON-DOM INTERNAL: Generate the "aggregated" post-mutation events
	 * DOMAttrModified and DOMSubtreeModified.
	 * Both of these should be issued only once for each user-requested
	 * mutation operation, even if that involves multiple changes to
	 * the DOM.
	 * For example, if a DOM operation makes multiple changes to a single
	 * Attr before returning, it would be nice to generate only one 
	 * DOMAttrModified, and multiple changes over larger scope but within
	 * a recognizable single subtree might want to generate only one 
	 * DOMSubtreeModified, sent to their lowest common ancestor. 
	 * <p>
	 * To manage this, use the "internal" versions of insert and remove
	 * with MUTATION_LOCAL, then make an explicit call to this routine
	 * at the higher level. Some examples now exist in our code.
	 *
	 * @param enclosingAttr The Attr node (if any) whose value has
	 * been changed as a result of the DOM operation. Null if none such.
	 * @param oldValue The String value previously held by the
	 * enclosingAttr. Ignored if none such.
	 */
	void dispatchAggregateEvents(AttrImpl enclosingAttr,String oldvalue)
	{
      if(MUTATIONEVENTS)
      {
	    if(nodeListeners==null)
            return;

	    // If we have to send DOMAttrModified (determined earlier),
	    // do so.
	    NodeImpl owner=null;
	    if(enclosingAttr!=null)
	    {
            LCount lc=LCount.lookup(MutationEventImpl.DOM_ATTR_MODIFIED);
	        if(lc.captures+lc.bubbles+lc.defaults>0)
	        {
                owner=((NodeImpl)(enclosingAttr.getOwnerElement()));
                if(owner!=null)
                {
                    MutationEvent me=
                        new MutationEventImpl();
                    //?????ownerDocument.createEvent("MutationEvents");
                    me.initMutationEvent(MutationEventImpl.DOM_ATTR_MODIFIED,true,false,
                       null,oldvalue,enclosingAttr.getNodeValue(),enclosingAttr.getNodeName());
                    owner.dispatchEvent(me);
                }
            }
        }
    
        // DOMSubtreeModified gets sent to the lowest common root of a
        // set of changes. 
        // "This event is dispatched after all other events caused by the
        // mutation have been fired."
        LCount lc=LCount.lookup(MutationEventImpl.DOM_SUBTREE_MODIFIED);
        if(lc.captures+lc.bubbles+lc.defaults>0)
        {
            MutationEvent me=
                    new MutationEventImpl();
                //?????ownerDocument.createEvent("MutationEvents");
            me.initMutationEvent(MutationEventImpl.DOM_SUBTREE_MODIFIED,true,false,
               null,null,null,null);
            
            
            // If we're within an Attr, DStM gets sent to the Attr
            // and to its owningElement. Otherwise we dispatch it
            // locally.
    	    if(enclosingAttr!=null)
    	    {
    	        enclosingAttr.dispatchEvent(me);
    	        if(owner!=null)
    	            owner.dispatchEvent(me);
    	    }
            else
                dispatchEvent(me);
        }
      }
	} //dispatchAggregateEvents(AttrImpl,String) :void


    //
    // Public methods
    //

    /**
     * NON-DOM: PR-DOM-Level-1-19980818 mentions readonly nodes in conjunction
     * with Entities, but provides no API to support this.
     * <P>
     * Most DOM users should not touch this method. Its anticpated use
     * is during construction of EntityRefernces, where it will be used to
     * lock the contents replicated from Entity so they can't be casually
     * altered. It _could_ be published as a DOM extension, if desired.
     * <P>
     * Note: since we never have any children deep is meaningless here,
     * ParentNode overrides this behavior.
     * @see ParentNode
     *
     * @param readOnly True or false as desired.
     * @param deep If true, children are also toggled. Note that this will
     *	not change the state of an EntityReference or its children,
     *  which are always read-only.
     */
    public void setReadOnly(boolean readOnly, boolean deep) {

        if (needsSyncData()) {
            synchronizeData();
        }
    	isReadOnly(readOnly);

    } // setReadOnly(boolean,boolean)

    /**
     * NON-DOM: Returns true if this node is read-only. This is a
     * shallow check.
     */
    public boolean getReadOnly() {

        if (needsSyncData()) {
            synchronizeData();
        }
        return isReadOnly();

    } // getReadOnly():boolean

    /**
     * NON-DOM: As an alternative to subclassing the DOM, this implementation
     * has been extended with the ability to attach an object to each node.
     * (If you need multiple objects, you can attach a collection such as a
     * vector or hashtable, then attach your application information to that.)
     * <p><b>Important Note:</b> You are responsible for removing references
     * to your data on nodes that are no longer used. Failure to do so will
     * prevent the nodes, your data is attached to, to be garbage collected
     * until the whole document is.
     *
     * @param data the object to store or null to remove any existing reference
     */
    public void setUserData(Object data) {
        ownerDocument().setUserData(this, data);
    }

    /**
     * NON-DOM:
     * Returns the user data associated to this node.
     */
    public Object getUserData() {
        return ownerDocument().getUserData(this);
    }

    //
    // Protected methods
    //

    /**
     * Denotes that this node has changed.
     */
    protected void changed() {
        // we do not actually store this information on every node, we only
        // have a global indicator on the Document. Doing otherwise cost us too
        // much for little gain.
        ownerDocument().changed();
    }

    /**
     * Returns the number of changes to this node.
     */
    protected int changes() {
        // we do not actually store this information on every node, we only
        // have a global indicator on the Document. Doing otherwise cost us too
        // much for little gain.
        return ownerDocument().changes();
    }

    /**
     * Override this method in subclass to hook in efficient
     * internal data structure.
     */
    protected void synchronizeData() {
        // By default just change the flag to avoid calling this method again
        needsSyncData(false);
    }


    /*
     * Flags setters and getters
     */

    final boolean isReadOnly() {
        return (flags & READONLY) != 0;
    }

    final void isReadOnly(boolean value) {
        flags = (short) (value ? flags | READONLY : flags & ~READONLY);
    }

    final boolean needsSyncData() {
        return (flags & SYNCDATA) != 0;
    }

    final void needsSyncData(boolean value) {
        flags = (short) (value ? flags | SYNCDATA : flags & ~SYNCDATA);
    }

    final boolean needsSyncChildren() {
        return (flags & SYNCCHILDREN) != 0;
    }

    final void needsSyncChildren(boolean value) {
        flags = (short) (value ? flags | SYNCCHILDREN : flags & ~SYNCCHILDREN);
    }

    final boolean isOwned() {
        return (flags & OWNED) != 0;
    }

    final void isOwned(boolean value) {
        flags = (short) (value ? flags | OWNED : flags & ~OWNED);
    }

    final boolean isFirstChild() {
        return (flags & FIRSTCHILD) != 0;
    }

    final void isFirstChild(boolean value) {
        flags = (short) (value ? flags | FIRSTCHILD : flags & ~FIRSTCHILD);
    }

    final boolean isSpecified() {
        return (flags & SPECIFIED) != 0;
    }

    final void isSpecified(boolean value) {
        flags = (short) (value ? flags | SPECIFIED : flags & ~SPECIFIED);
    }

    // inconsistent name to avoid clash with public method on TextImpl
    final boolean internalIsIgnorableWhitespace() {
        return (flags & IGNORABLEWS) != 0;
    }

    final void isIgnorableWhitespace(boolean value) {
        flags = (short) (value ? flags | IGNORABLEWS : flags & ~IGNORABLEWS);
    }

    final boolean setValueCalled() {
        return (flags & SETVALUE) != 0;
    }

    final void setValueCalled(boolean value) {
        flags = (short) (value ? flags | SETVALUE : flags & ~SETVALUE);
    }

    //
    // Object methods
    //

    /** NON-DOM method for debugging convenience. */
    public String toString() {
        return "["+getNodeName()+": "+getNodeValue()+"]";
    }

    //
    // Serialization methods
    //

    /** Serialize object. */
    private void writeObject(ObjectOutputStream out) throws IOException {

        // synchronize data
        if (needsSyncData()) {
            synchronizeData();
        }
        // write object
        out.defaultWriteObject();

    } // writeObject(ObjectOutputStream)

} // class NodeImpl
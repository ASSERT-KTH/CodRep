for (ChildNode child = (ChildNode) value;

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

import org.w3c.dom.*;
import org.w3c.dom.events.MutationEvent;
import org.apache.xerces.dom.events.MutationEventImpl;

/**
 * Attribute represents an XML-style attribute of an
 * Element. Typically, the allowable values are controlled by its
 * declaration in the Document Type Definition (DTD) governing this
 * kind of document.
 * <P>
 * If the attribute has not been explicitly assigned a value, but has
 * been declared in the DTD, it will exist and have that default. Only
 * if neither the document nor the DTD specifies a value will the
 * Attribute really be considered absent and have no value; in that
 * case, querying the attribute will return null.
 * <P>
 * Attributes may have multiple children that contain their data. (XML
 * allows attributes to contain entity references, and tokenized
 * attribute types such as NMTOKENS may have a child for each token.)
 * For convenience, the Attribute object's getValue() method returns
 * the string version of the attribute's value.
 * <P>
 * Attributes are not children of the Elements they belong to, in the
 * usual sense, and have no valid Parent reference. However, the spec
 * says they _do_ belong to a specific Element, and an INUSE exception
 * is to be thrown if the user attempts to explicitly share them
 * between elements.
 * <P>
 * Note that Elements do not permit attributes to appear to be shared
 * (see the INUSE exception), so this object's mutability is
 * officially not an issue.
 * <p>
 * Note: The ownerNode attribute is used to store the Element the Attr
 * node is associated with. Attr nodes do not have parent nodes.
 * Besides, the getOwnerElement() method can be used to get the element node
 * this attribute is associated with.
 * <P>
 * AttrImpl does not support Namespaces. AttrNSImpl, which inherits from
 * it, does.
 *
 * <p>AttrImpl used to inherit from ParentNode. It now directly inherits from
 * NodeImpl and provide its own implementation of the ParentNode's behavior.
 * The reason is that we now try and avoid to always creating a Text node to
 * hold the value of an attribute. The DOM spec requires it, so we still have
 * to do it in case getFirstChild() is called for instance. The reason
 * attribute values are stored as a list of nodes is so that they can carry
 * more than a simple string. They can also contain EntityReference nodes.
 * However, most of the times people only have a single string that they only
 * set and get through Element.set/getAttribute or Attr.set/getValue. In this
 * new version, the Attr node has a value pointer which can either be the
 * String directly or a pointer to the first ChildNode. A flag tells which one
 * it currently is. Note that while we try to stick with the direct String as
 * much as possible once we've switched to a node there is no going back. This
 * is because we have no way to know whether the application keeps referring to
 * the node we once returned.
 * <p> The gain in memory varies on the density of attributes in the document.
 * But in the tests I've run I've seen up to 12% of memory gain. And the good
 * thing is that it also leads to a slight gain in speed because we allocate
 * fewer objects! I mean, that's until we have to actually create the node...
 * <p>
 * To avoid too much duplicated code, I got rid of ParentNode and renamed
 * ChildAndParentNode, which I never really liked, to ParentNode for
 * simplicity, this doesn't make much of a difference in memory usage because
 * there are only very objects that are only a Parent. This is only true now
 * because AttrImpl now inherits directly from NodeImpl and has its own
 * implementation of the ParentNode's node behavior. So there is still some
 * duplicated code there.
 *
 * <p><b>WARNING</b>: Some of the code here is partially duplicated in
 * ParentNode, be careful to keep these two classes in sync!
 *
 * @see AttrNSImpl
 *
 * @author Arnaud  Le Hors, IBM
 * @author Joe Kesselman, IBM
 * @author Andy Clark, IBM
 * @version
 * @since PR-DOM-Level-1-19980818.
 *
 */
public class AttrImpl
    extends NodeImpl
    implements Attr {

    //
    // Constants
    //

    /** Serialization version. */
    static final long serialVersionUID = 7277707688218972102L;

    //
    // Data
    //

    /** This can either be a String or the first child node. */
    protected Object value = null;

    /** Attribute name. */
    protected String name;

    protected static TextImpl textNode = null;

    //
    // Constructors
    //

    /**
     * Attribute has no public constructor. Please use the factory
     * method in the Document class.
     */
    protected AttrImpl(DocumentImpl ownerDocument, String name) {
    	super(ownerDocument);
        this.name = name;
        /** False for default attributes. */
        isSpecified(true);
        hasStringValue(true);
    }

    // for AttrNS
    protected AttrImpl() {}

    // create a real text node as child if we don't have one yet
    protected void makeChildNode() {
        if (hasStringValue()) {
            if (value != null) {
                TextImpl text =
                    (TextImpl) ownerDocument().createTextNode((String) value);
                value = text;
                text.isFirstChild(true);
                text.previousSibling = text;
                text.ownerNode = this;
                text.isOwned(true);
            }
            hasStringValue(false);
        }
    }

    /**
     * NON-DOM
     * set the ownerDocument of this node and its children
     */
    void setOwnerDocument(DocumentImpl doc) {
        if (needsSyncChildren()) {
            synchronizeChildren();
        }
        super.setOwnerDocument(doc);
        if (!hasStringValue()) {
            for (ChildNode child = firstChild;
                 child != null; child = child.nextSibling) {
                child.setOwnerDocument(doc);
            }
        }
    }

    //
    // Node methods
    //
    
    public Node cloneNode(boolean deep) {

        if (needsSyncChildren()) {
            synchronizeChildren();
        }
        AttrImpl clone = (AttrImpl) super.cloneNode(deep);

        // take care of case where there are kids
    	if (!clone.hasStringValue()) {

            // Need to break the association w/ original kids
            clone.value = null;

            // Then, if deep, clone the kids too.
            if (deep) {
                for (Node child = (Node) value; child != null;
                     child = child.getNextSibling()) {
                    clone.appendChild(child.cloneNode(true));
                }
            }
        }
        clone.isSpecified(true);
        return clone;
    }

    /**
     * A short integer indicating what type of node this is. The named
     * constants for this value are defined in the org.w3c.dom.Node interface.
     */
    public short getNodeType() {
        return Node.ATTRIBUTE_NODE;
    }

    /**
     * Returns the attribute name
     */
    public String getNodeName() {
        if (needsSyncData()) {
            synchronizeData();
        }
        return name;
    }

    /**
     * Implicit in the rerouting of getNodeValue to getValue is the
     * need to redefine setNodeValue, for symmetry's sake.  Note that
     * since we're explicitly providing a value, Specified should be set
     * true.... even if that value equals the default.
     */
    public void setNodeValue(String value) throws DOMException {
    	setValue(value);
    }

    /**
     * In Attribute objects, NodeValue is considered a synonym for
     * Value.
     *
     * @see #getValue()
     */
    public String getNodeValue() {
    	return getValue();
    }

    //
    // Attr methods
    //

    /**
     * In Attributes, NodeName is considered a synonym for the
     * attribute's Name
     */
    public String getName() {

        if (needsSyncData()) {
            synchronizeData();
        }
    	return name;

    } // getName():String

    /**
     * The DOM doesn't clearly define what setValue(null) means. I've taken it
     * as "remove all children", which from outside should appear
     * similar to setting it to the empty string.
     */
    public void setValue(String newvalue) {

    	if (isReadOnly()) {
            throw new DOMException(DOMException.NO_MODIFICATION_ALLOWED_ERR, 
                                   "DOM001 Modification not allowed");
        }
    		
        LCount lc=null;
        String oldvalue="";
        DocumentImpl ownerDocument = ownerDocument();
        if(MUTATIONEVENTS && ownerDocument.mutationEvents)
        {
            // MUTATION PREPROCESSING AND PRE-EVENTS:
            // Only DOMAttrModified need be produced directly.
            // It needs the previous value. Note that this may be
            // a treewalk, so I've put it under the conditional.
            lc=LCount.lookup(MutationEventImpl.DOM_ATTR_MODIFIED);
            if(lc.captures+lc.bubbles+lc.defaults>0 && ownerNode!=null)
            {
               oldvalue=getValue();
            }
            
        } // End mutation preprocessing

        if(MUTATIONEVENTS && ownerDocument.mutationEvents)
        {
            // Can no longer just discard the kids; they may have
            // event listeners waiting for them to disconnect.
            if (needsSyncChildren()) {
                synchronizeChildren();
            }
            if (value != null) {
                if (hasStringValue()) {
                    // temporarily sets an actual text node as our child so
                    // that we can use it in the event
                    if (textNode == null) {
                        textNode = (TextImpl)
                            ownerDocument.createTextNode((String) value);
                    }
                    else {
                        textNode.data = (String) value;
                    }
                    value = textNode;
                    textNode.isFirstChild(true);
                    textNode.previousSibling = textNode;
                    textNode.ownerNode = this;
                    textNode.isOwned(true);
                    hasStringValue(false);
                    internalRemoveChild(textNode, MUTATION_LOCAL);
                }
                else {
                    while (value != null) {
                        internalRemoveChild((Node) value, MUTATION_LOCAL);
                    }
                }
            }
        }
        else
        {
            // simply discard children if any
            if (!hasStringValue() && value != null) {
                // remove ref from first child to last child
                ChildNode firstChild = (ChildNode) value;
                firstChild.previousSibling = null;
                firstChild.isFirstChild(false);
            }
            // then remove ref to current value
            value = null;
            needsSyncChildren(false);
        }

        // Create and add the new one, generating only non-aggregate events
        // (There are no listeners on the new Text, but there may be
        // capture/bubble listeners on the Attr.
        // Note that aggregate events are NOT dispatched here,
        // since we need to combine the remove and insert.
    	isSpecified(true);
        if (newvalue != null) {
            if(MUTATIONEVENTS && ownerDocument.mutationEvents) {
                // if there are any event handlers create a real node
                internalInsertBefore(ownerDocument.createTextNode(newvalue),
                                     null, MUTATION_LOCAL);
                hasStringValue(false);
            } else {
                // directly store the string
                value = newvalue;
                hasStringValue(true);
            }
        }
		
    	changed(); // ***** Is this redundant?

        if(MUTATIONEVENTS && ownerDocument.mutationEvents)
        {
            // MUTATION POST-EVENTS:
            dispatchAggregateEvents(this,oldvalue,MutationEvent.MODIFICATION);
        }
		
    } // setValue(String)

    /**
     * The "string value" of an Attribute is its text representation,
     * which in turn is a concatenation of the string values of its children.
     */
    public String getValue() {

        if (needsSyncChildren()) {
            synchronizeChildren();
        }
        if (value == null) {
            return "";
        }
        if (hasStringValue()) {
            return (String) value;
        }
        ChildNode firstChild = ((ChildNode) value);
        ChildNode node = firstChild.nextSibling;
        if (node == null) {
            return firstChild.getNodeValue();
        }
    	StringBuffer value = new StringBuffer(firstChild.getNodeValue());
    	while (node != null) {
            value.append(node.getNodeValue());
            node = node.nextSibling;
    	}
    	return value.toString();

    } // getValue():String

    /**
     * The "specified" flag is true if and only if this attribute's
     * value was explicitly specified in the original document. Note that
     * the implementation, not the user, is in charge of this
     * property. If the user asserts an Attribute value (even if it ends
     * up having the same value as the default), it is considered a
     * specified attribute. If you really want to revert to the default,
     * delete the attribute from the Element, and the Implementation will
     * re-assert the default (if any) in its place, with the appropriate
     * specified=false setting.
     */
    public boolean getSpecified() {

        if (needsSyncData()) {
            synchronizeData();
        }
    	return isSpecified();

    } // getSpecified():boolean

    //
    // Attr2 methods
    //

    /**
     * Returns the element node that this attribute is associated with,
     * or null if the attribute has not been added to an element.
     *
     * @see #getOwnerElement
     *
     * @deprecated Previous working draft of DOM Level 2. New method
     *             is <tt>getOwnerElement()</tt>.
     */
    public Element getElement() {
        // if we have an owner, ownerNode is our ownerElement, otherwise it's
        // our ownerDocument and we don't have an ownerElement
        return (Element) (isOwned() ? ownerNode : null);
    }

    /**
     * Returns the element node that this attribute is associated with,
     * or null if the attribute has not been added to an element.
     *
     * @since WD-DOM-Level-2-19990719
     */
    public Element getOwnerElement() {
        // if we have an owner, ownerNode is our ownerElement, otherwise it's
        // our ownerDocument and we don't have an ownerElement
        return (Element) (isOwned() ? ownerNode : null);
    }
    
    public void normalize() {

        // No need to normalize if already normalized or
        // if value is kept as a String.
        if (isNormalized() || hasStringValue())
            return;

        Node kid, next;
        ChildNode firstChild = (ChildNode)value;
        for (kid = firstChild; kid != null; kid = next) {
            next = kid.getNextSibling();

            // If kid is a text node, we need to check for one of two
            // conditions:
            //   1) There is an adjacent text node
            //   2) There is no adjacent text node, but kid is
            //      an empty text node.
            if ( kid.getNodeType() == Node.TEXT_NODE )
            {
                // If an adjacent text node, merge it with kid
                if ( next!=null && next.getNodeType() == Node.TEXT_NODE )
                {
                    ((Text)kid).appendData(next.getNodeValue());
                    removeChild( next );
                    next = kid; // Don't advance; there might be another.
                }
                else
                {
                    // If kid is empty, remove it
                    if ( kid.getNodeValue().length()==0 )
                        removeChild( kid );
                }
            }
        }

        isNormalized(true);
    } // normalize()

    //
    // Public methods
    //

    /** NON-DOM, for use by parser */
    public void setSpecified(boolean arg) {

        if (needsSyncData()) {
            synchronizeData();
        }
    	isSpecified(arg);

    } // setSpecified(boolean)

    //
    // Object methods
    //

    /** NON-DOM method for debugging convenience */
    public String toString() {
    	return getName() + "=" + "\"" + getValue() + "\"";
    }

    /**
     * Test whether this node has any children. Convenience shorthand
     * for (Node.getFirstChild()!=null)
     */
    public boolean hasChildNodes() {
        if (needsSyncChildren()) {
            synchronizeChildren();
        }
        return value != null;
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
        // JKESS: KNOWN ISSUE HERE 

        if (needsSyncChildren()) {
            synchronizeChildren();
        }
        return this;

    } // getChildNodes():NodeList

    /** The first child of this Node, or null if none. */
    public Node getFirstChild() {

        if (needsSyncChildren()) {
            synchronizeChildren();
        }
        makeChildNode();
    	return (Node) value;

    }   // getFirstChild():Node

    /** The last child of this Node, or null if none. */
    public Node getLastChild() {

        if (needsSyncChildren()) {
            synchronizeChildren();
        }
        return lastChild();

    } // getLastChild():Node

    final ChildNode lastChild() {
        // last child is stored as the previous sibling of first child
        makeChildNode();
        return value != null ? ((ChildNode) value).previousSibling : null;
    }

    final void lastChild(ChildNode node) {
        // store lastChild as previous sibling of first child
        if (value != null) {
            ((ChildNode) value).previousSibling = node;
        }
    }

    /**
     * Move one or more node(s) to our list of children. Note that this
     * implicitly removes them from their previous parent.
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
        // Tail-call; optimizer should be able to do good things with.
        return internalInsertBefore(newChild,refChild,MUTATION_ALL);
    } // insertBefore(Node,Node):Node
     
    /** NON-DOM INTERNAL: Within DOM actions,we sometimes need to be able
     * to control which mutation events are spawned. This version of the
     * insertBefore operation allows us to do so. It is not intended
     * for use by application programs.
     */
    Node internalInsertBefore(Node newChild, Node refChild,int mutationMask) 
        throws DOMException {

        DocumentImpl ownerDocument = ownerDocument();
        boolean errorChecking = ownerDocument.errorChecking;

        if (newChild.getNodeType() == Node.DOCUMENT_FRAGMENT_NODE) {
            // SLOW BUT SAFE: We could insert the whole subtree without
            // juggling so many next/previous pointers. (Wipe out the
            // parent's child-list, patch the parent pointers, set the
            // ends of the list.) But we know some subclasses have special-
            // case behavior they add to insertBefore(), so we don't risk it.
            // This approch also takes fewer bytecodes.

            // NOTE: If one of the children is not a legal child of this
            // node, throw HIERARCHY_REQUEST_ERR before _any_ of the children
            // have been transferred. (Alternative behaviors would be to
            // reparent up to the first failure point or reparent all those
            // which are acceptable to the target node, neither of which is
            // as robust. PR-DOM-0818 isn't entirely clear on which it
            // recommends?????

            // No need to check kids for right-document; if they weren't,
            // they wouldn't be kids of that DocFrag.
            if (errorChecking) {
                for (Node kid = newChild.getFirstChild(); // Prescan
                     kid != null; kid = kid.getNextSibling()) {

                    if (!ownerDocument.isKidOK(this, kid)) {
                        throw new DOMException(
                                           DOMException.HIERARCHY_REQUEST_ERR, 
                                           "DOM006 Hierarchy request error");
                    }
                }
            }

            while (newChild.hasChildNodes()) {
                insertBefore(newChild.getFirstChild(), refChild);
            }
            return newChild;
        }

        if (newChild == refChild) {
            // stupid case that must be handled as a no-op triggering events...
            refChild = refChild.getNextSibling();
            removeChild(newChild);
            insertBefore(newChild, refChild);
            return newChild;
        }

        if (needsSyncChildren()) {
            synchronizeChildren();
        }

        if (errorChecking) {
            if (isReadOnly()) {
                throw new DOMException(
                                     DOMException.NO_MODIFICATION_ALLOWED_ERR, 
                                       "DOM001 Modification not allowed");
            }
            if (newChild.getOwnerDocument() != ownerDocument) {
                throw new DOMException(DOMException.WRONG_DOCUMENT_ERR, 
                                       "DOM005 Wrong document");
            }
            if (!ownerDocument.isKidOK(this, newChild)) {
                throw new DOMException(DOMException.HIERARCHY_REQUEST_ERR, 
                                       "DOM006 Hierarchy request error");
            }
            // refChild must be a child of this node (or null)
            if (refChild != null && refChild.getParentNode() != this) {
                throw new DOMException(DOMException.NOT_FOUND_ERR,
                                       "DOM008 Not found");
            }

            // Prevent cycles in the tree
            // newChild cannot be ancestor of this Node,
            // and actually cannot be this
            boolean treeSafe = true;
            for (NodeImpl a = this; treeSafe && a != null; a = a.parentNode())
            {
                treeSafe = newChild != a;
            }
            if (!treeSafe) {
                throw new DOMException(DOMException.HIERARCHY_REQUEST_ERR, 
                                       "DOM006 Hierarchy request error");
            }
        }

        makeChildNode(); // make sure we have a node and not a string

        EnclosingAttr enclosingAttr=null;
        if (MUTATIONEVENTS && ownerDocument.mutationEvents
            && (mutationMask&MUTATION_AGGREGATE)!=0) {
            // MUTATION PREPROCESSING
            // No direct pre-events, but if we're within the scope 
            // of an Attr and DOMAttrModified was requested,
            // we need to preserve its previous value.
            LCount lc=LCount.lookup(MutationEventImpl.DOM_ATTR_MODIFIED);
            if (lc.captures+lc.bubbles+lc.defaults>0) {
                enclosingAttr=getEnclosingAttr();
            }
        }

        // Convert to internal type, to avoid repeated casting
        ChildNode newInternal = (ChildNode)newChild;

        Node oldparent = newInternal.parentNode();
        if (oldparent != null) {
            oldparent.removeChild(newInternal);
        }

        // Convert to internal type, to avoid repeated casting
        ChildNode refInternal = (ChildNode) refChild;

        // Attach up
        newInternal.ownerNode = this;
        newInternal.isOwned(true);

        // Attach before and after
        // Note: firstChild.previousSibling == lastChild!!
        ChildNode firstChild = (ChildNode) value;
        if (firstChild == null) {
            // this our first and only child
            value = newInternal; // firstchild = newInternal;
            newInternal.isFirstChild(true);
            newInternal.previousSibling = newInternal;
        }
        else {
            if (refInternal == null) {
                // this is an append
                ChildNode lastChild = firstChild.previousSibling;
                lastChild.nextSibling = newInternal;
                newInternal.previousSibling = lastChild;
                firstChild.previousSibling = newInternal;
            }
            else {
                // this is an insert
                if (refChild == firstChild) {
                    // at the head of the list
                    firstChild.isFirstChild(false);
                    newInternal.nextSibling = firstChild;
                    newInternal.previousSibling = firstChild.previousSibling;
                    firstChild.previousSibling = newInternal;
                    value = newInternal; // firstChild = newInternal;
                    newInternal.isFirstChild(true);
                }
                else {
                    // somewhere in the middle
                    ChildNode prev = refInternal.previousSibling;
                    newInternal.nextSibling = refInternal;
                    prev.nextSibling = newInternal;
                    refInternal.previousSibling = newInternal;
                    newInternal.previousSibling = prev;
                }
            }
        }

        changed();

        if (MUTATIONEVENTS && ownerDocument.mutationEvents) {
            // MUTATION POST-EVENTS:
            // "Local" events (non-aggregated)
            if ((mutationMask&MUTATION_LOCAL) != 0) {
                // New child is told it was inserted, and where
                LCount lc = LCount.lookup(MutationEventImpl.DOM_NODE_INSERTED);
                if (lc.captures+lc.bubbles+lc.defaults>0) {
                    MutationEvent me= new MutationEventImpl();
                    me.initMutationEvent(MutationEventImpl.DOM_NODE_INSERTED,
                                         true,false,this,null,
                                         null,null,(short)0);
                    newInternal.dispatchEvent(me);
                }

                // If within the Document, tell the subtree it's been added
                // to the Doc.
                lc=LCount.lookup(
                            MutationEventImpl.DOM_NODE_INSERTED_INTO_DOCUMENT);
                if (lc.captures+lc.bubbles+lc.defaults>0) {
                    NodeImpl eventAncestor=this;
                    if (enclosingAttr!=null) 
                        eventAncestor=
                            (NodeImpl)(enclosingAttr.node.getOwnerElement());
                    if (eventAncestor!=null) { // Might have been orphan Attr
                        NodeImpl p=eventAncestor;
                        while (p!=null) {
                            eventAncestor=p; // Last non-null ancestor
                            // In this context, ancestry includes
                            // walking back from Attr to Element
                            if (p.getNodeType()==ATTRIBUTE_NODE) {
                                p=(ElementImpl)((AttrImpl)p).getOwnerElement();
                            }
                            else {
                                p=p.parentNode();
                            }
                        }
                        if (eventAncestor.getNodeType()==Node.DOCUMENT_NODE) {
                            MutationEvent me= new MutationEventImpl();
                            me.initMutationEvent(MutationEventImpl
                                              .DOM_NODE_INSERTED_INTO_DOCUMENT,
                                                 false,false,null,null,
                                                 null,null,(short)0);
                            dispatchEventToSubtree(newInternal,me);
                        }
                    }
                }
            }

            // Subroutine: Transmit DOMAttrModified and DOMSubtreeModified
            // (Common to most kinds of mutation)
            if ((mutationMask&MUTATION_AGGREGATE) != 0) {
                dispatchAggregateEvents(enclosingAttr);
            }
        }

        checkNormalizationAfterInsert(newInternal);

        return newChild;

    } // internalInsertBefore(Node,Node,int):Node

    /**
     * Remove a child from this Node. The removed child's subtree
     * remains intact so it may be re-inserted elsewhere.
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
        // Tail-call, should be optimizable
        if (hasStringValue()) {
            // we don't have any child per say so it can't be one of them!
            throw new DOMException(DOMException.NOT_FOUND_ERR, 
                                   "DOM008 Not found");
        }
        return internalRemoveChild(oldChild,MUTATION_ALL);
    } // removeChild(Node) :Node
     
    /** NON-DOM INTERNAL: Within DOM actions,we sometimes need to be able
     * to control which mutation events are spawned. This version of the
     * removeChild operation allows us to do so. It is not intended
     * for use by application programs.
     */
    Node internalRemoveChild(Node oldChild,int mutationMask)
        throws DOMException {

        DocumentImpl ownerDocument = ownerDocument();
        if (ownerDocument.errorChecking) {
            if (isReadOnly()) {
                throw new DOMException(
                                     DOMException.NO_MODIFICATION_ALLOWED_ERR, 
                                     "DOM001 Modification not allowed");
            }
            if (oldChild != null && oldChild.getParentNode() != this) {
                throw new DOMException(DOMException.NOT_FOUND_ERR, 
                                       "DOM008 Not found");
            }
        }

        // notify document
        ownerDocument.removedChildNode(oldChild);

        ChildNode oldInternal = (ChildNode) oldChild;

        EnclosingAttr enclosingAttr=null;
        if(MUTATIONEVENTS && ownerDocument.mutationEvents)
        {
            // MUTATION PREPROCESSING AND PRE-EVENTS:
            // If we're within the scope of an Attr and DOMAttrModified 
            // was requested, we need to preserve its previous value for
            // that event.
            LCount lc=LCount.lookup(MutationEventImpl.DOM_ATTR_MODIFIED);
            if(lc.captures+lc.bubbles+lc.defaults>0)
            {
                enclosingAttr=getEnclosingAttr();
            }
            
            if( (mutationMask&MUTATION_LOCAL) != 0)
            {
                // Child is told that it is about to be removed
                lc=LCount.lookup(MutationEventImpl.DOM_NODE_REMOVED);
                if(lc.captures+lc.bubbles+lc.defaults>0)
                {
                    MutationEvent me= new MutationEventImpl();
                    me.initMutationEvent(MutationEventImpl.DOM_NODE_REMOVED,
                                         true,false,this,null,
                                         null,null,(short)0);
                    oldInternal.dispatchEvent(me);
                }
            
                // If within Document, child's subtree is informed that it's
                // losing that status
                lc=LCount.lookup(
                             MutationEventImpl.DOM_NODE_REMOVED_FROM_DOCUMENT);
                if(lc.captures+lc.bubbles+lc.defaults>0)
                {
                    NodeImpl eventAncestor=this;
                    if(enclosingAttr!=null) 
                        eventAncestor=
                            (NodeImpl) enclosingAttr.node.getOwnerElement();
                    if(eventAncestor!=null) // Might have been orphan Attr
                    {
                        for(NodeImpl p=eventAncestor.parentNode();
                            p!=null;
                            p=p.parentNode())
                        {
                            eventAncestor=p; // Last non-null ancestor
                        }
                        if(eventAncestor.getNodeType()==Node.DOCUMENT_NODE)
                        {
                            MutationEvent me= new MutationEventImpl();
                            me.initMutationEvent(MutationEventImpl
                                               .DOM_NODE_REMOVED_FROM_DOCUMENT,
                                                 false,false,
                                                 null,null,null,null,(short)0);
                            dispatchEventToSubtree(oldInternal,me);
                        }
                    }
                }
            }
        } // End mutation preprocessing

        // Patch linked list around oldChild
        // Note: lastChild == firstChild.previousSibling
        if (oldInternal == value) { // oldInternal == firstChild
            // removing first child
            oldInternal.isFirstChild(false);
            value = oldInternal.nextSibling; // firstChild = oldInternal.nextSibling
            ChildNode firstChild = (ChildNode) value;
            if (firstChild != null) {
                firstChild.isFirstChild(true);
                firstChild.previousSibling = oldInternal.previousSibling;
            }
        } else {
            ChildNode prev = oldInternal.previousSibling;
            ChildNode next = oldInternal.nextSibling;
            prev.nextSibling = next;
            if (next == null) {
                // removing last child
                ChildNode firstChild = (ChildNode) value;
                firstChild.previousSibling = prev;
            } else {
                // removing some other child in the middle
                next.previousSibling = prev;
            }
        }

        // Save previous sibling for normalization checking.
        ChildNode oldPreviousSibling = oldInternal.previousSibling();

        // Remove oldInternal's references to tree
        oldInternal.ownerNode       = ownerDocument;
        oldInternal.isOwned(false);
        oldInternal.nextSibling     = null;
        oldInternal.previousSibling = null;

        changed();

        if(MUTATIONEVENTS && ownerDocument.mutationEvents)
        {
            // MUTATION POST-EVENTS:
            // Subroutine: Transmit DOMAttrModified and DOMSubtreeModified,
            // if required. (Common to most kinds of mutation)
            if( (mutationMask&MUTATION_AGGREGATE) != 0)
                dispatchAggregateEvents(enclosingAttr);
        } // End mutation postprocessing

        checkNormalizationAfterRemove(oldPreviousSibling);

        return oldInternal;

    } // internalRemoveChild(Node,int):Node

    /**
     * Make newChild occupy the location that oldChild used to
     * have. Note that newChild will first be removed from its previous
     * parent, if any. Equivalent to inserting newChild before oldChild,
     * then removing oldChild.
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

        makeChildNode();

        // If Mutation Events are being generated, this operation might
        // throw aggregate events twice when modifying an Attr -- once 
        // on insertion and once on removal. DOM Level 2 does not specify 
        // this as either desirable or undesirable, but hints that
        // aggregations should be issued only once per user request.

        EnclosingAttr enclosingAttr=null;
        DocumentImpl ownerDocument = ownerDocument();
        if(MUTATIONEVENTS && ownerDocument.mutationEvents)
        {
            // MUTATION PREPROCESSING AND PRE-EVENTS:
            // If we're within the scope of an Attr and DOMAttrModified 
            // was requested, we need to preserve its previous value for
            // that event.
            LCount lc=LCount.lookup(MutationEventImpl.DOM_ATTR_MODIFIED);
            if(lc.captures+lc.bubbles+lc.defaults>0)
            {
                enclosingAttr=getEnclosingAttr();
            }
        } // End mutation preprocessing

        internalInsertBefore(newChild, oldChild,MUTATION_LOCAL);
        if (newChild != oldChild) {
            internalRemoveChild(oldChild,MUTATION_LOCAL);
        }

        if(MUTATIONEVENTS && ownerDocument.mutationEvents)
        {
            dispatchAggregateEvents(enclosingAttr);
        }

        return oldChild;
    }

    //
    // NodeList methods
    //

    /**
     * NodeList method: Count the immediate children of this node
     * @return int
     */
    public int getLength() {

        if (hasStringValue()) {
            return 1;
        }
        ChildNode node = (ChildNode) value;
        int length = 0;
        for (; node != null; node = node.nextSibling) {
            length++;
        }
        return length;

    } // getLength():int

    /**
     * NodeList method: Return the Nth immediate child of this node, or
     * null if the index is out of bounds.
     * @return org.w3c.dom.Node
     * @param Index int
     */
    public Node item(int index) {

        if (hasStringValue()) {
            if (index != 0 || value == null) {
                return null;
            }
            else {
                makeChildNode();
                return (Node) value;
            }
        }
        ChildNode node = (ChildNode) value;
        for (int i = 0; i < index && node != null; i++) {
            node = node.nextSibling;
        }
        return node;

    } // item(int):Node

    //
    // DOM2: methods, getters, setters
    //

    //
    // Public methods
    //

    /**
     * Override default behavior so that if deep is true, children are also
     * toggled.
     * @see Node
     * <P>
     * Note: this will not change the state of an EntityReference or its
     * children, which are always read-only.
     */
    public void setReadOnly(boolean readOnly, boolean deep) {

        super.setReadOnly(readOnly, deep);

        if (deep) {

            if (needsSyncChildren()) {
                synchronizeChildren();
            }

            if (hasStringValue()) {
                return;
            }
            // Recursively set kids
            for (ChildNode mykid = (ChildNode) value;
                 mykid != null;
                 mykid = mykid.nextSibling) {
                if (mykid.getNodeType() != Node.ENTITY_REFERENCE_NODE) {
                    mykid.setReadOnly(readOnly,true);
                }
            }
        }
    } // setReadOnly(boolean,boolean)

    //
    // Protected methods
    //

    /**
     * Override this method in subclass to hook in efficient
     * internal data structure.
     */
    protected void synchronizeChildren() {
        // By default just change the flag to avoid calling this method again
        needsSyncChildren(false);
    }

    /**
     * Synchronizes the node's children with the internal structure.
     * Fluffing the children at once solves a lot of work to keep
     * the two structures in sync. The problem gets worse when
     * editing the tree -- this makes it a lot easier.
     * Even though this is only used in deferred classes this method is
     * put here so that it can be shared by all deferred classes.
     */
    protected final void synchronizeChildren(int nodeIndex) {

        // we don't want to generate any event for this so turn them off
        DeferredDocumentImpl ownerDocument =
            (DeferredDocumentImpl) ownerDocument();
        boolean orig = ownerDocument.mutationEvents;
        ownerDocument.mutationEvents = false;

        // no need to sync in the future
        needsSyncChildren(false);

        // create children and link them as siblings or simply store the value
        // as a String if all we have is one piece of text
        int last = ownerDocument.getLastChild(nodeIndex);
        int prev = ownerDocument.getPrevSibling(last);
        if (prev == -1) {
            value = ownerDocument.getNodeValueString(last);
            hasStringValue(true);
        }
        else {
            ChildNode firstNode = null;
            ChildNode lastNode = null;
            for (int index = last; index != -1;
                 index = ownerDocument.getPrevSibling(index)) {

                ChildNode node = (ChildNode)ownerDocument.getNodeObject(index);
                if (lastNode == null) {
                    lastNode = node;
                }
                else {
                    firstNode.previousSibling = node;
                }
                node.ownerNode = this;
                node.isOwned(true);
                node.nextSibling = firstNode;
                firstNode = node;
            }
            if (lastNode != null) {
                value = firstNode; // firstChild = firstNode
                firstNode.isFirstChild(true);
                lastChild(lastNode);
            }
            hasStringValue(false);
        }

        // set mutation events flag back to its original value
        ownerDocument.mutationEvents = orig;

    } // synchronizeChildren()

    /**
     * Checks the normalized state of this node after inserting a child.
     * If the inserted child causes this node to be unnormalized, then this
     * node is flagged accordingly.
     * The conditions for changing the normalized state are:
     * <ul>
     * <li>The inserted child is a text node and one of its adjacent siblings
     * is also a text node.
     * <li>The inserted child is is itself unnormalized.
     * </ul>
     *
     * @param insertedChild the child node that was inserted into this node
     *
     * @throws NullPointerException if the inserted child is <code>null</code>
     */
    void checkNormalizationAfterInsert(ChildNode insertedChild) {
        // See if insertion caused this node to be unnormalized.
        if (insertedChild.getNodeType() == Node.TEXT_NODE) {
            ChildNode prev = insertedChild.previousSibling();
            ChildNode next = insertedChild.nextSibling;
            // If an adjacent sibling of the new child is a text node,
            // flag this node as unnormalized.
            if ((prev != null && prev.getNodeType() == Node.TEXT_NODE) ||
                (next != null && next.getNodeType() == Node.TEXT_NODE)) {
                isNormalized(false);
            }
        }
        else {
            // If the new child is not normalized,
            // then this node is inherently not normalized.
            if (!insertedChild.isNormalized()) {
                isNormalized(false);
            }
        }
    } // checkNormalizationAfterInsert(ChildNode)

    /**
     * Checks the normalized of this node after removing a child.
     * If the removed child causes this node to be unnormalized, then this
     * node is flagged accordingly.
     * The conditions for changing the normalized state are:
     * <ul>
     * <li>The removed child had two adjacent siblings that were text nodes.
     * </ul>
     *
     * @param previousSibling the previous sibling of the removed child, or
     * <code>null</code>
     */
    void checkNormalizationAfterRemove(ChildNode previousSibling) {
        // See if removal caused this node to be unnormalized.
        // If the adjacent siblings of the removed child were both text nodes,
        // flag this node as unnormalized.
        if (previousSibling != null &&
            previousSibling.getNodeType() == Node.TEXT_NODE) {

            ChildNode next = previousSibling.nextSibling;
            if (next != null && next.getNodeType() == Node.TEXT_NODE) {
                isNormalized(false);
            }
        }
    } // checkNormalizationAfterRemove(ChildNode)

    //
    // Serialization methods
    //

    /** Serialize object. */
    private void writeObject(ObjectOutputStream out) throws IOException {

        // synchronize chilren
        if (needsSyncChildren()) {
            synchronizeChildren();
        }
        // write object
        out.defaultWriteObject();

    } // writeObject(ObjectOutputStream)

    /** Deserialize object. */
    private void readObject(ObjectInputStream ois)
        throws ClassNotFoundException, IOException {

        // perform default deseralization
        ois.defaultReadObject();

        // hardset synchildren - so we don't try to sync- it does not make any sense
        // to try to synchildren when we just desealize object.

        needsSyncChildren(false);

    } // readObject(ObjectInputStream)

} // class AttrImpl
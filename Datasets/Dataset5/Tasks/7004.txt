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
 * Note: Attributes do not have parent nodes. In other words, the
 * getParentNode() method is defined to return null for Attr nodes.
 * However, the getElement() method will return the element node
 * that this attribute is associated with.
 * <P>
 * AttrImpl does not support Namespaces. AttrNSImpl, which inherits from
 * it, does.
 * @see AttrNSImpl
 *
 * @version
 * @since  PR-DOM-Level-1-19980818.
 */
public class AttrImpl
    extends NodeContainer
    implements Attr {

    //
    // Constants
    //

    /** Serialization version. */
    static final long serialVersionUID = 7277707688218972102L;

    //
    // Data
    //

    /** Flag used for INUSE exception processing. */
    protected boolean owned;

    /** False for default attributes. */
    protected boolean specified = true;
  
    //
    // Constructors
    //

    /**
     * Attribute has no public constructor. Please use the factory
     * method in the Document class.
     */
    protected AttrImpl(DocumentImpl ownerDocument, String name) {
    	super(ownerDocument, name, null);
        syncData = true;
    }

    // for AttrNS
    protected AttrImpl() {}

    //
    // Node methods
    //
    
    /**
     * A short integer indicating what type of node this is. The named
     * constants for this value are defined in the org.w3c.dom.Node interface.
     */
    public short getNodeType() {
        return Node.ATTRIBUTE_NODE;
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

    /** Attributes don't have parent nodes. */
    public Node getParentNode() {
        return null;
    }

    //
    // Attr methods
    //

    /**
     * In Attributes, NodeName is considered a synonym for the
     * attribute's Name
     */
    public String getName() {

        if (syncData) {
            synchronizeData();
        }
    	return name;

    } // getName():String

    /**
     * The DOM doesn't clearly define what setValue(null) means. I've taken it
     * as "remove all children", which from outside should appear
     * similar to setting it to the empty string.
     */
    public void setValue(String value) {

    	if (readOnly) {
    		throw new DOMExceptionImpl(
    			DOMException.NO_MODIFICATION_ALLOWED_ERR, 
    			"NO_MODIFICATION_ALLOWED_ERR");
        }
    		
        LCount lc=null;
        String oldvalue="";
        if(MUTATIONEVENTS)
        {
            // MUTATION PREPROCESSING AND PRE-EVENTS:
            // Only DOMAttrModified need be produced directly.
            // It needs the previous value. Note that this may be
            // a treewalk, so I've put it under the conditional.
            lc=LCount.lookup(MutationEventImpl.DOM_ATTR_MODIFIED);
            if(lc.captures+lc.bubbles+lc.defaults>0 && parentNode!=null)
            {
               oldvalue=getValue();
            }
            
        } // End mutation preprocessing

        if(MUTATIONEVENTS)
        {
   		    // Can no longer just discard the kids; they may have
		    // event listeners waiting for them to disconnect.
		    while(firstChild!=null)
		        internalRemoveChild(firstChild,MUTATION_LOCAL);
        }
        else
        {
            firstChild   = null;
            lastChild    = null;
            syncChildren = false;
        }

		// Create and add the new one, generating only non-aggregate events
		// (There are no listeners on the new Text, but there may be
		// capture/bubble listeners on the Attr.
		// Note that aggregate events are NOT dispatched here,
		// since we need to combine the remove and insert.
    	specified = true;
		if (value != null) {
			internalInsertBefore(ownerDocument.createTextNode(value),null,
			    MUTATION_LOCAL);
		}
		
    	changed(); // ***** Is this redundant?

        if(MUTATIONEVENTS)
        {
            // MUTATION POST-EVENTS:
            dispatchAggregateEvents(this,oldvalue);            
        }
		
    } // setValue(String)

    /**
     * The "string value" of an Attribute is its text representation,
     * which in turn is a concatenation of the string values of its children.
     */
    public String getValue() {

    	StringBuffer value = new StringBuffer();
    	NodeImpl node = (NodeImpl)getFirstChild();
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

        if (syncData) {
            synchronizeData();
        }
    	return specified;

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
        return (Element)parentNode;
    }

    /**
     * Returns the element node that this attribute is associated with,
     * or null if the attribute has not been added to an element.
     *
     * @since WD-DOM-Level-2-19990719
     */
    public Element getOwnerElement() {
        return (Element)parentNode;
    }
    
    public void normalize() {

    	Node kid, next;
    	for (kid = getFirstChild(); kid != null; kid = next) {
    		next = kid.getNextSibling();

    		// If kid and next are both Text nodes (but _not_ CDATASection,
    		// which is a subclass of Text), they can be merged.
    		if (next != null
			 && kid.getNodeType() == Node.TEXT_NODE
			 && next.getNodeType() == Node.TEXT_NODE)
    	    {
    			((Text)kid).appendData(next.getNodeValue());
    			removeChild(next);
    			next = kid; // Don't advance; there might be another.
    		}

        }

    } // normalize()

    //
    // Public methods
    //

    /** NON-DOM, for use by parser */
    public void setSpecified(boolean arg) {

        if (syncData) {
            synchronizeData();
        }
    	specified = arg;

    } // setSpecified(boolean)

    //
    // Object methods
    //

    /** NON-DOM method for debugging convenience */
    public String toString() {
    	return getName() + "=" + "\"" + getValue() + "\"";
    }

} // class AttrImpl
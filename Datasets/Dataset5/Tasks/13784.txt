public TextImpl(CoreDocumentImpl ownerDoc, String data) {

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

import org.w3c.dom.CharacterData;
import org.w3c.dom.DOMException;
import org.w3c.dom.Node;
import org.w3c.dom.Text;

/**
 * Text nodes hold the non-markup, non-Entity content of
 * an Element or Attribute.
 * <P>
 * When a document is first made available to the DOM, there is only
 * one Text object for each block of adjacent plain-text. Users (ie,
 * applications) may create multiple adjacent Texts during editing --
 * see {@link Element#normalize} for discussion.
 * <P>
 * Note that CDATASection is a subclass of Text. This is conceptually
 * valid, since they're really just two different ways of quoting
 * characters when they're written out as part of an XML stream.
 *
 * @version
 * @since  PR-DOM-Level-1-19980818.
 */
public class TextImpl 
    extends CharacterDataImpl 
    implements CharacterData, Text {

    //
    // Constants
    //

    /** Serialization version. */
    static final long serialVersionUID = -5294980852957403469L;
    
    //
    // Constructors
    //

    /** Factory constructor. */
    public TextImpl(DocumentImpl ownerDoc, String data) {
        super(ownerDoc, data);
    }  
    
    //
    // Node methods
    //

    /** 
     * A short integer indicating what type of node this is. The named
     * constants for this value are defined in the org.w3c.dom.Node interface.
     */
    public short getNodeType() {
        return Node.TEXT_NODE;
    }

    /** Returns the node name. */
    public String getNodeName() {
        return "#text";
    }

    /**
     * NON-DOM: Set whether this Text is ignorable whitespace.
     */
    public void setIgnorableWhitespace(boolean ignore) {

        if (needsSyncData()) {
            synchronizeData();
        }
        isIgnorableWhitespace(ignore);

    } // setIgnorableWhitespace(boolean)
    

    /**
     * NON-DOM: Returns whether this Text is ignorable whitespace.
     */
    public boolean isIgnorableWhitespace() {

        if (needsSyncData()) {
            synchronizeData();
        }
        return internalIsIgnorableWhitespace();

    } // isIgnorableWhitespace():boolean
    
    //
    // Text methods
    //

    /** 
     * Break a text node into two sibling nodes.  (Note that if the
     * current node has no parent, they won't wind up as "siblings" --
     * they'll both be orphans.)
     *
     * @param offset The offset at which to split. If offset is at the
     * end of the available data, the second node will be empty.
     *
     * @returns A reference to the new node (containing data after the
     * offset point). The original node will contain data up to that
     * point.
     *
     * @throws DOMException(INDEX_SIZE_ERR) if offset is <0 or >length.
     *
     * @throws DOMException(NO_MODIFICATION_ALLOWED_ERR) if node is read-only.
     */
    public Text splitText(int offset) 
        throws DOMException {

    	if (isReadOnly()) {
            throw new DOMException(
    			DOMException.NO_MODIFICATION_ALLOWED_ERR, 
    			"DOM001 Modification not allowed");
        }

        if (needsSyncData()) {
            synchronizeData();
        }
    	if (offset < 0 || offset > data.length() ) {
            throw new DOMException(DOMException.INDEX_SIZE_ERR, 
                                       "DOM004 Index out of bounds");
        }
    		
        // split text into two separate nodes
    	Text newText =
            getOwnerDocument().createTextNode(data.substring(offset));
    	setNodeValue(data.substring(0, offset));

        // insert new text node
        Node parentNode = getParentNode();
    	if (parentNode != null) {
    		parentNode.insertBefore(newText, nextSibling);
        }

    	return newText;

    } // splitText(int):Text

} // class TextImpl
node.ownerNode = this;

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

import java.util.Vector;

import org.apache.xerces.framework.XMLAttrList;
import org.apache.xerces.utils.StringPool;

import org.w3c.dom.*;

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
 *
 * @version
 * @since  PR-DOM-Level-1-19980818.
 */
public class DeferredDocumentImpl
    extends DocumentImpl
    implements DeferredNode {

    //
    // Constants
    //

    /** Serialization version. */
    static final long serialVersionUID = 5186323580749626857L;

    // debugging

    /** To include code for printing the ref count tables. */
    private static final boolean DEBUG_PRINT_REF_COUNTS = false;

    /** To include code for printing the internal tables. */
    private static final boolean DEBUG_PRINT_TABLES = false;

    /** To debug identifiers set to true and recompile. */
    private static final boolean DEBUG_IDS = false;

    // protected

    /** Chunk shift. */
    protected static final int CHUNK_SHIFT = 11;           // 2^11 = 2k

    /** Chunk size. */
    protected static final int CHUNK_SIZE = (1 << CHUNK_SHIFT);

    /** Chunk mask. */
    protected static final int CHUNK_MASK = CHUNK_SIZE - 1;

    /** Initial chunk size. */
    protected static final int INITIAL_CHUNK_COUNT = (1 << (16 - CHUNK_SHIFT));   // 2^16 = 64k

    //
    // Data
    //

    // lazy-eval information

    /** Node count. */
    protected transient int fNodeCount = 0;

    /** Node types. */
    protected transient int fNodeType[][];

    /** Node names. */
    protected transient int fNodeName[][];

    /** Node values. */
    protected transient int fNodeValue[][];

    /** Node parents. */
    protected transient int fNodeParent[][];

    /** Node first children. */
    protected transient int fNodeFirstChild[][];

    /** Node next siblings. */
    protected transient int fNodeNextSib[][];

    /** Identifier count. */
    protected transient int fIdCount;

    /** Identifier name indexes. */
    protected transient int fIdName[];

    /** Identifier element indexes. */
    protected transient int fIdElement[];

    /** String pool cache. */
    protected transient StringPool fStringPool;

	/** DOM2: For namespace support in the deferred case.
	 */
	// Implementation Note: The deferred element and attribute must know how to
	// interpret the int representing the qname.
    protected boolean fNamespacesEnabled = false;

    //
    // Constructors
    //

    /**
     * NON-DOM: Actually creating a Document is outside the DOM's spec,
     * since it has to operate in terms of a particular implementation.
     */
    public DeferredDocumentImpl(StringPool stringPool) {
        this(stringPool, false);
    } // <init>(ParserState)

    /**
     * NON-DOM: Actually creating a Document is outside the DOM's spec,
     * since it has to operate in terms of a particular implementation.
     */
    public DeferredDocumentImpl(StringPool stringPool, boolean namespacesEnabled) {
        this(stringPool, namespacesEnabled, false);
    } // <init>(ParserState,boolean)

    /** Experimental constructor. */
    public DeferredDocumentImpl(StringPool stringPool,
                                boolean namespaces, boolean grammarAccess) {
        super(grammarAccess);

        fStringPool = stringPool;

        syncData = true;
        syncChildren = true;

        fNamespacesEnabled = namespaces;

    } // <init>(StringPool,boolean,boolean)

    //
    // Public methods
    //

    /** Returns the cached parser.getNamespaces() value.*/
    boolean getNamespacesEnabled() {
        return fNamespacesEnabled;
    }

    // internal factory methods

    /** Creates a document node in the table. */
    public int createDocument() {
        int nodeIndex = createNode(Node.DOCUMENT_NODE);
        return nodeIndex;
    }

    /** Creates a doctype. */
    public int createDocumentType(int rootElementNameIndex, int publicId, int systemId) {

        // create node
        int nodeIndex = createNode(Node.DOCUMENT_TYPE_NODE);
        int chunk     = nodeIndex >> CHUNK_SHIFT;
        int index     = nodeIndex & CHUNK_MASK;

        // added for DOM2: createDoctype factory method includes
        // name, publicID, systemID

        // create extra data node
        int extraDataIndex = createNode((short)0); // node type unimportant
        int echunk = extraDataIndex >> CHUNK_SHIFT;
        int eindex = extraDataIndex & CHUNK_MASK;

        // save name, public id, system id
        setChunkIndex(fNodeName, rootElementNameIndex, chunk, index);
        setChunkIndex(fNodeValue, extraDataIndex, chunk, index);
        setChunkIndex(fNodeName, publicId, echunk, eindex);
        setChunkIndex(fNodeValue, systemId, echunk, eindex);

        // return node index
        return nodeIndex;
        
    } // createDocumentType(int,int,int):int
    
    public void setInternalSubset(int doctypeIndex, int subsetIndex) {
        int chunk     = doctypeIndex >> CHUNK_SHIFT;
        int index     = doctypeIndex & CHUNK_MASK;
        int extraDataIndex = fNodeValue[chunk][index];
        int echunk = extraDataIndex >> CHUNK_SHIFT;
        int eindex = extraDataIndex & CHUNK_MASK;
        fNodeFirstChild[echunk][eindex]  = subsetIndex;
    }

    /** Creates a notation in the table. */
    public int createNotation(int notationName, int publicId, int systemId) throws Exception {

        // create node
        int nodeIndex = createNode(Node.NOTATION_NODE);
        int chunk     = nodeIndex >> CHUNK_SHIFT;
        int index     = nodeIndex & CHUNK_MASK;

        // create extra data node
        int extraDataIndex = createNode((short)0); // node type unimportant
        int echunk = extraDataIndex >> CHUNK_SHIFT;
        int eindex = extraDataIndex & CHUNK_MASK;

        // save name, public id, system id, and notation name
        setChunkIndex(fNodeName, notationName, chunk, index);
        setChunkIndex(fNodeValue, extraDataIndex, chunk, index);
        setChunkIndex(fNodeName, publicId, echunk, eindex);
        setChunkIndex(fNodeValue, systemId, echunk, eindex);

        // return node index
        return nodeIndex;

    } // createNotation(int,int,int):int

    /** Creates an entity in the table. */
    public int createEntity(int entityName, int publicId, int systemId, int notationName) throws Exception {

        // create node
        int nodeIndex = createNode(Node.ENTITY_NODE);
        int chunk     = nodeIndex >> CHUNK_SHIFT;
        int index     = nodeIndex & CHUNK_MASK;

        // create extra data node
        int extraDataIndex = createNode((short)0); // node type unimportant
        int echunk = extraDataIndex >> CHUNK_SHIFT;
        int eindex = extraDataIndex & CHUNK_MASK;

        // save name, public id, system id, and notation name
        setChunkIndex(fNodeName, entityName, chunk, index);
        setChunkIndex(fNodeValue, extraDataIndex, chunk, index);
        setChunkIndex(fNodeName, publicId, echunk, eindex);
        setChunkIndex(fNodeValue, systemId, echunk, eindex);
        setChunkIndex(fNodeFirstChild, notationName, echunk, eindex);

        // return node index
        return nodeIndex;

    } // createEntity(int,int,int,int):int

    /** Creates an entity reference node in the table. */
    public int createEntityReference(int nameIndex) throws Exception {

        // create node
        int nodeIndex = createNode(Node.ENTITY_REFERENCE_NODE);
        int chunk     = nodeIndex >> CHUNK_SHIFT;
        int index     = nodeIndex & CHUNK_MASK;
        setChunkIndex(fNodeName, nameIndex, chunk, index);

        // return node index
        return nodeIndex;

    } // createEntityReference(int):int

    /** Creates an element node in the table. */
    public int createElement(int elementNameIndex, XMLAttrList attrList, int attrListIndex) {

        // create node
        int elementNodeIndex = createNode(Node.ELEMENT_NODE);
        int elementChunk     = elementNodeIndex >> CHUNK_SHIFT;
        int elementIndex     = elementNodeIndex & CHUNK_MASK;
        setChunkIndex(fNodeName, elementNameIndex, elementChunk, elementIndex);

        // create attributes
        if (attrListIndex != -1) {
            int first = attrList.getFirstAttr(attrListIndex);
            int lastAttrNodeIndex = -1;
            int lastAttrChunk = -1;
            int lastAttrIndex = -1;
            for (int index = first;
                 index != -1;
                 index = attrList.getNextAttr(index)) {

                // create attribute
                int attrNodeIndex = createAttribute(attrList.getAttrName(index),
                                                    attrList.getAttValue(index),
                                                    attrList.isSpecified(index));
                int attrChunk = attrNodeIndex >> CHUNK_SHIFT;
                int attrIndex  = attrNodeIndex & CHUNK_MASK;
                setChunkIndex(fNodeParent, elementNodeIndex, attrChunk, attrIndex);

                // add links
                if (index == first) {
                    setChunkIndex(fNodeValue, attrNodeIndex, elementChunk, elementIndex);
                }
                else {
                    setChunkIndex(fNodeNextSib, attrNodeIndex, lastAttrChunk, lastAttrIndex);
                }

                // save last chunk and index
                lastAttrNodeIndex = attrNodeIndex;
                lastAttrChunk     = attrChunk;
                lastAttrIndex     = attrIndex;
            }
        }

        // return node index
        return elementNodeIndex;

    } // createElement(int,XMLAttrList,int):int

    /** Creates an attributes in the table. */
    public int createAttribute(int attrNameIndex, int attrValueIndex,
                               boolean specified) {

        // create node
        int nodeIndex = createNode(NodeImpl.ATTRIBUTE_NODE);
        int chunk = nodeIndex >> CHUNK_SHIFT;
        int index = nodeIndex & CHUNK_MASK;
        setChunkIndex(fNodeName, attrNameIndex, chunk, index);
        setChunkIndex(fNodeValue, specified ? 1 : 0, chunk, index);

        // append value as text node
        int textNodeIndex = createTextNode(attrValueIndex, false);
        appendChild(nodeIndex, textNodeIndex);

        // return node index
        return nodeIndex;

    } // createAttribute(int,int,boolean):int

    /** Creates an element definition in the table. */
    public int createElementDefinition(int elementNameIndex) {

        // create node
        int nodeIndex = createNode(NodeImpl.ELEMENT_DEFINITION_NODE);
        int chunk = nodeIndex >> CHUNK_SHIFT;
        int index = nodeIndex & CHUNK_MASK;
        setChunkIndex(fNodeName, elementNameIndex, chunk, index);

        // return node index
        return nodeIndex;

    } // createElementDefinition(int):int

    /** Creates a text node in the table. */
    public int createTextNode(int dataIndex, boolean ignorableWhitespace) {

        // create node
        int nodeIndex = createNode(Node.TEXT_NODE);
        int chunk = nodeIndex >> CHUNK_SHIFT;
        int index = nodeIndex & CHUNK_MASK;
        setChunkIndex(fNodeValue, dataIndex, chunk, index);
        setChunkIndex(fNodeFirstChild, ignorableWhitespace ?  1 : 0, chunk, index);

        // return node index
        return nodeIndex;

    } // createTextNode(int,boolean):int

    /** Creates a CDATA section node in the table. */
    public int createCDATASection(int dataIndex, boolean ignorableWhitespace) {

        // create node
        int nodeIndex = createNode(Node.CDATA_SECTION_NODE);
        int chunk = nodeIndex >> CHUNK_SHIFT;
        int index = nodeIndex & CHUNK_MASK;
        setChunkIndex(fNodeValue, dataIndex, chunk, index);
        setChunkIndex(fNodeFirstChild, ignorableWhitespace ?  1 : 0, chunk, index);

        // return node index
        return nodeIndex;

    } // createCDATASection(int,boolean):int

    /** Creates a processing instruction node in the table. */
    public int createProcessingInstruction(int targetIndex, int dataIndex) {

        // create node
        int nodeIndex = createNode(Node.PROCESSING_INSTRUCTION_NODE);
        int chunk = nodeIndex >> CHUNK_SHIFT;
        int index = nodeIndex & CHUNK_MASK;
        setChunkIndex(fNodeName, targetIndex, chunk, index);
        setChunkIndex(fNodeValue, dataIndex, chunk, index);

        // return node index
        return nodeIndex;

    } // createProcessingInstruction(int,int):int

    /** Creates a comment node in the table. */
    public int createComment(int dataIndex) {

        // create node
        int nodeIndex = createNode(Node.COMMENT_NODE);
        int chunk = nodeIndex >> CHUNK_SHIFT;
        int index = nodeIndex & CHUNK_MASK;
        setChunkIndex(fNodeValue, dataIndex, chunk, index);

        // return node index
        return nodeIndex;

    } // createComment(int):int

    /** Appends a child to the specified parent in the table. */
    public void appendChild(int parentIndex, int childIndex) {

        // append parent index
        int pchunk = parentIndex >> CHUNK_SHIFT;
        int pindex = parentIndex & CHUNK_MASK;
        int cchunk = childIndex >> CHUNK_SHIFT;
        int cindex = childIndex & CHUNK_MASK;
        setChunkIndex(fNodeParent, parentIndex, cchunk, cindex);

        // look for last child
        int prev = -1;
        int index = getChunkIndex(fNodeFirstChild, pchunk, pindex);
        while (index != -1) {
            prev = index;
            int nextIndex = getChunkIndex(fNodeNextSib, index >> CHUNK_SHIFT, index & CHUNK_MASK);
            if (nextIndex == -1) {
                break;
            }
            index = nextIndex;
        }

        // first child
        if (prev == -1) {
            setChunkIndex(fNodeFirstChild, childIndex, pchunk, pindex);
            }

        // last child
        else {
            int chnk = prev >> CHUNK_SHIFT;
            int indx = prev & CHUNK_MASK;
            setChunkIndex(fNodeNextSib, childIndex, chnk, indx);
        }

    } // appendChild(int,int)

    /** Adds an attribute node to the specified element. */
    public int setAttributeNode(int elemIndex, int attrIndex) {

        int echunk = elemIndex >> CHUNK_SHIFT;
        int eindex = elemIndex & CHUNK_MASK;
        int achunk = attrIndex >> CHUNK_SHIFT;
        int aindex = attrIndex & CHUNK_MASK;

        // see if this attribute is already here
        String attrName = fStringPool.toString(getChunkIndex(fNodeName, achunk, aindex));
        int oldAttrIndex = getChunkIndex(fNodeValue, echunk, eindex);
        int prevIndex = -1;
        int oachunk = -1;
        int oaindex = -1;
        while (oldAttrIndex != -1) {
            oachunk = oldAttrIndex >> CHUNK_SHIFT;
            oaindex = oldAttrIndex & CHUNK_MASK;
            String oldAttrName = fStringPool.toString(getChunkIndex(fNodeName, oachunk, oaindex));
            if (oldAttrName.equals(attrName)) {
                break;
            }
            prevIndex = oldAttrIndex;
            oldAttrIndex = getChunkIndex(fNodeNextSib, oachunk, oaindex);
        }

        // remove old attribute
        if (oldAttrIndex != -1) {

            // patch links
            int nextIndex = getChunkIndex(fNodeNextSib, oachunk, oaindex);
            if (prevIndex == -1) {
                setChunkIndex(fNodeValue, nextIndex, echunk, eindex);
            }
            else {
                int pchunk = prevIndex >> CHUNK_SHIFT;
                int pindex = prevIndex & CHUNK_MASK;
                setChunkIndex(fNodeNextSib, nextIndex, pchunk, pindex);
            }

            // remove connections to siblings
            clearChunkIndex(fNodeType, oachunk, oaindex);
            clearChunkIndex(fNodeName, oachunk, oaindex);
            clearChunkIndex(fNodeValue, oachunk, oaindex);
            clearChunkIndex(fNodeParent, oachunk, oaindex);
            clearChunkIndex(fNodeNextSib, oachunk, oaindex);
            int attrTextIndex = clearChunkIndex(fNodeFirstChild, oachunk, oaindex);
            int atchunk = attrTextIndex >> CHUNK_SHIFT;
            int atindex = attrTextIndex & CHUNK_MASK;
            clearChunkIndex(fNodeType, atchunk, atindex);
            clearChunkIndex(fNodeValue, atchunk, atindex);
            clearChunkIndex(fNodeParent, atchunk, atindex);
            clearChunkIndex(fNodeFirstChild, atchunk, atindex);
        }

        // add new attribute
        int nextIndex = getChunkIndex(fNodeValue, echunk, eindex);
        setChunkIndex(fNodeValue, attrIndex, echunk, eindex);
        setChunkIndex(fNodeNextSib, nextIndex, achunk, aindex);

        // return
        return oldAttrIndex;

    } // setAttributeNode(int,int):int

    /** Inserts a child before the specified node in the table. */
    public int insertBefore(int parentIndex, int newChildIndex, int refChildIndex) {

        if (refChildIndex == -1) {
            appendChild(parentIndex, newChildIndex);
            return newChildIndex;
        }

        int pchunk = parentIndex >> CHUNK_SHIFT;
        int pindex = parentIndex & CHUNK_MASK;
        int nchunk = newChildIndex >> CHUNK_SHIFT;
        int nindex = newChildIndex & CHUNK_MASK;
        int rchunk = refChildIndex >> CHUNK_SHIFT;
        int rindex = refChildIndex & CHUNK_MASK;

        // 1) if ref.parent.first = ref then
        //      begin
        //        ref.parent.first := new;
        //      end;
        int firstIndex = getChunkIndex(fNodeFirstChild, pchunk, pindex);
        if (firstIndex == refChildIndex) {
            setChunkIndex(fNodeFirstChild, newChildIndex, pchunk, pindex);
        }
        // 2) if ref.prev != null then
        //      begin
        //        ref.prev.next := new;
        //      end;
        int prevIndex = -1;
        for (int index = getChunkIndex(fNodeFirstChild, pchunk, pindex);
             index != -1;
             index = getChunkIndex(fNodeNextSib, index >> CHUNK_SHIFT, index & CHUNK_MASK)) {

            if (index == refChildIndex) {
                break;
            }
            prevIndex = index;
        }
        if (prevIndex != -1) {
            int chunk = prevIndex >> CHUNK_SHIFT;
            int index = prevIndex & CHUNK_MASK;
            setChunkIndex(fNodeNextSib, newChildIndex, chunk, index);
        }
        // 3) new.next := ref;
        setChunkIndex(fNodeNextSib, refChildIndex, nchunk, nindex);

        return newChildIndex;

    } // insertBefore(int,int,int):int

    /** Sets the first child of the parentIndex to childIndex. */
    public void setAsFirstChild(int parentIndex, int childIndex) {

        int pchunk = parentIndex >> CHUNK_SHIFT;
        int pindex = parentIndex & CHUNK_MASK;
        int chunk = childIndex >> CHUNK_SHIFT;
        int index = childIndex & CHUNK_MASK;
        setChunkIndex(fNodeFirstChild, childIndex, pchunk, pindex);

        int next = childIndex;
        while (next != -1) {
            childIndex = next;
            next = getChunkIndex(fNodeNextSib, chunk, index);
            chunk = next >> CHUNK_SHIFT;
            index = next & CHUNK_MASK;
        }

    } // setAsFirstChild(int,int)

    // methods used when objects are "fluffed-up"

    /** 
     * Returns the parent node of the given node. 
     * <em>Calling this method does not free the parent index.</em>
     */
    public int getParentNode(int nodeIndex) {
        return getParentNode(nodeIndex, false);
    }

    /** 
     * Returns the parent node of the given node. 
     * @param free True to free parent node.
     */
    public int getParentNode(int nodeIndex, boolean free) {

        if (nodeIndex == -1) {
            return -1;
        }

        int chunk = nodeIndex >> CHUNK_SHIFT;
        int index = nodeIndex & CHUNK_MASK;
        return free ? clearChunkIndex(fNodeParent, chunk, index)
                    : getChunkIndex(fNodeParent, chunk, index);

    } // getParentNode(int):int

    /** Returns the first child of the given node. */
    public int getFirstChild(int nodeIndex) {
        return getFirstChild(nodeIndex, true);
    }

    /** 
     * Returns the first child of the given node. 
     * @param free True to free child index.
     */
    public int getFirstChild(int nodeIndex, boolean free) {

        if (nodeIndex == -1) {
            return -1;
        }

        int chunk = nodeIndex >> CHUNK_SHIFT;
        int index = nodeIndex & CHUNK_MASK;
        return free ? clearChunkIndex(fNodeFirstChild, chunk, index)
                    : getChunkIndex(fNodeFirstChild, chunk, index);

    } // getFirstChild(int,boolean):int

    /** 
     * Returns the next sibling of the given node.
     * This is post-normalization of Text Nodes.
     */
    public int getNextSibling(int nodeIndex) {
        return getNextSibling(nodeIndex, true);
    }

    /** 
     * Returns the next sibling of the given node.
     * @param free True to free sibling index.
     */
    public int getNextSibling(int nodeIndex, boolean free) {

        if (nodeIndex == -1) {
            return -1;
        }

        int chunk = nodeIndex >> CHUNK_SHIFT;
        int index = nodeIndex & CHUNK_MASK;
        nodeIndex = free ? clearChunkIndex(fNodeNextSib, chunk, index)
                         : getChunkIndex(fNodeNextSib, chunk, index);

        while (nodeIndex != -1 && getChunkIndex(fNodeType, chunk, index) == Node.TEXT_NODE) {
            nodeIndex = getChunkIndex(fNodeNextSib, chunk, index);
            chunk = nodeIndex >> CHUNK_SHIFT;
            index = nodeIndex & CHUNK_MASK;
        }

        return nodeIndex;

    } // getNextSibling(int,boolean):int

    /**
     * Returns the <i>real</i> next sibling of the given node,
     * directly from the data structures. Used by TextImpl#getNodeValue()
     * to normalize values.
     */
    public int getRealNextSibling(int nodeIndex) {
        return getRealNextSibling(nodeIndex, true);
    }

    /**
     * Returns the <i>real</i> next sibling of the given node.
     * @param free True to free sibling index.
     */
    public int getRealNextSibling(int nodeIndex, boolean free) {

        if (nodeIndex == -1) {
            return -1;
        }

        int chunk = nodeIndex >> CHUNK_SHIFT;
        int index = nodeIndex & CHUNK_MASK;
        return free ? clearChunkIndex(fNodeNextSib, chunk, index)
                    : getChunkIndex(fNodeNextSib, chunk, index);

    } // getReadNextSibling(int,boolean):int

    /**
     * Returns the index of the element definition in the table
     * with the specified name index, or -1 if no such definition
     * exists.
     */
    public int lookupElementDefinition(int elementNameIndex) {

        if (fNodeCount > 1) {

            // find doctype
            int docTypeIndex = -1;
            int nchunk = 0;
            int nindex = 0;
            for (int index = getChunkIndex(fNodeFirstChild, nchunk, nindex);
                 index != -1;
                 index = getChunkIndex(fNodeNextSib, nchunk, nindex)) {

                nchunk = index >> CHUNK_SHIFT;
                nindex = index  & CHUNK_MASK;
                if (getChunkIndex(fNodeType, nchunk, nindex) == Node.DOCUMENT_TYPE_NODE) {
                    docTypeIndex = index;
                    break;
                }
            }

            // find element definition
            if (docTypeIndex == -1) {
                return -1;
            }
            nchunk = docTypeIndex >> CHUNK_SHIFT;
            nindex = docTypeIndex & CHUNK_MASK;
            for (int index = getChunkIndex(fNodeFirstChild, nchunk, nindex);
                 index != -1;
                 index = getChunkIndex(fNodeNextSib, nchunk, nindex)) {

                nchunk = index >> CHUNK_SHIFT;
                nindex = index & CHUNK_MASK;
                if (getChunkIndex(fNodeName, nchunk, nindex) == elementNameIndex) {
                    return index;
                }
            }
        }

        return -1;

    } // lookupElementDefinition(int):int

    /** Instantiates the requested node object. */
    public DeferredNode getNodeObject(int nodeIndex) {

        // is there anything to do?
        if (nodeIndex == -1) {
            return null;
        }

        // get node type
        int chunk = nodeIndex >> CHUNK_SHIFT;
        int index = nodeIndex & CHUNK_MASK;
        int type = clearChunkIndex(fNodeType, chunk, index);
        clearChunkIndex(fNodeParent, chunk, index);

        // create new node
        DeferredNode node = null;
        switch (type) {

            //
            // Standard DOM node types
            //

            case Node.ATTRIBUTE_NODE: {
		if (fNamespacesEnabled) {
		    node = new DeferredAttrNSImpl(this, nodeIndex);
		} else {
		    node = new DeferredAttrImpl(this, nodeIndex);
		}
                break;
            }

            case Node.CDATA_SECTION_NODE: {
                node = new DeferredCDATASectionImpl(this, nodeIndex);
                break;
            }

            case Node.COMMENT_NODE: {
                node = new DeferredCommentImpl(this, nodeIndex);
                break;
            }

            // NOTE: Document fragments can never be "fast".
            //
            //       The parser will never ask to create a document
            //       fragment during the parse. Document fragments
            //       are used by the application *after* the parse.
            //
            // case Node.DOCUMENT_FRAGMENT_NODE: { break; }
            case Node.DOCUMENT_NODE: {
                // this node is never "fast"
                node = this;
                break;
            }

            case Node.DOCUMENT_TYPE_NODE: {
                node = new DeferredDocumentTypeImpl(this, nodeIndex);
                // save the doctype node
                docType = (DocumentTypeImpl)node;
                break;
            }

            case Node.ELEMENT_NODE: {

                if (DEBUG_IDS) {
                    System.out.println("getNodeObject(ELEMENT_NODE): "+nodeIndex);
                }

                // create node
		if (fNamespacesEnabled) {
		    node = new DeferredElementNSImpl(this, nodeIndex);
		} else {
		    node = new DeferredElementImpl(this, nodeIndex);
		}

                // save the document element node
                if (docElement == null) {
                    docElement = (ElementImpl)node;
                }

                // check to see if this element needs to be
                // registered for its ID attributes
                if (fIdElement != null) {
                    int idIndex = DeferredDocumentImpl.binarySearch(fIdElement, 0, fIdCount-1, nodeIndex);
                    while (idIndex != -1) {

                        if (DEBUG_IDS) {
                            System.out.println("  id index: "+idIndex);
                            System.out.println("  fIdName["+idIndex+
                                               "]: "+fIdName[idIndex]);
                        }

                        // register ID
                        int nameIndex = fIdName[idIndex];
                        if (nameIndex != -1) {
                            String name = fStringPool.toString(nameIndex);
                            if (DEBUG_IDS) {
                                System.out.println("  name: "+name);
                                System.out.print("getNodeObject()#");
                            }
                            putIdentifier0(name, (Element)node);
                            fIdName[idIndex] = -1;
                        }

                        // continue if there are more IDs for
                        // this element
                        if (idIndex + 1 < fIdCount &&
                            fIdElement[idIndex + 1] == nodeIndex) {
                            idIndex++;
                        }
                        else {
                            idIndex = -1;
                        }
                    }
                }
                break;
            }

            case Node.ENTITY_NODE: {
                node = new DeferredEntityImpl(this, nodeIndex);
                break;
            }

            case Node.ENTITY_REFERENCE_NODE: {
                node = new DeferredEntityReferenceImpl(this, nodeIndex);
                break;
            }

            case Node.NOTATION_NODE: {
                node = new DeferredNotationImpl(this, nodeIndex);
                break;
            }

            case Node.PROCESSING_INSTRUCTION_NODE: {
                node = new DeferredProcessingInstructionImpl(this, nodeIndex);
                break;
            }

            case Node.TEXT_NODE: {
                node = new DeferredTextImpl(this, nodeIndex);
                break;
            }

            //
            // non-standard DOM node types
            //

            case NodeImpl.ELEMENT_DEFINITION_NODE: {
                node = new DeferredElementDefinitionImpl(this, nodeIndex);
                break;
            }

            default: {
                throw new IllegalArgumentException("type: "+type);
            }

        } // switch node type

        // store and return
        if (node != null) {
            return node;
        }

        // error
        throw new IllegalArgumentException();

    } // createNodeObject(int):Node

    /** Returns the name of the given node. */
    public String getNodeNameString(int nodeIndex) {
        return getNodeNameString(nodeIndex, true);
    } // getNodeNameString(int):String

    /** 
     * Returns the name of the given node. 
     * @param free True to free the string index.
     */
    public String getNodeNameString(int nodeIndex, boolean free) {

        if (nodeIndex == -1) {
            return null;
        }

        int chunk = nodeIndex >> CHUNK_SHIFT;
        int index = nodeIndex & CHUNK_MASK;
        int nameIndex = free 
                      ? clearChunkIndex(fNodeName, chunk, index)
                      : getChunkIndex(fNodeName, chunk, index);
        if (nameIndex == -1) {
            return null;
        }

        return fStringPool.toString(nameIndex);

    } // getNodeNameString(int,boolean):String

    /** Returns the value of the given node. */
    public String getNodeValueString(int nodeIndex) {
        return getNodeValueString(nodeIndex, true);
    } // getNodeValueString(int):String

    /** 
     * Returns the value of the given node. 
     * @param free True to free the string index.
     */
    public String getNodeValueString(int nodeIndex, boolean free) {

        if (nodeIndex == -1) {
            return null;
        }

        int chunk = nodeIndex >> CHUNK_SHIFT;
        int index = nodeIndex & CHUNK_MASK;
        int valueIndex = free
                       ? clearChunkIndex(fNodeValue, chunk, index)
                       : getChunkIndex(fNodeValue, chunk, index);
        if (valueIndex == -1) {
            return null;
        }

        return fStringPool.toString(valueIndex);

    } // getNodeValueString(int,boolean):String

    /** Returns the real int name of the given node. */
    public int getNodeName(int nodeIndex) {
        return getNodeName(nodeIndex, true);
    }

    /** 
     * Returns the real int name of the given node. 
     * @param free True to free the name index.
     */
    public int getNodeName(int nodeIndex, boolean free) {

        if (nodeIndex == -1) {
            return -1;
        }

        int chunk = nodeIndex >> CHUNK_SHIFT;
        int index = nodeIndex & CHUNK_MASK;
        return free ? clearChunkIndex(fNodeName, chunk, index)
                    : getChunkIndex(fNodeName, chunk, index);

    } // getNodeName(int,boolean):int

    /**
     * Returns the real int value of the given node.
     *  Used by AttrImpl to store specified value (1 == true).
     */
    public int getNodeValue(int nodeIndex) {
        return getNodeValue(nodeIndex, true);
    }

    /**
     * Returns the real int value of the given node.
     * @param free True to free the value index. 
     */
    public int getNodeValue(int nodeIndex, boolean free) {

        if (nodeIndex == -1) {
            return -1;
        }

        int chunk = nodeIndex >> CHUNK_SHIFT;
        int index = nodeIndex & CHUNK_MASK;
        return free ? clearChunkIndex(fNodeValue, chunk, index)
                    : getChunkIndex(fNodeValue, chunk, index);

    } // getNodeValue(int,boolean):int

    /** Returns the type of the given node. */
    public short getNodeType(int nodeIndex) {
        return getNodeType(nodeIndex, true);
    }

    /** 
     * Returns the type of the given node. 
     * @param True to free type index.
     */
    public short getNodeType(int nodeIndex, boolean free) {

        if (nodeIndex == -1) {
            return -1;
        }

        int chunk = nodeIndex >> CHUNK_SHIFT;
        int index = nodeIndex & CHUNK_MASK;
        if (free) {
            return (short)clearChunkIndex(fNodeType, chunk, index);
        }
        return (short)getChunkIndex(fNodeType, chunk, index);

    } // getNodeType(int):int

    // identifier maintenance

    /** Registers an identifier name with a specified element node. */
    public void putIdentifier(int nameIndex, int elementNodeIndex) {

        if (DEBUG_IDS) {
            System.out.println("putIdentifier("+nameIndex+", "+elementNodeIndex+')'+
                               " // "+
                               fStringPool.toString(nameIndex)+
                               ", "+
                               fStringPool.toString(getChunkIndex(fNodeName, elementNodeIndex >> CHUNK_SHIFT, elementNodeIndex & CHUNK_MASK)));
        }

        // initialize arrays
        if (fIdName == null) {
            fIdName    = new int[64];
            fIdElement = new int[64];
        }

        // resize arrays
        if (fIdCount == fIdName.length) {
            int idName[] = new int[fIdCount * 2];
            System.arraycopy(fIdName, 0, idName, 0, fIdCount);
            fIdName = idName;

            int idElement[] = new int[idName.length];
            System.arraycopy(fIdElement, 0, idElement, 0, fIdCount);
            fIdElement = idElement;
        }

        // store identifier
        fIdName[fIdCount] = nameIndex;
        fIdElement[fIdCount] = elementNodeIndex;
        fIdCount++;

    } // putIdentifier(int,int)

    //
    // DEBUG
    //

    /** Prints out the tables. */
    public void print() {

        if (DEBUG_PRINT_REF_COUNTS) {
            System.out.print("num\t");
            System.out.print("type\t");
            System.out.print("name\t");
            System.out.print("val\t");
            System.out.print("par\t");
            System.out.print("fch\t");
            System.out.print("nsib");
            System.out.println();
            for (int i = 0; i < fNodeType.length; i++) {
                if (fNodeType[i] != null) {
                    // separator
                    System.out.print("--------");
                    System.out.print("--------");
                    System.out.print("--------");
                    System.out.print("--------");
                    System.out.print("--------");
                    System.out.print("--------");
                    System.out.print("--------");
                    System.out.println();

                    // set count
                    System.out.print(i);
                    System.out.print('\t');
                    System.out.print(fNodeType[i][CHUNK_SIZE]);
                    System.out.print('\t');
                    System.out.print(fNodeName[i][CHUNK_SIZE]);
                    System.out.print('\t');
                    System.out.print(fNodeValue[i][CHUNK_SIZE]);
                    System.out.print('\t');
                    System.out.print(fNodeParent[i][CHUNK_SIZE]);
                    System.out.print('\t');
                    System.out.print(fNodeFirstChild[i][CHUNK_SIZE]);
                    System.out.print('\t');
                    System.out.print(fNodeNextSib[i][CHUNK_SIZE]);
                    System.out.println();

                    // clear count
                    System.out.print(i);
                    System.out.print('\t');
                    System.out.print(fNodeType[i][CHUNK_SIZE + 1]);
                    System.out.print('\t');
                    System.out.print(fNodeName[i][CHUNK_SIZE + 1]);
                    System.out.print('\t');
                    System.out.print(fNodeValue[i][CHUNK_SIZE + 1]);
                    System.out.print('\t');
                    System.out.print(fNodeParent[i][CHUNK_SIZE + 1]);
                    System.out.print('\t');
                    System.out.print(fNodeFirstChild[i][CHUNK_SIZE + 1]);
                    System.out.print('\t');
                    System.out.print(fNodeNextSib[i][CHUNK_SIZE + 1]);
                    System.out.println();
                }
            }
        }

        if (DEBUG_PRINT_TABLES) {
            // This assumes that the document is small
            System.out.println("# start table");
            for (int i = 0; i < fNodeCount; i++) {
                int chunk = i >> CHUNK_SHIFT;
                int index = i & CHUNK_MASK;
                if (i % 10 == 0) {
                    System.out.print("num\t");
                    System.out.print("type\t");
                    System.out.print("name\t");
                    System.out.print("val\t");
                    System.out.print("par\t");
                    System.out.print("fch\t");
                    System.out.print("nsib");
                    System.out.println();
                }
                System.out.print(i);
                System.out.print('\t');
                System.out.print(getChunkIndex(fNodeType, chunk, index));
                System.out.print('\t');
                System.out.print(getChunkIndex(fNodeName, chunk, index));
                System.out.print('\t');
                System.out.print(getChunkIndex(fNodeValue, chunk, index));
                System.out.print('\t');
                System.out.print(getChunkIndex(fNodeParent, chunk, index));
                System.out.print('\t');
                System.out.print(getChunkIndex(fNodeFirstChild, chunk, index));
                System.out.print('\t');
                System.out.print(getChunkIndex(fNodeNextSib, chunk, index));
                /***
                System.out.print(fNodeType[0][i]);
                System.out.print('\t');
                System.out.print(fNodeName[0][i]);
                System.out.print('\t');
                System.out.print(fNodeValue[0][i]);
                System.out.print('\t');
                System.out.print(fNodeParent[0][i]);
                System.out.print('\t');
                System.out.print(fNodeFirstChild[0][i]);
                System.out.print('\t');
                System.out.print(fNodeLastChild[0][i]);
                System.out.print('\t');
                System.out.print(fNodePrevSib[0][i]);
                System.out.print('\t');
                System.out.print(fNodeNextSib[0][i]);
                /***/
                System.out.println();
            }
            System.out.println("# end table");
        }

    } // print()

    //
    // DeferredNode methods
    //

    /** Returns the node index. */
    public int getNodeIndex() {
        return 0;
    }

    //
    // Protected methods
    //

    /** access to string pool. */
    protected StringPool getStringPool() {
        return fStringPool;
    }

    /** Synchronizes the node's data. */
    protected void synchronizeData() {

        // no need to sync in the future
        syncData = false;

        // fluff up enough nodes to fill identifiers hash
        if (fIdElement != null) {

            // REVISIT: There has to be a more efficient way of
            //          doing this. But keep in mind that the
            //          tree can have been altered and re-ordered
            //          before all of the element nodes with ID
            //          attributes have been registered. For now
            //          this is reasonable and safe. -Ac

            IntVector path = new IntVector();
            for (int i = 0; i < fIdCount; i++) {

                // ignore if it's already been registered
                int elementNodeIndex = fIdElement[i];
                int idNameIndex      = fIdName[i];
                if (idNameIndex == -1) {
                    continue;
                }

                // find path from this element to the root
                path.removeAllElements();
                int index = elementNodeIndex;
                do {
                    path.addElement(index);
                    int pchunk = index >> CHUNK_SHIFT;
                    int pindex = index & CHUNK_MASK;
                    index = getChunkIndex(fNodeParent, pchunk, pindex);
                } while (index != -1);

                // Traverse path (backwards), fluffing the elements
                // along the way. When this loop finishes, "place"
                // will contain the reference to the element node
                // we're interested in. -Ac
                Node place = this;
                for (int j = path.size() - 2; j >= 0; j--) {
                    index = path.elementAt(j);
                    Node child = place.getFirstChild();
                    while (child != null) {
                        if (child instanceof DeferredNode) {
                            int nodeIndex = ((DeferredNode)child).getNodeIndex();
                            if (nodeIndex == index) {
                                place = child;
                                break;
                            }
                        }
                        child = child.getNextSibling();
                    }
                }

                // register the element
                Element element = (Element)place;
                String  name    = fStringPool.toString(idNameIndex);
                putIdentifier0(name, element);
                fIdName[i] = -1;

                // see if there are more IDs on this element
                while (fIdElement[i + 1] == elementNodeIndex) {
                    name = fStringPool.toString(fIdName[++i]);
                    putIdentifier0(name, element);
                }
            }

        } // if identifiers

    } // synchronizeData()

    /**
     * Synchronizes the node's children with the internal structure.
     * Fluffing the children at once solves a lot of work to keep
     * the two structures in sync. The problem gets worse when
     * editing the tree -- this makes it a lot easier.
     */
    protected void synchronizeChildren() {

        if (syncData) {
            synchronizeData();
        }

        // no need to sync in the future
        syncChildren = false;

        getNodeType(0);

        // create children and link them as siblings
        NodeImpl last = null;
        for (int index = getFirstChild(0);
             index != -1;
             index = getNextSibling(index)) {

            NodeImpl node = (NodeImpl)getNodeObject(index);
            if (last == null) {
                firstChild = node;
            }
            else {
                last.nextSibling = node;
            }
            node.parentNode = this;
            node.previousSibling = last;
            last = node;

            // save doctype and document type
            int type = node.getNodeType();
            if (type == Node.ELEMENT_NODE) {
                docElement = (ElementImpl)node;
            }
            else if (type == Node.DOCUMENT_TYPE_NODE) {
                docType = (DocumentTypeImpl)node;
            }
        }

        if (last != null) {
            lastChild = last;
        }

    } // synchronizeChildren()

    // utility methods

    /** Ensures that the internal tables are large enough. */
    protected boolean ensureCapacity(int chunk, int index) {

        // create buffers
        if (fNodeType == null) {
            fNodeType       = new int[INITIAL_CHUNK_COUNT][];
            fNodeName       = new int[INITIAL_CHUNK_COUNT][];
            fNodeValue      = new int[INITIAL_CHUNK_COUNT][];
            fNodeParent     = new int[INITIAL_CHUNK_COUNT][];
            fNodeFirstChild = new int[INITIAL_CHUNK_COUNT][];
            fNodeNextSib    = new int[INITIAL_CHUNK_COUNT][];
        }

        // return true if table is already big enough
        try {
            return fNodeType[chunk][index] != 0;
        }

        // resize the tables
        catch (ArrayIndexOutOfBoundsException ex) {
            int newsize = chunk * 2;

            int[][] newArray = new int[newsize][];
            System.arraycopy(fNodeType, 0, newArray, 0, chunk);
            fNodeType = newArray;

            newArray = new int[newsize][];
            System.arraycopy(fNodeName, 0, newArray, 0, chunk);
            fNodeName = newArray;

            newArray = new int[newsize][];
            System.arraycopy(fNodeValue, 0, newArray, 0, chunk);
            fNodeValue = newArray;

            newArray = new int[newsize][];
            System.arraycopy(fNodeParent, 0, newArray, 0, chunk);
            fNodeParent = newArray;

            newArray = new int[newsize][];
            System.arraycopy(fNodeFirstChild, 0, newArray, 0, chunk);
            fNodeFirstChild = newArray;

            newArray = new int[newsize][];
            System.arraycopy(fNodeNextSib, 0, newArray, 0, chunk);
            fNodeNextSib = newArray;
        }

        catch (NullPointerException ex) {
            // ignore
        }

        // create chunks
        createChunk(fNodeType, chunk);
        createChunk(fNodeName, chunk);
        createChunk(fNodeValue, chunk);
        createChunk(fNodeParent, chunk);
        createChunk(fNodeFirstChild, chunk);
        createChunk(fNodeNextSib, chunk);

        // success
        return true;

    } // ensureCapacity(int,int):boolean

    /** Creates a node of the specified type. */
    protected int createNode(short nodeType) {

        // ensure tables are large enough
        int chunk = fNodeCount >> CHUNK_SHIFT;
        int index = fNodeCount & CHUNK_MASK;
        ensureCapacity(chunk, index);

        // initialize node
        setChunkIndex(fNodeType, nodeType, chunk, index);

        // return node index number
        return fNodeCount++;

    } // createNode(short):int

    /**
     * Performs a binary search for a target value in an array of
     * values. The array of values must be in ascending sorted order
     * before calling this method and all array values must be
     * non-negative.
     *
     * @param values  The array of values to search.
     * @param start   The starting offset of the search.
     * @param end     The ending offset of the search.
     * @param target  The target value.
     *
     * @return This function will return the <i>first</i> occurrence
     *         of the target value, or -1 if the target value cannot
     *         be found.
     */
    protected static int binarySearch(final int values[],
                                      int start, int end, int target) {

        if (DEBUG_IDS) {
            System.out.println("binarySearch(), target: "+target);
        }

        // look for target value
        while (start <= end) {

            // is this the one we're looking for?
            int middle = (start + end) / 2;
            int value  = values[middle];
            if (DEBUG_IDS) {
                System.out.print("  value: "+value+", target: "+target+" // ");
                print(values, start, end, middle, target);
            }
            if (value == target) {
                while (middle > 0 && values[middle - 1] == target) {
                    middle--;
                }
                if (DEBUG_IDS) {
                    System.out.println("FOUND AT "+middle);
                }
                return middle;
            }

            // is this point higher or lower?
            if (value > target) {
                end = middle - 1;
            }
            else {
                start = middle + 1;
            }

        } // while

        // not found
        if (DEBUG_IDS) {
            System.out.println("NOT FOUND!");
        }
        return -1;

    } // binarySearch(int[],int,int,int):int

    //
    // Private methods
    //

    /** Creates the specified chunk in the given array of chunks. */
    private final void createChunk(int data[][], int chunk) {
        data[chunk] = new int[CHUNK_SIZE + 2];
        for (int i = 0; i < CHUNK_SIZE; i++) {
            data[chunk][i] = -1;
        }
    }

    /**
     * Sets the specified value in the given of data at the chunk and index.
     *
     * @return Returns the old value.
     */
    private final int setChunkIndex(int data[][], int value, int chunk, int index) {
        if (value == -1) {
            return clearChunkIndex(data, chunk, index);
        }
        int ovalue = data[chunk][index];
        if (ovalue == -1) {
            data[chunk][CHUNK_SIZE]++;
        }
        data[chunk][index] = value;
        return ovalue;
    }

    /**
     * Returns the specified value in the given data at the chunk and index.
     */
    private final int getChunkIndex(int data[][], int chunk, int index) {
        return data[chunk] != null ? data[chunk][index] : -1;
    }

    /**
     * Clears the specified value in the given data at the chunk and index.
     * Note that this method will clear the given chunk if the reference
     * count becomes zero.
     *
     * @return Returns the old value.
     */
    private final int clearChunkIndex(int data[][], int chunk, int index) {
        int value = data[chunk] != null ? data[chunk][index] : -1;
        if (value != -1) {
            data[chunk][CHUNK_SIZE + 1]++;
            data[chunk][index] = -1;
            if (data[chunk][CHUNK_SIZE] == data[chunk][CHUNK_SIZE + 1]) {
                data[chunk] = null;
            }
        }
        return value;
    }

    /**
     * This version of putIdentifier is needed to avoid fluffing
     * all of the paths to ID attributes when a node object is
     * created that contains an ID attribute.
     */
    private final void putIdentifier0(String idName, Element element) {

        if (DEBUG_IDS) {
            System.out.println("putIdentifier0("+
                               idName+", "+
                               element+')');
        }

        // create hashtable
        if (identifiers == null) {
            identifiers = new java.util.Hashtable();
        }

        // save ID and its associated element
        identifiers.put(idName, element);

    } // putIdentifier0(String,Element)

    /** Prints the ID array. */
    private static void print(int values[], int start, int end,
                              int middle, int target) {

        if (DEBUG_IDS) {
            System.out.print(start);
            System.out.print(" [");
            for (int i = start; i < end; i++) {
                if (middle == i) {
                    System.out.print("!");
                }
                System.out.print(values[i]);
                if (values[i] == target) {
                    System.out.print("*");
                }
                if (i < end - 1) {
                    System.out.print(" ");
                }
            }
            System.out.println("] "+end);
        }

    } // print(int[],int,int,int,int)

    //
    // Classes
    //

    /**
     * A simple integer vector.
     */
    static class IntVector {

        //
        // Data
        //

        /** Data. */
        private int data[];

        /** Size. */
        private int size;

        //
        // Public methods
        //

        /** Returns the length of this vector. */
        public int size() {
            return size;
        }

        /** Returns the element at the specified index. */
        public int elementAt(int index) {
            return data[index];
        }

        /** Appends an element to the end of the vector. */
        public void addElement(int element) {
            ensureCapacity(size + 1);
            data[size++] = element;
        }

        /** Clears the vector. */
        public void removeAllElements() {
            size = 0;
        }

        //
        // Private methods
        //

        /** Makes sure that there is enough storage. */
        private void ensureCapacity(int newsize) {

            if (data == null) {
                data = new int[newsize + 15];
            }
            else if (newsize > data.length) {
                int newdata[] = new int[newsize + 15];
                System.arraycopy(data, 0, newdata, 0, data.length);
                data = newdata;
            }

        } // ensureCapacity(int)

    } // class IntVector

} // class DeferredDocumentImpl
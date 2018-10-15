import org.w3c.dom.ranges.*;

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
 *4dorse or promote products derived from this
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
import org.w3c.dom.DocumentFragment;
import org.w3c.dom.Document;
import org.w3c.dom.Node;
import org.w3c.dom.CharacterData;
import org.apache.xerces.dom.DocumentImpl;
import org.w3c.dom.range.*;
import java.util.Vector;

/** The RangeImpl class implements the org.w3c.dom.range.Range interface.
 *  <p> Please see the API documentation for the interface classes  
 *  and use the interfaces in your client programs.
 */
public class RangeImpl  implements Range {
    
    //
    // Constants
    //
    

    // Where to collapse to.
    static final int START = 0;
    static final int AFTER = 1;
    static final int BEFORE = -1;
    
    //
    // Data
    //
    
    DocumentImpl fDocument;
    Node fStartContainer;
    Node fEndContainer;
    int fStartOffset;
    int fEndOffset;
    boolean fIsCollapsed;   
    boolean fDetach = false;
    Node fInsertNode = null;
    Node fDeleteNode = null;
    Node fSplitNode = null;
    
    
    /** The constructor. Clients must use DocumentRange.createRange(),
     *  because it registers the Range with the document, so it can 
     *  be fixed-up.
     */
    public RangeImpl(DocumentImpl document) {
        fDocument = document;
        fStartContainer = document;
        fEndContainer = document;
        fStartOffset = 0;
        fEndOffset = 0;
        fDetach = false;
    }
    
    public Node getStartContainer() {
        return fStartContainer;
    }
    
    public int getStartOffset() {
        return fStartOffset;
    }
    
    public Node getEndContainer() {
        return fEndContainer;
    }
    public int getEndOffset() {
        return fEndOffset;
    }
    
    public boolean getCollapsed() {
        return (fStartContainer == fEndContainer 
             && fStartOffset == fEndOffset);
    }
    
    public Node getCommonAncestorContainer(){
        Vector startV = new Vector();
        Node node;
        for (node=fStartContainer; node != null; 
             node=node.getParentNode()) 
        {
            startV.addElement(node);
        }
        Vector endV = new Vector();
        for (node=fEndContainer; node != null; 
             node=node.getParentNode()) 
        {
            endV.addElement(node);
        }
        int s = startV.size()-1;
        int e = endV.size()-1;
        Object result = null;
        while (s>=0 && e>=0) {
            if (startV.elementAt(s) == endV.elementAt(e)) {
                result = startV.elementAt(s);
            } else {
                break;
            }
            --s;
            --e;
        }
        return (Node)result; 
    }
    
    
    public void setStart(Node refNode, int offset)
                         throws RangeException, DOMException
    {
    	if( fDetach) {
    		throw new DOMException(
    			DOMException.INVALID_STATE_ERR, 
			"DOM011 Invalid state");
        }
        if ( !isLegalContainer(refNode)) {
    		throw new RangeExceptionImpl(
    			RangeException.INVALID_NODE_TYPE_ERR, 
			"DOM012 Invalid node type");
        }
        
        checkIndex(refNode, offset);
        
        fStartContainer = refNode;
        fStartOffset = offset;
    }
    
    public void setEnd(Node refNode, int offset)
                       throws RangeException, DOMException
    {
    	if( fDetach) {
    		throw new DOMException(
    			DOMException.INVALID_STATE_ERR, 
			"DOM011 Invalid state");
        }
        if ( !isLegalContainer(refNode)) {
    		throw new RangeExceptionImpl(
    			RangeException.INVALID_NODE_TYPE_ERR, 
			"DOM012 Invalid node type");
        }
        
        checkIndex(refNode, offset);
        
        fEndContainer = refNode;
        fEndOffset = offset;
    }
    public void setStartBefore(Node refNode) 
        throws RangeException 
    {
    	if( fDetach) {
    		throw new DOMException(
    			DOMException.INVALID_STATE_ERR, 
			"DOM011 Invalid state");
        }
		if ( !hasLegalRootContainer(refNode) ||
			 !isLegalContainedNode(refNode) )
		{
    		throw new RangeExceptionImpl(
    			RangeException.INVALID_NODE_TYPE_ERR, 
			"DOM012 Invalid node type");
        }
        fStartContainer = refNode.getParentNode();
        int i = 0;
        for (Node n = refNode; n!=null; n = n.getPreviousSibling()) {
            i++;
        }
        fStartOffset = i-1;
    }
    public void setStartAfter(Node refNode)
        throws RangeException
    {
    	if( fDetach) {
    		throw new DOMException(
    			DOMException.INVALID_STATE_ERR, 
			"DOM011 Invalid state");
        }
        if ( !hasLegalRootContainer(refNode) || 
			 !isLegalContainedNode(refNode)) {
    		throw new RangeExceptionImpl(
    			RangeException.INVALID_NODE_TYPE_ERR, 
			"DOM012 Invalid node type");
        }
        fStartContainer = refNode.getParentNode();
        int i = 0;
        for (Node n = refNode; n!=null; n = n.getPreviousSibling()) {
            i++;
        }
        fStartOffset = i;
    }
    public void setEndBefore(Node refNode)
        throws RangeException
    {
    	if( fDetach) {
    		throw new DOMException(
    			DOMException.INVALID_STATE_ERR, 
			"DOM011 Invalid state");
        }
        if ( !hasLegalRootContainer(refNode) ||
			 !isLegalContainedNode(refNode)) {
    		throw new RangeExceptionImpl(
    			RangeException.INVALID_NODE_TYPE_ERR, 
			"DOM012 Invalid node type");
        }
        fEndContainer = refNode.getParentNode();
        int i = 0;
        for (Node n = refNode; n!=null; n = n.getPreviousSibling()) {
            i++;
        }
        fEndOffset = i-1;
    }
                                            
    public void setEndAfter(Node refNode)
        throws RangeException
    {
    	if( fDetach) {
    		throw new DOMException(
    			DOMException.INVALID_STATE_ERR, 
			"DOM011 Invalid state");
        }
        if ( !hasLegalRootContainer(refNode) ||
			 !isLegalContainedNode(refNode)) {
    		throw new RangeExceptionImpl(
    			RangeException.INVALID_NODE_TYPE_ERR, 
			"DOM012 Invalid node type");
        }
        fEndContainer = refNode.getParentNode();
        int i = 0;
        for (Node n = refNode; n!=null; n = n.getPreviousSibling()) {
            i++;
        }
        fEndOffset = i;
    }
    public void collapse(boolean toStart) {
        
    	if( fDetach) {
    		throw new DOMException(
    			DOMException.INVALID_STATE_ERR, 
			"DOM011 Invalid state");
        }
        
        if (toStart) {
            fEndContainer = fStartContainer;
            fEndOffset = fStartOffset;
        } else {
            fStartContainer = fEndContainer;
            fStartOffset = fEndOffset;
        }
    }
    
    public void selectNode(Node refNode)
        throws RangeException
    {
    	if( fDetach) {
    		throw new DOMException(
    			DOMException.INVALID_STATE_ERR, 
			"DOM011 Invalid state");
        }
        if ( !isLegalContainer( refNode.getParentNode() ) ||
			 !isLegalContainedNode( refNode ) ) {
    		throw new RangeExceptionImpl(
    			RangeException.INVALID_NODE_TYPE_ERR, 
			"DOM012 Invalid node type");
        }
        Node parent = refNode.getParentNode();
        if (parent != null ) // REVIST: what to do if it IS null?
        {
            fStartContainer = parent;
            fEndContainer = parent;
            int i = 0;
            for (Node n = refNode; n!=null; n = n.getPreviousSibling()) {
                i++;
            }
            fStartOffset = i-1;
            fEndOffset = fStartOffset+1;
        }
    }
        
    public void selectNodeContents(Node refNode)
        throws RangeException
    {
    	if( fDetach) {
    		throw new DOMException(
    			DOMException.INVALID_STATE_ERR, 
			"DOM011 Invalid state");
        }
        if ( !isLegalContainer(refNode)) {
    		throw new RangeExceptionImpl(
    			RangeException.INVALID_NODE_TYPE_ERR, 
			"DOM012 Invalid node type");
        }
        fStartContainer = refNode;
        fEndContainer = refNode;
        Node first = refNode.getFirstChild();
        fStartOffset = 0;
        if (first == null) {
            fEndOffset = 0;
        } else {
            int i = 0;
            for (Node n = first; n!=null; n = n.getNextSibling()) {
                i++;
            }
            fEndOffset = i;
        }
        
    }

    public short compareBoundaryPoints(short how, Range sourceRange)
        throws DOMException
    {
    	if( fDetach) {
    		throw new DOMException(
    			DOMException.INVALID_STATE_ERR, 
			"DOM011 Invalid state");
    	}
       
        Node endPointA;
        Node endPointB;
        int offsetA;
        int offsetB;
        
        if (how == START_TO_START) {
            endPointA = sourceRange.getStartContainer();
            endPointB = fStartContainer;
            offsetA = sourceRange.getStartOffset();
            offsetB = fStartOffset;
        } else 
        if (how == START_TO_END) {
            endPointA = sourceRange.getStartContainer();
            endPointB = fEndContainer;
            offsetA = sourceRange.getStartOffset();
            offsetB = fEndOffset;
        } else 
        if (how == END_TO_START) {
            endPointA = sourceRange.getEndContainer();
            endPointB = fStartContainer;
            offsetA = sourceRange.getEndOffset();
            offsetB = fStartOffset;
        } else {
            endPointA = sourceRange.getEndContainer();
            endPointB = fEndContainer;
            offsetA = sourceRange.getEndOffset();
            offsetB = fEndOffset;
        }

        // The DOM Spec outlines four cases that need to be tested
        // to compare two range boundary points:
        //   case 1: same container
        //   case 2: Child C of container A is ancestor of B
        //   case 3: Child C of container B is ancestor of A
        //   case 4: preorder traversal of context tree.
        
        // case 1: same container
        if (endPointA == endPointB) {
            if (offsetA < offsetB) return -1;
            if (offsetA == offsetB) return 0;
            return 1;
        }
        // case 2: Child C of container A is ancestor of B
        // This can be quickly tested by walking the parent chain of B
        for ( Node c = endPointB, p = c.getParentNode();
             p != null;
             c = p, p = p.getParentNode())
        {
            if (p == endPointA) {
                int index = indexOf(c, endPointA);
                if (offsetA <= index) return -1;
                return 1;
            }
        }

        // case 3: Child C of container B is ancestor of A
        // This can be quickly tested by walking the parent chain of A
        for ( Node c = endPointA, p = c.getParentNode();
             p != null;
             c = p, p = p.getParentNode())
        {
            if (p == endPointB) {
                int index = indexOf(c, endPointB);
                if (index < offsetB) return -1;
                return 1;
            }
        }

        // case 4: preorder traversal of context tree.
        // Instead of literally walking the context tree in pre-order,
        // we use relative node depth walking which is usually faster

        int depthDiff = 0;
        for ( Node n = endPointA; n != null; n = n.getParentNode() )
            depthDiff++;
        for ( Node n = endPointB; n != null; n = n.getParentNode() )
            depthDiff--;
        while (depthDiff > 0) {
            endPointA = endPointA.getParentNode();
            depthDiff--;
        }
        while (depthDiff < 0) {
            endPointB = endPointB.getParentNode();
            depthDiff++;
        }
        for (Node pA = endPointA.getParentNode(),
             pB = endPointB.getParentNode();
             pA != pB;
             pA = pA.getParentNode(), pB = pB.getParentNode() )
        {
            endPointA = pA;
            endPointB = pB;
        }
        for ( Node n = endPointA.getNextSibling();
             n != null;
             n = n.getNextSibling() )
        {
            if (n == endPointB) {
                return -1;
            }
        }
        return 1;
    }
    
    public void deleteContents()
        throws DOMException
    {
        Node current = fStartContainer;
        Node parent = null;
        Node next;
        boolean deleteCurrent = false;
        Node root = getCommonAncestorContainer();
        
        // if same container, simplify case
        if (fStartContainer == fEndContainer) {
            if (fStartOffset == fEndOffset) { // eg collapsed
                return; 
            } 
            if (fStartContainer.getNodeType() == Node.TEXT_NODE) {
                String value = fStartContainer.getNodeValue();
                //REVIST: This section should probably throw an exception!
                // This should NEVER happen, if the Range is always valid.
                int realStart = fStartOffset;
                int realEnd = fEndOffset;
                if (fStartOffset > value.length()) realStart = value.length()-1;
                if (fEndOffset > value.length()) realEnd = value.length()-1;
                
                deleteData((CharacterData)fStartContainer, realStart, realEnd-realStart);
                
                } else {
                current = fStartContainer.getFirstChild();
                int i = 0;
                for(i = 0; i < fStartOffset && current != null; i++) {
                    current=current.getNextSibling();
                }
                for(i = 0; i < fEndOffset-fStartOffset && current != null; i++) {
                    Node newCurrent=current.getNextSibling();
                    removeChild(fStartContainer, current);
                    current = newCurrent;
                }
            }
            collapse(true);
            return;
        }
        
        Node partialNode = null;
        int partialInt = START;
        
        Node startRoot = null;
        // initialize current for startContainer.
        if (current.getNodeType() == Node.TEXT_NODE) {
            deleteData((CharacterData)current, fStartOffset, 
                current.getNodeValue().length()-fStartOffset);
        } else {
            current = current.getFirstChild();
            for (int i = 0 ; i < fStartOffset && current != null; i++){
                current = current.getNextSibling();
            }
            if (current==null) {
                current = fStartContainer;
            } else 
            if (current != fStartContainer)
            {
                deleteCurrent = true;
            }
        }
        
        
        // traverse up from the startContainer...
        // current starts as the node to delete;
        while (current != root && current != null) {
            
            parent = current.getParentNode();
            if (parent == root) {
                if (startRoot == null)
                    startRoot = current;
            } else {
                if (partialNode==null) {
                    partialNode = parent;
                    partialInt = AFTER;
                }
            }

            
            if (parent != root) {
                next = current.getNextSibling();
                Node nextnext;
                while (next != null) {
                    nextnext = next.getNextSibling();
                    //parent.removeChild(next);
                    removeChild(parent, next);
                    next = nextnext;
                }
            }
            
            if (deleteCurrent) {
                //parent.removeChild(current);
                removeChild(parent, current);
                deleteCurrent = false;
            }
            current = parent;
        }
        
        Node endRoot = null;
        // initialize current for endContainer.
        current = fEndContainer;
        if (current.getNodeType() == Node.TEXT_NODE) {
            deleteData((CharacterData)current, 0, fEndOffset); 
        } else {
    
            if (fEndOffset == 0) { // "before"
                current = fEndContainer;
            }
            else {
                current = current.getFirstChild();
                for(int i = 1; i < fEndOffset && current != null; i++) {
                    current=current.getNextSibling();
                }
                if (current==null) { // REVIST: index-out-of-range what to do?
                    current = fEndContainer.getLastChild();
                } else 
                if (current != fStartContainer) {
                    deleteCurrent = true;
                }
                
            }
        }
        
        // traverse up from the endContainer...
        while (current != root && current != null) {
            
            parent = current.getParentNode();
            if (parent == root) {
                if (endRoot == null)
                    endRoot = current;
            } else {
                if (partialNode==null) {
                    partialNode = parent;
                    partialInt = BEFORE;
                }
            }
       
            if (parent != root && parent != null) {
                next = current.getPreviousSibling();
                Node nextnext;
                while (next != null) {
                    nextnext = next.getPreviousSibling();
                    removeChild(parent, next);
                    next = nextnext;
                }
            }
            
            if (deleteCurrent) {
                removeChild(parent, current);
                deleteCurrent = false;
            }
            current = parent;
        }
        
        //if (endRoot == null || startRoot == null) return; //REVIST
        current = endRoot.getPreviousSibling();
        Node prev = null;
        while (current != null && current != startRoot ) {
            prev = current.getPreviousSibling();
            parent = current.getParentNode();
            if (parent != null) {
                removeChild(parent, current);
            }
            current = prev;
        }
        
        if (partialNode == null) {
            collapse(true);
        } else 
        if (partialInt == AFTER) {
            setStartAfter(partialNode);
            setEndAfter(partialNode);
        }
        else if (partialInt == BEFORE) {
            setStartBefore(partialNode);
            setEndBefore(partialNode);
        }        
    }
        
    public DocumentFragment extractContents()
        throws DOMException
    {
        return traverseContents(EXTRACT_CONTENTS);
    }
        
    public DocumentFragment cloneContents()
        throws DOMException
    {
        return traverseContents(CLONE_CONTENTS);
    }
    
    public void insertNode(Node newNode)
        throws DOMException, RangeException
    {
    	if ( newNode == null ) return; //throw exception?
        
        if( fDetach) {
    		throw new DOMException(
    			DOMException.INVALID_STATE_ERR, 
			"DOM011 Invalid state");
    	}
        if ( fDocument != newNode.getOwnerDocument() ) {
            throw new DOMException(DOMException.WRONG_DOCUMENT_ERR,"DOM004 Wrong document");
        }
       
        int type = newNode.getNodeType();
        if (type == Node.ATTRIBUTE_NODE
            || type == Node.ENTITY_NODE
            || type == Node.NOTATION_NODE
            || type == Node.DOCUMENT_NODE)
        {
    		throw new RangeExceptionImpl(
    			RangeException.INVALID_NODE_TYPE_ERR, 
			"DOM012 Invalid node type");
        }
        Node cloneCurrent;
        Node current;
        int currentChildren = 0;

        //boolean MULTIPLE_MODE = false;
        if (fStartContainer.getNodeType() == Node.TEXT_NODE) {
        
            Node parent = fStartContainer.getParentNode();
            currentChildren = parent.getChildNodes().getLength(); //holds number of kids before insertion
            // split text node: results is 3 nodes..
            cloneCurrent = fStartContainer.cloneNode(false);
            ((TextImpl)cloneCurrent).setNodeValueInternal(
                    (cloneCurrent.getNodeValue()).substring(fStartOffset));
            ((TextImpl)fStartContainer).setNodeValueInternal(
                    (fStartContainer.getNodeValue()).substring(0,fStartOffset));
            Node next = fStartContainer.getNextSibling();
            if (next != null) {
                    if (parent !=  null) {
                        parent.insertBefore(newNode, next);
                        parent.insertBefore(cloneCurrent, next);
                    }
            } else {
                    if (parent != null) {
                        parent.appendChild(newNode);
                        parent.appendChild(cloneCurrent);
                    }
            }
             //update ranges after the insertion
             if ( fEndContainer == fStartContainer) {
                  fEndContainer = cloneCurrent; //endContainer is the new Node created
                  fEndOffset -= fStartOffset;   
             }
             else if ( fEndContainer == parent ) {    //endContainer was not a text Node.
                  //endOffset + = number_of_children_added
                   fEndOffset += (parent.getChildNodes().getLength() - currentChildren);  
             }

             // signal other Ranges to update their start/end containers/offsets
             signalSplitData(fStartContainer, cloneCurrent, fStartOffset);
                
             
        } else { // ! TEXT_NODE
            if ( fEndContainer == fStartContainer )      //need to remember number of kids
                currentChildren= fEndContainer.getChildNodes().getLength();

            current = fStartContainer.getFirstChild();
            int i = 0;
            for(i = 0; i < fStartOffset && current != null; i++) {
                current=current.getNextSibling();
            }
            if (current != null) {
                fStartContainer.insertBefore(newNode, current);
            } else {
                fStartContainer.appendChild(newNode);
            }
            //update fEndOffset. ex:<body><p/></body>. Range(start;end): body,0; body,1
            // insert <h1>: <body></h1><p/></body>. Range(start;end): body,0; body,2
            if ( fEndContainer == fStartContainer ) {     //update fEndOffset
                fEndOffset += (fEndContainer.getChildNodes().getLength() - currentChildren);
            }

        } 
    }
    
    public void surroundContents(Node newParent)
        throws DOMException, RangeException
    {
        if (newParent==null) return;
        
    	if( fDetach) {
    		throw new DOMException(
    			DOMException.INVALID_STATE_ERR, 
			"DOM011 Invalid state");
    	}
        int type = newParent.getNodeType();
        if (type == Node.ATTRIBUTE_NODE
            || type == Node.ENTITY_NODE
            || type == Node.NOTATION_NODE
            || type == Node.DOCUMENT_TYPE_NODE
            || type == Node.DOCUMENT_NODE
            || type == Node.DOCUMENT_FRAGMENT_NODE)
        {
    		throw new RangeExceptionImpl(
    			RangeException.INVALID_NODE_TYPE_ERR, 
			"DOM012 Invalid node type");
        }
        
        Node root = getCommonAncestorContainer();
        
        Node realStart = fStartContainer;
        Node realEnd = fEndContainer;
        if (fStartContainer.getNodeType() == Node.TEXT_NODE) {
            realStart = fStartContainer.getParentNode();
        }
        if (fEndContainer.getNodeType() == Node.TEXT_NODE) {
            realEnd = fEndContainer.getParentNode();
        }
            
        if (realStart != realEnd) {
           	throw new RangeExceptionImpl(
    		RangeException.BAD_BOUNDARYPOINTS_ERR, 
    		"DOM013 Bad boundary points");
        }

    	DocumentFragment frag = extractContents();
    	insertNode(newParent);
    	newParent.appendChild(frag);
    	selectNode(newParent);
    }
        
    public Range cloneRange(){
    	if( fDetach) {
    		throw new DOMException(
    			DOMException.INVALID_STATE_ERR, 
			"DOM011 Invalid state");
    	}
        
        Range range = fDocument.createRange();
        range.setStart(fStartContainer, fStartOffset);
        range.setEnd(fEndContainer, fEndOffset);
        return range;
    }
    
    public String toString(){
    	if( fDetach) {
    		throw new DOMException(
    			DOMException.INVALID_STATE_ERR, 
			"DOM011 Invalid state");
    	}
    	
    	Node node = fStartContainer;
        Node stopNode = fEndContainer;
    	StringBuffer sb = new StringBuffer();
    	if (fStartContainer.getNodeType() == Node.TEXT_NODE
    	 || fStartContainer.getNodeType() == Node.CDATA_SECTION_NODE
    	) {
    	    if (fStartContainer == fEndContainer) {
    	        sb.append(fStartContainer.getNodeValue().substring(fStartOffset, fEndOffset));
    	        return sb.toString();
            }
    	    sb.append(fStartContainer.getNodeValue().substring(fStartOffset));
            node=nextNode (node,true); //fEndContainer!=fStartContainer
    	    
    	}
        else {  //fStartContainer is not a TextNode
            node=node.getFirstChild();
            if (fStartOffset>0) { //find a first node within a range, specified by fStartOffset
               int counter=0;
               while (counter<fStartOffset && node!=null) {
                   node=node.getNextSibling();
                   counter++;
               }  
            }
            if (node == null) {
                   node = nextNode(fStartContainer,false);
            }
        } 
        if ( fEndContainer.getNodeType()!= Node.TEXT_NODE &&
             fEndContainer.getNodeType()!= Node.CDATA_SECTION_NODE ){
             int i=fEndOffset;
             stopNode = fEndContainer.getFirstChild();
             while( i>0 && stopNode!=null ){
                 --i;
                 stopNode = stopNode.getNextSibling();
             }
             if ( stopNode == null )
                 stopNode = nextNode( fEndContainer, false );
         }
         while (node != stopNode) {  //look into all kids of the Range
             if (node == null) break;
             if (node.getNodeType() == Node.TEXT_NODE
             ||  node.getNodeType() == Node.CDATA_SECTION_NODE) {
                 sb.append(node.getNodeValue());
             }

             node = nextNode(node, true);
         }

      	if (fEndContainer.getNodeType() == Node.TEXT_NODE
    	 || fEndContainer.getNodeType() == Node.CDATA_SECTION_NODE) {
    	    sb.append(fEndContainer.getNodeValue().substring(0,fEndOffset));
    	}
    	return sb.toString();
    }
    
    public void detach() {
        fDetach = true;
        fDocument.removeRange(this);
    }
    
    // 
    // Mutation functions
    //
    
    /** Signal other Ranges to update their start/end 
     *  containers/offsets. The data has already been split
     *  into the two Nodes.
     */
    void signalSplitData(Node node, Node newNode, int offset) {
        fSplitNode = node;
        // notify document
        fDocument.splitData(node, newNode, offset);
        fSplitNode = null;
    }
    
    /** Fix up this Range if another Range has split a Text Node
     *  into 2 Nodes.
     */
    void receiveSplitData(Node node, Node newNode, int offset) {
        if (node == null || newNode == null) return;
        if (fSplitNode == node) return;
        
        if (node == fStartContainer 
        && fStartContainer.getNodeType() == Node.TEXT_NODE) {
            if (fStartOffset > offset) {
                fStartOffset = fStartOffset - offset;
                fStartContainer = newNode;
            }
        }
        if (node == fEndContainer 
        && fEndContainer.getNodeType() == Node.TEXT_NODE) {
            if (fEndOffset > offset) {
                fEndOffset = fEndOffset-offset;
                fEndContainer = newNode;
            }
        }
        
    }
   
    /** This function inserts text into a Node and invokes
     *  a method to fix-up all other Ranges.
     */
    void deleteData(CharacterData node, int offset, int count) {
        fDeleteNode = node;
        node.deleteData( offset,  count);
        fDeleteNode = null;
    }
    
    
    /** This function is called from DOM.
     *  The  text has already beeen inserted.
     *  Fix-up any offsets.
     */
    void receiveDeletedText(Node node, int offset, int count) {
        if (node == null) return;
        if (fDeleteNode == node) return;
        if (node == fStartContainer 
        && fStartContainer.getNodeType() == Node.TEXT_NODE) {
            if (fStartOffset > offset+count) {
                fStartOffset = offset+(fStartOffset-(offset+count));
            } else 
            if (fStartOffset > offset) {
                fStartOffset = offset;
            }  
        }
        if (node == fEndContainer 
        && fEndContainer.getNodeType() == Node.TEXT_NODE) {
            if (fEndOffset > offset+count) {
                fEndOffset = offset+(fEndOffset-(offset+count));
            } else 
            if (fEndOffset > offset) {
                fEndOffset = offset;
            }  
        }
        
    }
   
    /** This function inserts text into a Node and invokes
     *  a method to fix-up all other Ranges.
     */
    void insertData(CharacterData node, int index, String insert) {
        fInsertNode = node;
        node.insertData( index,  insert);
        fInsertNode = null;
    }
    
    
    /** This function is called from DOM.
     *  The  text has already beeen inserted.
     *  Fix-up any offsets.
     */
    void receiveInsertedText(Node node, int index, int len) {
        if (node == null) return;
        if (fInsertNode == node) return;
        if (node == fStartContainer 
        && fStartContainer.getNodeType() == Node.TEXT_NODE) {
            if (index < fStartOffset) {
                fStartOffset = fStartOffset+len;
            }
        }
        if (node == fEndContainer 
        && fEndContainer.getNodeType() == Node.TEXT_NODE) {
            if (index < fEndOffset) {
                fEndOffset = fEndOffset+len;
            }
        }
        
    }
   
    /** This function is called from DOM.
     *  The  text has already beeen replaced.
     *  Fix-up any offsets.
     */
    void receiveReplacedText(Node node) {
        if (node == null) return;
        if (node == fStartContainer 
        && fStartContainer.getNodeType() == Node.TEXT_NODE) {
            fStartOffset = 0;
        }
        if (node == fEndContainer 
        && fEndContainer.getNodeType() == Node.TEXT_NODE) {
            fEndOffset = 0;
        }
        
    }
    
    /** This function is called from the DOM.
     *  This node has already been inserted into the DOM.
     *  Fix-up any offsets.
     */
    public void insertedNodeFromDOM(Node node) {
        if (node == null) return;
        if (fInsertNode == node) return;
        
        Node parent = node.getParentNode();
        
        if (parent == fStartContainer) {
            int index = indexOf(node, fStartContainer);
            if (index < fStartOffset) {
                fStartOffset++;
            }
        }
        
        if (parent == fEndContainer) {
            int index = indexOf(node, fEndContainer);
            if (index < fEndOffset) {
                fEndOffset++;
            }
        }
        
    }
    
    /** This function is called within Range 
     *  instead of Node.removeChild,
     *  so that the range can remember that it is actively
     *  removing this child.
     */
     
    Node fRemoveChild = null;
    Node removeChild(Node parent, Node child) {
        fRemoveChild = child;
        Node n = parent.removeChild(child);
        fRemoveChild = null;
        return n;
    }
    
    /** This function must be called by the DOM _BEFORE_
     *  a node is deleted, because at that time it is
     *  connected in the DOM tree, which we depend on.
     */
    void removeNode(Node node) {
        if (node == null) return;
        if (fRemoveChild == node) return;
        
        Node parent = node.getParentNode();
        
        if (parent == fStartContainer) {
            int index = indexOf(node, fStartContainer);
            if (index <= fStartOffset) {
                fStartOffset--;
            }
        }
        
        if (parent == fEndContainer) {
            int index = indexOf(node, fEndContainer);
            if (index < fEndOffset) {
                fEndOffset--;
            }
        }
   
        if (parent != fStartContainer 
        &&  parent != fEndContainer) {
            if (isAncestorOf(node, fStartContainer)) {
                fStartContainer = parent;
                fStartOffset = indexOf( node, parent)-1;
            }   
            if (isAncestorOf(node, fEndContainer)) {
                fEndContainer = parent;
                fEndOffset = indexOf( node, parent)-1;
            }
        } 
        
    }
        
    //
    // Utility functions.
    //
    
    // parameters for traverseContents(int)
    //REVIST: use boolean, since there are only 2 now...
    static final int EXTRACT_CONTENTS = 1;
    static final int CLONE_CONTENTS = 2;
    
    /** This is the master traversal function which is used by 
     *  both extractContents and cloneContents().
     */
    DocumentFragment traverseContents(int traversalType)
        throws DOMException
    {
        if (fStartContainer == null || fEndContainer == null) {
            return null; // REVIST: Throw exception?
        }
        
        DocumentFragment frag = fDocument.createDocumentFragment();
        
        
        Node current = fStartContainer;
        Node cloneCurrent = null;
        Node cloneParent = null;
        Node partialNode = null;
        int partialInt = START;
        
        Vector d = new Vector();
        
        // if same container, simplify case
        if (fStartContainer == fEndContainer) {
            if (fStartOffset == fEndOffset) { // eg collapsed
                return frag; // REVIST: what is correct re spec?
            } 
            if (fStartContainer.getNodeType() == Node.TEXT_NODE) {
                cloneCurrent = fStartContainer.cloneNode(false);
                cloneCurrent.setNodeValue(
                (cloneCurrent.getNodeValue()).substring(fStartOffset, fEndOffset));
                if (traversalType == EXTRACT_CONTENTS) {
                    deleteData((CharacterData)current, fStartOffset, fEndOffset-fStartOffset);
                }
                frag.appendChild(cloneCurrent);
            } else {
                current = current.getFirstChild();
                int i = 0;
                for(i = 0; i < fStartOffset && current != null; i++) {
                    current=current.getNextSibling();
                }
                int n = fEndOffset-fStartOffset;
                for(i = 0; i < n && current != null ;i++) {
                    Node newCurrent=current.getNextSibling();
                
                    if (traversalType == CLONE_CONTENTS) {
                        cloneCurrent = current.cloneNode(true);
                        frag.appendChild(cloneCurrent);
                    } else
                    if (traversalType == EXTRACT_CONTENTS) {
                        frag.appendChild(current);
                    }
                    current = newCurrent;
                }
            }
            return frag;
        }
        
        //***** END SIMPLE CASE ****
   
        Node root = getCommonAncestorContainer();
        Node parent = null;
        
        // go up the start tree...
        current = fStartContainer;
        
        //REVIST: Always clone TEXT_NODE's?
        if (current.getNodeType() == Node.TEXT_NODE) {
            cloneCurrent = current.cloneNode(false);
            cloneCurrent.setNodeValue(
                (cloneCurrent.getNodeValue()).substring(fStartOffset));
            if (traversalType == EXTRACT_CONTENTS) {
                deleteData((CharacterData)current, fStartOffset, 
                    current.getNodeValue().length()-fStartOffset);
            }
        } else {
            current = current.getFirstChild();
            for(int i = 0; i < fStartOffset && current != null; i++) {
                current=current.getNextSibling();
            }
            // current is now at the offset.
            if (current==null) { //"after"
                current = fStartContainer;
            }
        
            if (traversalType == CLONE_CONTENTS) {
                cloneCurrent = current.cloneNode(true);
            } else
            if (traversalType == EXTRACT_CONTENTS ) {
                cloneCurrent = current;
            }
        }
        
        Node startRoot = null;
        parent = null;
        
        // going up in a direct line from boundary point 
        // through parents to the common ancestor,
        // all these nodes are partially selected, and must
        // be cloned.
        while (current != root) {
            parent = current.getParentNode();

            if (parent == root) {
                cloneParent = frag;
                startRoot = current;
            } else {
                if (parent == null) System.out.println("parent==null: current="+current);
                cloneParent = parent.cloneNode(false);
                if (partialNode==null && parent != root) {
                    partialNode = parent;
                    partialInt = AFTER;
                }
                
            }
            
            // The children to thr "right" of the "ancestor hierarchy"
            // are "fully-selected".
            Node next = null;
            
            //increment to the next sibling BEFORE doing the appendChild
            current = current.getNextSibling();
            
            //do this appendChild after the increment above.
            cloneParent.appendChild(cloneCurrent);
                     
            while (current != null) {
                next = current.getNextSibling();
                if (current != null && parent != root) {
                    if (traversalType == CLONE_CONTENTS) {
                        cloneCurrent = current.cloneNode(true);
                        cloneParent.appendChild(cloneCurrent);
                    } else
                    if (traversalType == EXTRACT_CONTENTS) {
                        cloneParent.appendChild(current);
                    }
                }
                current = next;
            }
            
            current = parent;
            cloneCurrent = cloneParent;
        }
        
        // go up the end tree...
        Node endRoot = null;
        current = fEndContainer;
        
        if (current.getNodeType() == Node.TEXT_NODE) {
            cloneCurrent = current.cloneNode(false);
            cloneCurrent.setNodeValue(
                (cloneCurrent.getNodeValue()).substring(0,fEndOffset));
            if (traversalType == EXTRACT_CONTENTS) {
                deleteData((CharacterData)current, 0, fEndOffset); 
            } 
        } else {
            if (fEndOffset == 0) { // "before"
                current = fEndContainer;
            }
            else {
                current = current.getFirstChild();
                for(int i = 1; i < fEndOffset && current != null; i++) {
                    current=current.getNextSibling();
                }
                if (current==null) { // REVIST: index-out-of-range what to do?
                    current = fEndContainer.getLastChild();
                }
            }
            if (traversalType == CLONE_CONTENTS) {
                cloneCurrent = current.cloneNode(true);
            } else
            if (traversalType == EXTRACT_CONTENTS ) {
                cloneCurrent = current;
            }
        }
                
        while (current != root && current != null) {
            parent = current.getParentNode();
            if (parent == root) {
                cloneParent = frag;
                endRoot = current;
            } else {
                cloneParent = parent.cloneNode(false);
                if (partialNode==null && parent != root) {
                    partialNode = parent;
                    partialInt = BEFORE;
                }
            }
            
            Node holdCurrent = current;
                
            current = parent.getFirstChild();
            
            cloneParent.appendChild(cloneCurrent);
          
            Node next = null;
            while (current != holdCurrent && current != null) {
                next = current.getNextSibling();
                // The leftmost children are fully-selected
                // and are removed, and appended, not cloned.
                if (current != null && parent != root) {
                    if (traversalType == CLONE_CONTENTS) {
                        cloneCurrent = current.cloneNode(true);
                        cloneParent.appendChild(cloneCurrent);
                    } else
                    if (traversalType == EXTRACT_CONTENTS) {
                        //cloneCurrent = current;
                        cloneParent.appendChild(current);
                    }
                }
                current = next;
            }
            
            current = parent;
            cloneCurrent = cloneParent;
        
        }
        
        d.removeAllElements();
        
        // traverse the "fully-selected" middle...
        Node clonedPrevious = frag.getLastChild();
        current = endRoot.getPreviousSibling();
        Node prev = null;
        while (current != startRoot && current != null) {
            prev = current.getPreviousSibling();
            
            if (traversalType == CLONE_CONTENTS) {
                cloneCurrent = current.cloneNode(true);
            } else
            if (traversalType == EXTRACT_CONTENTS) {
                cloneCurrent = current;
            } 
                        
            frag.insertBefore(cloneCurrent, clonedPrevious);
            
            current = prev;
            clonedPrevious = cloneCurrent;
        }

        // collapse the range...
        if (traversalType == EXTRACT_CONTENTS ) {
            if (partialNode == null) {
                collapse(true);
            } else 
            if (partialInt == AFTER) {
                setStartAfter(partialNode);
                setEndAfter(partialNode);
            }
            else if (partialInt == BEFORE) {
                setStartBefore(partialNode);
                setEndBefore(partialNode);
            }          
        }
        
        return frag;
            
    }
    
    void checkIndex(Node refNode, int offset) throws DOMException
    {
        if (offset < 0) {
            throw new DOMException(
                                   DOMException.INDEX_SIZE_ERR, 
                                   "DOM004 Index out of bounds");
    	}

        int type = refNode.getNodeType();
        
        // If the node contains text, ensure that the
        // offset of the range is <= to the length of the text
        if (type == Node.TEXT_NODE
            || type == Node.CDATA_SECTION_NODE
            || type == Node.COMMENT_NODE
            || type == Node.PROCESSING_INSTRUCTION_NODE) {
            if (offset > refNode.getNodeValue().length()) {
                throw new DOMException(DOMException.INDEX_SIZE_ERR, 
                                       "DOM004 Index out of bounds");
            }
        }
        else {
            // Since the node is not text, ensure that the offset
            // is valid with respect to the number of child nodes
            if (offset > refNode.getChildNodes().getLength()) {
    		throw new DOMException(DOMException.INDEX_SIZE_ERR, 
                                       "DOM004 Index out of bounds");
            }
        }
    }

	/**
	 * Given a node, calculate what the Range's root container
	 * for that node would be.
	 */
	private Node getRootContainer( Node node )
	{
		if ( node==null )
			return null;

		while( node.getParentNode()!=null )
			node = node.getParentNode();
		return node;
	}

	/**
	 * Returns true IFF the given node can serve as a container
	 * for a range's boundary points.
	 */
	private boolean isLegalContainer( Node node )
	{
		if ( node==null )
			return false;

		while( node!=null )
		{
			switch( node.getNodeType() )
			{
			case Node.ENTITY_NODE:
			case Node.NOTATION_NODE:
			case Node.DOCUMENT_TYPE_NODE:
				return false;
			}
			node = node.getParentNode();
		}

		return true;
	}


	/**
	 * Finds the root container for the given node and determines
	 * if that root container is legal with respect to the
	 * DOM 2 specification.  At present, that means the root
	 * container must be either an attribute, a document,
	 * or a document fragment.
	 */
	private boolean hasLegalRootContainer( Node node )
	{
		if ( node==null )
			return false;

		Node rootContainer = getRootContainer( node );
		switch( rootContainer.getNodeType() )
		{
		case Node.ATTRIBUTE_NODE:
		case Node.DOCUMENT_NODE:
		case Node.DOCUMENT_FRAGMENT_NODE:
			return true;
		}
		return false;
	}

	/**
	 * Returns true IFF the given node can be contained by
	 * a range.
	 */
	private boolean isLegalContainedNode( Node node )
	{
		if ( node==null )
			return false;
		switch( node.getNodeType() )
		{
		case Node.DOCUMENT_NODE:
		case Node.DOCUMENT_FRAGMENT_NODE:
		case Node.ATTRIBUTE_NODE:
		case Node.ENTITY_NODE:
		case Node.NOTATION_NODE:
			return false;
		}
		return true;
	}

    Node nextNode(Node node, boolean visitChildren) {
            
        if (node == null) return null;

        Node result;
        if (visitChildren) {
            result = node.getFirstChild();
            if (result != null) {
                return result;
            }
        }
            
        // if hasSibling, return sibling
        result = node.getNextSibling();
        if (result != null) {
            return result;
        }
        
                
        // return parent's 1st sibling.
        Node parent = node.getParentNode();
        while (parent != null
               && parent != fDocument
                ) {
            result = parent.getNextSibling();
            if (result != null) {
                return result;
            } else {
                parent = parent.getParentNode();
            }
                            
        } // while (parent != null && parent != fRoot) {
        
        // end of list, return null
        return null;            
    }
    
    /** is a an ancestor of b ? */
    boolean isAncestorOf(Node a, Node b) {
        for (Node node=b; node != null; node=node.getParentNode()) {
            if (node == a) return true;
        }
        return false;
    }

    /** what is the index of the child in the parent */
    int indexOf(Node child, Node parent) {
        Node node;
        int i = 0;
        if (child.getParentNode() != parent) return -1;
        for(node = child; node!= null; node=node.getPreviousSibling()) {
            i++;
        }
        return i;
    }

}
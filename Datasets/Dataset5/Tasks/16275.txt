serializer.fNSBinder.reset();

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 1999-2002 The Apache Software Foundation.  All rights
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
 * originally based on software copyright (c) 2002, International
 * Business Machines, Inc., http://www.apache.org.  For more
 * information on the Apache Software Foundation, please see
 * <http://www.apache.org/>.
 */



package org.apache.xml.serialize;

import org.w3c.dom.Node;
import org.w3c.dom.Document;
import org.w3c.dom.DocumentFragment;
import org.w3c.dom.Element;
import org.w3c.dom.DOMException;
import org.w3c.dom.DOMErrorHandler;
import org.w3c.dom.DOMErrorHandler;
import org.w3c.dom.ls.DOMWriter;
import org.w3c.dom.ls.DOMWriterFilter;
import org.w3c.dom.traversal.NodeFilter;

import org.apache.xerces.impl.Constants;
import org.apache.xerces.util.SymbolTable;
import org.apache.xerces.util.XMLSymbols;
import org.apache.xerces.util.NamespaceSupport;

import java.io.IOException;
import java.io.OutputStream;
import java.io.Writer;
import java.io.StringWriter;
import java.util.Hashtable;


/**
 * Implemenatation of DOM Level 3 org.w3c.ls.DOMWriter  by delegating serialization 
 * calls to <CODE>XMLSerializer</CODE>. 
 * DOMWriter provides an API for serializing (writing) a DOM document out in an
 * XML document. The XML data is written to an output stream.
 * During serialization of XML data, namespace fixup is done when possible as
 * defined in DOM Level 3 Core, Appendix B.
 * 
 * @author Elena Litani, IBM
 * @version $Id$
 */
public class DOMWriterImpl implements DOMWriter {

    // data
    private String fEncoding; 

    // serializer
    private XMLSerializer serializer;

    /**
     * Constructs a new DOMWriter.
     * The constructor turns on the namespace support in <code>XMLSerializer</code> and
     * initializes the following fields: fNSBinder, fLocalNSBinder, fSymbolTable, 
     * fEmptySymbol, fXmlSymbol, fXmlnsSymbol, fNamespaceCounter, fFeatures.
     */
    public DOMWriterImpl(boolean namespaces) {
        serializer = new XMLSerializer();
        serializer.fNamespaces = namespaces;
        serializer.fNSBinder = new NamespaceSupport();
        serializer.fLocalNSBinder = new NamespaceSupport();
        serializer.fSymbolTable = new SymbolTable();
        serializer.fFeatures = new Hashtable();
        serializer.fFeatures.put(Constants.DOM_NORMALIZE_CHARACTERS, new Boolean(false));
        serializer.fFeatures.put(Constants.DOM_SPLIT_CDATA, new Boolean(true));
        serializer.fFeatures.put(Constants.DOM_VALIDATE, new Boolean(false));
        serializer.fFeatures.put(Constants.DOM_ENTITIES, new Boolean(false));
        serializer.fFeatures.put(Constants.DOM_WHITESPACE_IN_ELEMENT_CONTENT, new Boolean(true));
        serializer.fFeatures.put(Constants.DOM_DISCARD_DEFAULT_CONTENT, new Boolean(true));
        serializer.fFeatures.put(Constants.DOM_CANONICAL_FORM, new Boolean(false));
        serializer.fFeatures.put(Constants.DOM_FORMAT_PRETTY_PRINT, new Boolean(false));
    }



    //
    // DOMWriter methods   
    //


    /**
     * DOM L3-EXPERIMENTAL: Set the state of a feature.
     * <br>The feature name has the same form as a DOM hasFeature string.
     * <br>It is possible for a <code>DOMWriter</code> to recognize a feature 
     * name but to be unable to set its value.
     * @param name The feature name.
     * @param state The requested state of the feature (<code>true</code> or 
     *   <code>false</code>).
     * @exception DOMException
     *   Raise a NOT_SUPPORTED_ERR exception when the <code>DOMWriter</code> 
     *   recognizes the feature name but cannot set the requested value. 
     *   <br>Raise a NOT_FOUND_ERR When the <code>DOMWriter</code> does not 
     *   recognize the feature name.
     */
    public void setFeature(String name, boolean state) throws DOMException {
        if (name != null && serializer.fFeatures.containsKey(name))
            if (canSetFeature(name,state))
                serializer.fFeatures.put(name,new Boolean(state));
            else
                throw new DOMException(DOMException.NOT_SUPPORTED_ERR,"Feature "+name+" cannot be set as "+state);
        else
            throw new DOMException(DOMException.NOT_FOUND_ERR,"Feature "+name+" not found");
    }

    /**
     * DOM L3-EXPERIMENTAL: Query whether setting a feature to a specific value is supported.
     * <br>The feature name has the same form as a DOM hasFeature string.
     * @param name The feature name, which is a DOM has-feature style string.
     * @param state The requested state of the feature (<code>true</code> or 
     *   <code>false</code>).
     * @return <code>true</code> if the feature could be successfully set to 
     *   the specified value, or <code>false</code> if the feature is not 
     *   recognized or the requested value is not supported. The value of 
     *   the feature itself is not changed.
     */
    public boolean canSetFeature(String name, boolean state) {
        if (name.equals(Constants.DOM_NORMALIZE_CHARACTERS) && state)
            return false;     
        else if (name.equals(Constants.DOM_VALIDATE) && state)
            return false;
        else if (name.equals(Constants.DOM_WHITESPACE_IN_ELEMENT_CONTENT) && !state)
            return false;
        else if (name.equals(Constants.DOM_CANONICAL_FORM) && state)
            return false;
        else if (name.equals(Constants.DOM_FORMAT_PRETTY_PRINT) && state)
            return false;
        else
            return true;
    }   

    /**
     * DOM L3-EXPERIMENTAL: Look up the value of a feature.
     * <br>The feature name has the same form as a DOM hasFeature string
     * @param name The feature name, which is a string with DOM has-feature 
     *   syntax.
     * @return The current state of the feature (<code>true</code> or 
     *   <code>false</code>).
     * @exception DOMException
     *   Raise a NOT_FOUND_ERR When the <code>DOMWriter</code> does not 
     *   recognize the feature name.
     */
    public boolean getFeature(String name) throws DOMException {
        Boolean state = (Boolean)serializer.fFeatures.get(name);
        if (state == null)
            throw new DOMException(DOMException.NOT_FOUND_ERR,"Feature "+name+" not found");
        return state.booleanValue();
    }

    /**
     * DOM L3 EXPERIMENTAL: 
     *  The character encoding in which the output will be written. 
     * <br> The encoding to use when writing is determined as follows: If the 
     * encoding attribute has been set, that value will be used.If the 
     * encoding attribute is <code>null</code> or empty, but the item to be 
     * written includes an encoding declaration, that value will be used.If 
     * neither of the above provides an encoding name, a default encoding of 
     * "UTF-8" will be used.
     * <br>The default value is <code>null</code>.
     */
    public String getEncoding() {
        return fEncoding;
    }

    /**
     * DOM L3 EXPERIMENTAL: 
     *  The character encoding in which the output will be written. 
     * <br> The encoding to use when writing is determined as follows: If the 
     * encoding attribute has been set, that value will be used.If the 
     * encoding attribute is <code>null</code> or empty, but the item to be 
     * written includes an encoding declaration, that value will be used.If 
     * neither of the above provides an encoding name, a default encoding of 
     * "UTF-8" will be used.
     * <br>The default value is <code>null</code>.
     */
    public void setEncoding(String encoding) {
        serializer._format.setEncoding(encoding);
        fEncoding = serializer._format.getEncoding();
    }

    /**
     *  The error handler that will receive error notifications during 
     * serialization. The node where the error occured is passed to this 
     * error handler, any modification to nodes from within an error 
     * callback should be avoided since this will result in undefined, 
     * implementation dependent behavior. 
     */
    public DOMErrorHandler getErrorHandler() {
        return serializer.fDOMErrorHandler;
    }

    /**
     * DOM L3 EXPERIMENTAL: 
     *  The error handler that will receive error notifications during 
     * serialization. The node where the error occured is passed to this 
     * error handler, any modification to nodes from within an error 
     * callback should be avoided since this will result in undefined, 
     * implementation dependent behavior. 
     */
    public void setErrorHandler(DOMErrorHandler errorHandler) {
        serializer.fDOMErrorHandler = errorHandler;
    }

    /**
     * DOM L3 EXPERIMENTAL: 
     * Write out the specified node as described above in the description of 
     * <code>DOMWriter</code>. Writing a Document or Entity node produces a 
     * serialized form that is well formed XML. Writing other node types 
     * produces a fragment of text in a form that is not fully defined by 
     * this document, but that should be useful to a human for debugging or 
     * diagnostic purposes. 
     * @param destination The destination for the data to be written.
     * @param wnode The <code>Document</code> or <code>Entity</code> node to 
     *   be written. For other node types, something sensible should be 
     *   written, but the exact serialized form is not specified.
     * @return  Returns <code>true</code> if <code>node</code> was 
     *   successfully serialized and <code>false</code> in case a failure 
     *   occured and the failure wasn't canceled by the error handler. 
     * @exception DOMSystemException
     *   This exception will be raised in response to any sort of IO or system 
     *   error that occurs while writing to the destination. It may wrap an 
     *   underlying system exception.
     */
    public boolean writeNode(java.io.OutputStream destination, 
                             Node wnode)
    throws Exception {
        checkAllFeatures();
        try {
            reset();
            serializer.setOutputByteStream(destination);
            if (wnode == null)
                return false;
            else if (wnode.getNodeType() == Node.DOCUMENT_NODE)
                serializer.serialize((Document)wnode);
            else if (wnode.getNodeType() == Node.DOCUMENT_FRAGMENT_NODE)
                serializer.serialize((DocumentFragment)wnode);
            else if (wnode.getNodeType() == Node.ELEMENT_NODE)
                serializer.serialize((Element)wnode);
            else
                return false;
        } catch (NullPointerException npe) {
            throw npe;
        } catch (IOException ioe) {
            throw ioe;
        }
        return true;
    }

    /**
     * DOM L3 EXPERIMENTAL: 
     *  Serialize the specified node as described above in the description of 
     * <code>DOMWriter</code>. The result of serializing the node is 
     * returned as a string. Writing a Document or Entity node produces a 
     * serialized form that is well formed XML. Writing other node types 
     * produces a fragment of text in a form that is not fully defined by 
     * this document, but that should be useful to a human for debugging or 
     * diagnostic purposes. 
     * @param wnode  The node to be written. 
     * @return  Returns the serialized data, or <code>null</code> in case a 
     *   failure occured and the failure wasn't canceled by the error 
     *   handler. 
     * @exception DOMException
     *    DOMSTRING_SIZE_ERR: The resulting string is too long to fit in a 
     *   <code>DOMString</code>. 
     */
    public String writeToString(Node wnode)
    throws DOMException {
        checkAllFeatures();
        StringWriter destination = new StringWriter();
        try {
            reset();
            serializer.setOutputCharStream(destination);
            if (wnode == null)
                return null;
            else if (wnode.getNodeType() == Node.DOCUMENT_NODE)
                serializer.serialize((Document)wnode);
            else if (wnode.getNodeType() == Node.DOCUMENT_FRAGMENT_NODE)
                serializer.serialize((DocumentFragment)wnode);
            else if (wnode.getNodeType() == Node.ELEMENT_NODE)
                serializer.serialize((Element)wnode);
            else
                return null;
        } catch (IOException ioe) {
            throw new DOMException(DOMException.DOMSTRING_SIZE_ERR,"The resulting string is too long to fit in a DOMString: "+ioe.getMessage());
        }
        return destination.toString();
    }

    /**
     * DOM L3 EXPERIMENTAL: 
     * The end-of-line sequence of characters to be used in the XML being 
     * written out. The only permitted values are these: 
     * <dl>
     * <dt><code>null</code></dt>
     * <dd> 
     * Use a default end-of-line sequence. DOM implementations should choose 
     * the default to match the usual convention for text files in the 
     * environment being used. Implementations must choose a default 
     * sequence that matches one of those allowed by  2.11 "End-of-Line 
     * Handling". </dd>
     * <dt>CR</dt>
     * <dd>The carriage-return character (#xD).</dd>
     * <dt>CR-LF</dt>
     * <dd> The 
     * carriage-return and line-feed characters (#xD #xA). </dd>
     * <dt>LF</dt>
     * <dd> The line-feed 
     * character (#xA). </dd>
     * </dl>
     * <br>The default value for this attribute is <code>null</code>.
     */
    public void setNewLine(String newLine) {
        serializer._format.setLineSeparator(newLine);
    }


    /**
     * DOM L3 EXPERIMENTAL: 
     * The end-of-line sequence of characters to be used in the XML being 
     * written out. The only permitted values are these: 
     * <dl>
     * <dt><code>null</code></dt>
     * <dd> 
     * Use a default end-of-line sequence. DOM implementations should choose 
     * the default to match the usual convention for text files in the 
     * environment being used. Implementations must choose a default 
     * sequence that matches one of those allowed by  2.11 "End-of-Line 
     * Handling". </dd>
     * <dt>CR</dt>
     * <dd>The carriage-return character (#xD).</dd>
     * <dt>CR-LF</dt>
     * <dd> The 
     * carriage-return and line-feed characters (#xD #xA). </dd>
     * <dt>LF</dt>
     * <dd> The line-feed 
     * character (#xA). </dd>
     * </dl>
     * <br>The default value for this attribute is <code>null</code>.
     */
    public String getNewLine() {
        return serializer._format.getLineSeparator();
    }


    /**
     *  When the application provides a filter, the serializer will call out 
     * to the filter before serializing each Node. Attribute nodes are never 
     * passed to the filter. The filter implementation can choose to remove 
     * the node from the stream or to terminate the serialization early. 
     */
    public DOMWriterFilter getFilter(){
        return null;
    }
    /**
     *  When the application provides a filter, the serializer will call out 
     * to the filter before serializing each Node. Attribute nodes are never 
     * passed to the filter. The filter implementation can choose to remove 
     * the node from the stream or to terminate the serialization early. 
     */
    public void setFilter(DOMWriterFilter filter){
        serializer.fDOMFilter = filter;
    }


    private boolean reset() {
        serializer.reset();
        serializer.fNSBinder.reset(serializer.fSymbolTable);
        // during serialization always have a mapping to empty string
        // so we assume there is a declaration.
        serializer.fNSBinder.declarePrefix(XMLSymbols.EMPTY_STRING, XMLSymbols.EMPTY_STRING);
        serializer.fNamespaceCounter = 1;
        return true;

    }


    private void checkAllFeatures() {
        if (getFeature("whitespace-in-element-content"))
            serializer._format.setPreserveSpace(true);
        else
            serializer._format.setPreserveSpace(false);
    }


}




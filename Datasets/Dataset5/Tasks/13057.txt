if (getParameter(Constants.DOM_WHITESPACE_IN_ELEMENT_CONTENT) == Boolean.TRUE)

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

import org.apache.xerces.dom3.DOMErrorHandler;
import org.apache.xerces.dom3.DOMConfiguration;
import org.w3c.dom.ls.DOMWriter;
import org.w3c.dom.ls.DOMWriterFilter;
import org.w3c.dom.traversal.NodeFilter;

import org.apache.xerces.dom.DOMMessageFormatter;
import org.apache.xerces.dom.DOMErrorImpl;
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
public class DOMWriterImpl implements DOMWriter, DOMConfiguration {

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
    public DOMWriterImpl() {
        serializer = new XMLSerializer();
        serializer.fNamespaces = true;
        serializer.fNSBinder = new NamespaceSupport();
        serializer.fLocalNSBinder = new NamespaceSupport();
        serializer.fSymbolTable = new SymbolTable();
        serializer.fFeatures = new Hashtable();
        serializer.fFeatures.put(Constants.NAMESPACES_FEATURE, Boolean.TRUE);
        serializer.fFeatures.put(Constants.DOM_NORMALIZE_CHARACTERS, Boolean.FALSE);
        serializer.fFeatures.put(Constants.DOM_SPLIT_CDATA, Boolean.TRUE);
        serializer.fFeatures.put(Constants.DOM_VALIDATE, Boolean.FALSE);
        serializer.fFeatures.put(Constants.DOM_ENTITIES, Boolean.FALSE);
        serializer.fFeatures.put(Constants.DOM_WHITESPACE_IN_ELEMENT_CONTENT, Boolean.TRUE);
        serializer.fFeatures.put(Constants.DOM_DISCARD_DEFAULT_CONTENT, Boolean.TRUE);
        serializer.fFeatures.put(Constants.DOM_CANONICAL_FORM, Boolean.FALSE);
        serializer.fFeatures.put(Constants.DOM_FORMAT_PRETTY_PRINT, Boolean.FALSE);
        serializer.fFeatures.put(Constants.DOM_XMLDECL, Boolean.TRUE);
        serializer.fFeatures.put(Constants.DOM_UNKNOWNCHARS, Boolean.TRUE);
    }



    //
    // DOMWriter methods   
    //
    
    public DOMConfiguration getConfig(){
        return this;
    }

    /** DOM L3-EXPERIMENTAL: 
     * Setter for boolean and object parameters
     */
	public void setParameter(String name, Object value) throws DOMException {
		if (serializer.fFeatures.containsKey(name)) {
			// This is a feature
			if (value instanceof Boolean) {
				if (canSetParameter(name, value)) {
					serializer.fFeatures.put(name, value);
					if (name.equals(Constants.DOM_XMLDECL)) {
						serializer._format.setOmitXMLDeclaration(
							!((Boolean) value).booleanValue());
					}
                    else if (name.equals(Constants.DOM_NAMESPACES)){
                        serializer.fNamespaces = (value==Boolean.TRUE)?true:false;
                    }
				}
				else {
					String msg = DOMMessageFormatter.formatMessage(
							DOMMessageFormatter.DOM_DOMAIN,
							"FEATURE_NOT_SUPPORTED",
							new Object[] { name });
                    throw new DOMException(DOMException.NOT_SUPPORTED_ERR, msg);
				}
			}
            else {
                // REVISIT: should be TYPE_MISMATCH
                String msg = DOMMessageFormatter.formatMessage(
                            DOMMessageFormatter.DOM_DOMAIN,
                            "FEATURE_NOT_SUPPORTED",
                            new Object[] { name });
                throw new DOMException(DOMException.NOT_SUPPORTED_ERR, msg);
            }
		}
		else if (name.equals(Constants.DOM_ERROR_HANDLER)) {
			if (value instanceof DOMErrorHandler) {
				serializer.fDOMErrorHandler = (DOMErrorHandler) value;
			}
			else {
				// REVISIT: modify error exception to TYPE_MISMATCH
                String msg = DOMMessageFormatter.formatMessage(
                            DOMMessageFormatter.DOM_DOMAIN,
                            "FEATURE_NOT_SUPPORTED",
                            new Object[] { name });
               throw new DOMException(DOMException.NOT_SUPPORTED_ERR, msg);
			}
		}
		else if (name.equals(Constants.DOM_ENTITY_RESOLVER)
				|| name.equals(Constants.DOM_SCHEMA_LOCATION)
				|| name.equals(Constants.DOM_SCHEMA_TYPE)) {
                String msg = DOMMessageFormatter.formatMessage(
                            DOMMessageFormatter.DOM_DOMAIN,
                            "FEATURE_NOT_SUPPORTED",
                            new Object[] { name });
               throw new DOMException(DOMException.NOT_SUPPORTED_ERR, msg);
		}
		else {
                String msg = DOMMessageFormatter.formatMessage(
                            DOMMessageFormatter.DOM_DOMAIN,
                            "FEATURE_NOT_FOUND",
                            new Object[] { name });		
                throw new DOMException(DOMException.NOT_FOUND_ERR, msg);
        }
	}
    
    /** DOM L3-EXPERIMENTAL: 
     * Check if parameter can be set
     */
	public boolean canSetParameter(String name, Object state) {
		if (name.equals(Constants.DOM_NORMALIZE_CHARACTERS) 
			&& state == Boolean.TRUE){
			return false;
		}
		else if (name.equals(Constants.DOM_VALIDATE) && state == Boolean.TRUE) {
			return false;
		}
		else if (name.equals(Constants.DOM_WHITESPACE_IN_ELEMENT_CONTENT)
				&& state == Boolean.FALSE) {
			return false;
		}
		else if (name.equals(Constants.DOM_CANONICAL_FORM)
				&& state == Boolean.TRUE) {
			return false;
		}
		else if (name.equals(Constants.DOM_FORMAT_PRETTY_PRINT)
				&& state == Boolean.TRUE) {
			return false;
		}
        else if (serializer.fFeatures.get(name)!=null ||
            name.equals(Constants.DOM_ERROR_HANDLER)){
            return true;
        }
	    return false; 
    }
    
    /** DOM L3-EXPERIMENTAL: 
     * Getter for boolean and object parameters
     */
	public Object getParameter(String name) throws DOMException {
		Object state = serializer.fFeatures.get(name);
		if (state == null) {
			if (name.equals(Constants.DOM_ERROR_HANDLER)) {
				return serializer.fDOMErrorHandler;
			}
			else if (name.equals(Constants.DOM_ENTITY_RESOLVER)
					|| name.equals(Constants.DOM_SCHEMA_LOCATION)
					|| name.equals(Constants.DOM_SCHEMA_TYPE)) {
				String msg =
					DOMMessageFormatter.formatMessage(
						DOMMessageFormatter.DOM_DOMAIN,
						"FEATURE_NOT_SUPPORTED",
						new Object[] { name });
				throw new DOMException(DOMException.NOT_SUPPORTED_ERR, msg);
			}
			else {
				String msg =
					DOMMessageFormatter.formatMessage(
						DOMMessageFormatter.DOM_DOMAIN,
						"FEATURE_NOT_FOUND",
						new Object[] { name });
				throw new DOMException(DOMException.NOT_FOUND_ERR, msg);
			}
		}

		return ((Boolean) state);
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
     * @exception none
     */
    public boolean writeNode(java.io.OutputStream destination, 
                             Node wnode) {
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
        } catch (Exception e) {
            if (serializer.fDOMErrorHandler != null) {
                  DOMErrorImpl error = new DOMErrorImpl();
                  error.fException = e;
                  error.fMessage = e.getMessage();
                  error.fSeverity = error.SEVERITY_ERROR;
                  serializer.fDOMErrorHandler.handleError(error);

            }
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
        serializer.fNSBinder.reset();
        // during serialization always have a mapping to empty string
        // so we assume there is a declaration.
        serializer.fNSBinder.declarePrefix(XMLSymbols.EMPTY_STRING, XMLSymbols.EMPTY_STRING);
        serializer.fNamespaceCounter = 1;
        return true;

    }


    private void checkAllFeatures() {
        if (getFeature(Constants.DOM_WHITESPACE_IN_ELEMENT_CONTENT))
            serializer._format.setPreserveSpace(true);
        else
            serializer._format.setPreserveSpace(false);
    }


}




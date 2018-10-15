return new DOMWriterImpl();

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
 * originally based on software copyright (c) 1999, International
 * Business Machines, Inc., http://www.apache.org.  For more
 * information on the Apache Software Foundation, please see
 * <http://www.apache.org/>.
 */
package org.apache.xerces.dom;
import org.w3c.dom.DOMException;
import org.w3c.dom.DOMImplementation;
import org.w3c.dom.Document;
import org.w3c.dom.DocumentType;
import org.w3c.dom.Element;
// DOM L3 LS
import org.w3c.dom.ls.DOMImplementationLS;
import org.w3c.dom.ls.DOMBuilder;
import org.w3c.dom.ls.DOMWriter;
import org.w3c.dom.ls.DOMInputSource;
import org.apache.xerces.parsers.DOMBuilderImpl;
import org.apache.xerces.util.XMLChar;
import org.apache.xml.serialize.DOMWriterImpl;
// DOM Revalidation
import org.apache.xerces.impl.RevalidationHandler;
import org.apache.xerces.util.ObjectFactory;
/**
 * The DOMImplementation class is description of a particular
 * implementation of the Document Object Model. As such its data is
 * static, shared by all instances of this implementation.
 * <P>
 * The DOM API requires that it be a real object rather than static
 * methods. However, there's nothing that says it can't be a singleton,
 * so that's how I've implemented it.
 * <P>
 * This particular class, along with CoreDocumentImpl, supports the DOM
 * Core and Load/Save (Experimental). Optional modules are supported by 
 * the more complete DOMImplementation class along with DocumentImpl.
 * @version $Id$
 * @since PR-DOM-Level-1-19980818.
 */
public class CoreDOMImplementationImpl
	implements DOMImplementation, DOMImplementationLS {
	//
	// Data
	//
	RevalidationHandler fDOMRevalidator = null;
	boolean free = true;
	// static
	/** Dom implementation singleton. */
	static CoreDOMImplementationImpl singleton =
		new CoreDOMImplementationImpl();
	//
	// Public methods
	//
	/** NON-DOM: Obtain and return the single shared object */
	public static DOMImplementation getDOMImplementation() {
		return singleton;
	}
	//
	// DOMImplementation methods
	//
	/** 
	 * Test if the DOM implementation supports a specific "feature" --
	 * currently meaning language and level thereof.
	 * 
	 * @param feature      The package name of the feature to test.
	 * In Level 1, supported values are "HTML" and "XML" (case-insensitive).
	 * At this writing, org.apache.xerces.dom supports only XML.
	 *
	 * @param version      The version number of the feature being tested.
	 * This is interpreted as "Version of the DOM API supported for the
	 * specified Feature", and in Level 1 should be "1.0"
	 *
	 * @return    true iff this implementation is compatable with the specified
	 * feature and version.
	 */
	public boolean hasFeature(String feature, String version) {
		// Currently, we support only XML Level 1 version 1.0
		boolean anyVersion = version == null || version.length() == 0;
		return (
			feature.equalsIgnoreCase("Core")
				&& (anyVersion || version.equals("1.0") || version.equals("2.0")))
			|| (feature.equalsIgnoreCase("XML")
				&& (anyVersion || version.equals("1.0") || version.equals("2.0")))
			|| (feature.equalsIgnoreCase("LS-Load")
				&& (anyVersion || version.equals("3.0")));
	} // hasFeature(String,String):boolean
    
    
	/**
	 * Introduced in DOM Level 2. <p>
	 * 
	 * Creates an empty DocumentType node.
	 *
	 * @param qualifiedName The qualified name of the document type to be created. 
	 * @param publicID The document type public identifier.
	 * @param systemID The document type system identifier.
	 * @since WD-DOM-Level-2-19990923
	 */
	public DocumentType createDocumentType( String qualifiedName, 
                                    String publicID, String systemID) {
		// REVISIT: this might allow creation of invalid name for DOCTYPE
		//          xmlns prefix.
		//          also there is no way for a user to turn off error checking.
		checkQName(qualifiedName);
		return new DocumentTypeImpl(null, qualifiedName, publicID, systemID);
	}
    
    final void checkQName(String qname){
        int index = qname.indexOf(':');
        int lastIndex = qname.lastIndexOf(':');
        int length = qname.length();
        
        // it is an error for NCName to have more than one ':'
        // check if it is valid QName [Namespace in XML production 6]
        if (index == 0 || index == length - 1 || lastIndex != index) {
            String msg =
                DOMMessageFormatter.formatMessage(
                    DOMMessageFormatter.DOM_DOMAIN,
                    "NAMESPACE_ERR",
                    null);
            throw new DOMException(DOMException.NAMESPACE_ERR, msg);
        }
        int start = 0;
        // Namespace in XML production [6]
        if (index > 0) {
            // check that prefix is NCName
            if (!XMLChar.isNCNameStart(qname.charAt(start))) {
                String msg =
                    DOMMessageFormatter.formatMessage(
                        DOMMessageFormatter.DOM_DOMAIN,
                        "INVALID_CHARACTER_ERR",
                        null);
                throw new DOMException(DOMException.INVALID_CHARACTER_ERR, msg);
            }
            for (int i = 1; i < index; i++) {
                if (!XMLChar.isNCName(qname.charAt(i))) {
                    String msg =
                        DOMMessageFormatter.formatMessage(
                            DOMMessageFormatter.DOM_DOMAIN,
                            "INVALID_CHARACTER_ERR",
                            null);
                    throw new DOMException(
                        DOMException.INVALID_CHARACTER_ERR,
                        msg);
                }
            }
            start = index + 1;
        }

        // check local part 
        if (!XMLChar.isNCNameStart(qname.charAt(start))) {
            // REVISIT: add qname parameter to the message
            String msg =
                DOMMessageFormatter.formatMessage(
                    DOMMessageFormatter.DOM_DOMAIN,
                    "INVALID_CHARACTER_ERR",
                    null);
            throw new DOMException(DOMException.INVALID_CHARACTER_ERR, msg);
        }
        for (int i = start + 1; i < length; i++) {
            if (!XMLChar.isNCName(qname.charAt(i))) {
                String msg =
                    DOMMessageFormatter.formatMessage(
                        DOMMessageFormatter.DOM_DOMAIN,
                        "INVALID_CHARACTER_ERR",
                        null);
                throw new DOMException(DOMException.INVALID_CHARACTER_ERR, msg);
            }
        }           
    }


	/**
	 * Introduced in DOM Level 2. <p>
	 * 
	 * Creates an XML Document object of the specified type with its document
	 * element.
	 *
	 * @param namespaceURI     The namespace URI of the document
	 *                         element to create, or null. 
	 * @param qualifiedName    The qualified name of the document
	 *                         element to create. 
	 * @param doctype          The type of document to be created or null.<p>
	 *
	 *                         When doctype is not null, its
	 *                         Node.ownerDocument attribute is set to
	 *                         the document being created.
	 * @return Document        A new Document object.
	 * @throws DOMException    WRONG_DOCUMENT_ERR: Raised if doctype has
	 *                         already been used with a different document.
	 * @since WD-DOM-Level-2-19990923
	 */
	public Document createDocument(
		String namespaceURI,
		String qualifiedName,
		DocumentType doctype)
		throws DOMException {
		if (doctype != null && doctype.getOwnerDocument() != null) {
			String msg =
				DOMMessageFormatter.formatMessage(
					DOMMessageFormatter.DOM_DOMAIN,
					"WRONG_DOCUMENT_ERR",
					null);
			throw new DOMException(DOMException.WRONG_DOCUMENT_ERR, msg);
		}
		CoreDocumentImpl doc = new CoreDocumentImpl(doctype);
		Element e = doc.createElementNS(namespaceURI, qualifiedName);
		doc.appendChild(e);
		return doc;
	}
	/**
	 * DOM Level 3 WD - Experimental.
	 * This method makes available a <code>DOMImplementation</code>'s 
	 * specialized interface (see ).
	 * @param feature The name of the feature requested (case-insensitive).
	 * @return Returns an alternate <code>DOMImplementation</code> which 
	 *   implements the specialized APIs of the specified feature, if any, 
	 *   or <code>null</code> if there is no alternate 
	 *   <code>DOMImplementation</code> object which implements interfaces 
	 *   associated with that feature. Any alternate 
	 *   <code>DOMImplementation</code> returned by this method must 
	 *   delegate to the primary core <code>DOMImplementation</code> and not 
	 *   return results inconsistent with the primary 
	 *   <code>DOMImplementation</code>
	 */
	public DOMImplementation getInterface(String feature) {
		String msg =
			DOMMessageFormatter.formatMessage(
				DOMMessageFormatter.DOM_DOMAIN,
				"NOT_SUPPORTED_ERR",
				null);
		throw new DOMException(DOMException.NOT_SUPPORTED_ERR, msg);
	}
	// DOM L3 LS
	/**
	 * DOM Level 3 WD - Experimental.
	 */
	public DOMBuilder createDOMBuilder(short mode, String schemaType)
		throws DOMException {
		if (mode == DOMImplementationLS.MODE_ASYNCHRONOUS) {
			String msg =
				DOMMessageFormatter.formatMessage(
					DOMMessageFormatter.DOM_DOMAIN,
					"NOT_SUPPORTED_ERR",
					null);
			throw new DOMException(DOMException.NOT_SUPPORTED_ERR, msg);
		}
		if (schemaType != null
			&& schemaType.equals("http://www.w3.org/TR/REC-xml")) {
			return new DOMBuilderImpl(
				"org.apache.xerces.parsers.DTDConfiguration",
				schemaType);
		}
		else {
			// create default parser configuration validating against XMLSchemas
			return new DOMBuilderImpl(
				"org.apache.xerces.parsers.StandardParserConfiguration",
				schemaType);
		}
	}
	/**
	 * DOM Level 3 WD - Experimental.
	 */
	public DOMWriter createDOMWriter() {
		return new DOMWriterImpl(true);
	}
	/**
	 * DOM Level 3 WD - Experimental.
	 */
	public DOMInputSource createDOMInputSource() {
		return new DOMInputSourceImpl();
	}
	//
	// Protected methods
	//
	/** NON-DOM */
	synchronized RevalidationHandler getValidator(String schemaType) {
		// REVISIT: implement a pool of validators to avoid long
		//          waiting for several threads
		//          implement retrieving grammar based on schemaType
		if (fDOMRevalidator == null) {
			try {
				// use context class loader.  If it returns
				// null, class.forName gets used.
				fDOMRevalidator =
					(RevalidationHandler) (ObjectFactory
						.newInstance(
							"org.apache.xerces.impl.xs.XMLSchemaValidator",
							ObjectFactory.findClassLoader(),
							true));
			}
			catch (Exception e) {}
		}
		while (!isFree()) {
			try {
				wait();
			}
			catch (InterruptedException e) {
				try {
					return (RevalidationHandler)
						(ObjectFactory
							.newInstance(
								"org.apache.xerces.impl.xs.XMLSchemaValidator",
								ObjectFactory.findClassLoader(),
								true));
				}
				catch (Exception exception) {
					return null;
				}
			}
		}
		free = false;
		return fDOMRevalidator;
	}
	/** NON-DOM */
	synchronized void releaseValidator(String schemaType) {
		// REVISIT: implement releasing grammar base on the schema type
		notifyAll();
		free = true;
	}
	/** NON-DOM */
	final synchronized boolean isFree() {
		return free;
	}
} // class DOMImplementationImpl
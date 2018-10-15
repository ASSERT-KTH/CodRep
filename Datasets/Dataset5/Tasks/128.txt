"org.apache.xerces.parsers.XML11Configuration"));

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 2000-2003 The Apache Software Foundation.  All rights 
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
 * originally based on software copyright (c) 2001, International
 * Business Machines, Inc., http://www.apache.org.  For more
 * information on the Apache Software Foundation, please see
 * <http://www.apache.org/>.
 */

package org.apache.xerces.parsers;

import java.io.StringReader;
import java.util.Stack;

import org.apache.xerces.dom.DOMErrorImpl;
import org.apache.xerces.dom.DOMMessageFormatter;
import org.apache.xerces.dom3.DOMConfiguration;
import org.apache.xerces.dom3.DOMErrorHandler;
import org.apache.xerces.impl.Constants;
import org.apache.xerces.util.DOMEntityResolverWrapper;
import org.apache.xerces.util.DOMErrorHandlerWrapper;
import org.apache.xerces.util.ObjectFactory;
import org.apache.xerces.util.SymbolTable;
import org.apache.xerces.xni.grammars.XMLGrammarPool;
import org.apache.xerces.xni.parser.XMLConfigurationException;
import org.apache.xerces.xni.parser.XMLEntityResolver;
import org.apache.xerces.xni.parser.XMLInputSource;
import org.apache.xerces.xni.parser.XMLParserConfiguration;
import org.w3c.dom.DOMException;
import org.w3c.dom.Document;
import org.w3c.dom.Node;
import org.w3c.dom.ls.DOMBuilder;
import org.w3c.dom.ls.DOMBuilderFilter;
import org.w3c.dom.ls.DOMEntityResolver;
import org.w3c.dom.ls.DOMInputSource;


/**
 * This is Xerces DOM Builder class. It uses the abstract DOM
 * parser with a document scanner, a dtd scanner, and a validator, as 
 * well as a grammar pool.
 *
 * @author Pavani Mukthipudi, Sun Microsystems Inc.
 * @author Elena Litani, IBM
 * @author Rahul Srivastava, Sun Microsystems Inc.
 * @version $Id$
 */


public class DOMBuilderImpl
extends AbstractDOMParser implements DOMBuilder, DOMConfiguration {



    // SAX & Xerces feature ids

    /** Feature identifier: namespaces. */
    protected static final String NAMESPACES =
    Constants.SAX_FEATURE_PREFIX + Constants.NAMESPACES_FEATURE;

    /** Feature id: validation. */
    protected static final String VALIDATION_FEATURE =
    Constants.SAX_FEATURE_PREFIX+Constants.VALIDATION_FEATURE;

    /** XML Schema validation */
    protected static final String XMLSCHEMA =
    Constants.XERCES_FEATURE_PREFIX + Constants.SCHEMA_VALIDATION_FEATURE;    

    /** Dynamic validation */
    protected static final String DYNAMIC_VALIDATION = 
    Constants.XERCES_FEATURE_PREFIX + Constants.DYNAMIC_VALIDATION_FEATURE;

    /** Feature identifier: expose schema normalized value */
    protected static final String NORMALIZE_DATA =
    Constants.XERCES_FEATURE_PREFIX + Constants.SCHEMA_NORMALIZED_VALUE;
    
    // internal properties
    protected static final String SYMBOL_TABLE = 
    Constants.XERCES_PROPERTY_PREFIX + Constants.SYMBOL_TABLE_PROPERTY;
    
    protected static final String PSVI_AUGMENT = 
    Constants.XERCES_FEATURE_PREFIX +Constants.SCHEMA_AUGMENT_PSVI;


    // 
    // Data
    //


    // REVISIT: this value should be null by default and should be set during creation of
    //          DOMBuilder
    protected String fSchemaType = null;

    protected final static boolean DEBUG = false;

    //
    // Constructors
    //

    /**
     * Constructs a DOM Builder using the standard parser configuration.
     */
	public DOMBuilderImpl(String configuration, String schemaType) {
		this(
			(XMLParserConfiguration) ObjectFactory.createObject(
				"org.apache.xerces.xni.parser.XMLParserConfiguration",
				configuration));
		if (schemaType != null) {
			if (schemaType.equals(Constants.NS_DTD)) {
				fConfiguration.setFeature(
					Constants.XERCES_FEATURE_PREFIX + Constants.SCHEMA_VALIDATION_FEATURE,
					false);
				fConfiguration.setProperty(
					Constants.JAXP_PROPERTY_PREFIX + Constants.SCHEMA_LANGUAGE,
					Constants.NS_DTD);
				fSchemaType = Constants.NS_DTD;
			}
			else if (schemaType.equals(Constants.NS_XMLSCHEMA)) {
				// XML Schem validation
				fConfiguration.setProperty(
					Constants.JAXP_PROPERTY_PREFIX + Constants.SCHEMA_LANGUAGE,
					Constants.NS_XMLSCHEMA);
			}
		}

	}

    /**
     * Constructs a DOM Builder using the specified parser configuration.
     */
    public DOMBuilderImpl(XMLParserConfiguration config) {
        super(config);
        
        // add recognized features
        final String[] domRecognizedFeatures = {
            Constants.DOM_CANONICAL_FORM,
            Constants.DOM_CDATA_SECTIONS,
            Constants.DOM_CHARSET_OVERRIDES_XML_ENCODING,
            Constants.DOM_INFOSET,
            Constants.DOM_NAMESPACE_DECLARATIONS,
            Constants.DOM_SUPPORTED_MEDIATYPES_ONLY,
            Constants.DOM_CERTIFIED,
        };

        fConfiguration.addRecognizedFeatures(domRecognizedFeatures);

        // turn off deferred DOM
        fConfiguration.setFeature(DEFER_NODE_EXPANSION, false);
        
        // set default values
        fConfiguration.setFeature(Constants.DOM_CANONICAL_FORM, false);
        fConfiguration.setFeature(Constants.DOM_CDATA_SECTIONS, true);
        fConfiguration.setFeature(Constants.DOM_CHARSET_OVERRIDES_XML_ENCODING, true);
        fConfiguration.setFeature(Constants.DOM_INFOSET, false);
        fConfiguration.setFeature(Constants.DOM_NAMESPACE_DECLARATIONS, true);
        fConfiguration.setFeature(Constants.DOM_SUPPORTED_MEDIATYPES_ONLY, false);
        
        // REVISIT: by default Xerces assumes that input is certified.
        //          default is different from the one specified in the DOM spec
        fConfiguration.setFeature(Constants.DOM_CERTIFIED, true);

        // Xerces datatype-normalization feature is on by default
        fConfiguration.setFeature( NORMALIZE_DATA, false ); 
    } // <init>(XMLParserConfiguration)

    /**
     * Constructs a DOM Builder using the specified symbol table.
     */
	public DOMBuilderImpl(SymbolTable symbolTable) {
		this(
			(XMLParserConfiguration) ObjectFactory.createObject(
				"org.apache.xerces.xni.parser.XMLParserConfiguration",
				"org.apache.xerces.parsers.IntegratedParserConfiguration"));
		fConfiguration.setProperty(
			Constants.XERCES_PROPERTY_PREFIX + Constants.SYMBOL_TABLE_PROPERTY,
			symbolTable);
	} // <init>(SymbolTable)


    /**
     * Constructs a DOM Builder using the specified symbol table and
     * grammar pool.
     */
	public DOMBuilderImpl(SymbolTable symbolTable, XMLGrammarPool grammarPool) {
		this(
			(XMLParserConfiguration) ObjectFactory.createObject(
				"org.apache.xerces.xni.parser.XMLParserConfiguration",
				"org.apache.xerces.parsers.StandardParserConfiguration"));
		fConfiguration.setProperty(
			Constants.XERCES_PROPERTY_PREFIX + Constants.SYMBOL_TABLE_PROPERTY,
			symbolTable);
		fConfiguration.setProperty(
			Constants.XERCES_PROPERTY_PREFIX
				+ Constants.XMLGRAMMAR_POOL_PROPERTY,
			grammarPool);
	}

    /**
     * Resets the parser state.
     *
     * @throws SAXException Thrown on initialization error.
     */
    public void reset() {
        super.reset();
        // DOM Filter
        if (fSkippedElemStack!=null) {        
            fSkippedElemStack.removeAllElements();
        }
        fRejectedElement.clear();
        fFilterReject = false;
        fSchemaType = null;


    } // reset() 

    //
    // DOMBuilder methods
    //
 
    public DOMConfiguration getConfig(){
        return this;
    }
 

    /**
     *  When the application provides a filter, the parser will call out to 
     * the filter at the completion of the construction of each 
     * <code>Element</code> node. The filter implementation can choose to 
     * remove the element from the document being constructed (unless the 
     * element is the document element) or to terminate the parse early. If 
     * the document is being validated when it's loaded the validation 
     * happens before the filter is called. 
     */
    public DOMBuilderFilter getFilter() {
        return fDOMFilter;
    }

    /**
     *  When the application provides a filter, the parser will call out to 
     * the filter at the completion of the construction of each 
     * <code>Element</code> node. The filter implementation can choose to 
     * remove the element from the document being constructed (unless the 
     * element is the document element) or to terminate the parse early. If 
     * the document is being validated when it's loaded the validation 
     * happens before the filter is called. 
     */
    public void setFilter(DOMBuilderFilter filter) {
        fDOMFilter = filter;
        if (fSkippedElemStack == null) {
            fSkippedElemStack = new Stack();
        }
    }

    /** 
    * Set parameters and properties
    */
	public void setParameter(String name, Object value) throws DOMException {
		// set features           
		if (value == Boolean.TRUE || value == Boolean.FALSE) {
			boolean state = (value == Boolean.TRUE) ? true : false;
			try {
				if (name.equals(Constants.DOM_COMMENTS)) {
					fConfiguration.setFeature(INCLUDE_COMMENTS_FEATURE, state);
				}
				else if (name.equals(Constants.DOM_DATATYPE_NORMALIZATION)) {
					fConfiguration.setFeature(NORMALIZE_DATA, state);
				}
				else if (name.equals(Constants.DOM_ENTITIES)) {
					fConfiguration.setFeature(CREATE_ENTITY_REF_NODES, state);
				}
				else if (name.equals(Constants.DOM_INFOSET)
						|| name.equals(Constants.DOM_SUPPORTED_MEDIATYPES_ONLY)
						|| name.equals(Constants.DOM_CANONICAL_FORM)) {
					if (state) { // true is not supported
						String msg =
							DOMMessageFormatter.formatMessage(
								DOMMessageFormatter.DOM_DOMAIN,
								"FEATURE_NOT_SUPPORTED",
								new Object[] { name });
						throw new DOMException(DOMException.NOT_SUPPORTED_ERR, msg);
					}
					// setting those features to false is no-op
				}
				else if (name.equals(Constants.DOM_NAMESPACES)) {
					fConfiguration.setFeature(NAMESPACES, state);
				}
				else if (name.equals(Constants.DOM_CDATA_SECTIONS)
						|| name.equals(Constants.DOM_NAMESPACE_DECLARATIONS)) {
					if (!state) { // false is not supported
						String msg =
							DOMMessageFormatter.formatMessage(
								DOMMessageFormatter.DOM_DOMAIN,
								"FEATURE_NOT_SUPPORTED",
								new Object[] { name });
						throw new DOMException(DOMException.NOT_SUPPORTED_ERR, msg);
					}
					// setting these features to true is no-op
					// REVISIT: implement "namespace-declaration" feature
				}
				else if (name.equals(Constants.DOM_VALIDATE)) {
					fConfiguration.setFeature(VALIDATION_FEATURE, state);
					if (fSchemaType != Constants.NS_DTD) {
						fConfiguration.setFeature(XMLSCHEMA, state);
					}
				}
				else if (name.equals(Constants.DOM_VALIDATE_IF_SCHEMA)) {
					fConfiguration.setFeature(DYNAMIC_VALIDATION, state);
				}
				else if (name.equals(Constants.DOM_WHITESPACE_IN_ELEMENT_CONTENT)) {
					fConfiguration.setFeature(INCLUDE_IGNORABLE_WHITESPACE, state);
				}
                else if (name.equals(Constants.DOM_PSVI)){
                    //XSModel - turn on PSVI augmentation
                    fConfiguration.setFeature(PSVI_AUGMENT, true);
                    fConfiguration.setProperty(DOCUMENT_CLASS_NAME, 
                    "org.apache.xerces.dom.PSVIDocumentImpl");
                }
				else {
					// Constants.DOM_CHARSET_OVERRIDES_XML_ENCODING feature
					// or any Xerces feature
					fConfiguration.setFeature(name, state);
				}

			}
			catch (XMLConfigurationException e) {
				String msg =
					DOMMessageFormatter.formatMessage(
						DOMMessageFormatter.DOM_DOMAIN,
						"FEATURE_NOT_FOUND",
						new Object[] { name });
				throw new DOMException(DOMException.NOT_FOUND_ERR, msg);
			}
		}
		else { // set properties
			if (name.equals(Constants.DOM_ERROR_HANDLER)) {
				if (value instanceof DOMErrorHandler) {
					try {
						fErrorHandler = new DOMErrorHandlerWrapper((DOMErrorHandler) value);
						fConfiguration.setProperty(ERROR_HANDLER, fErrorHandler);
					}
					catch (XMLConfigurationException e) {}
				}
				else {
					// REVISIT: type mismatch
					String msg =
						DOMMessageFormatter.formatMessage(
							DOMMessageFormatter.DOM_DOMAIN,
							"FEATURE_NOT_SUPPORTED",
							new Object[] { name });
					throw new DOMException(DOMException.NOT_SUPPORTED_ERR, msg);
				}

			}
			else if (name.equals(Constants.DOM_ENTITY_RESOLVER)) {
				if (value instanceof DOMEntityResolver) {
					try {
                        fConfiguration.setProperty(ENTITY_RESOLVER, new DOMEntityResolverWrapper((DOMEntityResolver) value));
					}
					catch (XMLConfigurationException e) {}
				}
				else {
					// REVISIT: type mismatch
					String msg =
						DOMMessageFormatter.formatMessage(
							DOMMessageFormatter.DOM_DOMAIN,
							"FEATURE_NOT_SUPPORTED",
							new Object[] { name });
					throw new DOMException(DOMException.NOT_SUPPORTED_ERR, msg);
				}

			}
			else if (name.equals(Constants.DOM_SCHEMA_LOCATION)) {
				if (value instanceof String) {
					try {
						if (fSchemaType == Constants.NS_XMLSCHEMA) {
							// map DOM schema-location to JAXP schemaSource property
							fConfiguration.setProperty(
								Constants.JAXP_PROPERTY_PREFIX + Constants.SCHEMA_SOURCE,
								value);
						}
						else {
							// REVISIT: allow pre-parsing DTD grammars
							String msg =
								DOMMessageFormatter.formatMessage(
									DOMMessageFormatter.DOM_DOMAIN,
									"FEATURE_NOT_SUPPORTED",
									new Object[] { name });
							throw new DOMException(DOMException.NOT_SUPPORTED_ERR, msg);
						}

					}
					catch (XMLConfigurationException e) {}
				}
				else {
					// REVISIT: type mismatch
					String msg =
						DOMMessageFormatter.formatMessage(
							DOMMessageFormatter.DOM_DOMAIN,
							"FEATURE_NOT_SUPPORTED",
							new Object[] { name });
					throw new DOMException(DOMException.NOT_SUPPORTED_ERR, msg);
				}

			}
			else if (name.equals(Constants.DOM_SCHEMA_TYPE)) {
				// REVISIT: should null value be supported?
				if (value instanceof String) {
					try {
						if (value.equals(Constants.NS_XMLSCHEMA)) {
							// turn on schema feature
							fConfiguration.setFeature(Constants.XERCES_FEATURE_PREFIX
									                  + Constants.SCHEMA_VALIDATION_FEATURE,
								                      true);
                                // map to JAXP schemaLanguage
							fConfiguration.setProperty( Constants.JAXP_PROPERTY_PREFIX 
                                                        + Constants.SCHEMA_LANGUAGE,
								                        Constants.NS_XMLSCHEMA);
							fSchemaType = Constants.NS_XMLSCHEMA;
						}
						else if (value.equals(Constants.NS_DTD)) {
							fConfiguration.setFeature(
								Constants.XERCES_FEATURE_PREFIX
								+ Constants.SCHEMA_VALIDATION_FEATURE,
								false);
                            fConfiguration.setProperty( Constants.JAXP_PROPERTY_PREFIX 
                                                        + Constants.SCHEMA_LANGUAGE,
                                                        Constants.NS_DTD);
							fSchemaType = Constants.NS_DTD;
						}
					}
					catch (XMLConfigurationException e) {}
				}
				else {
					String msg =
						DOMMessageFormatter.formatMessage(
							DOMMessageFormatter.DOM_DOMAIN,
							"FEATURE_NOT_SUPPORTED",
							new Object[] { name });
					throw new DOMException(DOMException.NOT_SUPPORTED_ERR, msg);
				}

			}
            else if (name.equals(DOCUMENT_CLASS_NAME)) {
                fConfiguration.setProperty(DOCUMENT_CLASS_NAME, value);
            }
			else {
				// REVISIT: check if this is a boolean parameter -- type mismatch should be thrown.       
				//parameter is not recognized
				String msg =
					DOMMessageFormatter.formatMessage(
						DOMMessageFormatter.DOM_DOMAIN,
						"FEATURE_NOT_FOUND",
						new Object[] { name });
				throw new DOMException(DOMException.NOT_FOUND_ERR, msg);
			}
		}
	}

	/**
	  * Look up the value of a feature or a property.
	  */
	public Object getParameter(String name) throws DOMException {
		if (name.equals(Constants.DOM_COMMENTS)) {
			return (fConfiguration.getFeature(INCLUDE_COMMENTS_FEATURE))
				? Boolean.TRUE
				: Boolean.FALSE;
		}
		else if (name.equals(Constants.DOM_DATATYPE_NORMALIZATION)) {
			return (fConfiguration.getFeature(NORMALIZE_DATA))
				? Boolean.TRUE
				: Boolean.FALSE;
		}
		else if (name.equals(Constants.DOM_ENTITIES)) {
			return (fConfiguration.getFeature(CREATE_ENTITY_REF_NODES))
				? Boolean.TRUE
				: Boolean.FALSE;
		}
		else if (name.equals(Constants.DOM_NAMESPACES)) {
			return (fConfiguration.getFeature(NAMESPACES))
				? Boolean.TRUE
				: Boolean.FALSE;
		}
		else if (name.equals(Constants.DOM_VALIDATE)) {
			return (fConfiguration.getFeature(VALIDATION_FEATURE))
				? Boolean.TRUE
				: Boolean.FALSE;
		}
		else if (name.equals(Constants.DOM_VALIDATE_IF_SCHEMA)) {
			return (fConfiguration.getFeature(DYNAMIC_VALIDATION))
				? Boolean.TRUE
				: Boolean.FALSE;
		}
		else if (name.equals(Constants.DOM_WHITESPACE_IN_ELEMENT_CONTENT)) {
			return (fConfiguration.getFeature(INCLUDE_IGNORABLE_WHITESPACE))
				? Boolean.TRUE
				: Boolean.FALSE;
		}
		else if (
			name.equals(Constants.DOM_NAMESPACE_DECLARATIONS)
				|| name.equals(Constants.DOM_CDATA_SECTIONS)
				|| name.equals(Constants.DOM_CANONICAL_FORM)
				|| name.equals(Constants.DOM_SUPPORTED_MEDIATYPES_ONLY)
				|| name.equals(Constants.DOM_INFOSET)
				|| name.equals(Constants.DOM_CHARSET_OVERRIDES_XML_ENCODING)) {
			return (fConfiguration.getFeature(name))
				? Boolean.TRUE
				: Boolean.FALSE;
		}
		else if (name.equals(Constants.DOM_ERROR_HANDLER)) {
			if (fErrorHandler != null) {
				return fErrorHandler.getErrorHandler();
			}
			return null;
		}
		else if (name.equals(Constants.DOM_ENTITY_RESOLVER)) {
			try {               
                XMLEntityResolver entityResolver = 
               (XMLEntityResolver) fConfiguration.getProperty(ENTITY_RESOLVER);
                if (entityResolver != null
                    && entityResolver instanceof DOMEntityResolverWrapper) {
                    return ((DOMEntityResolverWrapper) entityResolver).getEntityResolver();
                    }
                    return null;
			}
			catch (XMLConfigurationException e) {}
		}
		else if (name.equals(Constants.DOM_SCHEMA_TYPE)) {
			return fConfiguration.getProperty(
				Constants.JAXP_PROPERTY_PREFIX + Constants.SCHEMA_LANGUAGE);
		}
		else if (name.equals(Constants.DOM_SCHEMA_LOCATION)) {
			return fConfiguration.getProperty(
				Constants.JAXP_PROPERTY_PREFIX + Constants.SCHEMA_SOURCE);
		}
        else if (name.equals(SYMBOL_TABLE)){
            return fConfiguration.getProperty(SYMBOL_TABLE);
        }
        else if (name.equals(DOCUMENT_CLASS_NAME)) {
             return fConfiguration.getProperty(DOCUMENT_CLASS_NAME);
        }
		else {
			String msg =
				DOMMessageFormatter.formatMessage(
					DOMMessageFormatter.DOM_DOMAIN,
					"FEATURE_NOT_FOUND",
					new Object[] { name });
			throw new DOMException(DOMException.NOT_FOUND_ERR, msg);
		}
		return null;
	}

	public boolean canSetParameter(String name, Object value) {
		if (value == Boolean.TRUE || value == Boolean.FALSE) {
			boolean state = (value == Boolean.TRUE) ? true : false;
			if (name.equals(Constants.DOM_INFOSET)
				|| name.equals(Constants.DOM_SUPPORTED_MEDIATYPES_ONLY)
				|| name.equals(Constants.DOM_CANONICAL_FORM)) {
				// true is not supported
				return (state) ? false : true;
			}
			else if (
				name.equals(Constants.DOM_CDATA_SECTIONS)
					|| name.equals(Constants.DOM_NAMESPACE_DECLARATIONS)) {
				// false is not supported
				return (state) ? true : false;
			}
			else if (
				name.equals(Constants.DOM_CHARSET_OVERRIDES_XML_ENCODING)
					|| name.equals(Constants.DOM_COMMENTS)
					|| name.equals(Constants.DOM_DATATYPE_NORMALIZATION)
					|| name.equals(Constants.DOM_ENTITIES)
					|| name.equals(Constants.DOM_NAMESPACES)
					|| name.equals(Constants.DOM_VALIDATE)
					|| name.equals(Constants.DOM_VALIDATE_IF_SCHEMA)
					|| name.equals(Constants.DOM_WHITESPACE_IN_ELEMENT_CONTENT)) {
				return true;
			}

			// Recognize Xerces features.
			try {
				fConfiguration.getFeature(name);
				return true;
			}
			catch (XMLConfigurationException e) {
				return false;
			}
		}
		else { // check properties
			if (name.equals(Constants.DOM_ERROR_HANDLER)) {
				if (value instanceof DOMErrorHandler) {
					return true;
				}
				return false;
			}
			else if (name.equals(Constants.DOM_ENTITY_RESOLVER)) {
				if (value instanceof DOMEntityResolver) {
					return true;
				}
				return false;
			}
			else if (name.equals(Constants.DOM_SCHEMA_TYPE)) {
				if (value instanceof String
					&& (value.equals(Constants.NS_XMLSCHEMA)
						|| value.equals(Constants.NS_DTD))) {
					return true;
				}
				return false;
			}
			else if (name.equals(Constants.DOM_SCHEMA_LOCATION)) {
				if (value instanceof String)
					return true;
				return false;
			}
            else if (name.equals(DOCUMENT_CLASS_NAME)){
                return true;
            }
			return false;
		}
	}


    /**
     * Parse an XML document from a location identified by an URI reference. 
     * If the URI contains a fragment identifier (see section 4.1 in ), the 
     * behavior is not defined by this specification.
     *  
     */
    public Document parseURI(String uri)  {
        XMLInputSource source = new XMLInputSource(null, uri, null);

        try {        
            parse(source);
        } catch (Exception e){
            if (fErrorHandler != null) {
                DOMErrorImpl error = new DOMErrorImpl();
                error.fException = e;
                error.fMessage = e.getMessage();
                error.fSeverity = error.SEVERITY_FATAL_ERROR;
                fErrorHandler.getErrorHandler().handleError(error);
            }
            if (DEBUG) {            
               e.printStackTrace();
            }
        }
        return getDocument();
    }

    /**
     * Parse an XML document from a resource identified by an 
     * <code>DOMInputSource</code>.
     * 
     */
    public Document parse(DOMInputSource is) {

        // need to wrap the DOMInputSource with an XMLInputSource
        XMLInputSource xmlInputSource = dom2xmlInputSource(is);

        try {        
            parse(xmlInputSource);
        } catch (Exception e) {
            if (fErrorHandler != null) {
                DOMErrorImpl error = new DOMErrorImpl();
                error.fException = e;
                error.fMessage = e.getMessage();
                error.fSeverity = error.SEVERITY_FATAL_ERROR;
                fErrorHandler.getErrorHandler().handleError(error);

            }
            if (DEBUG) {            
               e.printStackTrace();
            }
        }
        return getDocument();
    }

    /**
     *  Parse an XML document or fragment from a resource identified by an 
     * <code>DOMInputSource</code> and insert the content into an existing 
     * document at the position epcified with the <code>contextNode</code> 
     * and <code>action</code> arguments. When parsing the input stream the 
     * context node is used for resolving unbound namespace prefixes.
     *  
     * @param is  The <code>DOMInputSource</code> from which the source 
     *   document is to be read. 
     * @param cnode  The <code>Node</code> that is used as the context for 
     *   the data that is being parsed. 
     * @param action This parameter describes which action should be taken 
     *   between the new set of node being inserted and the existing 
     *   children of the context node. The set of possible actions is 
     *   defined above. 
     * @exception DOMException
     *   HIERARCHY_REQUEST_ERR: Thrown if this action results in an invalid 
     *   hierarchy (i.e. a Document with more than one document element). 
     */
    public void parseWithContext(DOMInputSource is, Node cnode, 
                                 short action) throws DOMException {
        // REVISIT: need to implement.
        throw new DOMException(DOMException.NOT_SUPPORTED_ERR, "Not supported");
    }


    /**
     * NON-DOM: convert DOMInputSource to XNIInputSource
     * 
     * @param is
     * @return 
     */
    XMLInputSource dom2xmlInputSource(DOMInputSource is) {
        // need to wrap the DOMInputSource with an XMLInputSource
        XMLInputSource xis = null;
        // if there is a string data, use a StringReader
        // according to DOM, we need to treat such data as "UTF-16".
        if (is.getStringData() != null) {
            xis = new XMLInputSource(is.getPublicId(), is.getSystemId(),
                                     is.getBaseURI(), new StringReader(is.getStringData()),
                                     "UTF-16");
        }
        // check whether there is a Reader
        // according to DOM, we need to treat such reader as "UTF-16".
        else if (is.getCharacterStream() != null) {
            xis = new XMLInputSource(is.getPublicId(), is.getSystemId(),
                                     is.getBaseURI(), is.getCharacterStream(),
                                     "UTF-16");
        }
        // check whether there is an InputStream
        else if (is.getByteStream() != null) {
            xis = new XMLInputSource(is.getPublicId(), is.getSystemId(),
                                     is.getBaseURI(), is.getByteStream(),
                                     is.getEncoding());
        }
        // otherwise, just use the public/system/base Ids
        else {
            xis = new XMLInputSource(is.getPublicId(), is.getSystemId(),
                                     is.getBaseURI());
        }

        return xis;
    }


} // class DOMBuilderImpl
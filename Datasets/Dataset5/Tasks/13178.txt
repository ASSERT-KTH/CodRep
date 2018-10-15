fSkippedElemStack.removeAllElements();

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 2000-2002 The Apache Software Foundation.  All rights 
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

import java.io.InputStream;
import java.io.IOException;
import java.io.Reader;
import java.io.StringReader;
import java.util.Hashtable;
import java.util.Stack;
import java.util.Vector;

import org.apache.xerces.dom.CoreDocumentImpl;

import org.w3c.dom.DOMException;
import org.w3c.dom.Document;
import org.w3c.dom.Node;
import org.w3c.dom.DOMErrorHandler;
import org.w3c.dom.ls.DOMBuilder;
import org.w3c.dom.ls.DOMEntityResolver;
import org.w3c.dom.ls.DOMBuilderFilter;
import org.w3c.dom.ls.DOMInputSource;


import org.apache.xerces.impl.Constants;
import org.apache.xerces.util.DOMEntityResolverWrapper;
import org.apache.xerces.util.SymbolTable;
import org.apache.xerces.util.ObjectFactory;
import org.apache.xerces.util.DOMErrorHandlerWrapper;
import org.apache.xerces.util.XMLGrammarPoolImpl;
import org.apache.xerces.xni.Augmentations;
import org.apache.xerces.xni.XNIException;
import org.apache.xerces.xni.grammars.XMLGrammarPool;
import org.apache.xerces.xni.parser.XMLConfigurationException;
import org.apache.xerces.xni.parser.XMLInputSource;
import org.apache.xerces.xni.parser.XMLParserConfiguration;


/**
 * This is Xerces DOM Builder class. It uses the abstract DOM
 * parser with a document scanner, a dtd scanner, and a validator, as 
 * well as a grammar pool.
 *
 * @author Pavani Mukthipudi, Sun Microsystems Inc.
 * @author Elena Litani, IBM
 * @author Rahul Srivastava, Sun Microsystems Inc.
 *
 */


public class DOMBuilderImpl
extends AbstractDOMParser implements DOMBuilder {



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


    // DOM L3 Schema validation types:
    protected static final String XML_SCHEMA_VALIDATION = "http://www.w3.org/2001/XMLSchema";
    protected static final String DTD_VALIDATION = "http://www.w3.org/TR/REC-xml";

    // 
    // Data
    //


    // REVISIT: this value should be null by default and should be set during creation of
    //          DOMBuilder
    protected String fSchemaType = XML_SCHEMA_VALIDATION;

    protected final static boolean DEBUG = false;
    //
    // Constructors
    //

    /**
     * Constructs a DOM Builder using the standard parser configuration.
     */
    public DOMBuilderImpl(String configuration, String schemaType) {
          this( (XMLParserConfiguration)ObjectFactory.createObject( 
              "org.apache.xerces.xni.parser.XMLParserConfiguration",
              configuration));
          fSchemaType = schemaType;
    } // <init>

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
            Constants.DOM_SUPPORTED_MEDIATYPES_ONLY
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

        // Xerces datatype-normalization feature is on by default
        fConfiguration.setFeature( NORMALIZE_DATA, false ); 


        // REVISIT: we need to be able to validate against XMLSchema ONLY if
        //          schemaType equal XML Schema namespace, even if
        //          DOCTYPE is present.
        //          This is similar to JAXP schemaLanguage property.         

        

    } // <init>(XMLParserConfiguration)

    /**
     * Constructs a DOM Builder using the specified symbol table.
     */
    public DOMBuilderImpl(SymbolTable symbolTable) {
        this((XMLParserConfiguration)ObjectFactory.createObject(
                                                               "org.apache.xerces.xni.parser.XMLParserConfiguration",
                                                               "org.apache.xerces.parsers.StandardParserConfiguration"
                                                               ));
        fConfiguration.setProperty(Constants.XERCES_PROPERTY_PREFIX+Constants.SYMBOL_TABLE_PROPERTY, symbolTable);
    } // <init>(SymbolTable)


    /**
     * Constructs a DOM Builder using the specified symbol table and
     * grammar pool.
     */
    public DOMBuilderImpl(SymbolTable symbolTable, XMLGrammarPool grammarPool) {
        this((XMLParserConfiguration)ObjectFactory.createObject(
                                                               "org.apache.xerces.xni.parser.XMLParserConfiguration",
                                                               "org.apache.xerces.parsers.StandardParserConfiguration"
                                                               ));
        fConfiguration.setProperty(Constants.XERCES_PROPERTY_PREFIX+Constants.SYMBOL_TABLE_PROPERTY, symbolTable);
        fConfiguration.setProperty(Constants.XERCES_PROPERTY_PREFIX+Constants.XMLGRAMMAR_POOL_PROPERTY, grammarPool);
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
            fSkippedElemStack.clear();
        }
        fRejectedElement.clear();
        fFilterReject = false;


    } // reset() 

    //
    // DOMBuilder methods
    //

    /**
     * If a <code>DOMEntityResolver</code> has been specified, each time a 
     * reference to an external entity is encountered the 
     * <code>DOMBuilder</code> will pass the public and system IDs to the 
     * entity resolver, which can then specify the actual source of the 
     * entity.
     */
    public DOMEntityResolver getEntityResolver() {
        DOMEntityResolver domEntityResolver = null;
        try {
            DOMEntityResolver entityResolver = (DOMEntityResolver)fConfiguration.getProperty(ENTITY_RESOLVER);
            if (entityResolver != null && 
                entityResolver instanceof DOMEntityResolverWrapper) {
                domEntityResolver = ((DOMEntityResolverWrapper)entityResolver).getEntityResolver();
            }
        } catch (XMLConfigurationException e) {

        }
        return domEntityResolver;
    }

    /**
     * If a <code>DOMEntityResolver</code> has been specified, each time a 
     * reference to an external entity is encountered the 
     * <code>DOMBuilder</code> will pass the public and system IDs to the 
     * entity resolver, which can then specify the actual source of the 
     * entity.
     */
    public void setEntityResolver(DOMEntityResolver entityResolver) {
        try {
            fConfiguration.setProperty(ENTITY_RESOLVER, 
                                       new DOMEntityResolverWrapper(entityResolver));
        } catch (XMLConfigurationException e) {

        }
    }

    /**
     *  In the event that an error is encountered in the XML document being 
     * parsed, the <code>DOMDcoumentBuilder</code> will call back to the 
     * <code>errorHandler</code> with the error information. When the 
     * document loading process calls the error handler the node closest to 
     * where the error occured is passed to the error handler if the 
     * implementation, if the implementation is unable to pass the node 
     * where the error occures the document Node is passed to the error 
     * handler. Mutations to the document from within an error handler will 
     * result in implementation dependent behavour. 
     */
    public DOMErrorHandler getErrorHandler() {
        DOMErrorHandler errorHandler = null;
        try {
            DOMErrorHandler domErrorHandler = 
            (DOMErrorHandler)fConfiguration.getProperty(ERROR_HANDLER);
            if (domErrorHandler != null && 
                domErrorHandler instanceof DOMErrorHandlerWrapper) {
                errorHandler = ((DOMErrorHandlerWrapper)domErrorHandler).getErrorHandler();
            }
        } catch (XMLConfigurationException e) {

        }
        return errorHandler;
    }

    /**
     *  In the event that an error is encountered in the XML document being 
     * parsed, the <code>DOMDcoumentBuilder</code> will call back to the 
     * <code>errorHandler</code> with the error information. When the 
     * document loading process calls the error handler the node closest to 
     * where the error occured is passed to the error handler if the 
     * implementation, if the implementation is unable to pass the node 
     * where the error occures the document Node is passed to the error 
     * handler. Mutations to the document from within an error handler will 
     * result in implementation dependent behavour. 
     */
    public void setErrorHandler(DOMErrorHandler errorHandler) {
        try {
            fConfiguration.setProperty(ERROR_HANDLER, 
                                       new DOMErrorHandlerWrapper(errorHandler));
        } catch (XMLConfigurationException e) {

        }
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
     * Set the state of a feature.
     * 
     * <br>The feature name has the same form as a DOM hasFeature string.
     * <br>It is possible for a <code>DOMBuilder</code> to recognize a feature 
     * name but to be unable to set its value.
     * 
     * @param name The feature name.
     * @param state The requested state of the feature (<code>true</code> or 
     *   <code>false</code>).
     * @exception DOMException
     *   Raise a NOT_SUPPORTED_ERR exception when the <code>DOMBuilder</code> 
     *   recognizes the feature name but cannot set the requested value. 
     *   <br>Raise a NOT_FOUND_ERR When the <code>DOMBuilder</code> does not 
     *   recognize the feature name.
     */
    public void setFeature(String name, boolean state) throws DOMException {
        try {
            if (name.equals(Constants.DOM_COMMENTS)) {
                fConfiguration.setFeature(INCLUDE_COMMENTS_FEATURE, state);
            } else if (name.equals(Constants.DOM_DATATYPE_NORMALIZATION)) {
                fConfiguration.setFeature(NORMALIZE_DATA, state);
            } else if (name.equals(Constants.DOM_ENTITIES)) {
                fConfiguration.setFeature(CREATE_ENTITY_REF_NODES, state);
            } else if (name.equals(Constants.DOM_INFOSET) || 
                       name.equals(Constants.DOM_SUPPORTED_MEDIATYPES_ONLY) ||
                       name.equals(Constants.DOM_CANONICAL_FORM)) {
                if (state) { // true is not supported
                    throw new DOMException(DOMException.NOT_SUPPORTED_ERR,"Feature \""+name+"\" cannot be set to \""+state+"\"");
                }
            } else if (name.equals(Constants.DOM_NAMESPACES)) {
                fConfiguration.setFeature (NAMESPACES, state);
            } else if (name.equals(Constants.DOM_CDATA_SECTIONS) ||
                       name.equals(Constants.DOM_NAMESPACE_DECLARATIONS)) {
                if (!state) { // false is not supported
                    throw new DOMException(DOMException.NOT_SUPPORTED_ERR,"Feature \""+name+"\" cannot be set to \""+state+"\"");
                }
            } else if (name.equals(Constants.DOM_VALIDATE)) {
                fConfiguration.setFeature(VALIDATION_FEATURE, state);

                // REVISIT: user can speficy schemaType
                if (fSchemaType==null || fSchemaType.equals(XML_SCHEMA_VALIDATION)) {
                    fConfiguration.setFeature(XMLSCHEMA, state);
                }
            } else if (name.equals(Constants.DOM_VALIDATE_IF_SCHEMA)) {
                fConfiguration.setFeature(DYNAMIC_VALIDATION, state);
            } else if (name.equals(Constants.DOM_WHITESPACE_IN_ELEMENT_CONTENT)) {
                fConfiguration.setFeature(INCLUDE_IGNORABLE_WHITESPACE, state);             
            } else {
                // Constants.DOM_CHARSET_OVERRIDES_XML_ENCODING feature
                fConfiguration.setFeature(name, state);
            }
        } catch (XMLConfigurationException e) {
            throw new DOMException(DOMException.NOT_FOUND_ERR,"Feature \""+name+"\" not recognized");
        }
    }

    /**
     * Query whether setting a feature to a specific value is supported.
     * <br>The feature name has the same form as a DOM hasFeature string.
     * 
     * @param name The feature name, which is a DOM has-feature style string.
     * @param state The requested state of the feature (<code>true</code> or 
     *   <code>false</code>).
     * @return <code>true</code> if the feature could be successfully set to 
     *   the specified value, or <code>false</code> if the feature is not 
     *   recognized or the requested value is not supported. The value of 
     *   the feature itself is not changed.
     */
    public boolean canSetFeature(String name, boolean state) {
        if (name.equals(Constants.DOM_INFOSET) || 
            name.equals(Constants.DOM_SUPPORTED_MEDIATYPES_ONLY) ||
            name.equals(Constants.DOM_CANONICAL_FORM)) {
            // true is not supported
            return(state)?false:true;
        } else if (name.equals(Constants.DOM_CDATA_SECTIONS) ||
                   name.equals(Constants.DOM_NAMESPACE_DECLARATIONS)) {
            // false is not supported
            return(state)?true:false;
        } else if (name.equals(Constants.DOM_CHARSET_OVERRIDES_XML_ENCODING) || 
                   name.equals(Constants.DOM_COMMENTS) || 
                   name.equals(Constants.DOM_DATATYPE_NORMALIZATION) ||
                   name.equals(Constants.DOM_ENTITIES) ||
                   name.equals(Constants.DOM_NAMESPACES) ||
                   name.equals(Constants.DOM_VALIDATE) ||
                   name.equals(Constants.DOM_VALIDATE_IF_SCHEMA) ||
                   name.equals(Constants.DOM_WHITESPACE_IN_ELEMENT_CONTENT)) {
            return true;
        }
        return false;        
    }

    /**
     * Look up the value of a feature.
     * <br>The feature name has the same form as a DOM hasFeature string
     * 
     * @param name The feature name, which is a string with DOM has-feature 
     *   syntax.
     * @return The current state of the feature (<code>true</code> or 
     *   <code>false</code>).
     * @exception DOMException
     *   Raise a NOT_FOUND_ERR When the <code>DOMBuilder</code> does not 
     *   recognize the feature name.
     */
    public boolean getFeature(String name) throws DOMException {
        if (name.equals(Constants.DOM_COMMENTS)) {
            return fConfiguration.getFeature(INCLUDE_COMMENTS_FEATURE);
        } else if (name.equals(Constants.DOM_DATATYPE_NORMALIZATION)) {
            return fConfiguration.getFeature(NORMALIZE_DATA);
        } else if (name.equals(Constants.DOM_ENTITIES)) {
            return fConfiguration.getFeature(CREATE_ENTITY_REF_NODES);
        } else if (name.equals(Constants.DOM_NAMESPACES)) {
            return fConfiguration.getFeature (NAMESPACES);
        } else if (name.equals(Constants.DOM_VALIDATE)) {
            return fConfiguration.getFeature(VALIDATION_FEATURE);
        } else if (name.equals(Constants.DOM_VALIDATE_IF_SCHEMA)) {
            return fConfiguration.getFeature(DYNAMIC_VALIDATION);
        } else if (name.equals(Constants.DOM_WHITESPACE_IN_ELEMENT_CONTENT)) {
            return fConfiguration.getFeature(INCLUDE_IGNORABLE_WHITESPACE);             
        } else if (name.equals(Constants.DOM_NAMESPACE_DECLARATIONS) || 
                   name.equals(Constants.DOM_CDATA_SECTIONS) ||
                   name.equals(Constants.DOM_CANONICAL_FORM) ||
                   name.equals(Constants.DOM_SUPPORTED_MEDIATYPES_ONLY) ||
                   name.equals(Constants.DOM_INFOSET) ||
                   name.equals(Constants.DOM_CHARSET_OVERRIDES_XML_ENCODING)) {
            return fConfiguration.getFeature(name);
        } else {
            throw new DOMException(DOMException.NOT_FOUND_ERR,"Feature \""+name+"\" not recognized");
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

        // initialize grammar pool
        initGrammarPool();
        try {        
            parse(source);
        } catch (Exception e){
            // REVISIT: report exception via the error handler
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
    public Document parse(DOMInputSource is) throws Exception {

        // need to wrap the DOMInputSource with an XMLInputSource
        XMLInputSource xmlInputSource = dom2xmlInputSource(is);


        // initialize grammar pool
        initGrammarPool();
        try {        
            parse(xmlInputSource);
        } catch (Exception e) {
            // REVISIT: report exception via the error handler
            if (DEBUG) {            
               e.printStackTrace();
            }
        }
        return getDocument();
    }

    protected void initGrammarPool(){

        // REVISIT: do we want to use custome grammar pool to be able
        //          to retrieve a grammar used in validation of the document
        //          for dom revalidation?
        
        /*
        fGrammarPool = (XMLGrammarPool)fConfiguration.getProperty(GRAMMAR_POOL);
        if (fGrammarPool == null) {
            fGrammarPool = new XMLGrammarPoolImpl();
            // set our own grammar pool
            fConfiguration.setProperty(GRAMMAR_POOL, fGrammarPool);
        }
        else {
            //REVISIT: if user sets its own grammar pool do we do anything?
        }
        */
        
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



    /**
     * Overwrite endDocument call to copy some information 
     * required for re-validation of DOM tree.
     * 
     * @param augs
     * @exception XNIException
     */
    public void endDocument(Augmentations augs) throws XNIException {
        super.endDocument(augs);

        // If this is a DOM Level 3 implementation we should copy some information
        if (fDocumentImpl != null) {  
            CoreDocumentImpl doc = (CoreDocumentImpl)fDocument;
            doc.copyConfigurationProperties(fConfiguration);
        }

    } // endDocument()


} // class DOMBuilderImpl
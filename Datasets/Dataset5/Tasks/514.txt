protected class ContentDispatcher

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 1999-2002 The Apache Software Foundation.
 * All rights reserved.
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

package org.apache.xerces.impl;

import java.io.EOFException;
import java.io.IOException;
import java.util.Stack;

import org.apache.xerces.impl.XMLEntityManager;
import org.apache.xerces.impl.XMLEntityScanner;
import org.apache.xerces.impl.XMLErrorReporter;
import org.apache.xerces.impl.msg.XMLMessageFormatter;
import org.apache.xerces.impl.validation.ValidationManager;

import org.apache.xerces.util.XMLAttributesImpl;
import org.apache.xerces.util.XMLStringBuffer;
import org.apache.xerces.util.XMLResourceIdentifierImpl;
import org.apache.xerces.util.SymbolTable;
import org.apache.xerces.util.XMLChar;

import org.apache.xerces.xni.QName;
import org.apache.xerces.xni.XMLAttributes;
import org.apache.xerces.xni.XMLDocumentHandler;
import org.apache.xerces.xni.XMLResourceIdentifier;
import org.apache.xerces.xni.XMLString;
import org.apache.xerces.xni.XNIException;
import org.apache.xerces.xni.parser.XMLComponent;
import org.apache.xerces.xni.parser.XMLComponentManager;
import org.apache.xerces.xni.parser.XMLConfigurationException;
import org.apache.xerces.xni.parser.XMLDocumentScanner;
import org.apache.xerces.xni.parser.XMLDTDScanner;
import org.apache.xerces.xni.parser.XMLInputSource;

/**
 * This class is responsible for scanning XML document structure
 * and content. The scanner acts as the source for the document
 * information which is communicated to the document handler.
 * <p>
 * This component requires the following features and properties from the
 * component manager that uses it:
 * <ul>
 *  <li>http://xml.org/sax/features/namespaces</li>
 *  <li>http://xml.org/sax/features/validation</li>
 *  <li>http://apache.org/xml/features/nonvalidating/load-external-dtd</li>
 *  <li>http://apache.org/xml/features/scanner/notify-char-refs</li>
 *  <li>http://apache.org/xml/features/scanner/notify-builtin-refs</li>
 *  <li>http://apache.org/xml/properties/internal/symbol-table</li>
 *  <li>http://apache.org/xml/properties/internal/error-reporter</li>
 *  <li>http://apache.org/xml/properties/internal/entity-manager</li>
 *  <li>http://apache.org/xml/properties/internal/dtd-scanner</li>
 * </ul>
 *
 * @author Glenn Marcy, IBM
 * @author Andy Clark, IBM
 * @author Arnaud  Le Hors, IBM
 * @author Eric Ye, IBM
 *
 * @version $Id$
 */
public class XMLDocumentScannerImpl
    extends XMLDocumentFragmentScannerImpl {

    //
    // Constants
    //

    // scanner states

    /** Scanner state: XML declaration. */
    protected static final int SCANNER_STATE_XML_DECL = 0;

    /** Scanner state: prolog. */
    protected static final int SCANNER_STATE_PROLOG = 5;

    /** Scanner state: trailing misc. */
    protected static final int SCANNER_STATE_TRAILING_MISC = 12;

    /** Scanner state: DTD internal declarations. */
    protected static final int SCANNER_STATE_DTD_INTERNAL_DECLS = 17;

    /** Scanner state: open DTD external subset. */
    protected static final int SCANNER_STATE_DTD_EXTERNAL = 18;

    /** Scanner state: DTD external declarations. */
    protected static final int SCANNER_STATE_DTD_EXTERNAL_DECLS = 19;

    // feature identifiers

    /** Feature identifier: load external DTD. */
    protected static final String LOAD_EXTERNAL_DTD =
        Constants.XERCES_FEATURE_PREFIX + Constants.LOAD_EXTERNAL_DTD_FEATURE;

    // property identifiers

    /** Property identifier: DTD scanner. */
    protected static final String DTD_SCANNER =
        Constants.XERCES_PROPERTY_PREFIX + Constants.DTD_SCANNER_PROPERTY;

    // property identifier:  ValidationManager
    protected static final String VALIDATION_MANAGER =
        Constants.XERCES_PROPERTY_PREFIX + Constants.VALIDATION_MANAGER_PROPERTY;

    // recognized features and properties

    /** Recognized features. */
    private static final String[] RECOGNIZED_FEATURES = {
        NAMESPACES,
        VALIDATION,
        LOAD_EXTERNAL_DTD,
        NOTIFY_BUILTIN_REFS,
        NOTIFY_CHAR_REFS,
    };

    /** Recognized properties. */
    private static final String[] RECOGNIZED_PROPERTIES = {
        SYMBOL_TABLE,
        ERROR_REPORTER,
        ENTITY_MANAGER,
        DTD_SCANNER,
        VALIDATION_MANAGER,
    };

    //
    // Data
    //

    // properties

    /** DTD scanner. */
    protected XMLDTDScanner fDTDScanner;
    /** Validation manager . */
    protected ValidationManager fValidationManager;

    // protected data

    /** Scanning DTD. */
    protected boolean fScanningDTD;

    // other info

    /** Doctype name. */
    protected String fDoctypeName;

    /** Doctype declaration public identifier. */
    protected String fDoctypePublicId;

    /** Doctype declaration system identifier. */
    protected String fDoctypeSystemId;

    // features

    /** Load external DTD. */
    protected boolean fLoadExternalDTD = true;

    // state

    /** Seen doctype declaration. */
    protected boolean fSeenDoctypeDecl;

    // dispatchers

    /** XML declaration dispatcher. */
    protected Dispatcher fXMLDeclDispatcher = new XMLDeclDispatcher();

    /** Prolog dispatcher. */
    protected Dispatcher fPrologDispatcher = new PrologDispatcher();

    /** DTD dispatcher. */
    protected Dispatcher fDTDDispatcher = new DTDDispatcher();

    /** Trailing miscellaneous section dispatcher. */
    protected Dispatcher fTrailingMiscDispatcher = new TrailingMiscDispatcher();

    // temporary variables

    /** Array of 3 strings. */
    private String[] fStrings = new String[3];

    /** String. */
    private XMLString fString = new XMLString();

    /** String buffer. */
    private XMLStringBuffer fStringBuffer = new XMLStringBuffer();

    //
    // Constructors
    //

    /** Default constructor. */
    public XMLDocumentScannerImpl() {} // <init>()

    //
    // XMLDocumentScanner methods
    //

    /**
     * Sets the input source.
     *
     * @param inputSource The input source.
     *
     * @throws IOException Thrown on i/o error.
     */
    public void setInputSource(XMLInputSource inputSource) throws IOException {
        fEntityManager.setEntityHandler(this);
        fEntityManager.startDocumentEntity(inputSource);
        fDocumentSystemId = fEntityManager.expandSystemId(inputSource.getSystemId());
    } // setInputSource(XMLInputSource)

    //
    // XMLComponent methods
    //

    /**
     * Resets the component. The component can query the component manager
     * about any features and properties that affect the operation of the
     * component.
     *
     * @param componentManager The component manager.
     *
     * @throws SAXException Thrown by component on initialization error.
     *                      For example, if a feature or property is
     *                      required for the operation of the component, the
     *                      component manager may throw a
     *                      SAXNotRecognizedException or a
     *                      SAXNotSupportedException.
     */
    public void reset(XMLComponentManager componentManager)
        throws XMLConfigurationException {

        super.reset(componentManager);

        // other settings
        fDoctypeName = null;
        fDoctypePublicId = null;
        fDoctypeSystemId = null;
        fSeenDoctypeDecl = false;

        // xerces features
        try {
            fLoadExternalDTD = componentManager.getFeature(LOAD_EXTERNAL_DTD);
        }
        catch (XMLConfigurationException e) {
            fLoadExternalDTD = true;
        }
        
        // xerces properties
        fDTDScanner = (XMLDTDScanner)componentManager.getProperty(DTD_SCANNER);
        try {
            fValidationManager = (ValidationManager)componentManager.getProperty(VALIDATION_MANAGER);
        }
        catch (XMLConfigurationException e) {
            fValidationManager = null;
        }

        // initialize vars
        fScanningDTD = false;

        // setup dispatcher
        setScannerState(SCANNER_STATE_XML_DECL);
        setDispatcher(fXMLDeclDispatcher);

    } // reset(XMLComponentManager)

    /**
     * Returns a list of feature identifiers that are recognized by
     * this component. This method may return null if no features
     * are recognized by this component.
     */
    public String[] getRecognizedFeatures() {
        return (String[])(RECOGNIZED_FEATURES.clone());
    } // getRecognizedFeatures():String[]

    /**
     * Sets the state of a feature. This method is called by the component
     * manager any time after reset when a feature changes state.
     * <p>
     * <strong>Note:</strong> Components should silently ignore features
     * that do not affect the operation of the component.
     *
     * @param featureId The feature identifier.
     * @param state     The state of the feature.
     *
     * @throws SAXNotRecognizedException The component should not throw
     *                                   this exception.
     * @throws SAXNotSupportedException The component should not throw
     *                                  this exception.
     */
    public void setFeature(String featureId, boolean state)
        throws XMLConfigurationException {

        super.setFeature(featureId, state);

        // Xerces properties
        if (featureId.startsWith(Constants.XERCES_FEATURE_PREFIX)) {
            String feature = featureId.substring(Constants.XERCES_FEATURE_PREFIX.length());
            if (feature.equals(Constants.LOAD_EXTERNAL_DTD_FEATURE)) {
                fLoadExternalDTD = state;
                return;
            }
        }

    } // setFeature(String,boolean)

    /**
     * Returns a list of property identifiers that are recognized by
     * this component. This method may return null if no properties
     * are recognized by this component.
     */
    public String[] getRecognizedProperties() {
        return (String[])(RECOGNIZED_PROPERTIES.clone());
    } // getRecognizedProperties():String[]

    /**
     * Sets the value of a property. This method is called by the component
     * manager any time after reset when a property changes value.
     * <p>
     * <strong>Note:</strong> Components should silently ignore properties
     * that do not affect the operation of the component.
     *
     * @param propertyId The property identifier.
     * @param value      The value of the property.
     *
     * @throws SAXNotRecognizedException The component should not throw
     *                                   this exception.
     * @throws SAXNotSupportedException The component should not throw
     *                                  this exception.
     */
    public void setProperty(String propertyId, Object value)
        throws XMLConfigurationException {

        super.setProperty(propertyId, value);

        // Xerces properties
        if (propertyId.startsWith(Constants.XERCES_PROPERTY_PREFIX)) {
            String property = propertyId.substring(Constants.XERCES_PROPERTY_PREFIX.length());
            if (property.equals(Constants.DTD_SCANNER_PROPERTY)) {
                fDTDScanner = (XMLDTDScanner)value;
            }
            return;
        }

    } // setProperty(String,Object)

    //
    // XMLEntityHandler methods
    //

    /**
     * This method notifies of the start of an entity. The DTD has the
     * pseudo-name of "[dtd]" parameter entity names start with '%'; and
     * general entities are just specified by their name.
     *
     * @param name     The name of the entity.
     * @param identifier The resource identifier.
     * @param encoding The auto-detected IANA encoding name of the entity
     *                 stream. This value will be null in those situations
     *                 where the entity encoding is not auto-detected (e.g.
     *                 internal entities or a document entity that is
     *                 parsed from a java.io.Reader).
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void startEntity(String name,
                            XMLResourceIdentifier identifier,
                            String encoding) throws XNIException {

        super.startEntity(name, identifier, encoding);

        // prepare to look for a TextDecl if external general entity
        if (!name.equals("[xml]") && fEntityScanner.isExternal()) {
            setScannerState(SCANNER_STATE_TEXT_DECL);
        } 

        // call handler
        if (fDocumentHandler != null && name.equals("[xml]")) {
            fDocumentHandler.startDocument(fEntityScanner, encoding, null);
        }

    } // startEntity(String,identifier,String)

    /**
     * This method notifies the end of an entity. The DTD has the pseudo-name
     * of "[dtd]" parameter entity names start with '%'; and general entities
     * are just specified by their name.
     *
     * @param name The name of the entity.
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void endEntity(String name) throws XNIException {

        super.endEntity(name);

        // call handler
        if (fDocumentHandler != null && name.equals("[xml]")) {
            fDocumentHandler.endDocument(null);
        }

    } // endEntity(String)

    //
    // Protected methods
    //

    // dispatcher factory methods

    /** Creates a content dispatcher. */
    protected Dispatcher createContentDispatcher() {
        return new ContentDispatcher();
    } // createContentDispatcher():Dispatcher

    // scanning methods

    /** Scans a doctype declaration. */
    protected boolean scanDoctypeDecl() throws IOException, XNIException {

        // spaces
        if (!fEntityScanner.skipSpaces()) {
            reportFatalError("MSG_SPACE_REQUIRED_BEFORE_ROOT_ELEMENT_TYPE_IN_DOCTYPEDECL",
                             null);
        }

        // root element name
        fDoctypeName = fEntityScanner.scanName();
        if (fDoctypeName == null) {
            reportFatalError("MSG_ROOT_ELEMENT_TYPE_REQUIRED", null);
        }

        // external id
        if (fEntityScanner.skipSpaces()) {
            scanExternalID(fStrings, false);
            fDoctypeSystemId = fStrings[0];
            fDoctypePublicId = fStrings[1];
            fEntityScanner.skipSpaces();
        }

        fHasExternalDTD = fDoctypeSystemId != null;

        // call handler
        if (fDocumentHandler != null) {
            // NOTE: I don't like calling the doctypeDecl callback until
            //       end of the *full* doctype line (including internal
            //       subset) is parsed correctly but SAX2 requires that
            //       it knows the root element name and public and system
            //       identifier for the startDTD call. -Ac
            fDocumentHandler.doctypeDecl(fDoctypeName, fDoctypePublicId, fDoctypeSystemId,
                                         null);
        }

        // is there an internal subset?
        boolean internalSubset = true;
        if (!fEntityScanner.skipChar('[')) {
            internalSubset = false;
            fEntityScanner.skipSpaces();
            if (!fEntityScanner.skipChar('>')) {
                reportFatalError("DoctypedeclUnterminated", new Object[]{fDoctypeName});
            }
            fMarkupDepth--;
        }

        return internalSubset;

    } // scanDoctypeDecl():boolean

    //
    // Private methods
    //

    /** Returns the scanner state name. */
    protected String getScannerStateName(int state) {

        switch (state) {
            case SCANNER_STATE_XML_DECL: return "SCANNER_STATE_XML_DECL";
            case SCANNER_STATE_PROLOG: return "SCANNER_STATE_PROLOG";
            case SCANNER_STATE_TRAILING_MISC: return "SCANNER_STATE_TRAILING_MISC";
            case SCANNER_STATE_DTD_INTERNAL_DECLS: return "SCANNER_STATE_DTD_INTERNAL_DECLS";
            case SCANNER_STATE_DTD_EXTERNAL: return "SCANNER_STATE_DTD_EXTERNAL";
            case SCANNER_STATE_DTD_EXTERNAL_DECLS: return "SCANNER_STATE_DTD_EXTERNAL_DECLS";
        }
        return super.getScannerStateName(state);

    } // getScannerStateName(int):String

    //
    // Classes
    //

    /**
     * Dispatcher to handle XMLDecl scanning.
     *
     * @author Andy Clark, IBM
     */
    protected final class XMLDeclDispatcher
        implements Dispatcher {

        //
        // Dispatcher methods
        //

        /**
         * Dispatch an XML "event".
         *
         * @param complete True if this dispatcher is intended to scan
         *                 and dispatch as much as possible.
         *
         * @returns True if there is more to dispatch either from this
         *          or a another dispatcher.
         *
         * @throws IOException  Thrown on i/o error.
         * @throws XNIException Thrown on parse error.
         */
        public boolean dispatch(boolean complete)
            throws IOException, XNIException {

            // next dispatcher is prolog regardless of whether there
            // is an XMLDecl in this document
            setScannerState(SCANNER_STATE_PROLOG);
            setDispatcher(fPrologDispatcher);

            // scan XMLDecl
            try {
                if (fEntityScanner.skipString("<?xml")) {
                    fMarkupDepth++;
                    // NOTE: special case where document starts with a PI
                    //       whose name starts with "xml" (e.g. "xmlfoo")
                    if (XMLChar.isName(fEntityScanner.peekChar())) {
                        fStringBuffer.clear();
                        fStringBuffer.append("xml");
                        while (XMLChar.isName(fEntityScanner.peekChar())) {
                            fStringBuffer.append((char)fEntityScanner.scanChar());
                        }
                        String target = fSymbolTable.addSymbol(fStringBuffer.ch, fStringBuffer.offset, fStringBuffer.length);
                        scanPIData(target, fString);
                    }

                    // standard XML declaration
                    else {
                        scanXMLDeclOrTextDecl(false);
                    }
                }
                fEntityManager.fCurrentEntity.mayReadChunks = true;

                // if no XMLDecl, then scan piece of prolog
                return true;
            }

            // premature end of file
            catch (EOFException e) {
                reportFatalError("PrematureEOF", null);
                throw e;
            }


        } // dispatch(boolean):boolean

    } // class XMLDeclDispatcher

    /**
     * Dispatcher to handle prolog scanning.
     *
     * @author Andy Clark, IBM
     */
    protected final class PrologDispatcher
        implements Dispatcher {

        //
        // Dispatcher methods
        //

        /**
         * Dispatch an XML "event".
         *
         * @param complete True if this dispatcher is intended to scan
         *                 and dispatch as much as possible.
         *
         * @returns True if there is more to dispatch either from this
         *          or a another dispatcher.
         *
         * @throws IOException  Thrown on i/o error.
         * @throws XNIException Thrown on parse error.
         */
        public boolean dispatch(boolean complete)
            throws IOException, XNIException {

            try {
                boolean again;
                do {
                    again = false;
                    switch (fScannerState) {
                        case SCANNER_STATE_PROLOG: {
                            fEntityScanner.skipSpaces();
                            if (fEntityScanner.skipChar('<')) {
                                setScannerState(SCANNER_STATE_START_OF_MARKUP);
                                again = true;
                            }
                            else if (fEntityScanner.skipChar('&')) {
                                setScannerState(SCANNER_STATE_REFERENCE);
                                again = true;
                            }
                            else {
                                setScannerState(SCANNER_STATE_CONTENT);
                                again = true;
                            }
                            break;
                        }
                        case SCANNER_STATE_START_OF_MARKUP: {
                            fMarkupDepth++;
                            if (fEntityScanner.skipChar('?')) {
                                setScannerState(SCANNER_STATE_PI);
                                again = true;
                            }
                            else if (fEntityScanner.skipChar('!')) {
                                if (fEntityScanner.skipChar('-')) {
                                    if (!fEntityScanner.skipChar('-')) {
                                        reportFatalError("InvalidCommentStart",
                                                         null);
                                    }
                                    setScannerState(SCANNER_STATE_COMMENT);
                                    again = true;
                                }
                                else if (fEntityScanner.skipString("DOCTYPE")) {
                                    setScannerState(SCANNER_STATE_DOCTYPE);
                                    again = true;
                                }
                                else {
                                    reportFatalError("MarkupNotRecognizedInProlog",
                                                     null);
                                }
                            }
                            else if (XMLChar.isNameStart(fEntityScanner.peekChar())) {
                                setScannerState(SCANNER_STATE_ROOT_ELEMENT);
                                setDispatcher(fContentDispatcher);
                                return true;
                            }
                            else {
                                reportFatalError("MarkupNotRecognizedInProlog",
                                                 null);
                            }
                            break;
                        }
                        case SCANNER_STATE_COMMENT: {
                            scanComment();
                            setScannerState(SCANNER_STATE_PROLOG);
                            break;
                        }
                        case SCANNER_STATE_PI: {
                            scanPI();
                            setScannerState(SCANNER_STATE_PROLOG);
                            break;
                        }
                        case SCANNER_STATE_DOCTYPE: {
                            if (fSeenDoctypeDecl) {
                                reportFatalError("AlreadySeenDoctype", null);
                            }
                            fSeenDoctypeDecl = true;

                            // scanDoctypeDecl() sends XNI doctypeDecl event that 
                            // in SAX is converted to startDTD() event.
                            if (scanDoctypeDecl()) {
                                setScannerState(SCANNER_STATE_DTD_INTERNAL_DECLS);
                                setDispatcher(fDTDDispatcher);
                                return true;
                            }

                            if (fDoctypeSystemId != null && ((fValidation || fLoadExternalDTD) 
                                    && (fValidationManager == null || !fValidationManager.isCachedDTD()))) {
                                setScannerState(SCANNER_STATE_DTD_EXTERNAL);
                                setDispatcher(fDTDDispatcher);
                                return true;
                            } 
                            else {
                                // Send endDTD() call if: 
                                // a) systemId is null
                                // b) "load-external-dtd" and validation are false
                                // c) DTD grammar is cached
                                
                                // in XNI this results in 3 events:  doctypeDecl, startDTD, endDTD
                                // in SAX this results in 2 events: startDTD, endDTD
                                fDTDScanner.setInputSource(null);
                            }
                            setScannerState(SCANNER_STATE_PROLOG);
                            break;
                        }
                        case SCANNER_STATE_CONTENT: {
                            reportFatalError("ContentIllegalInProlog", null);
                            fEntityScanner.scanChar();
                        }
                        case SCANNER_STATE_REFERENCE: {
                            reportFatalError("ReferenceIllegalInProlog", null);
                        }
                    }
                } while (complete || again);

                if (complete) {
                    if (fEntityScanner.scanChar() != '<') {
                        reportFatalError("RootElementRequired", null);
                    }
                    setScannerState(SCANNER_STATE_ROOT_ELEMENT);
                    setDispatcher(fContentDispatcher);
                }
            }

            // premature end of file
            catch (EOFException e) {
                reportFatalError("PrematureEOF", null);
                throw e;
            }

            return true;

        } // dispatch(boolean):boolean

    } // class PrologDispatcher

    /**
     * Dispatcher to handle the internal and external DTD subsets.
     *
     * @author Andy Clark, IBM
     */
    protected final class DTDDispatcher
        implements Dispatcher {

        //
        // Dispatcher methods
        //

        /**
         * Dispatch an XML "event".
         *
         * @param complete True if this dispatcher is intended to scan
         *                 and dispatch as much as possible.
         *
         * @returns True if there is more to dispatch either from this
         *          or a another dispatcher.
         *
         * @throws IOException  Thrown on i/o error.
         * @throws XNIException Thrown on parse error.
         */
        public boolean dispatch(boolean complete)
            throws IOException, XNIException {
            fEntityManager.setEntityHandler(null);
            try {
                boolean again;
		        XMLResourceIdentifierImpl resourceIdentifier = new XMLResourceIdentifierImpl();
                do {
                    again = false;
                    switch (fScannerState) {
                        case SCANNER_STATE_DTD_INTERNAL_DECLS: {
                            // REVISIT: Should there be a feature for
                            //          the "complete" parameter?
                            boolean completeDTD = true;

                            boolean moreToScan = fDTDScanner.scanDTDInternalSubset(completeDTD, fStandalone, fHasExternalDTD && fLoadExternalDTD);
                            if (!moreToScan) {
                                // end doctype declaration
                                if (!fEntityScanner.skipChar(']')) {
                                    reportFatalError("EXPECTED_SQUARE_BRACKET_TO_CLOSE_INTERNAL_SUBSET",
                                                     null);
                                }
                                fEntityScanner.skipSpaces();
                                if (!fEntityScanner.skipChar('>')) {
                                    reportFatalError("DoctypedeclUnterminated", new Object[]{fDoctypeName});
                                }
                                fMarkupDepth--;

                                // scan external subset next
                                if (fDoctypeSystemId != null && (fValidation || fLoadExternalDTD) 
                                        && (fValidationManager == null || !fValidationManager.isCachedDTD())) {
                                    setScannerState(SCANNER_STATE_DTD_EXTERNAL);
                                }

                                // break out of here
                                else {
                                    setScannerState(SCANNER_STATE_PROLOG);
                                    setDispatcher(fPrologDispatcher);
                                    fEntityManager.setEntityHandler(XMLDocumentScannerImpl.this);
                                    return true;
                                }
                            }
                            break;
                        }
                        case SCANNER_STATE_DTD_EXTERNAL: {
			                resourceIdentifier.setValues(fDoctypePublicId, fDoctypeSystemId, null, null);
                            XMLInputSource xmlInputSource =
                                fEntityManager.resolveEntity(resourceIdentifier);
                            fDTDScanner.setInputSource(xmlInputSource);
                            setScannerState(SCANNER_STATE_DTD_EXTERNAL_DECLS);
                            again = true;
                            break;
                        }
                        case SCANNER_STATE_DTD_EXTERNAL_DECLS: {
                            // REVISIT: Should there be a feature for
                            //          the "complete" parameter?
                            boolean completeDTD = true;
                            boolean moreToScan = fDTDScanner.scanDTDExternalSubset(completeDTD);
                            if (!moreToScan) {
                                setScannerState(SCANNER_STATE_PROLOG);
                                setDispatcher(fPrologDispatcher);
                                fEntityManager.setEntityHandler(XMLDocumentScannerImpl.this);
                                return true;
                            }
                            break;
                        }
                        default: {
                            throw new XNIException("DTDDispatcher#dispatch: scanner state="+fScannerState+" ("+getScannerStateName(fScannerState)+')');
                        }
                    }
                } while (complete || again);
            }

            // premature end of file
            catch (EOFException e) {
                reportFatalError("PrematureEOF", null);
                throw e;
            }

            // cleanup
            finally {
                fEntityManager.setEntityHandler(XMLDocumentScannerImpl.this);
            }

            return true;

        } // dispatch(boolean):boolean

    } // class DTDDispatcher

    /**
     * Dispatcher to handle content scanning.
     *
     * @author Andy Clark, IBM
     * @author Eric Ye, IBM
     */
    protected final class ContentDispatcher
        extends FragmentContentDispatcher {

        //
        // Protected methods
        //

        // hooks

        // NOTE: These hook methods are added so that the full document
        //       scanner can share the majority of code with this class.

        /**
         * Scan for DOCTYPE hook. This method is a hook for subclasses
         * to add code to handle scanning for a the "DOCTYPE" string
         * after the string "<!" has been scanned.
         *
         * @returns True if the "DOCTYPE" was scanned; false if "DOCTYPE"
         *          was not scanned.
         */
        protected boolean scanForDoctypeHook()
            throws IOException, XNIException {

            if (fEntityScanner.skipString("DOCTYPE")) {
                setScannerState(SCANNER_STATE_DOCTYPE);
                return true;
            }
            return false;

        } // scanForDoctypeHook():boolean

        /**
         * Element depth iz zero. This methos is a hook for subclasses
         * to add code to handle when the element depth hits zero. When
         * scanning a document fragment, an element depth of zero is
         * normal. However, when scanning a full XML document, the
         * scanner must handle the trailing miscellanous section of
         * the document after the end of the document's root element.
         *
         * @returns True if the caller should stop and return true which
         *          allows the scanner to switch to a new scanning
         *          dispatcher. A return value of false indicates that
         *          the content dispatcher should continue as normal.
         */
        protected boolean elementDepthIsZeroHook()
            throws IOException, XNIException {

            setScannerState(SCANNER_STATE_TRAILING_MISC);
            setDispatcher(fTrailingMiscDispatcher);
            return true;

        } // elementDepthIsZeroHook():boolean

        /**
         * Scan for root element hook. This method is a hook for
         * subclasses to add code that handles scanning for the root
         * element. When scanning a document fragment, there is no
         * "root" element. However, when scanning a full XML document,
         * the scanner must handle the root element specially.
         *
         * @returns True if the caller should stop and return true which
         *          allows the scanner to switch to a new scanning
         *          dispatcher. A return value of false indicates that
         *          the content dispatcher should continue as normal.
         */
        protected boolean scanRootElementHook()
            throws IOException, XNIException {

            if (scanStartElement()) {
                setScannerState(SCANNER_STATE_TRAILING_MISC);
                setDispatcher(fTrailingMiscDispatcher);
                return true;
            }
            return false;

        } // scanRootElementHook():boolean

        /**
         * End of file hook. This method is a hook for subclasses to
         * add code that handles the end of file. The end of file in
         * a document fragment is OK if the markup depth is zero.
         * However, when scanning a full XML document, an end of file
         * is always premature.
         */
        protected void endOfFileHook(EOFException e)
            throws IOException, XNIException {

            reportFatalError("PrematureEOF", null);
            throw e;

        } // endOfFileHook()

    } // class ContentDispatcher

    /**
     * Dispatcher to handle trailing miscellaneous section scanning.
     *
     * @author Andy Clark, IBM
     * @author Eric Ye, IBM
     */
    protected final class TrailingMiscDispatcher
        implements Dispatcher {

        //
        // Dispatcher methods
        //

        /**
         * Dispatch an XML "event".
         *
         * @param complete True if this dispatcher is intended to scan
         *                 and dispatch as much as possible.
         *
         * @returns True if there is more to dispatch either from this
         *          or a another dispatcher.
         *
         * @throws IOException  Thrown on i/o error.
         * @throws XNIException Thrown on parse error.
         */
        public boolean dispatch(boolean complete)
            throws IOException, XNIException {

            try {
                boolean again;
                do {
                    again = false;
                    switch (fScannerState) {
                        case SCANNER_STATE_TRAILING_MISC: {
                            fEntityScanner.skipSpaces();
                            if (fEntityScanner.skipChar('<')) {
                                setScannerState(SCANNER_STATE_START_OF_MARKUP);
                                again = true;
                            }
                            else {
                                setScannerState(SCANNER_STATE_CONTENT);
                                again = true;
                            }
                            break;
                        }
                        case SCANNER_STATE_START_OF_MARKUP: {
                            fMarkupDepth++;
                            if (fEntityScanner.skipChar('?')) {
                                setScannerState(SCANNER_STATE_PI);
                                again = true;
                            }
                            else if (fEntityScanner.skipChar('!')) {
                                setScannerState(SCANNER_STATE_COMMENT);
                                again = true;
                            }
                            /***
                            // REVISIT: Should we detect this?
                            else if (XMLChar.isNameStart(fEntityScanner.peekChar())) {
                                reportFatalError("MarkupNotRecognizedInMisc",
                                                 null);
                                // REVISIT: continue after fatal error
                            }
                            /***/
                            else {
                                reportFatalError("MarkupNotRecognizedInMisc",
                                                 null);
                            }
                            break;
                        }
                        case SCANNER_STATE_PI: {
                            scanPI();
                            setScannerState(SCANNER_STATE_TRAILING_MISC);
                            break;
                        }
                        case SCANNER_STATE_COMMENT: {
                            if (!fEntityScanner.skipString("--")) {
                                reportFatalError("InvalidCommentStart", null);
                            }
                            scanComment();
                            setScannerState(SCANNER_STATE_TRAILING_MISC);
                            break;
                        }
                        case SCANNER_STATE_CONTENT: {
                            int ch = fEntityScanner.peekChar();
                            if (ch == -1) {
                                setScannerState(SCANNER_STATE_TERMINATED);
                                return false;
                            }
                            reportFatalError("ContentIllegalInTrailingMisc",
                                             null);
                            fEntityScanner.scanChar();
                            setScannerState(SCANNER_STATE_TRAILING_MISC);
                            break;
                        }
                        case SCANNER_STATE_REFERENCE: {
                            reportFatalError("ReferenceIllegalInTrailingMisc",
                                             null);
                            setScannerState(SCANNER_STATE_TRAILING_MISC);
                            break;
                        }
                        case SCANNER_STATE_TERMINATED: {
                            return false;
                        }
                    }
                } while (complete || again);
            }
            catch (EOFException e) {
                // NOTE: This is the only place we're allowed to reach
                //       the real end of the document stream. Unless the
                //       end of file was reached prematurely.
                if (fMarkupDepth != 0) {
                    reportFatalError("PrematureEOF", null);
                    throw e;
                }

                setScannerState(SCANNER_STATE_TERMINATED);
                return false;
            }

            return true;

        } // dispatch(boolean):boolean

    } // class TrailingMiscDispatcher

} // class XMLDocumentScannerImpl
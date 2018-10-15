new Object [] { "In element '"+fStringPool.toString(elementType)+"' : "+idve.getMessage()},

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 1999,2000 The Apache Software Foundation.  All rights 
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

package org.apache.xerces.validators.common;

import org.apache.xerces.framework.XMLAttrList;
import org.apache.xerces.framework.XMLContentSpec;
import org.apache.xerces.framework.XMLDocumentHandler;
import org.apache.xerces.framework.XMLDocumentScanner;
import org.apache.xerces.framework.XMLErrorReporter;
import org.apache.xerces.readers.DefaultEntityHandler;
import org.apache.xerces.readers.XMLEntityHandler;
import org.apache.xerces.utils.ChunkyCharArray;
import org.apache.xerces.utils.Hash2intTable;
import org.apache.xerces.utils.NamespacesScope;
import org.apache.xerces.utils.QName;
import org.apache.xerces.utils.StringPool;
import org.apache.xerces.utils.XMLCharacterProperties;
import org.apache.xerces.utils.XMLMessages;
import org.apache.xerces.utils.ImplementationMessages;

import org.apache.xerces.parsers.DOMParser;

import org.w3c.dom.Document;
import org.w3c.dom.Element;

import org.xml.sax.InputSource;
import org.xml.sax.EntityResolver;
import org.xml.sax.Locator;
import org.xml.sax.helpers.LocatorImpl;
import org.xml.sax.SAXException;
import org.xml.sax.SAXParseException;

import java.io.IOException;

import java.util.Enumeration;
import java.util.Hashtable;
import java.util.StringTokenizer;
import java.util.Vector;

import org.apache.xerces.validators.dtd.DTDGrammar;

import org.apache.xerces.validators.schema.EquivClassComparator;
import org.apache.xerces.validators.schema.SchemaGrammar;
import org.apache.xerces.validators.schema.SchemaMessageProvider;
import org.apache.xerces.validators.schema.SchemaSymbols;
import org.apache.xerces.validators.schema.TraverseSchema;

import org.apache.xerces.validators.datatype.DatatypeValidatorFactoryImpl;
import org.apache.xerces.validators.datatype.DatatypeValidator;
import org.apache.xerces.validators.datatype.InvalidDatatypeValueException;
import org.apache.xerces.validators.datatype.StateMessageDatatype;
import org.apache.xerces.validators.datatype.IDREFDatatypeValidator;
import org.apache.xerces.validators.datatype.IDDatatypeValidator;
import org.apache.xerces.validators.datatype.ENTITYDatatypeValidator;

/**
 * This class is the super all-in-one validator used by the parser.
 *
 * @version $Id$
 */
public final class XMLValidator
implements DefaultEntityHandler.EventHandler,
XMLEntityHandler.CharDataHandler,
XMLDocumentScanner.EventHandler,
NamespacesScope.NamespacesHandler {

    //
    // Constants
    //

    // debugging

    private static final boolean PRINT_EXCEPTION_STACK_TRACE = false;
    private static final boolean DEBUG_PRINT_ATTRIBUTES = false;
    private static final boolean DEBUG_PRINT_CONTENT = false;
    private static final boolean DEBUG_SCHEMA_VALIDATION = false;
    private static final boolean DEBUG_ELEMENT_CHILDREN = false;

    // Chunk size constants

    private static final int CHUNK_SHIFT = 8;           // 2^8 = 256
    private static final int CHUNK_SIZE = (1 << CHUNK_SHIFT);
    private static final int CHUNK_MASK = CHUNK_SIZE - 1;
    private static final int INITIAL_CHUNK_COUNT = (1 << (10 - CHUNK_SHIFT));   // 2^10 = 1k

    private Hashtable fIdDefs = null;


    private  StateMessageDatatype fStoreIDRef = new StateMessageDatatype() {
        private Hashtable fIdDefs;
        public Object getDatatypeObject(){
            return(Object) fIdDefs;
        }
        public int    getDatatypeState(){
            return IDREFDatatypeValidator.IDREF_STORE;
        }
        public void setDatatypeObject( Object data ){
            fIdDefs = (Hashtable) data;
        }
    };

    private StateMessageDatatype fResetID = new StateMessageDatatype() {
        public Object getDatatypeObject(){
            return(Object) null;
        }
        public int    getDatatypeState(){
            return IDDatatypeValidator.ID_CLEAR;
        }
        public void setDatatypeObject( Object data ){
        }
    };


    private StateMessageDatatype fResetIDRef = new StateMessageDatatype() {
        public Object getDatatypeObject(){
            return(Object) null;
        }
        public int    getDatatypeState(){
            return IDREFDatatypeValidator.IDREF_CLEAR;
        }
        public void setDatatypeObject( Object data ){
        }
    };

    private  StateMessageDatatype fValidateIDRef = new StateMessageDatatype() {
        public Object getDatatypeObject(){
            return(Object) null;
        }
        public int    getDatatypeState(){
            return IDREFDatatypeValidator.IDREF_VALIDATE;
        }
        public void setDatatypeObject( Object data ){
        }
    };


    private  StateMessageDatatype fValidateENTITYMsg = new StateMessageDatatype() {
        private  Object  packagedMessage = null;
        public Object getDatatypeObject(){
            return packagedMessage;
        }
        public int    getDatatypeState(){
            return ENTITYDatatypeValidator.ENTITY_INITIALIZE;//No state
        }
        public void setDatatypeObject( Object data ){
            packagedMessage = data;// Set Entity Handler
        }
    };

    /*
    private  StateMessageDatatype fValidateNOTATIONMsg = new StateMessageDatatype() {
        private  Object  packagedMessage = null;
        public Object getDatatypeObject(){
            return packagedMessage;
        }
        public int    getDatatypeState(){
            return NOTATIONDatatypeValidator.ENTITY_INITIALIZE;//No state
        }
        public void setDatatypeObject( Object data ){
            packagedMessage = data;// Set Entity Handler
        }
    };
    */





    //
    // Data
    //

    // REVISIT: The data should be regrouped and re-organized so that
    //          it's easier to find a meaningful field.

    // debugging

//    private static boolean DEBUG = false;

    // other

    // attribute validators

    private AttributeValidator fAttValidatorNOTATION = new AttValidatorNOTATION();
    private AttributeValidator fAttValidatorENUMERATION = new AttValidatorENUMERATION();
    private AttributeValidator fAttValidatorDATATYPE = null;

    // Package access for use by AttributeValidator classes.

    StringPool fStringPool = null;
    boolean fValidating = false;
    boolean fInElementContent = false;
    int fStandaloneReader = -1;


    // settings

    private boolean fValidationEnabled = false;
    private boolean fDynamicValidation = false;
    private boolean fSchemaValidation = true;
    private boolean fValidationEnabledByDynamic = false;
    private boolean fDynamicDisabledByValidation = false;
    private boolean fWarningOnDuplicateAttDef = false;
    private boolean fWarningOnUndeclaredElements = false;
    private boolean fLoadDTDGrammar = true;

    // declarations

    private int fDeclaration[];
    private XMLErrorReporter fErrorReporter = null;
    private DefaultEntityHandler fEntityHandler = null;
    private QName fCurrentElement = new QName();

    private ContentLeafNameTypeVector[] fContentLeafStack = new ContentLeafNameTypeVector[8];
    private int[] fValidationFlagStack = new int[8];

    private int[] fScopeStack = new int[8];
    private int[] fGrammarNameSpaceIndexStack = new int[8];

    private int[] fElementEntityStack = new int[8];
    private int[] fElementIndexStack = new int[8];
    private int[] fContentSpecTypeStack = new int[8];

    private static final int sizeQNameParts      = 8;
    private QName[] fElementQNamePartsStack      = new QName[sizeQNameParts];

    private QName[] fElementChildren = new QName[32];
    private int fElementChildrenLength = 0;
    private int[] fElementChildrenOffsetStack = new int[32];
    private int fElementDepth = -1;

    private boolean fNamespacesEnabled = false;
    private NamespacesScope fNamespacesScope = null;
    private int fNamespacesPrefix = -1;
    private QName fRootElement = new QName();
    private int fAttrListHandle = -1;
    private int fCurrentElementEntity = -1;
    private int fCurrentElementIndex = -1;
    private int fCurrentContentSpecType = -1;
    private boolean fSeenDoctypeDecl = false;

    private final int TOP_LEVEL_SCOPE = -1;
    private int fCurrentScope = TOP_LEVEL_SCOPE;
    private int fCurrentSchemaURI = -1;
    private int fEmptyURI = - 1; 
    private int fXsiPrefix = - 1;
    private int fXsiURI = -2; 
    private int fXsiTypeAttValue = -1;
    private DatatypeValidator fXsiTypeValidator = null;

    private Grammar fGrammar = null;
    private int fGrammarNameSpaceIndex = -1;
    private GrammarResolver fGrammarResolver = null;

    // state and stuff

    private boolean fScanningDTD = false;
    private XMLDocumentScanner fDocumentScanner = null;
    private boolean fCalledStartDocument = false;
    private XMLDocumentHandler fDocumentHandler = null;
    private XMLDocumentHandler.DTDHandler fDTDHandler = null;
    private boolean fSeenRootElement = false;
    private XMLAttrList fAttrList = null;
    private int fXMLLang = -1;
    private LocatorImpl fAttrNameLocator = null;
    private boolean fCheckedForSchema = false;
    private boolean fDeclsAreExternal = false;
    private StringPool.CharArrayRange fCurrentElementCharArrayRange = null;
    private char[] fCharRefData = null;
    private boolean fSendCharDataAsCharArray = false;
    private boolean fBufferDatatype = false;
    private StringBuffer fDatatypeBuffer = new StringBuffer();

    private QName fTempQName = new QName();
    private XMLAttributeDecl fTempAttDecl = new XMLAttributeDecl();
    private XMLAttributeDecl fTempAttributeDecl = new XMLAttributeDecl();
    private XMLElementDecl fTempElementDecl = new XMLElementDecl();

    private boolean fGrammarIsDTDGrammar = false;
    private boolean fGrammarIsSchemaGrammar = false;

    private boolean fNeedValidationOff = false;

    // symbols

    private int fEMPTYSymbol = -1;
    private int fANYSymbol = -1;
    private int fMIXEDSymbol = -1;
    private int fCHILDRENSymbol = -1;
    private int fCDATASymbol = -1;
    private int fIDSymbol = -1;
    private int fIDREFSymbol = -1;
    private int fIDREFSSymbol = -1;
    private int fENTITYSymbol = -1;
    private int fENTITIESSymbol = -1;
    private int fNMTOKENSymbol = -1;
    private int fNMTOKENSSymbol = -1;
    private int fNOTATIONSymbol = -1;
    private int fENUMERATIONSymbol = -1;
    private int fREQUIREDSymbol = -1;
    private int fFIXEDSymbol = -1;
    private int fDATATYPESymbol = -1;
    private int fEpsilonIndex = -1;


    //Datatype Registry

    private DatatypeValidatorFactoryImpl fDataTypeReg = 
    DatatypeValidatorFactoryImpl.getDatatypeRegistry();

    private DatatypeValidator     fValID   = this.fDataTypeReg.getDatatypeValidator("ID" );
    private DatatypeValidator fValIDRef    = this.fDataTypeReg.getDatatypeValidator("IDREF" );
    private DatatypeValidator fValIDRefs   = this.fDataTypeReg.getDatatypeValidator("IDREFS" );
    private DatatypeValidator fValENTITY   = this.fDataTypeReg.getDatatypeValidator("ENTITY" );
    private DatatypeValidator fValENTITIES = this.fDataTypeReg.getDatatypeValidator("ENTITIES" );
    private DatatypeValidator fValNMTOKEN  = this.fDataTypeReg.getDatatypeValidator("NMTOKEN");
    private DatatypeValidator fValNMTOKENS = this.fDataTypeReg.getDatatypeValidator("NMTOKENS");
    private DatatypeValidator fValNOTATION = this.fDataTypeReg.getDatatypeValidator("NOTATION" );


    //
    // Constructors
    //

    /** Constructs an XML validator. */
    public XMLValidator(StringPool stringPool,
                        XMLErrorReporter errorReporter,
                        DefaultEntityHandler entityHandler,
                        XMLDocumentScanner documentScanner) {

        // keep references
        fStringPool = stringPool;
        fErrorReporter = errorReporter;
        fEntityHandler = entityHandler;
        fDocumentScanner = documentScanner;

        fEmptyURI = fStringPool.addSymbol("");
        fXsiURI = fStringPool.addSymbol(SchemaSymbols.URI_XSI);
        // initialize
        fAttrList = new XMLAttrList(fStringPool);
        entityHandler.setEventHandler(this);
        entityHandler.setCharDataHandler(this);
        fDocumentScanner.setEventHandler(this);

        for (int i = 0; i < sizeQNameParts; i++) {
            fElementQNamePartsStack[i] = new QName();
        }
        init();

    } // <init>(StringPool,XMLErrorReporter,DefaultEntityHandler,XMLDocumentScanner)

    public void setGrammarResolver(GrammarResolver grammarResolver){
        fGrammarResolver = grammarResolver;
    }

    //
    // Public methods
    //

    // initialization

    /** Set char data processing preference and handlers. */
    public void initHandlers(boolean sendCharDataAsCharArray,
                             XMLDocumentHandler docHandler,
                             XMLDocumentHandler.DTDHandler dtdHandler) {

        fSendCharDataAsCharArray = sendCharDataAsCharArray;
        fEntityHandler.setSendCharDataAsCharArray(fSendCharDataAsCharArray);
        fDocumentHandler = docHandler;
        fDTDHandler = dtdHandler;

    } // initHandlers(boolean,XMLDocumentHandler,XMLDocumentHandler.DTDHandler)

    /** Reset or copy. */
    public void resetOrCopy(StringPool stringPool) throws Exception {
        fAttrList = new XMLAttrList(stringPool);
        resetCommon(stringPool);
    }

    /** Reset. */
    public void reset(StringPool stringPool) throws Exception {
        fAttrList.reset(stringPool);
        resetCommon(stringPool);
    }


    // settings

    /**
     * Turning on validation/dynamic turns on validation if it is off, and 
     * this is remembered.  Turning off validation DISABLES validation/dynamic
     * if it is on.  Turning off validation/dynamic DOES NOT turn off
     * validation if it was explicitly turned on, only if it was turned on
     * BECAUSE OF the call to turn validation/dynamic on.  Turning on
     * validation will REENABLE and turn validation/dynamic back on if it
     * was disabled by a call that turned off validation while 
     * validation/dynamic was enabled.
     */
    public void setValidationEnabled(boolean flag) throws Exception {
        fValidationEnabled = flag;
        fValidationEnabledByDynamic = false;
        if (fValidationEnabled) {
            if (fDynamicDisabledByValidation) {
                fDynamicValidation = true;
                fDynamicDisabledByValidation = false;
            }
        } else if (fDynamicValidation) {
            fDynamicValidation = false;
            fDynamicDisabledByValidation = true;
        }
        fValidating = fValidationEnabled;
    }

    /** Returns true if validation is enabled. */
    public boolean getValidationEnabled() {
        return fValidationEnabled;
    }

    /** Sets whether Schema support is on/off. */
    public void setSchemaValidationEnabled(boolean flag) {
        fSchemaValidation = flag;
    }

    /** Returns true if Schema support is on. */
    public boolean getSchemaValidationEnabled() {
        return fSchemaValidation;
    }

    /** Sets whether validation is dynamic. */
    public void setDynamicValidationEnabled(boolean flag) throws Exception {
        fDynamicValidation = flag;
        fDynamicDisabledByValidation = false;
        if (!fDynamicValidation) {
            if (fValidationEnabledByDynamic) {
                fValidationEnabled = false;
                fValidationEnabledByDynamic = false;
            }
        } else if (!fValidationEnabled) {
            fValidationEnabled = true;
            fValidationEnabledByDynamic = true;
        }
        fValidating = fValidationEnabled;
    }

    /** Returns true if validation is dynamic. */
    public boolean getDynamicValidationEnabled() {
        return fDynamicValidation;
    }

    /** Sets fLoadDTDGrammar when validation is off **/
    public void setLoadDTDGrammar(boolean loadDG){
        if (fValidating) {
            fLoadDTDGrammar = true;
        } else {
            fLoadDTDGrammar = loadDG;
        }
    }

    /** Returns fLoadDTDGrammar **/
    public boolean getLoadDTDGrammar() {
        return fLoadDTDGrammar;
    }

    /** Sets whether namespaces are enabled. */
    public void setNamespacesEnabled(boolean flag) {
        fNamespacesEnabled = flag;
    }

    /** Returns true if namespaces are enabled. */
    public boolean getNamespacesEnabled() {
        return fNamespacesEnabled;
    }

    /** Sets whether duplicate attribute definitions signal a warning. */
    public void setWarningOnDuplicateAttDef(boolean flag) {
        fWarningOnDuplicateAttDef = flag;
    }

    /** Returns true if duplicate attribute definitions signal a warning. */
    public boolean getWarningOnDuplicateAttDef() {
        return fWarningOnDuplicateAttDef;
    }

    /** Sets whether undeclared elements signal a warning. */
    public void setWarningOnUndeclaredElements(boolean flag) {
        fWarningOnUndeclaredElements = flag;
    }

    /** Returns true if undeclared elements signal a warning. */
    public boolean getWarningOnUndeclaredElements() {
        return fWarningOnUndeclaredElements;
    }

    //
    // DefaultEntityHandler.EventHandler methods
    //

    /** Start entity reference. */
    public void startEntityReference(int entityName, int entityType, int entityContext) throws Exception {
        fDocumentHandler.startEntityReference(entityName, entityType, entityContext);
    }

    /** End entity reference. */
    public void endEntityReference(int entityName, int entityType, int entityContext) throws Exception {
        fDocumentHandler.endEntityReference(entityName, entityType, entityContext);
    }

    /** Send end of input notification. */
    public void sendEndOfInputNotifications(int entityName, boolean moreToFollow) throws Exception {
        fDocumentScanner.endOfInput(entityName, moreToFollow);
        /***
        if (fScanningDTD) {
            fDTDImporter.sendEndOfInputNotifications(entityName, moreToFollow);
        }
        /***/
    }

    /** Send reader change notifications. */
    public void sendReaderChangeNotifications(XMLEntityHandler.EntityReader reader, int readerId) throws Exception {
        fDocumentScanner.readerChange(reader, readerId);
        /***
        if (fScanningDTD) {
            fDTDImporter.sendReaderChangeNotifications(reader, readerId);
        }
        /***/
    }

    /** External entity standalone check. */
    public boolean externalEntityStandaloneCheck() {
        return(fStandaloneReader != -1 && fValidating);
    }

    /** Return true if validating. */
    public boolean getValidating() {
        return fValidating;
    }

    //
    // XMLEntityHandler.CharDataHandler methods
    //

    /** Process characters. */
    public void processCharacters(char[] chars, int offset, int length) throws Exception {
        if (fValidating) {
            if (fInElementContent || fCurrentContentSpecType == XMLElementDecl.TYPE_EMPTY) {
                charDataInContent();
            }
            if (fBufferDatatype) {
                fDatatypeBuffer.append(chars, offset, length);
            }
        }
        fDocumentHandler.characters(chars, offset, length);
    }

    /** Process characters. */
    public void processCharacters(int data) throws Exception {
        if (fValidating) {
            if (fInElementContent || fCurrentContentSpecType == XMLElementDecl.TYPE_EMPTY) {
                charDataInContent();
            }
            if (fBufferDatatype) {
                fDatatypeBuffer.append(fStringPool.toString(data));
            }
        }
        fDocumentHandler.characters(data);
    }

    /** Process whitespace. */
    public void processWhitespace(char[] chars, int offset, int length) 
    throws Exception {

        if (fInElementContent) {
            if (fStandaloneReader != -1 && fValidating && getElementDeclIsExternal(fCurrentElementIndex)) {
                reportRecoverableXMLError(XMLMessages.MSG_WHITE_SPACE_IN_ELEMENT_CONTENT_WHEN_STANDALONE,
                                          XMLMessages.VC_STANDALONE_DOCUMENT_DECLARATION);
            }
            fDocumentHandler.ignorableWhitespace(chars, offset, length);
        } else {
            if (fCurrentContentSpecType == XMLElementDecl.TYPE_EMPTY) {
                charDataInContent();
            }
            fDocumentHandler.characters(chars, offset, length);
        }

    } // processWhitespace(char[],int,int)

    /** Process whitespace. */
    public void processWhitespace(int data) throws Exception {

        if (fInElementContent) {
            if (fStandaloneReader != -1 && fValidating && getElementDeclIsExternal(fCurrentElementIndex)) {
                reportRecoverableXMLError(XMLMessages.MSG_WHITE_SPACE_IN_ELEMENT_CONTENT_WHEN_STANDALONE,
                                          XMLMessages.VC_STANDALONE_DOCUMENT_DECLARATION);
            }
            fDocumentHandler.ignorableWhitespace(data);
        } else {
            if (fCurrentContentSpecType == XMLElementDecl.TYPE_EMPTY) {
                charDataInContent();
            }
            fDocumentHandler.characters(data);
        }

    } // processWhitespace(int)

    //
    // XMLDocumentScanner.EventHandler methods
    //

    /** Scans element type. */
    public void scanElementType(XMLEntityHandler.EntityReader entityReader, 
                                char fastchar, QName element) throws Exception {

        if (!fNamespacesEnabled) {
            element.clear();
            element.localpart = entityReader.scanName(fastchar);
            element.rawname = element.localpart;
        } else {
            entityReader.scanQName(fastchar, element);
            if (entityReader.lookingAtChar(':', false)) {
                fErrorReporter.reportError(fErrorReporter.getLocator(),
                                           XMLMessages.XML_DOMAIN,
                                           XMLMessages.MSG_TWO_COLONS_IN_QNAME,
                                           XMLMessages.P5_INVALID_CHARACTER,
                                           null,
                                           XMLErrorReporter.ERRORTYPE_FATAL_ERROR);
                entityReader.skipPastNmtoken(' ');
            }
        }

    } // scanElementType(XMLEntityHandler.EntityReader,char,QName)

    /** Scans expected element type. */
    public boolean scanExpectedElementType(XMLEntityHandler.EntityReader entityReader, 
                                           char fastchar, QName element) 
    throws Exception {

        if (fCurrentElementCharArrayRange == null) {
            fCurrentElementCharArrayRange = fStringPool.createCharArrayRange();
        }
        fStringPool.getCharArrayRange(fCurrentElement.rawname, fCurrentElementCharArrayRange);
        return entityReader.scanExpectedName(fastchar, fCurrentElementCharArrayRange);

    } // scanExpectedElementType(XMLEntityHandler.EntityReader,char,QName)

    /** Scans attribute name. */
    public void scanAttributeName(XMLEntityHandler.EntityReader entityReader, 
                                  QName element, QName attribute) 
    throws Exception {

        if (!fSeenRootElement) {
            fSeenRootElement = true;
            rootElementSpecified(element);
            fStringPool.resetShuffleCount();
        }

        if (!fNamespacesEnabled) {
            attribute.clear();
            attribute.localpart = entityReader.scanName('=');
            attribute.rawname = attribute.localpart;
        } else {
            entityReader.scanQName('=', attribute);
            if (entityReader.lookingAtChar(':', false)) {
                fErrorReporter.reportError(fErrorReporter.getLocator(),
                                           XMLMessages.XML_DOMAIN,
                                           XMLMessages.MSG_TWO_COLONS_IN_QNAME,
                                           XMLMessages.P5_INVALID_CHARACTER,
                                           null,
                                           XMLErrorReporter.ERRORTYPE_FATAL_ERROR);
                entityReader.skipPastNmtoken(' ');
            }
        }

    } // scanAttributeName(XMLEntityHandler.EntityReader,QName,QName)

    /** Call start document. */
    public void callStartDocument() throws Exception {

        if (!fCalledStartDocument) {
            fDocumentHandler.startDocument();
            fCalledStartDocument = true;
        }
    }

    /** Call end document. */
    public void callEndDocument() throws Exception {

        if (fCalledStartDocument) {
            fDocumentHandler.endDocument();
        }
    }

    /** Call XML declaration. */
    public void callXMLDecl(int version, int encoding, int standalone) throws Exception {
        fDocumentHandler.xmlDecl(version, encoding, standalone);
    }
    public void callStandaloneIsYes() throws Exception {
        // standalone = "yes". said XMLDocumentScanner.
        fStandaloneReader = fEntityHandler.getReaderId() ;

    }



    /** Call text declaration. */
    public void callTextDecl(int version, int encoding) throws Exception {
        fDocumentHandler.textDecl(version, encoding);
    }

    /**
     * Signal the scanning of an element name in a start element tag.
     *
     * @param element Element name scanned.
     */
    public void element(QName element) throws Exception {
        fAttrListHandle = -1;
    }
    /**
     * Signal the scanning of an attribute associated to the previous
     * start element tag.
     *
     * @param element Element name scanned.
     * @param attrName Attribute name scanned.
     * @param attrValue The string pool index of the attribute value.
     */
    public boolean attribute(QName element, QName attrName, int attrValue) throws Exception {
        if (fAttrListHandle == -1) {
            fAttrListHandle = fAttrList.startAttrList();
        }

        // if fAttrList.addAttr returns -1, indicates duplicate att in start tag of an element.
        // specified: true, search : true
        return fAttrList.addAttr(attrName, attrValue, fCDATASymbol, true, true) == -1;
    }

    /** Call start element. */
    public void callStartElement(QName element) throws Exception {

        if ( DEBUG_SCHEMA_VALIDATION )
            System.out.println("\n=======StartElement : " + fStringPool.toString(element.localpart));


        //
        // Check after all specified attrs are scanned
        // (1) report error for REQUIRED attrs that are missing (V_TAGc)
        // (2) add default attrs (FIXED and NOT_FIXED)
        //

        if (!fSeenRootElement) {
            fSeenRootElement = true;
            rootElementSpecified(element);
            fStringPool.resetShuffleCount();
        }

        if (fGrammar != null && fGrammarIsDTDGrammar) {
            fAttrListHandle = addDTDDefaultAttributes(element, fAttrList, fAttrListHandle, fValidating, fStandaloneReader != -1);
        }

        fCheckedForSchema = true;
        if (fNamespacesEnabled) {
            bindNamespacesToElementAndAttributes(element, fAttrList);
        }

        validateElementAndAttributes(element, fAttrList);
        if (fAttrListHandle != -1) {
            fAttrList.endAttrList();
        }

        fDocumentHandler.startElement(element, fAttrList, fAttrListHandle);
        fAttrListHandle = -1;

        //before we increment the element depth, add this element's QName to its enclosing element 's children list
        fElementDepth++;
        //if (fElementDepth >= 0) {
        if (fValidating) {
            // push current length onto stack
            if (fElementChildrenOffsetStack.length < fElementDepth) {
                int newarray[] = new int[fElementChildrenOffsetStack.length * 2];
                System.arraycopy(fElementChildrenOffsetStack, 0, newarray, 0, fElementChildrenOffsetStack.length);
                fElementChildrenOffsetStack = newarray;
            }
            fElementChildrenOffsetStack[fElementDepth] = fElementChildrenLength;

            // add this element to children
            if (fElementChildren.length <= fElementChildrenLength) {
                QName[] newarray = new QName[fElementChildrenLength * 2];
                System.arraycopy(fElementChildren, 0, newarray, 0, fElementChildren.length);
                fElementChildren = newarray;
            }
            QName qname = fElementChildren[fElementChildrenLength];
            if (qname == null) {
                for (int i = fElementChildrenLength; i < fElementChildren.length; i++) {
                    fElementChildren[i] = new QName();
                }
                qname = fElementChildren[fElementChildrenLength];
            }
            qname.setValues(element);
            fElementChildrenLength++;

            if (DEBUG_ELEMENT_CHILDREN) {
                printChildren();
                printStack();
            }
        }

        // One more level of depth
        //fElementDepth++;

        ensureStackCapacity(fElementDepth);
        fCurrentElement.setValues(element);
        fCurrentElementEntity = fEntityHandler.getReaderId();

        fElementQNamePartsStack[fElementDepth].setValues(fCurrentElement); 

        fElementEntityStack[fElementDepth] = fCurrentElementEntity;
        fElementIndexStack[fElementDepth] = fCurrentElementIndex;
        fContentSpecTypeStack[fElementDepth] = fCurrentContentSpecType;

        if (fNeedValidationOff) {
            fValidating = false;
            fNeedValidationOff = false;
        }

        if (fValidating && fGrammarIsSchemaGrammar) {
            pushContentLeafStack();
        }

        fValidationFlagStack[fElementDepth] = fValidating ? 0 : -1;

        fScopeStack[fElementDepth] = fCurrentScope;
        fGrammarNameSpaceIndexStack[fElementDepth] = fGrammarNameSpaceIndex;

    } // callStartElement(QName)

    private void pushContentLeafStack() throws Exception {
        int contentType = getContentSpecType(fCurrentElementIndex);
        if ( contentType == XMLElementDecl.TYPE_CHILDREN) {
            XMLContentModel cm = getElementContentModel(fCurrentElementIndex);
            ContentLeafNameTypeVector cv = cm.getContentLeafNameTypeVector();
            if (cm != null) {
                fContentLeafStack[fElementDepth] = cv;
            }
        }
    }

    private void ensureStackCapacity ( int newElementDepth) {

        if (newElementDepth == fElementQNamePartsStack.length ) {
            int[] newStack = new int[newElementDepth * 2];
            System.arraycopy(fScopeStack, 0, newStack, 0, newElementDepth);
            fScopeStack = newStack;

            newStack = new int[newElementDepth * 2];
            System.arraycopy(fGrammarNameSpaceIndexStack, 0, newStack, 0, newElementDepth);
            fGrammarNameSpaceIndexStack = newStack;

            QName[] newStackOfQueue = new QName[newElementDepth * 2];
            System.arraycopy(this.fElementQNamePartsStack, 0, newStackOfQueue, 0, newElementDepth );
            fElementQNamePartsStack      = newStackOfQueue;

            QName qname = fElementQNamePartsStack[newElementDepth];
            if (qname == null) {
                for (int i = newElementDepth; i < fElementQNamePartsStack.length; i++) {
                    fElementQNamePartsStack[i] = new QName();
                }
            }

            newStack = new int[newElementDepth * 2];
            System.arraycopy(fElementEntityStack, 0, newStack, 0, newElementDepth);
            fElementEntityStack = newStack;

            newStack = new int[newElementDepth * 2];
            System.arraycopy(fElementIndexStack, 0, newStack, 0, newElementDepth);
            fElementIndexStack = newStack;

            newStack = new int[newElementDepth * 2];
            System.arraycopy(fContentSpecTypeStack, 0, newStack, 0, newElementDepth);
            fContentSpecTypeStack = newStack;

            newStack = new int[newElementDepth * 2];
            System.arraycopy(fValidationFlagStack, 0, newStack, 0, newElementDepth);
            fValidationFlagStack = newStack;

            ContentLeafNameTypeVector[] newStackV = new ContentLeafNameTypeVector[newElementDepth * 2];
            System.arraycopy(fContentLeafStack, 0, newStackV, 0, newElementDepth);
            fContentLeafStack = newStackV;
        }
    }

    /** Call end element. */
    public void callEndElement(int readerId) throws Exception {
        if ( DEBUG_SCHEMA_VALIDATION )
            System.out.println("=======EndElement : " + fStringPool.toString(fCurrentElement.localpart)+"\n");

        int prefixIndex = fCurrentElement.prefix;
        int elementType = fCurrentElement.rawname;

        if (fCurrentElementEntity != readerId) {
            fErrorReporter.reportError(fErrorReporter.getLocator(),
                                       XMLMessages.XML_DOMAIN,
                                       XMLMessages.MSG_ELEMENT_ENTITY_MISMATCH,
                                       XMLMessages.P78_NOT_WELLFORMED,
                                       new Object[] { fStringPool.toString(elementType)},
                                       XMLErrorReporter.ERRORTYPE_FATAL_ERROR);
        }

        fElementDepth--;
        if (fValidating) {
            int elementIndex = fCurrentElementIndex;
            if (elementIndex != -1 && fCurrentContentSpecType != -1) {
                QName children[] = fElementChildren;
                int childrenOffset = fElementChildrenOffsetStack[fElementDepth + 1] + 1;
                int childrenLength = fElementChildrenLength - childrenOffset;
                if (DEBUG_ELEMENT_CHILDREN) {
                    System.out.println("endElement("+fStringPool.toString(fCurrentElement.rawname)+')');
                    System.out.println("fCurrentContentSpecType : " + fCurrentContentSpecType );
                    System.out.print("offset: ");
                    System.out.print(childrenOffset);
                    System.out.print(", length: ");
                    System.out.print(childrenLength);
                    System.out.println();
                    printChildren();
                    printStack();
                }
                int result = checkContent(elementIndex, 
                                          children, childrenOffset, childrenLength);

                if ( DEBUG_SCHEMA_VALIDATION )
                    System.out.println("!!!!!!!!In XMLValidator, the return value from checkContent : " + result);

                if (result != -1) {
                    int majorCode = result != childrenLength ? XMLMessages.MSG_CONTENT_INVALID : XMLMessages.MSG_CONTENT_INCOMPLETE;
                    fGrammar.getElementDecl(elementIndex, fTempElementDecl);
                    if (fTempElementDecl.type == XMLElementDecl.TYPE_EMPTY) {
                        reportRecoverableXMLError(majorCode,
                                                  0,
                                                  fStringPool.toString(elementType),
                                                  "EMPTY");
                    } else
                        reportRecoverableXMLError(majorCode,
                                                  0,
                                                  fStringPool.toString(elementType),
                                                  XMLContentSpec.toString(fGrammar, fStringPool, fTempElementDecl.contentSpecIndex));
                }
            }
            fElementChildrenLength = fElementChildrenOffsetStack[fElementDepth + 1] + 1;
        }
        fDocumentHandler.endElement(fCurrentElement);
        if (fNamespacesEnabled) {
            fNamespacesScope.decreaseDepth();
        }

        // now pop this element off the top of the element stack
        //if (fElementDepth-- < 0) {
        if (fElementDepth < -1) {
            throw new RuntimeException("FWK008 Element stack underflow");
        }
        if (fElementDepth < 0) {
            fCurrentElement.clear();
            fCurrentElementEntity = -1;
            fCurrentElementIndex = -1;
            fCurrentContentSpecType = -1;
            fInElementContent = false;
            //
            // Check after document is fully parsed
            // (1) check that there was an element with a matching id for every
            //   IDREF and IDREFS attr (V_IDREF0)
            //
            if (fValidating ) {
                try {
                    this.fValIDRef.validate( null, this.fValidateIDRef );   
                    this.fValIDRefs.validate( null, this.fValidateIDRef );
                } catch ( InvalidDatatypeValueException ex ) {
                    reportRecoverableXMLError( ex.getMajorCode(), ex.getMinorCode(), 
                                               ex.getMessage() ); 


                }
            }
            
            try {//Reset datatypes state
               this.fValID.validate( null, this.fResetID );
               this.fValIDRef.validate(null, this.fResetIDRef );
               this.fValIDRefs.validate(null, this.fResetIDRef );
            } catch ( InvalidDatatypeValueException ex ) {
                System.err.println("Error re-Initializing: ID,IDRef,IDRefs pools" );
            }
            return;
        }


        //restore enclosing element to all the "current" variables
        // REVISIT: Validation. This information needs to be stored.
        fCurrentElement.prefix = -1;


        if (fNamespacesEnabled) { //If Namespace enable then localName != rawName
            fCurrentElement.localpart = fElementQNamePartsStack[fElementDepth].localpart;
        } else {//REVISIT - jeffreyr - This is so we still do old behavior when namespace is off 
            fCurrentElement.localpart = fElementQNamePartsStack[fElementDepth].rawname;
        }
        fCurrentElement.rawname      = fElementQNamePartsStack[fElementDepth].rawname;
        fCurrentElement.uri          = fElementQNamePartsStack[fElementDepth].uri;
        fCurrentElement.prefix       = fElementQNamePartsStack[fElementDepth].prefix;


        fCurrentElementEntity = fElementEntityStack[fElementDepth];
        fCurrentElementIndex = fElementIndexStack[fElementDepth];
        fCurrentContentSpecType = fContentSpecTypeStack[fElementDepth];

        fValidating = fValidationFlagStack[fElementDepth] == 0 ? true : false;

        fCurrentScope = fScopeStack[fElementDepth];  

        //if ( DEBUG_SCHEMA_VALIDATION ) {

/****
System.out.println("+++++ currentElement : " + fStringPool.toString(elementType)+
                   "\n fCurrentElementIndex : " + fCurrentElementIndex +
                   "\n fCurrentScope : " + fCurrentScope +
                   "\n fCurrentContentSpecType : " + fCurrentContentSpecType +
                   "\n++++++++++++++++++++++++++++++++++++++++++++++++" );
/****/
        //}

        // if enclosing element's Schema is different, need to switch "context"
        if ( fGrammarNameSpaceIndex != fGrammarNameSpaceIndexStack[fElementDepth] ) {
            fGrammarNameSpaceIndex = fGrammarNameSpaceIndexStack[fElementDepth];
            if ( fValidating && fGrammarIsSchemaGrammar )
                if ( !switchGrammar(fGrammarNameSpaceIndex) ) {
                    reportRecoverableXMLError(XMLMessages.MSG_GENERIC_SCHEMA_ERROR, XMLMessages.SCHEMA_GENERIC_ERROR, 
                                              "Grammar with uri : " + fStringPool.toString(fGrammarNameSpaceIndex) 
                                              + " , can not found");
                }
        }

        if (fValidating) {
            fBufferDatatype = false;
        }
        fInElementContent = (fCurrentContentSpecType == XMLElementDecl.TYPE_CHILDREN);

    } // callEndElement(int)

    /** Call start CDATA section. */
    public void callStartCDATA() throws Exception {
        fDocumentHandler.startCDATA();
    }

    /** Call end CDATA section. */
    public void callEndCDATA() throws Exception {
        fDocumentHandler.endCDATA();
    }

    /** Call characters. */
    public void callCharacters(int ch) throws Exception {

        if (fCharRefData == null) {
            fCharRefData = new char[2];
        }
        int count = (ch < 0x10000) ? 1 : 2;
        if (count == 1) {
            fCharRefData[0] = (char)ch;
        } else {
            fCharRefData[0] = (char)(((ch-0x00010000)>>10)+0xd800);
            fCharRefData[1] = (char)(((ch-0x00010000)&0x3ff)+0xdc00);
        }
        if (fValidating && (fInElementContent || fCurrentContentSpecType == XMLElementDecl.TYPE_EMPTY)) {
            charDataInContent();
        }
        if (fSendCharDataAsCharArray) {
            fDocumentHandler.characters(fCharRefData, 0, count);
        } else {
            int index = fStringPool.addString(new String(fCharRefData, 0, count));
            fDocumentHandler.characters(index);
        }

    } // callCharacters(int)

    /** Call processing instruction. */
    public void callProcessingInstruction(int target, int data) throws Exception {
        fDocumentHandler.processingInstruction(target, data);
    }

    /** Call comment. */
    public void callComment(int comment) throws Exception {
        fDocumentHandler.comment(comment);
    }

    //
    // NamespacesScope.NamespacesHandler methods
    //

    /** Start a new namespace declaration scope. */
    public void startNamespaceDeclScope(int prefix, int uri) throws Exception {
        fDocumentHandler.startNamespaceDeclScope(prefix, uri);
    }

    /** End a namespace declaration scope. */
    public void endNamespaceDeclScope(int prefix) throws Exception {
        fDocumentHandler.endNamespaceDeclScope(prefix);
    }

    // attributes


    // other

    /** Sets the root element. */
    public void setRootElementType(QName rootElement) {
        fRootElement.setValues(rootElement);
    }

    /** 
     * Returns true if the element declaration is external. 
     * <p>
     * <strong>Note:</strong> This method is primarilly useful for
     * DTDs with internal and external subsets.
     */
    private boolean getElementDeclIsExternal(int elementIndex) {
        /*if (elementIndex < 0 || elementIndex >= fElementCount) {
            return false;
        }
        int chunk = elementIndex >> CHUNK_SHIFT;
        int index = elementIndex & CHUNK_MASK;
        return (fElementDeclIsExternal[chunk][index] != 0);
        */

        if (fGrammarIsDTDGrammar ) {
            return((DTDGrammar) fGrammar).getElementDeclIsExternal(elementIndex);
        }
        return false;
    }

    /** Returns the content spec type for an element index. */
    public int getContentSpecType(int elementIndex) {

        int contentSpecType = -1;
        if ( elementIndex > -1) {
            if ( fGrammar.getElementDecl(elementIndex,fTempElementDecl) ) {
                contentSpecType = fTempElementDecl.type;
            }
        }
        return contentSpecType;
    }

    /** Returns the content spec handle for an element index. */
    public int getContentSpecHandle(int elementIndex) {
        int contentSpecHandle = -1;
        if ( elementIndex > -1) {
            if ( fGrammar.getElementDecl(elementIndex,fTempElementDecl) ) {
                contentSpecHandle = fTempElementDecl.contentSpecIndex;
            }
        }
        return contentSpecHandle;
    }

    //
    // Protected methods
    //

    // error reporting

    /** Report a recoverable xml error. */
    protected void reportRecoverableXMLError(int majorCode, int minorCode) 
    throws Exception {

        fErrorReporter.reportError(fErrorReporter.getLocator(),
                                   XMLMessages.XML_DOMAIN,
                                   majorCode,
                                   minorCode,
                                   null,
                                   XMLErrorReporter.ERRORTYPE_RECOVERABLE_ERROR);

    } // reportRecoverableXMLError(int,int)

    /** Report a recoverable xml error. */
    protected void reportRecoverableXMLError(int majorCode, int minorCode, 
                                             int stringIndex1) 
    throws Exception {

        Object[] args = { fStringPool.toString(stringIndex1)};
        fErrorReporter.reportError(fErrorReporter.getLocator(),
                                   XMLMessages.XML_DOMAIN,
                                   majorCode,
                                   minorCode,
                                   args,
                                   XMLErrorReporter.ERRORTYPE_RECOVERABLE_ERROR);

    } // reportRecoverableXMLError(int,int,int)

    /** Report a recoverable xml error. */
    protected void reportRecoverableXMLError(int majorCode, int minorCode, 
                                             String string1) throws Exception {

        Object[] args = { string1};
        fErrorReporter.reportError(fErrorReporter.getLocator(),
                                   XMLMessages.XML_DOMAIN,
                                   majorCode,
                                   minorCode,
                                   args,
                                   XMLErrorReporter.ERRORTYPE_RECOVERABLE_ERROR);

    } // reportRecoverableXMLError(int,int,String)

    /** Report a recoverable xml error. */
    protected void reportRecoverableXMLError(int majorCode, int minorCode, 
                                             int stringIndex1, int stringIndex2) 
    throws Exception {

        Object[] args = { fStringPool.toString(stringIndex1), fStringPool.toString(stringIndex2)};
        fErrorReporter.reportError(fErrorReporter.getLocator(),
                                   XMLMessages.XML_DOMAIN,
                                   majorCode,
                                   minorCode,
                                   args,
                                   XMLErrorReporter.ERRORTYPE_RECOVERABLE_ERROR);

    } // reportRecoverableXMLError(int,int,int,int)

    /** Report a recoverable xml error. */
    protected void reportRecoverableXMLError(int majorCode, int minorCode, 
                                             String string1, String string2) 
    throws Exception {

        Object[] args = { string1, string2};
        fErrorReporter.reportError(fErrorReporter.getLocator(),
                                   XMLMessages.XML_DOMAIN,
                                   majorCode,
                                   minorCode,
                                   args,
                                   XMLErrorReporter.ERRORTYPE_RECOVERABLE_ERROR);

    } // reportRecoverableXMLError(int,int,String,String)

    /** Report a recoverable xml error. */
    protected void reportRecoverableXMLError(int majorCode, int minorCode, 
                                             String string1, String string2, 
                                             String string3) throws Exception {

        Object[] args = { string1, string2, string3};
        fErrorReporter.reportError(fErrorReporter.getLocator(),
                                   XMLMessages.XML_DOMAIN,
                                   majorCode,
                                   minorCode,
                                   args,
                                   XMLErrorReporter.ERRORTYPE_RECOVERABLE_ERROR);

    } // reportRecoverableXMLError(int,int,String,String,String)

    // content spec

    /**
     * Returns information about which elements can be placed at a particular point
     * in the passed element's content model.
     * <p>
     * Note that the incoming content model to test must be valid at least up to
     * the insertion point. If not, then -1 will be returned and the info object
     * will not have been filled in.
     * <p>
     * If, on return, the info.isValidEOC flag is set, then the 'insert after'
     * elemement is a valid end of content, i.e. nothing needs to be inserted
     * after it to make the parent element's content model valid.
     *
     * @param elementIndex The index within the <code>ElementDeclPool</code> of the
     *                     element which is being querying.
     * @param fullyValid Only return elements that can be inserted and still
     *                   maintain the validity of subsequent elements past the
     *                   insertion point (if any).  If the insertion point is at
     *                   the end, and this is true, then only elements that can
     *                   be legal final states will be returned.
     * @param info An object that contains the required input data for the method,
     *             and which will contain the output information if successful.
     *
     * @return The value -1 if fully valid, else the 0 based index of the child
     *         that first failed before the insertion point. If the value
     *         returned is equal to the number of children, then the specified
     *         children are valid but additional content is required to reach a
     *         valid ending state.
     *
     * @exception Exception Thrown on error.
     *
     * @see InsertableElementsInfo
     */
    protected int whatCanGoHere(int elementIndex, boolean fullyValid,
                                InsertableElementsInfo info) throws Exception {

        //
        //  Do some basic sanity checking on the info packet. First, make sure
        //  that insertAt is not greater than the child count. It can be equal,
        //  which means to get appendable elements, but not greater. Or, if
        //  the current children array is null, that's bad too.
        //
        //  Since the current children array must have a blank spot for where
        //  the insert is going to be, the child count must always be at least
        //  one.
        //
        //  Make sure that the child count is not larger than the current children
        //  array. It can be equal, which means get appendable elements, but not
        //  greater.
        //
        if (info.insertAt > info.childCount || info.curChildren == null ||  
            info.childCount < 1 || info.childCount > info.curChildren.length) {
            fErrorReporter.reportError(fErrorReporter.getLocator(),
                                       ImplementationMessages.XERCES_IMPLEMENTATION_DOMAIN,
                                       ImplementationMessages.VAL_WCGHI,
                                       0,
                                       null,
                                       XMLErrorReporter.ERRORTYPE_FATAL_ERROR);
        }

        int retVal = 0;
        try {
            // Get the content model for this element
            final XMLContentModel cmElem = getElementContentModel(elementIndex);

            // And delegate this call to it
            retVal = cmElem.whatCanGoHere(fullyValid, info);
        } catch (CMException excToCatch) {
            // REVISIT - Translate caught error to the protected error handler interface
            int majorCode = excToCatch.getErrorCode();
            fErrorReporter.reportError(fErrorReporter.getLocator(),
                                       ImplementationMessages.XERCES_IMPLEMENTATION_DOMAIN,
                                       majorCode,
                                       0,
                                       null,
                                       XMLErrorReporter.ERRORTYPE_FATAL_ERROR);
            throw excToCatch;
        }
        return retVal;

    } // whatCanGoHere(int,boolean,InsertableElementsInfo):int

    // attribute information

    /** Protected for use by AttributeValidator classes. */
    protected boolean getAttDefIsExternal(QName element, QName attribute) {
        int attDefIndex = getAttDef(element, attribute);
        if (fGrammarIsDTDGrammar ) {
            return((DTDGrammar) fGrammar).getAttributeDeclIsExternal(attDefIndex);
        }
        return false;
    }



    //
    // Private methods
    //

    // other

    /** Returns true if using a standalone reader. */
    private boolean usingStandaloneReader() {
        return fStandaloneReader == -1 || fEntityHandler.getReaderId() == fStandaloneReader;
    }

    /** Returns a locator implementation. */
    private LocatorImpl getLocatorImpl(LocatorImpl fillin) {

        Locator here = fErrorReporter.getLocator();
        if (fillin == null)
            return new LocatorImpl(here);
        fillin.setPublicId(here.getPublicId());
        fillin.setSystemId(here.getSystemId());
        fillin.setLineNumber(here.getLineNumber());
        fillin.setColumnNumber(here.getColumnNumber());
        return fillin;

    } // getLocatorImpl(LocatorImpl):LocatorImpl


    // initialization

    /** Reset pool. */
    private void poolReset() {
        try {
            //System.out.println("We reset" );
            this.fValID.validate( null, this.fResetID );
            this.fValIDRef.validate(null, this.fResetIDRef );
            this.fValIDRefs.validate(null, this.fResetIDRef );
        } catch ( InvalidDatatypeValueException ex ) {
            System.err.println("Error re-Initializing: ID,IDRef,IDRefs pools" );
        }
    } // poolReset()

    /** Reset common. */
    private void resetCommon(StringPool stringPool) throws Exception {

        fStringPool = stringPool;
        fValidating = fValidationEnabled;
        fValidationEnabledByDynamic = false;
        fDynamicDisabledByValidation = false;
        poolReset();
        fCalledStartDocument = false;
        fStandaloneReader = -1;
        fElementChildrenLength = 0;
        fElementDepth = -1;
        fSeenRootElement = false;
        fSeenDoctypeDecl = false;
        fNamespacesScope = null;
        fNamespacesPrefix = -1;
        fRootElement.clear();
        fAttrListHandle = -1;
        fCheckedForSchema = false;

        fCurrentScope = TOP_LEVEL_SCOPE;
        fCurrentSchemaURI = -1;
        fEmptyURI = - 1; 
        fXsiPrefix = - 1;
        fXsiTypeValidator = null;

        fGrammar = null;
        fGrammarNameSpaceIndex = -1;
        //fGrammarResolver = null;
        if (fGrammarResolver != null) {
            fGrammarResolver.clearGrammarResolver();
        }
        fGrammarIsDTDGrammar = false;
        fGrammarIsSchemaGrammar = false;


        init();

    } // resetCommon(StringPool)

    /** Initialize. */
    private void init() {

        fEmptyURI = fStringPool.addSymbol("");
        fXsiURI = fStringPool.addSymbol(SchemaSymbols.URI_XSI);


        fEMPTYSymbol = fStringPool.addSymbol("EMPTY");
        fANYSymbol = fStringPool.addSymbol("ANY");
        fMIXEDSymbol = fStringPool.addSymbol("MIXED");
        fCHILDRENSymbol = fStringPool.addSymbol("CHILDREN");

        fCDATASymbol = fStringPool.addSymbol("CDATA");
        fIDSymbol = fStringPool.addSymbol("ID");
        fIDREFSymbol = fStringPool.addSymbol("IDREF");
        fIDREFSSymbol = fStringPool.addSymbol("IDREFS");
        fENTITYSymbol = fStringPool.addSymbol("ENTITY");
        fENTITIESSymbol = fStringPool.addSymbol("ENTITIES");
        fNMTOKENSymbol = fStringPool.addSymbol("NMTOKEN");
        fNMTOKENSSymbol = fStringPool.addSymbol("NMTOKENS");
        fNOTATIONSymbol = fStringPool.addSymbol("NOTATION");
        fENUMERATIONSymbol = fStringPool.addSymbol("ENUMERATION");
        fREQUIREDSymbol = fStringPool.addSymbol("#REQUIRED");
        fFIXEDSymbol = fStringPool.addSymbol("#FIXED");
        fDATATYPESymbol = fStringPool.addSymbol("<<datatype>>");
        fEpsilonIndex = fStringPool.addSymbol("<<CMNODE_EPSILON>>");
        fXMLLang = fStringPool.addSymbol("xml:lang");

        try {//Initialize ENTITIES and ENTITY Validators
            Object[] packageArgsEntityVal = { (Object) this.fEntityHandler,
                (Object) this.fStringPool};
            fValidateENTITYMsg.setDatatypeObject( (Object ) packageArgsEntityVal);
            fValENTITIES.validate( null, fValidateENTITYMsg );
            fValENTITY.validate( null, fValidateENTITYMsg );
        } catch ( InvalidDatatypeValueException ex ) {
            System.err.println("Error: " + ex.getLocalizedMessage() );//Should not happen
        }


    } // init()

    // other

    // default attribute

    /** addDefaultAttributes. */
    private int addDefaultAttributes(int elementIndex, XMLAttrList attrList, int attrIndex, boolean validationEnabled, boolean standalone) throws Exception {

        //System.out.println("XMLValidator#addDefaultAttributes");
        //System.out.print("  ");
        //fGrammar.printAttributes(elementIndex);

        //
        // Check after all specified attrs are scanned
        // (1) report error for REQUIRED attrs that are missing (V_TAGc)
        // (2) check that FIXED attrs have matching value (V_TAGd)
        // (3) add default attrs (FIXED and NOT_FIXED)
        //
        fGrammar.getElementDecl(elementIndex,fTempElementDecl);

        int elementNameIndex = fTempElementDecl.name.localpart;
        int attlistIndex = fGrammar.getFirstAttributeDeclIndex(elementIndex);
        int firstCheck = attrIndex;
        int lastCheck = -1;
        while (attlistIndex != -1) {
            fGrammar.getAttributeDecl(attlistIndex, fTempAttDecl);


            int attPrefix = fTempAttDecl.name.prefix;
            int attName = fTempAttDecl.name.localpart;
            int attType = attributeTypeName(fTempAttDecl);
            int attDefType =fTempAttDecl.defaultType;
            int attValue = -1 ;
            if (fTempAttDecl.defaultValue != null ) {
                attValue = fStringPool.addSymbol(fTempAttDecl.defaultValue);
            }

            boolean specified = false;
            boolean required = attDefType == XMLAttributeDecl.DEFAULT_TYPE_REQUIRED;

            if (firstCheck != -1) {
                boolean cdata = attType == fCDATASymbol;
                if (!cdata || required || attValue != -1) {
                    int i = attrList.getFirstAttr(firstCheck);
                    while (i != -1 && (lastCheck == -1 || i <= lastCheck)) {

                        if ( (fGrammarIsDTDGrammar && (attrList.getAttrName(i) == fTempAttDecl.name.rawname)) ||
                             (  fStringPool.equalNames(attrList.getAttrLocalpart(i), attName)
                                && fStringPool.equalNames(attrList.getAttrURI(i), fTempAttDecl.name.uri) ) ) {

                            if (validationEnabled && attDefType == XMLAttributeDecl.DEFAULT_TYPE_FIXED) {
                                int alistValue = attrList.getAttValue(i);
                                if (alistValue != attValue &&
                                    !fStringPool.toString(alistValue).equals(fStringPool.toString(attValue))) {
                                    Object[] args = { fStringPool.toString(elementNameIndex),
                                        fStringPool.toString(attName),
                                        fStringPool.toString(alistValue),
                                        fStringPool.toString(attValue)};
                                    fErrorReporter.reportError(fErrorReporter.getLocator(),
                                                               XMLMessages.XML_DOMAIN,
                                                               XMLMessages.MSG_FIXED_ATTVALUE_INVALID,
                                                               XMLMessages.VC_FIXED_ATTRIBUTE_DEFAULT,
                                                               args,
                                                               XMLErrorReporter.ERRORTYPE_RECOVERABLE_ERROR);
                                }
                            }
                            specified = true;
                            break;
                        }
                        i = attrList.getNextAttr(i);
                    }
                }
            }

            if (!specified) {
                if (required) {
                    if (validationEnabled) {
                        Object[] args = { fStringPool.toString(elementNameIndex),
                            fStringPool.toString(attName)};
                        fErrorReporter.reportError(fErrorReporter.getLocator(),
                                                   XMLMessages.XML_DOMAIN,
                                                   XMLMessages.MSG_REQUIRED_ATTRIBUTE_NOT_SPECIFIED,
                                                   XMLMessages.VC_REQUIRED_ATTRIBUTE,
                                                   args,
                                                   XMLErrorReporter.ERRORTYPE_RECOVERABLE_ERROR);
                    }
                } else if (attValue != -1) {
                    if (validationEnabled && standalone )
                        if ( fGrammarIsDTDGrammar 
                             && ((DTDGrammar) fGrammar).getAttributeDeclIsExternal(attlistIndex) ) {

                            Object[] args = { fStringPool.toString(elementNameIndex),
                                fStringPool.toString(attName)};
                            fErrorReporter.reportError(fErrorReporter.getLocator(),
                                                       XMLMessages.XML_DOMAIN,
                                                       XMLMessages.MSG_DEFAULTED_ATTRIBUTE_NOT_SPECIFIED,
                                                       XMLMessages.VC_STANDALONE_DOCUMENT_DECLARATION,
                                                       args,
                                                       XMLErrorReporter.ERRORTYPE_RECOVERABLE_ERROR);
                        }
                    if (attType == fIDREFSymbol) {
                        this.fValIDRef.validate( fStringPool.toString(attValue), this.fStoreIDRef );
                    } else if (attType == fIDREFSSymbol) {
                        this.fValIDRefs.validate( fStringPool.toString(attValue), this.fStoreIDRef );
                    }
                    if (attrIndex == -1) {
                        attrIndex = attrList.startAttrList();
                    }
                    // REVISIT: Validation. What should the prefix be?
                    fTempQName.setValues(attPrefix, attName, attName, fTempAttDecl.name.uri);
                    int newAttr = attrList.addAttr(fTempQName, 
                                                   attValue, attType, 
                                                   false, false);
                    if (lastCheck == -1) {
                        lastCheck = newAttr;
                    }
                }
            }
            attlistIndex = fGrammar.getNextAttributeDeclIndex(attlistIndex);
        }
        return attrIndex;

    } // addDefaultAttributes(int,XMLAttrList,int,boolean,boolean):int

    /** addDTDDefaultAttributes. */
    private int addDTDDefaultAttributes(QName element, XMLAttrList attrList, int attrIndex, boolean validationEnabled, boolean standalone) throws Exception {


        //
        // Check after all specified attrs are scanned
        // (1) report error for REQUIRED attrs that are missing (V_TAGc)
        // (2) check that FIXED attrs have matching value (V_TAGd)
        // (3) add default attrs (FIXED and NOT_FIXED)
        //

        int elementIndex = fGrammar.getElementDeclIndex(element, -1);

        if (elementIndex == -1) {
            return attrIndex;
        }

        fGrammar.getElementDecl(elementIndex,fTempElementDecl);


        int elementNameIndex = fTempElementDecl.name.rawname;
        int attlistIndex = fGrammar.getFirstAttributeDeclIndex(elementIndex);
        int firstCheck = attrIndex;
        int lastCheck = -1;
        while (attlistIndex != -1) {

            fGrammar.getAttributeDecl(attlistIndex, fTempAttDecl);

            // TO DO: For ericye Debug only
            /***
            if (fTempAttDecl != null) {
                XMLElementDecl element = new XMLElementDecl();
                fGrammar.getElementDecl(elementIndex, element);
                System.out.println("element: "+fStringPool.toString(element.name.localpart));
                System.out.println("attlistIndex " + attlistIndex + "\n"+
                    "attName : '"+fStringPool.toString(fTempAttDecl.name.localpart) + "'\n"
                                   + "attType : "+fTempAttDecl.type + "\n"
                                   + "attDefaultType : "+fTempAttDecl.defaultType + "\n"
                                   + "attDefaultValue : '"+fTempAttDecl.defaultValue + "'\n"
                                   + attrList.getLength() +"\n"
                                   );
            }
            /***/

            int attPrefix = fTempAttDecl.name.prefix;
            int attName = fTempAttDecl.name.rawname;
            int attLocalpart = fTempAttDecl.name.localpart;
            int attType = attributeTypeName(fTempAttDecl);
            int attDefType =fTempAttDecl.defaultType;
            int attValue = -1 ;
            if (fTempAttDecl.defaultValue != null ) {
                attValue = fStringPool.addSymbol(fTempAttDecl.defaultValue);
            }
            boolean specified = false;
            boolean required = attDefType == XMLAttributeDecl.DEFAULT_TYPE_REQUIRED;


            /****
            if (fValidating && fGrammar != null && fGrammarIsDTDGrammar && attValue != -1) {
                normalizeAttValue(null, fTempAttDecl.name,
                                  attValue,attType,fTempAttDecl.list, 
                                  fTempAttDecl.enumeration);
            }
            /****/

            if (firstCheck != -1) {
                boolean cdata = attType == fCDATASymbol;
                if (!cdata || required || attValue != -1) {
                    int i = attrList.getFirstAttr(firstCheck);
                    while (i != -1 && (lastCheck == -1 || i <= lastCheck)) {

                        if ( attrList.getAttrName(i) == fTempAttDecl.name.rawname ) {

                            if (validationEnabled && attDefType == XMLAttributeDecl.DEFAULT_TYPE_FIXED) {
                                int alistValue = attrList.getAttValue(i);
                                if (alistValue != attValue &&
                                    !fStringPool.toString(alistValue).equals(fStringPool.toString(attValue))) {
                                    Object[] args = { fStringPool.toString(elementNameIndex),
                                        fStringPool.toString(attName),
                                        fStringPool.toString(alistValue),
                                        fStringPool.toString(attValue)};
                                    fErrorReporter.reportError(fErrorReporter.getLocator(),
                                                               XMLMessages.XML_DOMAIN,
                                                               XMLMessages.MSG_FIXED_ATTVALUE_INVALID,
                                                               XMLMessages.VC_FIXED_ATTRIBUTE_DEFAULT,
                                                               args,
                                                               XMLErrorReporter.ERRORTYPE_RECOVERABLE_ERROR);
                                }
                            }
                            specified = true;
                            break;
                        }
                        i = attrList.getNextAttr(i);
                    }
                }
            }

            if (!specified) {
                if (required) {
                    if (validationEnabled) {
                        Object[] args = { fStringPool.toString(elementNameIndex),
                            fStringPool.toString(attName)};
                        fErrorReporter.reportError(fErrorReporter.getLocator(),
                                                   XMLMessages.XML_DOMAIN,
                                                   XMLMessages.MSG_REQUIRED_ATTRIBUTE_NOT_SPECIFIED,
                                                   XMLMessages.VC_REQUIRED_ATTRIBUTE,
                                                   args,
                                                   XMLErrorReporter.ERRORTYPE_RECOVERABLE_ERROR);
                    }
                } else if (attValue != -1) {
                    if (validationEnabled && standalone )
                        if ( fGrammarIsDTDGrammar 
                             && ((DTDGrammar) fGrammar).getAttributeDeclIsExternal(attlistIndex) ) {

                            Object[] args = { fStringPool.toString(elementNameIndex),
                                fStringPool.toString(attName)};
                            fErrorReporter.reportError(fErrorReporter.getLocator(),
                                                       XMLMessages.XML_DOMAIN,
                                                       XMLMessages.MSG_DEFAULTED_ATTRIBUTE_NOT_SPECIFIED,
                                                       XMLMessages.VC_STANDALONE_DOCUMENT_DECLARATION,
                                                       args,
                                                       XMLErrorReporter.ERRORTYPE_RECOVERABLE_ERROR);
                        }
                    if (attType == fIDREFSymbol) {
                        this.fValIDRef.validate( fStringPool.toString(attValue), this.fStoreIDRef );
                    } else if (attType == fIDREFSSymbol) {
                        this.fValIDRefs.validate( fStringPool.toString(attValue), this.fStoreIDRef );
                    }
                    if (attrIndex == -1) {
                        attrIndex = attrList.startAttrList();
                    }

                    fTempQName.setValues(attPrefix, attLocalpart, attName, fTempAttDecl.name.uri);
                    int newAttr = attrList.addAttr(fTempQName, 
                                                   attValue, attType, 
                                                   false, false);
                    if (lastCheck == -1) {
                        lastCheck = newAttr;
                    }
                }
            }
            attlistIndex = fGrammar.getNextAttributeDeclIndex(attlistIndex);
        }
        return attrIndex;

    } // addDTDDefaultAttributes(int,XMLAttrList,int,boolean,boolean):int

    // content models

    /** Queries the content model for the specified element index. */
    private XMLContentModel getElementContentModel(int elementIndex) throws CMException {
        XMLContentModel contentModel = null;
        if ( elementIndex > -1) {
            if ( fGrammar.getElementDecl(elementIndex,fTempElementDecl) ) {
                contentModel = fGrammar.getElementContentModel(elementIndex);
            }
        }
        //return fGrammar.getElementContentModel(elementIndex);
        return contentModel;
    }



    // query attribute information

    /** Returns an attribute definition for an element type. */
    // this is only used by DTD validation.
    private int getAttDef(QName element, QName attribute) {
        if (fGrammar != null) {
            int scope = fCurrentScope;
            if (element.uri > -1) {
                scope = TOP_LEVEL_SCOPE;
            }
            int elementIndex = fGrammar.getElementDeclIndex(element,scope);
            if (elementIndex == -1) {
                return -1;
            }
            int attDefIndex = fGrammar.getFirstAttributeDeclIndex(elementIndex);
            while (attDefIndex != -1) {
                fGrammar.getAttributeDecl(attDefIndex, fTempAttributeDecl);
                if (fTempAttributeDecl.name.localpart == attribute.localpart &&
                    fTempAttributeDecl.name.uri == attribute.uri ) {
                    return attDefIndex;
                }
                attDefIndex = fGrammar.getNextAttributeDeclIndex(attDefIndex);
            }
        }
        return -1;

    } // getAttDef(QName,QName)

    /** Returns an attribute definition for an element type. */
    private int getAttDefByElementIndex(int elementIndex, QName attribute) {
        if (fGrammar != null && elementIndex > -1) {
            if (elementIndex == -1) {
                return -1;
            }
            int attDefIndex = fGrammar.getFirstAttributeDeclIndex(elementIndex);
            while (attDefIndex != -1) {
                fGrammar.getAttributeDecl(attDefIndex, fTempAttDecl);

                if (fGrammarIsDTDGrammar) {
                    if (fTempAttDecl.name.rawname == attribute.rawname )
                        return attDefIndex;
                } else
                    if (fTempAttDecl.name.localpart == attribute.localpart &&
                        fTempAttDecl.name.uri == attribute.uri ) {
                    return attDefIndex;
                }

                if (fGrammarIsSchemaGrammar) {
                    if (fTempAttDecl.type == XMLAttributeDecl.TYPE_ANY_ANY) {
                        return attDefIndex;
                    } else if (fTempAttDecl.type == XMLAttributeDecl.TYPE_ANY_LOCAL) {
                        if (attribute.uri == -1) {
                            return attDefIndex;
                        }
                    } else if (fTempAttDecl.type == XMLAttributeDecl.TYPE_ANY_OTHER) {
                        if (attribute.uri != fTempAttDecl.name.uri) {
                            return attDefIndex;
                        }
                    } else if (fTempAttDecl.type == XMLAttributeDecl.TYPE_ANY_LIST) {
                        if (fStringPool.stringInList(fTempAttDecl.enumeration, attribute.uri)) {
                            return attDefIndex;
                        }
                    }
                }

                attDefIndex = fGrammar.getNextAttributeDeclIndex(attDefIndex);
            }
        }
        return -1;

    } // getAttDef(QName,QName)

    // validation

    /** Root element specified. */
    private void rootElementSpecified(QName rootElement) throws Exception {

        // this is what it used to be
        //if  (fDynamicValidation && !fSeenDoctypeDecl) {
        //fValidating = false;
        //}


        if ( fLoadDTDGrammar )
            // initialize the grammar to be the default one, 
            // it definitely should be a DTD Grammar at this case;
            if (fGrammar == null) {

                fGrammar = fGrammarResolver.getGrammar("");

                //TO DO, for ericye debug only
                if (fGrammar == null && DEBUG_SCHEMA_VALIDATION) {
                    System.out.println("Oops! no grammar is found for validation");
                }

                if (fDynamicValidation && fGrammar==null) {
                    fValidating = false;
                }

                if (fGrammar != null) {
                    if (fGrammar instanceof DTDGrammar) {
                        fGrammarIsDTDGrammar = true;
                        fGrammarIsSchemaGrammar = false;
                    } else if ( fGrammar instanceof SchemaGrammar ) {
                        fGrammarIsSchemaGrammar = true;
                        fGrammarIsDTDGrammar = false;
                    }

                    fGrammarNameSpaceIndex = fEmptyURI;
                }
            }

        if (fValidating) {
            if ( fGrammarIsDTDGrammar && 
                 ((DTDGrammar) fGrammar).getRootElementQName(fRootElement) ) {

                String root1 = fStringPool.toString(fRootElement.rawname);
                String root2 = fStringPool.toString(rootElement.rawname);
                if (!root1.equals(root2)) {
                    reportRecoverableXMLError(XMLMessages.MSG_ROOT_ELEMENT_TYPE,
                                              XMLMessages.VC_ROOT_ELEMENT_TYPE,
                                              fRootElement.rawname, 
                                              rootElement.rawname);
                }
            }
        }

        if (fNamespacesEnabled) {
            if (fNamespacesScope == null) {
                fNamespacesScope = new NamespacesScope(this);
                fNamespacesPrefix = fStringPool.addSymbol("xmlns");
                fNamespacesScope.setNamespaceForPrefix(fNamespacesPrefix, -1);
                int xmlSymbol = fStringPool.addSymbol("xml");
                int xmlNamespace = fStringPool.addSymbol("http://www.w3.org/XML/1998/namespace");
                fNamespacesScope.setNamespaceForPrefix(xmlSymbol, xmlNamespace);
            }
        }

    } // rootElementSpecified(QName)

    /** Switchs to correct validating symbol tables when Schema changes.*/

    private boolean switchGrammar(int newGrammarNameSpaceIndex) throws Exception {
        Grammar tempGrammar = fGrammarResolver.getGrammar(fStringPool.toString(newGrammarNameSpaceIndex));
        if (tempGrammar == null) {
            // This is a case where namespaces is on with a DTD grammar.
            tempGrammar = fGrammarResolver.getGrammar("");
        }
        if (tempGrammar == null) {
            return false;
        } else {
            fGrammar = tempGrammar;
            if (fGrammar instanceof DTDGrammar) {
                fGrammarIsDTDGrammar = true;
                fGrammarIsSchemaGrammar = false;
            } else if ( fGrammar instanceof SchemaGrammar ) {
                fGrammarIsSchemaGrammar = true;
                fGrammarIsDTDGrammar = false;
            }

            return true;
        }
    }

    /** Binds namespaces to the element and attributes. */
    private void bindNamespacesToElementAndAttributes(QName element, 
                                                      XMLAttrList attrList)
    throws Exception {

        fNamespacesScope.increaseDepth();

        //Vector schemaCandidateURIs = null;
        Hashtable locationUriPairs = null;

        if (fAttrListHandle != -1) {
            int index = attrList.getFirstAttr(fAttrListHandle);
            while (index != -1) {
                int attName = attrList.getAttrName(index);
                int attPrefix = attrList.getAttrPrefix(index);
                if (fStringPool.equalNames(attName, fXMLLang)) {
                    /***
                    // NOTE: This check is done in the validateElementsAndAttributes
                    //       method.
                    fDocumentScanner.checkXMLLangAttributeValue(attrList.getAttValue(index));
                    /***/
                } else if (fStringPool.equalNames(attName, fNamespacesPrefix)) {
                    int uri = fStringPool.addSymbol(attrList.getAttValue(index));
                    fNamespacesScope.setNamespaceForPrefix(StringPool.EMPTY_STRING, uri);
                } else {
                    if (attPrefix == fNamespacesPrefix) {
                        int nsPrefix = attrList.getAttrLocalpart(index);
                        int uri = fStringPool.addSymbol(attrList.getAttValue(index));
                        fNamespacesScope.setNamespaceForPrefix(nsPrefix, uri);

                        if (fValidating && fSchemaValidation) {
                            boolean seeXsi = false;
                            String attrValue = fStringPool.toString(attrList.getAttValue(index));

                            if (attrValue.equals(SchemaSymbols.URI_XSI)) {
                                fXsiPrefix = nsPrefix;
                                seeXsi = true;
                            }

                            if (!seeXsi) {
                                /***
                                if (schemaCandidateURIs == null) {
                                    schemaCandidateURIs = new Vector();
                                }
                                schemaCandidateURIs.addElement( fStringPool.toString(uri) );
                                /***/
                            }
                        }
                    }
                }
                index = attrList.getNextAttr(index);
            }
            // if validating, walk through the list again to deal with "xsi:...."
            if (fValidating && fSchemaValidation) {
                fXsiTypeAttValue = -1;
                index = attrList.getFirstAttr(fAttrListHandle);
                while (index != -1) {

                    int attName = attrList.getAttrName(index);
                    int attPrefix = attrList.getAttrPrefix(index);

                    if (fStringPool.equalNames(attName, fNamespacesPrefix)) {
                        // REVISIT
                    } else {
                        if ( DEBUG_SCHEMA_VALIDATION ) {
                            System.out.println("deal with XSI");
                            System.out.println("before find XSI: "+fStringPool.toString(attPrefix)
                                               +","+fStringPool.toString(fXsiPrefix) );
                        }
                        if ( fXsiPrefix != -1 && attPrefix == fXsiPrefix ) {

                            if (DEBUG_SCHEMA_VALIDATION) {
                                System.out.println("find XSI: "+fStringPool.toString(attPrefix)
                                                   +","+fStringPool.toString(attName) );
                            }


                            int localpart = attrList.getAttrLocalpart(index);
                            if (localpart == fStringPool.addSymbol(SchemaSymbols.XSI_SCHEMALOCACTION)) {
                                if (locationUriPairs == null) {
                                    locationUriPairs = new Hashtable();
                                }
                                parseSchemaLocation(fStringPool.toString(attrList.getAttValue(index)), locationUriPairs);
                            } else if (localpart == fStringPool.addSymbol(SchemaSymbols.XSI_NONAMESPACESCHEMALOCACTION)) {
                                if (locationUriPairs == null) {
                                    locationUriPairs = new Hashtable();
                                }
                                locationUriPairs.put(fStringPool.toString(attrList.getAttValue(index)), "");
                                if (fNamespacesScope != null) {
                                    //bind prefix "" to URI "" in this case
                                    fNamespacesScope.setNamespaceForPrefix( fStringPool.addSymbol(""), 
                                                                            fStringPool.addSymbol(""));
                                }
                            } else if (localpart == fStringPool.addSymbol(SchemaSymbols.XSI_TYPE)) {
                                fXsiTypeAttValue = attrList.getAttValue(index);
                            }
                            // REVISIT: should we break here? 
                            //break;
                        }
                    }
                    index = attrList.getNextAttr(index);
                }

                // try to resolve all the grammars here
                if (locationUriPairs != null) {
                    Enumeration locations = locationUriPairs.keys();

                    while (locations.hasMoreElements()) {
                        String loc = (String) locations.nextElement();
                        String uri = (String) locationUriPairs.get(loc);
                        resolveSchemaGrammar( loc, uri);
                        //schemaCandidateURIs.removeElement(uri);
                    }
                }

                //TO DO: This should be a feature that can be turned on or off
                /*****
                for (int i=0; i< schemaCandidateURIs.size(); i++) {
                
                    String uri = (String) schemaCandidateURIs.elementAt(i);
                    resolveSchemaGrammar(uri);
                }
                /*****/

            }

        }

        // bind element to URI
        int prefix = element.prefix != -1 ? element.prefix : 0;
        int uri    = fNamespacesScope.getNamespaceForPrefix(prefix);
        if (element.prefix != -1 || uri != -1) {
            element.uri = uri;
            if (element.uri == -1) {
                Object[] args = { fStringPool.toString(element.prefix)};
                fErrorReporter.reportError(fErrorReporter.getLocator(),
                                           XMLMessages.XMLNS_DOMAIN,
                                           XMLMessages.MSG_PREFIX_DECLARED,
                                           XMLMessages.NC_PREFIX_DECLARED,
                                           args,
                                           XMLErrorReporter.ERRORTYPE_RECOVERABLE_ERROR);
            }
        }


        if (fAttrListHandle != -1) {
            int index = attrList.getFirstAttr(fAttrListHandle);
            while (index != -1) {
                int attName = attrList.getAttrName(index);
                if (!fStringPool.equalNames(attName, fNamespacesPrefix)) {
                    int attPrefix = attrList.getAttrPrefix(index);
                    if (attPrefix != fNamespacesPrefix) {
                        if (attPrefix != -1 ) {
                            int attrUri = fNamespacesScope.getNamespaceForPrefix(attPrefix);
                            if (attrUri == -1) {
                                Object[] args = { fStringPool.toString(attPrefix)};
                                fErrorReporter.reportError(fErrorReporter.getLocator(),
                                                           XMLMessages.XMLNS_DOMAIN,
                                                           XMLMessages.MSG_PREFIX_DECLARED,
                                                           XMLMessages.NC_PREFIX_DECLARED,
                                                           args,
                                                           XMLErrorReporter.ERRORTYPE_RECOVERABLE_ERROR);
                            }
                            attrList.setAttrURI(index, attrUri);
                        }
                    }
                }
                index = attrList.getNextAttr(index);
            }
        }

    } // bindNamespacesToElementAndAttributes(QName,XMLAttrList)

    void parseSchemaLocation(String schemaLocationStr, Hashtable locationUriPairs){
        if (locationUriPairs != null) {
            StringTokenizer tokenizer = new StringTokenizer(schemaLocationStr, " \n\t\r", false);
            int tokenTotal = tokenizer.countTokens();
            if (tokenTotal % 2 != 0 ) {
                // TO DO: report warning - malformed schemaLocation string
            } else {
                while (tokenizer.hasMoreTokens()) {
                    String uri = tokenizer.nextToken();
                    String location = tokenizer.nextToken();

                    locationUriPairs.put(location, uri);
                }
            }
        } else {
            // TO DO: should report internal error here
        }

    }// parseSchemaLocaltion(String, Hashtable)
    private void resolveSchemaGrammar( String loc, String uri) throws Exception {

        SchemaGrammar grammar = (SchemaGrammar) fGrammarResolver.getGrammar(uri);

        if (grammar == null) {
            DOMParser parser = new DOMParser();
            parser.setEntityResolver( new Resolver(fEntityHandler) );
            parser.setErrorHandler(  new ErrorHandler() );

            try {
                parser.setFeature("http://xml.org/sax/features/validation", false);
                parser.setFeature("http://xml.org/sax/features/namespaces", true);
                parser.setFeature("http://apache.org/xml/features/dom/defer-node-expansion", false);
            } catch (  org.xml.sax.SAXNotRecognizedException e ) {
                e.printStackTrace();
            } catch ( org.xml.sax.SAXNotSupportedException e ) {
                e.printStackTrace();
            }

            // expand it before passing it to the parser
            InputSource source = null;
            EntityResolver currentER = parser.getEntityResolver();
            if (currentER != null) {
                source = currentER.resolveEntity("", loc);
            }
            if (source == null) {
                loc = fEntityHandler.expandSystemId(loc);
                source = new InputSource(loc);
            }
            try {
                parser.parse( source );
            } catch ( IOException e ) {
                e.printStackTrace();
            } catch ( SAXException e ) {
                //System.out.println("loc = "+loc);
                //e.printStackTrace();
                reportRecoverableXMLError( XMLMessages.MSG_GENERIC_SCHEMA_ERROR, 
                                           XMLMessages.SCHEMA_GENERIC_ERROR, e.getMessage() );
            }

            Document     document   = parser.getDocument(); //Our Grammar

            TraverseSchema tst = null;
            try {
                if (DEBUG_SCHEMA_VALIDATION) {
                    System.out.println("I am geting the Schema Document");
                }

                Element root   = document.getDocumentElement();// This is what we pass to TraverserSchema
                if (root == null) {
                    reportRecoverableXMLError(XMLMessages.MSG_GENERIC_SCHEMA_ERROR, XMLMessages.SCHEMA_GENERIC_ERROR, "Can't get back Schema document's root element :" + loc); 
                } else {
                    if (uri == null || !uri.equals(root.getAttribute(SchemaSymbols.ATT_TARGETNAMESPACE)) ) {
                        reportRecoverableXMLError(XMLMessages.MSG_GENERIC_SCHEMA_ERROR, XMLMessages.SCHEMA_GENERIC_ERROR, "Schema in " + loc + " has a different target namespace " + 
                                                  "from the one specified in the instance document :" + uri); 
                    }
                    grammar = new SchemaGrammar();
                    grammar.setGrammarDocument(document);
                    tst = new TraverseSchema( root, fStringPool, (SchemaGrammar)grammar, fGrammarResolver, fErrorReporter, source.getSystemId());
                    fGrammarResolver.putGrammar(document.getDocumentElement().getAttribute("targetNamespace"), grammar);
                }
            } catch (Exception e) {
                e.printStackTrace(System.err);
            }
        }

    }

    private void resolveSchemaGrammar(String uri) throws Exception{

        resolveSchemaGrammar(uri, uri);

    }

    static class Resolver implements EntityResolver {

        //
        // Constants
        //

        private static final String SYSTEM[] = {
            "http://www.w3.org/TR/2000/WD-xmlschema-1-20000407/structures.dtd",
            "http://www.w3.org/TR/2000/WD-xmlschema-1-20000407/datatypes.dtd",
            "http://www.w3.org/TR/2000/WD-xmlschema-1-20000407/versionInfo.ent",
        };
        private static final String PATH[] = {
            "structures.dtd",
            "datatypes.dtd",
            "versionInfo.ent",
        };

        //
        // Data
        //

        private DefaultEntityHandler fEntityHandler;

        //
        // Constructors
        //

        public Resolver(DefaultEntityHandler handler) {
            fEntityHandler = handler;
        }

        //
        // EntityResolver methods
        //

        public InputSource resolveEntity(String publicId, String systemId)
        throws IOException, SAXException {

            // looking for the schema DTDs?
            for (int i = 0; i < SYSTEM.length; i++) {
                if (systemId.equals(SYSTEM[i])) {
                    InputSource source = new InputSource(getClass().getResourceAsStream(PATH[i]));
                    source.setPublicId(publicId);
                    source.setSystemId(systemId);
                    return source;
                }
            }

            // first try to resolve using user's entity resolver
            EntityResolver resolver = fEntityHandler.getEntityResolver();
            if (resolver != null) {
                InputSource source = resolver.resolveEntity(publicId, systemId);
                if (source != null) {
                    return source;
                }
            }

            // use default resolution
            return new InputSource(fEntityHandler.expandSystemId(systemId));

        } // resolveEntity(String,String):InputSource

    } // class Resolver

    static class ErrorHandler implements org.xml.sax.ErrorHandler {

        /** Warning. */
        public void warning(SAXParseException ex) {
            System.err.println("[Warning] "+
                               getLocationString(ex)+": "+
                               ex.getMessage());
        }

        /** Error. */
        public void error(SAXParseException ex) {
            System.err.println("[Error] "+
                               getLocationString(ex)+": "+
                               ex.getMessage());
        }

        /** Fatal error. */
        public void fatalError(SAXParseException ex)  {
            System.err.println("[Fatal Error] "+
                               getLocationString(ex)+": "+
                               ex.getMessage());
            //throw ex;
        }

        //
        // Private methods
        //

        /** Returns a string of the location. */
        private String getLocationString(SAXParseException ex) {
            StringBuffer str = new StringBuffer();

            String systemId_ = ex.getSystemId();
            if (systemId_ != null) {
                int index = systemId_.lastIndexOf('/');
                if (index != -1)
                    systemId_ = systemId_.substring(index + 1);
                str.append(systemId_);
            }
            str.append(':');
            str.append(ex.getLineNumber());
            str.append(':');
            str.append(ex.getColumnNumber());

            return str.toString();

        } // getLocationString(SAXParseException):String
    }

    private int attributeTypeName(XMLAttributeDecl attrDecl) {
        switch (attrDecl.type) {
        case XMLAttributeDecl.TYPE_ENTITY: {
                return attrDecl.list ? fENTITIESSymbol : fENTITYSymbol;
            }
        case XMLAttributeDecl.TYPE_ENUMERATION: {
                String enumeration = fStringPool.stringListAsString(attrDecl.enumeration);
                return fStringPool.addString(enumeration);
            }
        case XMLAttributeDecl.TYPE_ID: {
                return fIDSymbol;
            }
        case XMLAttributeDecl.TYPE_IDREF: {
                return attrDecl.list ? fIDREFSSymbol : fIDREFSymbol;
            }
        case XMLAttributeDecl.TYPE_NMTOKEN: {
                return attrDecl.list ? fNMTOKENSSymbol : fNMTOKENSSymbol;
            }
        case XMLAttributeDecl.TYPE_NOTATION: {
                return fNOTATIONSymbol;
            }
        }
        return fCDATASymbol;
    }

    /** Validates element and attributes. */
    private void validateElementAndAttributes(QName element, 
                                              XMLAttrList attrList) 
        throws Exception {

        if ((fElementDepth >= 0 && fValidationFlagStack[fElementDepth] != 0 )|| 
            (fGrammar == null && !fValidating && !fNamespacesEnabled) ) {
            fCurrentElementIndex = -1;
            fCurrentContentSpecType = -1;
            fInElementContent = false;
            if (fAttrListHandle != -1) {
                fAttrList.endAttrList();
                int index = fAttrList.getFirstAttr(fAttrListHandle);
                while (index != -1) {
                    if (fStringPool.equalNames(fAttrList.getAttrName(index), fXMLLang)) {
                        fDocumentScanner.checkXMLLangAttributeValue(fAttrList.getAttValue(index));
                        break;
                    }
                    index = fAttrList.getNextAttr(index);
                }
            }
            return;
        }

        int elementIndex = -1;
        int contentSpecType = -1;

        boolean skipThisOne = false;
        boolean laxThisOne = false;

        if ( fGrammarIsSchemaGrammar && fContentLeafStack[fElementDepth] != null ) {
            ContentLeafNameTypeVector cv = fContentLeafStack[fElementDepth];

            QName[] fElemMap = cv.leafNames;
            for (int i=0; i<cv.leafCount; i++) {
                int type = cv.leafTypes[i]  ;
                //System.out.println("******* see a ANY_OTHER_SKIP, "+type+","+element+","+fElemMap[i]+"\n*******");

                if (type == XMLContentSpec.CONTENTSPECNODE_LEAF) {
                    if (fElemMap[i].uri==element.uri
                        && fElemMap[i].localpart == element.localpart)
                        break;
                } else if (type == XMLContentSpec.CONTENTSPECNODE_ANY) {
                    int uri = fElemMap[i].uri;
                    if (uri == -1 || uri == element.uri) {
                        break;
                    }
                } else if (type == XMLContentSpec.CONTENTSPECNODE_ANY_LOCAL) {
                    if (element.uri == -1) {
                        break;
                    }
                } else if (type == XMLContentSpec.CONTENTSPECNODE_ANY_OTHER) {
                    if (fElemMap[i].uri != element.uri) {
                        break;
                    }
                } else if (type == XMLContentSpec.CONTENTSPECNODE_ANY_SKIP) {
                    int uri = fElemMap[i].uri;
                    if (uri == -1 || uri == element.uri) {
                        skipThisOne = true;
                        break;
                    }
                } else if (type == XMLContentSpec.CONTENTSPECNODE_ANY_LOCAL_SKIP) {
                    if (element.uri == -1) {
                        skipThisOne = true;
                        break;
                    }
                } else if (type == XMLContentSpec.CONTENTSPECNODE_ANY_OTHER_SKIP) {
                    if (fElemMap[i].uri != element.uri) {
                        skipThisOne = true;
                        break;
                    }
                } else if (type == XMLContentSpec.CONTENTSPECNODE_ANY_LAX) {
                    int uri = fElemMap[i].uri;
                    if (uri == -1 || uri == element.uri) {
                        laxThisOne = true;
                        break;
                    }
                } else if (type == XMLContentSpec.CONTENTSPECNODE_ANY_LOCAL_LAX) {
                    if (element.uri == -1) {
                        laxThisOne = true;
                        break;
                    }
                } else if (type == XMLContentSpec.CONTENTSPECNODE_ANY_OTHER_LAX) {
                    if (fElemMap[i].uri != element.uri) {
                        laxThisOne = true;
                        break;
                    }
                }

            }

        }

        if (skipThisOne) {
            fNeedValidationOff = true;
        } else {

            //REVISIT: is this the right place to check on if the Schema has changed?

            if ( fNamespacesEnabled && fValidating && element.uri != fGrammarNameSpaceIndex && element.uri != -1  ) {
                fGrammarNameSpaceIndex = element.uri;

                boolean success = switchGrammar(fGrammarNameSpaceIndex);

                if (!success && !laxThisOne) {
                    reportRecoverableXMLError(XMLMessages.MSG_GENERIC_SCHEMA_ERROR, XMLMessages.SCHEMA_GENERIC_ERROR, 
                                              "Grammar with uri : " + fStringPool.toString(fGrammarNameSpaceIndex) 
                                              + " , can not found");
                }
            }


            if ( fGrammar != null ) {
                if (DEBUG_SCHEMA_VALIDATION) {
                    System.out.println("*******Lookup element: uri: " + fStringPool.toString(element.uri)+
                                       "localpart: '" + fStringPool.toString(element.localpart)
                                       +"' and scope : " + fCurrentScope+"\n");
                }

                elementIndex = fGrammar.getElementDeclIndex(element,fCurrentScope);

                if (elementIndex == -1 ) {
                    elementIndex = fGrammar.getElementDeclIndex(element, TOP_LEVEL_SCOPE);
                }

                if (elementIndex == -1) {
                    // if validating based on a Schema, try to resolve the element again by look it up in its ancestor types
                    if (fGrammarIsSchemaGrammar && fCurrentElementIndex != -1) {
                        TraverseSchema.ComplexTypeInfo baseTypeInfo = null;
                        baseTypeInfo = ((SchemaGrammar)fGrammar).getElementComplexTypeInfo(fCurrentElementIndex);
                        //TO DO: 
                        //      should check if baseTypeInfo is from the same Schema.
                        while (baseTypeInfo != null) {
                            elementIndex = fGrammar.getElementDeclIndex(element, baseTypeInfo.scopeDefined);
                            if (elementIndex > -1 ) {
                                break;
                            }
                            baseTypeInfo = baseTypeInfo.baseComplexTypeInfo;
                        }
                    }
                    //if still can't resolve it, try TOP_LEVEL_SCOPE AGAIN
                    /****
                    if ( element.uri == -1 && elementIndex == -1 
                    && fNamespacesScope != null 
                    && fNamespacesScope.getNamespaceForPrefix(StringPool.EMPTY_STRING) != -1 ) {
                    elementIndex = fGrammar.getElementDeclIndex(element.localpart, TOP_LEVEL_SCOPE);
                    // REVISIT:
                    // this is a hack to handle the situation where namespace prefix "" is bound to nothing, and there
                    // is a "noNamespaceSchemaLocation" specified, and element 
                    element.uri = StringPool.EMPTY_STRING;
                    }
                    /****/

                    /****/
                    if (elementIndex == -1) {
                        if (laxThisOne) {
                            fNeedValidationOff = true;
                        } else
                            if (DEBUG_SCHEMA_VALIDATION)
                            System.out.println("!!! can not find elementDecl in the grammar, " +
                                               " the element localpart: " + element.localpart +
                                               "["+fStringPool.toString(element.localpart) +"]" +
                                               " the element uri: " + element.uri + 
                                               "["+fStringPool.toString(element.uri) +"]" +
                                               " and the current enclosing scope: " + fCurrentScope );
                    }
                    /****/
                }

                if (DEBUG_SCHEMA_VALIDATION) {
                    fGrammar.getElementDecl(elementIndex, fTempElementDecl);
                    System.out.println("elementIndex: " + elementIndex+" \n and itsName : '" 
                                       + fStringPool.toString(fTempElementDecl.name.localpart)
                                       +"' \n its ContentType:" + fTempElementDecl.type
                                       +"\n its ContentSpecIndex : " + fTempElementDecl.contentSpecIndex +"\n"+
                                       " and the current enclosing scope: " + fCurrentScope);
                }
            }

            contentSpecType =  getContentSpecType(elementIndex);

            if (fGrammarIsSchemaGrammar && elementIndex != -1) {

                // handle "xsi:type" right here
                if (fXsiTypeAttValue > -1) {
                    String xsiType = fStringPool.toString(fXsiTypeAttValue);
                    int colonP = xsiType.indexOf(":");
                    String prefix = "";
                    String localpart = xsiType;
                    if (colonP > -1) {
                        prefix = xsiType.substring(0,colonP);
                        localpart = xsiType.substring(colonP+1);
                    }

                    String uri = "";
                    int uriIndex = -1;
                    if (fNamespacesScope != null) {
                        uriIndex = fNamespacesScope.getNamespaceForPrefix(fStringPool.addSymbol(prefix));
                        if (uriIndex > -1) {
                            uri = fStringPool.toString(uriIndex);
                            if (uriIndex != fGrammarNameSpaceIndex) {
                                fGrammarNameSpaceIndex = fCurrentSchemaURI = uriIndex;
                                boolean success = switchGrammar(fCurrentSchemaURI);
                                if (!success && !fNeedValidationOff) {
                                    reportRecoverableXMLError(XMLMessages.MSG_GENERIC_SCHEMA_ERROR, 
                                                              XMLMessages.SCHEMA_GENERIC_ERROR, 
                                                              "Grammar with uri : " 
                                                              + fStringPool.toString(fCurrentSchemaURI) 
                                                              + " , can not found");
                                }
                            }
                        }
                    }


                    Hashtable complexRegistry = ((SchemaGrammar)fGrammar).getComplexTypeRegistry();
                    DatatypeValidatorFactoryImpl dataTypeReg = ((SchemaGrammar)fGrammar).getDatatypeRegistry();
                    if (complexRegistry==null || dataTypeReg == null) {
                        reportRecoverableXMLError(XMLMessages.MSG_GENERIC_SCHEMA_ERROR, 
                                                  XMLMessages.SCHEMA_GENERIC_ERROR, 
                                                  fErrorReporter.getLocator().getSystemId()
                                                  +" line"+fErrorReporter.getLocator().getLineNumber()
                                                  +", canot resolve xsi:type = " + xsiType+"  ---2");
                    } else {
                        TraverseSchema.ComplexTypeInfo typeInfo = 
                        (TraverseSchema.ComplexTypeInfo) complexRegistry.get(uri+","+localpart);
                        //TO DO:
                        //      here need to check if this substitution is legal based on the current active grammar,
                        //      this should be easy, cause we already saved final, block and base type information in 
                        //      the SchemaGrammar.

                        if (typeInfo==null) {
                            if (uri.length() == 0 || uri.equals(SchemaSymbols.URI_SCHEMAFORSCHEMA) ) {
                                fXsiTypeValidator = dataTypeReg.getDatatypeValidator(localpart);
                            } else
                                fXsiTypeValidator = dataTypeReg.getDatatypeValidator(uri+","+localpart);
                            if ( fXsiTypeValidator == null )
                                reportRecoverableXMLError(XMLMessages.MSG_GENERIC_SCHEMA_ERROR, 
                                                          XMLMessages.SCHEMA_GENERIC_ERROR, 
                                                          "unresolved type : "+uri+","+localpart 
                                                          +" found  in xsi:type handling");
                        } else
                            elementIndex = typeInfo.templateElementIndex;
                    }

                    fXsiTypeAttValue = -1;
                }

                //Change the current scope to be the one defined by this element.
                fCurrentScope = ((SchemaGrammar) fGrammar).getElementDefinedScope(elementIndex);

                //       here need to check if we need to switch Grammar by asking SchemaGrammar whether 
                //       this element actually is of a type in another Schema.
                String anotherSchemaURI = ((SchemaGrammar)fGrammar).getElementFromAnotherSchemaURI(elementIndex);
                if (anotherSchemaURI != null) {
                    //before switch Grammar, set the elementIndex to be the template elementIndex of its type
                    if (contentSpecType != -1 
                        && contentSpecType != XMLElementDecl.TYPE_EMPTY ) {
                        TraverseSchema.ComplexTypeInfo typeInfo = ((SchemaGrammar) fGrammar).getElementComplexTypeInfo(elementIndex);
                        if (typeInfo != null) {
                            elementIndex = typeInfo.templateElementIndex;
                        }

                    }

                    // now switch the grammar
                    fGrammarNameSpaceIndex = fCurrentSchemaURI = fStringPool.addSymbol(anotherSchemaURI);
                    boolean success = switchGrammar(fCurrentSchemaURI);
                    if (!success && !fNeedValidationOff) {
                        reportRecoverableXMLError(XMLMessages.MSG_GENERIC_SCHEMA_ERROR, 
                                                  XMLMessages.SCHEMA_GENERIC_ERROR, 
                                                  "Grammar with uri : " 
                                                  + fStringPool.toString(fCurrentSchemaURI) 
                                                  + " , can not found");
                    }
                }

            }

            if (contentSpecType == -1 && fValidating && !fNeedValidationOff ) {
                reportRecoverableXMLError(XMLMessages.MSG_ELEMENT_NOT_DECLARED,
                                          XMLMessages.VC_ELEMENT_VALID,
                                          element.rawname);
            }
            if (fGrammar != null && fGrammarIsSchemaGrammar && elementIndex != -1) {
                fAttrListHandle = addDefaultAttributes(elementIndex, attrList, fAttrListHandle, fValidating, fStandaloneReader != -1);
            }
            if (fAttrListHandle != -1) {
                fAttrList.endAttrList();
            }

            if (DEBUG_PRINT_ATTRIBUTES) {
                String elementStr = fStringPool.toString(element.rawname);
                System.out.print("startElement: <" + elementStr);
                if (fAttrListHandle != -1) {
                    int index = attrList.getFirstAttr(fAttrListHandle);
                    while (index != -1) {
                        System.out.print(" " + fStringPool.toString(attrList.getAttrName(index)) + "=\"" +
                                         fStringPool.toString(attrList.getAttValue(index)) + "\"");
                        index = attrList.getNextAttr(index);
                    }
                }
                System.out.println(">");
            }
            // REVISIT: Validation. Do we need to recheck for the xml:lang
            //          attribute? It was already checked above -- perhaps
            //          this is to check values that are defaulted in? If
            //          so, this check could move to the attribute decl
            //          callback so we can check the default value before
            //          it is used.
            if (fAttrListHandle != -1 && !fNeedValidationOff ) {
                int index = fAttrList.getFirstAttr(fAttrListHandle);
                while (index != -1) {
                    int attrNameIndex = attrList.getAttrName(index);

                    if (fStringPool.equalNames(attrNameIndex, fXMLLang)) {
                        fDocumentScanner.checkXMLLangAttributeValue(attrList.getAttValue(index));
                        // break;
                    }
                    // here, we validate every "user-defined" attributes
                    int _xmlns = fStringPool.addSymbol("xmlns");

                    if (attrNameIndex != _xmlns && attrList.getAttrPrefix(index) != _xmlns)
                        if (fGrammar != null) {
                            fAttrNameLocator = getLocatorImpl(fAttrNameLocator);
                            fTempQName.setValues(attrList.getAttrPrefix(index), 
                                                 attrList.getAttrLocalpart(index),
                                                 attrList.getAttrName(index),
                                                 attrList.getAttrURI(index) );
                            int attDefIndex = getAttDefByElementIndex(elementIndex, fTempQName);

                            if (fTempQName.uri != fXsiURI)
                                if (attDefIndex == -1 ) {
                                    if (fValidating) {
                                        // REVISIT - cache the elem/attr tuple so that we only give
                                        //  this error once for each unique occurrence
                                        Object[] args = { fStringPool.toString(element.rawname),
                                            fStringPool.toString(attrList.getAttrName(index))};

                                        /*****/
                                        fErrorReporter.reportError(fAttrNameLocator,
                                                                   XMLMessages.XML_DOMAIN,
                                                                   XMLMessages.MSG_ATTRIBUTE_NOT_DECLARED,
                                                                   XMLMessages.VC_ATTRIBUTE_VALUE_TYPE,
                                                                   args,
                                                                   XMLErrorReporter.ERRORTYPE_RECOVERABLE_ERROR);   
                                        /******/
                                    }
                                } else {

                                    fGrammar.getAttributeDecl(attDefIndex, fTempAttDecl); 

                                    int attributeType = attributeTypeName(fTempAttDecl);
                                    attrList.setAttType(index, attributeType);

                                    if (fValidating) {

                                        if (fGrammarIsDTDGrammar && 
                                            (fTempAttDecl.type == XMLAttributeDecl.TYPE_ENTITY ||
                                             fTempAttDecl.type == XMLAttributeDecl.TYPE_ENUMERATION ||
                                             fTempAttDecl.type == XMLAttributeDecl.TYPE_ID ||
                                             fTempAttDecl.type == XMLAttributeDecl.TYPE_IDREF ||
                                             fTempAttDecl.type == XMLAttributeDecl.TYPE_NMTOKEN ||
                                             fTempAttDecl.type == XMLAttributeDecl.TYPE_NOTATION)
                                           ) {
                                            validateDTDattribute(element, attrList.getAttValue(index), fTempAttDecl);
                                        }

                                        // check to see if this attribute matched an attribute wildcard
                                        else if ( fGrammarIsSchemaGrammar && 
                                                  (fTempAttDecl.type == XMLAttributeDecl.TYPE_ANY_ANY 
                                                   ||fTempAttDecl.type == XMLAttributeDecl.TYPE_ANY_LIST
                                                   ||fTempAttDecl.type == XMLAttributeDecl.TYPE_ANY_LOCAL 
                                                   ||fTempAttDecl.type == XMLAttributeDecl.TYPE_ANY_OTHER) ) {

                                            if (fTempAttDecl.defaultType == XMLAttributeDecl.PROCESSCONTENTS_SKIP) {
                                                // attribute should just be bypassed, 
                                            } else if ( fTempAttDecl.defaultType == XMLAttributeDecl.PROCESSCONTENTS_STRICT
                                                        || fTempAttDecl.defaultType == XMLAttributeDecl.PROCESSCONTENTS_LAX) {

                                                boolean reportError = false;
                                                boolean processContentStrict = 
                                                fTempAttDecl.defaultType == XMLAttributeDecl.PROCESSCONTENTS_STRICT;

                                                if (fTempQName.uri == -1) {
                                                    if (processContentStrict) {
                                                        reportError = true;
                                                    }
                                                } else {
                                                    Grammar aGrammar = 
                                                    fGrammarResolver.getGrammar(fStringPool.toString(fTempQName.uri));

                                                    if (aGrammar == null || !(aGrammar instanceof SchemaGrammar) ) {
                                                        if (processContentStrict) {
                                                            reportError = true;
                                                        }
                                                    } else {
                                                        SchemaGrammar sGrammar = (SchemaGrammar) aGrammar;
                                                        Hashtable attRegistry = sGrammar.getAttirubteDeclRegistry();
                                                        if (attRegistry == null) {
                                                            if (processContentStrict) {
                                                                reportError = true;
                                                            }
                                                        } else {
                                                            XMLAttributeDecl attDecl = (XMLAttributeDecl) attRegistry.get(fStringPool.toString(fTempQName.localpart));
                                                            if (attDecl == null) {
                                                                if (processContentStrict) {
                                                                    reportError = true;
                                                                }
                                                            } else {
                                                                DatatypeValidator attDV = attDecl.datatypeValidator;
                                                                if (attDV == null) {
                                                                    if (processContentStrict) {
                                                                        reportError = true;
                                                                    }
                                                                } else {
                                                                    try {
                                                                        String  unTrimValue = fStringPool.toString(attrList.getAttValue(index));
                                                                        String  value       = unTrimValue.trim();
                                                                        if (attDecl.type == XMLAttributeDecl.TYPE_ID ) {
                                                                            this.fStoreIDRef.setDatatypeObject( fValID.validate( value, null ) );
                                                                        }
                                                                        if (attDecl.type == XMLAttributeDecl.TYPE_IDREF ) {
                                                                            attDV.validate(value, this.fStoreIDRef );
                                                                        } else
                                                                            attDV.validate(unTrimValue, null );
                                                                    } catch (InvalidDatatypeValueException idve) {
                                                                        fErrorReporter.reportError(fErrorReporter.getLocator(),
                                                                                                   SchemaMessageProvider.SCHEMA_DOMAIN,
                                                                                                   SchemaMessageProvider.DatatypeError,
                                                                                                   SchemaMessageProvider.MSG_NONE,
                                                                                                   new Object [] { idve.getMessage()},
                                                                                                   XMLErrorReporter.ERRORTYPE_RECOVERABLE_ERROR);
                                                                    }
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                                if (reportError) {
                                                    Object[] args = { fStringPool.toString(element.rawname),
                                                        "ANY---"+fStringPool.toString(attrList.getAttrName(index))};

                                                    fErrorReporter.reportError(fAttrNameLocator,    
                                                                               XMLMessages.XML_DOMAIN,
                                                                               XMLMessages.MSG_ATTRIBUTE_NOT_DECLARED,
                                                                               XMLMessages.VC_ATTRIBUTE_VALUE_TYPE,
                                                                               args,
                                                                               XMLErrorReporter.ERRORTYPE_RECOVERABLE_ERROR);

                                                }
                                            }
                                        } else if (fTempAttDecl.datatypeValidator == null) {
                                            Object[] args = { fStringPool.toString(element.rawname),
                                                fStringPool.toString(attrList.getAttrName(index))};

                                            System.out.println("[Error] Datatypevalidator for attribute " + fStringPool.toString(attrList.getAttrName(index))
                                                               + " not found in element type " + fStringPool.toString(element.rawname));
                                            //REVISIT : is this the right message?
                                            /****/
                                            fErrorReporter.reportError(fAttrNameLocator,    
                                                                       XMLMessages.XML_DOMAIN,
                                                                       XMLMessages.MSG_ATTRIBUTE_NOT_DECLARED,
                                                                       XMLMessages.VC_ATTRIBUTE_VALUE_TYPE,
                                                                       args,
                                                                       XMLErrorReporter.ERRORTYPE_RECOVERABLE_ERROR);   
                                            /****/
                                        } else {
                                            try {
                                                String  unTrimValue = fStringPool.toString(attrList.getAttValue(index));
                                                String  value       = unTrimValue.trim();
                                                if (fTempAttDecl.type == XMLAttributeDecl.TYPE_ID ) {
                                                    this.fStoreIDRef.setDatatypeObject( fValID.validate( value, null ) );
                                                } else if (fTempAttDecl.type == XMLAttributeDecl.TYPE_IDREF ) {
                                                    fTempAttDecl.datatypeValidator.validate(value, this.fStoreIDRef );
                                                } else {
                                                    fTempAttDecl.datatypeValidator.validate(unTrimValue, null );
                                                }

                                            } catch (InvalidDatatypeValueException idve) {
                                                fErrorReporter.reportError(fErrorReporter.getLocator(),
                                                                           SchemaMessageProvider.SCHEMA_DOMAIN,
                                                                           SchemaMessageProvider.DatatypeError,
                                                                           SchemaMessageProvider.MSG_NONE,
                                                                           new Object [] { idve.getMessage()},
                                                                           XMLErrorReporter.ERRORTYPE_RECOVERABLE_ERROR);
                                            }
                                        }
                                    } // end of if (fValidating)


                                } // end of if (attDefIndex == -1) else

                        }// end of if (fGrammar != null)
                    index = fAttrList.getNextAttr(index);
                }
            }
        }
        if (fAttrListHandle != -1) {
            int index = attrList.getFirstAttr(fAttrListHandle);
            while (index != -1) {
                int attName = attrList.getAttrName(index);
                if (!fStringPool.equalNames(attName, fNamespacesPrefix)) {
                    int attPrefix = attrList.getAttrPrefix(index);
                    if (attPrefix != fNamespacesPrefix) {
                        if (attPrefix != -1) {
                            int uri = fNamespacesScope.getNamespaceForPrefix(attPrefix);
                            if (uri == -1) {
                                Object[] args = { fStringPool.toString(attPrefix)};
                                fErrorReporter.reportError(fErrorReporter.getLocator(),
                                                           XMLMessages.XMLNS_DOMAIN,
                                                           XMLMessages.MSG_PREFIX_DECLARED,
                                                           XMLMessages.NC_PREFIX_DECLARED,
                                                           args,
                                                           XMLErrorReporter.ERRORTYPE_RECOVERABLE_ERROR);
                            }
                            attrList.setAttrURI(index, uri);
                        }
                    }
                }
                index = attrList.getNextAttr(index);
            }
        }

        fCurrentElementIndex = elementIndex;
        fCurrentContentSpecType = contentSpecType;

        if (fValidating && contentSpecType == XMLElementDecl.TYPE_SIMPLE) {
            fBufferDatatype = true;
            fDatatypeBuffer.setLength(0);
        }

        fInElementContent = (contentSpecType == XMLElementDecl.TYPE_CHILDREN);

    } // validateElementAndAttributes(QName,XMLAttrList)


    //validate attributes in DTD fashion
    private void validateDTDattribute(QName element, int attValue, 
                                      XMLAttributeDecl attributeDecl) throws Exception{
        AttributeValidator av = null;
        switch (attributeDecl.type) {
        case XMLAttributeDecl.TYPE_ENTITY:
            {
                boolean isAlistAttribute = attributeDecl.list;//Caveat - Save this information because invalidStandaloneAttDef
                String  unTrimValue      = fStringPool.toString(attValue);
                String  value            = unTrimValue.trim();
                //System.out.println("value = " + value );
                                                               //changes fTempAttDef
                if (fValidationEnabled) {
                    if (value != unTrimValue) {
                        if (invalidStandaloneAttDef(element, attributeDecl.name)) {
                            reportRecoverableXMLError(XMLMessages.MSG_ATTVALUE_CHANGED_DURING_NORMALIZATION_WHEN_STANDALONE,
                                                      XMLMessages.VC_STANDALONE_DOCUMENT_DECLARATION,
                                                      fStringPool.toString(attributeDecl.name.rawname), unTrimValue, value);
                        }
                    }
                }

                try {
                    if ( isAlistAttribute ) {
                        fValENTITIES.validate( value, null );
                    } else {
                        fValENTITY.validate( value, null );
                    }
                } catch ( InvalidDatatypeValueException ex ) {
                    if ( ex.getMajorCode() != 1 && ex.getMinorCode() != -1 ) {
                        reportRecoverableXMLError(ex.getMajorCode(),
                                                  ex.getMinorCode(),
                                                  fStringPool.toString( attributeDecl.name.rawname), value );
                    } else {
                        System.err.println("Error: " + ex.getLocalizedMessage() );//Should not happen
                    }
                }

                /*if (attributeDecl.list) {
                    av = fAttValidatorENTITIES;
                }
                else {
                    av = fAttValidatorENTITY;
                }*/

            }
            break;
        case XMLAttributeDecl.TYPE_ENUMERATION:
            av = fAttValidatorENUMERATION;
            break;
        case XMLAttributeDecl.TYPE_ID:
            {
                String  unTrimValue = fStringPool.toString(attValue);
                String  value       = unTrimValue.trim();
                if (fValidationEnabled) {
                    if (value != unTrimValue) {
                        if (invalidStandaloneAttDef(element, attributeDecl.name)) {
                            reportRecoverableXMLError(XMLMessages.MSG_ATTVALUE_CHANGED_DURING_NORMALIZATION_WHEN_STANDALONE,
                                                      XMLMessages.VC_STANDALONE_DOCUMENT_DECLARATION,
                                                      fStringPool.toString(attributeDecl.name.rawname), unTrimValue, value);
                        }
                    }
                }
                try {
                    //this.fIdDefs = (Hashtable) fValID.validate( value, null );
                    //System.out.println("this.fIdDefs = " + this.fIdDefs );

                    this.fStoreIDRef.setDatatypeObject( fValID.validate( value, null ) );
                    fValIDRef.validate( value, this.fStoreIDRef ); //just in case we called id after IDREF
                } catch ( InvalidDatatypeValueException ex ) {
                    reportRecoverableXMLError(ex.getMajorCode(),
                                              ex.getMinorCode(),
                                              fStringPool.toString( attributeDecl.name.rawname), value );
                }
            }
            break;
        case XMLAttributeDecl.TYPE_IDREF:
            {
                String  unTrimValue = fStringPool.toString(attValue);
                String  value       = unTrimValue.trim();
                boolean isAlistAttribute = attributeDecl.list;//Caveat - Save this information because invalidStandaloneAttDef
                                                              //changes fTempAttDef
                if (fValidationEnabled) {
                    if (value != unTrimValue) {
                        if (invalidStandaloneAttDef(element, attributeDecl.name)) {
                            reportRecoverableXMLError(XMLMessages.MSG_ATTVALUE_CHANGED_DURING_NORMALIZATION_WHEN_STANDALONE,
                                                      XMLMessages.VC_STANDALONE_DOCUMENT_DECLARATION,
                                                      fStringPool.toString(attributeDecl.name.rawname), unTrimValue, value);
                        }
                    }
                }
                try {
                    if ( isAlistAttribute ) {
                        fValIDRefs.validate( value, this.fStoreIDRef );
                    } else {
                        fValIDRef.validate( value, this.fStoreIDRef );
                    }
                } catch ( InvalidDatatypeValueException ex ) {
                    if ( ex.getMajorCode() != 1 && ex.getMinorCode() != -1 ) {
                        reportRecoverableXMLError(ex.getMajorCode(),
                                                  ex.getMinorCode(),
                                                  fStringPool.toString( attributeDecl.name.rawname), value );
                    } else {
                        System.err.println("Error: " + ex.getLocalizedMessage() );//Should not happen
                    }
                }

            }
            break;
        case XMLAttributeDecl.TYPE_NOTATION:
            {
                /* WIP
                String  unTrimValue = fStringPool.toString(attValue);
             String  value       = unTrimValue.trim();
             if (fValidationEnabled) {
                 if (value != unTrimValue) {
                     if (invalidStandaloneAttDef(element, attributeDecl.name)) {
                         reportRecoverableXMLError(XMLMessages.MSG_ATTVALUE_CHANGED_DURING_NORMALIZATION_WHEN_STANDALONE,
                                                   XMLMessages.VC_STANDALONE_DOCUMENT_DECLARATION,
                                                   fStringPool.toString(attributeDecl.name.rawname), unTrimValue, value);
                     }
                 }
             }
             try {
                 //this.fIdDefs = (Hashtable) fValID.validate( value, null );
                 //System.out.println("this.fIdDefs = " + this.fIdDefs );

                 this.fStoreIDRef.setDatatypeObject( fValID.validate( value, null ) );
             } catch ( InvalidDatatypeValueException ex ) {
                 reportRecoverableXMLError(ex.getMajorCode(),
                                           ex.getMinorCode(),
                                           fStringPool.toString( attributeDecl.name.rawname), value );
             }
          }
            */
            av = fAttValidatorNOTATION;


            }
            break;
        case XMLAttributeDecl.TYPE_NMTOKEN:
            {
                String  unTrimValue = fStringPool.toString(attValue);
                String  value       = unTrimValue.trim();
                boolean isAlistAttribute = attributeDecl.list;//Caveat - Save this information because invalidStandaloneAttDef
                //changes fTempAttDef
                if (fValidationEnabled) {
                    if (value != unTrimValue) {
                        if (invalidStandaloneAttDef(element, attributeDecl.name)) {
                            reportRecoverableXMLError(XMLMessages.MSG_ATTVALUE_CHANGED_DURING_NORMALIZATION_WHEN_STANDALONE,
                                                      XMLMessages.VC_STANDALONE_DOCUMENT_DECLARATION,
                                                      fStringPool.toString(attributeDecl.name.rawname), unTrimValue, value);
                        }
                    }
                }
                try {
                    if ( isAlistAttribute ) {
                        fValNMTOKENS.validate( value, null );
                    } else {
                        fValNMTOKEN.validate( value, null );
                    }
                } catch ( InvalidDatatypeValueException ex ) {
                    reportRecoverableXMLError(XMLMessages.MSG_NMTOKEN_INVALID,
                                              XMLMessages.VC_NAME_TOKEN,
                                              fStringPool.toString(attributeDecl.name.rawname), value);//TODO NMTOKENS messge
                }

            }
            break;
        }
        if ( av != null )
            av.normalize(element, attributeDecl.name, attValue, 
                         attributeDecl.type, attributeDecl.enumeration);
    }

    /** Character data in content. */
    private void charDataInContent() {

        if (DEBUG_ELEMENT_CHILDREN) {
            System.out.println("charDataInContent()");
        }
        if (fElementChildren.length <= fElementChildrenLength) {
            QName[] newarray = new QName[fElementChildren.length * 2];
            System.arraycopy(fElementChildren, 0, newarray, 0, fElementChildren.length);
            fElementChildren = newarray;
        }
        QName qname = fElementChildren[fElementChildrenLength];
        if (qname == null) {
            for (int i = fElementChildrenLength; i < fElementChildren.length; i++) {
                fElementChildren[i] = new QName();
            }
            qname = fElementChildren[fElementChildrenLength];
        }
        qname.clear();
        fElementChildrenLength++;

    } // charDataInCount()

    /**
     * Check that the content of an element is valid.
     * <p>
     * This is the method of primary concern to the validator. This method is called
     * upon the scanner reaching the end tag of an element. At that time, the
     * element's children must be structurally validated, so it calls this method.
     * The index of the element being checked (in the decl pool), is provided as
     * well as an array of element name indexes of the children. The validator must
     * confirm that this element can have these children in this order.
     * <p>
     * This can also be called to do 'what if' testing of content models just to see
     * if they would be valid.
     * <p>
     * Note that the element index is an index into the element decl pool, whereas
     * the children indexes are name indexes, i.e. into the string pool.
     * <p>
     * A value of -1 in the children array indicates a PCDATA node. All other
     * indexes will be positive and represent child elements. The count can be
     * zero, since some elements have the EMPTY content model and that must be
     * confirmed.
     *
     * @param elementIndex The index within the <code>ElementDeclPool</code> of this
     *                     element.
     * @param childCount The number of entries in the <code>children</code> array.
     * @param children The children of this element.  Each integer is an index within
     *                 the <code>StringPool</code> of the child element name.  An index
     *                 of -1 is used to indicate an occurrence of non-whitespace character
     *                 data.
     *
     * @return The value -1 if fully valid, else the 0 based index of the child
     *         that first failed. If the value returned is equal to the number
     *         of children, then additional content is required to reach a valid
     *         ending state.
     *
     * @exception Exception Thrown on error.
     */
    private int checkContent(int elementIndex, 
                             QName[] children,
                             int childOffset, 
                             int childCount) throws Exception {

        // Get the element name index from the element
        // REVISIT: Validation
        final int elementType = fCurrentElement.rawname;

        if (DEBUG_PRINT_CONTENT) {
            String strTmp = fStringPool.toString(elementType);
            System.out.println("Name: "+strTmp+", "+
                               "Count: "+childCount+", "+
                               "ContentSpecType: " +fCurrentContentSpecType); //+getContentSpecAsString(elementIndex));
            for (int index = childOffset; index < (childOffset+childCount)  && index < 10; index++) {
                if (index == 0) {
                    System.out.print("  (");
                }
                String childName = (children[index].localpart == -1) ? "#PCDATA" : fStringPool.toString(children[index].localpart);
                if (index + 1 == childCount) {
                    System.out.println(childName + ")");
                } else if (index + 1 == 10) {
                    System.out.println(childName + ",...)");
                } else {
                    System.out.print(childName + ",");
                }
            }
        }

        // Get out the content spec for this element
        final int contentType = fCurrentContentSpecType;

// debugging
//System.out.println("~~~~~~in checkContent, fCurrentContentSpecType : " + fCurrentContentSpecType);

        //
        //  Deal with the possible types of content. We try to optimized here
        //  by dealing specially with content models that don't require the
        //  full DFA treatment.
        //
        if (contentType == XMLElementDecl.TYPE_EMPTY) {
            //
            //  If the child count is greater than zero, then this is
            //  an error right off the bat at index 0.
            //
            if (childCount != 0) {
                return 0;
            }
        } else if (contentType == XMLElementDecl.TYPE_ANY) {
            //
            //  This one is open game so we don't pass any judgement on it
            //  at all. Its assumed to fine since it can hold anything.
            //
        } else if (contentType == XMLElementDecl.TYPE_MIXED ||  
                   contentType == XMLElementDecl.TYPE_CHILDREN) {
            // Get the content model for this element, faulting it in if needed
            XMLContentModel cmElem = null;
            try {
                cmElem = getElementContentModel(elementIndex);
                int result = cmElem.validateContent(children, childOffset, childCount);
                if (result != -1 && fGrammarIsSchemaGrammar) {
                    // REVISIT: not optimized for performance, 
                    EquivClassComparator comparator = new EquivClassComparator(fGrammarResolver, fStringPool);
                    cmElem.setEquivClassComparator(comparator);
                    result = cmElem.validateContentSpecial(children, childOffset, childCount);
                }
                return result;
            } catch (CMException excToCatch) {
                // REVISIT - Translate the caught exception to the protected error API
                int majorCode = excToCatch.getErrorCode();
                fErrorReporter.reportError(fErrorReporter.getLocator(),
                                           ImplementationMessages.XERCES_IMPLEMENTATION_DOMAIN,
                                           majorCode,
                                           0,
                                           null,
                                           XMLErrorReporter.ERRORTYPE_FATAL_ERROR);
            }
        } else if (contentType == -1) {
            reportRecoverableXMLError(XMLMessages.MSG_ELEMENT_NOT_DECLARED,
                                      XMLMessages.VC_ELEMENT_VALID,
                                      elementType);
        } else if (contentType == XMLElementDecl.TYPE_SIMPLE ) {

            XMLContentModel cmElem = null;
            if (childCount > 0) {
                fErrorReporter.reportError(fErrorReporter.getLocator(),
                                           SchemaMessageProvider.SCHEMA_DOMAIN,
                                           SchemaMessageProvider.DatatypeError,
                                           SchemaMessageProvider.MSG_NONE,
                                           new Object [] { "In element '"+fStringPool.toString(elementType)+"' : "+
                                               "Can not have element children within a simple type content"},
                                           XMLErrorReporter.ERRORTYPE_RECOVERABLE_ERROR);
            } else {
                try {

                    fGrammar.getElementDecl(elementIndex, fTempElementDecl);

                    DatatypeValidator dv = fTempElementDecl.datatypeValidator;

                    // If there is xsi:type validator, substitute it.
                    if ( fXsiTypeValidator != null ) {
                        dv = fXsiTypeValidator;
                        fXsiTypeValidator = null;
                    }

                    if (dv == null) {
                        System.out.println("Internal Error: this element have a simpletype "+
                                           "but no datatypevalidator was found, element "+fTempElementDecl.name
                                           +",locapart: "+fStringPool.toString(fTempElementDecl.name.localpart));
                    } else {
                        dv.validate(fDatatypeBuffer.toString(), null);
                    }

                } catch (InvalidDatatypeValueException idve) {
                    fErrorReporter.reportError(fErrorReporter.getLocator(),
                                               SchemaMessageProvider.SCHEMA_DOMAIN,
                                               SchemaMessageProvider.DatatypeError,
                                               SchemaMessageProvider.MSG_NONE,
                                               new Object [] { idve.getMessage()},
                                               XMLErrorReporter.ERRORTYPE_RECOVERABLE_ERROR);
                }
            }
        } else {
            fErrorReporter.reportError(fErrorReporter.getLocator(),
                                       ImplementationMessages.XERCES_IMPLEMENTATION_DOMAIN,
                                       ImplementationMessages.VAL_CST,
                                       0,
                                       null,
                                       XMLErrorReporter.ERRORTYPE_FATAL_ERROR);
        }

        // We succeeded
        return -1;

    } // checkContent(int,int,int[]):int


    /** 
     * Checks that all declared elements refer to declared elements
     * in their content models. This method calls out to the error
     * handler to indicate warnings.
     */
    /*private void checkDeclaredElements() throws Exception {

                //****DEBUG****
                if (DEBUG) print("(???) XMLValidator.checkDeclaredElements\n");
                //****DEBUG****

        for (int i = 0; i < fElementCount; i++) {
            int type = fGrammar.getContentSpecType(i);
            if (type == XMLElementDecl.TYPE_MIXED || type == XMLElementDecl.TYPE_CHILDREN) {
                int chunk = i >> CHUNK_SHIFT;
                int index = i &  CHUNK_MASK;
                int contentSpecIndex = fContentSpec[chunk][index];
                checkDeclaredElements(i, contentSpecIndex);
            }
        }
    }
    */

    private void printChildren() {
        if (DEBUG_ELEMENT_CHILDREN) {
            System.out.print('[');
            for (int i = 0; i < fElementChildrenLength; i++) {
                System.out.print(' ');
                QName qname = fElementChildren[i];
                if (qname != null) {
                    System.out.print(fStringPool.toString(qname.rawname));
                } else {
                    System.out.print("null");
                }
                if (i < fElementChildrenLength - 1) {
                    System.out.print(", ");
                }
                System.out.flush();
            }
            System.out.print(" ]");
            System.out.println();
        }
    }

    private void printStack() {
        if (DEBUG_ELEMENT_CHILDREN) {
            System.out.print('{');
            for (int i = 0; i <= fElementDepth; i++) {
                System.out.print(' ');
                System.out.print(fElementChildrenOffsetStack[i]);
                if (i < fElementDepth) {
                    System.out.print(", ");
                }
                System.out.flush();
            }
            System.out.print(" }");
            System.out.println();
        }
    }


    //
    // Interfaces
    //

    /**
     * AttributeValidator.
     */
    public interface AttributeValidator {

        //
        // AttributeValidator methods
        //

        /** Normalize. */
        public int normalize(QName element, QName attribute, 
                             int attValue, int attType, int enumHandle) 
        throws Exception;

    } // interface AttributeValidator


    /** Returns true if invalid standalone attribute definition. */
    boolean invalidStandaloneAttDef(QName element, QName attribute) {
        if (fStandaloneReader == -1) {
            return false;
        }
        // we are normalizing a default att value...  this ok?
        if (element.rawname == -1) {
            return false;
        }
        return getAttDefIsExternal(element, attribute);
    }


    //
    // Classes
    //


    /**
     * AttValidatorNOTATION.
     */
    final class AttValidatorNOTATION 
    implements AttributeValidator {

        //
        // AttributeValidator methods
        //

        /** Normalize. */
        public int normalize(QName element, QName attribute, 
                             int attValueHandle, int attType, 
                             int enumHandle) throws Exception {
            //
            // Normalize attribute based upon attribute type...
            //
            String attValue = fStringPool.toString(attValueHandle);
            String newAttValue = attValue.trim();
            if (fValidating) {
                // REVISIT - can we release the old string?
                if (newAttValue != attValue) {
                    if (invalidStandaloneAttDef(element, attribute)) {
                        reportRecoverableXMLError(XMLMessages.MSG_ATTVALUE_CHANGED_DURING_NORMALIZATION_WHEN_STANDALONE,
                                                  XMLMessages.VC_STANDALONE_DOCUMENT_DECLARATION,
                                                  fStringPool.toString(attribute.rawname), attValue, newAttValue);
                    }
                    attValueHandle = fStringPool.addSymbol(newAttValue);
                } else {
                    attValueHandle = fStringPool.addSymbol(attValueHandle);
                }
                //
                // NOTATION - check that the value is in the AttDef enumeration (V_TAGo)
                //
                if (!fStringPool.stringInList(enumHandle, attValueHandle)) {
                    reportRecoverableXMLError(XMLMessages.MSG_ATTRIBUTE_VALUE_NOT_IN_LIST,
                                              XMLMessages.VC_NOTATION_ATTRIBUTES,
                                              fStringPool.toString(attribute.rawname),
                                              newAttValue, fStringPool.stringListAsString(enumHandle));
                }
            } else if (newAttValue != attValue) {
                // REVISIT - can we release the old string?
                attValueHandle = fStringPool.addSymbol(newAttValue);
            }
            return attValueHandle;

        } // normalize(QName,QName,int,int,int):int

        //
        // Package methods
        //

        /** Returns true if invalid standalone attribute definition. */
        boolean invalidStandaloneAttDef(QName element, QName attribute) {
            if (fStandaloneReader == -1) {
                return false;
            }
            // we are normalizing a default att value...  this ok?
            if (element.rawname == -1) {
                return false;
            }
            return getAttDefIsExternal(element, attribute);
        }

    } // class AttValidatorNOTATION

    /**
     * AttValidatorENUMERATION.
     */
    final class AttValidatorENUMERATION 
    implements AttributeValidator {

        //
        // AttributeValidator methods
        //

        /** Normalize. */
        public int normalize(QName element, QName attribute, 
                             int attValueHandle, int attType, 
                             int enumHandle) throws Exception {
            //
            // Normalize attribute based upon attribute type...
            //
            String attValue = fStringPool.toString(attValueHandle);
            String newAttValue = attValue.trim();
            if (fValidating) {
                // REVISIT - can we release the old string?
                if (newAttValue != attValue) {
                    if (invalidStandaloneAttDef(element, attribute)) {
                        reportRecoverableXMLError(XMLMessages.MSG_ATTVALUE_CHANGED_DURING_NORMALIZATION_WHEN_STANDALONE,
                                                  XMLMessages.VC_STANDALONE_DOCUMENT_DECLARATION,
                                                  fStringPool.toString(attribute.rawname), attValue, newAttValue);
                    }
                    attValueHandle = fStringPool.addSymbol(newAttValue);
                } else {
                    attValueHandle = fStringPool.addSymbol(attValueHandle);
                }
                //
                // ENUMERATION - check that value is in the AttDef enumeration (V_TAG9)
                //
                if (!fStringPool.stringInList(enumHandle, attValueHandle)) {
                    reportRecoverableXMLError(XMLMessages.MSG_ATTRIBUTE_VALUE_NOT_IN_LIST,
                                              XMLMessages.VC_ENUMERATION,
                                              fStringPool.toString(attribute.rawname),
                                              newAttValue, fStringPool.stringListAsString(enumHandle));
                }
            } else if (newAttValue != attValue) {
                // REVISIT - can we release the old string?
                attValueHandle = fStringPool.addSymbol(newAttValue);
            }
            return attValueHandle;

        } // normalize(QName,QName,int,int,int):int

        //
        // Package methods
        //

        /** Returns true if invalid standalone attribute definition. */
        boolean invalidStandaloneAttDef(QName element, QName attribute) {
            if (fStandaloneReader == -1) {
                return false;
            }
            // we are normalizing a default att value...  this ok?
            if (element.rawname == -1) {
                return false;
            }
            return getAttDefIsExternal(element, attribute);
        }

    } // class AttValidatorENUMERATION

} // class XMLValidator
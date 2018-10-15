contentSpecType = XMLElementDecl.TYPE_MIXED_SIMPLE;

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

package org.apache.xerces.framework;

import org.apache.xerces.readers.XMLEntityHandler;
import org.apache.xerces.readers.DefaultEntityHandler;
import org.apache.xerces.utils.QName;
import org.apache.xerces.utils.StringPool;
import org.apache.xerces.utils.XMLCharacterProperties;
import org.apache.xerces.utils.XMLMessages;
import org.apache.xerces.validators.common.Grammar;
import org.apache.xerces.validators.common.GrammarResolver;
import org.apache.xerces.validators.common.XMLAttributeDecl;
import org.apache.xerces.validators.common.XMLElementDecl;
import org.apache.xerces.validators.dtd.DTDGrammar;

import org.xml.sax.Locator;
import org.xml.sax.SAXParseException;

import java.util.StringTokenizer;
/**
 * Default implementation of an XML DTD scanner.
 * <p>
 * Clients who wish to scan a DTD should implement
 * XMLDTDScanner.EventHandler to provide the desired behavior
 * when various DTD components are encountered.
 * <p>
 * To process the DTD, the client application should follow the 
 * following sequence:
 * <ol>
 *  <li>call scanDocTypeDecl() to scan the DOCTYPE declaration
 *  <li>call getReadingExternalEntity() to determine if scanDocTypeDecl found an
 *      external subset
 * <li>if scanning an external subset, call scanDecls(true) to process the external subset
 * </ol>
 *
 * @see XMLDTDScanner.EventHandler
 * @version $Id$
 */
public final class XMLDTDScanner {
    //
    // Constants
    //
    //
    // [24] VersionInfo ::= S 'version' Eq (' VersionNum ' | " VersionNum ")
    //
    private static final char[] version_string = { 'v','e','r','s','i','o','n' };
    //
    // [45] elementdecl ::= '<!ELEMENT' S Name S contentspec S? '>'
    //
    private static final char[] element_string = { 'E','L','E','M','E','N','T' };
    //
    // [46] contentspec ::= 'EMPTY' | 'ANY' | Mixed | children
    //
    private static final char[] empty_string = { 'E','M','P','T','Y' };
    private static final char[] any_string = { 'A','N','Y' };
    //
    // [51] Mixed ::= '(' S? '#PCDATA' (S? '|' S? Name)* S? ')*'
    //                | '(' S? '#PCDATA' S? ')'
    //
    private static final char[] pcdata_string = { '#','P','C','D','A','T','A' };
    //
    // [52] AttlistDecl ::= '<!ATTLIST' S Name AttDef* S? '>'
    //
    private static final char[] attlist_string = { 'A','T','T','L','I','S','T' };
    //
    // [55] StringType ::= 'CDATA'
    //
    private static final char[] cdata_string = { 'C','D','A','T','A' };
    //
    // [56] TokenizedType ::= 'ID' | 'IDREF' | 'IDREFS' | 'ENTITY' | 'ENTITIES'
    //                        | 'NMTOKEN' | 'NMTOKENS'
    //
    // Note: We search for common substrings always trying to move forward
    //
    //  'ID'      - Common prefix of ID, IDREF and IDREFS
    //  'REF'     - Common substring of IDREF and IDREFS after matching ID prefix
    //  'ENTIT'   - Common prefix of ENTITY and ENTITIES
    //  'IES'     - Suffix of ENTITIES
    //  'NMTOKEN' - Common prefix of NMTOKEN and NMTOKENS
    //
    private static final char[] id_string = { 'I','D' };
    private static final char[] ref_string = { 'R','E','F' };
    private static final char[] entit_string = { 'E','N','T','I','T' };
    private static final char[] ies_string = { 'I','E','S' };
    private static final char[] nmtoken_string = { 'N','M','T','O','K','E','N' };
    //
    // [58] NotationType ::= 'NOTATION' S '(' S? Name (S? '|' S? Name)* S? ')'
    // [82] NotationDecl ::= '<!NOTATION' S Name S (ExternalID |  PublicID) S? '>'
    //
    private static final char[] notation_string = { 'N','O','T','A','T','I','O','N' };
    //
    // [60] DefaultDecl ::= '#REQUIRED' | '#IMPLIED' | (('#FIXED' S)? AttValue)
    //
    private static final char[] required_string = { '#','R','E','Q','U','I','R','E','D' };
    private static final char[] implied_string = { '#','I','M','P','L','I','E','D' };
    private static final char[] fixed_string = { '#','F','I','X','E','D' };
    //
    // [62] includeSect ::= '<![' S? 'INCLUDE' S? '[' extSubsetDecl ']]>'
    //
    private static final char[] include_string = { 'I','N','C','L','U','D','E' };
    //
    // [63] ignoreSect ::= '<![' S? 'IGNORE' S? '[' ignoreSectContents* ']]>'
    //
    private static final char[] ignore_string = { 'I','G','N','O','R','E' };
    //
    // [71] GEDecl ::= '<!ENTITY' S Name S EntityDef S? '>'
    // [72] PEDecl ::= '<!ENTITY' S '%' S Name S PEDef S? '>'
    //
    private static final char[] entity_string = { 'E','N','T','I','T','Y' };
    //
    // [75] ExternalID ::= 'SYSTEM' S SystemLiteral
    //                     | 'PUBLIC' S PubidLiteral S SystemLiteral
    // [83] PublicID ::= 'PUBLIC' S PubidLiteral
    //
    private static final char[] system_string = { 'S','Y','S','T','E','M' };
    private static final char[] public_string = { 'P','U','B','L','I','C' };
    //
    // [76] NDataDecl ::= S 'NDATA' S Name
    //
    private static final char[] ndata_string = { 'N','D','A','T','A' };
    //
    // [80] EncodingDecl ::= S 'encoding' Eq ('"' EncName '"' |  "'" EncName "'" )
    //
    private static final char[] encoding_string = { 'e','n','c','o','d','i','n','g' };
    //
    // Instance Variables
    //
    private DTDGrammar fDTDGrammar = null;
    private GrammarResolver fGrammarResolver = null;
    private boolean fNamespacesEnabled = false;
    private boolean fValidationEnabled = false;
    private boolean fLoadExternalDTD = true;
    private XMLElementDecl fTempElementDecl = new XMLElementDecl();
    private XMLAttributeDecl fTempAttributeDecl = new XMLAttributeDecl();
    private QName fElementQName = new QName();
    private QName fAttributeQName = new QName();
    private QName fElementRefQName = new QName();
    private EventHandler fEventHandler = null;
    private XMLDocumentHandler.DTDHandler fDTDHandler = null;
    private StringPool fStringPool = null;
    private XMLErrorReporter fErrorReporter = null;
    private XMLEntityHandler fEntityHandler = null;
    private XMLEntityHandler.EntityReader fEntityReader = null;
    private XMLEntityHandler.CharBuffer fLiteralData = null;
    private int fReaderId = -1;
    private int fSystemLiteral = -1;
    private int fPubidLiteral = -1;
    private int[] fOpStack = null;
    private int[] fNodeIndexStack = null;
    private int[] fPrevNodeIndexStack = null;
    private int fScannerState = SCANNER_STATE_INVALID;
    private int fIncludeSectDepth = 0;
    private int fDoctypeReader = -1;
    private int fExternalSubsetReader = -1;
    private int fDefaultAttValueReader = -1;
    private int fDefaultAttValueElementType = -1;
    private int fDefaultAttValueAttrName = -1;
    private int fDefaultAttValueOffset = -1;
    private int fDefaultAttValueMark = -1;
    private int fEntityValueReader = -1;
    private int fEntityValueMark = -1;
    private int fXMLSymbol = -1;
    private int fXMLNamespace = -1;
    private int fXMLSpace = -1;
    private int fDefault = -1;
    private int fPreserve = -1;
    private int fScannerMarkupDepth = 0;
    private int fScannerParenDepth = 0;
    //
    // Constructors
    //
    public XMLDTDScanner(StringPool stringPool,
                         XMLErrorReporter errorReporter,
                         XMLEntityHandler entityHandler,
                         XMLEntityHandler.CharBuffer literalData) {
        fStringPool = stringPool;
        fErrorReporter = errorReporter;
        fEntityHandler = entityHandler;
        fLiteralData = literalData;
        init();
    }

    /**
     * Set the event handler
     *
     * @param eventHandler The place to send our callbacks.
     */
    public void setEventHandler(XMLDTDScanner.EventHandler eventHandler) {
        fEventHandler = eventHandler;
    }

    /** Set the DTD handler. */
    public void setDTDHandler(XMLDocumentHandler.DTDHandler dtdHandler) {
        fDTDHandler = dtdHandler;
    }

    /** Sets the grammar resolver. */
    public void setGrammarResolver(GrammarResolver resolver) {
        fGrammarResolver = resolver;
    }

    /** set fNamespacesEnabled  **/
    public void setNamespacesEnabled(boolean enabled) {
        fNamespacesEnabled = enabled;
    }
    
    /** set fValidationEnabled  **/
    public void setValidationEnabled(boolean enabled) {
        fValidationEnabled = enabled;
    }

    /** Sets whether the parser loads the external DTD. */
    public void setLoadExternalDTD(boolean enabled) {
        fLoadExternalDTD = enabled;
    }

    /**
     * Is the XMLDTDScanner reading from an external entity?
     *
     * This will be true, in particular if there was an external subset
     *
     * @return true if the XMLDTDScanner is reading from an external entity.
     */
    public boolean getReadingExternalEntity() {
        return fReaderId != fDoctypeReader;
    }
    /**
     * Is the scanner reading a ContentSpec?
     * 
     * @return true if the scanner is reading a ContentSpec
     */
    public boolean getReadingContentSpec() {
        return getScannerState() == SCANNER_STATE_CONTENTSPEC;
    }
    /**
     * Report the markup nesting depth.  This allows a client to
     * perform validation checks for correct markup nesting.  This keeps
     * scanning and validation separate.
     *
     * @return the markup nesting depth
     */
    public int markupDepth() {
        return fScannerMarkupDepth;
    }
    private int increaseMarkupDepth() {
        return fScannerMarkupDepth++;
    }
    private int decreaseMarkupDepth() {
        return fScannerMarkupDepth--;
    }
    /**
     * Report the parenthesis nesting depth.  This allows a client to
     * perform validation checks for correct parenthesis balancing.  This keeps 
     * scanning and validation separate.
     *
     * @return the parenthesis depth
     */
    public int parenDepth() {
        return fScannerParenDepth;
    }
    private void setParenDepth(int parenDepth) {
        fScannerParenDepth = parenDepth;
    }
    private void increaseParenDepth() {
        fScannerParenDepth++;
    }
    private void decreaseParenDepth() {
        fScannerParenDepth--;
    }
    //
    //
    //
    /**
     * Allow XMLDTDScanner to be reused.  This method is called from an
     * XMLParser reset method, which passes the StringPool to be used
     * by the reset DTD scanner instance.
     *
     * @param stringPool the string pool to be used by XMLDTDScanner.  
     */
    public void reset(StringPool stringPool, XMLEntityHandler.CharBuffer literalData) throws Exception {
        fStringPool = stringPool;
        fLiteralData = literalData;
        fEntityReader = null;
        fReaderId = -1;
        fSystemLiteral = -1;
        fPubidLiteral = -1;
        fOpStack = null;
        fNodeIndexStack = null;
        fPrevNodeIndexStack = null;
        fScannerState = SCANNER_STATE_INVALID;
        fIncludeSectDepth = 0;
        fDoctypeReader = -1;
        fExternalSubsetReader = -1;
        fDefaultAttValueReader = -1;
        fDefaultAttValueElementType = -1;
        fDefaultAttValueAttrName = -1;
        fDefaultAttValueOffset = -1;
        fDefaultAttValueMark = -1;
        fEntityValueReader = -1;
        fEntityValueMark = -1;
        fScannerMarkupDepth = 0;
        fScannerParenDepth = 0;
        init();
    }
    private void init() {
        fXMLSymbol = fStringPool.addSymbol("xml");
        fXMLNamespace = fStringPool.addSymbol("http://www.w3.org/XML/1998/namespace");

        fXMLSpace = fStringPool.addSymbol("xml:space");
        fDefault = fStringPool.addSymbol("default");
        fPreserve = fStringPool.addSymbol("preserve");
    }

    //
    // Interfaces
    //

    /**
     * This interface must be implemented by the users of the XMLDTDScanner class.
     * These methods form the abstraction between the implementation semantics and the
     * more generic task of scanning the DTD-specific XML grammar.
     */
    public interface EventHandler {

        /** Start of DTD. */
        public void callStartDTD() throws Exception;

        /** End of DTD. */
        public void callEndDTD() throws Exception;

        /**
         * Signal the Text declaration of an external entity.
         *
         * @param version the handle in the string pool for the version number
         * @param encoding the handle in the string pool for the encoding
         * @exception java.lang.Exception
         */
        public void callTextDecl(int version, int encoding) throws Exception;
        /**
         * Called when the doctype decl is scanned
         *
         * @param rootElementType handle of the rootElement
         * @param publicId StringPool handle of the public id
         * @param systemId StringPool handle of the system id
         * @exception java.lang.Exception
         */
        public void doctypeDecl(QName rootElement, int publicId, int systemId) throws Exception;
        /**
         * Called when the DTDScanner starts reading from the external subset
         *
         * @param publicId StringPool handle of the public id
         * @param systemId StringPool handle of the system id
         * @exception java.lang.Exception
         */
        public void startReadingFromExternalSubset(int publicId, int systemId) throws Exception;
        /**
         * Called when the DTDScanner stop reading from the external subset
         *
         * @exception java.lang.Exception
         */
        public void stopReadingFromExternalSubset() throws Exception;
        /**
         * Add an element declaration (forward reference)
         *
         * @param handle to the name of the element being declared
         * @return handle to the element whose declaration was added
         * @exception java.lang.Exception
         */
        public int addElementDecl(QName elementDecl) throws Exception;
        /**
         * Add an element declaration
         *
         * @param handle to the name of the element being declared
         * @param contentSpecType handle to the type name of the content spec
         * @param ContentSpec handle to the content spec node for the contentSpecType
         * @return handle to the element declaration that was added 
         * @exception java.lang.Exception
         */
        public int addElementDecl(QName elementDecl, int contentSpecType, int contentSpec, boolean isExternal) throws Exception;
        /**
         * Add an attribute definition
         *
         * @param handle to the element whose attribute is being declared
         * @param attName StringPool handle to the attribute name being declared
         * @param attType type of the attribute
         * @param enumeration StringPool handle of the attribute's enumeration list (if any)
         * @param attDefaultType an integer value denoting the DefaultDecl value
         * @param attDefaultValue StringPool handle of this attribute's default value
         * @return handle to the attribute definition
         * @exception java.lang.Exception
         */
        public int addAttDef(QName elementDecl, QName attributeDecl, 
                             int attType, boolean attList, int enumeration, 
                             int attDefaultType, int attDefaultValue, boolean isExternal) throws Exception;
        /**
         * create an XMLContentSpec for a leaf
         *
         * @param nameIndex StringPool handle to the name (Element) for the node
         * @return handle to the newly create XMLContentSpec
         * @exception java.lang.Exception
         */
        public int addUniqueLeafNode(int nameIndex) throws Exception;
        /**
         * Create an XMLContentSpec for a single non-leaf
         * 
         * @param nodeType the type of XMLContentSpec to create - from XMLContentSpec.CONTENTSPECNODE_*
         * @param nodeValue handle to an XMLContentSpec
         * @return handle to the newly create XMLContentSpec
         * @exception java.lang.Exception
         */
        public int addContentSpecNode(int nodeType, int nodeValue) throws Exception;
        /**
         * Create an XMLContentSpec for a two child leaf
         *
         * @param nodeType the type of XMLContentSpec to create - from XMLContentSpec.CONTENTSPECNODE_*
         * @param leftNodeIndex handle to an XMLContentSpec
         * @param rightNodeIndex handle to an XMLContentSpec
         * @return handle to the newly create XMLContentSpec
         * @exception java.lang.Exception
         */
        public int addContentSpecNode(int nodeType, int leftNodeIndex, int rightNodeIndex) throws Exception;
        /**
         * Create a string representation of an XMLContentSpec tree
         * 
         * @param handle to an XMLContentSpec
         * @return String representation of the content spec tree
         * @exception java.lang.Exception
         */
        public String getContentSpecNodeAsString(int nodeIndex) throws Exception;
        /**
         * Start the scope of an entity declaration.
         *
         * @return <code>true</code> on success; otherwise
         *         <code>false</code> if the entity declaration is recursive.
         * @exception java.lang.Exception
         */
        public boolean startEntityDecl(boolean isPE, int entityName) throws Exception;
        /**
         * End the scope of an entity declaration.
         * @exception java.lang.Exception
         */
        public void endEntityDecl() throws Exception;
        /**
         * Add a declaration for an internal parameter entity
         *
         * @param name StringPool handle of the parameter entity name
         * @param value StringPool handle of the parameter entity value
         * @return handle to the parameter entity declaration
         * @exception java.lang.Exception
         */
        public int addInternalPEDecl(int name, int value) throws Exception;
        /**
         * Add a declaration for an external parameter entity
         *
         * @param name StringPool handle of the parameter entity name
         * @param publicId StringPool handle of the publicId
         * @param systemId StringPool handle of the systemId
         * @return handle to the parameter entity declaration
         * @exception java.lang.Exception
         */
        public int addExternalPEDecl(int name, int publicId, int systemId) throws Exception;
        /**
         * Add a declaration for an internal entity
         *
         * @param name StringPool handle of the entity name
         * @param value StringPool handle of the entity value
         * @return handle to the entity declaration
         * @exception java.lang.Exception
         */
        public int addInternalEntityDecl(int name, int value) throws Exception;
        /**
         * Add a declaration for an entity
         *
         * @param name StringPool handle of the entity name
         * @param publicId StringPool handle of the publicId
         * @param systemId StringPool handle of the systemId
         * @return handle to the entity declaration
         * @exception java.lang.Exception
         */
        public int addExternalEntityDecl(int name, int publicId, int systemId) throws Exception;
        /**
         * Add a declaration for an unparsed entity
         *
         * @param name StringPool handle of the entity name
         * @param publicId StringPool handle of the publicId
         * @param systemId StringPool handle of the systemId
         * @param notationName StringPool handle of the notationName
         * @return handle to the entity declaration
         * @exception java.lang.Exception
         */
        public int addUnparsedEntityDecl(int name, int publicId, int systemId, int notationName) throws Exception;
        /**
         * Called when the scanner start scanning an enumeration
         * @return StringPool handle to a string list that will hold the enumeration names
         * @exception java.lang.Exception
         */
        public int startEnumeration() throws Exception;
        /**
         * Add a name to an enumeration
         * @param enumIndex StringPool handle to the string list for the enumeration
         * @param elementType handle to the element that owns the attribute with the enumeration
         * @param attrName StringPool handle to the name of the attribut with the enumeration
         * @param nameIndex StringPool handle to the name to be added to the enumeration
         * @param isNotationType true if the enumeration is an enumeration of NOTATION names
         * @exception java.lang.Exception
         */
        public void addNameToEnumeration(int enumIndex, int elementType, int attrName, int nameIndex, boolean isNotationType) throws Exception;
        /**
         * Finish processing an enumeration
         *
         * @param enumIndex handle to the string list which holds the enumeration to be finshed.
         * @exception java.lang.Exception
         */
        public void endEnumeration(int enumIndex) throws Exception;
        /**
         * Add a declaration for a notation
         *
         * @param notationName
         * @param publicId
         * @param systemId
         * @return handle to the notation declaration
         * @exception java.lang.Exception
         */
        public int addNotationDecl(int notationName, int publicId, int systemId) throws Exception;
        /**
         * Called when a comment has been scanned
         *
         * @param data StringPool handle of the comment text
         * @exception java.lang.Exception
         */
        public void callComment(int data) throws Exception;
        /**
         * Called when a processing instruction has been scanned
         * @param piTarget StringPool handle of the PI target
         * @param piData StringPool handle of the PI data
         * @exception java.lang.Exception
         */
        public void callProcessingInstruction(int piTarget, int piData) throws Exception;
        /**
         * Supports DOM Level 2 internalSubset additions.
         * Called when the internal subset is completely scanned.
         */
        public void internalSubset(int internalSubset) throws Exception;
    }
    //
    //
    //
    
    /** Report a recoverable xml error. */
    protected void reportRecoverableXMLError(int majorCode, int minorCode, 
                                             int stringIndex1) 
        throws Exception {

        Object[] args = { fStringPool.toString(stringIndex1) };
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

        Object[] args = { string1 };
        fErrorReporter.reportError(fErrorReporter.getLocator(),
                                   XMLMessages.XML_DOMAIN,
                                   majorCode,
                                   minorCode,
                                   args,
                                   XMLErrorReporter.ERRORTYPE_RECOVERABLE_ERROR);

    } // reportRecoverableXMLError(int,int,String)
    
    /** Report a recoverable xml error. */
    protected void reportRecoverableXMLError(int majorCode, int minorCode, 
                                             String string1, String string2) 
        throws Exception {

        Object[] args = { string1, string2 };
        fErrorReporter.reportError(fErrorReporter.getLocator(),
                                   XMLMessages.XML_DOMAIN,
                                   majorCode,
                                   minorCode,
                                   args,
                                   XMLErrorReporter.ERRORTYPE_RECOVERABLE_ERROR);

    } // reportRecoverableXMLError(int,int,String,String)
    
 
    private void reportFatalXMLError(int majorCode, int minorCode) throws Exception {
        fErrorReporter.reportError(fErrorReporter.getLocator(),
                                   XMLMessages.XML_DOMAIN,
                                   majorCode,
                                   minorCode,
                                   null,
                                   XMLErrorReporter.ERRORTYPE_FATAL_ERROR);
    }
    private void reportFatalXMLError(int majorCode, int minorCode, int stringIndex1) throws Exception {
        Object[] args = { fStringPool.toString(stringIndex1) };
        fErrorReporter.reportError(fErrorReporter.getLocator(),
                                   XMLMessages.XML_DOMAIN,
                                   majorCode,
                                   minorCode,
                                   args,
                                   XMLErrorReporter.ERRORTYPE_FATAL_ERROR);
    }
    private void reportFatalXMLError(int majorCode, int minorCode, String string1) throws Exception {
        Object[] args = { string1 };
        fErrorReporter.reportError(fErrorReporter.getLocator(),
                                   XMLMessages.XML_DOMAIN,
                                   majorCode,
                                   minorCode,
                                   args,
                                   XMLErrorReporter.ERRORTYPE_FATAL_ERROR);
    }
    private void reportFatalXMLError(int majorCode, int minorCode, int stringIndex1, int stringIndex2) throws Exception {
        Object[] args = { fStringPool.toString(stringIndex1),
                          fStringPool.toString(stringIndex2) };
        fErrorReporter.reportError(fErrorReporter.getLocator(),
                                   XMLMessages.XML_DOMAIN,
                                   majorCode,
                                   minorCode,
                                   args,
                                   XMLErrorReporter.ERRORTYPE_FATAL_ERROR);
    }
    private void reportFatalXMLError(int majorCode, int minorCode, String string1, String string2) throws Exception {
        Object[] args = { string1, string2 };
        fErrorReporter.reportError(fErrorReporter.getLocator(),
                                   XMLMessages.XML_DOMAIN,
                                   majorCode,
                                   minorCode,
                                   args,
                                   XMLErrorReporter.ERRORTYPE_FATAL_ERROR);
    }
    private void reportFatalXMLError(int majorCode, int minorCode, String string1, String string2, String string3) throws Exception {
        Object[] args = { string1, string2, string3 };
        fErrorReporter.reportError(fErrorReporter.getLocator(),
                                   XMLMessages.XML_DOMAIN,
                                   majorCode,
                                   minorCode,
                                   args,
                                   XMLErrorReporter.ERRORTYPE_FATAL_ERROR);
    }
    private void abortMarkup(int majorCode, int minorCode) throws Exception {
        reportFatalXMLError(majorCode, minorCode);
        skipPastEndOfCurrentMarkup();
    }
    private void abortMarkup(int majorCode, int minorCode, int stringIndex1) throws Exception {
        reportFatalXMLError(majorCode, minorCode, stringIndex1);
        skipPastEndOfCurrentMarkup();
    }
    private void abortMarkup(int majorCode, int minorCode, String string1) throws Exception {
        reportFatalXMLError(majorCode, minorCode, string1);
        skipPastEndOfCurrentMarkup();
    }
    private void abortMarkup(int majorCode, int minorCode, int stringIndex1, int stringIndex2) throws Exception {
        reportFatalXMLError(majorCode, minorCode, stringIndex1, stringIndex2);
        skipPastEndOfCurrentMarkup();
    }
    private void skipPastEndOfCurrentMarkup() throws Exception {
        fEntityReader.skipToChar('>');
        if (fEntityReader.lookingAtChar('>', true))
            decreaseMarkupDepth();
    }
    //
    //
    //
    static private final int SCANNER_STATE_INVALID = -1;
    static private final int SCANNER_STATE_END_OF_INPUT = 0;
    static private final int SCANNER_STATE_DOCTYPEDECL = 50;
    static private final int SCANNER_STATE_MARKUP_DECL = 51;
    static private final int SCANNER_STATE_TEXTDECL = 53;
    static private final int SCANNER_STATE_COMMENT = 54;
    static private final int SCANNER_STATE_PI = 55;
    static private final int SCANNER_STATE_DEFAULT_ATTRIBUTE_VALUE = 56;
    static private final int SCANNER_STATE_CONTENTSPEC = 57;
    static private final int SCANNER_STATE_ENTITY_VALUE = 58;
    static private final int SCANNER_STATE_SYSTEMLITERAL = 59;
    static private final int SCANNER_STATE_PUBIDLITERAL = 60;

    private int setScannerState(int scannerState) {
        int prevState = fScannerState;
        fScannerState = scannerState;
        return prevState;
    }
    private int getScannerState() {
        return fScannerState;
    }
    private void restoreScannerState(int scannerState) {
        if (fScannerState != SCANNER_STATE_END_OF_INPUT)
            fScannerState = scannerState;
    }
    /**
     * Change readers
     *
     * @param nextReader the new reader that the scanner will use
     * @param nextReaderId id of the reader to change to
     * @exception throws java.lang.Exception
     */
    public void readerChange(XMLEntityHandler.EntityReader nextReader, int nextReaderId) throws Exception {
        fEntityReader = nextReader;
        fReaderId = nextReaderId;
        if (fScannerState == SCANNER_STATE_DEFAULT_ATTRIBUTE_VALUE) {
            fDefaultAttValueOffset = fEntityReader.currentOffset();
            fDefaultAttValueMark = fDefaultAttValueOffset;
        } else if (fScannerState == SCANNER_STATE_ENTITY_VALUE) {
            fEntityValueMark = fEntityReader.currentOffset();
        }
    }
    /**
     * Handle the end of input
     *
     * @param entityName the handle in the string pool of the name of the entity which has reached end of input
     * @param moreToFollow if true, there is still input left to process in other readers
     * @exception java.lang.Exception
     */
    public void endOfInput(int entityNameIndex, boolean moreToFollow) throws Exception {
        if (fValidationEnabled ) {
            int readerDepth = fEntityHandler.getReaderDepth();
            if (getReadingContentSpec()) {
                int parenDepth = parenDepth();
                if (readerDepth != parenDepth) {
                    reportRecoverableXMLError(XMLMessages.MSG_IMPROPER_GROUP_NESTING,
                                                XMLMessages.VC_PROPER_GROUP_PE_NESTING,
                                                entityNameIndex);
                }
            } else {
                int markupDepth = markupDepth();
                if (readerDepth != markupDepth) {
                    reportRecoverableXMLError(XMLMessages.MSG_IMPROPER_DECLARATION_NESTING,
                                                XMLMessages.VC_PROPER_DECLARATION_PE_NESTING,
                                                entityNameIndex);
                }
            }
        }
        //REVISIT, why are we doing this?
        moreToFollow = fReaderId != fExternalSubsetReader;

//      System.out.println("current Scanner state " + getScannerState() +","+ fScannerState + moreToFollow);
        switch (fScannerState) {
        case SCANNER_STATE_INVALID:
            throw new RuntimeException("FWK004 XMLDTDScanner.endOfInput: cannot happen: 2"+"\n2");
        case SCANNER_STATE_END_OF_INPUT:
            break;
        case SCANNER_STATE_MARKUP_DECL:
            if (!moreToFollow && fIncludeSectDepth > 0) {
                reportFatalXMLError(XMLMessages.MSG_INCLUDESECT_UNTERMINATED,
                                    XMLMessages.P62_UNTERMINATED);
            }
            break;
        case SCANNER_STATE_DOCTYPEDECL:
            throw new RuntimeException("FWK004 XMLDTDScanner.endOfInput: cannot happen: 2.5"+"\n2.5");
//            break;
        case SCANNER_STATE_TEXTDECL:
// REVISIT            reportFatalXMLError(XMLMessages.MSG_ATTVAL0);
            break;
        case SCANNER_STATE_SYSTEMLITERAL:
            if (!moreToFollow) {
                reportFatalXMLError(XMLMessages.MSG_SYSTEMID_UNTERMINATED,
                                    XMLMessages.P11_UNTERMINATED);
            } else {
// REVISIT                reportFatalXMLError(XMLMessages.MSG_ATTVAL0);
            }
            break;
        case SCANNER_STATE_PUBIDLITERAL:
            if (!moreToFollow) {
                reportFatalXMLError(XMLMessages.MSG_PUBLICID_UNTERMINATED,
                                    XMLMessages.P12_UNTERMINATED);
            } else {
// REVISIT                reportFatalXMLError(XMLMessages.MSG_ATTVAL0);
            }
            break;
        case SCANNER_STATE_COMMENT:
            if (!moreToFollow && !getReadingExternalEntity()) {
                reportFatalXMLError(XMLMessages.MSG_COMMENT_UNTERMINATED,
                                    XMLMessages.P15_UNTERMINATED);
            } else {
                //
                // REVISIT - HACK !!!  code changed to pass incorrect OASIS test 'invalid--001'
                //  Uncomment the next line to conform to the spec...
                //
                //reportFatalXMLError(XMLMessages.MSG_COMMENT_NOT_IN_ONE_ENTITY,
                //                    XMLMessages.P78_NOT_WELLFORMED);
            }
            break;
        case SCANNER_STATE_PI:
            if (!moreToFollow) {
                reportFatalXMLError(XMLMessages.MSG_PI_UNTERMINATED,
                                    XMLMessages.P16_UNTERMINATED);
            } else {
                reportFatalXMLError(XMLMessages.MSG_PI_NOT_IN_ONE_ENTITY,
                                    XMLMessages.P78_NOT_WELLFORMED);
            }
            break;
        case SCANNER_STATE_DEFAULT_ATTRIBUTE_VALUE:
            if (!moreToFollow) {
                reportFatalXMLError(XMLMessages.MSG_ATTRIBUTE_VALUE_UNTERMINATED,
                                    XMLMessages.P10_UNTERMINATED,
                                    fDefaultAttValueElementType,
                                    fDefaultAttValueAttrName);
            } else if (fReaderId == fDefaultAttValueReader) {
// REVISIT                reportFatalXMLError(XMLMessages.MSG_ATTVAL0);
            } else {
                fEntityReader.append(fLiteralData, fDefaultAttValueMark, fDefaultAttValueOffset - fDefaultAttValueMark);
            }
            break;
        case SCANNER_STATE_CONTENTSPEC:
            break;
        case SCANNER_STATE_ENTITY_VALUE:
            if (fReaderId == fEntityValueReader) {
// REVISIT                reportFatalXMLError(XMLMessages.MSG_ATTVAL0);
            } else {
                fEntityReader.append(fLiteralData, fEntityValueMark, fEntityReader.currentOffset() - fEntityValueMark);
            }
            break;
        default:
            throw new RuntimeException("FWK004 XMLDTDScanner.endOfInput: cannot happen: 3"+"\n3");
        }
        if (!moreToFollow) {
            setScannerState(SCANNER_STATE_END_OF_INPUT);
        }
    }
    //
    // [66] CharRef ::= '&#' [0-9]+ ';' | '&#x' [0-9a-fA-F]+ ';'
    //
    private int scanCharRef() throws Exception {
        int valueOffset = fEntityReader.currentOffset();
        boolean hex = fEntityReader.lookingAtChar('x', true);
        int num = fEntityReader.scanCharRef(hex);
        if (num < 0) {
            switch (num) {
            case XMLEntityHandler.CHARREF_RESULT_SEMICOLON_REQUIRED:
                reportFatalXMLError(XMLMessages.MSG_SEMICOLON_REQUIRED_IN_CHARREF,
                                    XMLMessages.P66_SEMICOLON_REQUIRED);
                return -1;
            case XMLEntityHandler.CHARREF_RESULT_INVALID_CHAR:
                int majorCode = hex ? XMLMessages.MSG_HEXDIGIT_REQUIRED_IN_CHARREF :
                                      XMLMessages.MSG_DIGIT_REQUIRED_IN_CHARREF;
                int minorCode = hex ? XMLMessages.P66_HEXDIGIT_REQUIRED :
                                      XMLMessages.P66_DIGIT_REQUIRED;
                reportFatalXMLError(majorCode, minorCode);
                return -1;
            case XMLEntityHandler.CHARREF_RESULT_OUT_OF_RANGE:
                num = 0x110000; // this will cause the right error to be reported below...
                break;
            }
        }
        //
        //  [2] Char ::= #x9 | #xA | #xD | [#x20-#xD7FF]        // any Unicode character, excluding the
        //               | [#xE000-#xFFFD] | [#x10000-#x10FFFF] // surrogate blocks, FFFE, and FFFF.
        //
        if (num < 0x20) {
            if (num == 0x09 || num == 0x0A || num == 0x0D) {
                return num;
            }
        } else if (num <= 0xD7FF || (num >= 0xE000 && (num <= 0xFFFD || (num >= 0x10000 && num <= 0x10FFFF)))) {
            return num;
        }
        int valueLength = fEntityReader.currentOffset() - valueOffset;
        reportFatalXMLError(XMLMessages.MSG_INVALID_CHARREF,
                            XMLMessages.WFC_LEGAL_CHARACTER,
                            fEntityReader.addString(valueOffset, valueLength));
        return -1;
    }
    //
    // From the standard:
    //
    // [15] Comment ::= '<!--' ((Char - '-') | ('-' (Char - '-')))* '-->'
    //
    // Called after scanning past '<!--'
    //
    private void scanComment() throws Exception
    {
        int commentOffset = fEntityReader.currentOffset();
        boolean sawDashDash = false;
        int previousState = setScannerState(SCANNER_STATE_COMMENT);
        while (fScannerState == SCANNER_STATE_COMMENT) {
            if (fEntityReader.lookingAtChar('-', false)) {
                int nextEndOffset = fEntityReader.currentOffset();
                int endOffset = 0;
                fEntityReader.lookingAtChar('-', true);
                int offset = fEntityReader.currentOffset();
                int count = 1;
                while (fEntityReader.lookingAtChar('-', true)) {
                    count++;
                    endOffset = nextEndOffset;
                    nextEndOffset = offset;
                    offset = fEntityReader.currentOffset();
                }
                if (count > 1) {
                    if (fEntityReader.lookingAtChar('>', true)) {
                        if (!sawDashDash && count > 2) {
                            reportFatalXMLError(XMLMessages.MSG_DASH_DASH_IN_COMMENT,
                                                XMLMessages.P15_DASH_DASH);
                            sawDashDash = true;
                        }
                        decreaseMarkupDepth();
                        int comment = fEntityReader.addString(commentOffset, endOffset - commentOffset);
                        fDTDGrammar.callComment(comment);
                        if (fDTDHandler != null) {
                            fDTDHandler.comment(comment);
                        }
                        restoreScannerState(previousState);
                        return;
                    } else if (!sawDashDash) {
                        reportFatalXMLError(XMLMessages.MSG_DASH_DASH_IN_COMMENT,
                                            XMLMessages.P15_DASH_DASH);
                        sawDashDash = true;
                    }
                }
            } else {
                if (!fEntityReader.lookingAtValidChar(true)) {
                    int invChar = fEntityReader.scanInvalidChar();
                    if (fScannerState != SCANNER_STATE_END_OF_INPUT) {
                        if (invChar >= 0) {
                            reportFatalXMLError(XMLMessages.MSG_INVALID_CHAR_IN_COMMENT,
                                                XMLMessages.P15_INVALID_CHARACTER,
                                                Integer.toHexString(invChar));
                        }
                    }
                }
            }
        }
        restoreScannerState(previousState);
    }
    //
    // From the standard:
    //
    // [16] PI ::= '<?' PITarget (S (Char* - (Char* '?>' Char*)))? '?>'
    // [17] PITarget ::= Name - (('X' | 'x') ('M' | 'm') ('L' | 'l'))
    //
    private void scanPI(int piTarget) throws Exception
    {
        String piTargetString = fStringPool.toString(piTarget);
        if (piTargetString.length() == 3 &&
            (piTargetString.charAt(0) == 'X' || piTargetString.charAt(0) == 'x') &&
            (piTargetString.charAt(1) == 'M' || piTargetString.charAt(1) == 'm') &&
            (piTargetString.charAt(2) == 'L' || piTargetString.charAt(2) == 'l')) {
            abortMarkup(XMLMessages.MSG_RESERVED_PITARGET,
                        XMLMessages.P17_RESERVED_PITARGET);
            return;
        }
        int prevState = setScannerState(SCANNER_STATE_PI);
        int piDataOffset = -1;
        int piDataLength = 0;
        if (!fEntityReader.lookingAtSpace(true)) {
            if (!fEntityReader.lookingAtChar('?', true) || !fEntityReader.lookingAtChar('>', true)) {
                if (fScannerState != SCANNER_STATE_END_OF_INPUT) {
                    abortMarkup(XMLMessages.MSG_SPACE_REQUIRED_IN_PI,
                                XMLMessages.P16_WHITESPACE_REQUIRED);
                    restoreScannerState(prevState);
                }
                return;
            }
            decreaseMarkupDepth();
            restoreScannerState(prevState);
        } else {
            fEntityReader.skipPastSpaces();
            piDataOffset = fEntityReader.currentOffset();
            while (fScannerState == SCANNER_STATE_PI) {
                while (fEntityReader.lookingAtChar('?', false)) {
                    int offset = fEntityReader.currentOffset();
                    fEntityReader.lookingAtChar('?', true);
                    if (fEntityReader.lookingAtChar('>', true)) {
                        piDataLength = offset - piDataOffset;
                        decreaseMarkupDepth();
                        restoreScannerState(prevState);
                        break;
                    }
                }
                if (fScannerState != SCANNER_STATE_PI)
                    break;
                if (!fEntityReader.lookingAtValidChar(true)) {
                    int invChar = fEntityReader.scanInvalidChar();
                    if (fScannerState != SCANNER_STATE_END_OF_INPUT) {
                        if (invChar >= 0) {
                            reportFatalXMLError(XMLMessages.MSG_INVALID_CHAR_IN_PI,
                                                XMLMessages.P16_INVALID_CHARACTER,
                                                Integer.toHexString(invChar));
                        }
                        skipPastEndOfCurrentMarkup();
                        restoreScannerState(prevState);
                    }
                    return;
                }
            }
        }
        int piData = piDataLength == 0 ?
                     StringPool.EMPTY_STRING : fEntityReader.addString(piDataOffset, piDataLength);
        fDTDGrammar.callProcessingInstruction(piTarget, piData);
        if (fDTDHandler != null) {
            fDTDHandler.processingInstruction(piTarget, piData);
        }
    }
    //
    // From the standard:
    //
    // [28] doctypedecl ::= '<!DOCTYPE' S Name (S ExternalID)? S?
    //                      ('[' (markupdecl | PEReference | S)* ']' S?)? '>'
    // [29] markupdecl ::= elementdecl | AttlistDecl | EntityDecl
    //                     | NotationDecl | PI | Comment
    //
    // Called after scanning '<!DOCTYPE'
    //
    /**
     * This routine is called after the &lt;!DOCTYPE portion of a DOCTYPE
     * line has been called.  scanDocTypeDecl goes onto scan the rest of the DOCTYPE
     * decl.  If an internal DTD subset exists, it is scanned. If an external DTD
     * subset exists, scanDocTypeDecl sets up the state necessary to process it.
     *
     * @return true if successful
     * @exception java.lang.Exception
     */
    public boolean scanDoctypeDecl() throws Exception
    {
        //System.out.println("XMLDTDScanner#scanDoctypeDecl()");

        fDTDGrammar = new DTDGrammar(fStringPool);
        fDTDGrammar.callStartDTD();
        increaseMarkupDepth();
        fEntityReader = fEntityHandler.getEntityReader();
        fReaderId = fEntityHandler.getReaderId();
        fDoctypeReader = fReaderId;
        setScannerState(SCANNER_STATE_DOCTYPEDECL);
        if (!fEntityReader.lookingAtSpace(true)) {
            abortMarkup(XMLMessages.MSG_SPACE_REQUIRED_BEFORE_ROOT_ELEMENT_TYPE_IN_DOCTYPEDECL,
                        XMLMessages.P28_SPACE_REQUIRED);
            return false;
        }
        fEntityReader.skipPastSpaces();
        scanElementType(fEntityReader, ' ', fElementQName);
        if (fElementQName.rawname == -1) {
            abortMarkup(XMLMessages.MSG_ROOT_ELEMENT_TYPE_REQUIRED,
                        XMLMessages.P28_ROOT_ELEMENT_TYPE_REQUIRED);
            return false;
        }
        boolean lbrkt;
        boolean scanExternalSubset = false;
        int publicId = -1;
        int systemId = -1;
        if (fEntityReader.lookingAtSpace(true)) {
            fEntityReader.skipPastSpaces();
            if (!(lbrkt = fEntityReader.lookingAtChar('[', true)) && !fEntityReader.lookingAtChar('>', false)) {
                if (!scanExternalID(false)) {
                    skipPastEndOfCurrentMarkup();
                    return false;
                }
                if (fValidationEnabled || fLoadExternalDTD) {
                    scanExternalSubset = true;
                }
                publicId = fPubidLiteral;
                systemId = fSystemLiteral;
                fEntityReader.skipPastSpaces();
                lbrkt = fEntityReader.lookingAtChar('[', true);
            }
        } else
            lbrkt = fEntityReader.lookingAtChar('[', true);
        fDTDGrammar.doctypeDecl(fElementQName, publicId, systemId);
        if (fDTDHandler != null) {
            fDTDHandler.startDTD(fElementQName, publicId, systemId);
        }
        if (lbrkt) {
            scanDecls(false);
            fEntityReader.skipPastSpaces();
        }
        if (!fEntityReader.lookingAtChar('>', true)) {
            if (fScannerState != SCANNER_STATE_END_OF_INPUT) {
                abortMarkup(XMLMessages.MSG_DOCTYPEDECL_UNTERMINATED,
                            XMLMessages.P28_UNTERMINATED,
                            fElementQName.rawname);
            }
            return false;
        }

        decreaseMarkupDepth();

        //System.out.println("  scanExternalSubset: "+scanExternalSubset);
        if (scanExternalSubset) {
            ((DefaultEntityHandler) fEntityHandler).startReadingFromExternalSubset( fStringPool.toString(publicId),
                                                                                    fStringPool.toString(systemId),
                                                                                    markupDepth());
            fDTDGrammar.startReadingFromExternalSubset(publicId, systemId);
        }
        else {
            fDTDGrammar.callEndDTD();
            if (fDTDHandler != null) {
                fDTDHandler.endDTD();
            }
        }

        fGrammarResolver.putGrammar("", fDTDGrammar);


        return true;
    }
    //
    // [75] ExternalID ::= 'SYSTEM' S SystemLiteral
    //                     | 'PUBLIC' S PubidLiteral S SystemLiteral
    // [83] PublicID ::= 'PUBLIC' S PubidLiteral
    //
    private boolean scanExternalID(boolean scanPublicID) throws Exception
    {
        fSystemLiteral = -1;
        fPubidLiteral = -1;
        int offset = fEntityReader.currentOffset();
        if (fEntityReader.skippedString(system_string)) {
            if (!fEntityReader.lookingAtSpace(true)) {
                reportFatalXMLError(XMLMessages.MSG_SPACE_REQUIRED_BEFORE_SYSTEMLITERAL_IN_EXTERNALID,
                                    XMLMessages.P75_SPACE_REQUIRED);
                return false;
            }
            fEntityReader.skipPastSpaces();
            if( getReadingExternalEntity() == true ) {  //Are we in external subset?
               checkForPEReference(false);//If so Check for PE Ref
             }
            return scanSystemLiteral();
        }
        if (fEntityReader.skippedString(public_string)) {
            if (!fEntityReader.lookingAtSpace(true)) {
                reportFatalXMLError(XMLMessages.MSG_SPACE_REQUIRED_BEFORE_PUBIDLITERAL_IN_EXTERNALID,
                                    XMLMessages.P75_SPACE_REQUIRED);
                return false;
            }
            fEntityReader.skipPastSpaces();
            if (!scanPubidLiteral())
                return false;
            if (scanPublicID) {
                //
                // [82] NotationDecl ::= '<!NOTATION' S Name S (ExternalID |  PublicID) S? '>'
                //
                if (!fEntityReader.lookingAtSpace(true))
                    return true; // no S, not an ExternalID
                fEntityReader.skipPastSpaces();
                if (fEntityReader.lookingAtChar('>', false)) // matches end of NotationDecl
                    return true;
            } else {
                if (!fEntityReader.lookingAtSpace(true)) {
                    reportFatalXMLError(XMLMessages.MSG_SPACE_REQUIRED_AFTER_PUBIDLITERAL_IN_EXTERNALID,
                                        XMLMessages.P75_SPACE_REQUIRED);
                    return false;
                }
                fEntityReader.skipPastSpaces();
            }
            return scanSystemLiteral();
        }
        reportFatalXMLError(XMLMessages.MSG_EXTERNALID_REQUIRED,
                            XMLMessages.P75_INVALID);
        return false;
    }
    //
    // [11] SystemLiteral ::= ('"' [^"]* '"') | ("'" [^']* "'")
    //
    // REVISIT - need to look into uri escape mechanism for non-ascii characters.
    //
    private boolean scanSystemLiteral() throws Exception
    {
        boolean single;
        if (!(single = fEntityReader.lookingAtChar('\'', true)) && !fEntityReader.lookingAtChar('\"', true)) {
            reportFatalXMLError(XMLMessages.MSG_QUOTE_REQUIRED_IN_SYSTEMID,
                                XMLMessages.P11_QUOTE_REQUIRED);
            return false;
        }
        int prevState = setScannerState(SCANNER_STATE_SYSTEMLITERAL);
        int offset = fEntityReader.currentOffset();
        char qchar = single ? '\'' : '\"';
        boolean dataok = true;
        boolean fragment = false;
        while (!fEntityReader.lookingAtChar(qchar, false)) {
//ericye
//System.out.println("XMLDTDScanner#scanDoctypeDecl() 3333333, "+fReaderId+", " + fScannerState+", " +fExternalSubsetReader);
            if (fEntityReader.lookingAtChar('#', true)) {
                fragment = true;
            } else if (!fEntityReader.lookingAtValidChar(true)) {
//System.out.println("XMLDTDScanner#scanDoctypeDecl() 555555 scan state: " + fScannerState);
                dataok = false;
                int invChar = fEntityReader.scanInvalidChar();
                if (fScannerState == SCANNER_STATE_END_OF_INPUT)
                    return false;
                if (invChar >= 0) {
                    reportFatalXMLError(XMLMessages.MSG_INVALID_CHAR_IN_SYSTEMID,
                                        XMLMessages.P11_INVALID_CHARACTER,
                                        Integer.toHexString(invChar));
                }
            }
        }
        if (dataok) {
            fSystemLiteral = fEntityReader.addString(offset, fEntityReader.currentOffset() - offset);
            if (fragment) {
                // NOTE: RECOVERABLE ERROR
                Object[] args = { fStringPool.toString(fSystemLiteral) };
                fErrorReporter.reportError(fErrorReporter.getLocator(),
                                           XMLMessages.XML_DOMAIN,
                                           XMLMessages.MSG_URI_FRAGMENT_IN_SYSTEMID,
                                           XMLMessages.P11_URI_FRAGMENT,
                                           args,
                                           XMLErrorReporter.ERRORTYPE_RECOVERABLE_ERROR);
            }
        }
        fEntityReader.lookingAtChar(qchar, true);
        restoreScannerState(prevState);
        return dataok;
    }
    //
    // [12] PubidLiteral ::= '"' PubidChar* '"' | "'" (PubidChar - "'")* "'"
    // [13] PubidChar ::= #x20 | #xD | #xA | [a-zA-Z0-9] | [-'()+,./:=?;!*#@$_%]
    //
    private boolean scanPubidLiteral() throws Exception
    {
        boolean single;
        if (!(single = fEntityReader.lookingAtChar('\'', true)) && !fEntityReader.lookingAtChar('\"', true)) {
            reportFatalXMLError(XMLMessages.MSG_QUOTE_REQUIRED_IN_PUBLICID,
                                XMLMessages.P12_QUOTE_REQUIRED);
            return false;
        }
        char qchar = single ? '\'' : '\"';
        int prevState = setScannerState(SCANNER_STATE_PUBIDLITERAL);
        boolean dataok = true;
        while (true) {
            if (fEntityReader.lookingAtChar((char)0x09, true)) {
                dataok = false;
                reportFatalXMLError(XMLMessages.MSG_PUBIDCHAR_ILLEGAL,
                                    XMLMessages.P12_INVALID_CHARACTER, "9");
            }
            if (!fEntityReader.lookingAtSpace(true))
                break;
        }
        int offset = fEntityReader.currentOffset();
        int dataOffset = fLiteralData.length();
        int toCopy = offset;
        while (true) {
            if (fEntityReader.lookingAtChar(qchar, true)) {
                if (dataok && offset - toCopy > 0)
                    fEntityReader.append(fLiteralData, toCopy, offset - toCopy);
                break;
            }
            if (fEntityReader.lookingAtChar((char)0x09, true)) {
                dataok = false;
                reportFatalXMLError(XMLMessages.MSG_PUBIDCHAR_ILLEGAL,
                                    XMLMessages.P12_INVALID_CHARACTER, "9");
                continue;
            }
            if (fEntityReader.lookingAtSpace(true)) {
                if (dataok && offset - toCopy > 0)
                    fEntityReader.append(fLiteralData, toCopy, offset - toCopy);
                while (true) {
                    if (fEntityReader.lookingAtChar((char)0x09, true)) {
                        dataok = false;
                        reportFatalXMLError(XMLMessages.MSG_PUBIDCHAR_ILLEGAL,
                                            XMLMessages.P12_INVALID_CHARACTER, "9");
                        break;
                    } else if (!fEntityReader.lookingAtSpace(true)) {
                        break;
                    }
                }
                if (fEntityReader.lookingAtChar(qchar, true))
                    break;
                if (dataok) {
                    fLiteralData.append(' ');
                    offset = fEntityReader.currentOffset();
                    toCopy = offset;
                }
                continue;
            }
            if (!fEntityReader.lookingAtValidChar(true)) {
                int invChar = fEntityReader.scanInvalidChar();
                if (fScannerState == SCANNER_STATE_END_OF_INPUT)
                    return false;
                dataok = false;
                if (invChar >= 0) {
                    reportFatalXMLError(XMLMessages.MSG_INVALID_CHAR_IN_PUBLICID,
                                        XMLMessages.P12_INVALID_CHARACTER,
                                        Integer.toHexString(invChar));
                }
            }
            if (dataok)
                offset = fEntityReader.currentOffset();
        }
        if (dataok) {
            int dataLength = fLiteralData.length() - dataOffset;
            fPubidLiteral = fLiteralData.addString(dataOffset, dataLength);
            String publicId = fStringPool.toString(fPubidLiteral);
            int invCharIndex = validPublicId(publicId);
            if (invCharIndex >= 0) {
                reportFatalXMLError(XMLMessages.MSG_PUBIDCHAR_ILLEGAL,
                                    XMLMessages.P12_INVALID_CHARACTER,
                                    Integer.toHexString(publicId.charAt(invCharIndex)));
                return false;
            }
        }
        restoreScannerState(prevState);
        return dataok;
    }
    //
    // [??] intSubsetDecl = '[' (markupdecl | PEReference | S)* ']'
    //
    // [31] extSubsetDecl ::= ( markupdecl | conditionalSect | PEReference | S )*
    // [62] includeSect ::= '<![' S? 'INCLUDE' S? '[' extSubsetDecl ']]>'
    //
    // [29] markupdecl ::= elementdecl | AttlistDecl | EntityDecl
    //                     | NotationDecl | PI | Comment
    //
    // [45] elementdecl ::= '<!ELEMENT' S Name S contentspec S? '>'
    //
    // [52] AttlistDecl ::= '<!ATTLIST' S Name AttDef* S? '>'
    //
    // [70] EntityDecl ::= GEDecl | PEDecl
    // [71] GEDecl ::= '<!ENTITY' S Name S EntityDef S? '>'
    // [72] PEDecl ::= '<!ENTITY' S '%' S Name S PEDef S? '>'
    //
    // [82] NotationDecl ::= '<!NOTATION' S Name S (ExternalID |  PublicID) S? '>'
    //
    // [16] PI ::= '<?' PITarget (S (Char* - (Char* '?>' Char*)))? '?>'
    //
    // [15] Comment ::= '<!--' ((Char - '-') | ('-' (Char - '-')))* '-->'
    //
    // [61] conditionalSect ::= includeSect | ignoreSect
    // [62] includeSect ::= '<![' S? 'INCLUDE' S? '[' extSubsetDecl ']]>'
    // [63] ignoreSect ::= '<![' S? 'IGNORE' S? '[' ignoreSectContents* ']]>'
    // [64] ignoreSectContents ::= Ignore ('<![' ignoreSectContents ']]>' Ignore)*
    // [65] Ignore ::= Char* - (Char* ('<![' | ']]>') Char*)
    //
    /**
     * Scan markup declarations
     *
     * @param extSubset true if the scanner is scanning an external subset, false
     *                  if it is scanning an internal subset
     * @exception java.lang.Exception
     */
    public void scanDecls(boolean extSubset) throws Exception
    {
        int subsetOffset = fEntityReader.currentOffset();
        if (extSubset)
            fExternalSubsetReader = fReaderId;
        fIncludeSectDepth = 0;
        boolean parseTextDecl = extSubset;
        int prevState = setScannerState(SCANNER_STATE_MARKUP_DECL);
        while (fScannerState == SCANNER_STATE_MARKUP_DECL) {

            boolean newParseTextDecl = false;
            if (fEntityReader.lookingAtChar(']', false) &&
                !getReadingExternalEntity()) {
                int subsetLength = fEntityReader.currentOffset() - subsetOffset;
                int internalSubset = fEntityReader.addString(subsetOffset, subsetLength);
                fDTDGrammar.internalSubset(internalSubset);
                if (fDTDHandler != null) {
                    fDTDHandler.internalSubset(internalSubset);
                }
                fEntityReader.lookingAtChar(']', true);
                restoreScannerState(prevState);
                return;
            }
            if (fEntityReader.lookingAtChar('<', true)) {
                int olddepth = markupDepth();
                increaseMarkupDepth();
                if (fEntityReader.lookingAtChar('!', true)) {
                    if (fEntityReader.lookingAtChar('-', true)) {
                        if (fEntityReader.lookingAtChar('-', true)) {
                            scanComment();
                        } else {
                            abortMarkup(XMLMessages.MSG_MARKUP_NOT_RECOGNIZED_IN_DTD,
                                        XMLMessages.P29_NOT_RECOGNIZED);
                        }
                    } else if (fEntityReader.lookingAtChar('[', true) && getReadingExternalEntity()) {
                        checkForPEReference(false);
                        if (fEntityReader.skippedString(include_string)) {
                            checkForPEReference(false);
                            if (!fEntityReader.lookingAtChar('[', true)) {
                                abortMarkup(XMLMessages.MSG_MARKUP_NOT_RECOGNIZED_IN_DTD,
                                            XMLMessages.P29_NOT_RECOGNIZED);
                            } else {
                                fIncludeSectDepth++;
                            }
                        } else if (fEntityReader.skippedString(ignore_string)) {
                            checkForPEReference(false);
                            if (!fEntityReader.lookingAtChar('[', true)) {
                                abortMarkup(XMLMessages.MSG_MARKUP_NOT_RECOGNIZED_IN_DTD,
                                            XMLMessages.P29_NOT_RECOGNIZED);
                            } else
                                scanIgnoreSectContents();
                        } else {
                            abortMarkup(XMLMessages.MSG_MARKUP_NOT_RECOGNIZED_IN_DTD,
                                        XMLMessages.P29_NOT_RECOGNIZED);
                        }
                    } else if (fEntityReader.skippedString(element_string)) {
                        scanElementDecl();
                    }
                    else if (fEntityReader.skippedString(attlist_string))
                        scanAttlistDecl();
                    else if (fEntityReader.skippedString(entity_string))
                        scanEntityDecl();
                    else if (fEntityReader.skippedString(notation_string))
                        scanNotationDecl();
                    else {
                        abortMarkup(XMLMessages.MSG_MARKUP_NOT_RECOGNIZED_IN_DTD,
                                    XMLMessages.P29_NOT_RECOGNIZED);
                    }
                } else if (fEntityReader.lookingAtChar('?', true)) {
                    int piTarget = fEntityReader.scanName(' ');
                    if (piTarget == -1) {
                        abortMarkup(XMLMessages.MSG_PITARGET_REQUIRED,
                                    XMLMessages.P16_REQUIRED);
                    } else if ("xml".equals(fStringPool.toString(piTarget))) {
                        if (fEntityReader.lookingAtSpace(true)) {
                            if (parseTextDecl) { // a TextDecl looks like a PI with the target 'xml'
                                scanTextDecl();
                            } else {
                                abortMarkup(XMLMessages.MSG_TEXTDECL_MUST_BE_FIRST,
                                            XMLMessages.P30_TEXTDECL_MUST_BE_FIRST);
                            }
                        } else { // a PI target matching 'xml'
                            abortMarkup(XMLMessages.MSG_RESERVED_PITARGET,
                                        XMLMessages.P17_RESERVED_PITARGET);
                        }
                    } else // PI
                        scanPI(piTarget);
                } else {
                    abortMarkup(XMLMessages.MSG_MARKUP_NOT_RECOGNIZED_IN_DTD,
                                XMLMessages.P29_NOT_RECOGNIZED);
                }
            } else if (fEntityReader.lookingAtSpace(true)) {
                fEntityReader.skipPastSpaces();
            } else if (fEntityReader.lookingAtChar('%', true)) {
                //
                // [69] PEReference ::= '%' Name ';'
                //
                int nameOffset = fEntityReader.currentOffset();
                fEntityReader.skipPastName(';');
                int nameLength = fEntityReader.currentOffset() - nameOffset;
                if (nameLength == 0) {
                    reportFatalXMLError(XMLMessages.MSG_NAME_REQUIRED_IN_PEREFERENCE,
                                        XMLMessages.P69_NAME_REQUIRED);
                } else if (!fEntityReader.lookingAtChar(';', true)) {
                    reportFatalXMLError(XMLMessages.MSG_SEMICOLON_REQUIRED_IN_PEREFERENCE,
                                        XMLMessages.P69_SEMICOLON_REQUIRED,
                                        fEntityReader.addString(nameOffset, nameLength));
                } else {
                    int peNameIndex = fEntityReader.addSymbol(nameOffset, nameLength);
                    newParseTextDecl = fEntityHandler.startReadingFromEntity(peNameIndex, markupDepth(), XMLEntityHandler.ENTITYREF_IN_DTD_AS_MARKUP);
                }
            } else if (fIncludeSectDepth > 0 && fEntityReader.lookingAtChar(']', true)) {
                if (!fEntityReader.lookingAtChar(']', true) || !fEntityReader.lookingAtChar('>', true)) {
                    abortMarkup(XMLMessages.MSG_INCLUDESECT_UNTERMINATED,
                                XMLMessages.P62_UNTERMINATED);
                } else
                    decreaseMarkupDepth();
                fIncludeSectDepth--;
            } else {
                if (!fEntityReader.lookingAtValidChar(false)) {
                    int invChar = fEntityReader.scanInvalidChar();
                    if (fScannerState == SCANNER_STATE_END_OF_INPUT)
                        break;
                    if (invChar >= 0) {
                        if (!extSubset) {
                            reportFatalXMLError(XMLMessages.MSG_INVALID_CHAR_IN_INTERNAL_SUBSET,
                                                XMLMessages.P28_INVALID_CHARACTER,
                                                Integer.toHexString(invChar));
                        } else {
                            reportFatalXMLError(XMLMessages.MSG_INVALID_CHAR_IN_EXTERNAL_SUBSET,
                                                XMLMessages.P30_INVALID_CHARACTER,
                                                Integer.toHexString(invChar));
                        }
                    }
                } else {
                    reportFatalXMLError(XMLMessages.MSG_MARKUP_NOT_RECOGNIZED_IN_DTD,
                                        XMLMessages.P29_NOT_RECOGNIZED);
                    fEntityReader.lookingAtValidChar(true);
                }
            }
            parseTextDecl = newParseTextDecl;
        }
        if (extSubset) {

            ((DefaultEntityHandler) fEntityHandler).stopReadingFromExternalSubset();

            fDTDGrammar.stopReadingFromExternalSubset();
            fDTDGrammar.callEndDTD();
            if (fDTDHandler != null) {
                fDTDHandler.endDTD();
            }
            // REVISIT: What should the namspace URI of a DTD be?
            fGrammarResolver.putGrammar("", fDTDGrammar);
        }
    }
    //
    // [64] ignoreSectContents ::= Ignore ('<![' ignoreSectContents ']]>' Ignore)*
    // [65] Ignore ::= Char* - (Char* ('<![' | ']]>') Char*)
    //
    private void scanIgnoreSectContents() throws Exception
    {
        int initialDepth = ++fIncludeSectDepth;
        while (true) {
            if (fEntityReader.lookingAtChar('<', true)) {
                //
                // These tests are split so that we handle cases like
                // '<<![' and '<!<![' which we might otherwise miss.
                //
                if (fEntityReader.lookingAtChar('!', true) && fEntityReader.lookingAtChar('[', true))
                    fIncludeSectDepth++;
            } else if (fEntityReader.lookingAtChar(']', true)) {
                //
                // The same thing goes for ']<![' and '<]]>', etc.
                //
                if (fEntityReader.lookingAtChar(']', true)) {
                    while (fEntityReader.lookingAtChar(']', true)) {
                        /* empty loop body */
                    }
                    if (fEntityReader.lookingAtChar('>', true)) {
                        if (fIncludeSectDepth-- == initialDepth) {
                            decreaseMarkupDepth();
                            return;
                        }
                    }
                }
            } else if (!fEntityReader.lookingAtValidChar(true)) {
                int invChar = fEntityReader.scanInvalidChar();
                if (fScannerState == SCANNER_STATE_END_OF_INPUT)
                    return;
                if (invChar >= 0) {
                    reportFatalXMLError(XMLMessages.MSG_INVALID_CHAR_IN_IGNORESECT,
                                        XMLMessages.P65_INVALID_CHARACTER,
                                        Integer.toHexString(invChar));
                }
            }
        }
    }
    //
    // From the standard:
    //
    // [77] TextDecl ::= '<?xml' VersionInfo? EncodingDecl S? '?>'
    // [24] VersionInfo ::= S 'version' Eq (' VersionNum ' | " VersionNum ")
    // [80] EncodingDecl ::= S 'encoding' Eq ('"' EncName '"' |  "'" EncName "'" )
    // [81] EncName ::= [A-Za-z] ([A-Za-z0-9._] | '-')*
    //
    private void scanTextDecl() throws Exception {
        int version = -1;
        int encoding = -1;
        final int TEXTDECL_START = 0;
        final int TEXTDECL_VERSION = 1;
        final int TEXTDECL_ENCODING = 2;
        final int TEXTDECL_FINISHED = 3;
        int prevState = setScannerState(SCANNER_STATE_TEXTDECL);
        int state = TEXTDECL_START;
        do {
            fEntityReader.skipPastSpaces();
            int offset = fEntityReader.currentOffset();
            if (state == TEXTDECL_START && fEntityReader.skippedString(version_string)) {
                state = TEXTDECL_VERSION;
            } else if (fEntityReader.skippedString(encoding_string)) {
                state = TEXTDECL_ENCODING;
            } else {
                abortMarkup(XMLMessages.MSG_ENCODINGDECL_REQUIRED,
                            XMLMessages.P77_ENCODINGDECL_REQUIRED);
                restoreScannerState(prevState);
                return;
            }
            int length = fEntityReader.currentOffset() - offset;
            fEntityReader.skipPastSpaces();
            if (!fEntityReader.lookingAtChar('=', true)) {
                int minorCode = state == TEXTDECL_VERSION ?
                                XMLMessages.P24_EQ_REQUIRED :
                                XMLMessages.P80_EQ_REQUIRED;
                abortMarkup(XMLMessages.MSG_EQ_REQUIRED_IN_TEXTDECL, minorCode,
                            fEntityReader.addString(offset, length));
                restoreScannerState(prevState);
                return;
            }
            fEntityReader.skipPastSpaces();
            int result = fEntityReader.scanStringLiteral();
            switch (result) {
            case XMLEntityHandler.STRINGLIT_RESULT_QUOTE_REQUIRED:
            {
                int minorCode = state == TEXTDECL_VERSION ?
                                XMLMessages.P24_QUOTE_REQUIRED :
                                XMLMessages.P80_QUOTE_REQUIRED;
                abortMarkup(XMLMessages.MSG_QUOTE_REQUIRED_IN_TEXTDECL, minorCode,
                            fEntityReader.addString(offset, length));
                restoreScannerState(prevState);
                return;
            }
            case XMLEntityHandler.STRINGLIT_RESULT_INVALID_CHAR:
                int invChar = fEntityReader.scanInvalidChar();
                if (fScannerState != SCANNER_STATE_END_OF_INPUT) {
                    if (invChar >= 0) {
                        int minorCode = state == TEXTDECL_VERSION ?
                                        XMLMessages.P26_INVALID_CHARACTER :
                                        XMLMessages.P81_INVALID_CHARACTER;
                        reportFatalXMLError(XMLMessages.MSG_INVALID_CHAR_IN_TEXTDECL, minorCode,
                                            Integer.toHexString(invChar));
                    }
                    skipPastEndOfCurrentMarkup();
                    restoreScannerState(prevState);
                }
                return;
            default:
                break;
            }
            switch (state) {
            case TEXTDECL_VERSION:
                //
                // version="..."
                //
                version = result;
                String versionString = fStringPool.toString(version);
                if (!"1.0".equals(versionString)) {
                    if (!validVersionNum(versionString)) {
                        abortMarkup(XMLMessages.MSG_VERSIONINFO_INVALID,
                                    XMLMessages.P26_INVALID_VALUE,
                                    versionString);
                        restoreScannerState(prevState);
                        return;
                    }
                    // NOTE: RECOVERABLE ERROR
                    Object[] args = { versionString };
                    fErrorReporter.reportError(fErrorReporter.getLocator(),
                                               XMLMessages.XML_DOMAIN,
                                               XMLMessages.MSG_VERSION_NOT_SUPPORTED,
                                               XMLMessages.P26_NOT_SUPPORTED,
                                               args,
                                               XMLErrorReporter.ERRORTYPE_RECOVERABLE_ERROR);
                    // REVISIT - hope it is a compatible version...
                    // skipPastEndOfCurrentMarkup();
                    // return;
                }
                if (!fEntityReader.lookingAtSpace(true)) {
                    abortMarkup(XMLMessages.MSG_SPACE_REQUIRED_IN_TEXTDECL,
                                XMLMessages.P80_WHITESPACE_REQUIRED);
                    restoreScannerState(prevState);
                    return;
                }
                break;
            case TEXTDECL_ENCODING:
                //
                // encoding = "..."
                //
                encoding = result;
                String encodingString = fStringPool.toString(encoding);
                if (!validEncName(encodingString)) {
                    abortMarkup(XMLMessages.MSG_ENCODINGDECL_INVALID,
                                XMLMessages.P81_INVALID_VALUE,
                                encodingString);
                    restoreScannerState(prevState);
                    return;
                }
                fEntityReader.skipPastSpaces();
                state = TEXTDECL_FINISHED;
                break;
            }
        } while (state != TEXTDECL_FINISHED);
        if (!fEntityReader.lookingAtChar('?', true) || !fEntityReader.lookingAtChar('>', true)) {
            abortMarkup(XMLMessages.MSG_TEXTDECL_UNTERMINATED,
                        XMLMessages.P77_UNTERMINATED);
            restoreScannerState(prevState);
            return;
        }
        decreaseMarkupDepth();
        fDTDGrammar.callTextDecl(version, encoding);
        if (fDTDHandler != null) {
            fDTDHandler.textDecl(version, encoding);
        }
        restoreScannerState(prevState);
    }

    private QName fElementDeclQName = new QName();

    /**
     * Scans an element declaration.
     * <pre>
     * [45] elementdecl ::= '&lt;!ELEMENT' S Name S contentspec S? '&gt;'
     * </pre>
     */
    private void scanElementDecl() throws Exception {
        
        if (!checkForPEReference(true)) {
            abortMarkup(XMLMessages.MSG_SPACE_REQUIRED_BEFORE_ELEMENT_TYPE_IN_ELEMENTDECL,
                        XMLMessages.P45_SPACE_REQUIRED);
            return;
        }
        checkForElementTypeWithPEReference(fEntityReader, ' ', fElementQName);
        if (fElementQName.rawname == -1) {
            abortMarkup(XMLMessages.MSG_ELEMENT_TYPE_REQUIRED_IN_ELEMENTDECL,
                        XMLMessages.P45_ELEMENT_TYPE_REQUIRED);
            return;
        }
        if (fDTDHandler != null) {
            fElementDeclQName.setValues(fElementQName);
        }
        if (!checkForPEReference(true)) {
            abortMarkup(XMLMessages.MSG_SPACE_REQUIRED_BEFORE_CONTENTSPEC_IN_ELEMENTDECL,
                        XMLMessages.P45_SPACE_REQUIRED,
                        fElementQName.rawname);
            return;
        }
        int contentSpecType = -1;
        int contentSpec = -1;
        if (fEntityReader.skippedString(empty_string)) {
            contentSpecType = XMLElementDecl.TYPE_EMPTY;
        } else if (fEntityReader.skippedString(any_string)) {
            contentSpecType = XMLElementDecl.TYPE_ANY;
        } else if (!fEntityReader.lookingAtChar('(', true)) {
            abortMarkup(XMLMessages.MSG_CONTENTSPEC_REQUIRED_IN_ELEMENTDECL,
                        XMLMessages.P45_CONTENTSPEC_REQUIRED,
                        fElementQName.rawname);
            return;
        } else {
            int contentSpecReader = fReaderId;
            int contentSpecReaderDepth = fEntityHandler.getReaderDepth();
            int prevState = setScannerState(SCANNER_STATE_CONTENTSPEC);
            int oldDepth = parenDepth();
            fEntityHandler.setReaderDepth(oldDepth);
            increaseParenDepth();
            checkForPEReference(false);
            boolean skippedPCDATA = fEntityReader.skippedString(pcdata_string);
            if (skippedPCDATA) {
                contentSpecType = XMLElementDecl.TYPE_MIXED;
                // REVISIT: Validation. Should we pass in QName?
                contentSpec = scanMixed(fElementQName);
            } else {
                contentSpecType = XMLElementDecl.TYPE_CHILDREN;
                // REVISIT: Validation. Should we pass in QName?
                contentSpec = scanChildren(fElementQName);
            }
            boolean success = contentSpec != -1;
            restoreScannerState(prevState);
            fEntityHandler.setReaderDepth(contentSpecReaderDepth);
            if (!success) {
                setParenDepth(oldDepth);
                skipPastEndOfCurrentMarkup();
                return;
            } else {
                if (parenDepth() != oldDepth) // REVISIT - should not be needed
                    // System.out.println("nesting depth mismatch");
                    ;
            }
        }
        checkForPEReference(false);
        if (!fEntityReader.lookingAtChar('>', true)) {
            abortMarkup(XMLMessages.MSG_ELEMENTDECL_UNTERMINATED,
                        XMLMessages.P45_UNTERMINATED,
                        fElementQName.rawname);
            return;
        }
        decreaseMarkupDepth();
        int elementIndex = fDTDGrammar.getElementDeclIndex(fElementQName, -1);
        boolean elementDeclIsExternal = getReadingExternalEntity();
        if (elementIndex == -1) {
            elementIndex = fDTDGrammar.addElementDecl(fElementQName, contentSpecType, contentSpec, elementDeclIsExternal);
            //System.out.println("XMLDTDScanner#scanElementDecl->DTDGrammar#addElementDecl: "+elementIndex+" ("+fElementQName.localpart+","+fStringPool.toString(fElementQName.localpart)+')');
        }
        else {
            //now check if we already add this element Decl by foward reference
            fDTDGrammar.getElementDecl(elementIndex, fTempElementDecl);
            if (fTempElementDecl.type == -1) {
                fTempElementDecl.type = contentSpecType;
                fTempElementDecl.contentSpecIndex = contentSpec;
                fDTDGrammar.setElementDeclDTD(elementIndex, fTempElementDecl);
                fDTDGrammar.setElementDeclIsExternal(elementIndex, elementDeclIsExternal);
            }
            else {
                //REVISIT, valiate VC duplicate element type. 
                if ( fValidationEnabled )
                    //&& 
                    // (elemenetDeclIsExternal==fDTDGrammar.getElementDeclIsExternal(elementIndex)
                {

                    reportRecoverableXMLError(
                        XMLMessages.MSG_ELEMENT_ALREADY_DECLARED,
                        XMLMessages.VC_UNIQUE_ELEMENT_TYPE_DECLARATION,
                        fStringPool.toString(fElementQName.rawname)
                        );
                }
            }
        }
        if (fDTDHandler != null) {
            fDTDGrammar.getElementDecl(elementIndex, fTempElementDecl);
            fDTDHandler.elementDecl(fElementDeclQName, contentSpecType, contentSpec, fDTDGrammar);
        }

    } // scanElementDecl()

    
    /**
     * Scans mixed content model. Called after scanning past '(' S? '#PCDATA'
     * <pre>
     * [51] Mixed ::= '(' S? '#PCDATA' (S? '|' S? Name)* S? ')*' | '(' S? '#PCDATA' S? ')'
     * </pre>
     */
    private int scanMixed(QName element) throws Exception {

        int valueIndex = -1;  // -1 is special value for #PCDATA
        int prevNodeIndex = -1;
        boolean starRequired = false;
        int[] valueSeen = new int[32];
        int valueCount = 0;
        boolean dupAttrType = false;
        int nodeIndex = -1;

        while (true) {
            if (fValidationEnabled) {
                for (int i=0; i<valueCount;i++) {
                    if ( valueSeen[i] == valueIndex) {
                        dupAttrType = true;
                        break;
                    }
                }
            }
            if (dupAttrType && fValidationEnabled) {
                reportRecoverableXMLError(XMLMessages.MSG_DUPLICATE_TYPE_IN_MIXED_CONTENT,
                                          XMLMessages.VC_NO_DUPLICATE_TYPES,
                                          valueIndex);
                dupAttrType = false;

            }
            else {
                try {
                    valueSeen[valueCount] = valueIndex;
                }
                catch (ArrayIndexOutOfBoundsException ae) {
                    int[] newArray = new int[valueSeen.length*2];
                    System.arraycopy(valueSeen,0,newArray,0,valueSeen.length);
                    valueSeen = newArray;
                    valueSeen[valueCount] = valueIndex;
                }
                valueCount++;

                nodeIndex = fDTDGrammar.addUniqueLeafNode(valueIndex);
            }

            checkForPEReference(false);
            if (!fEntityReader.lookingAtChar('|', true)) {
                if (!fEntityReader.lookingAtChar(')', true)) {
                    reportFatalXMLError(XMLMessages.MSG_CLOSE_PAREN_REQUIRED_IN_MIXED,
                                        XMLMessages.P51_CLOSE_PAREN_REQUIRED,
                                        element.rawname);
                    return -1;
                }
                decreaseParenDepth();
                if (nodeIndex == -1) {
                    nodeIndex = prevNodeIndex;
                } else if (prevNodeIndex != -1) {
                    nodeIndex = fDTDGrammar.addContentSpecNode(XMLContentSpec.CONTENTSPECNODE_CHOICE, prevNodeIndex, nodeIndex);
                }
                if (fEntityReader.lookingAtChar('*', true)) {
                    nodeIndex = fDTDGrammar.addContentSpecNode(XMLContentSpec.CONTENTSPECNODE_ZERO_OR_MORE, nodeIndex);
                } else if (starRequired) {
                    reportFatalXMLError(XMLMessages.MSG_MIXED_CONTENT_UNTERMINATED,
                                        XMLMessages.P51_UNTERMINATED,
                                        fStringPool.toString(element.rawname),
                                        fDTDGrammar.getContentSpecNodeAsString(nodeIndex));
                    return -1;
                }
                return nodeIndex;
            }
            if (nodeIndex != -1) {
                if (prevNodeIndex != -1) {
                    nodeIndex = fDTDGrammar.addContentSpecNode(XMLContentSpec.CONTENTSPECNODE_CHOICE, prevNodeIndex, nodeIndex);
                }
                prevNodeIndex = nodeIndex;
            }
            starRequired = true;
            checkForPEReference(false);
            checkForElementTypeWithPEReference(fEntityReader, ')', fElementRefQName);
            valueIndex = fElementRefQName.rawname;
            if (valueIndex == -1) {
                reportFatalXMLError(XMLMessages.MSG_ELEMENT_TYPE_REQUIRED_IN_MIXED_CONTENT,
                                    XMLMessages.P51_ELEMENT_TYPE_REQUIRED,
                                    element.rawname);
                return -1;
            }
        }

    } // scanMixed(QName):int
    
    /**
     * Scans a children content model.
     * <pre>
     * [47] children ::= (choice | seq) ('?' | '*' | '+')?
     * [49] choice ::= '(' S? cp ( S? '|' S? cp )* S? ')'
     * [50] seq ::= '(' S? cp ( S? ',' S? cp )* S? ')'
     * [48] cp ::= (Name | choice | seq) ('?' | '*' | '+')?
     * </pre>
     */
    private int scanChildren(QName element) throws Exception {
        
        int depth = 1;
        initializeContentModelStack(depth);
        while (true) {
            if (fEntityReader.lookingAtChar('(', true)) {
                increaseParenDepth();
                checkForPEReference(false);
                depth++;
                initializeContentModelStack(depth);
                continue;
            }
            checkForElementTypeWithPEReference(fEntityReader, ')', fElementRefQName);
            int valueIndex = fElementRefQName.rawname;
            if (valueIndex == -1) {
                reportFatalXMLError(XMLMessages.MSG_OPEN_PAREN_OR_ELEMENT_TYPE_REQUIRED_IN_CHILDREN,
                                    XMLMessages.P47_OPEN_PAREN_OR_ELEMENT_TYPE_REQUIRED,
                                    element.rawname);
                return -1;
            }
            fNodeIndexStack[depth] = fDTDGrammar.addContentSpecNode(XMLContentSpec.CONTENTSPECNODE_LEAF, valueIndex);
            if (fEntityReader.lookingAtChar('?', true)) {
                fNodeIndexStack[depth] = fDTDGrammar.addContentSpecNode(XMLContentSpec.CONTENTSPECNODE_ZERO_OR_ONE, fNodeIndexStack[depth]);
            } else if (fEntityReader.lookingAtChar('*', true)) {
                fNodeIndexStack[depth] = fDTDGrammar.addContentSpecNode(XMLContentSpec.CONTENTSPECNODE_ZERO_OR_MORE, fNodeIndexStack[depth]);
            } else if (fEntityReader.lookingAtChar('+', true)) {
                fNodeIndexStack[depth] = fDTDGrammar.addContentSpecNode(XMLContentSpec.CONTENTSPECNODE_ONE_OR_MORE, fNodeIndexStack[depth]);
            }
            while (true) {
                checkForPEReference(false);
                if (fOpStack[depth] != XMLContentSpec.CONTENTSPECNODE_SEQ && fEntityReader.lookingAtChar('|', true)) {
                    if (fPrevNodeIndexStack[depth] != -1) {
                        fNodeIndexStack[depth] = fDTDGrammar.addContentSpecNode(fOpStack[depth], fPrevNodeIndexStack[depth], fNodeIndexStack[depth]);
                    }
                    fPrevNodeIndexStack[depth] = fNodeIndexStack[depth];
                    fOpStack[depth] = XMLContentSpec.CONTENTSPECNODE_CHOICE;
                    break;
                } else if (fOpStack[depth] != XMLContentSpec.CONTENTSPECNODE_CHOICE && fEntityReader.lookingAtChar(',', true)) {
                    if (fPrevNodeIndexStack[depth] != -1) {
                        fNodeIndexStack[depth] = fDTDGrammar.addContentSpecNode(fOpStack[depth], fPrevNodeIndexStack[depth], fNodeIndexStack[depth]);
                    }
                    fPrevNodeIndexStack[depth] = fNodeIndexStack[depth];
                    fOpStack[depth] = XMLContentSpec.CONTENTSPECNODE_SEQ;
                    break;
                } else {
                    if (!fEntityReader.lookingAtChar(')', true)) {
                        reportFatalXMLError(XMLMessages.MSG_CLOSE_PAREN_REQUIRED_IN_CHILDREN,
                                            XMLMessages.P47_CLOSE_PAREN_REQUIRED,
                                            element.rawname);
                    }
                    decreaseParenDepth();
                    if (fPrevNodeIndexStack[depth] != -1) {
                        fNodeIndexStack[depth] = fDTDGrammar.addContentSpecNode(fOpStack[depth], fPrevNodeIndexStack[depth], fNodeIndexStack[depth]);
                    }
                    int nodeIndex = fNodeIndexStack[depth--];
                    fNodeIndexStack[depth] = nodeIndex;
                    if (fEntityReader.lookingAtChar('?', true)) {
                        fNodeIndexStack[depth] = fDTDGrammar.addContentSpecNode(XMLContentSpec.CONTENTSPECNODE_ZERO_OR_ONE, fNodeIndexStack[depth]);
                    } else if (fEntityReader.lookingAtChar('*', true)) {
                        fNodeIndexStack[depth] = fDTDGrammar.addContentSpecNode(XMLContentSpec.CONTENTSPECNODE_ZERO_OR_MORE, fNodeIndexStack[depth]);
                    } else if (fEntityReader.lookingAtChar('+', true)) {
                        fNodeIndexStack[depth] = fDTDGrammar.addContentSpecNode(XMLContentSpec.CONTENTSPECNODE_ONE_OR_MORE, fNodeIndexStack[depth]);
                    }
                    if (depth == 0) {
                        return fNodeIndexStack[0];
                    }
                }
            }
            checkForPEReference(false);
        }

    } // scanChildren(QName):int

    //
    // [52] AttlistDecl ::= '<!ATTLIST' S Name AttDef* S? '>'
    // [53] AttDef ::= S Name S AttType S DefaultDecl
    // [60] DefaultDecl ::= '#REQUIRED' | '#IMPLIED' | (('#FIXED' S)? AttValue)
    //
    private void scanAttlistDecl() throws Exception
    {
        if (!checkForPEReference(true)) {
            abortMarkup(XMLMessages.MSG_SPACE_REQUIRED_BEFORE_ELEMENT_TYPE_IN_ATTLISTDECL,
                        XMLMessages.P52_SPACE_REQUIRED);
            return;
        }
        checkForElementTypeWithPEReference(fEntityReader, ' ', fElementQName);
        int elementTypeIndex = fElementQName.rawname;
        if (elementTypeIndex == -1) {
            abortMarkup(XMLMessages.MSG_ELEMENT_TYPE_REQUIRED_IN_ATTLISTDECL,
                        XMLMessages.P52_ELEMENT_TYPE_REQUIRED);
            return;
        }
        int elementIndex = fDTDGrammar.getElementDeclIndex(fElementQName, -1);
        if (elementIndex == -1) {
            elementIndex = fDTDGrammar.addElementDecl(fElementQName);
            //System.out.println("XMLDTDScanner#scanAttListDecl->DTDGrammar#addElementDecl: "+elementIndex+" ("+fElementQName.localpart+","+fStringPool.toString(fElementQName.localpart)+')');
        }
        boolean sawSpace = checkForPEReference(true);
        if (fEntityReader.lookingAtChar('>', true)) {
            decreaseMarkupDepth();
            return;
        }
        // REVISIT - review this code...
        if (!sawSpace) {
            if (fEntityReader.lookingAtSpace(true)) {
                fEntityReader.skipPastSpaces();
            } else
                reportFatalXMLError(XMLMessages.MSG_SPACE_REQUIRED_BEFORE_ATTRIBUTE_NAME_IN_ATTDEF,
                                    XMLMessages.P53_SPACE_REQUIRED);
        } else {
            if (fEntityReader.lookingAtSpace(true)) {
                fEntityReader.skipPastSpaces();
            }
        }
        if (fEntityReader.lookingAtChar('>', true)) {
            decreaseMarkupDepth();
            return;
        }
        while (true) {
            checkForAttributeNameWithPEReference(fEntityReader, ' ', fAttributeQName);
            int attDefName = fAttributeQName.rawname;
            if (attDefName == -1) {
                abortMarkup(XMLMessages.MSG_ATTRIBUTE_NAME_REQUIRED_IN_ATTDEF,
                            XMLMessages.P53_NAME_REQUIRED,
                            fElementQName.rawname);
                return;
            }
            if (!checkForPEReference(true)) {
                abortMarkup(XMLMessages.MSG_SPACE_REQUIRED_BEFORE_ATTTYPE_IN_ATTDEF,
                            XMLMessages.P53_SPACE_REQUIRED);
                return;
            }
            int attDefType = -1;
            boolean attDefList = false;
            int attDefEnumeration = -1;
            if (fEntityReader.skippedString(cdata_string)) {
                attDefType = XMLAttributeDecl.TYPE_CDATA;
            } else if (fEntityReader.skippedString(id_string)) {
                if (!fEntityReader.skippedString(ref_string)) {
                    attDefType = XMLAttributeDecl.TYPE_ID;
                } else if (!fEntityReader.lookingAtChar('S', true)) {
                    attDefType = XMLAttributeDecl.TYPE_IDREF;
                } else {
                    attDefType = XMLAttributeDecl.TYPE_IDREF;
                    attDefList = true;
                }
            } else if (fEntityReader.skippedString(entit_string)) {
                if (fEntityReader.lookingAtChar('Y', true)) {
                    attDefType = XMLAttributeDecl.TYPE_ENTITY;
                } else if (fEntityReader.skippedString(ies_string)) {
                    attDefType = XMLAttributeDecl.TYPE_ENTITY;
                    attDefList = true;
                } else {
                    abortMarkup(XMLMessages.MSG_ATTTYPE_REQUIRED_IN_ATTDEF,
                                XMLMessages.P53_ATTTYPE_REQUIRED,
                                elementTypeIndex, attDefName);
                    return;
                }
            } else if (fEntityReader.skippedString(nmtoken_string)) {
                if (fEntityReader.lookingAtChar('S', true)) {
                    attDefType = XMLAttributeDecl.TYPE_NMTOKEN;
                    attDefList = true;
                } else {
                    attDefType = XMLAttributeDecl.TYPE_NMTOKEN;
                }
            } else if (fEntityReader.skippedString(notation_string)) {
                if (!checkForPEReference(true)) {
                    abortMarkup(XMLMessages.MSG_SPACE_REQUIRED_AFTER_NOTATION_IN_NOTATIONTYPE,
                                XMLMessages.P58_SPACE_REQUIRED,
                                elementTypeIndex, attDefName);
                    return;
                }
                if (!fEntityReader.lookingAtChar('(', true)) {
                    abortMarkup(XMLMessages.MSG_OPEN_PAREN_REQUIRED_IN_NOTATIONTYPE,
                                XMLMessages.P58_OPEN_PAREN_REQUIRED,
                                elementTypeIndex, attDefName);
                    return;
                }
                increaseParenDepth();
                attDefType = XMLAttributeDecl.TYPE_NOTATION;
                attDefEnumeration = scanEnumeration(elementTypeIndex, attDefName, true);
                if (attDefEnumeration == -1) {
                    skipPastEndOfCurrentMarkup();
                    return;
                }
            } else if (fEntityReader.lookingAtChar('(', true)) {
                increaseParenDepth();
                attDefType = XMLAttributeDecl.TYPE_ENUMERATION;
                attDefEnumeration = scanEnumeration(elementTypeIndex, attDefName, false);
                if (attDefEnumeration == -1) {
                    skipPastEndOfCurrentMarkup();
                    return;
                }
            } else {
                abortMarkup(XMLMessages.MSG_ATTTYPE_REQUIRED_IN_ATTDEF,
                            XMLMessages.P53_ATTTYPE_REQUIRED,
                            elementTypeIndex, attDefName);
                return;
            }
            if (!checkForPEReference(true)) {
                abortMarkup(XMLMessages.MSG_SPACE_REQUIRED_BEFORE_DEFAULTDECL_IN_ATTDEF,
                            XMLMessages.P53_SPACE_REQUIRED,
                            elementTypeIndex, attDefName);
                return;
            }
            int attDefDefaultType = -1;
            int attDefDefaultValue = -1;
            if (fEntityReader.skippedString(required_string)) {
                attDefDefaultType = XMLAttributeDecl.DEFAULT_TYPE_REQUIRED;
            } else if (fEntityReader.skippedString(implied_string)) {
                attDefDefaultType = XMLAttributeDecl.DEFAULT_TYPE_IMPLIED;
            } else {
                if (fEntityReader.skippedString(fixed_string)) {
                    if (!checkForPEReference(true)) {
                        abortMarkup(XMLMessages.MSG_SPACE_REQUIRED_AFTER_FIXED_IN_DEFAULTDECL,
                                    XMLMessages.P60_SPACE_REQUIRED,
                                    elementTypeIndex, attDefName);
                        return;
                    }
                    attDefDefaultType = XMLAttributeDecl.DEFAULT_TYPE_FIXED;
                } else
                    attDefDefaultType = XMLAttributeDecl.DEFAULT_TYPE_DEFAULT;

                //fElementQName.setValues(-1, elementTypeIndex, elementTypeIndex);

                // if attribute name has a prefix "xml", bind it to the XML Namespace.
                // since this is the only pre-defined namespace.
                /***
                if (fAttributeQName.prefix == fXMLSymbol) {
                    fAttributeQName.uri = fXMLNamespace;
                }
                else 
                    fAttributeQName.setValues(-1, attDefName, attDefName);
                ****/

                attDefDefaultValue = scanDefaultAttValue(fElementQName, fAttributeQName, 
                                                         attDefType, 
                                                         attDefEnumeration);

                //normalize and check VC: Attribute Default Legal
                if (attDefDefaultValue != -1 && attDefType != XMLAttributeDecl.TYPE_CDATA ) {
                    attDefDefaultValue = normalizeDefaultAttValue( fAttributeQName, attDefDefaultValue, 
                                                                attDefType, attDefEnumeration,
                                                                attDefList);
                }

                if (attDefDefaultValue == -1) {
                    skipPastEndOfCurrentMarkup();
                    return;
                }
            }
            if (attDefName == fXMLSpace) {
                boolean ok = false;
                if (attDefType == XMLAttributeDecl.TYPE_ENUMERATION) {
                    int index = attDefEnumeration;
                    if (index != -1) {
                        ok = (fStringPool.stringListLength(index) == 1 &&
                              (fStringPool.stringInList(index, fDefault) ||
                               fStringPool.stringInList(index, fPreserve))) ||
                            (fStringPool.stringListLength(index) == 2 &&
                             fStringPool.stringInList(index, fDefault) &&
                             fStringPool.stringInList(index, fPreserve));
                    }
                }
                if (!ok) {
                    reportFatalXMLError(XMLMessages.MSG_XML_SPACE_DECLARATION_ILLEGAL,
                                        XMLMessages.S2_10_DECLARATION_ILLEGAL,
                                        elementTypeIndex);
                }
            }
            sawSpace = checkForPEReference(true);
            
            // if attribute name has a prefix "xml", bind it to the XML Namespace.
            // since this is the only pre-defined namespace.
            if (fAttributeQName.prefix == fXMLSymbol) {
                fAttributeQName.uri = fXMLNamespace;
            }
            
            if (fEntityReader.lookingAtChar('>', true)) {
                int attDefIndex = addAttDef(fElementQName, fAttributeQName, 
                                                        attDefType, attDefList, attDefEnumeration, 
                                                        attDefDefaultType, attDefDefaultValue, 
                                                        getReadingExternalEntity());
                //System.out.println("XMLDTDScanner#scanAttlistDecl->DTDGrammar#addAttDef: "+attDefIndex+
                //                   " ("+fElementQName.localpart+","+fStringPool.toString(fElementQName.rawname)+')'+
                //                   " ("+fAttributeQName.localpart+","+fStringPool.toString(fAttributeQName.rawname)+')');
                decreaseMarkupDepth();
                return;
            }
            // REVISIT - review this code...
            if (!sawSpace) {
                if (fEntityReader.lookingAtSpace(true)) {
                    fEntityReader.skipPastSpaces();
                } else
                    reportFatalXMLError(XMLMessages.MSG_SPACE_REQUIRED_BEFORE_ATTRIBUTE_NAME_IN_ATTDEF,
                                        XMLMessages.P53_SPACE_REQUIRED);
            } else {
                if (fEntityReader.lookingAtSpace(true)) {
                    fEntityReader.skipPastSpaces();
                }
            }
            if (fEntityReader.lookingAtChar('>', true)) {
                int attDefIndex = addAttDef(fElementQName, fAttributeQName, 
                                                        attDefType, attDefList, attDefEnumeration, 
                                                        attDefDefaultType, attDefDefaultValue,
                                                        getReadingExternalEntity() );
                //System.out.println("XMLDTDScanner#scanAttlistDecl->DTDGrammar#addAttDef: "+attDefIndex+
                //                   " ("+fElementQName.localpart+","+fStringPool.toString(fElementQName.rawname)+')'+
                //                   " ("+fAttributeQName.localpart+","+fStringPool.toString(fAttributeQName.rawname)+')');
                decreaseMarkupDepth();
                return;
            }
            int attDefIndex = addAttDef(fElementQName, fAttributeQName, 
                                                    attDefType, attDefList, attDefEnumeration, 
                                                    attDefDefaultType, attDefDefaultValue,
                                                    getReadingExternalEntity());
            //System.out.println("XMLDTDScanner#scanAttlistDecl->DTDGrammar#addAttDef: "+attDefIndex+
            //                   " ("+fElementQName.localpart+","+fStringPool.toString(fElementQName.rawname)+')'+
            //                   " ("+fAttributeQName.localpart+","+fStringPool.toString(fAttributeQName.rawname)+')');
        }
    }

    private int addAttDef(QName element, QName attribute, 
                          int attDefType, boolean attDefList, int attDefEnumeration, 
                          int attDefDefaultType, int attDefDefaultValue,
                          boolean isExternal ) throws Exception {

        if (fDTDHandler != null) {
            String enumString = attDefEnumeration != -1 ? fStringPool.stringListAsString(attDefEnumeration) : null;
            fDTDHandler.attlistDecl(element, attribute, 
                                    attDefType, attDefList,
                                    enumString, 
                                    attDefDefaultType, attDefDefaultValue);
        }
        int elementIndex = fDTDGrammar.getElementDeclIndex(element, -1);
        if (elementIndex == -1) {
            // REPORT Internal error here
        }
        else {
            int attlistIndex = fDTDGrammar.getFirstAttributeDeclIndex(elementIndex);
            int dupID = -1;
            int dupNotation = -1;
            while (attlistIndex != -1) {
                fDTDGrammar.getAttributeDecl(attlistIndex, fTempAttributeDecl);

                // REVISIT: Validation. Attributes are also tuples.
                if (fStringPool.equalNames(fTempAttributeDecl.name.rawname, attribute.rawname)) {
                    /******
                    if (fWarningOnDuplicateAttDef) {
                        Object[] args = { fStringPool.toString(fElementType[elemChunk][elemIndex]),
                                          fStringPool.toString(attributeDecl.rawname) };
                        fErrorReporter.reportError(fErrorReporter.getLocator(),
                                                   XMLMessages.XML_DOMAIN,
                                                   XMLMessages.MSG_DUPLICATE_ATTDEF,
                                                   XMLMessages.P53_DUPLICATE,
                                                   args,
                                                   XMLErrorReporter.ERRORTYPE_WARNING);
                    }
                    ******/
                    return -1;
                }

                if (fValidationEnabled) {
                    if (attDefType == XMLAttributeDecl.TYPE_ID && 
                        fTempAttributeDecl.type == XMLAttributeDecl.TYPE_ID ) {
                        dupID = fTempAttributeDecl.name.rawname;
                    }
                    if (attDefType == XMLAttributeDecl.TYPE_NOTATION 
                        && fTempAttributeDecl.type == XMLAttributeDecl.TYPE_NOTATION) {
                        dupNotation = fTempAttributeDecl.name.rawname;
                    }
                }
                attlistIndex = fDTDGrammar.getNextAttributeDeclIndex(attlistIndex);
            }
            if (fValidationEnabled) {
                if (dupID != -1) {
                    Object[] args = { fStringPool.toString(element.rawname),
                                      fStringPool.toString(dupID),
                                      fStringPool.toString(attribute.rawname) };
                    fErrorReporter.reportError(fErrorReporter.getLocator(),
                                               XMLMessages.XML_DOMAIN,
                                               XMLMessages.MSG_MORE_THAN_ONE_ID_ATTRIBUTE,
                                               XMLMessages.VC_ONE_ID_PER_ELEMENT_TYPE,
                                               args,
                                               XMLErrorReporter.ERRORTYPE_RECOVERABLE_ERROR);
                    return -1;
                }
                if (dupNotation != -1) {
                    Object[] args = { fStringPool.toString(element.rawname),
                                      fStringPool.toString(dupNotation),
                                      fStringPool.toString(attribute.rawname) };
                    fErrorReporter.reportError(fErrorReporter.getLocator(),
                                               XMLMessages.XML_DOMAIN,
                                               XMLMessages.MSG_MORE_THAN_ONE_NOTATION_ATTRIBUTE,
                                               XMLMessages.VC_ONE_NOTATION_PER_ELEMENT_TYPE,
                                               args,
                                               XMLErrorReporter.ERRORTYPE_RECOVERABLE_ERROR);
                    return -1;
                }
            }
        }
        return fDTDGrammar.addAttDef(element, attribute, 
                                     attDefType, attDefList, attDefEnumeration, 
                                     attDefDefaultType, attDefDefaultValue,
                                     isExternal);

    }
    //
    // [58] NotationType ::= 'NOTATION' S '(' S? Name (S? '|' S? Name)* S? ')'
    // [59] Enumeration ::= '(' S? Nmtoken (S? '|' S? Nmtoken)* S? ')'
    //
    private int scanEnumeration(int elementType, int attrName, boolean isNotationType) throws Exception
    {
        int enumIndex = fDTDGrammar.startEnumeration();
        while (true) {
            checkForPEReference(false);
            int nameIndex = isNotationType ?
                            checkForNameWithPEReference(fEntityReader, ')') :
                            checkForNmtokenWithPEReference(fEntityReader, ')');
            if (nameIndex == -1) {
                if (isNotationType) {
                    reportFatalXMLError(XMLMessages.MSG_NAME_REQUIRED_IN_NOTATIONTYPE,
                                        XMLMessages.P58_NAME_REQUIRED,
                                        elementType,
                                        attrName);
                } else {
                    reportFatalXMLError(XMLMessages.MSG_NMTOKEN_REQUIRED_IN_ENUMERATION,
                                        XMLMessages.P59_NMTOKEN_REQUIRED,
                                        elementType,
                                        attrName);
                }
                fDTDGrammar.endEnumeration(enumIndex);
                return -1;
            }
            fDTDGrammar.addNameToEnumeration(enumIndex, elementType, attrName, nameIndex, isNotationType);
            /*****/
            if (isNotationType && !((DefaultEntityHandler)fEntityHandler).isNotationDeclared(nameIndex)) {
                Object[] args = { fStringPool.toString(elementType),
                    fStringPool.toString(attrName),
                    fStringPool.toString(nameIndex) };
                    ((DefaultEntityHandler)fEntityHandler).addRequiredNotation(nameIndex,
                                                       fErrorReporter.getLocator(),
                                                       XMLMessages.MSG_NOTATION_NOT_DECLARED_FOR_NOTATIONTYPE_ATTRIBUTE,
                                                       XMLMessages.VC_NOTATION_DECLARED,
                                                       args);
            }
            /*****/
            checkForPEReference(false);
            if (!fEntityReader.lookingAtChar('|', true)) {
                fDTDGrammar.endEnumeration(enumIndex);
                if (!fEntityReader.lookingAtChar(')', true)) {
                    if (isNotationType) {
                        reportFatalXMLError(XMLMessages.MSG_NOTATIONTYPE_UNTERMINATED,
                                            XMLMessages.P58_UNTERMINATED,
                                        elementType,
                                        attrName);
                    } else {
                        reportFatalXMLError(XMLMessages.MSG_ENUMERATION_UNTERMINATED,
                                            XMLMessages.P59_UNTERMINATED,
                                        elementType,
                                        attrName);
                    }
                    return -1;
                }
                decreaseParenDepth();
                return enumIndex;
            }
        }
    }
    //
    // [10] AttValue ::= '"' ([^<&"] | Reference)* '"'
    //                   | "'" ([^<&'] | Reference)* "'"
    //
    /**
     * Scan the default value in an attribute declaration
     *
     * @param elementType handle to the element that owns the attribute
     * @param attrName handle in the string pool for the attribute name
     * @return handle in the string pool for the default attribute value
     * @exception java.lang.Exception
     */
    public int scanDefaultAttValue(QName element, QName attribute) throws Exception
    {
        boolean single;
        if (!(single = fEntityReader.lookingAtChar('\'', true)) && !fEntityReader.lookingAtChar('\"', true)) {
            reportFatalXMLError(XMLMessages.MSG_QUOTE_REQUIRED_IN_ATTVALUE,
                                XMLMessages.P10_QUOTE_REQUIRED,
                                element.rawname,
                                attribute.rawname);
            return -1;
        }
        int previousState = setScannerState(SCANNER_STATE_DEFAULT_ATTRIBUTE_VALUE);
        char qchar = single ? '\'' : '\"';
        fDefaultAttValueReader = fReaderId;
        fDefaultAttValueElementType = element.rawname;
        fDefaultAttValueAttrName = attribute.rawname;
        boolean setMark = true;
        int dataOffset = fLiteralData.length();
        while (true) {
            fDefaultAttValueOffset = fEntityReader.currentOffset();
            if (setMark) {
                fDefaultAttValueMark = fDefaultAttValueOffset;
                setMark = false;
            }
            if (fEntityReader.lookingAtChar(qchar, true)) {
                if (fReaderId == fDefaultAttValueReader)
                    break;
                continue;
            }
            if (fEntityReader.lookingAtChar(' ', true)) {
                continue;
            }
            boolean skippedCR;
            if ((skippedCR = fEntityReader.lookingAtChar((char)0x0D, true)) || fEntityReader.lookingAtSpace(true)) {
                if (fDefaultAttValueOffset - fDefaultAttValueMark > 0)
                    fEntityReader.append(fLiteralData, fDefaultAttValueMark, fDefaultAttValueOffset - fDefaultAttValueMark);
                setMark = true;
                fLiteralData.append(' ');
                if (skippedCR)
                    fEntityReader.lookingAtChar((char)0x0A, true);
                continue;
            }
            if (fEntityReader.lookingAtChar('&', true)) {
                if (fDefaultAttValueOffset - fDefaultAttValueMark > 0)
                    fEntityReader.append(fLiteralData, fDefaultAttValueMark, fDefaultAttValueOffset - fDefaultAttValueMark);
                setMark = true;
                //
                // Check for character reference first.
                //
                if (fEntityReader.lookingAtChar('#', true)) {
                    int ch = scanCharRef();
                    if (ch != -1) {
                        if (ch < 0x10000)
                            fLiteralData.append((char)ch);
                        else {
                            fLiteralData.append((char)(((ch-0x00010000)>>10)+0xd800));
                            fLiteralData.append((char)(((ch-0x00010000)&0x3ff)+0xdc00));
                        }
                    }
                } else {
                    //
                    // Entity reference
                    //
                    int nameOffset = fEntityReader.currentOffset();
                    fEntityReader.skipPastName(';');
                    int nameLength = fEntityReader.currentOffset() - nameOffset;
                    if (nameLength == 0) {
                        reportFatalXMLError(XMLMessages.MSG_NAME_REQUIRED_IN_REFERENCE,
                                            XMLMessages.P68_NAME_REQUIRED);
                    } else if (!fEntityReader.lookingAtChar(';', true)) {
                        reportFatalXMLError(XMLMessages.MSG_SEMICOLON_REQUIRED_IN_REFERENCE,
                                            XMLMessages.P68_SEMICOLON_REQUIRED,
                                            fEntityReader.addString(nameOffset, nameLength));
                    } else {
                        int entityNameIndex = fEntityReader.addSymbol(nameOffset, nameLength);
                        fEntityHandler.startReadingFromEntity(entityNameIndex, markupDepth(), XMLEntityHandler.ENTITYREF_IN_DEFAULTATTVALUE);
                    }
                }
                continue;
            }
            if (fEntityReader.lookingAtChar('<', true)) {
                if (fDefaultAttValueOffset - fDefaultAttValueMark > 0)
                    fEntityReader.append(fLiteralData, fDefaultAttValueMark, fDefaultAttValueOffset - fDefaultAttValueMark);
                setMark = true;
                reportFatalXMLError(XMLMessages.MSG_LESSTHAN_IN_ATTVALUE,
                                    XMLMessages.WFC_NO_LESSTHAN_IN_ATTVALUE,
                                    element.rawname,
                                    attribute.rawname);
                continue;
            }
            if (!fEntityReader.lookingAtValidChar(true)) {
                if (fDefaultAttValueOffset - fDefaultAttValueMark > 0)
                    fEntityReader.append(fLiteralData, fDefaultAttValueMark, fDefaultAttValueOffset - fDefaultAttValueMark);
                setMark = true;
                int invChar = fEntityReader.scanInvalidChar();
                if (fScannerState == SCANNER_STATE_END_OF_INPUT)
                    return -1;
                if (invChar >= 0) {
                    reportFatalXMLError(XMLMessages.MSG_INVALID_CHAR_IN_ATTVALUE,
                                        XMLMessages.P10_INVALID_CHARACTER,
                                        fStringPool.toString(element.rawname),
                                        fStringPool.toString(attribute.rawname),
                                        Integer.toHexString(invChar));
                }
                continue;
            }
        }
        restoreScannerState(previousState);
        int dataLength = fLiteralData.length() - dataOffset;
        if (dataLength == 0) {
            return fEntityReader.addString(fDefaultAttValueMark, fDefaultAttValueOffset - fDefaultAttValueMark);
        }
        if (fDefaultAttValueOffset - fDefaultAttValueMark > 0) {
            fEntityReader.append(fLiteralData, fDefaultAttValueMark, fDefaultAttValueOffset - fDefaultAttValueMark);
            dataLength = fLiteralData.length() - dataOffset;
        }
        return fLiteralData.addString(dataOffset, dataLength);
    }
    //
    // [82] NotationDecl ::= '<!NOTATION' S Name S (ExternalID |  PublicID) S? '>'
    //
    private void scanNotationDecl() throws Exception
    {
        if (!checkForPEReference(true)) {
            abortMarkup(XMLMessages.MSG_SPACE_REQUIRED_BEFORE_NOTATION_NAME_IN_NOTATIONDECL,
                        XMLMessages.P82_SPACE_REQUIRED);
            return;
        }
        int notationName = checkForNameWithPEReference(fEntityReader, ' ');
        if (notationName == -1) {
            abortMarkup(XMLMessages.MSG_NOTATION_NAME_REQUIRED_IN_NOTATIONDECL,
                        XMLMessages.P82_NAME_REQUIRED);
            return;
        }
        if (!checkForPEReference(true)) {
            abortMarkup(XMLMessages.MSG_SPACE_REQUIRED_AFTER_NOTATION_NAME_IN_NOTATIONDECL,
                        XMLMessages.P82_SPACE_REQUIRED,
                        notationName);
            return;
        }
        if (!scanExternalID(true)) {
            skipPastEndOfCurrentMarkup();
            return;
        }
        checkForPEReference(false);
        if (!fEntityReader.lookingAtChar('>', true)) {
            abortMarkup(XMLMessages.MSG_NOTATIONDECL_UNTERMINATED,
                        XMLMessages.P82_UNTERMINATED,
                        notationName);
            return;
        }
        decreaseMarkupDepth();
        /****
        System.out.println(fStringPool.toString(notationName)+","
                           +fStringPool.toString(fPubidLiteral) + ","
                           +fStringPool.toString(fSystemLiteral) + ","
                           +getReadingExternalEntity());
        /****/

        int notationIndex = ((DefaultEntityHandler) fEntityHandler).addNotationDecl( notationName, 
                                                                                     fPubidLiteral, 
                                                                                     fSystemLiteral,
                                                                                     getReadingExternalEntity());
        fDTDGrammar.addNotationDecl(notationName, fPubidLiteral, fSystemLiteral);
        if (fDTDHandler != null) {
            fDTDHandler.notationDecl(notationName, fPubidLiteral, fSystemLiteral);
        }
    }
    //
    // [70] EntityDecl ::= GEDecl | PEDecl
    // [71] GEDecl ::= '<!ENTITY' S Name S EntityDef S? '>'
    // [72] PEDecl ::= '<!ENTITY' S '%' S Name S PEDef S? '>'
    // [73] EntityDef ::= EntityValue | (ExternalID NDataDecl?)
    // [74] PEDef ::= EntityValue | ExternalID
    // [75] ExternalID ::= 'SYSTEM' S SystemLiteral
    //                     | 'PUBLIC' S PubidLiteral S SystemLiteral
    // [76] NDataDecl ::= S 'NDATA' S Name
    //  [9] EntityValue ::= '"' ([^%&"] | PEReference | Reference)* '"'
    //                      | "'" ([^%&'] | PEReference | Reference)* "'"
    //
    // Called after scanning 'ENTITY'
    //
    private void scanEntityDecl() throws Exception
    {
        boolean isPEDecl = false;
        boolean sawPERef = false;
        if (fEntityReader.lookingAtSpace(true)) {
            fEntityReader.skipPastSpaces();
            if (!fEntityReader.lookingAtChar('%', true)) {
                isPEDecl = false; // <!ENTITY x "x">
            } else if (fEntityReader.lookingAtSpace(true)) {
                checkForPEReference(false); // <!ENTITY % x "x">
                isPEDecl = true;
            } else if (!getReadingExternalEntity()) {
                reportFatalXMLError(XMLMessages.MSG_SPACE_REQUIRED_BEFORE_ENTITY_NAME_IN_PEDECL,
                                    XMLMessages.P72_SPACE);
                isPEDecl = true;
            } else if (fEntityReader.lookingAtChar('%', false)) {
                checkForPEReference(false); // <!ENTITY %%x; "x"> is legal
                isPEDecl = true;
            } else {
                sawPERef = true;
            }
        } else if (!getReadingExternalEntity() || !fEntityReader.lookingAtChar('%', true)) {
            // <!ENTITY[^ ]...> or <!ENTITY[^ %]...>
            reportFatalXMLError(XMLMessages.MSG_SPACE_REQUIRED_BEFORE_ENTITY_NAME_IN_ENTITYDECL,
                                XMLMessages.P70_SPACE);
            isPEDecl = false;
        } else if (fEntityReader.lookingAtSpace(false)) {
            // <!ENTITY% ...>
            reportFatalXMLError(XMLMessages.MSG_SPACE_REQUIRED_BEFORE_PERCENT_IN_PEDECL,
                                XMLMessages.P72_SPACE);
            isPEDecl = false;
        } else {
            sawPERef = true;
        }
        if (sawPERef) {
            while (true) {
                int nameOffset = fEntityReader.currentOffset();
                fEntityReader.skipPastName(';');
                int nameLength = fEntityReader.currentOffset() - nameOffset;
                if (nameLength == 0) {
                    reportFatalXMLError(XMLMessages.MSG_NAME_REQUIRED_IN_PEREFERENCE,
                                        XMLMessages.P69_NAME_REQUIRED);
                } else if (!fEntityReader.lookingAtChar(';', true)) {
                    reportFatalXMLError(XMLMessages.MSG_SEMICOLON_REQUIRED_IN_PEREFERENCE,
                                        XMLMessages.P69_SEMICOLON_REQUIRED,
                                        fEntityReader.addString(nameOffset, nameLength));
                } else {
                    int peNameIndex = fEntityReader.addSymbol(nameOffset, nameLength);
                    int readerDepth = (fScannerState == SCANNER_STATE_CONTENTSPEC) ? parenDepth() : markupDepth();
                    fEntityHandler.startReadingFromEntity(peNameIndex, readerDepth, XMLEntityHandler.ENTITYREF_IN_DTD_WITHIN_MARKUP);
                }
                fEntityReader.skipPastSpaces();
                if (!fEntityReader.lookingAtChar('%', true))
                    break;
                if (!isPEDecl) {
                    if (fEntityReader.lookingAtSpace(true)) {
                        checkForPEReference(false);
                        isPEDecl = true;
                        break;
                    }
                    isPEDecl = fEntityReader.lookingAtChar('%', true);
                }
            }
        }
        int entityName = checkForNameWithPEReference(fEntityReader, ' ');
        if (entityName == -1) {
            abortMarkup(XMLMessages.MSG_ENTITY_NAME_REQUIRED_IN_ENTITYDECL,
                        XMLMessages.P70_REQUIRED_NAME);
            return;
        }
        if (!fDTDGrammar.startEntityDecl(isPEDecl, entityName)) {
            skipPastEndOfCurrentMarkup();
            return;
        }
        if (!checkForPEReference(true)) {
            abortMarkup(XMLMessages.MSG_SPACE_REQUIRED_AFTER_ENTITY_NAME_IN_ENTITYDECL,
                        XMLMessages.P70_REQUIRED_SPACE,
                        entityName);
            fDTDGrammar.endEntityDecl();
            return;
        }
        if (isPEDecl) {
            boolean single;
            if ((single = fEntityReader.lookingAtChar('\'', true)) || fEntityReader.lookingAtChar('\"', true)) {
                int value = scanEntityValue(single);
                if (value == -1) {
                    skipPastEndOfCurrentMarkup();
                    fDTDGrammar.endEntityDecl();
                    return;
                }
                checkForPEReference(false);
                if (!fEntityReader.lookingAtChar('>', true)) {
                    abortMarkup(XMLMessages.MSG_ENTITYDECL_UNTERMINATED,
                                XMLMessages.P72_UNTERMINATED,
                                entityName);
                    fDTDGrammar.endEntityDecl();
                    return;
                }
                decreaseMarkupDepth();
                fDTDGrammar.endEntityDecl();

                // a hack by Eric
                //REVISIT
                fDTDGrammar.addInternalPEDecl(entityName, value);
                if (fDTDHandler != null) {
                    fDTDHandler.internalPEDecl(entityName, value);
                }
                int entityIndex = ((DefaultEntityHandler) fEntityHandler).addInternalPEDecl(entityName, 
                                                                                            value, 
                                                                                            getReadingExternalEntity());

            } else {
                if (!scanExternalID(false)) {
                    skipPastEndOfCurrentMarkup();
                    fDTDGrammar.endEntityDecl();
                    return;
                }
                checkForPEReference(false);
                if (!fEntityReader.lookingAtChar('>', true)) {
                    abortMarkup(XMLMessages.MSG_ENTITYDECL_UNTERMINATED,
                                XMLMessages.P72_UNTERMINATED,
                                entityName);
                    fDTDGrammar.endEntityDecl();
                    return;
                }
                decreaseMarkupDepth();
                fDTDGrammar.endEntityDecl();

                //a hack by Eric
                //REVISIT
                fDTDGrammar.addExternalPEDecl(entityName, fPubidLiteral, fSystemLiteral);
                if (fDTDHandler != null) {
                    fDTDHandler.externalPEDecl(entityName, fPubidLiteral, fSystemLiteral);
                }
                int entityIndex = ((DefaultEntityHandler) fEntityHandler).addExternalPEDecl(entityName, 
                                                                                            fPubidLiteral, 
                                                                                            fSystemLiteral, getReadingExternalEntity());
            }
        } else {
            boolean single;
            if ((single = fEntityReader.lookingAtChar('\'', true)) || fEntityReader.lookingAtChar('\"', true)) {
                int value = scanEntityValue(single);
                if (value == -1) {
                    skipPastEndOfCurrentMarkup();
                    fDTDGrammar.endEntityDecl();
                    return;
                }
                checkForPEReference(false);
                if (!fEntityReader.lookingAtChar('>', true)) {
                    abortMarkup(XMLMessages.MSG_ENTITYDECL_UNTERMINATED,
                                XMLMessages.P71_UNTERMINATED,
                                entityName);
                    fDTDGrammar.endEntityDecl();
                    return;
                }
                decreaseMarkupDepth();
                fDTDGrammar.endEntityDecl();

                //a hack by Eric
                //REVISIT
                fDTDGrammar.addInternalEntityDecl(entityName, value);
                if (fDTDHandler != null) {
                    fDTDHandler.internalEntityDecl(entityName, value);
                }
                int entityIndex = ((DefaultEntityHandler) fEntityHandler).addInternalEntityDecl(entityName, 
                                                                                                value, 
                                                                                                getReadingExternalEntity());
            } else {
                if (!scanExternalID(false)) {
                    skipPastEndOfCurrentMarkup();
                    fDTDGrammar.endEntityDecl();
                    return;
                }
                boolean unparsed = false;
                if (fEntityReader.lookingAtSpace(true)) {
                    fEntityReader.skipPastSpaces();
                    unparsed = fEntityReader.skippedString(ndata_string);
                }
                if (!unparsed) {
                    checkForPEReference(false);
                    if (!fEntityReader.lookingAtChar('>', true)) {
                        abortMarkup(XMLMessages.MSG_ENTITYDECL_UNTERMINATED,
                                    XMLMessages.P72_UNTERMINATED,
                                    entityName);
                        fDTDGrammar.endEntityDecl();
                        return;
                    }
                    decreaseMarkupDepth();
                    fDTDGrammar.endEntityDecl();

                    //a hack by Eric
                    //REVISIT
                    fDTDGrammar.addExternalEntityDecl(entityName, fPubidLiteral, fSystemLiteral);
                    if (fDTDHandler != null) {
                        fDTDHandler.externalEntityDecl(entityName, fPubidLiteral, fSystemLiteral);
                    }
                    int entityIndex = ((DefaultEntityHandler) fEntityHandler).addExternalEntityDecl(entityName, 
                                                                                                    fPubidLiteral, 
                                                                                                    fSystemLiteral, 
                                                                                                    getReadingExternalEntity());

                } else {
                    if (!fEntityReader.lookingAtSpace(true)) {
                        abortMarkup(XMLMessages.MSG_SPACE_REQUIRED_BEFORE_NOTATION_NAME_IN_UNPARSED_ENTITYDECL,
                                    XMLMessages.P76_SPACE_REQUIRED,
                                    entityName);
                        fDTDGrammar.endEntityDecl();
                        return;
                    }
                    fEntityReader.skipPastSpaces();
                    int ndataOffset = fEntityReader.currentOffset();
                    fEntityReader.skipPastName('>');
                    int ndataLength = fEntityReader.currentOffset() - ndataOffset;
                    if (ndataLength == 0) {
                        abortMarkup(XMLMessages.MSG_NOTATION_NAME_REQUIRED_FOR_UNPARSED_ENTITYDECL,
                                    XMLMessages.P76_REQUIRED,
                                    entityName);
                        fDTDGrammar.endEntityDecl();
                        return;
                    }
                    int notationName = fEntityReader.addSymbol(ndataOffset, ndataLength);
                    checkForPEReference(false);
                    if (!fEntityReader.lookingAtChar('>', true)) {
                        abortMarkup(XMLMessages.MSG_ENTITYDECL_UNTERMINATED,
                                    XMLMessages.P72_UNTERMINATED,
                                    entityName);
                        fDTDGrammar.endEntityDecl();
                        return;
                    }
                    decreaseMarkupDepth();
                    fDTDGrammar.endEntityDecl();
                    
                    //a hack by Eric
                    //REVISIT
                    fDTDGrammar.addUnparsedEntityDecl(entityName, fPubidLiteral, fSystemLiteral, notationName);
                    if (fDTDHandler != null) {
                        fDTDHandler.unparsedEntityDecl(entityName, fPubidLiteral, fSystemLiteral, notationName);
                    }
                    /****
                    System.out.println("----addUnparsedEntity--- "+ fStringPool.toString(entityName)+","
                                       +fStringPool.toString(notationName)+","
                                       +fStringPool.toString(fPubidLiteral) + ","
                                       +fStringPool.toString(fSystemLiteral) + ","
                                       +getReadingExternalEntity());
                    /****/
                    int entityIndex = ((DefaultEntityHandler) fEntityHandler).addUnparsedEntityDecl(entityName, 
                                                                                                    fPubidLiteral, 
                                                                                                    fSystemLiteral, 
                                                                                                    notationName, 
                                                                                                    getReadingExternalEntity());
                }
            }
        }
    }
    //
    //  [9] EntityValue ::= '"' ([^%&"] | PEReference | Reference)* '"'
    //                      | "'" ([^%&'] | PEReference | Reference)* "'"
    //
    private int scanEntityValue(boolean single) throws Exception
    {
        char qchar = single ? '\'' : '\"';
        fEntityValueMark = fEntityReader.currentOffset();
        int entityValue = fEntityReader.scanEntityValue(qchar, true);
        if (entityValue < 0)
            entityValue = scanComplexEntityValue(qchar, entityValue);
        return entityValue;
    }
    private int scanComplexEntityValue(char qchar, int result) throws Exception
    {
        int previousState = setScannerState(SCANNER_STATE_ENTITY_VALUE);
        fEntityValueReader = fReaderId;
        int dataOffset = fLiteralData.length();
        while (true) {
            switch (result) {
            case XMLEntityHandler.ENTITYVALUE_RESULT_FINISHED:
            {
                int offset = fEntityReader.currentOffset();
                fEntityReader.lookingAtChar(qchar, true);
                restoreScannerState(previousState);
                int dataLength = fLiteralData.length() - dataOffset;
                if (dataLength == 0) {
                    return fEntityReader.addString(fEntityValueMark, offset - fEntityValueMark);
                }
                if (offset - fEntityValueMark > 0) {
                    fEntityReader.append(fLiteralData, fEntityValueMark, offset - fEntityValueMark);
                    dataLength = fLiteralData.length() - dataOffset;
                }
                return fLiteralData.addString(dataOffset, dataLength);
            }
            case XMLEntityHandler.ENTITYVALUE_RESULT_REFERENCE:
            {
                int offset = fEntityReader.currentOffset();
                if (offset - fEntityValueMark > 0)
                    fEntityReader.append(fLiteralData, fEntityValueMark, offset - fEntityValueMark);
                fEntityReader.lookingAtChar('&', true);
                //
                // Check for character reference first.
                //
                if (fEntityReader.lookingAtChar('#', true)) {
                    int ch = scanCharRef();
                    if (ch != -1) {
                        if (ch < 0x10000)
                            fLiteralData.append((char)ch);
                        else {
                            fLiteralData.append((char)(((ch-0x00010000)>>10)+0xd800));
                            fLiteralData.append((char)(((ch-0x00010000)&0x3ff)+0xdc00));
                        }
                    }
                    fEntityValueMark = fEntityReader.currentOffset();
                } else {
                    //
                    // Entity reference
                    //
                    int nameOffset = fEntityReader.currentOffset();
                    fEntityReader.skipPastName(';');
                    int nameLength = fEntityReader.currentOffset() - nameOffset;
                    if (nameLength == 0) {
                        reportFatalXMLError(XMLMessages.MSG_NAME_REQUIRED_IN_REFERENCE,
                                            XMLMessages.P68_NAME_REQUIRED);
                        fEntityValueMark = fEntityReader.currentOffset();
                    } else if (!fEntityReader.lookingAtChar(';', true)) {
                        reportFatalXMLError(XMLMessages.MSG_SEMICOLON_REQUIRED_IN_REFERENCE,
                                            XMLMessages.P68_SEMICOLON_REQUIRED,
                                            fEntityReader.addString(nameOffset, nameLength));
                        fEntityValueMark = fEntityReader.currentOffset();
                    } else {
                        //
                        // 4.4.7 Bypassed
                        //
                        // When a general entity reference appears in the EntityValue in an
                        // entity declaration, it is bypassed and left as is.
                        //
                        fEntityValueMark = offset;
                    }
                }
                break;
            }
            case XMLEntityHandler.ENTITYVALUE_RESULT_PEREF:
            {
                int offset = fEntityReader.currentOffset();
                if (offset - fEntityValueMark > 0)
                    fEntityReader.append(fLiteralData, fEntityValueMark, offset - fEntityValueMark);
                fEntityReader.lookingAtChar('%', true);
                int nameOffset = fEntityReader.currentOffset();
                fEntityReader.skipPastName(';');
                int nameLength = fEntityReader.currentOffset() - nameOffset;
                if (nameLength == 0) {
                    reportFatalXMLError(XMLMessages.MSG_NAME_REQUIRED_IN_PEREFERENCE,
                                        XMLMessages.P69_NAME_REQUIRED);
                } else if (!fEntityReader.lookingAtChar(';', true)) {
                    reportFatalXMLError(XMLMessages.MSG_SEMICOLON_REQUIRED_IN_PEREFERENCE,
                                        XMLMessages.P69_SEMICOLON_REQUIRED,
                                        fEntityReader.addString(nameOffset, nameLength));
                } else if (!getReadingExternalEntity()) {
                    reportFatalXMLError(XMLMessages.MSG_PEREFERENCE_WITHIN_MARKUP,
                                        XMLMessages.WFC_PES_IN_INTERNAL_SUBSET,
                                        fEntityReader.addString(nameOffset, nameLength));
                } else {
                    int peNameIndex = fEntityReader.addSymbol(nameOffset, nameLength);
                    fEntityHandler.startReadingFromEntity(peNameIndex, markupDepth(), XMLEntityHandler.ENTITYREF_IN_ENTITYVALUE);
                }
                fEntityValueMark = fEntityReader.currentOffset();
                break;
            }
            case XMLEntityHandler.ENTITYVALUE_RESULT_INVALID_CHAR:
            {
                int offset = fEntityReader.currentOffset();
                if (offset - fEntityValueMark > 0)
                    fEntityReader.append(fLiteralData, fEntityValueMark, offset - fEntityValueMark);
                int invChar = fEntityReader.scanInvalidChar();
                if (fScannerState == SCANNER_STATE_END_OF_INPUT)
                    return -1;
                if (invChar >= 0) {
                    reportFatalXMLError(XMLMessages.MSG_INVALID_CHAR_IN_ENTITYVALUE,
                                        XMLMessages.P9_INVALID_CHARACTER,
                                        Integer.toHexString(invChar));
                }
                fEntityValueMark = fEntityReader.currentOffset();
                break;
            }
            case XMLEntityHandler.ENTITYVALUE_RESULT_END_OF_INPUT:
                // all the work is done by the previous reader, just invoke the next one now.
                break;
            default:
                break;
            }
            result = fEntityReader.scanEntityValue(fReaderId == fEntityValueReader ? qchar : -1, false);
        }
    }
    //
    //
    //
    private boolean checkForPEReference(boolean spaceRequired) throws Exception
    {
        boolean sawSpace = true;
        if (spaceRequired)
            sawSpace = fEntityReader.lookingAtSpace(true);
        fEntityReader.skipPastSpaces();
        if (!getReadingExternalEntity())
            return sawSpace;
        if (!fEntityReader.lookingAtChar('%', true))
            return sawSpace;
        while (true) {
            int nameOffset = fEntityReader.currentOffset();
            fEntityReader.skipPastName(';');
            int nameLength = fEntityReader.currentOffset() - nameOffset;
            if (nameLength == 0) {
                reportFatalXMLError(XMLMessages.MSG_NAME_REQUIRED_IN_PEREFERENCE,
                                    XMLMessages.P69_NAME_REQUIRED);
            } else if (!fEntityReader.lookingAtChar(';', true)) {
                reportFatalXMLError(XMLMessages.MSG_SEMICOLON_REQUIRED_IN_PEREFERENCE,
                                    XMLMessages.P69_SEMICOLON_REQUIRED,
                                    fEntityReader.addString(nameOffset, nameLength));
            } else {
                int peNameIndex = fEntityReader.addSymbol(nameOffset, nameLength);
                int readerDepth = (fScannerState == SCANNER_STATE_CONTENTSPEC) ? parenDepth() : markupDepth();
                fEntityHandler.startReadingFromEntity(peNameIndex, readerDepth, XMLEntityHandler.ENTITYREF_IN_DTD_WITHIN_MARKUP);
            }
            fEntityReader.skipPastSpaces();
            if (!fEntityReader.lookingAtChar('%', true))
                return true;
        }
    }
    //
    // content model stack
    //
    private void initializeContentModelStack(int depth) {
        if (fOpStack == null) {
            fOpStack = new int[8];
            fNodeIndexStack = new int[8];
            fPrevNodeIndexStack = new int[8];
        } else if (depth == fOpStack.length) {
            int[] newStack = new int[depth * 2];
            System.arraycopy(fOpStack, 0, newStack, 0, depth);
            fOpStack = newStack;
            newStack = new int[depth * 2];
            System.arraycopy(fNodeIndexStack, 0, newStack, 0, depth);
            fNodeIndexStack = newStack;
            newStack = new int[depth * 2];
            System.arraycopy(fPrevNodeIndexStack, 0, newStack, 0, depth);
            fPrevNodeIndexStack = newStack;
        }
        fOpStack[depth] = -1;
        fNodeIndexStack[depth] = -1;
        fPrevNodeIndexStack[depth] = -1;
    }

    private boolean validVersionNum(String version) {
        return XMLCharacterProperties.validVersionNum(version);
    }

    private boolean validEncName(String encoding) {
        return XMLCharacterProperties.validEncName(encoding);
    }

    private int validPublicId(String publicId) {
        return XMLCharacterProperties.validPublicId(publicId);
    }

    private void scanElementType(XMLEntityHandler.EntityReader entityReader, 
                                char fastchar, QName element) throws Exception {

        if (!fNamespacesEnabled) {
            element.clear();
            element.localpart = entityReader.scanName(fastchar);
            element.rawname = element.localpart;
            return;
        }
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

    } // scanElementType(XMLEntityHandler.EntityReader,char,QName)

    public void checkForElementTypeWithPEReference(XMLEntityHandler.EntityReader entityReader, 
                                                   char fastchar, QName element) throws Exception {

        if (!fNamespacesEnabled) {
            element.clear();
            element.localpart = entityReader.scanName(fastchar);
            element.rawname = element.localpart;
            return;
        }
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

    } // checkForElementTypeWithPEReference(XMLEntityHandler.EntityReader,char,QName)

    public void checkForAttributeNameWithPEReference(XMLEntityHandler.EntityReader entityReader, 
                                                     char fastchar, QName attribute) throws Exception {

        if (!fNamespacesEnabled) {
            attribute.clear();
            attribute.localpart = entityReader.scanName(fastchar);
            attribute.rawname = attribute.localpart;
            return;
        }

        entityReader.scanQName(fastchar, attribute);
        if (entityReader.lookingAtChar(':', false)) {
            fErrorReporter.reportError(fErrorReporter.getLocator(),
                                       XMLMessages.XML_DOMAIN,
                                       XMLMessages.MSG_TWO_COLONS_IN_QNAME,
                                       XMLMessages.P5_INVALID_CHARACTER,
                                       null,
                                       XMLErrorReporter.ERRORTYPE_FATAL_ERROR);
            entityReader.skipPastNmtoken(' ');
        }

    } // checkForAttributeNameWithPEReference(XMLEntityHandler.EntityReader,char,QName)

    public int checkForNameWithPEReference(XMLEntityHandler.EntityReader entityReader, char fastcheck) throws Exception {
        //
        // REVISIT - what does this have to do with PE references?
        //
        int valueIndex = entityReader.scanName(fastcheck);
        return valueIndex;
    }

    public int checkForNmtokenWithPEReference(XMLEntityHandler.EntityReader entityReader, char fastcheck) throws Exception {
        //
        // REVISIT - what does this have to do with PE references?
        //
        int nameOffset = entityReader.currentOffset();
        entityReader.skipPastNmtoken(fastcheck);
        int nameLength = entityReader.currentOffset() - nameOffset;
        if (nameLength == 0)
            return -1;
        int valueIndex = entityReader.addSymbol(nameOffset, nameLength);
        return valueIndex;
    }

    public int scanDefaultAttValue(QName element, QName attribute, 
                                   int attType, int enumeration) throws Exception {
        /***/
        if (fValidationEnabled && attType == XMLAttributeDecl.TYPE_ID) {
            reportRecoverableXMLError(XMLMessages.MSG_ID_DEFAULT_TYPE_INVALID,
                                      XMLMessages.VC_ID_ATTRIBUTE_DEFAULT,
                                      fStringPool.toString(attribute.rawname));
        }
        /***/
        int defaultAttValue = scanDefaultAttValue(element, attribute);
        if (defaultAttValue == -1)
            return -1;
        // REVISIT
        /***
        if (attType != fCDATASymbol) {
            // REVISIT: Validation. Should we pass in the element or is this
            //          default attribute value normalization?
            defaultAttValue = fValidator.normalizeAttValue(null, attribute, defaultAttValue, attType, enumeration);
        }
        /***/
        return defaultAttValue;
    }

    public int normalizeDefaultAttValue( QName attribute, int defaultAttValue, 
                                         int attType, int enumeration, 
                                         boolean list) throws Exception {
            //
            // Normalize attribute based upon attribute type...
            //
            String attValue = fStringPool.toString(defaultAttValue);

            if (list) {
                StringTokenizer tokenizer = new StringTokenizer(attValue);
                StringBuffer sb = new StringBuffer(attValue.length());
                boolean ok = true;
                if (tokenizer.hasMoreTokens()) {
                    while (true) {
                        String nmtoken = tokenizer.nextToken();
                        if (attType == XMLAttributeDecl.TYPE_NMTOKEN) {
                            if (fValidationEnabled && !XMLCharacterProperties.validNmtoken(nmtoken)) {
                                ok = false;
                            }
                        }
                        else if (attType == XMLAttributeDecl.TYPE_IDREF || attType == XMLAttributeDecl.TYPE_ENTITY) {
                            if (fValidationEnabled && !XMLCharacterProperties.validName(nmtoken)) {
                                ok = false;
                            }
                            // REVISIT: a Hack!!! THis is to pass SUN test /invalid/attr11.xml and attr12.xml
                            // not consistent with XML1.0 spec VC: Attribute Default Legal
                            if (fValidationEnabled && attType == XMLAttributeDecl.TYPE_ENTITY)
                            if (! ((DefaultEntityHandler) fEntityHandler).isUnparsedEntity(defaultAttValue)) {
                                reportRecoverableXMLError(XMLMessages.MSG_ENTITY_INVALID,
                                                          XMLMessages.VC_ENTITY_NAME,
                                                          fStringPool.toString(attribute.rawname), nmtoken);
                            }

                        }
                        sb.append(nmtoken);
                        if (!tokenizer.hasMoreTokens()) {
                            break;
                        }
                        sb.append(' ');
                    }
                }
                String newAttValue = sb.toString();
                if (fValidationEnabled && (!ok || newAttValue.length() == 0)) {
                    reportRecoverableXMLError(XMLMessages.MSG_ATT_DEFAULT_INVALID,
                                              XMLMessages.VC_ATTRIBUTE_DEFAULT_LEGAL,
                                              fStringPool.toString(attribute.rawname), newAttValue);
                }
                if (!newAttValue.equals(attValue)) {
                    defaultAttValue = fStringPool.addString(newAttValue);
                }
                return defaultAttValue;
            }
            else {
                String newAttValue = attValue.trim();

                if (fValidationEnabled) {
                    // REVISIT - can we release the old string?
                    if (newAttValue != attValue) {
                       defaultAttValue = fStringPool.addSymbol(newAttValue);
                    } 
                    else {
                       defaultAttValue = fStringPool.addSymbol(defaultAttValue);
                    }
                    if (attType == XMLAttributeDecl.TYPE_ENTITY ||
                        attType == XMLAttributeDecl.TYPE_ID ||
                        attType == XMLAttributeDecl.TYPE_IDREF ||
                        attType == XMLAttributeDecl.TYPE_NOTATION)  {

                        // REVISIT: A Hack!!! THis is to pass SUN test /invalid/attr11.xml and attr12.xml
                        // not consistent with XML1.0 spec VC: Attribute Default Legal
                        if (attType == XMLAttributeDecl.TYPE_ENTITY)
                        if (! ((DefaultEntityHandler) fEntityHandler).isUnparsedEntity(defaultAttValue)) {
                            reportRecoverableXMLError(XMLMessages.MSG_ENTITY_INVALID,
                                                      XMLMessages.VC_ENTITY_NAME,
                                                      fStringPool.toString(attribute.rawname), newAttValue);
                        }
                        
                        if (!XMLCharacterProperties.validName(newAttValue)) {
                            reportRecoverableXMLError(XMLMessages.MSG_ATT_DEFAULT_INVALID,
                                                      XMLMessages.VC_ATTRIBUTE_DEFAULT_LEGAL,
                                                      fStringPool.toString(attribute.rawname), newAttValue);
                        }

                    }
                    else if (attType == XMLAttributeDecl.TYPE_NMTOKEN ||
                             attType == XMLAttributeDecl.TYPE_ENUMERATION ) {

                        if (!XMLCharacterProperties.validNmtoken(newAttValue)) {
                            reportRecoverableXMLError(XMLMessages.MSG_ATT_DEFAULT_INVALID,
                                                      XMLMessages.VC_ATTRIBUTE_DEFAULT_LEGAL,
                                                      fStringPool.toString(attribute.rawname), newAttValue);
                        }
                    }
                    
                    if (attType == XMLAttributeDecl.TYPE_NOTATION ||
                        attType == XMLAttributeDecl.TYPE_ENUMERATION ) {

                        if ( !fStringPool.stringInList(enumeration, defaultAttValue) ) {
                            reportRecoverableXMLError(XMLMessages.MSG_ATT_DEFAULT_INVALID,
                                                      XMLMessages.VC_ATTRIBUTE_DEFAULT_LEGAL,
                                                      fStringPool.toString(attribute.rawname), newAttValue);
                        }
                    }

                } 
                else if (newAttValue != attValue) {
                    // REVISIT - can we release the old string?
                    defaultAttValue = fStringPool.addSymbol(newAttValue);
                }
            }

            return defaultAttValue;
    }
    /***
    public boolean scanDoctypeDecl(boolean standalone) throws Exception {
        fStandaloneReader = standalone ? fEntityHandler.getReaderId() : -1;
        fDeclsAreExternal = false;
        if (!fDTDScanner.scanDoctypeDecl()) {
            return false;
        }
        if (fDTDScanner.getReadingExternalEntity()) {
            fDTDScanner.scanDecls(true);
        }
        fDTDHandler.endDTD();
        return true;
    }
    /***/

} // class XMLDTDScanner
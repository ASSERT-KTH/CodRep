new Object []{entityName});

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 1999,2000,2001 The Apache Software Foundation.  
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

import org.apache.xerces.impl.XMLEntityScanner;
import org.apache.xerces.impl.XMLErrorReporter;
import org.apache.xerces.impl.msg.XMLMessageFormatter;
import org.apache.xerces.util.SymbolTable;
import org.apache.xerces.util.XMLStringBuffer;
import org.apache.xerces.util.XMLChar;
import org.apache.xerces.xni.XMLAttributes;
import org.apache.xerces.xni.XMLString;
import org.apache.xerces.xni.XNIException;
import org.apache.xerces.xni.parser.XMLComponent;
import org.apache.xerces.xni.parser.XMLComponentManager;
import org.apache.xerces.xni.parser.XMLConfigurationException;

/**
 * This class is responsible for holding scanning methods common to
 * scanning the XML document structure and content as well as the DTD
 * structure and content. Both XMLDocumentScanner and XMLDTDScanner inherit
 * from this base class.
 *
 * <p>
 * This component requires the following features and properties from the
 * component manager that uses it:
 * <ul>
 *  <li>http://xml.org/sax/features/validation</li>
 *  <li>http://apache.org/xml/features/scanner/notify-char-refs</li>
 *  <li>http://apache.org/xml/properties/internal/symbol-table</li>
 *  <li>http://apache.org/xml/properties/internal/error-reporter</li>
 *  <li>http://apache.org/xml/properties/internal/entity-manager</li>
 * </ul>
 *
 * @author Andy Clark, IBM
 * @author Arnaud  Le Hors, IBM
 * @author Eric Ye, IBM
 *
 * @version $Id$
 */
public abstract class XMLScanner 
    implements XMLComponent {

    //
    // Constants
    //

    // feature identifiers

    /** Feature identifier: validation. */
    protected static final String VALIDATION =
        Constants.SAX_FEATURE_PREFIX + Constants.VALIDATION_FEATURE;

    /** Feature identifier: notify character references. */
    protected static final String NOTIFY_CHAR_REFS =
        Constants.XERCES_FEATURE_PREFIX + Constants.NOTIFY_CHAR_REFS_FEATURE;

    // property identifiers

    /** Property identifier: symbol table. */
    protected static final String SYMBOL_TABLE = 
        Constants.XERCES_PROPERTY_PREFIX + Constants.SYMBOL_TABLE_PROPERTY;

    /** Property identifier: error reporter. */
    protected static final String ERROR_REPORTER = 
        Constants.XERCES_PROPERTY_PREFIX + Constants.ERROR_REPORTER_PROPERTY;

    /** Property identifier: entity manager. */
    protected static final String ENTITY_MANAGER = 
        Constants.XERCES_PROPERTY_PREFIX + Constants.ENTITY_MANAGER_PROPERTY;

    // debugging

    /** Debug attribute normalization. */
    protected static final boolean DEBUG_ATTR_NORMALIZATION = false;

    //
    // Data
    //

    // features

    /** 
     * Validation. This feature identifier is:
     * http://xml.org/sax/features/validation
     */
    protected boolean fValidation = false;
    
    /** Character references notification. */
    protected boolean fNotifyCharRefs = false;

    // properties

    /** Symbol table. */
    protected SymbolTable fSymbolTable;

    /** Error reporter. */
    protected XMLErrorReporter fErrorReporter;

    /** Entity manager. */
    protected XMLEntityManager fEntityManager;

    // protected data

    /** Entity scanner. */
    protected XMLEntityScanner fEntityScanner;

    /** Entity depth. */
    protected int fEntityDepth;

    /** Literal value of the last character refence scanned. */
    protected String fCharRefLiteral = null;

    /** Scanning attribute. */
    protected boolean fScanningAttribute;

    // symbols

    /** Symbol: "version". */
    protected String fVersionSymbol;

    /** Symbol: "encoding". */
    protected String fEncodingSymbol;

    /** Symbol: "standalone". */
    protected String fStandaloneSymbol;

    /** Symbol: "amp". */
    protected String fAmpSymbol;

    /** Symbol: "lt". */
    protected String fLtSymbol;

    /** Symbol: "gt". */
    protected String fGtSymbol;

    /** Symbol: "quot". */
    protected String fQuotSymbol;

    /** Symbol: "apos". */
    protected String fAposSymbol;

    // temporary variables

    // NOTE: These objects are private to help prevent accidental modification
    //       of values by a subclass. If there were protected *and* the sub-
    //       modified the values, it would be difficult to track down the real
    //       cause of the bug. By making these private, we avoid this 
    //       possibility.

    /** String. */
    private XMLString fString = new XMLString();

    /** String buffer. */
    private XMLStringBuffer fStringBuffer = new XMLStringBuffer();

    /** String buffer. */
    private XMLStringBuffer fStringBuffer2 = new XMLStringBuffer();

    /** String buffer. */
    private XMLStringBuffer fStringBuffer3 = new XMLStringBuffer();

    //
    // XMLComponent methods
    //

    /**
     * 
     * 
     * @param componentManager The component manager.
     *
     * @throws SAXException Throws exception if required features and
     *                      properties cannot be found.
     */
    public void reset(XMLComponentManager componentManager)
        throws XMLConfigurationException {

        // Xerces properties
        fSymbolTable = (SymbolTable)componentManager.getProperty(SYMBOL_TABLE);
        fErrorReporter = (XMLErrorReporter)componentManager.getProperty(ERROR_REPORTER);
        fEntityManager = (XMLEntityManager)componentManager.getProperty(ENTITY_MANAGER);

        // initialize scanner
        fEntityScanner = fEntityManager.getEntityScanner();
        
        // initialize vars
        fEntityDepth = 0;

        // save built-in entity names
        fVersionSymbol = fSymbolTable.addSymbol("version");
        fEncodingSymbol = fSymbolTable.addSymbol("encoding");
        fStandaloneSymbol = fSymbolTable.addSymbol("standalone");
        fAmpSymbol = fSymbolTable.addSymbol("amp");
        fLtSymbol = fSymbolTable.addSymbol("lt");
        fGtSymbol = fSymbolTable.addSymbol("gt");
        fQuotSymbol = fSymbolTable.addSymbol("quot");
        fAposSymbol = fSymbolTable.addSymbol("apos");
        
        // sax features
        try {
            fValidation = componentManager.getFeature(VALIDATION);
        }
        catch (XMLConfigurationException e) {
            fValidation = false;
        }
        try {
            fNotifyCharRefs = componentManager.getFeature(NOTIFY_CHAR_REFS);
        }
        catch (XMLConfigurationException e) {
            fNotifyCharRefs = false;
        }

    } // reset(XMLComponentManager)

    /**
     * Sets the value of a property during parsing.
     * 
     * @param propertyId 
     * @param value 
     */
    public void setProperty(String propertyId, Object value)
        throws XMLConfigurationException {
        
        // Xerces properties
        if (propertyId.startsWith(Constants.XERCES_PROPERTY_PREFIX)) {
            String property =
               propertyId.substring(Constants.XERCES_PROPERTY_PREFIX.length());
            if (property.equals(Constants.SYMBOL_TABLE_PROPERTY)) {
                fSymbolTable = (SymbolTable)value;
            }
            else if (property.equals(Constants.ERROR_REPORTER_PROPERTY)) {
                fErrorReporter = (XMLErrorReporter)value;
            }
            else if (property.equals(Constants.ENTITY_MANAGER_PROPERTY)) {
                fEntityManager = (XMLEntityManager)value;
            }
            return;
        }

    } // setProperty(String,Object)

    /*
     * Sets the feature of the scanner.
     */
    public void setFeature(String featureId, boolean value)
        throws XMLConfigurationException {
            
        if (VALIDATION.equals(featureId)) {
            fValidation = value;
        } else if (NOTIFY_CHAR_REFS.equals(featureId)) {
            fNotifyCharRefs = value;
        }
    }
    
    //
    // Protected methods
    //

    // common scanning methods

    /**
     * Scans an XML or text declaration.
     * <p>
     * <pre>
     * [23] XMLDecl ::= '<?xml' VersionInfo EncodingDecl? SDDecl? S? '?>'
     * [24] VersionInfo ::= S 'version' Eq (' VersionNum ' | " VersionNum ")
     * [80] EncodingDecl ::= S 'encoding' Eq ('"' EncName '"' |  "'" EncName "'" )
     * [81] EncName ::= [A-Za-z] ([A-Za-z0-9._] | '-')*
     * [32] SDDecl ::= S 'standalone' Eq (("'" ('yes' | 'no') "'")
     *                 | ('"' ('yes' | 'no') '"'))
     *
     * [77] TextDecl ::= '<?xml' VersionInfo? EncodingDecl S? '?>'
     * </pre>
     *
     * @param scanningTextDecl True if a text declaration is to
     *                         be scanned instead of an XML
     *                         declaration.
     * @param pseudoAttributeValues An array of size 3 to return the version,
     *                         encoding and standalone pseudo attribute values
     *                         (in that order).
     *
     * <strong>Note:</strong> This method uses fString, anything in it
     * at the time of calling is lost.
     */
    protected void scanXMLDeclOrTextDecl(boolean scanningTextDecl,
                                         String[] pseudoAttributeValues) 
        throws IOException, XNIException {

        // pseudo-attribute values
        String version = null;
        String encoding = null;
        String standalone = null;

        // scan pseudo-attributes
        final int STATE_VERSION = 0;
        final int STATE_ENCODING = 1;
        final int STATE_STANDALONE = 2;
        final int STATE_DONE = 3;
        int state = STATE_VERSION;
        boolean sawSpace = fEntityScanner.skipSpaces();
        while (fEntityScanner.peekChar() != '?') {
            String name = scanPseudoAttribute(scanningTextDecl, fString);
            switch (state) {
                case STATE_VERSION: {
                    if (name == fVersionSymbol) {
                        if (!sawSpace) {
                            reportFatalError(scanningTextDecl
                                       ? "SpaceRequiredBeforeVersionInTextDecl"
                                       : "SpaceRequiredBeforeVersionInXMLDecl",
                                             null);
                        }
                        version = fString.toString();
                        state = STATE_ENCODING;
                        if (!version.equals("1.0")) {
                            reportFatalError("VersionNotSupported", 
                                             new Object[]{version});
                        }
                    }
                    else if (name == fEncodingSymbol) {
                        if (!scanningTextDecl) {
                            reportFatalError("VersionInfoRequired", null);
                        }
                        if (!sawSpace) {
                            reportFatalError(scanningTextDecl
                                      ? "SpaceRequiredBeforeEncodingInTextDecl"
                                      : "SpaceRequiredBeforeEncodingInXMLDecl",
                                             null);
                        }
                        encoding = fString.toString();
                        state = scanningTextDecl ? STATE_DONE : STATE_STANDALONE;
                    }
                    else {
                        if (scanningTextDecl) {
                            reportFatalError("EncodingDeclRequired", null);
                        }
                        else {
                            reportFatalError("VersionInfoRequired", null);
                        }
                    }
                    break;
                }
                case STATE_ENCODING: {
                    if (name == fEncodingSymbol) {
                        if (!sawSpace) {
                            reportFatalError(scanningTextDecl
                                      ? "SpaceRequiredBeforeEncodingInTextDecl"
                                      : "SpaceRequiredBeforeEncodingInXMLDecl",
                                             null);
                        }
                        encoding = fString.toString();
                        state = scanningTextDecl ? STATE_DONE : STATE_STANDALONE;
                        // TODO: check encoding name; set encoding on
                        //       entity scanner
                    }
                    else if (!scanningTextDecl && name == fStandaloneSymbol) {
                        if (!sawSpace) {
                            reportFatalError("SpaceRequiredBeforeStandalone",
                                             null);
                        }
                        standalone = fString.toString();
                        state = STATE_DONE;
                        if (!standalone.equals("yes") && !standalone.equals("no")) {
                            reportFatalError("SDDeclInvalid", null);
                        }
                    }
                    else {
                        reportFatalError("EncodingDeclRequired", null);
                    }
                    break;
                }
                case STATE_STANDALONE: {
                    if (name == fStandaloneSymbol) {
                        if (!sawSpace) {
                            reportFatalError("SpaceRequiredBeforeStandalone",
                                             null);
                        }
                        standalone = fString.toString();
                        state = STATE_DONE;
                        if (!standalone.equals("yes") && !standalone.equals("no")) {
                            reportFatalError("SDDeclInvalid", null);
                        }
                    }
                    else {
                        reportFatalError("EncodingDeclRequired", null);
                    }
                    break;
                }
                default: {
                    reportFatalError("NoMorePseudoAttributes", null);
                }
            }
            sawSpace = fEntityScanner.skipSpaces();
        }
        if (scanningTextDecl && state != STATE_DONE) {
            reportFatalError("MorePseudoAttributes", null);
        }

        // end
        if (!fEntityScanner.skipChar('?')) {
            reportFatalError("XMLDeclUnterminated", null);
        }
        if (!fEntityScanner.skipChar('>')) {
            reportFatalError("XMLDeclUnterminated", null);

        }

        // fill in return array
        pseudoAttributeValues[0] = version;
        pseudoAttributeValues[1] = encoding;
        pseudoAttributeValues[2] = standalone;

    } // scanXMLDeclOrTextDecl(boolean)

    /**
     * Scans a pseudo attribute.
     *
     * @param scanningTextDecl True if scanning this pseudo-attribute for a
     *                         TextDecl; false if scanning XMLDecl. This 
     *                         flag is needed to report the correct type of
     *                         error.
     * @param value            The string to fill in with the attribute 
     *                         value.
     *
     * @return The name of the attribute
     *
     * <strong>Note:</strong> This method uses fStringBuffer2, anything in it
     * at the time of calling is lost.
     */
    public String scanPseudoAttribute(boolean scanningTextDecl, 
                                      XMLString value) 
        throws IOException, XNIException {

        String name = fEntityScanner.scanName();
        if (name == null) {
            reportFatalError("PseudoAttrNameExpected", null);
        }
        fEntityScanner.skipSpaces();
        if (!fEntityScanner.skipChar('=')) {
            reportFatalError(scanningTextDecl ? "EqRequiredInTextDecl"
                             : "EqRequiredInXMLDecl", new Object[]{name});
        }
        fEntityScanner.skipSpaces();
        int quote = fEntityScanner.peekChar();
        if (quote != '\'' && quote != '"') {
            reportFatalError(scanningTextDecl ? "QuoteRequiredInTextDecl"
                             : "QuoteRequiredInXMLDecl" , new Object[]{name});
        }
        fEntityScanner.scanChar();
        int c = fEntityScanner.scanLiteral(quote, value);
        if (c != quote) {
            fStringBuffer2.clear();
            do {
                fStringBuffer2.append(value);
                if (c != -1) {
                    if (c == '&' || c == '%' || c == '<' || c == ']') {
                        fStringBuffer2.append((char)fEntityScanner.scanChar());
                    }
                    else if (XMLChar.isHighSurrogate(c)) {
                        scanSurrogates(fStringBuffer2);
                    }
                    else if (XMLChar.isInvalid(c)) {
                        String key = scanningTextDecl
                            ? "InvalidCharInTextDecl" : "InvalidCharInXMLDecl";
                        reportFatalError(key,
                                       new Object[] {Integer.toString(c, 16)});
                        fEntityScanner.scanChar();
                    }
                }
                c = fEntityScanner.scanLiteral(quote, value);
            } while (c != quote);
            fStringBuffer2.append(value);
            value.setValues(fStringBuffer2);
        }
        if (!fEntityScanner.skipChar(quote)) {
            reportFatalError(scanningTextDecl ? "CloseQuoteMissingInTextDecl"
                             : "CloseQuoteMissingInXMLDecl",
                             new Object[]{name});
        }

        // return
        return name;

    } // scanPseudoAttribute(XMLString):String
    
    /**
     * Scans a processing instruction.
     * <p>
     * <pre>
     * [16] PI ::= '&lt;?' PITarget (S (Char* - (Char* '?>' Char*)))? '?>'
     * [17] PITarget ::= Name - (('X' | 'x') ('M' | 'm') ('L' | 'l'))
     * </pre>
     * <strong>Note:</strong> This method uses fString, anything in it
     * at the time of calling is lost.
     */
    protected void scanPI() throws IOException, XNIException {

        // target
        String target = fEntityScanner.scanName();
        if (target == null) {
            reportFatalError("PITargetRequired", null);
        }

        // scan data
        scanPIData(target, fString);

    } // scanPI()

    /**
     * Scans a processing data. This is needed to handle the situation
     * where a document starts with a processing instruction whose 
     * target name <em>starts with</em> "xml". (e.g. xmlfoo)
     *
     * <strong>Note:</strong> This method uses fStringBuffer, anything in it
     * at the time of calling is lost.
     *
     * @param target The PI target
     * @param data The string to fill in with the data
     */
    protected void scanPIData(String target, XMLString data) 
        throws IOException, XNIException {

        // check target
        if (target.length() == 3) {
            char c0 = Character.toLowerCase(target.charAt(0));
            char c1 = Character.toLowerCase(target.charAt(1));
            char c2 = Character.toLowerCase(target.charAt(2));
            if (c0 == 'x' && c1 == 'm' && c2 == 'l') {
                reportFatalError("ReservedPITarget", null);
            }
        }

        // spaces
        if (!fEntityScanner.skipSpaces()) {
            if (fEntityScanner.skipString("?>")) {
                // we found the end, there is no data
                data.clear();
                return;
            }
            else {
                // if there is data there should be some space
                reportFatalError("SpaceRequiredInPI", null);
            }
        }

        // data
        if (fEntityScanner.scanData("?>", data)) {
            fStringBuffer.clear();
            do {
                fStringBuffer.append(data);
                int c = fEntityScanner.peekChar();
                if (c != -1) {
                    if (XMLChar.isHighSurrogate(c)) {
                        scanSurrogates(fStringBuffer);
                    }
                    else if (XMLChar.isInvalid(c)) {
                        reportFatalError("InvalidCharInPI",
                                         new Object[]{Integer.toHexString(c)});
                        fEntityScanner.scanChar();
                    }
                }
            } while (fEntityScanner.scanData("?>", data));
            fStringBuffer.append(data);
            data.setValues(fStringBuffer);
        }

    } // scanPIData(String,XMLString)

    /**
     * Scans a comment.
     * <p>
     * <pre>
     * [15] Comment ::= '&lt!--' ((Char - '-') | ('-' (Char - '-')))* '-->'
     * </pre>
     * <p>
     * <strong>Note:</strong> Called after scanning past '&lt;!--'
     * <strong>Note:</strong> This method uses fString, anything in it
     * at the time of calling is lost.
     *
     * @param text The buffer to fill in with the text.
     */
    protected void scanComment(XMLStringBuffer text)
        throws IOException, XNIException {

        // text
        // REVISIT: handle invalid character, eof
        text.clear();
        while (fEntityScanner.scanData("--", fString)) {
            text.append(fString);
            /***/
            int c = fEntityScanner.peekChar();
            if (c != -1) {
                if (XMLChar.isHighSurrogate(c)) {
                    scanSurrogates(text);
                }
                if (XMLChar.isInvalid(c)) {
                    reportFatalError("InvalidCharInComment",
                                     new Object[] { Integer.toHexString(c) }); 
                    fEntityScanner.scanChar();
                }
            }
        }
        text.append(fString);
        if (!fEntityScanner.skipChar('>')) {
            reportFatalError("DashDashInComment", null);
        }

    } // scanComment()

    /**
     * Scans an attribute value and normalizes whitespace converting all
     * whitespace characters to space characters.
     * 
     * [10] AttValue ::= '"' ([^<&"] | Reference)* '"' | "'" ([^<&'] | Reference)* "'"
     *
     * @param value The XMLString to fill in with the value.
     * @param nonNormalizedValue The XMLString to fill in with the 
     *                           non-normalized value.
     * @param atName The name of the attribute being parsed (for error msgs).
     * @param attributes The attributes list for the scanned attribute.
     * @param attrIndex The index of the attribute to use from the list.
     * @param checkEntities true if undeclared entities should be reported as VC violation,  
     *                      false if undeclared entities should be reported as WFC violation.
     *
     * <strong>Note:</strong> This method uses fStringBuffer2, anything in it
     * at the time of calling is lost.
     **/
    protected void scanAttributeValue(XMLString value, 
                                      XMLString nonNormalizedValue,
                                      String atName,
                                      XMLAttributes attributes, int attrIndex,
                                      boolean checkEntities)
        throws IOException, XNIException
    {
        // quote
        int quote = fEntityScanner.peekChar();
        if (quote != '\'' && quote != '"') {
            reportFatalError("OpenQuoteExpected", new Object[]{atName});
        }

        fEntityScanner.scanChar();
        int entityDepth = fEntityDepth;

        int c = fEntityScanner.scanLiteral(quote, value);
        if (DEBUG_ATTR_NORMALIZATION) {
            System.out.println("** scanLiteral -> \""
                               + value.toString() + "\"");
        }
        fStringBuffer2.clear();
        fStringBuffer2.append(value);
        normalizeWhitespace(value);
        if (DEBUG_ATTR_NORMALIZATION) {
            System.out.println("** normalizeWhitespace -> \""
                               + value.toString() + "\"");
        }
        if (c != quote) {
            fScanningAttribute = true;
            fStringBuffer.clear();
            do {
                fStringBuffer.append(value);
                if (DEBUG_ATTR_NORMALIZATION) {
                    System.out.println("** value2: \""
                                       + fStringBuffer.toString() + "\"");
                }
                if (c == '&') {
                    fEntityScanner.skipChar('&');
                    if (entityDepth == fEntityDepth) {
                        fStringBuffer2.append('&');
                    }
                    if (fEntityScanner.skipChar('#')) {
                        if (entityDepth == fEntityDepth) {
                            fStringBuffer2.append('#');
                        }
                        int ch = scanCharReferenceValue(fStringBuffer, fStringBuffer2);
                        if (ch != -1) {
                            if (DEBUG_ATTR_NORMALIZATION) {
                                System.out.println("** value3: \""
                                                   + fStringBuffer.toString()
                                                   + "\"");
                            }
                        }
                    }
                    else {
                        String entityName = fEntityScanner.scanName();
                        if (entityName == null) {
                            reportFatalError("NameRequiredInReference", null);
                        }
                        else if (entityDepth == fEntityDepth) {
                            fStringBuffer2.append(entityName);
                        }
                        if (!fEntityScanner.skipChar(';')) {
                            reportFatalError("SemicolonRequiredInReference",
                                             null);
                        }
                        else if (entityDepth == fEntityDepth) {
                            fStringBuffer2.append(';');
                        }
                        if (entityName == fAmpSymbol) {
                            fStringBuffer.append('&');
                            if (DEBUG_ATTR_NORMALIZATION) {
                                System.out.println("** value5: \""
                                                   + fStringBuffer.toString()
                                                   + "\"");
                            }
                        }
                        else if (entityName == fAposSymbol) {
                            fStringBuffer.append('\'');
                            if (DEBUG_ATTR_NORMALIZATION) {
                                System.out.println("** value7: \""
                                                   + fStringBuffer.toString()
                                                   + "\"");
                            }
                        }
                        else if (entityName == fLtSymbol) {
                            fStringBuffer.append('<');
                            if (DEBUG_ATTR_NORMALIZATION) {
                                System.out.println("** value9: \""
                                                   + fStringBuffer.toString()
                                                   + "\"");
                            }
                        }
                        else if (entityName == fGtSymbol) {
                            fStringBuffer.append('>');
                            if (DEBUG_ATTR_NORMALIZATION) {
                                System.out.println("** valueB: \""
                                                   + fStringBuffer.toString()
                                                   + "\"");
                            }
                        }
                        else if (entityName == fQuotSymbol) {
                            fStringBuffer.append('"');
                            if (DEBUG_ATTR_NORMALIZATION) {
                                System.out.println("** valueD: \""
                                                   + fStringBuffer.toString()
                                                   + "\"");
                            }
                        }
                        else {
                            if (fEntityManager.isExternalEntity(entityName)) {
                                reportFatalError("ReferenceToExternalEntity",
                                                 new Object[] { entityName });
                            }
                            else {
                                if (!fEntityManager.isDeclaredEntity(entityName)) {
                                    //WFC & VC: Entity Declared
                                    if (checkEntities) {
                                        if (fValidation) {
                                            fErrorReporter.reportError(XMLMessageFormatter.XML_DOMAIN,
                                                                       "EntityNotDeclared",
                                                                       new Object[]{entityName},
                                                                       XMLErrorReporter.SEVERITY_ERROR);
                                        }
                                    }
                                    else {
                                        reportFatalError("EntityNotDeclared",
                                                         new Object[]{entityName});
                                    }
                                }
                                fEntityManager.startEntity(entityName, true);
                            }
                        }
                    }
                }
                else if (c == '<') {
                    reportFatalError("LessthanInAttValue",
                                     new Object[] { null, atName });
                }
                else if (c == '%' || c == ']') {
                    fEntityScanner.scanChar();
                    fStringBuffer.append((char)c);
                    if (entityDepth == fEntityDepth) {
                        fStringBuffer2.append((char)c);
                    }
                    if (DEBUG_ATTR_NORMALIZATION) {
                        System.out.println("** valueF: \""
                                           + fStringBuffer.toString() + "\"");
                    }
                }
                else if (c == '\r') {
                    // This happens when parsing the entity replacement text of
                    // an entity which had a character reference &#13; in its
                    // literal entity value. The character is normalized to
                    // #x20 and collapsed per the normal rules.
                    fEntityScanner.scanChar();
                    fStringBuffer.append(' ');
                    fStringBuffer.append((char)c);
                    if (entityDepth == fEntityDepth) {
                        fStringBuffer2.append((char)c);
                    }
                    if (DEBUG_ATTR_NORMALIZATION) {
                        System.out.println("** valueG: \""
                                           + fStringBuffer.toString()
                                           + "\"");
                    }
                }
                else if (c != -1 && XMLChar.isHighSurrogate(c)) {
                    if (scanSurrogates(fStringBuffer3)) {
                        fStringBuffer.append(fStringBuffer3);
                        if (entityDepth == fEntityDepth) {
                            fStringBuffer2.append(fStringBuffer3);
                        }
                        if (DEBUG_ATTR_NORMALIZATION) {
                            System.out.println("** valueI: \""
                                               + fStringBuffer.toString()
                                               + "\"");
                        }
                    }
                }
                else if (c != -1 && XMLChar.isInvalid(c)) {
                    reportFatalError("InvalidCharInAttValue",
                                     new Object[] {Integer.toString(c, 16)});
                    fEntityScanner.scanChar();
                }
                // the following is to handle quotes we get from entities
                // which we must not confused with the end quote
                while (true) {
                    c = fEntityScanner.scanLiteral(quote, value);
                    if (DEBUG_ATTR_NORMALIZATION) {
                        System.out.println("scanLiteral -> \"" +
                                           value.toString() + "\"");
                    }
                    //fStringBuffer2.append(value);
                    normalizeWhitespace(value);
                    if (DEBUG_ATTR_NORMALIZATION) {
                        System.out.println("normalizeWhitespace -> \""
                                           + value.toString()
                                           + "\"");
                    }
                    // this is: !(c == quote && entityDepth != fEntityDepth)
                    if (c != quote || entityDepth == fEntityDepth) {
                        break;
                    }
                    fStringBuffer.append(value);
                    if (DEBUG_ATTR_NORMALIZATION) {
                        System.out.println("** valueK: \""
                                           + fStringBuffer.toString()
                                           + "\"");
                    }
                    fEntityScanner.scanChar();
                    fStringBuffer.append((char)c);
                    if (entityDepth == fEntityDepth) {
                        fStringBuffer2.append((char)c);
                    }
                    if (DEBUG_ATTR_NORMALIZATION) {
                        System.out.println("** valueL: \""
                                           + fStringBuffer.toString()
                                           + "\"");
                    }
                }
            } while (c != quote);
            fStringBuffer.append(value);
            fStringBuffer2.append(value);
            if (DEBUG_ATTR_NORMALIZATION) {
                System.out.println("** valueN: \""
                                   + fStringBuffer.toString() + "\"");
            }
            value.setValues(fStringBuffer);
            fScanningAttribute = false;
        }
        nonNormalizedValue.setValues(fStringBuffer2);

        // quote
        int cquote = fEntityScanner.scanChar();
        if (cquote != quote) {
            reportFatalError("CloseQuoteExpected", new Object[]{atName});
        }
    } // scanAttributeValue()


    /**
     * Scans External ID and return the public and system IDs.
     *
     * @param identifiers An array of size 2 to return the system id,
     *                    and public id (in that order).
     * @param optionalSystemId Specifies whether the system id is optional.
     *
     * <strong>Note:</strong> This method uses fString and fStringBuffer,
     * anything in them at the time of calling is lost.
     */
    protected void scanExternalID(String[] identifiers,
                                  boolean optionalSystemId)
        throws IOException, XNIException {

        String systemId = null;
        String publicId = null;
        if (fEntityScanner.skipString("PUBLIC")) {
            if (!fEntityScanner.skipSpaces()) {
                reportFatalError("SpaceRequiredAfterPUBLIC", null);
            }
            scanPubidLiteral(fString);
            publicId = fString.toString();

            if (!fEntityScanner.skipSpaces() && !optionalSystemId) {
                reportFatalError("SpaceRequiredBetweenPublicAndSystem", null);
            }
        }

        if (publicId != null || fEntityScanner.skipString("SYSTEM")) {
            if (publicId == null && !fEntityScanner.skipSpaces()) {
                reportFatalError("SpaceRequiredAfterSYSTEM", null);
            }
            int quote = fEntityScanner.peekChar();
            if (quote != '\'' && quote != '"') {
                if (publicId != null && optionalSystemId) {
                    // looks like we don't have any system id
                    // simply return the public id
                    identifiers[0] = null;
                    identifiers[1] = publicId;
                    return;
                }
                reportFatalError("QuoteRequiredInSystemID", null);
            }
            fEntityScanner.scanChar();
            XMLString ident = fString;
            if (fEntityScanner.scanLiteral(quote, ident) != quote) {
                fStringBuffer.clear();
                do {
                    fStringBuffer.append(ident);
                    int c = fEntityScanner.peekChar();
                    if (XMLChar.isMarkup(c) || c == ']') {
                        fStringBuffer.append((char)fEntityScanner.scanChar());
                    }
                } while (fEntityScanner.scanLiteral(quote, ident) != quote);
                fStringBuffer.append(ident);
                ident = fStringBuffer;
            }
            systemId = ident.toString();
            if (!fEntityScanner.skipChar(quote)) {
                reportFatalError("SystemIDUnterminated", null);
            }
        }

        // store result in array
        identifiers[0] = systemId;
        identifiers[1] = publicId;
    }


    /**
     * Scans public ID literal.
     *
     * [12] PubidLiteral ::= '"' PubidChar* '"' | "'" (PubidChar - "'")* "'" 
     * [13] PubidChar::= #x20 | #xD | #xA | [a-zA-Z0-9] | [-'()+,./:=?;!*#@$_%]
     *
     * The returned string is normalized according to the following rule,
     * from http://www.w3.org/TR/REC-xml#dt-pubid:
     *
     * Before a match is attempted, all strings of white space in the public
     * identifier must be normalized to single space characters (#x20), and
     * leading and trailing white space must be removed.
     *
     * @param literal The string to fill in with the public ID literal.
     * @returns True on success.
     *
     * <strong>Note:</strong> This method uses fStringBuffer, anything in it at
     * the time of calling is lost.
     */
    protected boolean scanPubidLiteral(XMLString literal)
        throws IOException, XNIException
    {
        int quote = fEntityScanner.scanChar();
        if (quote != '\'' && quote != '"') {
            reportFatalError("QuoteRequiredInPublicID", null);
            return false;
        }

        fStringBuffer.clear();
        // skip leading whitespace
        boolean skipSpace = true;
        boolean dataok = true;
        while (true) {
            int c = fEntityScanner.scanChar();
            if (c == ' ' || c == '\n' || c == '\r') {
                if (!skipSpace) {
                    // take the first whitespace as a space and skip the others
                    fStringBuffer.append(' ');
                    skipSpace = true;
                }
            }
            else if (c == quote) {
                if (skipSpace) {
                    // if we finished on a space let's trim it
                    fStringBuffer.length--;
                }
                literal.setValues(fStringBuffer);
                break;
            }
            else if (XMLChar.isPubid(c)) {
                fStringBuffer.append((char)c);
                skipSpace = false;
            }
            else if (c == -1) {
                reportFatalError("PublicIDUnterminated", null);
                return false;
            }
            else {
                dataok = false;
                reportFatalError("InvalidCharInPublicID",
                                 new Object[]{Integer.toHexString(c)});
            }
        }
        return dataok;
   }


    /**
     * Normalize whitespace in an XMLString converting all whitespace
     * characters to space characters.
     */
    protected void normalizeWhitespace(XMLString value) {
        int end = value.offset + value.length;
        for (int i = value.offset; i < end; i++) {
            int c = value.ch[i];
            if (XMLChar.isSpace(c)) {
                value.ch[i] = ' ';
            }
        }
    }

    //
    // XMLEntityHandler methods
    //

    /**
     * This method notifies of the start of an entity. The document entity
     * has the pseudo-name of "[xml]"; the DTD has the pseudo-name of "[dtd]; 
     * parameter entity names start with '%'; and general entities are just
     * specified by their name.
     * 
     * @param name     The name of the entity.
     * @param publicId The public identifier of the entity if the entity
     *                 is external, null otherwise.
     * @param systemId The system identifier of the entity if the entity
     *                 is external, null otherwise.
     * @param baseSystemId The base system identifier of the entity if
     *                     the entity is external, null otherwise.
     * @param encoding The auto-detected IANA encoding name of the entity
     *                 stream. This value will be null in those situations
     *                 where the entity encoding is not auto-detected (e.g.
     *                 internal entities or a document entity that is
     *                 parsed from a java.io.Reader).
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void startEntity(String name, 
                            String publicId, String systemId,
                            String baseSystemId,
                            String encoding) throws XNIException {

        // keep track of the entity depth
        fEntityDepth++;

    } // startEntity(String,String,String,String,String)

    /**
     * This method notifies the end of an entity. The document entity has
     * the pseudo-name of "[xml]"; the DTD has the pseudo-name of "[dtd]; 
     * parameter entity names start with '%'; and general entities are just
     * specified by their name.
     * 
     * @param name The name of the entity.
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void endEntity(String name) throws XNIException {

        // keep track of the entity depth
        fEntityDepth--;

    } // endEntity(String)

    /**
     * Scans a character reference and append the corresponding chars to the
     * specified buffer.
     *
     * <p>
     * <pre>
     * [66] CharRef ::= '&#' [0-9]+ ';' | '&#x' [0-9a-fA-F]+ ';'
     * </pre>
     *
     * <strong>Note:</strong> This method uses fStringBuffer, anything in it
     * at the time of calling is lost.
     *
     * @param buf the character buffer to append chars to
     * @param buf2 the character buffer to append non-normalized chars to
     *
     * @return the character value or (-1) on conversion failure
     */
    protected int scanCharReferenceValue(XMLStringBuffer buf, XMLStringBuffer buf2) 
        throws IOException, XNIException {

        // scan hexadecimal value
        boolean hex = false;
        if (fEntityScanner.skipChar('x')) {
            if (buf2 != null) { buf2.append('x'); }
            hex = true;
            fStringBuffer3.clear();
            boolean digit = true;
            do {
                int c = fEntityScanner.peekChar();
                digit = (c >= '0' && c <= '9') ||
                        (c >= 'a' && c <= 'f') ||
                        (c >= 'A' && c <= 'F');
                if (digit) {
                    if (buf2 != null) { buf2.append((char)c); }
                    fEntityScanner.scanChar();
                    fStringBuffer3.append((char)c);
                }
            } while (digit);
        }

        // scan decimal value
        else {
            fStringBuffer3.clear();
            boolean digit = true;
            do {
                int c = fEntityScanner.peekChar();
                digit = c >= '0' && c <= '9';
                if (digit) {
                    if (buf2 != null) { buf2.append((char)c); }
                    fEntityScanner.scanChar();
                    fStringBuffer3.append((char)c);
                }
            } while (digit);
        }

        // end
        if (!fEntityScanner.skipChar(';')) {
            reportFatalError("SemicolonRequiredInCharRef", null);
        }
        if (buf2 != null) { buf2.append(';'); }
        
        // convert string to number
        int value = -1;
        try {
            value = Integer.parseInt(fStringBuffer3.toString(),
                                     hex ? 16 : 10);
        }
        catch (NumberFormatException e) {
            // let -1 value drop through
        }

        // character reference must be a valid XML character
        if (!XMLChar.isValid(value)) {
            reportFatalError("InvalidCharRef",
                             new Object[]{Integer.toString(value, 16)}); 
        }

        // append corresponding chars to the given buffer
        if (!XMLChar.isSupplemental(value)) {
            buf.append((char) value);
        }
        else {
            // character is supplemental, split it into surrogate chars
            buf.append(XMLChar.highSurrogate(value));
            buf.append(XMLChar.lowSurrogate(value));
        }

        // char refs notification code
        if (fNotifyCharRefs && value != -1) {
            String literal = "#" + (hex ? "x" : "") + fStringBuffer3.toString();
            if (!fScanningAttribute) {
                fCharRefLiteral = literal;
            }
        }
                
        return value;
    }


    /**
     * Scans surrogates and append them to the specified buffer.
     * <p>
     * <strong>Note:</strong> This assumes the current char has already been
     * identified as a high surrogate.
     *
     * @param buf The StringBuffer to append the read surrogates to.
     * @returns True if it succeeded.
     */
    protected boolean scanSurrogates(XMLStringBuffer buf)
        throws IOException, XNIException {

        int high = fEntityScanner.scanChar();
        int low = fEntityScanner.peekChar();
        if (!XMLChar.isLowSurrogate(low)) {
            reportFatalError("InvalidCharInContent",
                             new Object[] {Integer.toString(high, 16)});
            return false;
        }
        fEntityScanner.scanChar();

        // convert surrogates to supplemental character
        int c = XMLChar.supplemental((char)high, (char)low);

        // supplemental character must be a valid XML character
        if (!XMLChar.isValid(c)) {
            reportFatalError("InvalidCharInContent",
                             new Object[]{Integer.toString(c, 16)}); 
            return false;
        }

        // fill in the buffer
        buf.append((char)high);
        buf.append((char)low);

        return true;

    } // scanSurrogates():boolean


    /**
     * Convenience function used in all XML scanners.
     */
    protected void reportFatalError(String msgId, Object[] args)
        throws XNIException {
        fErrorReporter.reportError(XMLMessageFormatter.XML_DOMAIN,
                                   msgId, args,
                                   XMLErrorReporter.SEVERITY_FATAL_ERROR);
    }

} // class XMLScanner
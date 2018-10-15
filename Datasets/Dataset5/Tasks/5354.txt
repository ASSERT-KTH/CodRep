return (version.equals("1.1") || version.equals("1.0"));

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 1999-2003 The Apache Software Foundation.
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

import java.io.IOException;

import org.apache.xerces.impl.msg.XMLMessageFormatter;
import org.apache.xerces.util.XML11Char;
import org.apache.xerces.util.XMLChar;
import org.apache.xerces.util.XMLStringBuffer;
import org.apache.xerces.xni.XMLAttributes;
import org.apache.xerces.xni.XMLString;
import org.apache.xerces.xni.XNIException;

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
public class XML11DocumentScannerImpl
    extends XMLDocumentScannerImpl {


    /** Array of 3 strings. */
    private String[] fStrings = new String[3];

    /** String. */
    private XMLString fString = new XMLString();

    /** String buffer. */
    private XMLStringBuffer fStringBuffer = new XMLStringBuffer();
    private XMLStringBuffer fStringBuffer2 = new XMLStringBuffer();
    private XMLStringBuffer fStringBuffer3 = new XMLStringBuffer();

    //
    // Constructors
    //

    /** Default constructor. */
    public XML11DocumentScannerImpl() {super();} // <init>()

    //
    // overridden methods
    //

    // XMLDocumentFragmentImpl methods

    /**
     * Scans element content.
     *
     * @return Returns the next character on the stream.
     */
    protected int scanContent() throws IOException, XNIException {

        XMLString content = fString;
        int c = fEntityScanner.scanContent(content);
        if (c == '\r' || c == 0x85 || c == 0x2028) {
            // happens when there is the character reference &#13;
            // but scanContent doesn't do entity expansions...
            // is this *really* necessary???  - NG
            fEntityScanner.scanChar();
            fStringBuffer.clear();
            fStringBuffer.append(fString);
            fStringBuffer.append((char)c);
            content = fStringBuffer;
            c = -1;
        }
        if (fDocumentHandler != null && content.length > 0) {
            fDocumentHandler.characters(content, null);
        }

        if (c == ']' && fString.length == 0) {
            fStringBuffer.clear();
            fStringBuffer.append((char)fEntityScanner.scanChar());
            // remember where we are in case we get an endEntity before we
            // could flush the buffer out - this happens when we're parsing an
            // entity which ends with a ]
            fInScanContent = true;
            //
            // We work on a single character basis to handle cases such as:
            // ']]]>' which we might otherwise miss.
            //
            if (fEntityScanner.skipChar(']')) {
                fStringBuffer.append(']');
                while (fEntityScanner.skipChar(']')) {
                    fStringBuffer.append(']');
                }
                if (fEntityScanner.skipChar('>')) {
                    reportFatalError("CDEndInContent", null);
                }
            }
            if (fDocumentHandler != null && fStringBuffer.length != 0) {
                fDocumentHandler.characters(fStringBuffer, null);
            }
            fInScanContent = false;
            c = -1;
        }
        return c;

    } // scanContent():int

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
     * <p> this was overridden to allow for version="1.1"</p>
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

        boolean dataFoundForTarget = false;
        boolean sawSpace = fEntityScanner.skipSpaces();
        while (fEntityScanner.peekChar() != '?') {
            dataFoundForTarget = true;
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
                        if (!version.equals("1.0") || !version.equals("1.1")) {
                            // REVISIT: XML REC says we should throw an error in such cases.
                            // some may object the throwing of fatalError.
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
                    }
                    else if (!scanningTextDecl && name == fStandaloneSymbol) {
                        if (!sawSpace) {
                            reportFatalError("SpaceRequiredBeforeStandalone",
                                             null);
                        }
                        standalone = fString.toString();
                        state = STATE_DONE;
                        if (!standalone.equals("yes") && !standalone.equals("no")) {
                            reportFatalError("SDDeclInvalid", new Object[] {standalone});
                        }
                    }
                    else {
                        reportFatalError("EncodingDeclRequired", new Object[] {standalone});
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
                            reportFatalError("SDDeclInvalid", new Object[] {standalone});
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
        // REVISIT: should we remove this error reporting?
        if (scanningTextDecl && state != STATE_DONE) {
            reportFatalError("MorePseudoAttributes", null);
        }
        
        // If there is no data in the xml or text decl then we fail to report error 
        // for version or encoding info above.
        if (scanningTextDecl) {
            if (!dataFoundForTarget && encoding == null) {
                reportFatalError("EncodingDeclRequired", null);
            }
        }
        else {
            if (!dataFoundForTarget && version == null) {
                reportFatalError("VersionInfoRequired", null);
            }
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
                                      boolean checkEntities,String eleName)
        throws IOException, XNIException
    {
        // quote
        int quote = fEntityScanner.peekChar();
        if (quote != '\'' && quote != '"') {
            reportFatalError("OpenQuoteExpected", new Object[]{eleName,atName});
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
                                             new Object []{entityName});
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
                                     new Object[] { eleName, atName });
                    fEntityScanner.scanChar();
                    if (entityDepth == fEntityDepth) {
                        fStringBuffer2.append((char)c);
                    }
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
                // note that none of these characters should ever get through
                // XML11EntityScanner.  Not sure why
                // this check was originally necessary.  - NG
                else if (c == '\n' || c == '\r' || c == 0x85 || c == 0x2028) {
                    fEntityScanner.scanChar();
                    fStringBuffer.append(' ');
                    if (entityDepth == fEntityDepth) {
                        fStringBuffer2.append('\n');
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
                else if (c != -1 && XML11Char.isXML11Invalid(c)) {
                    reportFatalError("InvalidCharInAttValue",
                                     new Object[] {eleName, atName, Integer.toString(c, 16)});
                    fEntityScanner.scanChar();
                    if (entityDepth == fEntityDepth) {
                        fStringBuffer2.append((char)c);
                    }
                }
                c = fEntityScanner.scanLiteral(quote, value);
                if (entityDepth == fEntityDepth) {
                    fStringBuffer2.append(value);
                }
                normalizeWhitespace(value);
            } while (c != quote || entityDepth != fEntityDepth);
            fStringBuffer.append(value);
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
            reportFatalError("CloseQuoteExpected", new Object[]{eleName,atName});
        }
    } // scanAttributeValue()

    //
    // XMLScanner methods
    //
    // NOTE:  this is a carbon copy of the code in XML11DTDScannerImpl;
    // we need to override these methods in both places.  
    // this needs to be refactored!!!  - NG
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
     * @return True on success.
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
            // REVISIT:  none of these except \n and 0x20 should make it past the entity scanner
            if (c == ' ' || c == '\n' || c == '\r' || c == 0x85 || c == 0x2028) {
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

    // returns true if the given character is not
    // valid with respect to the version of
    // XML understood by this scanner.
    protected boolean isInvalid(int value) {
        return (XML11Char.isXML11Invalid(value)); 
    } // isInvalid(int):  boolean 

    // returns true if the given character is not
    // valid or may not be used outside a character reference 
    // with respect to the version of XML understood by this scanner.
    protected boolean isInvalidLiteral(int value) {
        return (!XML11Char.isXML11ValidLiteral(value)); 
    } // isInvalidLiteral(int):  boolean

    // returns true if the given character is 
    // a valid nameChar with respect to the version of
    // XML understood by this scanner.
    protected boolean isValidNameChar(int value) {
        return (XML11Char.isXML11Name(value)); 
    } // isValidNameChar(int):  boolean

    // returns true if the given character is 
    // a valid nameStartChar with respect to the version of
    // XML understood by this scanner.
    protected boolean isValidNameStartChar(int value) {
        return (XML11Char.isXML11NameStart(value)); 
    } // isValidNameStartChar(int):  boolean

    protected boolean versionSupported(String version) {
        return version.equals("1.1");
    } // versionSupported(String):  boolean

} // class XML11DocumentScannerImpl
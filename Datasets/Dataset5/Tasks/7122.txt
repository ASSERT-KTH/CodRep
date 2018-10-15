protected static final boolean DEFAULT_SCHEMA_VALIDATION = false;

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 2000 The Apache Software Foundation.  All rights
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

package sax;

import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.io.UnsupportedEncodingException;
import java.io.Writer;

import org.xml.sax.AttributeList;
import org.xml.sax.Attributes;
import org.xml.sax.ContentHandler;
import org.xml.sax.DocumentHandler;
import org.xml.sax.DTDHandler;
import org.xml.sax.ErrorHandler;
import org.xml.sax.Locator;
import org.xml.sax.Parser;
import org.xml.sax.SAXException;
import org.xml.sax.SAXNotRecognizedException;
import org.xml.sax.SAXNotSupportedException;
import org.xml.sax.SAXParseException;
import org.xml.sax.XMLReader;
import org.xml.sax.helpers.DefaultHandler;
import org.xml.sax.helpers.ParserAdapter;
import org.xml.sax.helpers.ParserFactory;
import org.xml.sax.helpers.XMLReaderFactory;
import org.xml.sax.ext.DeclHandler;
import org.xml.sax.ext.LexicalHandler;

/**
 * Provides a complete trace of SAX2 events for files parsed. This is
 * useful for making sure that a SAX parser implementation faithfully
 * communicates all information in the document to the SAX handlers.
 *
 * @author Andy Clark, IBM
 * @author Arnaud Le Hors, IBM
 *
 * @version $Id$
 */
public class DocumentTracer
    extends DefaultHandler
    implements ContentHandler, DTDHandler, ErrorHandler, // SAX2
               DeclHandler, LexicalHandler, // SAX2 extensions
               DocumentHandler // deprecated in SAX2
    {

    //
    // Constants
    //

    // feature ids

    /** Namespaces feature id (http://xml.org/sax/features/namespaces). */
    protected static final String NAMESPACES_FEATURE_ID = "http://xml.org/sax/features/namespaces";

    /** Validation feature id (http://xml.org/sax/features/validation). */
    protected static final String VALIDATION_FEATURE_ID = "http://xml.org/sax/features/validation";

    /** Schema validation feature id (http://apache.org/xml/features/validation/schema). */
    protected static final String SCHEMA_VALIDATION_FEATURE_ID = "http://apache.org/xml/features/validation/schema";

    /** Schema full checking feature id (http://apache.org/xml/features/validation/schema-full-checking). */
    protected static final String SCHEMA_FULL_CHECKING_FEATURE_ID = "http://apache.org/xml/features/validation/schema-full-checking";

    // property ids

    /** Lexical handler property id (http://xml.org/sax/properties/lexical-handler). */
    protected static final String LEXICAL_HANDLER_PROPERTY_ID = "http://xml.org/sax/properties/lexical-handler";

    // default settings

    /** Default parser name. */
    protected static final String DEFAULT_PARSER_NAME = "org.apache.xerces.parsers.SAXParser";

    /** Default namespaces support (true). */
    protected static final boolean DEFAULT_NAMESPACES = true;

    /** Default validation support (false). */
    protected static final boolean DEFAULT_VALIDATION = false;

    /** Default Schema validation support (true). */
    protected static final boolean DEFAULT_SCHEMA_VALIDATION = true;

    /** Default Schema full checking support (false). */
    protected static final boolean DEFAULT_SCHEMA_FULL_CHECKING = false;

    //
    // Data
    //

    /** Print writer. */
    protected PrintWriter fOut;

    /** Indent level. */
    protected int fIndent;

    //
    // Constructors
    //

    /** Default constructor. */
    public DocumentTracer() {
        setOutput(new PrintWriter(System.out));
    } // <init>()

    //
    // Public methods
    //

    /** Sets the output stream for printing. */
    public void setOutput(OutputStream stream, String encoding)
        throws UnsupportedEncodingException {

        if (encoding == null) {
            encoding = "UTF8";
        }

        Writer writer = new OutputStreamWriter(stream, encoding);
        fOut = new PrintWriter(writer);

    } // setOutput(OutputStream,String)

    /** Sets the output writer. */
    public void setOutput(Writer writer) {

        fOut = writer instanceof PrintWriter
             ? (PrintWriter)writer : new PrintWriter(writer);

    } // setOutput(Writer)

    //
    // ContentHandler and DocumentHandler methods
    //

    /** Set document locator. */
    public void setDocumentLocator(Locator locator) {

        printIndent();
        fOut.print("setDocumentLocator(");
        fOut.print("locator=");
        fOut.print(locator);
        fOut.println(')');
        fOut.flush();

    } // setDocumentLocator(Locator)

    /** Start document. */
    public void startDocument() throws SAXException {

        fIndent = 0;
        printIndent();
        fOut.println("startDocument()");
        fOut.flush();
        fIndent++;

    } // startDocument()

    /** Processing instruction. */
    public void processingInstruction(String target, String data)
        throws SAXException {

        printIndent();
        fOut.print("processingInstruction(");
        fOut.print("target=");
        printQuotedString(target);
        fOut.print(',');
        fOut.print("data=");
        printQuotedString(data);
        fOut.println(')');
        fOut.flush();

    } // processingInstruction(String,String)

    /** Characters. */
    public void characters(char[] ch, int offset, int length)
        throws SAXException {

        printIndent();
        fOut.print("characters(");
        fOut.print("text=");
        printQuotedString(ch, offset, length);
        fOut.println(')');
        fOut.flush();

    } // characters(char[],int,int)

    /** Ignorable whitespace. */
    public void ignorableWhitespace(char[] ch, int offset, int length)
        throws SAXException {

        printIndent();
        fOut.print("ignorableWhitespace(");
        fOut.print("text=");
        printQuotedString(ch, offset, length);
        fOut.println(')');
        fOut.flush();

    } // ignorableWhitespace(char[],int,int)

    /** End document. */
    public void endDocument() throws SAXException {

        fIndent--;
        printIndent();
        fOut.println("endDocument()");
        fOut.flush();

    } // endDocument()

    //
    // ContentHandler methods
    //

    /** Start prefix mapping. */
    public void startPrefixMapping(String prefix, String uri)
        throws SAXException {

        printIndent();
        fOut.print("startPrefixMapping(");
        fOut.print("prefix=");
        printQuotedString(prefix);
        fOut.print(',');
        fOut.print("uri=");
        printQuotedString(uri);
        fOut.println(')');
        fOut.flush();

    } // startPrefixMapping(String,String)

    /** Start element. */
    public void startElement(String uri, String localName, String qname,
                             Attributes attributes) throws SAXException {

        printIndent();
        fOut.print("startElement(");
        fOut.print("uri=");
        printQuotedString(uri);
        fOut.print(',');
        fOut.print("localName=");
        printQuotedString(localName);
        fOut.print(',');
        fOut.print("qname=");
        printQuotedString(qname);
        fOut.print(',');
        fOut.print("attributes=");
        if (attributes == null) {
            fOut.println("null");
        }
        else {
            fOut.print('{');
            int length = attributes.getLength();
            for (int i = 0; i < length; i++) {
                if (i > 0) {
                    fOut.print(',');
                }
                String attrLocalName = attributes.getLocalName(i);
                String attrQName = attributes.getQName(i);
                String attrURI = attributes.getURI(i);
                String attrType = attributes.getType(i);
                String attrValue = attributes.getValue(i);
                fOut.print('{');
                fOut.print("uri=");
                printQuotedString(attrURI);
                fOut.print(',');
                fOut.print("localName=");
                printQuotedString(attrLocalName);
                fOut.print(',');
                fOut.print("qname=");
                printQuotedString(attrQName);
                fOut.print(',');
                fOut.print("type=");
                printQuotedString(attrType);
                fOut.print(',');
                fOut.print("value=");
                printQuotedString(attrValue);
                fOut.print('}');
            }
            fOut.print('}');
        }
        fOut.println(')');
        fOut.flush();
        fIndent++;

    } // startElement(String,String,String,Attributes)

    /** End element. */
    public void endElement(String uri, String localName, String qname)
        throws SAXException {

        fIndent--;
        printIndent();
        fOut.print("endElement(");
        fOut.print("uri=");
        printQuotedString(uri);
        fOut.print(',');
        fOut.print("localName=");
        printQuotedString(localName);
        fOut.print(',');
        fOut.print("qname=");
        printQuotedString(qname);
        fOut.println(')');
        fOut.flush();

    } // endElement(String,String,String)

    /** End prefix mapping. */
    public void endPrefixMapping(String prefix) throws SAXException {

        printIndent();
        fOut.print("endPrefixMapping(");
        fOut.print("prefix=");
        printQuotedString(prefix);
        fOut.println(')');
        fOut.flush();

    } // endPrefixMapping(String)

    /** Skipped entity. */
    public void skippedEntity(String name) throws SAXException {

        printIndent();
        fOut.print("skippedEntity(");
        fOut.print("name=");
        printQuotedString(name);
        fOut.println(')');
        fOut.flush();

    } // skippedEntity(String)

    //
    // DocumentHandler methods
    //

    /** Start element. */
    public void startElement(String name, AttributeList attributes)
        throws SAXException {

        printIndent();
        fOut.print("startElement(");
        fOut.print("name=");
        printQuotedString(name);
        fOut.print(',');
        fOut.print("attributes=");
        if (attributes == null) {
            fOut.println("null");
        }
        else {
            fOut.print('{');
            int length = attributes.getLength();
            for (int i = 0; i < length; i++) {
                if (i > 0) {
                    System.out.print(',');
                }
                String attrName = attributes.getName(i);
                String attrType = attributes.getType(i);
                String attrValue = attributes.getValue(i);
                fOut.print('{');
                fOut.print("name=");
                printQuotedString(attrName);
                fOut.print(',');
                fOut.print("type=");
                printQuotedString(attrType);
                fOut.print(',');
                fOut.print("value=");
                printQuotedString(attrValue);
                fOut.print('}');
            }
            fOut.print('}');
        }
        fOut.println(')');
        fOut.flush();
        fIndent++;

    } // startElement(String,AttributeList)

    /** End element. */
    public void endElement(String name) throws SAXException {

        fIndent--;
        printIndent();
        fOut.print("endElement(");
        fOut.print("name=");
        printQuotedString(name);
        fOut.println(')');
        fOut.flush();

    } // endElement(String)

    //
    // DTDHandler methods
    //

    /** Notation declaration. */
    public void notationDecl(String name, String publicId, String systemId)
        throws SAXException {

        printIndent();
        fOut.print("notationDecl(");
        fOut.print("name=");
        printQuotedString(name);
        fOut.print(',');
        fOut.print("publicId=");
        printQuotedString(publicId);
        fOut.print(',');
        fOut.print("systemId=");
        printQuotedString(systemId);
        fOut.println(')');
        fOut.flush();

    } // notationDecl(String,String,String)

    /** Unparsed entity declaration. */
    public void unparsedEntityDecl(String name,
                                   String publicId, String systemId,
                                   String notationName) throws SAXException {
        printIndent();
        fOut.print("unparsedEntityDecl(");
        fOut.print("name=");
        printQuotedString(name);
        fOut.print(',');
        fOut.print("publicId=");
        printQuotedString(publicId);
        fOut.print(',');
        fOut.print("systemId=");
        printQuotedString(systemId);
        fOut.print(',');
        fOut.print("notationName=");
        printQuotedString(notationName);
        fOut.println(')');
        fOut.flush();

    } // unparsedEntityDecl(String,String,String,String)

    //
    // LexicalHandler methods
    //

    /** Start DTD. */
    public void startDTD(String name, String publicId, String systemId)
        throws SAXException {

        printIndent();
        fOut.print("startDTD(");
        fOut.print("name=");
        printQuotedString(name);
        fOut.print(',');
        fOut.print("publicId=");
        printQuotedString(publicId);
        fOut.print(',');
        fOut.print("systemId=");
        printQuotedString(systemId);
        fOut.println(')');
        fOut.flush();
        fIndent++;

    } // startDTD(String,String,String)

    /** Start entity. */
    public void startEntity(String name) throws SAXException {

        printIndent();
        fOut.print("startEntity(");
        fOut.print("name=");
        printQuotedString(name);
        fOut.println(')');
        fOut.flush();
        fIndent++;

    } // startEntity(String)

    /** Start CDATA section. */
    public void startCDATA() throws SAXException {

        printIndent();
        fOut.println("startCDATA()");
        fOut.flush();
        fIndent++;

    } // startCDATA()

    /** End CDATA section. */
    public void endCDATA() throws SAXException {

        fIndent--;
        printIndent();
        fOut.println("endCDATA()");
        fOut.flush();

    } // endCDATA()

    /** Comment. */
    public void comment(char[] ch, int offset, int length)
        throws SAXException {

        printIndent();
        fOut.print("comment(");
        fOut.print("text=");
        printQuotedString(ch, offset, length);
        fOut.println(')');
        fOut.flush();

    } // comment(char[],int,int)

    /** End entity. */
    public void endEntity(String name) throws SAXException {

        fIndent--;
        printIndent();
        fOut.print("endEntity(");
        fOut.print("name=");
        printQuotedString(name);
        fOut.println(')');

    } // endEntity(String)

    /** End DTD. */
    public void endDTD() throws SAXException {

        fIndent--;
        printIndent();
        fOut.println("endDTD()");
        fOut.flush();

    } // endDTD()

    //
    // DeclHandler methods
    //

    /** Element declaration. */
    public void elementDecl(String name, String contentModel)
        throws SAXException {

        printIndent();
        fOut.print("elementDecl(");
        fOut.print("name=");
        printQuotedString(name);
        fOut.print(',');
        fOut.print("contentModel=");
        printQuotedString(contentModel);
        fOut.println(')');
        fOut.flush();

    } // elementDecl(String,String)

    /** Attribute declaration. */
    public void attributeDecl(String elementName, String attributeName,
                              String type, String valueDefault,
                              String value) throws SAXException {

        printIndent();
        fOut.print("attributeDecl(");
        fOut.print("elementName=");
        printQuotedString(elementName);
        fOut.print(',');
        fOut.print("attributeName=");
        printQuotedString(attributeName);
        fOut.print(',');
        fOut.print("type=");
        printQuotedString(type);
        fOut.print(',');
        fOut.print("valueDefault=");
        printQuotedString(valueDefault);
        fOut.print(',');
        fOut.print("value=");
        printQuotedString(value);
        fOut.println(')');
        fOut.flush();

    } // attributeDecl(String,String,String,String,String)

    /** Internal entity declaration. */
    public void internalEntityDecl(String name, String text)
        throws SAXException {

        printIndent();
        fOut.print("internalEntityDecl(");
        fOut.print("name=");
        printQuotedString(name);
        fOut.print(',');
        fOut.print("text=");
        printQuotedString(text);
        fOut.println(')');
        fOut.flush();

    } // internalEntityDecl(String,String)

    /** External entity declaration. */
    public void externalEntityDecl(String name,
                                   String publicId, String systemId)
        throws SAXException {

        printIndent();
        fOut.print("externalEntityDecl(");
        fOut.print("name=");
        printQuotedString(name);
        fOut.print(',');
        fOut.print("publicId=");
        printQuotedString(publicId);
        fOut.print(',');
        fOut.print("systemId=");
        printQuotedString(systemId);
        fOut.println(')');
        fOut.flush();

    } // externalEntityDecl(String,String,String)

    //
    // ErrorHandler methods
    //

    /** Warning. */
    public void warning(SAXParseException ex) throws SAXException {
        printError("Warning", ex);
    } // warning(SAXParseException)

    /** Error. */
    public void error(SAXParseException ex) throws SAXException {
        printError("Error", ex);
    } // error(SAXParseException)

    /** Fatal error. */
    public void fatalError(SAXParseException ex) throws SAXException {
        printError("Fatal Error", ex);
        throw ex;
    } // fatalError(SAXParseException)

    //
    // Protected methods
    //

    /** Print quoted string. */
    protected void printQuotedString(String s) {

        if (s == null) {
            fOut.print("null");
            return;
        }

        fOut.print('"');
        int length = s.length();
        for (int i = 0; i < length; i++) {
            char c = s.charAt(i);
            normalizeAndPrint(c);
        }
        fOut.print('"');

    } // printQuotedString(String)

    /** Print quoted string. */
    protected void printQuotedString(char[] ch, int offset, int length) {

        fOut.print('"');
        for (int i = 0; i < length; i++) {
            normalizeAndPrint(ch[offset + i]);
        }
        fOut.print('"');

    } // printQuotedString(char[],int,int)

    /** Normalize and print. */
    protected void normalizeAndPrint(char c) {

        switch (c) {
            case '\n': {
                fOut.print("\\n");
                break;
            }
            case '\r': {
                fOut.print("\\r");
                break;
            }
            case '\t': {
                fOut.print("\\t");
                break;
            }
            case '\\': {
                fOut.print("\\\\");
                break;
            }
            case '"': {
                fOut.print("\\\"");
                break;
            }
            default: {
                fOut.print(c);
            }
        }

    } // normalizeAndPrint(char)

    /** Prints the error message. */
    protected void printError(String type, SAXParseException ex) {

        System.err.print("[");
        System.err.print(type);
        System.err.print("] ");
        String systemId = ex.getSystemId();
        if (systemId != null) {
            int index = systemId.lastIndexOf('/');
            if (index != -1)
                systemId = systemId.substring(index + 1);
            System.err.print(systemId);
        }
        System.err.print(':');
        System.err.print(ex.getLineNumber());
        System.err.print(':');
        System.err.print(ex.getColumnNumber());
        System.err.print(": ");
        System.err.print(ex.getMessage());
        System.err.println();
        System.err.flush();

    } // printError(String,SAXParseException)

    /** Prints the indent. */
    protected void printIndent() {
        for (int i = 0; i < fIndent; i++) {
            fOut.print(' ');
        }
    }

    //
    // MAIN
    //

    /** Main. */
    public static void main(String[] argv) throws Exception {

        // is there anything to do?
        if (argv.length == 0) {
            printUsage();
            System.exit(1);
        }

        // variables
        DocumentTracer tracer = new DocumentTracer();
        PrintWriter out = new PrintWriter(System.out);
        XMLReader parser = null;
        boolean namespaces = DEFAULT_NAMESPACES;
        boolean validation = DEFAULT_VALIDATION;
        boolean schemaValidation = DEFAULT_SCHEMA_VALIDATION;
        boolean schemaFullChecking = DEFAULT_SCHEMA_FULL_CHECKING;

        // process arguments
        for (int i = 0; i < argv.length; i++) {
            String arg = argv[i];
            if (arg.startsWith("-")) {
                String option = arg.substring(1);
                if (option.equals("p")) {
                    // get parser name
                    if (++i == argv.length) {
                        System.err.println("error: Missing argument to -p option.");
                    }
                    String parserName = argv[i];

                    // create parser
                    try {
                        parser = XMLReaderFactory.createXMLReader(parserName);
                    }
                    catch (Exception e) {
                        try {
                            Parser sax1Parser = ParserFactory.makeParser(parserName);
                            parser = new ParserAdapter(sax1Parser);
                            System.err.println("warning: Features and properties not supported on SAX1 parsers.");
                        }
                        catch (Exception ex) {
                            parser = null;
                            System.err.println("error: Unable to instantiate parser ("+parserName+")");
                        }
                    }
                    continue;
                }
                if (option.equalsIgnoreCase("n")) {
                    namespaces = option.equals("n");
                    continue;
                }
                if (option.equalsIgnoreCase("v")) {
                    validation = option.equals("v");
                    continue;
                }
                if (option.equalsIgnoreCase("s")) {
                    schemaValidation = option.equals("s");
                    continue;
                }
                if (option.equalsIgnoreCase("f")) {
                    schemaFullChecking = option.equals("f");
                    continue;
                }
                if (option.equals("h")) {
                    printUsage();
                    continue;
                }
            }

            // use default parser?
            if (parser == null) {

                // create parser
                try {
                    parser = XMLReaderFactory.createXMLReader(DEFAULT_PARSER_NAME);
                }
                catch (Exception e) {
                    System.err.println("error: Unable to instantiate parser ("+DEFAULT_PARSER_NAME+")");
                    continue;
                }
            }

            // set parser features
            try {
                parser.setFeature(NAMESPACES_FEATURE_ID, namespaces);
            }
            catch (SAXException e) {
                System.err.println("warning: Parser does not support feature ("+NAMESPACES_FEATURE_ID+")");
            }
            try {
                parser.setFeature(VALIDATION_FEATURE_ID, validation);
            }
            catch (SAXException e) {
                System.err.println("warning: Parser does not support feature ("+VALIDATION_FEATURE_ID+")");
            }
            try {
                parser.setFeature(SCHEMA_VALIDATION_FEATURE_ID, schemaValidation);
            }
            catch (SAXNotRecognizedException e) {
                // ignore
            }
            catch (SAXNotSupportedException e) {
                System.err.println("warning: Parser does not support feature ("+SCHEMA_VALIDATION_FEATURE_ID+")");
            }
            try {
                parser.setFeature(SCHEMA_FULL_CHECKING_FEATURE_ID, schemaFullChecking);
            }
            catch (SAXNotRecognizedException e) {
                // ignore
            }
            catch (SAXNotSupportedException e) {
                System.err.println("warning: Parser does not support feature ("+SCHEMA_FULL_CHECKING_FEATURE_ID+")");
            }

            // set handlers
            parser.setDTDHandler(tracer);
            parser.setErrorHandler(tracer);
            if (parser instanceof XMLReader) {
                parser.setContentHandler(tracer);
                try {
                    parser.setProperty("http://xml.org/sax/properties/declaration-handler", tracer);
                }
                catch (SAXException e) {
                    e.printStackTrace(System.err);
                }
                try {
                    parser.setProperty("http://xml.org/sax/properties/lexical-handler", tracer);
                }
                catch (SAXException e) {
                    e.printStackTrace(System.err);
                }
            }
            else {
                ((Parser)parser).setDocumentHandler(tracer);
            }

            // parse file
            try {
                parser.parse(arg);
            }
            catch (SAXParseException e) {
                // ignore
            }
            catch (Exception e) {
                System.err.println("error: Parse error occurred - "+e.getMessage());
                if (e instanceof SAXException) {
                    e = ((SAXException)e).getException();
                }
                e.printStackTrace(System.err);
            }
        }

    } // main(String[])

    //
    // Private static methods
    //

    /** Prints the usage. */
    private static void printUsage() {

        System.err.println("usage: java sax.DocumentTracer (options) uri ...");
        System.err.println();

        System.err.println("options:");
        System.err.println("  -p name  Select parser by name.");
        System.err.println("  -n | -N  Turn on/off namespace processing.");
        System.err.println("  -v | -V  Turn on/off validation.");
        System.err.println("  -s | -S  Turn on/off Schema validation support.");
        System.err.println("           NOTE: Not supported by all parsers.");
        System.err.println("  -f  | -F Turn on/off Schema full checking.");
        System.err.println("           NOTE: Requires use of -s and not supported by all parsers.");
        System.err.println("  -h       This help screen.");
        System.err.println();

        System.err.println("defaults:");
        System.err.println("  Parser:     "+DEFAULT_PARSER_NAME);
        System.err.print("  Namespaces: ");
        System.err.println(DEFAULT_NAMESPACES ? "on" : "off");
        System.err.print("  Validation: ");
        System.err.println(DEFAULT_VALIDATION ? "on" : "off");
        System.err.print("  Schema:     ");
        System.err.println(DEFAULT_SCHEMA_VALIDATION ? "on" : "off");
        System.err.print("  Schema full checking:     ");
        System.err.println(DEFAULT_SCHEMA_FULL_CHECKING ? "on" : "off");

    } // printUsage()

} // class DocumentTracer
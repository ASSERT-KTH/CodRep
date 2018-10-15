version = (String) getXMLVersion.invoke(fLocator, (Object[]) null);

/*
 * Copyright 1999-2004 The Apache Software Foundation.
 * 
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * 
 *      http://www.apache.org/licenses/LICENSE-2.0
 * 
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package sax;

import java.lang.reflect.Method;

import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.io.UnsupportedEncodingException;

import sax.helpers.AttributesImpl;

import org.xml.sax.Attributes;
import org.xml.sax.Locator;
import org.xml.sax.Parser;
import org.xml.sax.SAXException;
import org.xml.sax.SAXNotRecognizedException;
import org.xml.sax.SAXNotSupportedException;
import org.xml.sax.SAXParseException;
import org.xml.sax.XMLReader;
import org.xml.sax.ext.LexicalHandler;
import org.xml.sax.helpers.DefaultHandler;
import org.xml.sax.helpers.ParserAdapter;
import org.xml.sax.helpers.ParserFactory;
import org.xml.sax.helpers.XMLReaderFactory;

/**
 * A sample SAX2 writer. This sample program illustrates how to
 * register a SAX2 ContentHandler and receive the callbacks in
 * order to print a document that is parsed.
 *
 * @author Andy Clark, IBM
 *
 * @version $Id$
 */
public class Writer
    extends DefaultHandler
    implements LexicalHandler {

    //
    // Constants
    //

    // feature ids

    /** Namespaces feature id (http://xml.org/sax/features/namespaces). */
    protected static final String NAMESPACES_FEATURE_ID = "http://xml.org/sax/features/namespaces";

    /** Namespace prefixes feature id (http://xml.org/sax/features/namespace-prefixes). */
    protected static final String NAMESPACE_PREFIXES_FEATURE_ID = "http://xml.org/sax/features/namespace-prefixes";

    /** Validation feature id (http://xml.org/sax/features/validation). */
    protected static final String VALIDATION_FEATURE_ID = "http://xml.org/sax/features/validation";

    /** Schema validation feature id (http://apache.org/xml/features/validation/schema). */
    protected static final String SCHEMA_VALIDATION_FEATURE_ID = "http://apache.org/xml/features/validation/schema";

    /** Schema full checking feature id (http://apache.org/xml/features/validation/schema-full-checking). */
    protected static final String SCHEMA_FULL_CHECKING_FEATURE_ID = "http://apache.org/xml/features/validation/schema-full-checking";

    /** Dynamic validation feature id (http://apache.org/xml/features/validation/dynamic). */
    protected static final String DYNAMIC_VALIDATION_FEATURE_ID = "http://apache.org/xml/features/validation/dynamic";
    
    /** Load external DTD feature id (http://apache.org/xml/features/nonvalidating/load-external-dtd). */
    protected static final String LOAD_EXTERNAL_DTD_FEATURE_ID = "http://apache.org/xml/features/nonvalidating/load-external-dtd";

    // property ids

    /** Lexical handler property id (http://xml.org/sax/properties/lexical-handler). */
    protected static final String LEXICAL_HANDLER_PROPERTY_ID = "http://xml.org/sax/properties/lexical-handler";

    // default settings

    /** Default parser name. */
    protected static final String DEFAULT_PARSER_NAME = "org.apache.xerces.parsers.SAXParser";

    /** Default namespaces support (true). */
    protected static final boolean DEFAULT_NAMESPACES = true;
    
    /** Default namespace prefixes (false). */
    protected static final boolean DEFAULT_NAMESPACE_PREFIXES = false;

    /** Default validation support (false). */
    protected static final boolean DEFAULT_VALIDATION = false;
    
    /** Default load external DTD (true). */
    protected static final boolean DEFAULT_LOAD_EXTERNAL_DTD = true;

    /** Default Schema validation support (false). */
    protected static final boolean DEFAULT_SCHEMA_VALIDATION = false;

    /** Default Schema full checking support (false). */
    protected static final boolean DEFAULT_SCHEMA_FULL_CHECKING = false;
    
    /** Default dynamic validation support (false). */
    protected static final boolean DEFAULT_DYNAMIC_VALIDATION = false;

    /** Default canonical output (false). */
    protected static final boolean DEFAULT_CANONICAL = false;

    //
    // Data
    //

    /** Print writer. */
    protected PrintWriter fOut;

    /** Canonical output. */
    protected boolean fCanonical;

    /** Element depth. */
    protected int fElementDepth;
    
    /** Document locator. */
    protected Locator fLocator;
    
    /** Processing XML 1.1 document. */
    protected boolean fXML11;
    
    /** In CDATA section. */
    protected boolean fInCDATA;

    //
    // Constructors
    //

    /** Default constructor. */
    public Writer() {
    } // <init>()

    //
    // Public methods
    //

    /** Sets whether output is canonical. */
    public void setCanonical(boolean canonical) {
        fCanonical = canonical;
    } // setCanonical(boolean)

    /** Sets the output stream for printing. */
    public void setOutput(OutputStream stream, String encoding)
        throws UnsupportedEncodingException {

        if (encoding == null) {
            encoding = "UTF8";
        }

        java.io.Writer writer = new OutputStreamWriter(stream, encoding);
        fOut = new PrintWriter(writer);

    } // setOutput(OutputStream,String)

    /** Sets the output writer. */
    public void setOutput(java.io.Writer writer) {

        fOut = writer instanceof PrintWriter
             ? (PrintWriter)writer : new PrintWriter(writer);

    } // setOutput(java.io.Writer)

    //
    // ContentHandler methods
    //
    
    /** Set Document Locator. */
    public void setDocumentLocator(Locator locator) {
    	fLocator = locator;
    } // setDocumentLocator(Locator)
    	
    /** Start document. */
    public void startDocument() throws SAXException {

        fElementDepth = 0;
        fXML11 = false;
        fInCDATA = false;
        
    } // startDocument()

    /** Processing instruction. */
    public void processingInstruction(String target, String data)
        throws SAXException {

        if (fElementDepth > 0) {
            fOut.print("<?");
            fOut.print(target);
            if (data != null && data.length() > 0) {
                fOut.print(' ');
                fOut.print(data);
            }
            fOut.print("?>");
            fOut.flush();
        }

    } // processingInstruction(String,String)

    /** Start element. */
    public void startElement(String uri, String local, String raw,
                             Attributes attrs) throws SAXException {

        // Root Element
        if (fElementDepth == 0) {
            if (fLocator != null) {
                fXML11 = "1.1".equals(getVersion());
                fLocator = null;
            }

            // The XML declaration cannot be printed in startDocument because
            // the version reported by the Locator cannot be relied on until after
            // the XML declaration in the instance document has been read.
            if (!fCanonical) {
                if (fXML11) {
                    fOut.println("<?xml version=\"1.1\" encoding=\"UTF-8\"?>");
                }
                else {
                    fOut.println("<?xml version=\"1.0\" encoding=\"UTF-8\"?>");
                }
                fOut.flush();
            }
        }
        
        fElementDepth++;
        fOut.print('<');
        fOut.print(raw);
        if (attrs != null) {
            attrs = sortAttributes(attrs);
            int len = attrs.getLength();
            for (int i = 0; i < len; i++) {
                fOut.print(' ');
                fOut.print(attrs.getQName(i));
                fOut.print("=\"");
                normalizeAndPrint(attrs.getValue(i), true);
                fOut.print('"');
            }
        }
        fOut.print('>');
        fOut.flush();

    } // startElement(String,String,String,Attributes)

    /** Characters. */
    public void characters(char ch[], int start, int length)
        throws SAXException {

        if (!fInCDATA) {
            normalizeAndPrint(ch, start, length, false);
        }
        else {
            for (int i = 0; i < length; ++i) {
            	fOut.print(ch[start+i]);
            }
        }
        fOut.flush();

    } // characters(char[],int,int);

    /** Ignorable whitespace. */
    public void ignorableWhitespace(char ch[], int start, int length)
        throws SAXException {

        characters(ch, start, length);
        fOut.flush();

    } // ignorableWhitespace(char[],int,int);

    /** End element. */
    public void endElement(String uri, String local, String raw)
        throws SAXException {

        fElementDepth--;
        fOut.print("</");
        fOut.print(raw);
        fOut.print('>');
        fOut.flush();

    } // endElement(String)

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
    // LexicalHandler methods
    //

    /** Start DTD. */
    public void startDTD(String name, String publicId, String systemId)
        throws SAXException {
    } // startDTD(String,String,String)

    /** End DTD. */
    public void endDTD() throws SAXException {
    } // endDTD()

    /** Start entity. */
    public void startEntity(String name) throws SAXException {
    } // startEntity(String)

    /** End entity. */
    public void endEntity(String name) throws SAXException {
    } // endEntity(String)

    /** Start CDATA section. */
    public void startCDATA() throws SAXException {
        if (!fCanonical) {
            fOut.print("<![CDATA[");
            fInCDATA = true;
        }
    } // startCDATA()

    /** End CDATA section. */
    public void endCDATA() throws SAXException {
        if (!fCanonical) {
            fInCDATA = false;
            fOut.print("]]>");
        }
    } // endCDATA()

    /** Comment. */
    public void comment(char ch[], int start, int length) throws SAXException {
        if (!fCanonical && fElementDepth > 0) {
            fOut.print("<!--");
            for (int i = 0; i < length; ++i) {
                fOut.print(ch[start+i]);
            }
            fOut.print("-->");
            fOut.flush();
        }
    } // comment(char[],int,int)

    //
    // Protected methods
    //

    /** Returns a sorted list of attributes. */
    protected Attributes sortAttributes(Attributes attrs) {

        AttributesImpl attributes = new AttributesImpl();

        int len = (attrs != null) ? attrs.getLength() : 0;
        for (int i = 0; i < len; i++) {
            String name = attrs.getQName(i);
            int count = attributes.getLength();
            int j = 0;
            while (j < count) {
                if (name.compareTo(attributes.getQName(j)) < 0) {
                    break;
                }
                j++;
            }
            attributes.insertAttributeAt(j, name, attrs.getType(i),
                                         attrs.getValue(i));
        }

        return attributes;

    } // sortAttributes(AttributeList):AttributeList

    /** Normalizes and prints the given string. */
    protected void normalizeAndPrint(String s, boolean isAttValue) {

        int len = (s != null) ? s.length() : 0;
        for (int i = 0; i < len; i++) {
            char c = s.charAt(i);
            normalizeAndPrint(c, isAttValue);
        }

    } // normalizeAndPrint(String,boolean)

    /** Normalizes and prints the given array of characters. */
    protected void normalizeAndPrint(char[] ch, int offset, int length, boolean isAttValue) {
        for (int i = 0; i < length; i++) {
            normalizeAndPrint(ch[offset + i], isAttValue);
        }
    } // normalizeAndPrint(char[],int,int,boolean)

    /** Normalizes and print the given character. */
    protected void normalizeAndPrint(char c, boolean isAttValue) {

        switch (c) {
            case '<': {
                fOut.print("&lt;");
                break;
            }
            case '>': {
                fOut.print("&gt;");
                break;
            }
            case '&': {
                fOut.print("&amp;");
                break;
            }
            case '"': {
                // A '"' that appears in character data 
                // does not need to be escaped.
                if (isAttValue) {
                    fOut.print("&quot;");
                }
                else {
                    fOut.print("\"");
                }
                break;
            }
            case '\r': {
            	// If CR is part of the document's content, it
            	// must not be printed as a literal otherwise
            	// it would be normalized to LF when the document
            	// is reparsed.
            	fOut.print("&#xD;");
            	break;
            }
            case '\n': {
                if (fCanonical) {
                    fOut.print("&#xA;");
                    break;
                }
                // else, default print char
            }
            default: {
           	// In XML 1.1, control chars in the ranges [#x1-#x1F, #x7F-#x9F] must be escaped.
            	//
            	// Escape space characters that would be normalized to #x20 in attribute values
            	// when the document is reparsed.
            	//
            	// Escape NEL (0x85) and LSEP (0x2028) that appear in content 
            	// if the document is XML 1.1, since they would be normalized to LF 
            	// when the document is reparsed.
            	if (fXML11 && ((c >= 0x01 && c <= 0x1F && c != 0x09 && c != 0x0A) 
            	    || (c >= 0x7F && c <= 0x9F) || c == 0x2028)
            	    || isAttValue && (c == 0x09 || c == 0x0A)) {
            	    fOut.print("&#x");
            	    fOut.print(Integer.toHexString(c).toUpperCase());
            	    fOut.print(";");
                }
                else {
                    fOut.print(c);
                }        
            }
        }
    } // normalizeAndPrint(char,boolean)

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

    /** Extracts the XML version from the Locator. */
    protected String getVersion() {
        if (fLocator == null) {
            return null;
        }
        String version = null;
        Method getXMLVersion = null;
        try {
            getXMLVersion = fLocator.getClass().getMethod("getXMLVersion", new Class[]{});
            // If Locator implements Locator2, this method will exist.
            if (getXMLVersion != null) {
                version = (String) getXMLVersion.invoke(fLocator, null);
            }
        } 
        catch (Exception e) { 
            // Either this locator object doesn't have 
            // this method, or we're on an old JDK.
        }
        return version;
    } // getVersion()

    //
    // Main
    //

    /** Main program entry point. */
    public static void main(String argv[]) {

        // is there anything to do?
        if (argv.length == 0) {
            printUsage();
            System.exit(1);
        }

        // variables
        Writer writer = null;
        XMLReader parser = null;
        boolean namespaces = DEFAULT_NAMESPACES;
        boolean namespacePrefixes = DEFAULT_NAMESPACE_PREFIXES;
        boolean validation = DEFAULT_VALIDATION;
        boolean externalDTD = DEFAULT_LOAD_EXTERNAL_DTD;
        boolean schemaValidation = DEFAULT_SCHEMA_VALIDATION;
        boolean schemaFullChecking = DEFAULT_SCHEMA_FULL_CHECKING;
        boolean dynamicValidation = DEFAULT_DYNAMIC_VALIDATION;
        boolean canonical = DEFAULT_CANONICAL;

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
                            e.printStackTrace(System.err);
                        }
                    }
                    continue;
                }
                if (option.equalsIgnoreCase("n")) {
                    namespaces = option.equals("n");
                    continue;
                }
                if (option.equalsIgnoreCase("np")) {
                    namespacePrefixes = option.equals("np");
                    continue;
                }
                if (option.equalsIgnoreCase("v")) {
                    validation = option.equals("v");
                    continue;
                }
                if (option.equalsIgnoreCase("xd")) {
                    externalDTD = option.equals("xd");
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
                if (option.equalsIgnoreCase("dv")) {
                    dynamicValidation = option.equals("dv");
                    continue;
                }
                if (option.equalsIgnoreCase("c")) {
                    canonical = option.equals("c");
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
                    e.printStackTrace(System.err);
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
                parser.setFeature(NAMESPACE_PREFIXES_FEATURE_ID, namespacePrefixes);
            }
            catch (SAXException e) {
                System.err.println("warning: Parser does not support feature ("+NAMESPACE_PREFIXES_FEATURE_ID+")");
            }
            try {
                parser.setFeature(VALIDATION_FEATURE_ID, validation);
            }
            catch (SAXException e) {
                System.err.println("warning: Parser does not support feature ("+VALIDATION_FEATURE_ID+")");
            }
            try {
                parser.setFeature(LOAD_EXTERNAL_DTD_FEATURE_ID, externalDTD);
            }
            catch (SAXNotRecognizedException e) {
                System.err.println("warning: Parser does not recognize feature ("+LOAD_EXTERNAL_DTD_FEATURE_ID+")");
            }
            catch (SAXNotSupportedException e) {
                System.err.println("warning: Parser does not support feature ("+LOAD_EXTERNAL_DTD_FEATURE_ID+")");
            }
            try {
                parser.setFeature(SCHEMA_VALIDATION_FEATURE_ID, schemaValidation);
            }
            catch (SAXNotRecognizedException e) {
                System.err.println("warning: Parser does not recognize feature ("+SCHEMA_VALIDATION_FEATURE_ID+")");
            }
            catch (SAXNotSupportedException e) {
                System.err.println("warning: Parser does not support feature ("+SCHEMA_VALIDATION_FEATURE_ID+")");
            }
            try {
                parser.setFeature(SCHEMA_FULL_CHECKING_FEATURE_ID, schemaFullChecking);
            }
            catch (SAXNotRecognizedException e) {
                System.err.println("warning: Parser does not recognize feature ("+SCHEMA_FULL_CHECKING_FEATURE_ID+")");
            }
            catch (SAXNotSupportedException e) {
                System.err.println("warning: Parser does not support feature ("+SCHEMA_FULL_CHECKING_FEATURE_ID+")");
            }
            try {
                parser.setFeature(DYNAMIC_VALIDATION_FEATURE_ID, dynamicValidation);
            }
            catch (SAXNotRecognizedException e) {
                System.err.println("warning: Parser does not recognize feature ("+DYNAMIC_VALIDATION_FEATURE_ID+")");
            }
            catch (SAXNotSupportedException e) {
                System.err.println("warning: Parser does not support feature ("+DYNAMIC_VALIDATION_FEATURE_ID+")");
            }
            
            // setup writer
            if (writer == null) {
                writer = new Writer();
                try {
                    writer.setOutput(System.out, "UTF8");
                }
                catch (UnsupportedEncodingException e) {
                    System.err.println("error: Unable to set output. Exiting.");
                    System.exit(1);
                }
            }

            // set parser
            parser.setContentHandler(writer);
            parser.setErrorHandler(writer);
            try {
                parser.setProperty(LEXICAL_HANDLER_PROPERTY_ID, writer);
            }
            catch (SAXException e) {
                // ignore
            }

            // parse file
            writer.setCanonical(canonical);
            try {
                parser.parse(arg);
            }
            catch (SAXParseException e) {
                // ignore
            }
            catch (Exception e) {
                System.err.println("error: Parse error occurred - "+e.getMessage());
                if (e instanceof SAXException) {
                    Exception nested = ((SAXException)e).getException();
                    if (nested != null) {
                        e = nested;
                    } 
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

        System.err.println("usage: java sax.Writer (options) uri ...");
        System.err.println();

        System.err.println("options:");
        System.err.println("  -p name     Select parser by name.");
        System.err.println("  -n | -N     Turn on/off namespace processing.");
        System.err.println("  -np | -NP   Turn on/off namespace prefixes.");
        System.err.println("              NOTE: Requires use of -n.");
        System.err.println("  -v | -V     Turn on/off validation.");
        System.err.println("  -xd | -XD   Turn on/off loading of external DTDs.");
        System.err.println("              NOTE: Always on when -v in use and not supported by all parsers.");
        System.err.println("  -s | -S     Turn on/off Schema validation support.");
        System.err.println("              NOTE: Not supported by all parsers.");
        System.err.println("  -f  | -F    Turn on/off Schema full checking.");
        System.err.println("              NOTE: Requires use of -s and not supported by all parsers.");
        System.err.println("  -dv | -DV   Turn on/off dynamic validation.");
        System.err.println("              NOTE: Not supported by all parsers.");
        System.err.println("  -c | -C     Turn on/off Canonical XML output.");
        System.err.println("              NOTE: This is not W3C canonical output.");
        System.err.println("  -h          This help screen.");
        System.err.println();

        System.err.println("defaults:");
        System.err.println("  Parser:     "+DEFAULT_PARSER_NAME);
        System.err.print("  Namespaces: ");
        System.err.println(DEFAULT_NAMESPACES ? "on" : "off");
        System.err.print("  Prefixes:   ");
        System.err.println(DEFAULT_NAMESPACE_PREFIXES ? "on" : "off");
        System.err.print("  Validation: ");
        System.err.println(DEFAULT_VALIDATION ? "on" : "off");
        System.err.print("  Load External DTD: ");
        System.err.println(DEFAULT_LOAD_EXTERNAL_DTD ? "on" : "off");
        System.err.print("  Schema:     ");
        System.err.println(DEFAULT_SCHEMA_VALIDATION ? "on" : "off");
        System.err.print("  Schema full checking:     ");
        System.err.println(DEFAULT_SCHEMA_FULL_CHECKING ? "on" : "off");
        System.err.print("  Dynamic:    ");
        System.err.println(DEFAULT_DYNAMIC_VALIDATION ? "on" : "off");
        System.err.print("  Canonical:  ");
        System.err.println(DEFAULT_CANONICAL ? "on" : "off");

    } // printUsage()

} // class Writer
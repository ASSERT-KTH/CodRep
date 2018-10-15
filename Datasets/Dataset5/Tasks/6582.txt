"  -v | -V  Turn on/off validation [default=off]",

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 1999 The Apache Software Foundation.  All rights 
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

import util.Arguments;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.io.UnsupportedEncodingException;

import sax.helpers.AttributeListImpl;

import org.xml.sax.AttributeList;
import org.xml.sax.HandlerBase;
import org.xml.sax.Parser;
import org.xml.sax.SAXException;
import org.xml.sax.SAXParseException;
import org.xml.sax.helpers.ParserFactory;
import org.xml.sax.XMLReader;



/**
 * A sample SAX writer. This sample program illustrates how to
 * register a SAX DocumentHandler and receive the callbacks in
 * order to print a document that is parsed.
 *
 * @version
 */
public class SAXWriter 
extends HandlerBase {

    //
    // Constants
    //

    /** Default parser name. */
    private static final String 
    DEFAULT_PARSER_NAME = "org.apache.xerces.parsers.SAXParser";

    private static boolean setValidation    = false; //defaults
    private static boolean setNameSpaces    = true;
    private static boolean setSchemaSupport = true;




    //
    // Data
    //

    /** Print writer. */
    protected PrintWriter out;

    /** Canonical output. */
    protected boolean canonical;

    //
    // Constructors
    //

    /** Default constructor. */
    public SAXWriter(boolean canonical) throws UnsupportedEncodingException {
        this(null, canonical);
    }

    protected SAXWriter(String encoding, boolean canonical) throws UnsupportedEncodingException {

        if (encoding == null) {
            encoding = "UTF8";
        }

        out = new PrintWriter(new OutputStreamWriter(System.out, encoding));
        this.canonical = canonical;

    } // <init>(String,boolean)

    //
    // Public static methods
    //

    /** Prints the output from the SAX callbacks. */
    public static void print(String parserName, String uri, boolean canonical) {

        try {
            HandlerBase handler = new SAXWriter(canonical);

            Parser parser = ParserFactory.makeParser(parserName);


            if ( parser instanceof XMLReader ){
                ((XMLReader)parser).setFeature( "http://xml.org/sax/features/validation", 
                                                setValidation);
                ((XMLReader)parser).setFeature( "http://xml.org/sax/features/namespaces",
                                                setNameSpaces );
                ((XMLReader)parser).setFeature( "http://apache.org/xml/features/validation/schema",
                                                setSchemaSupport );

            }




            parser.setDocumentHandler(handler);
            parser.setErrorHandler(handler);
            parser.parse(uri);
        } catch (Exception e) {
            e.printStackTrace(System.err);
        }

    } // print(String,String,boolean)

    //
    // DocumentHandler methods
    //

    /** Processing instruction. */
    public void processingInstruction(String target, String data) {

        out.print("<?");
        out.print(target);
        if (data != null && data.length() > 0) {
            out.print(' ');
            out.print(data);
        }
        out.print("?>");

    } // processingInstruction(String,String)

    /** Start document. */
    public void startDocument() {

        if (!canonical) {
            out.println("<?xml version=\"1.0\" encoding=\"UTF-8\"?>");
        }

    } // startDocument()

    /** Start element. */
    public void startElement(String name, AttributeList attrs) {

        out.print('<');
        out.print(name);
        if (attrs != null) {
            attrs = sortAttributes(attrs);
            int len = attrs.getLength();
            for (int i = 0; i < len; i++) {
                out.print(' ');
                out.print(attrs.getName(i));
                out.print("=\"");
                out.print(normalize(attrs.getValue(i)));
                out.print('"');
            }
        }
        out.print('>');

    } // startElement(String,AttributeList)

    /** Characters. */
    public void characters(char ch[], int start, int length) {

        out.print(normalize(new String(ch, start, length)));

    } // characters(char[],int,int);

    /** Ignorable whitespace. */
    public void ignorableWhitespace(char ch[], int start, int length) {

        characters(ch, start, length);

    } // ignorableWhitespace(char[],int,int);

    /** End element. */
    public void endElement(String name) {

        out.print("</");
        out.print(name);
        out.print('>');

    } // endElement(String)

    /** End document. */
    public void endDocument() {

        out.flush();

    } // endDocument()

    //
    // ErrorHandler methods
    //

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
    public void fatalError(SAXParseException ex) throws SAXException {
        System.err.println("[Fatal Error] "+
                           getLocationString(ex)+": "+
                           ex.getMessage());
        throw ex;
    }

    /** Returns a string of the location. */
    private String getLocationString(SAXParseException ex) {
        StringBuffer str = new StringBuffer();

        String systemId = ex.getSystemId();
        if (systemId != null) {
            int index = systemId.lastIndexOf('/');
            if (index != -1)
                systemId = systemId.substring(index + 1);
            str.append(systemId);
        }
        str.append(':');
        str.append(ex.getLineNumber());
        str.append(':');
        str.append(ex.getColumnNumber());

        return str.toString();

    } // getLocationString(SAXParseException):String

    //
    // Protected static methods
    //

    /** Normalizes the given string. */
    protected String normalize(String s) {
        StringBuffer str = new StringBuffer();

        int len = (s != null) ? s.length() : 0;
        for (int i = 0; i < len; i++) {
            char ch = s.charAt(i);
            switch (ch) {
            case '<': {
                    str.append("&lt;");
                    break;
                }
            case '>': {
                    str.append("&gt;");
                    break;
                }
            case '&': {
                    str.append("&amp;");
                    break;
                }
            case '"': {
                    str.append("&quot;");
                    break;
                }
            case '\r':
            case '\n': {
                    if (canonical) {
                        str.append("&#");
                        str.append(Integer.toString(ch));
                        str.append(';');
                        break;
                    }
                    // else, default append char
                }
            default: {
                    str.append(ch);
                }
            }
        }

        return str.toString();

    } // normalize(String):String

    /** Returns a sorted list of attributes. */
    protected AttributeList sortAttributes(AttributeList attrs) {

        AttributeListImpl attributes = new AttributeListImpl();
        int len = (attrs != null) ? attrs.getLength() : 0;
        for (int i = 0; i < len; i++) {
            String name = attrs.getName(i);
            int count = attributes.getLength();
            int j = 0;
            while (j < count) {
                if (name.compareTo(attributes.getName(j)) < 0) {
                    break;
                }
                j++;
            }
            attributes.insertAttributeAt(j, name, attrs.getType(i), 
                                         attrs.getValue(i));
        }

        return attributes;

    } // sortAttributes(AttributeList):AttributeList

    //
    // Main
    //

    /** Main program entry point. */
    public static void main(String argv[]) {
        ///
        Arguments argopt = new Arguments();

        argopt.setUsage( new String[] {
                             "usage: java sax.SAXWriter (options) uri ...","",
                             "options:",
                             "  -n | -N  Turn on/off namespace [default=on]",
                             "  -v | -V  Turn on/off validation [default=on]",
                             "  -s | -S  Turn on/off Schema support [default=on]",
                             "  -c       Canonical XML output.",
                             "  -h       This help screen."} );




        // is there anything to do?
        if (argv.length == 0) {
            argopt.printUsage();
            System.exit(1);
        }

        // vars
        boolean canonical  = false;
        String  parserName = DEFAULT_PARSER_NAME;


        argopt.parseArgumentTokens(argv, new char[] { 'p'} );

        int   c;
        String arg = null; 
        while ( ( arg =  argopt.getlistFiles() ) != null ) {

            outer:
            while ( (c =  argopt.getArguments()) != -1 ){
                switch (c) {
                case 'c':
                    canonical     = true;
                    break;
                case 'C':
                    canonical     = false;
                    break;
                case 'v':
                    setValidation = true;
                    break;
                case 'V':
                    setValidation = false;
                    break;
                case 'N':
                    setNameSpaces = false;
                    break;
                case 'n':
                    setNameSpaces = true;
                    break;
                case 'p':
                    parserName = argopt.getStringParameter();
                    break;
                case 's':
                    setSchemaSupport = true;
                    break;
                case 'S':
                    setSchemaSupport = false;
                    break;
                case '?':
                case 'h':
                case '-':
                    argopt.printUsage();
                    System.exit(1);
                    break;
                case -1:
                    break outer;
                default:
                    break;
                }
            }
            // print 
            System.err.println(arg+':');
            print(parserName, arg, canonical);
        }
    } // main(String[])

} // class SAXWriter
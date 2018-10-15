//System.out.println( "c =" + c );

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

package sax;                    

import  util.Arguments;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.io.UnsupportedEncodingException;

import org.xml.sax.Attributes;
import org.xml.sax.SAXException;
import org.xml.sax.SAXParseException;
import org.xml.sax.XMLReader;
import org.xml.sax.helpers.DefaultHandler;

/**
 * A sample SAX2 counter. This sample program illustrates how to
 * register a SAX2 ContentHandler and receive the callbacks in
 * order to print information about the document.
 *
 * @version $Id$
 */
public class SAX2Count 
extends DefaultHandler {

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

    private static boolean warmup = false;

    /** Elements. */
    private long elements;

    /** Attributes. */
    private long attributes;

    /** Characters. */
    private long characters;

    /** Ignorable whitespace. */
    private long ignorableWhitespace;

    //
    // Public static methods
    //

    /** Prints the output from the SAX callbacks. */
    public static void print(String parserName, String uri, boolean validate) {

        try {
            SAX2Count counter = new SAX2Count();

            XMLReader parser = (XMLReader)Class.forName(parserName).newInstance();
            parser.setContentHandler(counter);
            parser.setErrorHandler(counter);



            //if (validate)
            //   parser.setFeature("http://xml.org/sax/features/validation", true);

            parser.setFeature( "http://xml.org/sax/features/validation", 
                                               validate);

            parser.setFeature( "http://xml.org/sax/features/namespaces",
                                               setNameSpaces );

            parser.setFeature( "http://apache.org/xml/features/validation/schema",
                                               setSchemaSupport );

            if (warmup) {
                parser.setFeature("http://apache.org/xml/features/continue-after-fatal-error", true);
                parser.parse(uri);
                warmup = false;
            }
            long before = System.currentTimeMillis();
            parser.parse(uri);
            long after = System.currentTimeMillis();
            counter.printResults(uri, after - before);
        } catch (org.xml.sax.SAXParseException spe) {
            spe.printStackTrace(System.err);
        } catch (org.xml.sax.SAXException se) {
            if (se.getException() != null)
                se.getException().printStackTrace(System.err);
            else
                se.printStackTrace(System.err);
        } catch (Exception e) {
            e.printStackTrace(System.err);
        }

    } // print(String,String)

    //
    // DocumentHandler methods
    //

    /** Start document. */
    public void startDocument() {

        if (warmup)
            return;

        elements            = 0;
        attributes          = 0;
        characters          = 0;
        ignorableWhitespace = 0;

    } // startDocument()

    /** Start element. */
    public void startElement(String uri, String local, String raw, Attributes attrs) {

        if (warmup)
            return;

        elements++;
        if (attrs != null) {
            attributes += attrs.getLength();
        }

    } // startElement(String,AttributeList)

    /** Characters. */
    public void characters(char ch[], int start, int length) {

        if (warmup)
            return;

        characters += length;

    } // characters(char[],int,int);

    /** Ignorable whitespace. */
    public void ignorableWhitespace(char ch[], int start, int length) {

        if (warmup)
            return;

        ignorableWhitespace += length;

    } // ignorableWhitespace(char[],int,int);

    //
    // ErrorHandler methods
    //

    /** Warning. */
    public void warning(SAXParseException ex) {
        if (warmup)
            return;

        System.err.println("[Warning] "+
                           getLocationString(ex)+": "+
                           ex.getMessage());
    }

    /** Error. */
    public void error(SAXParseException ex) {
        if (warmup)
            return;

        System.err.println("[Error] "+
                           getLocationString(ex)+": "+
                           ex.getMessage());
    }

    /** Fatal error. */
    public void fatalError(SAXParseException ex) throws SAXException {
        if (warmup)
            return;

        System.err.println("[Fatal Error] "+
                           getLocationString(ex)+": "+
                           ex.getMessage());
//        throw ex;
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
    // Public methods
    //

    /** Prints the results. */
    public void printResults(String uri, long time) {

        // filename.xml: 631 ms (4 elems, 0 attrs, 78 spaces, 0 chars)
        System.out.print(uri);
        System.out.print(": ");
        System.out.print(time);
        System.out.print(" ms (");
        System.out.print(elements);
        System.out.print(" elems, ");
        System.out.print(attributes);
        System.out.print(" attrs, ");
        System.out.print(ignorableWhitespace);
        System.out.print(" spaces, ");
        System.out.print(characters);
        System.out.print(" chars)");
        System.out.println();
    } // printResults(String,long)

    //
    // Main
    //

    /** Main program entry point. */
    public static void main(String argv[]) {

        Arguments argopt = new Arguments();
        argopt.setUsage( new String[] 
                         { "usage: java sax.SAX2Count (options) uri ...","",
                             "options:",
                             "  -p name  Specify SAX parser by name.",
                             "  -n | -N  Turn on/off namespace [default=on]",
                             "  -v | -V  Turn on/off validation [default=off]",
                             "  -s | -S  Turn on/off Schema support [default=on]",
                             "  -d | -D  Turn on/off deferred DOM [default=on]",
                             "  -w       Warmup the parser before timing.",
                             "  -h       This help screen."}  );


        // is there anything to do?
        if (argv.length == 0) {
            argopt.printUsage();
            System.exit(1);
        }

        // vars
        String  parserName = DEFAULT_PARSER_NAME;

        argopt.parseArgumentTokens(argv, new char[] { 'p'} );

        int   c;
        String arg = null; 
        while ( ( arg =  argopt.getlistFiles() ) != null ) {
            outer:
          
            while ( (c =  argopt.getArguments()) != -1 ){
                System.out.println( "c =" + c );
                switch (c) {
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
                case 'w':
                    warmup = true;
                    break;
                case -1:
                    break outer;
                default:
                    break;
                }

            }
            
            // print uri
            print(parserName, arg,  setValidation);
            ///
        }
    } // main(String[])

} // class SAX2Count
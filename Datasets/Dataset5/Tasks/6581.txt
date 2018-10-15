"  -v | -V  Turn on/off validation [default=off]",

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 1999, 2000 The Apache Software Foundation.  All rights 
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

package dom;

import util.Arguments;


import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.io.UnsupportedEncodingException;

import org.w3c.dom.Attr;
import org.w3c.dom.Document;
import org.w3c.dom.NamedNodeMap;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.apache.xerces.readers.MIME2Java;


/**
 * A sample DOM writer. This sample program illustrates how to
 * traverse a DOM tree in order to print a document that is parsed.
 *
 * @version $Id$
 */
public class DOMWriter {

    //
    // Constants
    //


    /** Default parser name. */
    private static final String 
    DEFAULT_PARSER_NAME = "dom.wrappers.DOMParser";


    private static boolean setValidation    = false; //defaults
    private static boolean setNameSpaces    = true;
    private static boolean setSchemaSupport = true;
    private static boolean setDeferredDOM   = true;



    //
    // Data
    //

    /** Default Encoding */
    private static  String
    PRINTWRITER_ENCODING = "UTF8";

    private static String MIME2JAVA_ENCODINGS[] =
    { "Default", "UTF-8", "US-ASCII", "ISO-8859-1", "ISO-8859-2", "ISO-8859-3", "ISO-8859-4", 
        "ISO-8859-5", "ISO-8859-6", "ISO-8859-7", "ISO-8859-8", "ISO-8859-9", "ISO-2022-JP",
        "SHIFT_JIS", "EUC-JP","GB2312", "BIG5", "EUC-KR", "ISO-2022-KR", "KOI8-R", "EBCDIC-CP-US", 
        "EBCDIC-CP-CA", "EBCDIC-CP-NL", "EBCDIC-CP-DK", "EBCDIC-CP-NO", "EBCDIC-CP-FI", "EBCDIC-CP-SE",
        "EBCDIC-CP-IT", "EBCDIC-CP-ES", "EBCDIC-CP-GB", "EBCDIC-CP-FR", "EBCDIC-CP-AR1", 
        "EBCDIC-CP-HE", "EBCDIC-CP-CH", "EBCDIC-CP-ROECE","EBCDIC-CP-YU",  
        "EBCDIC-CP-IS", "EBCDIC-CP-AR2", "UTF-16"
    };


/*
   private static String JAVA_SUPPORTED_ENCODINGS[] = 
   { "Default", "8859_1", "8859_2", "8859_3", "8859_4", "8859_5", "8859_6", 
      "8859_7", "8859_8", "8859_9", "Cp037", "Cp273", "Cp277", "Cp278",
      "Cp280", "Cp284", "Cp285", "Cp297", "Cp420", "Cp424", "Cp437",
      "Cp500", "Cp737", "Cp775", "Cp838", "Cp850", "Cp852", "Cp855", "Cp856",
      "Cp857", "Cp860", "Cp861",
      "Cp862", "Cp863", "Cp864", "Cp865", "Cp866", "Cp868", "Cp869", "Cp870",
      "Cp871", "Cp874", "Cp875",
      "Cp918", "Cp921", "Cp922", "Cp930", "Cp933", "Cp935", "Cp937", "Cp939",
      "Cp942", "Cp948", "Cp949",
      "Cp950", "Cp964", "Cp970", "Cp1006", "Cp1025", "Cp1026", "Cp1046", 
      "Cp1097", "Cp1098", "Cp1112",
      "Cp1122", "Cp1123", "Cp1124", "Cp1250", "Cp1251", "Cp1252", "Cp1253",
      "Cp1254", "Cp1255", "Cp1256",
      "Cp1257", "Cp1258", "Cp1381", "Cp1383", "Cp33722", "MS874",
      "EUCJIS", "GB2312", 
       "GBK", "ISO2022CN_CNS", "ISO2022CN_GB",
      "JIS",
      "JIS0208", "KOI8_R", "KSC5601","MS874",
      "SJIS",  "Big5", "CNS11643",
      "MacArabic", "MacCentralEurope", "MacCroatian", "MacCyrillic",
      "MacDingbat", "MacGreek",
      "MacHebrew", "MacIceland", "MacRoman", "MacRomania", "MacSymbol",
      "MacThai", "MacTurkish",
      "MacUkraine", "SJIS", "Unicode", "UnicodeBig", "UnicodeLittle", "UTF8"};
*/

    /** Print writer. */
    protected PrintWriter out;

    /** Canonical output. */
    protected boolean canonical;


    public DOMWriter(String encoding, boolean canonical)              
    throws UnsupportedEncodingException {
        out = new PrintWriter(new OutputStreamWriter(System.out, encoding));
        this.canonical = canonical;
    } // <init>(String,boolean)

    //
    // Constructors
    //

    /** Default constructor. */
    public DOMWriter(boolean canonical) throws UnsupportedEncodingException {
        this( getWriterEncoding(), canonical);
    }

    public static String getWriterEncoding( ) {
        return(PRINTWRITER_ENCODING);
    }// getWriterEncoding 

    public static void  setWriterEncoding( String encoding ) {
        if ( encoding.equalsIgnoreCase( "DEFAULT" ) )
            PRINTWRITER_ENCODING  = "UTF8";
        else if ( encoding.equalsIgnoreCase( "UTF-16" ) )
            PRINTWRITER_ENCODING  = "Unicode";
        else
            PRINTWRITER_ENCODING = MIME2Java.convert( encoding ); 
    }// setWriterEncoding 


    public static boolean isValidJavaEncoding( String encoding ) {
        for ( int i = 0; i < MIME2JAVA_ENCODINGS.length; i++ )
            if ( encoding.equals( MIME2JAVA_ENCODINGS[i] ) )
                return(true);

        return(false);
    }// isValidJavaEncoding 



    /** Prints the resulting document tree. */
    public static void print(String parserWrapperName, String uri, 
                             boolean canonical ) {
        try {
            DOMParserWrapper parser = 
            (DOMParserWrapper)Class.forName(parserWrapperName).newInstance();

            parser.setFeature( "http://apache.org/xml/features/dom/defer-node-expansion",
                               setDeferredDOM );
            parser.setFeature( "http://xml.org/sax/features/validation", 
                               setValidation );
            parser.setFeature( "http://xml.org/sax/features/namespaces",
                               setNameSpaces );
            parser.setFeature( "http://apache.org/xml/features/validation/schema",
                               setSchemaSupport );

            Document document = parser.parse(uri);
            DOMWriter writer = new DOMWriter(canonical);
            writer.print(document);
        } catch ( Exception e ) {
            //e.printStackTrace(System.err);
        }

    } // print(String,String,boolean)


    /** Prints the specified node, recursively. */
    public void print(Node node) {

        // is there anything to do?
        if ( node == null ) {
            return;
        }

        int type = node.getNodeType();
        switch ( type ) {
        // print document
        case Node.DOCUMENT_NODE: {
                if ( !canonical ) {
                    String  Encoding = this.getWriterEncoding();
                    if ( Encoding.equalsIgnoreCase( "DEFAULT" ) )
                        Encoding = "UTF-8";
                    else if ( Encoding.equalsIgnoreCase( "Unicode" ) )
                        Encoding = "UTF-16";
                    else
                        Encoding = MIME2Java.reverse( Encoding );

                    out.println("<?xml version=\"1.0\" encoding=\""+
                                Encoding + "\"?>");
                }
                print(((Document)node).getDocumentElement());
                out.flush();
                break;
            }

            // print element with attributes
        case Node.ELEMENT_NODE: {
                out.print('<');
                out.print(node.getNodeName());
                Attr attrs[] = sortAttributes(node.getAttributes());
                for ( int i = 0; i < attrs.length; i++ ) {
                    Attr attr = attrs[i];
                    out.print(' ');
                    out.print(attr.getNodeName());
                    out.print("=\"");
                    out.print(normalize(attr.getNodeValue()));
                    out.print('"');
                }
                out.print('>');
                NodeList children = node.getChildNodes();
                if ( children != null ) {
                    int len = children.getLength();
                    for ( int i = 0; i < len; i++ ) {
                        print(children.item(i));
                    }
                }
                break;
            }

            // handle entity reference nodes
        case Node.ENTITY_REFERENCE_NODE: {
                if ( canonical ) {
                    NodeList children = node.getChildNodes();
                    if ( children != null ) {
                        int len = children.getLength();
                        for ( int i = 0; i < len; i++ ) {
                            print(children.item(i));
                        }
                    }
                } else {
                    out.print('&');
                    out.print(node.getNodeName());
                    out.print(';');
                }
                break;
            }

            // print cdata sections
        case Node.CDATA_SECTION_NODE: {
                if ( canonical ) {
                    out.print(normalize(node.getNodeValue()));
                } else {
                    out.print("<![CDATA[");
                    out.print(node.getNodeValue());
                    out.print("]]>");
                }
                break;
            }

            // print text
        case Node.TEXT_NODE: {
                out.print(normalize(node.getNodeValue()));
                break;
            }

            // print processing instruction
        case Node.PROCESSING_INSTRUCTION_NODE: {
                out.print("<?");
                out.print(node.getNodeName());
                String data = node.getNodeValue();
                if ( data != null && data.length() > 0 ) {
                    out.print(' ');
                    out.print(data);
                }
                out.print("?>");
                break;
            }
        }

        if ( type == Node.ELEMENT_NODE ) {
            out.print("</");
            out.print(node.getNodeName());
            out.print('>');
        }

        out.flush();

    } // print(Node)

    /** Returns a sorted list of attributes. */
    protected Attr[] sortAttributes(NamedNodeMap attrs) {

        int len = (attrs != null) ? attrs.getLength() : 0;
        Attr array[] = new Attr[len];
        for ( int i = 0; i < len; i++ ) {
            array[i] = (Attr)attrs.item(i);
        }
        for ( int i = 0; i < len - 1; i++ ) {
            String name  = array[i].getNodeName();
            int    index = i;
            for ( int j = i + 1; j < len; j++ ) {
                String curName = array[j].getNodeName();
                if ( curName.compareTo(name) < 0 ) {
                    name  = curName;
                    index = j;
                }
            }
            if ( index != i ) {
                Attr temp    = array[i];
                array[i]     = array[index];
                array[index] = temp;
            }
        }

        return(array);

    } // sortAttributes(NamedNodeMap):Attr[]


    //
    // Main
    //

    /** Main program entry point. */
    public static void main(String argv[]) {
        Arguments argopt = new Arguments();
        argopt.setUsage( new String[] {
                             "usage: java dom.DOMWriter (options) uri ...","",
                             "options:",
                             "  -n | -N  Turn on/off namespace [default=on]",
                             "  -v | -V  Turn on/off validation [default=on]",
                             "  -s | -S  Turn on/off Schema support [default=on]",
                             "  -d | -D  Turn on/off deferred DOM [default=on]",
                             "  -c       Canonical XML output.",
                             "  -h       This help screen.",
                             "  -e       Output Java Encoding.",
                             "           Default encoding: UTF-8"} );



        // is there anything to do?
        if ( argv.length == 0 ) {
            argopt.printUsage();
            System.exit(1);
        }

        // vars
        String  parserName = DEFAULT_PARSER_NAME;
        boolean canonical  = false;
        String  encoding   = "UTF8"; // default encoding

        argopt.parseArgumentTokens(argv, new char[] { 'p', 'e'} );

        int   c;
        String arg = null; 
        while ( ( arg =  argopt.getlistFiles() ) != null ) {

            outer:
            while ( (c =  argopt.getArguments()) != -1 ){
                switch (c) {
                case 'c':
                    canonical = true;
                    break;
                case 'e':
                    encoding      = argopt.getStringParameter();
                    if ( encoding != null && isValidJavaEncoding( encoding ) )
                        setWriterEncoding( encoding );
                    else {
                        printValidJavaEncoding();
                        System.exit( 1 );
                    }
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
                    parserName    = argopt.getStringParameter();
                    break;
                case 'd':
                    setDeferredDOM = true;
                    break;
                case 'D':
                    setDeferredDOM = false;
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
            // print uri
             // print uri
            System.err.println(arg+':');
            print(parserName, arg, canonical );
            System.err.println();
        }
    } // main(String[])


    /** Normalizes the given string. */
    protected String normalize(String s) {
        StringBuffer str = new StringBuffer();

        int len = (s != null) ? s.length() : 0;
        for ( int i = 0; i < len; i++ ) {
            char ch = s.charAt(i);
            switch ( ch ) {
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
                    if ( canonical ) {
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

        return(str.toString());

    } // normalize(String):String


    private static void printValidJavaEncoding() {
        System.err.println( "    ENCODINGS:" );
        System.err.print( "   " );
        for ( int i = 0;
            i < MIME2JAVA_ENCODINGS.length; i++) {
            System.err.print( MIME2JAVA_ENCODINGS[i] + " " );
            if ( (i % 7 ) == 0 ){
                System.err.println();
                System.err.print( "   " );
            }
        }

    } // printJavaEncoding()            

} 
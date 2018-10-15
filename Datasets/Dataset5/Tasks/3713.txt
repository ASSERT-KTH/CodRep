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

import org.apache.xerces.dom.TextImpl;

import org.w3c.dom.Attr;
import org.w3c.dom.Document;
import org.w3c.dom.NamedNodeMap;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;

/**
 * A sample DOM counter. This sample program illustrates how to
 * traverse a DOM tree in order to information about the document.
 *
 * @version $id$
 */
public class DOMCount {

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

    /** Counts the resulting document tree. */
    public static void count(String parserWrapperName, String uri) {

        try {
            DOMParserWrapper parser =
            (DOMParserWrapper)Class.forName(parserWrapperName).newInstance();
            DOMCount counter = new DOMCount();
            long before = System.currentTimeMillis();
            parser.setFeature( "http://apache.org/xml/features/dom/defer-node-expansion",

                               setDeferredDOM );
            parser.setFeature( "http://xml.org/sax/features/validation", 
                               setValidation );
            parser.setFeature( "http://xml.org/sax/features/namespaces",
                               setNameSpaces );
            parser.setFeature( "http://apache.org/xml/features/validation/schema",
                               setSchemaSupport );

            Document document = parser.parse(uri);
            counter.traverse(document);
            long after = System.currentTimeMillis();
            counter.printResults(uri, after - before);
        } catch (org.xml.sax.SAXParseException spe) {
        } catch (org.xml.sax.SAXNotRecognizedException ex ){
        } catch (org.xml.sax.SAXNotSupportedException ex ){
        } catch (org.xml.sax.SAXException se) {
            if (se.getException() != null)
                se.getException().printStackTrace(System.err);
            else
                se.printStackTrace(System.err);
        } catch (Exception e) {
            e.printStackTrace(System.err);
        }

    } // print(String,String,boolean)

    //
    // Public methods
    //

    /** Traverses the specified node, recursively. */
    public void traverse(Node node) {

        // is there anything to do?
        if (node == null) {
            return;
        }

        int type = node.getNodeType();
        switch (type) {
        // print document
        case Node.DOCUMENT_NODE: {
                elements            = 0;
                attributes          = 0;
                characters          = 0;
                ignorableWhitespace = 0;
                traverse(((Document)node).getDocumentElement());
                break;
            }

            // print element with attributes
        case Node.ELEMENT_NODE: {
                elements++;
                NamedNodeMap attrs = node.getAttributes();
                if (attrs != null) {
                    attributes += attrs.getLength();
                }
                NodeList children = node.getChildNodes();
                if (children != null) {
                    int len = children.getLength();
                    for (int i = 0; i < len; i++) {
                        traverse(children.item(i));
                    }
                }
                break;
            }

            // handle entity reference nodes
        case Node.ENTITY_REFERENCE_NODE: {
                NodeList children = node.getChildNodes();
                if (children != null) {
                    int len = children.getLength();
                    for (int i = 0; i < len; i++) {
                        traverse(children.item(i));
                    }
                }
                break;
            }

            // print text
        case Node.CDATA_SECTION_NODE: {
                characters += node.getNodeValue().length();
                break;
            }
        case Node.TEXT_NODE: {
                if (node instanceof TextImpl) {
                    if (((TextImpl)node).isIgnorableWhitespace())
                        ignorableWhitespace += node.getNodeValue().length();
                    else
                        characters += node.getNodeValue().length();
                } else
                    characters += node.getNodeValue().length();
                break;
            }
        }

    } // traverse(Node)

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
        argopt.setUsage( new String[] {
                             "usage: java dom.DOMCount (options) uri ...",
                             "",
                             "options:",
                             "  -p name  Specify DOM parser wrapper by name.",
                             "  -n | -N  Turn on/off namespace [default=on]",
                             "  -v | -V  Turn on/off validation [default=on]",
                             "  -s | -S  Turn on/off Schema support [default=on]",
                             "  -d | -D  Turn on/off deferred DOM [default=on]",
                             "  -h       This help screen."} );


        // is there anything to do?
        if (argv.length == 0) {
            argopt.printUsage();
            System.exit(1);
        }

        // vars
        String  parserName = DEFAULT_PARSER_NAME;

        argopt.parseArgumentTokens(argv , new char[] { 'p'} );

        int   c;
        String arg = null; 
        while ( ( arg =  argopt.getlistFiles() ) != null ) {
outer:
            while ( (c =  argopt.getArguments()) != -1 ){
                switch (c) {
                case 'v':
                    setValidation = true;
                    //System.out.println( "v" );
                    break;
                case 'V':
                    setValidation = false;
                    //System.out.println( "V" );
                    break;
                case 'N':
                    setNameSpaces = false;
                    break;
                case 'n':
                    setNameSpaces = true;
                    break;
                case 'p':
                    //System.out.println('p');
                    parserName = argopt.getStringParameter();
                    //System.out.println( "parserName = " + parserName );
                    break;
                case 'd':
                    setDeferredDOM = true;
                    break;
                case 'D':
                    setDeferredDOM = false;
                    break;
                case 's':
                    //System.out.println("s" );
                    setSchemaSupport = true;
                    break;
                case 'S':
                    //System.out.println("S" );
                    setSchemaSupport = false;
                    break;
                case '?':
                case 'h':
                case '-':
                    argopt.printUsage();
                    System.exit(1);
                    break;
                case  -1:
                    //System.out.println( "-1" );
                    break outer;
                default:
                    
                    break;
                }
            }

            count(parserName, arg ); //count uri
        }

    } // main(String[])

} // class DOMCount
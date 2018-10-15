System.setProperty(DOMImplementationRegistry.PROPERTY,"org.apache.xerces.dom.DOMXSImplementationSourceImpl");

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 1999-2002 The Apache Software Foundation.  All rights
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
 * originally based on software copyright (c) 2002, International
 * Business Machines, Inc., http://www.apache.org.  For more
 * information on the Apache Software Foundation, please see
 * <http://www.apache.org/>.
 */

package dom;

import org.w3c.dom.DOMConfiguration;
import org.w3c.dom.DOMError;
import org.w3c.dom.DOMErrorHandler;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.bootstrap.DOMImplementationRegistry;
import org.w3c.dom.Document;
import org.w3c.dom.ls.LSParser;
import org.w3c.dom.ls.LSParserFilter;
import org.w3c.dom.ls.DOMImplementationLS;
import org.w3c.dom.ls.LSSerializer;
import org.w3c.dom.traversal.NodeFilter;
import org.w3c.dom.ls.LSOutput;
import org.apache.xerces.dom.DOMOutputImpl;

/**
 * This sample program illustrates how to use DOM L3 
 * DOMBuilder, DOMBuilderFilter DOMWriter and other DOM L3 functionality
 * to preparse, revalidate and safe document.
 */
public class DOM3 implements DOMErrorHandler, LSParserFilter {

    /** Default namespaces support (true). */
    protected static final boolean DEFAULT_NAMESPACES = true;

    /** Default validation support (false). */
    protected static final boolean DEFAULT_VALIDATION = false;

    /** Default Schema validation support (false). */
    protected static final boolean DEFAULT_SCHEMA_VALIDATION = false;

    static LSParser builder;
    public static void main( String[] argv) {

        if (argv.length == 0) {
            printUsage();
            System.exit(1);
        }


        try {

            // get DOM Implementation using DOM Registry
            System.setProperty(DOMImplementationRegistry.PROPERTY,"org.apache.xerces.dom.DOMImplementationSourceImpl");
            DOMImplementationRegistry registry =
                DOMImplementationRegistry.newInstance();

            DOMImplementationLS impl = 
                (DOMImplementationLS)registry.getDOMImplementation("LS");

            // create DOMBuilder
            builder = impl.createLSParser(DOMImplementationLS.MODE_SYNCHRONOUS, null);
            
            DOMConfiguration config = builder.getConfig();

            // create Error Handler
            DOMErrorHandler errorHandler = new DOM3();
            
            // create filter
            LSParserFilter filter = new DOM3();
            
            builder.setFilter(filter);

            // set error handler
            config.setParameter("error-handler", errorHandler);


            // set validation feature
            //config.setParameter("validate", Boolean.FALSE);
            config.setParameter("validate",Boolean.TRUE);
            
            // set schema language
            config.setParameter("schema-type", "http://www.w3.org/2001/XMLSchema");
            //config.setParameter("psvi",Boolean.TRUE);
            //config.setParameter("schema-type","http://www.w3.org/TR/REC-xml");
            
            // set schema location
            config.setParameter("schema-location","personal.xsd");
            
            // parse document
            System.out.println("Parsing "+argv[0]+"...");
            Document doc = builder.parseURI(argv[0]);

            // set error handler on the Document
            config = doc.getDomConfig();
            
            config.setParameter("error-handler", errorHandler);

            // set validation feature
            config.setParameter("validate", Boolean.TRUE);
            config.setParameter("schema-type", "http://www.w3.org/2001/XMLSchema");
            //config.setParameter("schema-type","http://www.w3.org/TR/REC-xml");
            config.setParameter("schema-location","data/personal.xsd");
            
            // remove comments from the document
            config.setParameter("comments", Boolean.FALSE);

            System.out.println("Normalizing document... ");
            doc.normalizeDocument();


            // create DOMWriter
            LSSerializer domWriter = impl.createLSSerializer();
            
            System.out.println("Serializing document... ");
            config = domWriter.getConfig();
            config.setParameter("xml-declaration", Boolean.FALSE);
            //config.setParameter("validate",errorHandler);

            // serialize document to standard output
            //domWriter.writeNode(System.out, doc);
            LSOutput dOut = new DOMOutputImpl();
            dOut.setByteStream(System.out);
            domWriter.write(doc,dOut);

        } catch ( Exception ex ) {
            ex.printStackTrace();
        }
    }


    private static void printUsage() {

        System.err.println("usage: java dom.DOM3 uri ...");
        System.err.println();
        System.err.println("NOTE: You can only validate DOM tree against XML Schemas.");

    } // printUsage()


    public boolean handleError(DOMError error){
        short severity = error.getSeverity();
        if (severity == error.SEVERITY_ERROR) {
            System.out.println("[dom3-error]: "+error.getMessage());
        }

        if (severity == error.SEVERITY_WARNING) {
            System.out.println("[dom3-warning]: "+error.getMessage());
        }
        return true;

    }
	/**
	 * @see org.w3c.dom.ls.LSParserFilter#acceptNode(Node)
	 */
	public short acceptNode(Node enode) {
        return NodeFilter.FILTER_ACCEPT;
	}

	/**
	 * @see org.w3c.dom.ls.LSParserFilter#getWhatToShow()
	 */
	public int getWhatToShow() {
		return NodeFilter.SHOW_ELEMENT;
	}

	/**
	 * @see org.w3c.dom.ls.LSParserFilter#startElement(Element)
	 */
	public short startElement(Element elt) {
		return LSParserFilter.FILTER_ACCEPT;
	}

}



// System.setProperty(DOMImplementationRegistry.PROPERTY,"org.apache.xerces.dom.DOMXSImplementationSourceImpl");

/*
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 * 
 *      http://www.apache.org/licenses/LICENSE-2.0
 * 
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package dom;

import org.w3c.dom.DOMConfiguration;
import org.w3c.dom.DOMError;
import org.w3c.dom.DOMErrorHandler;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.bootstrap.DOMImplementationRegistry;
import org.w3c.dom.ls.DOMImplementationLS;
import org.w3c.dom.ls.LSOutput;
import org.w3c.dom.ls.LSParser;
import org.w3c.dom.ls.LSParserFilter;
import org.w3c.dom.ls.LSSerializer;
import org.w3c.dom.traversal.NodeFilter;

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
            System.setProperty(DOMImplementationRegistry.PROPERTY,"org.apache.xerces.dom.DOMXSImplementationSourceImpl");
            DOMImplementationRegistry registry =
                DOMImplementationRegistry.newInstance();

            DOMImplementationLS impl = 
                (DOMImplementationLS)registry.getDOMImplementation("LS");

            // create DOMBuilder
            builder = impl.createLSParser(DOMImplementationLS.MODE_SYNCHRONOUS, null);
            
            DOMConfiguration config = builder.getDomConfig();

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
            config = domWriter.getDomConfig();
            config.setParameter("xml-declaration", Boolean.FALSE);
            //config.setParameter("validate",errorHandler);

            // serialize document to standard output
            //domWriter.writeNode(System.out, doc);
            LSOutput dOut = impl.createLSOutput();
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
        if (severity == DOMError.SEVERITY_ERROR) {
            System.out.println("[dom3-error]: "+error.getMessage());
        }

        if (severity == DOMError.SEVERITY_WARNING) {
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



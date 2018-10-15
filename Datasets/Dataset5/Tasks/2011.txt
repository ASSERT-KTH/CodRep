"org.apache.xerces.dom.DOMXSImplementationSourceImpl");

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 2003 The Apache Software Foundation.  All rights
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
 * originally based on software copyright (c) 2003, International
 * Business Machines, Inc., http://www.apache.org.  For more
 * information on the Apache Software Foundation, please see
 * <http://www.apache.org/>.
 */

package xs;

import org.apache.xerces.dom3.DOMConfiguration;
import org.apache.xerces.dom3.DOMError;
import org.apache.xerces.dom3.DOMErrorHandler;
import org.apache.xerces.dom3.bootstrap.DOMImplementationRegistry;
import org.apache.xerces.xs.XSConstants;
import org.apache.xerces.xs.XSImplementation;
import org.apache.xerces.xs.XSLoader;
import org.apache.xerces.xs.XSModel;
import org.apache.xerces.xs.XSNamedMap;
import org.apache.xerces.xs.XSObject;
import org.w3c.dom.ls.LSParser;

/**
 * This sample program illustrates how to use load XML Schemas and 
 * use XML Schema API (org.apache.xerces.xs) to navigate XML Schema components.
 *
 * @author Elena Litani, IBM
 * @version $Id$
 */
public class QueryXS implements DOMErrorHandler {

    /** Default namespaces support (true). */
    protected static final boolean DEFAULT_NAMESPACES = true;

    /** Default validation support (false). */
    protected static final boolean DEFAULT_VALIDATION = false;

    /** Default Schema validation support (false). */
    protected static final boolean DEFAULT_SCHEMA_VALIDATION = false;

    static LSParser builder;
    public static void main(String[] argv) {

        if (argv.length == 0) {
            printUsage();
            System.exit(1);
        }

        try {
            // get DOM Implementation using DOM Registry
            System.setProperty(
                DOMImplementationRegistry.PROPERTY,
                "org.apache.xerces.dom.DOMImplementationSourceImpl");
            DOMImplementationRegistry registry = DOMImplementationRegistry.newInstance();

            XSImplementation impl = (XSImplementation) registry.getDOMImplementation("XS-Loader");

            XSLoader schemaLoader = impl.createXSLoader(null);

            DOMConfiguration config = schemaLoader.getConfig();

            // create Error Handler
            DOMErrorHandler errorHandler = new QueryXS();

            // set error handler
            config.setParameter("error-handler", errorHandler);

            // set validation feature
            config.setParameter("validate", Boolean.TRUE);

            // parse document
            System.out.println("Parsing " + argv[0] + "...");
            XSModel model = schemaLoader.loadURI(argv[0]);
            if (model != null) {
            	// element declarations
                XSNamedMap map = model.getComponents(XSConstants.ELEMENT_DECLARATION);
                if (map.getLength() != 0) {
					System.out.println("*************************************************");
					System.out.println("* Global element declarations: {namespace} name ");
					System.out.println("*************************************************");
                    for (int i = 0; i < map.getLength(); i++) {
                        XSObject item = map.item(i);
                        System.out.println("{" + item.getNamespace() + "}" + item.getName());
                    }
                }
                // attribute declarations
                map = model.getComponents(XSConstants.ATTRIBUTE_DECLARATION);
                if (map.getLength() != 0) {
					System.out.println("*************************************************");
                    System.out.println("* Global attribute declarations: {namespace} name");
					System.out.println("*************************************************");
                    for (int i = 0; i < map.getLength(); i++) {
                        XSObject item = map.item(i);
                        System.out.println("{" + item.getNamespace() + "}" + item.getName());
                    }
                }
				// notation declarations
				map = model.getComponents(XSConstants.TYPE_DEFINITION);
				if (map.getLength() != 0) {
					System.out.println("*************************************************");
					System.out.println("* Global type declarations: {namespace} name");
					System.out.println("*************************************************");
					for (int i = 0; i < map.getLength(); i++) {
						XSObject item = map.item(i);
						System.out.println("{" + item.getNamespace() + "}" + item.getName());
					}
				}
                
				// notation declarations
				map = model.getComponents(XSConstants.NOTATION_DECLARATION);
				if (map.getLength() != 0) {
					System.out.println("*************************************************");
					System.out.println("* Global notation declarations: {namespace} name");
					System.out.println("*************************************************");
					for (int i = 0; i < map.getLength(); i++) {
						XSObject item = map.item(i);
						System.out.println("{" + item.getNamespace() + "}" + item.getName());
					}
				}

            }

        } catch (Exception ex) {
            ex.printStackTrace();
        }
    }

    private static void printUsage() {
        
        System.err.println("usage: java dom.QueryXS uri ...");
        System.err.println();

    } // printUsage()


    public boolean handleError(DOMError error){
        short severity = error.getSeverity();
        if (severity == DOMError.SEVERITY_ERROR) {
            System.out.println("[xs-error]: "+error.getMessage());
        }

        if (severity == DOMError.SEVERITY_WARNING) {
            System.out.println("[xs-warning]: "+error.getMessage());
        }
        return true;

    }

}



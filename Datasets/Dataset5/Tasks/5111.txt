import org.apache.xerces.xs.ElementPSVI;

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
 * originally based on software copyright (c) 1999, International
 * Business Machines, Inc., http://www.apache.org.  For more
 * information on the Apache Software Foundation, please see
 * <http://www.apache.org/>.
 */


package dom.dom3;
import java.io.Reader;
import java.io.StringReader;

import org.apache.xerces.dom.CoreDocumentImpl;
import org.apache.xerces.dom.DocumentImpl;
import org.apache.xerces.dom.NodeImpl;
import org.apache.xerces.dom.TextImpl;
import org.apache.xerces.dom3.DOMConfiguration;
import org.apache.xerces.dom3.DOMError;
import org.apache.xerces.dom3.DOMErrorHandler;
import org.apache.xerces.dom3.bootstrap.DOMImplementationRegistry;
import org.apache.xerces.dom3.DOMLocator;
import org.apache.xerces.xni.psvi.ElementPSVI;
import org.w3c.dom.Attr;
import org.w3c.dom.DOMException;
import org.w3c.dom.Document;
import org.w3c.dom.DocumentType;
import org.w3c.dom.Element;
import org.w3c.dom.NamedNodeMap;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.w3c.dom.Text;
import org.w3c.dom.ls.DOMParser;
import org.w3c.dom.ls.DOMResourceResolver;
import org.w3c.dom.ls.DOMImplementationLS;
import org.w3c.dom.ls.DOMInput;
import org.w3c.dom.ls.DOMSerializer;

import dom.util.Assertion;

/**
 * The program tests vacarious DOM Level 3 functionality
 */
public class Test implements DOMErrorHandler, DOMResourceResolver{
    
    static int errorCounter = 0;
    static DOMErrorHandler errorHandler = new Test();
    static DOMResourceResolver resolver = new Test();
    
    public static void main( String[] argv) {
        try {
            boolean namespaces = true;
            System.out.println("Running dom.dom3.Test...");
            System.setProperty(DOMImplementationRegistry.PROPERTY,"org.apache.xerces.dom.DOMImplementationSourceImpl");

            
            DOMImplementationLS impl = (DOMImplementationLS)DOMImplementationRegistry.newInstance().getDOMImplementation("LS");

            Assertion.verify(impl!=null, "domImplementation != null");

            DOMParser builder = impl.createDOMParser(DOMImplementationLS.MODE_SYNCHRONOUS,
                                                       null);

            DOMSerializer writer = impl.createDOMSerializer();
            DOMConfiguration config = writer.getConfig();
            config.setParameter("namespaces",(namespaces)?Boolean.TRUE:Boolean.FALSE);
            config.setParameter("validate",Boolean.FALSE);
            
            //----------------------------
            // TEST: lookupPrefix
            //       isDefaultNamespace
            //       lookupNamespaceURI
            //----------------------------
            //System.out.println("TEST #1: lookupPrefix, isDefaultNamespace, lookupNamespaceURI, input: tests/dom/dom3/input.xml");
            {

                Document doc = builder.parseURI("tests/dom/dom3/input.xml");
                NodeList ls = doc.getElementsByTagName("a:elem_a"); 

                NodeImpl elem = (NodeImpl)ls.item(0);
                if (namespaces) {
                    //System.out.println("[a:elem_a].lookupPrefix('http://www.example.com', true) == null");
                    Assertion.verify(elem.lookupPrefix("http://www.example.com").equals("ns1"), 
                                     "[a:elem_a].lookupPrefix(http://www.example.com)==null");


                    //System.out.println("[a:elem_a].isDefaultNamespace('http://www.example.com') == true");
                    Assertion.verify(elem.isDefaultNamespace("http://www.example.com") == true, 
                                     "[a:elem_a].isDefaultNamespace(http://www.example.com)==true");


                    //System.out.println("[a:elem_a].lookupPrefix('http://www.example.com', false) == ns1");
                    Assertion.verify(elem.lookupPrefix("http://www.example.com").equals("ns1"), 
                                     "[a:elem_a].lookupPrefix(http://www.example.com)==ns1");


                    Assertion.verify(elem.lookupNamespaceURI("xsi").equals("http://www.w3.org/2001/XMLSchema-instance"), 
                                     "[a:elem_a].lookupNamespaceURI('xsi') == 'http://www.w3.org/2001/XMLSchema-instance'" );

                } else {
                    Assertion.verify( elem.lookupPrefix("http://www.example.com") == null,"lookupPrefix(http://www.example.com)==null"); 
                }

                ls = doc.getElementsByTagName("bar:leaf");
                elem = (NodeImpl)ls.item(0);
                Assertion.verify(elem.lookupPrefix("url1:").equals("foo"), 
                                 "[bar:leaf].lookupPrefix('url1:', false) == foo");
                //System.out.println("[bar:leaf].lookupPrefix('url1:', false) == "+ );

                //System.out.println("==>Create b:baz with namespace 'b:' and xmlns:x='b:'");
                ls = doc.getElementsByTagName("baz");
                elem = (NodeImpl)ls.item(0);
                ls = doc.getElementsByTagName("elem8");
                elem = (NodeImpl)ls.item(0);
                Element e1 = doc.createElementNS("b:","p:baz");
                e1.setAttributeNS("http://www.w3.org/2000/xmlns/", "xmlns:x", "b:");
                elem.appendChild(e1);


                Assertion.verify(((NodeImpl)e1).lookupPrefix("b:").equals("p"), 
                                 "[p:baz].lookupPrefix('b:', false) == p");



                //System.out.println("[p:baz].lookupPrefix('b:', false) == "+ ((NodeImpl)e1).lookupPrefix("b:",false));

                Assertion.verify(elem.lookupNamespaceURI("xsi").equals("http://www.w3.org/2001/XMLSchema-instance"), 
                                 "[bar:leaf].lookupNamespaceURI('xsi') == 'http://www.w3.org/2001/XMLSchema-instance'" );

            
            }

            //************************
            //* Test normalizeDocument()
            //************************
            //System.out.println("TEST #2: normalizeDocumention() - 3 errors, input: tests/dom/dom3/schema.xml");
            {
                errorCounter = 0;
                config = builder.getConfig();
                config.setParameter("error-handler",errorHandler);
                config.setParameter("validate", Boolean.TRUE);
                DocumentImpl core = (DocumentImpl)builder.parseURI("tests/dom/dom3/schema.xml");
                Assertion.verify(errorCounter == 0, "No errors should be reported");
                
                errorCounter = 0;    
                NodeList ls2 = core.getElementsByTagName("decVal");
                Element testElem = (Element)ls2.item(0);
                testElem.removeAttributeNS("http://www.w3.org/2000/xmlns/", "xmlns");

                ls2 = core.getElementsByTagName("v02:decVal");
                testElem = (Element)ls2.item(0);
                testElem.setPrefix("myPrefix");
                Element root = core.getDocumentElement();

                Element newElem = core.createElementNS(null, "decVal");
                String data="4.5";
                if (true) {
                        data = "string";
                } 
                newElem.appendChild(core.createTextNode(data));
                root.insertBefore(newElem, testElem);

                newElem = core.createElementNS(null,  "notInSchema");
                newElem.appendChild(core.createTextNode("added new element"));
                root.insertBefore(newElem, testElem);

                root.appendChild(core.createElementNS("UndefinedNamespace", "NS1:foo"));
                config = core.getConfig();
                config.setParameter("error-handler",errorHandler);
                config.setParameter("validate", Boolean.TRUE);
                core.normalizeDocument();
                Assertion.verify(errorCounter == 3, "3 errors should be reported");

                errorCounter = 0;
                config.setParameter("validate", Boolean.FALSE);
                config.setParameter("comments", Boolean.FALSE);
                core.normalizeDocument();
                Assertion.verify(errorCounter == 0, "No errors should be reported");


                config = builder.getConfig();
                config.setParameter("validate", Boolean.FALSE);
                
            }


            //************************
            //* Test normalizeDocument()
            //************************
            // System.out.println("TEST #3: normalizeDocumention() + psvi, input: data/personal-schema.xml");
            {
                errorCounter = 0;
                config = builder.getConfig();
                config.setParameter("error-handler",errorHandler);
                config.setParameter("validate", Boolean.TRUE);
                config.setParameter("psvi", Boolean.TRUE);
                DocumentImpl core = (DocumentImpl)builder.parseURI("data/personal-schema.xml");
                Assertion.verify(errorCounter == 0, "No errors should be reported");

                NodeList ls2 = core.getElementsByTagName("person");

                Element testElem = (Element)ls2.item(0);
                Assertion.verify(((ElementPSVI)testElem).getElementDeclaration().getName().equals("person"), "testElem decl");
                Element e1 = core.createElementNS(null, "person");
                
                core.getDocumentElement().appendChild(e1);
                e1.setAttributeNS(null, "id", "newEmp");
                Element e2 = core.createElementNS(null, "name");
                e2.appendChild(core.createElementNS(null, "family"));
                e2.appendChild(core.createElementNS(null, "given"));
                e1.appendChild(e2);
                e1.appendChild(core.createElementNS(null, "email"));
                Element e3 = core.createElementNS(null, "link");
                e3.setAttributeNS(null, "manager", "Big.Boss");
                e1.appendChild(e3);

                testElem.removeAttributeNode(testElem.getAttributeNodeNS(null, "contr"));
                NamedNodeMap map = testElem.getAttributes();
                config = core.getConfig();
                errorCounter = 0;
                config.setParameter("psvi", Boolean.TRUE);
                config.setParameter("error-handler",errorHandler);
                config.setParameter("validate", Boolean.TRUE);
                core.normalizeDocument();
                Assertion.verify(errorCounter == 0, "No errors should be reported");
                Assertion.verify(((ElementPSVI)e1).getElementDeclaration().getName().equals("person"), "e1 decl");              
                
                config = builder.getConfig();
                config.setParameter("validate", Boolean.FALSE);
                

            }

            //************************
            //* Test normalizeDocument(): core tests
            //************************
            // System.out.println("TEST #4: normalizeDocument() core");
            {

                // check that namespace normalization algorithm works correctly
                Document doc= new DocumentImpl(); 
                Element root = doc.createElementNS("http://www.w3.org/1999/XSL/Transform", "xsl:stylesheet");
                doc.appendChild(root);
                root.setAttributeNS("http://attr1", "xsl:attr1","");

                Element child1 = doc.createElementNS("http://child1", "NS2:child1");
                child1.setAttributeNS("http://attr2", "NS2:attr2","");
                root.appendChild(child1);

                Element child2 = doc.createElementNS("http://child2","NS4:child2");
                child2.setAttributeNS("http://attr3","attr3", "");
                root.appendChild(child2);

                Element child3 = doc.createElementNS("http://www.w3.org/1999/XSL/Transform","xsl:child3");
                child3.setAttributeNS("http://a1","attr1", "");
                child3.setAttributeNS("http://a2","xsl:attr2", "");
                child3.setAttributeNS("http://www.w3.org/2000/xmlns/", "xmlns:a1", "http://a1");
                child3.setAttributeNS("http://www.w3.org/2000/xmlns/", "xmlns:xsl", "http://a2");
                
                Element child4 = doc.createElementNS(null, "child4");
                child4.setAttributeNS("http://a1", "xsl:attr1", "");
                child4.setAttributeNS("http://www.w3.org/2000/xmlns/", "xmlns", "default");
                child3.appendChild(child4);
                root.appendChild(child3);

                ((CoreDocumentImpl)doc).normalizeDocument();
                
                //
                // assertions
                //

                // xsl:stylesheet should include 2 namespace declarations
                String name = root.getNodeName();
                Assertion.verify(name.equals("xsl:stylesheet"), "xsl:stylesheet");

                String value = root.getAttributeNS("http://www.w3.org/2000/xmlns/", "xsl");
                Assertion.verify(value!=null, "xmlns:xsl != null");
                Assertion.verify(value.equals("http://www.w3.org/1999/XSL/Transform"), "xmlns:xsl="+value);
                
                value = root.getAttributeNS("http://www.w3.org/2000/xmlns/", "NS1");

                Assertion.verify(value!=null && 
                                 value.equals("http://attr1"), "xmlns:NS1="+value);

                // child includes 2 namespace decls

                Assertion.verify(child1.getNodeName().equals("NS2:child1"), "NS2:child1");
                value = child1.getAttributeNS("http://www.w3.org/2000/xmlns/", "NS2");
                Assertion.verify(value!=null && 
                                 value.equals("http://child1"), "xmlns:NS2="+value);

                value = child1.getAttributeNS("http://www.w3.org/2000/xmlns/", "NS1");
                Assertion.verify(value!=null && 
                                 value.equals("http://attr2"), "xmlns:NS1="+value);


                // child3
                

                Assertion.verify(child3.getNodeName().equals("xsl:child3"), "xsl:child3");
                value = child3.getAttributeNS("http://www.w3.org/2000/xmlns/", "NS1");
                Assertion.verify(value!=null && 
                                 value.equals("http://a2"), "xmlns:NS1="+value);


                value = child3.getAttributeNS("http://www.w3.org/2000/xmlns/", "a1");
                Assertion.verify(value!=null && 
                                 value.equals("http://a1"), "xmlns:a1="+value);


                value = child3.getAttributeNS("http://www.w3.org/2000/xmlns/", "xsl");
                Assertion.verify(value!=null && 
                                 value.equals("http://www.w3.org/1999/XSL/Transform"), "xmlns:xsl="+value);

                
                Attr attr = child3.getAttributeNodeNS("http://a2", "attr2");
                Assertion.verify(attr != null, "NS1:attr2 !=null");

                Assertion.verify(child3.getAttributes().getLength() == 5, "xsl:child3 has 5 attrs");
                
                // child 4
                Attr temp = child4.getAttributeNodeNS("http://www.w3.org/2000/xmlns/", "xmlns");
                Assertion.verify(temp.getNodeName().equals("xmlns"), "attribute name is xmlns");
                Assertion.verify(temp.getNodeValue().length() == 0, "xmlns=''");                
                /*
                OutputFormat format = new OutputFormat((Document)doc);
                format.setLineSeparator(LineSeparator.Windows);
                format.setIndenting(true);
                format.setLineWidth(0);             
                format.setPreserveSpace(true);
                XMLSerializer serializer = new XMLSerializer(System.out, format);
                serializer.serialize(doc); 
                */               

            }


            //************************
            //* Test normalizeDocument(): core tests
            //************************
            //System.out.println("TEST #4: namespace fixup during serialization");
            {

                Document doc= new DocumentImpl(); 
                Element root = doc.createElementNS("http://www.w3.org/1999/XSL/Transform", "xsl:stylesheet");
                doc.appendChild(root);
                root.setAttributeNS("http://attr1", "xsl:attr1","");

                Element child1 = doc.createElementNS("http://child1", "NS2:child1");
                child1.setAttributeNS("http://attr2", "NS2:attr2","");
                root.appendChild(child1);

                Element child2 = doc.createElementNS("http://child2","NS4:child2");
                child2.setAttributeNS("http://attr3","attr3", "");
                root.appendChild(child2);

                Element child3 = doc.createElementNS("http://www.w3.org/1999/XSL/Transform","xsl:child3");
                child3.setAttributeNS("http://a1","attr1", "");
                child3.setAttributeNS("http://a2","xsl:attr2", "");
                child3.setAttributeNS("http://www.w3.org/2000/xmlns/", "xmlns:a1", "http://a1");
                child3.setAttributeNS("http://www.w3.org/2000/xmlns/", "xmlns:xsl", "http://a2");
                
                Element child4 = doc.createElementNS(null, "child4");
                child4.setAttributeNS("http://a1", "xsl:attr1", "");
                child4.setAttributeNS("http://www.w3.org/2000/xmlns/", "xmlns", "default");

                child3.appendChild(child4);
                root.appendChild(child3);


                // serialize data
                writer.getConfig().setParameter("namespaces", Boolean.TRUE);
                String xmlData = writer.writeToString(doc);
                Reader r = new StringReader(xmlData);
                DOMInput in = impl.createDOMInput();
                in.setCharacterStream(r);
                doc = builder.parse(in);

                //
                // make sure algorithm works correctly
                //

                root = doc.getDocumentElement();
                child1 = (Element)root.getFirstChild();
                child2 = (Element)child1.getNextSibling();
                child3 = (Element)child2.getNextSibling();


                // xsl:stylesheet should include 2 namespace declarations
                String name = root.getNodeName();
                Assertion.verify(name.equals("xsl:stylesheet"), "xsl:stylesheet");

                String value = root.getAttributeNS("http://www.w3.org/2000/xmlns/", "xsl");
                Assertion.verify(value!=null, "xmlns:xsl != null");
                Assertion.verify(value.equals("http://www.w3.org/1999/XSL/Transform"), "xmlns:xsl="+value);
                
                value = root.getAttributeNS("http://www.w3.org/2000/xmlns/", "NS1");

                Assertion.verify(value!=null && 
                                 value.equals("http://attr1"), "xmlns:NS1="+value);

                // child includes 2 namespace decls

                Assertion.verify(child1.getNodeName().equals("NS2:child1"), "NS2:child1");
                value = child1.getAttributeNS("http://www.w3.org/2000/xmlns/", "NS2");
                Assertion.verify(value!=null && 
                                 value.equals("http://child1"), "xmlns:NS2="+value);

                value = child1.getAttributeNS("http://www.w3.org/2000/xmlns/", "NS1");
                Assertion.verify(value!=null && 
                                 value.equals("http://attr2"), "xmlns:NS1="+value);


                // child3
                

                Assertion.verify(child3.getNodeName().equals("xsl:child3"), "xsl:child3");
                value = child3.getAttributeNS("http://www.w3.org/2000/xmlns/", "NS1");
                Assertion.verify(value!=null && 
                                 value.equals("http://a2"), "xmlns:NS1="+value);


                value = child3.getAttributeNS("http://www.w3.org/2000/xmlns/", "a1");
                Assertion.verify(value!=null && 
                                 value.equals("http://a1"), "xmlns:a1="+value);


                value = child3.getAttributeNS("http://www.w3.org/2000/xmlns/", "xsl");
                Assertion.verify(value!=null && 
                                 value.equals("http://www.w3.org/1999/XSL/Transform"), "xmlns:xsl="+value);

                
                Attr attr = child3.getAttributeNodeNS("http://a2", "attr2");
                Assertion.verify(attr != null, "NS6:attr2 !=null");

                Assertion.verify(child3.getAttributes().getLength() == 5, "xsl:child3 has 5 attrs");


                
                //OutputFormat format = new OutputFormat((Document)doc);
                //format.setLineSeparator(LineSeparator.Windows);
                //format.setIndenting(true);
                //format.setLineWidth(0);             
                //format.setPreserveSpace(true);

                //XMLSerializer serializer = new XMLSerializer(System.out, format);
                //serializer.serialize(doc);                

            }


            //************************
            // TEST: replaceWholeText()
            //       getWholeText()
            //       
            //************************
           
            //System.out.println("TEST #5: wholeText, input: tests/dom/dom3/wholeText.xml");
           {
            config = builder.getConfig();
            config.setParameter("error-handler",errorHandler);
            config.setParameter("validate", Boolean.FALSE);
            config.setParameter("entities", Boolean.TRUE);
            DocumentImpl doc = (DocumentImpl)builder.parseURI("tests/dom/dom3/wholeText.xml");

            Element root = doc.getDocumentElement();
            Element test = (Element)doc.getElementsByTagName("elem").item(0);
            
            test.appendChild(doc.createTextNode("Address: "));
            test.appendChild(doc.createEntityReference("ent2"));
            test.appendChild(doc.createTextNode("City: "));
            
            test.appendChild(doc.createEntityReference("ent1"));
            DocumentType doctype = doc.getDoctype();
            Node entity = doctype.getEntities().getNamedItem("ent3");

            NodeList ls = test.getChildNodes();
            Assertion.verify(ls.getLength()==5, "List length");
            
            String compare1 = "Home Address: 1900 Dallas Road (East) City: Dallas. California. USA  PO #5668";
            Assertion.verify(((TextImpl)ls.item(0)).getWholeText().equals(compare1), "Compare1");
            String compare2 = "Address: 1900 Dallas Road (East) City: Dallas. California. USA  PO #5668";
            Assertion.verify(((TextImpl)ls.item(1)).getWholeText().equals(compare2), "Compare2");
            

            //TEST replaceWholeText()
            ((NodeImpl)ls.item(0)).setReadOnly(true, true);
            
            TextImpl original = (TextImpl)ls.item(0);
            Node newNode = original.replaceWholeText("Replace with this text");
            ls = test.getChildNodes();
            Assertion.verify(ls.getLength() == 1, "Length == 1");
            Assertion.verify(ls.item(0).getNodeValue().equals("Replace with this text"), "Replacement works");
            Assertion.verify(newNode != original, "New node created");

            // replace text for node which is not yet attached to the tree
            Text text = doc.createTextNode("readonly");
            ((NodeImpl)text).setReadOnly(true, true);
            text = ((TextImpl)text).replaceWholeText("Data");
            Assertion.verify(text.getNodeValue().equals("Data"), "New value 'Data'");

            // test with second child that does not have any content
            test = (Element)doc.getElementsByTagName("elem").item(1);
            try {            
                ((TextImpl)test.getFirstChild()).replaceWholeText("can't replace");
            } catch (DOMException e){
               Assertion.verify(e !=null);
            }
            String compare3 = "Test: The Content ends here. ";
            //Assertion.assert(((Text)test.getFirstChild()).getWholeText().equals(compare3), "Compare3");
            
           }

            //************************
            // TEST: schema-type
            //       schema-location
            //       
            //************************
            {
                errorCounter = 0;
                config = builder.getConfig();
                config.setParameter("error-handler",errorHandler);
                config.setParameter("entity-resolver",resolver);
                config.setParameter("validate", Boolean.TRUE);
                config.setParameter("psvi", Boolean.TRUE);
                
                // schema-type is not set validate against both grammars 
                errorCounter = 0;
                DocumentImpl core2 = (DocumentImpl)builder.parseURI("tests/dom/dom3/both-error.xml");
                Assertion.verify(errorCounter == 4, "4 errors should be reported");
                
                errorCounter = 0;
                // set schema-type to be XML Schema 
                config.setParameter("schema-type", "http://www.w3.org/2001/XMLSchema");
                // test parsing a file that has both XML schema and DTD
                core2 = (DocumentImpl)builder.parseURI("tests/dom/dom3/both.xml");
                Assertion.verify(errorCounter == 0, "No errors should be reported");
                
            
                // parse a file with XML schema and DTD but validate against DTD only
                errorCounter = 0;
                config.setParameter("schema-type","http://www.w3.org/TR/REC-xml");
                core2 = (DocumentImpl)builder.parseURI("tests/dom/dom3/both-error.xml");
                Assertion.verify(errorCounter == 3, "3 errors should be reported");
                
                // parse a file with DTD only but set schema-location and 
                // validate against XML Schema
                // set schema location
                
                
                core2 = (DocumentImpl)builder.parseURI("tests/dom/dom3/both-error.xml");
                
                // normalize document
                errorCounter = 0;
                Element root = core2.getDocumentElement();
                root.removeAttributeNS("http://www.w3.org/2001/XMLSchema", "xsi");               
                root.removeAttributeNS("http://www.w3.org/2001/XMLSchema", "noNamespaceSchemaLocation");
                config = core2.getConfig();
                config.setParameter("error-handler",errorHandler);
                config.setParameter("schema-type", "http://www.w3.org/2001/XMLSchema");
                config.setParameter("schema-location","personal.xsd");
                config.setParameter("entity-resolver",resolver);
                config.setParameter("validate", Boolean.TRUE);
                core2.normalizeDocument();
                Assertion.verify(errorCounter == 1, "1 error should be reported: "+errorCounter);
 
    
            }


        } catch ( Exception ex ) {
            ex.printStackTrace();
        }
        System.out.println("done!");
    }

    StringBuffer fError = new StringBuffer();
    public boolean handleError(DOMError error){
        fError.setLength(0);
        short severity = error.getSeverity();
        if (severity == error.SEVERITY_ERROR) {
            errorCounter++;
            fError.append("[Error]");
        }

        if (severity == error.SEVERITY_FATAL_ERROR) {
            fError.append("[FatalError]");
        }
        if (severity == error.SEVERITY_WARNING) {
            fError.append("[Warning]");
        }

        DOMLocator locator = error.getLocation();
        if (locator != null) {
            // line:colon:offset
            fError.append(locator.getLineNumber());
            fError.append(":");
            fError.append(locator.getColumnNumber());
            fError.append(":");
            fError.append(locator.getOffset());
            Node node = locator.getRelatedNode();
            if (node != null) {

                fError.append("[");
                fError.append(locator.getRelatedNode().getNodeName());
                fError.append("]");
            }
            String systemId = locator.getUri();
            if (systemId != null) {
                int index = systemId.lastIndexOf('/');
                if (index != -1)
                    systemId = systemId.substring(index + 1);
                fError.append(":");
                fError.append(systemId);
            }

            fError.append(": ");
            fError.append(error.getMessage());

        }
         //System.out.println(fError.toString());
        return true;

    }
    
	/**
	 * @see org.w3c.dom.ls.DOMEntityResolver#resolveEntity(String, String, String)
	 */
	public DOMInput resolveResource(String publicId, String systemId, String baseURI) {
		try {
			DOMImplementationLS impl =
				(DOMImplementationLS) DOMImplementationRegistry.newInstance().getDOMImplementation(
					"LS");
			DOMInput source = impl.createDOMInput();
			if (systemId.equals("personal.xsd")) {
				source.setSystemId("data/personal.xsd");
			}
			else {
				source.setSystemId("data/personal.dtd");
			}

			return source;
		}
		catch (Exception e) {
			return null;
		}
	}
    
   
}



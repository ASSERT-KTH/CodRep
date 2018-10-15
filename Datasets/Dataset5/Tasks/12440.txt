if (attributeNode.getValue().length() != 0)

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

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;

import org.w3c.dom.Attr;
import org.w3c.dom.CDATASection;
import org.w3c.dom.CharacterData;
import org.w3c.dom.Comment;
import org.w3c.dom.DOMException;
import org.w3c.dom.DOMImplementation;
import org.w3c.dom.Document;
import org.w3c.dom.DocumentFragment;
import org.w3c.dom.DocumentType;
import org.w3c.dom.Element;
import org.w3c.dom.Entity;
import org.w3c.dom.EntityReference;
import org.w3c.dom.NamedNodeMap;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.w3c.dom.Notation;
import org.w3c.dom.ProcessingInstruction;
import org.w3c.dom.Text;

import dom.util.Assertion;

/**
 * This class tests methods for XML DOM implementation
 * version 2.0 10/12/98
 * 
 * DOMException errors are tested by calls to DOMExceptionsTest from: Main, docBuilder...
 *
 * @author Philip W. Davis
 */
 
public class DTest {
	
	public static Element 		testElementNode;
	public static Attr 		testAttributeNode;
	public static Text 		testTextNode;
	public static CDATASection 	testCDATASectionNode;
	public static EntityReference 	testEntityReferenceNode;
	public static Entity 		testEntityNode;
	public static ProcessingInstruction testProcessingInstructionNode;
	public static Comment 		testCommentNode;
	public static Document 		testDocumentNode;
	public static DocumentType 	testDocumentTypeNode;
	public static DocumentFragment 	testDocumentFragmentNode;
	public static Notation 		testNotationNode;

/**
 * 
 * version 2.0 10/12/98
 *
 * @author Philip W. Davis
 */
public DTest() {
	super();
	
}
/**
 * version 3.0 01/25/99
 *  
 * @return org.w3c.dom.Document
 *
 * @author Philip W. Davis
 */
public Document createDocument() {
	return new org.apache.xerces.dom.DocumentImpl();	//Replace with a Document creator
}
/**
 * version 3.0 01/25/99
 * 
 * @return org.w3c.dom.DocumentType
 * @param name java.lang.String
 *
 * @author Philip W. Davis
 */
public DocumentType createDocumentType(Document doc, String name) {
	return ((org.apache.xerces.dom.DocumentImpl) doc).createDocumentType(name, null, null);	//Replace with a DocumentType creator
}
/**
 * version 3.0 01/25/99
 *  
 * @return org.w3c.dom.Entity
 * @param doc org.w3c.dom.Document
 * @param name java.lang.String
 *
 * @author Philip W. Davis
 */
public Entity createEntity(Document doc, String name) {
	return new org.apache.xerces.dom.EntityImpl((org.apache.xerces.dom.DocumentImpl)doc, name);	//Replace with an Entity creator
}
/**
 * version 3.0 01/25/99
 * 
 * @return org.w3c.dom.Notation
 * @param doc org.w3c.dom.Document
 * @param name java.lang.String
 *
 * @author Philip W. Davis
 */
public Notation createNotation(Document doc, String name) {
	return new org.apache.xerces.dom.NotationImpl((org.apache.xerces.dom.DocumentImpl) doc, name);	// Replace with a Notation creator
}
/**
 * This method builds test documents for the XML DOM implementation
 * version 2.0 10/12/98
 * @param document org.w3c.dom.Document
 * @param name document's name
 * @param type document's type
 *
 * @author Philip W. Davis
 */
public void docBuilder(org.w3c.dom.Document document, String name)
{
	Document doc = document;
	boolean OK = true;
		
	Element docFirstElement = doc.createElement(name + "FirstElement");
	doc.appendChild(docFirstElement);
	docFirstElement.setAttribute(name + "FirstElement", name + "firstElement");
	
	ProcessingInstruction docProcessingInstruction = doc.createProcessingInstruction(name +
					"TargetProcessorChannel", "This is " + doc + "'s processing instruction");
	docFirstElement.appendChild(docProcessingInstruction);
	
	Element docBody = doc.createElement(name + "TestBody");
	docFirstElement.appendChild(docBody);
	
	Element docBodyLevel21 = doc.createElement(name + "BodyLevel21");
	Element docBodyLevel22 = doc.createElement(name + "BodyLevel22");
	Element docBodyLevel23 = doc.createElement(name + "BodyLevel23");
	Element docBodyLevel24 = doc.createElement(name + "BodyLevel24");
	docBody.appendChild(docBodyLevel21);
	docBody.appendChild(docBodyLevel22);
	docBody.appendChild(docBodyLevel23);
	docBody.appendChild(docBodyLevel24);
	
	Element docBodyLevel31 = doc.createElement(name + "BodyLevel31");
	Element docBodyLevel32 = doc.createElement(name + "BodyLevel32");
	Element docBodyLevel33 = doc.createElement(name + "BodyLevel33");
	Element docBodyLevel34 = doc.createElement(name + "BodyLevel34");
	docBodyLevel21.appendChild(docBodyLevel31);
	docBodyLevel21.appendChild(docBodyLevel32);
	docBodyLevel22.appendChild(docBodyLevel33);
	docBodyLevel22.appendChild(docBodyLevel34);
	
	Text docTextNode11 = doc.createTextNode(name + "BodyLevel31'sChildTextNode11");
	Text docTextNode12 = doc.createTextNode(name + "BodyLevel31'sChildTextNode12");
	Text docTextNode13 = doc.createTextNode(name + "BodyLevel31'sChildTextNode13");
	Text docTextNode2 = doc.createTextNode(name + "TextNode2");
	Text docTextNode3 = doc.createTextNode(name + "TextNode3");
	Text docTextNode4 = doc.createTextNode(name + "TextNode4");
	docBodyLevel31.appendChild(docTextNode11);
	docBodyLevel31.appendChild(docTextNode12);
	docBodyLevel31.appendChild(docTextNode13);
	docBodyLevel32.appendChild(docTextNode2);
	docBodyLevel33.appendChild(docTextNode3);
	docBodyLevel34.appendChild(docTextNode4);
	
	CDATASection docCDATASection = doc.createCDATASection("<![CDATA[<greeting>Hello, world!</greeting>]]>");
	docBodyLevel23.appendChild(docCDATASection);
	
	Comment docComment = doc.createComment("This should be a comment of some kind ");
	docBodyLevel23.appendChild(docComment);
	
	EntityReference docReferenceEntity = doc.createEntityReference("ourEntityNode");
	docBodyLevel24.appendChild(docReferenceEntity);

	DTest make = new DTest();
	Notation docNotation = make.createNotation(doc, "ourNotationNode");
//	NotationImpl docNotation = new NotationImpl((DocumentImpl) doc, "ourNotationNode");//*****?
	DocumentType docType = (DocumentType)doc.getFirstChild();
	docType.getNotations().setNamedItem(docNotation);
	
	DocumentFragment docDocFragment = doc.createDocumentFragment();
	
//	System.out.println("This document's first element name is " + docFirstElement.getTagName() + "\n");


//***********Following are for errorTests
	Text docNode3 = doc.createTextNode(name + "docTextNode3");
	Text docNode4 = doc.createTextNode(name + "docTextNode4");
	
	Entity docEntity = (Entity) doc.getDoctype().getEntities().getNamedItem("ourEntityNode"); // Get the Entity node
	DocumentType docDocType = (DocumentType) doc.getFirstChild();	// Get the DocumentType node
	EntityReference entityReferenceText = (EntityReference) doc.getLastChild().getLastChild().getLastChild().getFirstChild();
	Text entityReferenceText2 = doc.createTextNode("entityReferenceText information");
//************************************************* ERROR TESTS
	DTest tests = new DTest();

	OK &= Assertion.verify(DTest.DOMExceptionsTest(document, "appendChild", new Class[]{Node.class}, new Object[]{docBody}, DOMException.HIERARCHY_REQUEST_ERR )); 
	OK &= Assertion.verify(DTest.DOMExceptionsTest(docNode3, "appendChild", new Class[]{Node.class}, new Object[]{docNode4}, DOMException.HIERARCHY_REQUEST_ERR )); 
	OK &= Assertion.verify(DTest.DOMExceptionsTest(doc, "insertBefore", new Class[]{Node.class, Node.class}, new Object[]{docEntity, docFirstElement}, DOMException.HIERARCHY_REQUEST_ERR )); 
	OK &= Assertion.verify(DTest.DOMExceptionsTest(doc, "replaceChild", new Class[]{Node.class, Node.class}, new Object[]{docCDATASection, docFirstElement}, DOMException.HIERARCHY_REQUEST_ERR )); 

        docFirstElement.setNodeValue("This shouldn't do anything!");
	OK &= Assertion.verify(docFirstElement.getNodeValue() == null);
        docReferenceEntity.setNodeValue("This shouldn't do anything!");
	OK &= Assertion.verify(docReferenceEntity.getNodeValue() == null);
        docEntity.setNodeValue("This shouldn't do anything!");
	OK &= Assertion.verify(docEntity.getNodeValue() == null);
        doc.setNodeValue("This shouldn't do anything!");
	OK &= Assertion.verify(doc.getNodeValue() == null);
        docType.setNodeValue("This shouldn't do anything!");
	OK &= Assertion.verify(docType.getNodeValue() == null);
        docDocFragment.setNodeValue("This shouldn't do anything!");
	OK &= Assertion.verify(docDocFragment.getNodeValue() == null);
        docNotation.setNodeValue("This shouldn't do anything!");
	OK &= Assertion.verify(docNotation.getNodeValue() == null);

	OK &= Assertion.verify(DTest.DOMExceptionsTest(docReferenceEntity, "appendChild", new Class[]{Node.class}, new Object[]{entityReferenceText2 }, DOMException.NO_MODIFICATION_ALLOWED_ERR ));
	OK &= Assertion.verify(DTest.DOMExceptionsTest(docBodyLevel32, "insertBefore", new Class[]{Node.class, Node.class}, new Object[]{docTextNode11,docBody }, DOMException.NOT_FOUND_ERR ));
	OK &= Assertion.verify(DTest.DOMExceptionsTest(docBodyLevel32, "removeChild", new Class[]{Node.class}, new Object[]{docFirstElement}, DOMException.NOT_FOUND_ERR ));
	OK &= Assertion.verify(DTest.DOMExceptionsTest(docBodyLevel32, "replaceChild", new Class[]{Node.class, Node.class}, new Object[]{docTextNode11,docFirstElement }, DOMException.NOT_FOUND_ERR ));


//!! Throws a NOT_FOUND_ERR	********
	 
	 //	docBodyLevel32.getAttributes().removeNamedItem(testAttribute.getName()); 	16  // To test removeNamedItem
	 
}//END OF DOCBUILDER
/**
 * version 3.0 01/25/99
 * 
 * @return boolean
 * @param node java.lang.Object
 * @param mNameIndex int
 * @param signatureIndex int
 * @param parameters java.lang.Object[]
 * @param code short
 *
 * @author Philip W. Davis
 */
public static boolean DOMExceptionsTest(Object node, String methodName, Class[] methodSignature, Object[] parameters, short code) {
	
	
	boolean asExpected = false;
	Method method;

	try
	{
		method = node.getClass().getMethod(methodName,methodSignature);
		method.invoke(node, parameters);
	}catch(InvocationTargetException exc)
	{
		Throwable realE = exc.getTargetException(); 
		if(realE instanceof DOMException)
		{
			asExpected = (((DOMException)realE).code== code);
			if(!asExpected)
				System.out.println("Wrong DOMException(" + ((DOMException)realE).code + ")");
		}
		else
			System.out.println("Wrong Exception (" + code + ")");

		if(!asExpected)
		{
			System.out.println("Expected DOMException (" + code + ") not thrown");			
		}
	}catch(Exception exc)
	{
		System.out.println("test invocation failure (" + exc + ")");
	}
	
	
	return (asExpected);
}

/**
 * @author Philip W. Davis
 * @param document org.w3c.dom.Document
 */
public void findTestNodes(Document document) {




	Node node = document;
	int nodeCount = 0;

	// Walk the tree until you find and assign all node types needed that exist.
	while (node != null && nodeCount < 12)
	{

		switch (node.getNodeType())
	{
		case org.w3c.dom.Node.ELEMENT_NODE :
			if (testElementNode == null) {testElementNode = (Element)node; nodeCount++;}
			break;
		case org.w3c.dom.Node.ATTRIBUTE_NODE :
			if (testAttributeNode == null) {testAttributeNode = (Attr)node; nodeCount++;}
			break;
		case org.w3c.dom.Node.TEXT_NODE :
			if (testTextNode == null) {testTextNode = (Text)node; nodeCount++;}
			break;
		case org.w3c.dom.Node.CDATA_SECTION_NODE :
			if (testCDATASectionNode == null) {testCDATASectionNode = (CDATASection)node; nodeCount++;}
			break;
		case org.w3c.dom.Node.ENTITY_REFERENCE_NODE :
			if (testEntityReferenceNode == null) {testEntityReferenceNode = (EntityReference)node; nodeCount++;}
			break;
		case org.w3c.dom.Node.ENTITY_NODE :
			if (testEntityNode == null) {testEntityNode = (Entity)node; nodeCount++;}
			break;
		case org.w3c.dom.Node.PROCESSING_INSTRUCTION_NODE :
			if (testProcessingInstructionNode == null) {testProcessingInstructionNode = (ProcessingInstruction)node; nodeCount++;}
			break;
		case org.w3c.dom.Node.COMMENT_NODE :
			if (testCommentNode == null) {testCommentNode = (Comment)node; nodeCount++;}
			break;
		case org.w3c.dom.Node.DOCUMENT_TYPE_NODE :
			if (testDocumentTypeNode == null) {testDocumentTypeNode = (DocumentType)node; nodeCount++;}
			break;
		case org.w3c.dom.Node.DOCUMENT_FRAGMENT_NODE :
			if (testDocumentFragmentNode == null) {testDocumentFragmentNode = (DocumentFragment)node; nodeCount++;}
			break;
		case org.w3c.dom.Node.NOTATION_NODE :
			if (testNotationNode == null) {testNotationNode = (Notation)node; nodeCount++;}
			break;
		case org.w3c.dom.Node.DOCUMENT_NODE :
			if (testDocumentNode == null) {testDocumentNode = (Document)node; nodeCount++;}
			break;
		default:
	}// End of switch

	


	}// End of while
	













	
}

/**
 * @author Philip W. Davis
 * @param document org.w3c.dom.Document
 */
public void findTestNodes(Node node) {

	DTest test = new DTest();
	Node kid;
	// Walk the tree until you find and assign all node types needed that exist.
	
		
	if (node.getFirstChild() != null)
	{
		kid = node.getFirstChild();
		test.findTestNodes(kid);
	}
			
				
	if (node.getNextSibling() != null)
	{
		kid = node.getNextSibling();
		test.findTestNodes(kid);
	}

		
	switch (node.getNodeType())
	{
		case org.w3c.dom.Node.ELEMENT_NODE :
			if (testElementNode == null) {testElementNode = (Element)node; }
			break;
		case org.w3c.dom.Node.ATTRIBUTE_NODE :
			if (testAttributeNode == null) {testAttributeNode = (Attr)node; }
			break;
		case org.w3c.dom.Node.TEXT_NODE :
			if (testTextNode == null) {testTextNode = (Text)node; }
			break;
		case org.w3c.dom.Node.CDATA_SECTION_NODE :
			if (testCDATASectionNode == null) {testCDATASectionNode = (CDATASection)node; }
			break;
		case org.w3c.dom.Node.ENTITY_REFERENCE_NODE :
			if (testEntityReferenceNode == null) {testEntityReferenceNode = (EntityReference)node;}
			break;
		case org.w3c.dom.Node.ENTITY_NODE :
			if (testEntityNode == null) {testEntityNode = (Entity)node;}
			break;
		case org.w3c.dom.Node.PROCESSING_INSTRUCTION_NODE :
			if (testProcessingInstructionNode == null) {testProcessingInstructionNode = (ProcessingInstruction)node;}
			break;
		case org.w3c.dom.Node.COMMENT_NODE :
			if (testCommentNode == null) {testCommentNode = (Comment)node;}
			break;
		case org.w3c.dom.Node.DOCUMENT_TYPE_NODE :
			if (testDocumentTypeNode == null) {testDocumentTypeNode = (DocumentType)node; }
			break;
		case org.w3c.dom.Node.DOCUMENT_FRAGMENT_NODE :
			if (testDocumentFragmentNode == null) {testDocumentFragmentNode = (DocumentFragment)node;}
			break;
		case org.w3c.dom.Node.NOTATION_NODE :
			if (testNotationNode == null) {testNotationNode = (Notation)node;}
			break;
		case org.w3c.dom.Node.DOCUMENT_NODE :
			if (testDocumentNode == null) {testDocumentNode = (Document)node;}
			break;
		default:
	}// End of switch
	

}
	
/**
 * 
 * version 2.0 10/12/98
 *
 * @author Philip W. Davis
 */

public static void main(String args[]) {
    System.out.println("# main()");
	
	DTest test = new DTest();

	long avgTime = 0;
	boolean OK = true;
	long startTime = 0;//****************Time the whole thing for efficiency of DOM implementation
	 
//	for (int i=0; i< 1000; i++)
//	{	
		startTime = System.currentTimeMillis();
//		if(!OK)
//		break;

	Document d = test.createDocument();
//	Document z = test.createDocument();

	DocumentType docDocType = test.createDocumentType(d,"testDocument1");
	d.appendChild(docDocType);

	Entity docEntity = test.createEntity( d, "ourEntityNode");
	Text entityChildText = d.createTextNode("entityChildText information"); // Build a branch for entityReference tests
        ((org.apache.xerces.dom.NodeImpl)docEntity).setReadOnly(false, true);
	docEntity.appendChild(entityChildText);					  // & for READONLY_ERR tests
        ((org.apache.xerces.dom.NodeImpl)docEntity).setReadOnly(true, true);
	docDocType.getEntities().setNamedItem(docEntity);
	
	test.docBuilder(d, "d");

	test.findTestNodes((Node)d);
//	test.docBuilder(z, "z");
	try {
/**/		test.testAttr(d);
		test.testCDATASection(d);
		test.testCharacterData(d);
		test.testChildNodeList(d);
		test.testComment(d);
		test.testDeepNodeList(d);
		test.testDocument(d);
		test.testDocumentFragment(d);
		test.testDocumentType(d);
		test.testDOMImplementation(d);
		test.testElement(d);
		test.testEntity(d);
		test.testEntityReference(d);
		test.testNode(d);
		test.testNotation(d);
		test.testPI(d);
		test.testText(d);
/**/		test.testDOMerrors(d);
	
//!! Throws WRONG_DOCUMENT_ERR **********
		
	//	z.appendChild(d.createComment("Test doc d comment"));// Tries to append z document with document d comment
	//	d.getDocumentElement().appendChild(z.createElement("newZdocElement"));// Tries to append d document with document z Element
	//	d.getLastChild().getLastChild().insertBefore(z.createElement("newZdocElement"),d.getLastChild().getLastChild().getFirstChild());// Tries to insert into d document with document z Element
	//	d.replaceChild(z.createElement("newZdocElement"),d.getLastChild().getLastChild().getFirstChild());	// Tries to replace in d document with document z Element

	/*	Attribute newAttribute = d.createAttribute("newAttribute");
		d.getDocumentElement().setAttributeNode(newAttribute);
		d.getDocumentElement().getAttributes().setNamedItem(z.createAttribute("newzAttribute"));
	*/
		
//!! Throws INVALID_CHARACTER_ERR **********
	// ******This just gets us through each method. JKess has a comprehensive test of Invalid Names******
	//	d.createAttribute("Invalid Name"); // Name with blank space
	//	d.createElement("5InvalidName"); // Name starts with numeric
	//	d.createProcessingInstruction("This is the target processor channel","InvalidName>");// Name ends with >
	//	d.getDocumentElement().setAttribute("Invalid%Name",""); // Name contains %
		

//!!	******** NO_DATA_ALLOWED_ERR ********No cases to test as of 9/15


//!! 	******** NO_MODIFICATION_ALLOWED_ERR ******** When read only exists
	/*
		

		
		//**** FOR Element when read only exists********
		.removeAttribute("aString");		   //***** Not until read only exists.
		.removeAttributeNode(Attribute); 	   //***** Not until read only exists.
		.setAttribute("aString", "anotherString"); //***** Not until read only exists.
		
		
		//**** FOR Node when read only exists********
		.appendChild(aNode);			//***** Not until read only exists.
		.insertBefore(aNode, AnotherNode);	//***** Not until read only exists.
		.removeChild(aNode);			//***** Not until read only exists.
		.replaceChild(aNode);			//***** Not until read only exists.
		
		.splitText(2); //***** Not until read only exists.
		
		.setNamedItem(Node); //***** Not until read only exists.
	*/
	

//!!******** NOT_SUPPORTED_ERR	********For HTML when implemented
	/*
		.createCDATASection("String stuff");
		.createEntityReference("String stuff");
		.createProcessingInstruction("String stuff", "Some more String stuff");
	*/

	} catch (Exception e) {
		System.out.println("Exception is: ");
		e.printStackTrace();
		OK = false;
		
	}
//System.err.println("Elapsed time (measured in seconds): " +   ((System.currentTimeMillis() - startTime) / 1000.0));
	avgTime += System.currentTimeMillis() - startTime;
//	}//END OF FOR
	  
	
//	System.err.println("Elapsed time (measured in seconds): " +
//					   ((System.currentTimeMillis() - startTime) / 1000.0));
//	      System.err.println("Elapsed time (measured in mili-seconds): " +
//					   ((System.currentTimeMillis() - startTime)));


//	System.err.println("Average Elapsed time (measured in seconds): " + (avgTime/10000000.0) );

}
/**
 * This method tests Attr methods for the XML DOM implementation
 * version 2.0 10/12/98
 * @param document org.w3c.dom.Document
 *
 * @author Philip W. Davis
 */
public void testAttr(org.w3c.dom.Document document)
{
	
	Node node;	
	Attr attributeNode, attribute2;
	String compare;
	boolean T = true;
	boolean F = false;
	boolean OK = true;
// For debugging*****	println("\n          testAttr's outputs:\n");

	Attr testAttribute = document.createAttribute("testAttribute");
	testAttribute.setValue("testAttribute's value");
	node = document.getDocumentElement(); // node gets first element
	((Element)node).setAttributeNode(testAttribute);
	attributeNode = ((Element)node).getAttributeNode("testAttribute");

	compare = "testAttribute";
	if (!compare.equals(attributeNode.getName()))
	{
		System.out.println("Warning!!! Attr's 'getName' method failed to work properly!");
		OK = false;
	}
	compare = "testAttribute's value";
	if (!compare.equals(attributeNode.getNodeValue()))
	{
		System.out.println("Warning!!! Attr's 'getNodeValue' method failed to work properly!");
		OK = false;
	}
	if (! T ==attributeNode.getSpecified())
	{
		System.out.println("Warning!!! Attr's 'getSpecified' method failed to work properly!");
		OK = false;
	}
	
	if (!compare.equals(attributeNode.getValue()))
	{
		System.out.println("Warning!!! Attr's 'getValue' method failed to work properly!");
		OK = false;
	}
	
	attributeNode.setNodeValue("Reset Value");
	compare = "Reset Value";
	if (!compare.equals(attributeNode.getNodeValue()))
	{
		System.out.println("Warning!!! Attr's 'setNodeValue' method failed to work properly!");
		OK = false;
	}
	((org.apache.xerces.dom.AttrImpl)attributeNode).setSpecified(F);//***** How do we change this for external use??
	if (! F ==attributeNode.getSpecified())
	{
		System.out.println("Warning!!! Attr's 'setSpecified' method failed to work properly!");
		OK = false;
	}
	
	attributeNode.setValue(null);
	if (! attributeNode.getValue().equals(""))
	{
		System.out.println("Warning!!! Attr's 'setValue' to 'null' method failed to work properly!");
		OK = false;
	}
	
	attributeNode.setValue("Another value ");
	compare = "Another value ";
	if (!compare.equals(attributeNode.getValue()))
	{
		System.out.println("Warning!!! Attr's 'setValue' method failed to work properly!");
		OK = false;
	}

	node = attributeNode.cloneNode(T);//*****?
	// Check nodes for equality, both their name and value or lack thereof
	if (! (node.getNodeName().equals(attributeNode.getNodeName()) &&	     // Compares node names for equality
	      (node.getNodeValue() != null && attributeNode.getNodeValue() != null)  // Checks to make sure each node has a value node
	    ?  node.getNodeValue().equals(attributeNode.getNodeValue()) 	     // If both have value nodes test those value nodes for equality
	    : (node.getNodeValue() == null && attributeNode.getNodeValue() == null)))// If one node doesn't have a value node make sure both don't
		{	
			System.out.println("'cloneNode' did not clone the Attribute node correctly");
			OK = false;
		}
		// Deep clone test comparison is in testNode & testDocument

//************************************************* ERROR TESTS
	DTest tests = new DTest();
        Assertion.verify(
          DTest.DOMExceptionsTest(document.getDocumentElement(),
                                  "appendChild",
                                  new Class[]{Node.class},
                                  new Object[]{attributeNode},
                                  DOMException.HIERARCHY_REQUEST_ERR));

	attribute2 = document.createAttribute("testAttribute2");
        Assertion.verify(
          DTest.DOMExceptionsTest(document.getDocumentElement(),
                                  "removeAttributeNode",
                                  new Class[]{Attr.class},
                                  new Object[]{attribute2},
                                  DOMException.NOT_FOUND_ERR));

        Element element = (Element)document.getLastChild().getLastChild();
        // Tests setNamedItem
        Assertion.verify(
          DTest.DOMExceptionsTest(element,
                                  "setAttributeNode",
                                  new Class[]{Attr.class},
                                  new Object[]{testAttribute},
                                  DOMException.INUSE_ATTRIBUTE_ERR));
	
	if (! OK)
		System.out.println("\n*****The Attr method calls listed above failed, all others worked correctly.*****");
//	println("");
}
/**
 * This method tests CDATASection methods for the XML DOM implementation
 * version 2.0 10/12/98
 * @param document org.w3c.dom.Document
 *
 * @author Philip W. Davis
 */
public void testCDATASection(org.w3c.dom.Document document)
{
	
	Node node, node2;
	boolean T = true;
	boolean OK = true;
// For debugging*****	println("\n          testCDATASection's outputs:\n");
	node = document.getDocumentElement().getElementsByTagName("dBodyLevel23").item(0).getFirstChild(); // node gets CDATASection node

	node2 = node.cloneNode(T);//*****?
	// Check nodes for equality, both their name and value or lack thereof
	if (! (node.getNodeName().equals(node2.getNodeName()) && 		// Compares node names for equality
	      (node.getNodeValue() != null && node2.getNodeValue() != null)     // Checks to make sure each node has a value node
	    ?  node.getNodeValue().equals(node2.getNodeValue()) 		// If both have value nodes test those value nodes for equality
	    : (node.getNodeValue() == null && node2.getNodeValue() == null)))	// If one node doesn't have a value node make sure both don't
	{
		System.out.println("'cloneNode' did not clone the CDATASection node correctly");
		OK = false;
	}
	// Deep clone test comparison is in testNode & testDocument
	
// For debugging*****	println("All CDATASection method calls worked correctly.");
		
	if (! OK)
		System.out.println("\n*****The CDATASection method calls listed above failed, all others worked correctly.*****");
//	println("");
}
/**
 * This method tests CharacterData methods for the XML DOM implementation
 * version 2.0 10/12/98
 * @param document org.w3c.dom.Document
 *
 * @author Philip W. Davis
 */
public void testCharacterData(org.w3c.dom.Document document)
{
	CharacterData charData;
	String compareData, newData, resetData;
	boolean OK = true;
// For debugging*****	println("\n          testCharacterData's outputs:\n");
	charData = (CharacterData) document.getDocumentElement().getElementsByTagName("dBodyLevel31").item(0).getFirstChild(); // charData gets textNode11
	compareData = "dBodyLevel31'sChildTextNode11";
	if (!compareData.equals(charData.getData()))
	{
		System.out.println("Warning!!! CharacterData's 'getData' failed to work properly!\n This may corrupt other CharacterData tests!!!*****");
		OK = false;
	}	
	
	resetData = charData.getData();
	//  println("This node's original data is: " + charData.getData());

	newData = " This is new data for this node";
	compareData = charData.getData() + newData;
	charData.appendData(newData);
	if (!compareData.equals(charData.getData()))
	{
		System.out.println("Warning!!! CharacterData's 'appendData' failed to work properly!");
		OK = false;
	}
	//	println("This node's appended data is: " + charData.getData());

	compareData = "dBodyLevel";
	charData.deleteData(10, 100);
	if (!compareData.equals(charData.getData()))
	{
		System.out.println("Warning!!! CharacterData's 'deleteData' failed to work properly!");
		OK = false;
	}
	//  println("This node's partially deleted data is: " + charData.getData());

	int length = 10;
	if (!(length == charData.getLength()))
	{
		System.out.println("Warning!!! CharacterData's 'getLength' failed to work properly!");
		OK = false;
	}
	//  println("This node's data length is: " + charData.getLength());

	compareData = "dBody' This is data inserted into this node'Level";
	charData.insertData(5, "' This is data inserted into this node'");
	if (!compareData.equals(charData.getData()))
	{
		System.out.println("Warning!!! CharacterData's 'insertData' failed to work properly!");
		OK = false;
	}
	//	println("This node's updated with insert data is: " + charData.getData());

	compareData = "dBody' This is ' replacement data'ted into this node'Level";
	charData.replaceData(15, 10, "' replacement data'");
	if (!compareData.equals(charData.getData()))
	{
		System.out.println("Warning!!! CharacterData's 'replaceData' failed to work properly!");
		OK = false;
	}
	//	println("This node's updated with replacement data is: " +charData.getData());

	compareData = "New data A123456789B123456789C123456789D123456789E123456789";
	charData.setData("New data A123456789B123456789C123456789D123456789E123456789");
	if (!compareData.equals(charData.getData()))
	{
		System.out.println("Warning!!! CharacterData's 'setData' failed to work properly!");
		OK = false;
	}
	//	println("This node's new data via setData: " + charData.getData());

	compareData = "123456789D123456789E123456789";
	if (!compareData.equals(charData.substringData(30, 30)))
	{
		System.out.println("Warning!!! CharacterData's 'substringData' failed to work properly!");
		OK = false;
	}
	//	println("Using subString 30,30 you get:" + charData.substringData(30,30));

	compareData = "New data A123456789B12345";
	if (!compareData.equals(charData.substringData(0, 25)))
	{
		System.out.println("Warning!!! CharacterData's 'substringData' failed to work properly!");
		OK = false;
	}
	//	println("Using subString 0,25 you get:" + charData.substringData(0,25));

//************************************************* ERROR TESTS
	DTest tests = new DTest();

//!! Throws INDEX_SIZE_ERR ********************
	OK &= Assertion.verify(DTest.DOMExceptionsTest(charData, "deleteData", new Class[]{int.class, int.class}, 
			new Object[]{new Integer(-1),new Integer(5) }, DOMException.INDEX_SIZE_ERR ));
	OK &= Assertion.verify(DTest.DOMExceptionsTest(charData, "deleteData", new Class[]{int.class, int.class}, 
			new Object[]{new Integer(2),new Integer(-1) }, DOMException.INDEX_SIZE_ERR ));
	OK &= Assertion.verify(DTest.DOMExceptionsTest(charData, "deleteData", new Class[]{int.class, int.class}, 
			new Object[]{new Integer(100),new Integer(5) }, DOMException.INDEX_SIZE_ERR ));
	
	OK &= Assertion.verify(DTest.DOMExceptionsTest(charData, "insertData", new Class[]{int.class, String.class}, 
			new Object[]{new Integer(-1),"Stuff inserted" }, DOMException.INDEX_SIZE_ERR ));
	OK &= Assertion.verify(DTest.DOMExceptionsTest(charData, "insertData", new Class[]{int.class, String.class}, 
			new Object[]{new Integer(100),"Stuff inserted" }, DOMException.INDEX_SIZE_ERR ));
	
	OK &= Assertion.verify(DTest.DOMExceptionsTest(charData, "replaceData", new Class[]{int.class, int.class, String.class}, 
			new Object[]{new Integer(-1),new Integer(5),"Replacement stuff" }, DOMException.INDEX_SIZE_ERR ));
	OK &= Assertion.verify(DTest.DOMExceptionsTest(charData, "replaceData", new Class[]{int.class, int.class, String.class}, 
			new Object[]{new Integer(100),new Integer(5),"Replacement stuff" }, DOMException.INDEX_SIZE_ERR ));
	OK &= Assertion.verify(DTest.DOMExceptionsTest(charData, "replaceData", new Class[]{int.class, int.class, String.class}, 
			new Object[]{new Integer(2),new Integer(-1),"Replacement stuff" }, DOMException.INDEX_SIZE_ERR ));
	
	OK &= Assertion.verify(DTest.DOMExceptionsTest(charData, "substringData", new Class[]{int.class, int.class}, 
			new Object[]{new Integer(-1),new Integer(5) }, DOMException.INDEX_SIZE_ERR ));
	OK &= Assertion.verify(DTest.DOMExceptionsTest(charData, "substringData", new Class[]{int.class, int.class}, 
			new Object[]{new Integer(100),new Integer(5) }, DOMException.INDEX_SIZE_ERR ));
	OK &= Assertion.verify(DTest.DOMExceptionsTest(charData, "substringData", new Class[]{int.class, int.class}, 
			new Object[]{new Integer(2),new Integer(-1) }, DOMException.INDEX_SIZE_ERR ));
	

//!! Throws NO_MODIFICATION_ALLOWED_ERR ******** 
	Node node = document.getDocumentElement().getElementsByTagName("dBodyLevel24").item(0).getFirstChild().getChildNodes().item(0); // node gets ourEntityReference node's child text

	OK &= Assertion.verify(DTest.DOMExceptionsTest(node, "appendData", new Class[]{String.class}, 
			new Object[]{"new data" }, DOMException.NO_MODIFICATION_ALLOWED_ERR ));
	OK &= Assertion.verify(DTest.DOMExceptionsTest(node, "deleteData", new Class[]{int.class, int.class}, 
			new Object[]{new Integer(5),new Integer(10) }, DOMException.NO_MODIFICATION_ALLOWED_ERR ));
	OK &= Assertion.verify(DTest.DOMExceptionsTest(node, "insertData", new Class[]{int.class, String.class}, 
			new Object[]{new Integer(5),"Stuff inserted" }, DOMException.NO_MODIFICATION_ALLOWED_ERR ));
	OK &= Assertion.verify(DTest.DOMExceptionsTest(node, "replaceData", new Class[]{int.class, int.class, String.class}, 
			new Object[]{new Integer(5),new Integer(10),"Replacementstuff" }, DOMException.NO_MODIFICATION_ALLOWED_ERR ));
	OK &= Assertion.verify(DTest.DOMExceptionsTest(node, "setData", new Class[]{String.class}, 
			new Object[]{"New setdata stuff"}, DOMException.NO_MODIFICATION_ALLOWED_ERR ));
	
		
// For debugging*****		println("All CharacterData method calls worked correctly.");
	if (!OK)
		System.out.println("\n*****The CharacterData method calls listed above failed, all others worked correctly.*****");
	charData.setData(resetData); // reset node to original data
//	println("");
}
/**
 * This method tests ChildNodeList methods for the XML DOM implementation
 * version 2.0 10/12/98
 * @param document org.w3c.dom.Document
 *
 * @author Philip W. Davis
 */
public void testChildNodeList(org.w3c.dom.Document document)
{
	
	Node node, node2;
	boolean OK = true;
// For debugging*****	println("\n          testChildNodeList's outputs:\n");
	node = document.getDocumentElement().getLastChild(); // node gets doc's testBody element
	
	if (!(node.getChildNodes().getLength()== 4))
		OK = false;
	node2 = node.getChildNodes().item(2);
	if (! node2.getNodeName().equals("dBodyLevel23"))
		OK = false;
	
// For debugging*****		println("All ChildNodeList method calls worked correctly.");
	if (!OK)
		System.out.println("\n*****The ChildNodeList method calls listed above failed, all others worked correctly.*****");		
//	println("");
}
/**
 * This method tests Comment methods for the XML DOM implementation
 * version 1.0 10/12/98
 * @param document org.w3c.dom.Document
 *
 * @author Philip W. Davis
 */
public void testComment(org.w3c.dom.Document document)
{
	Node node, node2;
	boolean T = true;
	boolean OK = true;
// For debugging*****	println("\n          testComment's outputs:\n");
	node = document.getDocumentElement().getElementsByTagName("dBodyLevel31").item(0).getFirstChild(); // node gets textNode11
	node2 = node.cloneNode(T);
	// Check nodes for equality, both their name and value or lack thereof
	if (!(node.getNodeName().equals(node2.getNodeName()) && 		// Compares node names for equality
	      (node.getNodeValue() != null && node2.getNodeValue() != null)     // Checks to make sure each node has a value node
	    ?  node.getNodeValue().equals(node2.getNodeValue()) 		// If both have value nodes test those value nodes for equality
	    : (node.getNodeValue() == null && node2.getNodeValue() == null)))	// If one node doesn't have a value node make sure both don't
		//println("'cloneNode' did not clone the Comment node correctly");
		OK = false;
	// Deep clone test comparison is in testNode & testDocument
	if (OK)
// For debugging*****		println("All Comment method calls worked correctly.");
	if (!OK)
		System.out.println("\n*****The Comment method calls listed above failed, all others worked correctly.*****");
//	println("");
}
/**
 * This method tests DeepNodeList methods for the XML DOM implementation
 * version 2.0 10/12/98
 * @param document org.w3c.dom.Document
 *
 * @author Philip W. Davis
 */
public void testDeepNodeList(org.w3c.dom.Document document)
{
	
	Node node, node2;
	boolean OK = true;
// For debugging*****	println("\n          testDeepNodeList's outputs:\n");
	node = document.getLastChild().getLastChild(); // node gets docBody element
	if (!(8 == ((Element) node).getElementsByTagName("*").getLength()))
		{
			System.out.println ("Warning!!! DeepNodeList's 'getLength' failed to work properly!");
			OK = false;		
		}
	node2 = ((Element) node).getElementsByTagName("*").item(2); //This also runs through 'nextMatchingElementAfter"
	if (! node2.getNodeName().equals("dBodyLevel32"))
		{
			System.out.println ("Warning!!! DeepNodeList's 'item' (or Element's 'getElementsBy TagName)failed to work properly!");
			OK = false;		
		}
	node2 = document.getLastChild();
	if (! ((Element) node2).getElementsByTagName("dTestBody").item(0).getNodeName().equals("dTestBody"))//This also runs through 'nextMatchingElementAfter"
		{
			System.out.println ("Warning!!! DeepNodeList's 'item' (or Element's 'getElementsBy TagName)failed to work properly!");
			OK = false;		
		}
		
	
// For debugging*****		println("All DeepNodeList method calls worked correctly.");
	if (!OK)
		System.out.println("\n*****The DeepNodeList method calls listed above failed, all others worked correctly.*****");
//	println("");
}
/**
 * This method tests Document methods for the XML DOM implementation
 * version 2.0 10/12/98
 * @param document org.w3c.dom.Document
 *
 * @author Philip W. Davis
 *
 **** ALL Document create methods are run in docBuilder except createAttribute which is in testAttribute**
 */
public void testDocument(org.w3c.dom.Document document)
{
	DTest make = new DTest();
	DocumentFragment docFragment, docFragment2;
	Element newElement;
	Node node, node2;
	String[] elementNames =  {"dFirstElement", "dTestBody", "dBodyLevel21","dBodyLevel31","dBodyLevel32",
				   "dBodyLevel22","dBodyLevel33","dBodyLevel34","dBodyLevel23","dBodyLevel24"};
	String[] newElementNames = {"dFirstElement", "dTestBody", "dBodyLevel22","dBodyLevel33","dBodyLevel34","dBodyLevel23"};
	boolean result;
	boolean OK = true;
// For debugging*****	println("\n          testDocument's outputs:\n ");
	
	DocumentType checkDocType =  make.createDocumentType(document,"testDocument1");
	DocumentType docType = document.getDoctype();
	if (! (checkDocType.getNodeName().equals(docType.getNodeName()) && 		// Compares node names for equality
	      (checkDocType.getNodeValue() != null && docType.getNodeValue() != null)   // Checks to make sure each node has a value node
	    ?  checkDocType.getNodeValue().equals(docType.getNodeValue()) 		// If both have value nodes test those value nodes for equality
	    : (checkDocType.getNodeValue() == null && docType.getNodeValue() == null)))	// If one node doesn't have a value node make sure both don't
	{
		System.out.println("Warning!!! Document's 'getDocType method failed!" );
		OK = false;
	}
		
	Node rootElement = document.getLastChild();
	if (! (rootElement.getNodeName().equals(document.getDocumentElement().getNodeName()) && 		// Compares node names for equality
	      (rootElement.getNodeValue() != null && document.getDocumentElement().getNodeValue() != null)   // Checks to make sure each node has a value node
	    ?  rootElement.getNodeValue().equals(document.getDocumentElement().getNodeValue()) 		// If both have value nodes test those value nodes for equality
	    : (rootElement.getNodeValue() == null && document.getDocumentElement().getNodeValue() == null)))	// If one node doesn't have a value node make sure both don't
	{
		System.out.println("Warning!!! Document's 'getDocumentElement' method failed!" );
		OK = false;
	}
	
	NodeList docElements = document.getElementsByTagName("*");
	int docSize = docElements.getLength();
	int i;
	for (i = 0; i < docSize; i++)
	{
		Node n = (Node) docElements.item(i);
		if (! (elementNames[i].equals(n.getNodeName())))
		{
			System.out.println("Comparison of this document's elements failed at element number " + i + " : " + n.getNodeName());
			OK = false;
			break;
		}
	}
	if (document.equals(document.getImplementation()))
	{
		System.out.println("Warning!!! Document's 'getImplementation' method failed!" );
		OK = false;		
	}
		
	newElement = document.createElement("NewElementTestsInsertBefore");
	//	doc.insertBefore(newElement,null);//!! Throws a HIERARCHY_REQUEST_ERR	*******	
	//	doc.removeChild(docElements.item(9));//!! Throws a NOT_FOUND_ERR  ********

	docFragment = document.createDocumentFragment();
	//Tests removeChild and stores removed branch for tree reconstruction
	docFragment.appendChild(docElements.item(1).removeChild(docElements.item(9)));
	docFragment2 = document.createDocumentFragment();
	//Tests removeChild and stores removed branch for tree reconstruction
	docFragment2.appendChild(docElements.item(1).removeChild(docElements.item(2)));
	docSize = docElements.getLength();
	for (i = 0; i < docSize; i++)
	{
		Node n = (Node) docElements.item(i);
		if (! (newElementNames[i].equals(n.getNodeName())))
		{
			System.out.println("Comparison of new document's elements failed at element number " + i + " : " + n.getNodeName());
			OK = false;
			break;
		}
	}
	docElements.item(1).insertBefore(docFragment, null); //Reattaches removed branch to restore tree to the original
	docElements.item(1).insertBefore(docFragment2, docElements.item(2)); //Reattaches removed branch to restore tree to the original

	//	println(docElements.item(2).getNodeName());

	docSize = docElements.getLength();
	for (i = 0; i < docSize; i++)
	{
		Node n = (Node) docElements.item(i);
		if (! (elementNames[i].equals(n.getNodeName())))
		{
			System.out.println("Comparison of restored document's elements failed at element number " + i + " : " + n.getNodeName());
			OK = false;
			break;
		}
	}

	DTest tests = new DTest();

	
//	Document z = tests.createDocument();
//	tests.docBuilder(z, "z");

//!! Throws WRONG_DOCUMENT_ERR **********
//	OK &= Assertion.assert(tests.DOMExceptionsTest(z, "appendChild", new Class[]{Node.class}, new Object[]{doc.createComment("Test doc d comment")}, DOMException.HIERARCHY_REQUEST_ERR )); 
		
	//	z.appendChild(d.createComment("Test doc d comment"));// Tries to append z document with document d comment
	//	d.getDocumentElement().appendChild(z.createElement("newZdocElement"));// Tries to append d document with document z Element
	//	d.getLastChild().getLastChild().insertBefore(z.createElement("newZdocElement"),d.getLastChild().getLastChild().getFirstChild());// Tries to insert into d document with document z Element
	//	d.replaceChild(z.createElement("newZdocElement"),d.getLastChild().getLastChild().getFirstChild());	// Tries to replace in d document with document z Element

	//	doc.setNodeValue("This shouldn't work");//!! Throws a NO_MODIFICATION_ALLOWED_ERR ********
	
	node = document;
	node2 = document.cloneNode(true);
	result = treeCompare(node, node2); // Deep clone test comparison of document cloneNode
	if (!result)
	{
		System.out.println("Warning!!! Deep clone of the document failed!");
		OK = false;
	}

	// check on the ownerDocument of the cloned nodes
	Document doc2 = (Document) node2;
	Assertion.verify(doc2.getDocumentElement().getOwnerDocument() == doc2);

	// Deep clone test comparison is also in testNode

	// try adding a new element to the cloned document
	node2 = doc2.createElement("foo");
	doc2.getDocumentElement().appendChild(node2);
	
// For debugging*****		println("All Document method calls worked correctly.");
	if (!OK)
		System.out.println("\n*****The Document method calls listed above failed, all others worked correctly.*****");
//	println("");
}
/**
 * This method tests DocumentFragment methods for the XML DOM implementation
 * version 2.0 10/12/98
 * @param document org.w3c.dom.Document
 *
 * @author Philip W. Davis
 *
 *
 ********This really isn't needed, only exists to throw NO_MODIFICATION_ALLOWED_ERR ********
 */
public void testDocumentFragment(org.w3c.dom.Document document)
{
	boolean OK = true;
// For debugging*****	println("\n          testDocumentFragment's outputs:\n");
	DocumentFragment testDocFragment = document.createDocumentFragment();
		
	//	testDocFragment.setNodeValue("This is a document fragment!");//!! Throws a NO_MODIFICATION_ALLOWED_ERR ********
	
// For debugging*****		println("All DocumentFragment method calls worked correctly.");
	if (!OK)
		System.out.println("\n*****The DocumentFragment method calls listed above failed, all others worked correctly.*****");
//	println("");
}
/**
 * This method tests DocumentType methods for the XML DOM implementation
 * version 2.0 10/12/98
 * @param document org.w3c.dom.Document
 *
 * @author Philip W. Davis
 */
public void testDocumentType(org.w3c.dom.Document document)
{
	DTest test = new DTest();
	DocumentType docType, holdDocType;
	NamedNodeMap docEntityMap, docNotationMap;
	Node node, node2;
	String compare;
	boolean OK = true;
// For debugging*****	println("\n          testDocumentType's outputs:\n");
	DocumentType newDocumentType =  test.createDocumentType(document, "TestDocument");
	node = document.getFirstChild(); // node gets doc's docType node
	node2 = node.cloneNode(true);
	// Check nodes for equality, both their name and value or lack thereof
	if (! (node.getNodeName().equals(node2.getNodeName()) && 	     // Compares node names for equality
	      (node.getNodeValue() != null && node2.getNodeValue() != null)  // Checks to make sure each node has a value node
	    ?  node.getNodeValue().equals(node2.getNodeValue()) 	     // If both have value nodes test those value nodes for equality
	    : (node.getNodeValue() == null && node2.getNodeValue() == null)))// If one node doesn't have a value node make sure both don't
	{	
		System.out.println("'cloneNode' did not clone the DocumentType node correctly");
		OK = false;
	}
	 // Deep clone test comparison is in testNode & testDocument

	docType = (DocumentType) document.getFirstChild();
	compare = "ourEntityNode";
	docEntityMap = docType.getEntities();
	if (! compare.equals(docEntityMap.item(0).getNodeName()))
	{
		System.out.println("Warning!!! DocumentType's 'getEntities' failed!" );
		OK = false;
	}
	docNotationMap = docType.getNotations();
	compare = "ourNotationNode";
	if (! compare.equals(docNotationMap.item(0).getNodeName()))
	{
		System.out.println("Warning!!! DocumentType's 'getNotations' failed!");
		OK = false;
	}
	//	doc.appendChild(newDocumentTypeImpl);//!! Throws a HIERARCHY_REQUEST_ERR	*******	
	holdDocType = (DocumentType) document.removeChild(document.getFirstChild()); //Tests removeChild and stores removed branch for tree reconstruction
	document.insertBefore(newDocumentType, document.getDocumentElement());
	//** Other aspects of insertBefore are tested in docBuilder through appendChild*

	document.removeChild(document.getFirstChild()); //Removes newDocumentType for tree restoral
	document.insertBefore(holdDocType, document.getFirstChild()); //Reattaches removed branch to restore tree to the original

	
// For debugging*****		println("All DocumentType method calls worked correctly.");
	if (!OK)
		System.out.println("\n*****The DocumentType method calls listed above failed, all others worked correctly.*****");
//	println("");
}
/**
 * @author Philip W. Davis
 * @param document org.w3c.dom.Document
 */
public void testDOMerrors(Document document) {

	boolean OK = true;

	DTest tests = new DTest();

	OK &= Assertion.verify(DTest.DOMExceptionsTest(document, "appendChild", new Class[]{Node.class}, new Object[]{testElementNode}, DOMException.HIERARCHY_REQUEST_ERR )); 
	OK &= Assertion.verify(DTest.DOMExceptionsTest(testTextNode, "appendChild", new Class[]{Node.class}, new Object[]{testTextNode}, DOMException.HIERARCHY_REQUEST_ERR )); 
//	OK &= Assertion.assert(tests.DOMExceptionsTest(document, "insertBefore", new Class[]{Node.class, Node.class}, new Object[]{document.getElementsByTagName("docEntity").item(0), document.getElementsByTagName("docFirstElement").item(0)}, DOMException.HIERARCHY_REQUEST_ERR )); 
//	OK &= Assertion.assert(tests.DOMExceptionsTest(document, "replaceChild", new Class[]{Node.class, Node.class}, new Object[]{document.getElementsByTagName("docCDATASection").item(0), document.getElementsByTagName("docFirstElement").item(0)}, DOMException.HIERARCHY_REQUEST_ERR )); 

//	OK &= Assertion.assert(tests.DOMExceptionsTest(document.getElementsByTagName("docFirstElement").item(0), "setNodeValue", new Class[]{String.class}, new Object[]{"This shouldn't work!" }, DOMException.NO_MODIFICATION_ALLOWED_ERR ));	
/*	OK &= Assertion.assert(tests.DOMExceptionsTest(docReferenceEntity, "setNodeValue", new Class[]{String.class}, new Object[]{"This shouldn't work!" }, DOMException.NO_MODIFICATION_ALLOWED_ERR ));
	OK &= Assertion.assert(tests.DOMExceptionsTest(docEntity, "setNodeValue", new Class[]{String.class}, new Object[]{"This shouldn't work!" }, DOMException.NO_MODIFICATION_ALLOWED_ERR ));
	OK &= Assertion.assert(tests.DOMExceptionsTest(document, "setNodeValue", new Class[]{String.class}, new Object[]{"This shouldn't work!" }, DOMException.NO_MODIFICATION_ALLOWED_ERR ));
	OK &= Assertion.assert(tests.DOMExceptionsTest(docDocType, "setNodeValue", new Class[]{String.class}, new Object[]{"This shouldn't work!" }, DOMException.NO_MODIFICATION_ALLOWED_ERR ));
	OK &= Assertion.assert(tests.DOMExceptionsTest(docDocFragment, "setNodeValue", new Class[]{String.class}, new Object[]{"This shouldn't work!" }, DOMException.NO_MODIFICATION_ALLOWED_ERR ));
	OK &= Assertion.assert(tests.DOMExceptionsTest(docNotation, "setNodeValue", new Class[]{String.class}, new Object[]{"This shouldn't work!" }, DOMException.NO_MODIFICATION_ALLOWED_ERR ));
	OK &= Assertion.assert(tests.DOMExceptionsTest(docReferenceEntity, "appendChild", new Class[]{Node.class}, new Object[]{entityReferenceText2 }, DOMException.NO_MODIFICATION_ALLOWED_ERR ));


	OK &= Assertion.assert(tests.DOMExceptionsTest(docBodyLevel32, "insertBefore", new Class[]{Node.class, Node.class}, new Object[]{docTextNode11,docBody }, DOMException.NOT_FOUND_ERR ));
	OK &= Assertion.assert(tests.DOMExceptionsTest(docBodyLevel32, "removeChild", new Class[]{Node.class}, new Object[]{docFirstElement}, DOMException.NOT_FOUND_ERR ));
	OK &= Assertion.assert(tests.DOMExceptionsTest(docBodyLevel32, "replaceChild", new Class[]{Node.class, Node.class}, new Object[]{docTextNode11,docFirstElement }, DOMException.NOT_FOUND_ERR ));
*/

//!! Throws a NOT_FOUND_ERR	********
	 
	 //	docBodyLevel32.getAttributes().removeNamedItem(testAttribute.getName()); 	16  // To test removeNamedItem
	 











	
}
/**
 * This method tests DOMImplementation methods for the XML DOM implementation
 * version 2.0 10/12/98
 * @param document org.w3c.dom.Document
 *
 * @author Philip W. Davis
 */
public void testDOMImplementation(org.w3c.dom.Document document)
{
	
	DOMImplementation implementation;
	boolean result = false;
	boolean OK = true;
// For debugging*****	println("\n          testDOMImplementation's outputs:\n");
	implementation = document.getImplementation(); //Uses getDOMImplementation to obtain implementation	

	result = implementation.hasFeature("XML", "1.0");
	if(!result)
	{
		System.out.println("Warning!!! DOMImplementation's 'hasFeature' that should be 'true' failed!");
		OK = false;
	}
	
	result = implementation.hasFeature("HTML", "4.0");
	if(result)
	{
		System.out.println("Warning!!! DOMImplementation's 'hasFeature' that should be 'false' failed!");
		OK = false;
	}
	
	
// For debugging*****		println("All DOMImplementation method calls worked correctly.");
	if (!OK)
		System.out.println("\n*****The DOMImplementation method calls listed above failed, all others worked correctly.*****");
//	println("");
}
/**
 * This method tests Element methods for the XML DOM implementation
 * version 2.0 10/12/98
 * @param document org.w3c.dom.Document
 *
 * @author Philip W. Davis
 */
public void testElement(org.w3c.dom.Document document)
{
	Attr attributeNode, newAttributeNode;
	Element element, element2;
	Node node, node2;
	String attribute, compare;
	String[] attributeCompare = {"AnotherFirstElementAttribute", "dFirstElement", "testAttribute"};
	String[] elementNames =  {"dFirstElement", "dTestBody", "dBodyLevel21","dBodyLevel31","dBodyLevel32",
				   "dBodyLevel22","dBodyLevel33","dBodyLevel34","dBodyLevel23","dBodyLevel24"};
	String[] textCompare = {"dBodyLevel31'sChildTextNode11", "dBodyLevel31'sChildTextNode12", "dBodyLevel31'sChildTextNode13"};
	NamedNodeMap nodeMap;
	boolean OK = true;
// For debugging*****	println("\n          testElement's outputs:\n");
	node = document.getDocumentElement(); // node gets doc's firstElement
	node2 = node.cloneNode(true);
	// Check nodes for equality, both their name and value or lack thereof
	if (!(node.getNodeName().equals(node2.getNodeName()) &&		    // Compares node names for equality
	     (node.getNodeValue() != null && node2.getNodeValue() != null)  // Checks to make sure each node has a value node
	    ? node.getNodeValue().equals(node2.getNodeValue())  	    // If both have value nodes test those value nodes for equality
	    :(node.getNodeValue() == null && node2.getNodeValue() == null)))// If one node doesn't have a value node make sure both don't
	{	
		System.out.println("'cloneNode' did not clone the Element node correctly");
		OK = false;
	}
	// Deep clone test comparison is in testNode & testDocument

	element = document.getDocumentElement(); // element gets doc's firstElement
	compare = "";
	attribute = element.getAttribute(document + "'s test attribute");
	if (! compare.equals(element.getAttribute(document + "'s test attribute")))
	{
		System.out.println("Warning!!! Element's 'getAttribute' failed!");
		OK = false;
	}
	
	attributeNode = element.getAttributeNode(document + "FirstElement");
	if(! (attributeNode == null))
	{
		System.out.println("Warning!!! Element's 'getAttributeNode' failed! It should have returned 'null' here!");
		OK = false;
	}
	
	newAttributeNode = document.createAttribute("AnotherFirstElementAttribute");
	newAttributeNode.setValue("A new attribute which helps test calls in Element");
	element.setAttributeNode(newAttributeNode);
	nodeMap = element.getAttributes();
	int size = nodeMap.getLength();
	int k;
	for (k = 0; k < size; k++)
	{
		Node n = (Node) nodeMap.item(k);
		if (! (attributeCompare[k].equals(n.getNodeName())))
		{
			System.out.println("Warning!!! Comparison of firstElement's attributes failed at attribute #"+ (k+1) +" " + n.getNodeValue());
			System.out.println("This failure can be a result of Element's 'setValue' and/or 'setAttributeNode' and/or 'getAttributes' failing.");
			OK = false;
			break;
		}
	//	println("firstElement's attribute number " + k + " : " + n.getNodeName());
	}
	NodeList docElements = document.getElementsByTagName("*");
	int docSize = docElements.getLength();
	int i;
	for (i = 0; i < docSize; i++)
	{
		Node n = (Node) docElements.item(i);
		if (! (elementNames[i].equals(n.getNodeName())))
		{
			System.out.println("Warning!!! Comparison of Element's 'getElementsByTagName' and/or 'item' failed at element number " 
						+ i + " : " + n.getNodeName());
			OK = false;
			break;
		}		
	//	println("docElement's number " + i + " is: " + n.getNodeName());
	}
	element = (Element) document.getElementsByTagName("dBodyLevel21").item(0); // element gets Element test BodyLevel21 
	element2 = (Element) document.getElementsByTagName("dBodyLevel31").item(0); // element2 gets Element test BodyLevel31 
	NodeList text = ((Node) element2).getChildNodes();
	int textSize = text.getLength();
	int j;
	for (j = 0; j < textSize; j++)
	{
		Node n = (Node) text.item(j);
		if (! (textCompare[j].equals(n.getNodeValue())))
		{
			System.out.println("Warning!!! Comparison of original text nodes via Node 'getChildNodes' & NodeList 'item'"
						+ "failed at text node: #" + j +" " + n.getNodeValue());
			OK = false;
			break;
		}
	//	println("Element testBodyLevel31's child text node " + j + " is: " + n.getNodeValue());
	}
	element = document.getDocumentElement(); // element gets doc's firstElement
	element.normalize();		// Concatenates all adjacent text nodes in this element's subtree
	NodeList text2 = ((Node) element2).getChildNodes();
	compare = "dBodyLevel31'sChildTextNode11dBodyLevel31'sChildTextNode12dBodyLevel31'sChildTextNode13";
	Node n = (Node) text2.item(0);
		if (! (compare.equals(n.getNodeValue())))
		{
			System.out.println("Warning!!! Comparison of concatenated text nodes created by Element's 'normalize' failed!");
			OK = false;
		}
	
	element.setAttribute("FirstElementLastAttribute", "More attribute stuff for firstElement!!");
	element.removeAttribute("FirstElementLastAttribute");
	element.removeAttributeNode(newAttributeNode);

	//	doc.getLastChild().setNodeValue("This shouldn't work");//!! Throws a NO_MODIFICATION_ALLOWED_ERR***
	
// For debugging*****		println("All Element method calls worked correctly.");
	if (!OK)
		System.out.println("\n*****The Element method calls listed above failed, all others worked correctly.*****");
//	println("");
}
/**
 * This method tests Entity methods for the XML DOM implementation
 * version 2.0 10/12/98
 * @param document org.w3c.dom.Document
 *
 * @author Philip W. Davis
 */
public void testEntity(org.w3c.dom.Document document)
{
	Entity entity;
	Node node, node2;
	boolean OK = true;
	String compare;
// For debugging*****	println("\n          testEntity's outputs:\n");
	entity = (Entity) document.getDoctype().getEntities().getNamedItem("ourEntityNode");
	node = entity;
	node2 = entity.cloneNode(true);
	// Check nodes for equality, both their name and value or lack thereof
	if (!(node.getNodeName().equals(node2.getNodeName()) && 		// Compares node names for equality
	     (node.getNodeValue() != null && node2.getNodeValue() != null) ?    // Checks to make sure each node has a value node
	      node.getNodeValue().equals(node2.getNodeValue()) :		// If both have value nodes test those value nodes for equality
	     (node.getNodeValue() == null && node2.getNodeValue() == null)))	// If one node doesn't have a value node make sure both don't
	{	
		System.out.println("Warning!!! 'cloneNode' did not clone the Entity node correctly");
		OK = false;
	}
	// Deep clone test comparison is in testNode & testDocument

 	((org.apache.xerces.dom.EntityImpl) entity).setNotationName("testNotationName");
	compare = "testNotationName";
 	if(! compare.equals(entity.getNotationName()))
	{
		System.out.println("Warning!!! Entity's 'setNotationName' and/or getNotationName' failed!");
		OK = false;
	}
 	((org.apache.xerces.dom.EntityImpl) entity).setPublicId("testPublicId");
	compare = "testPublicId";
 	if(! compare.equals(entity.getPublicId()))
	{
		System.out.println("Warning!!! Entity's 'setPublicId' and/or getPublicId' failed!");
		OK = false;
	}	
 	((org.apache.xerces.dom.EntityImpl) entity).setSystemId("testSystemId");
	compare = "testSystemId";
 	if(! compare.equals(entity.getSystemId()))
	{
		System.out.println("Warning!!! Entity's 'setSystemId' and/or getSystemId' failed!");
		OK = false;
	}		
	//	entity.setNodeValue("This shouldn't work");//!! Throws a NO_MODIFICATION_ALLOWED_ERR ********
	
// For debugging*****		println("All Entity method calls worked correctly.");
	if (!OK)
		System.out.println("\n*****The Entity method calls listed above failed, all others worked correctly.*****");
//	println("");
}
/**
 * This method tests EntityReference methods for the XML DOM implementation
 * version 2.0 10/12/98
 * @param document org.w3c.dom.Document
 *
 * @author Philip W. Davis
 */
public void testEntityReference(org.w3c.dom.Document document)
{
	EntityReference entityReference;
	Node node, node2;
	boolean OK = true;
// For debugging*****	println("\n          testEntityReference's outputs:\n");
	entityReference = (EntityReference) document.getLastChild().getLastChild().getLastChild().getFirstChild();
	node = entityReference;
	node2 = node.cloneNode(true);
	// Check nodes for equality, both their name and value or lack thereof
	if (!(node.getNodeName().equals(node2.getNodeName()) && 	    // Compares node names for equality
	     (node.getNodeValue() != null && node2.getNodeValue() != null)  // Checks to make sure each node has a value node
	    ? node.getNodeValue().equals(node2.getNodeValue()) 		    // If both have value nodes test those value nodes for equality
	    :(node.getNodeValue() == null && node2.getNodeValue() == null)))// If one node doesn't have a value node make sure both don't
	{	
		System.out.println("'cloneNode' did not clone the EntityReference node correctly");
		OK = false;
	}
	// Deep clone test comparison is in testNode & testDocument

	//	entityReference.setNodeValue("This shouldn't work");//!! Throws a NO_MODIFICATION_ALLOWED_ERR ********
	
// For debugging*****		println("All EntityReference method calls worked correctly.");
	if (!OK)
		System.out.println("\n*****The EntityReference method calls listed above failed, all others worked correctly.*****");
//	println("");
}
/**
 * This method tests Node methods for the XML DOM implementation
 * version 2.0 10/12/98
 * @param document org.w3c.dom.Document
 *
 * @author Philip W. Davis
 *
 *
 ********* This is only for a test of cloneNode "deep"*******
 ********* And for error tests*********
 */
public void testNode(org.w3c.dom.Document document)
{
	Node node, node2;
	boolean result;
	boolean OK = true;
// For debugging*****	println("\n          testNode's outputs:\n");
	node = document.getDocumentElement();
	node2 = node.cloneNode(true);
	result = treeCompare(node, node2); // Deep clone test of cloneNode
	if (result)
	{
		//println("'cloneNode' successfully cloned this whole node tree (deep)!");
	}
	else
	{
		System.out.println("'cloneNode' did not successfully clone this whole node tree (deep)!");
		OK = false;	
	}
	//!! The following gives a did not clone successfully message*********
	node = document.getDocumentElement();
	node2 = node.getFirstChild();
	result = treeCompare(node, node2);
	if (!result)
	{
		//println("'cloneNode' did not successfully clone this whole node tree (deep)!");
	}
	else
	{
		System.out.println("'cloneNode' was supposed to fail here, either it or 'treeCompare' failed!!!");
		OK = false;
	}
	// Deep clone test also in testDocument
	
// For debugging*****		println("All Node method calls worked correctly.");
	if (!OK)
		System.out.println("\n*****The Node method calls listed above failed, all others worked correctly.*****");	
//	println("");
}
/**
 * This method tests Notation methods for the XML DOM implementation
 * version 2.0 10/12/98
 * @param document org.w3c.dom.Document
 *
 * @author Philip W. Davis
 */
public void testNotation(org.w3c.dom.Document document)
{
	Node node, node2;
	Notation notation;
	boolean OK = true;
	String compare;
// For debugging*****	println("\n          testNotation's outputs:\n");
	notation = (Notation) document.getDoctype().getNotations().getNamedItem("ourNotationNode");
	node = notation;
	node2 = notation.cloneNode(true);//*****?
	// Check nodes for equality, both their name and value or lack thereof
	if (!(node.getNodeName().equals(node2.getNodeName()) && 	    // Compares node names for equality
	     (node.getNodeValue() != null && node2.getNodeValue() != null)  // Checks to make sure each node has a value node
	    ? node.getNodeValue().equals(node2.getNodeValue()) 		    // If both have value nodes test those value nodes for equality
	    :(node.getNodeValue() == null && node2.getNodeValue() == null)))// If one node doesn't have a value node make sure both don't
	{	
		System.out.println("'cloneNode' did not clone the Notation node correctly");
		OK = false;
	}
	// Deep clone test comparison is in testNode & testDocument

 	((org.apache.xerces.dom.NotationImpl) notation).setPublicId("testPublicId");//*****?
	compare = "testPublicId";
	if (!compare.equals(notation.getPublicId()))
	{
		System.out.println("Warning!!! Notation's 'getPublicId' failed!");
		OK = false;
	}
 	((org.apache.xerces.dom.NotationImpl) notation).setSystemId("testSystemId");//*****?
	compare = "testSystemId";
	if (! compare.equals(notation.getSystemId()))
	{
		System.out.println("Warning!!! Notation's 'getSystemId' failed!");
		OK = false;
	}
	//	notation.setNodeValue("This shouldn't work");//!! Throws a NO_MODIFICATION_ALLOWED_ERR ********
	
// For debugging*****		println("All Notation method calls worked correctly.");
	if (!OK)
		System.out.println("\n*****The Notation method calls listed above failed, all others worked correctly.*****");
//	println("");
}
/**
 * This method tests ProcessingInstruction methods for the XML DOM implementation
 * version 2.0 10/12/98
 * @param document org.w3c.dom.Document
 *
 * @author Philip W. Davis
 */
public void testPI(org.w3c.dom.Document document)
{
	Node node, node2;
	ProcessingInstruction pI, pI2;
	String compare;
	boolean OK = true;
// For debugging*****	println("\n          testPI's outputs:\n");
	pI = (ProcessingInstruction) document.getDocumentElement().getFirstChild();// Get doc's ProcessingInstruction
	pI2 = (org.apache.xerces.dom.ProcessingInstructionImpl) pI.cloneNode(true);//*****?
	// Check nodes for equality, both their name and value or lack thereof
	if (!(pI.getNodeName().equals(pI2.getNodeName()) && 		// Compares node names for equality
	     (pI.getNodeValue() != null && pI2.getNodeValue() != null)  // Checks to make sure each node has a value node
	    ? pI.getNodeValue().equals(pI2.getNodeValue()) 		// If both have value nodes test those value nodes for equality
	    :(pI.getNodeValue() == null && pI2.getNodeValue() == null)))// If one node doesn't have a value node make sure both don't
	{	
		System.out.println("'cloneNode' did not clone the Entity node correctly");
		OK = false;
	}
	// Deep clone test comparison is in testNode & testDocument
	compare = "This is [#document: null]'s processing instruction";
	if (! compare.equals(pI.getData()))
	{
		System.out.println("Warning!!! PI's 'getData' failed!");
		OK = false;
	}
	
	pI.setData("PI's reset data");
	compare = "PI's reset data";
	if (! compare.equals(pI.getData()))
	{
		System.out.println("Warning!!! PI's 'setData' failed!");
		OK = false;
	}	
	compare = "dTargetProcessorChannel";
	if (! compare.equals(pI.getTarget()))
	{
		System.out.println("Warning!!! PI's 'getTarget' failed!");
		OK = false;
	}	
	
// For debugging*****		println("All PI method calls worked correctly.");
	if (!OK)
		System.out.println("\n*****The PI method calls listed above failed, all others worked correctly.*****");
	
//	println("");
}
/**
 * This method tests Text methods for the XML DOM implementation
 * version 2.0 10/12/98
 * @param document org.w3c.dom.Document
 *
 * @author Philip W. Davis
 */
public void testText(org.w3c.dom.Document document)
{
	Node node, node2;
	Text text;
	String compare;
	boolean OK = true;
// For debugging*****	println("\n          testText's outputs:\n");
	node = document.getDocumentElement().getElementsByTagName("dBodyLevel31").item(0).getFirstChild(); // charData gets textNode11
	text = (Text) node;
	node2 = node.cloneNode(true);//*****?
	// Check nodes for equality, both their name and value or lack thereof
	if (!(node.getNodeName().equals(node2.getNodeName()) && 	    // Compares node names for equality
	     (node.getNodeValue() != null && node2.getNodeValue() != null)  // Checks to make sure each node has a value node
	    ? node.getNodeValue().equals(node2.getNodeValue()) 		    // If both have value nodes test those value nodes for equality
	    :(node.getNodeValue() == null && node2.getNodeValue() == null)))// If one node doesn't have a value node make sure both don't
	{	
		System.out.println("'cloneNode' did not clone the Text node correctly");
		OK = false;
	}
	// Deep clone test comparison is in testNode & testDocument
	text.splitText(25);
	compare = "dBodyLevel31'sChildTextNo";	// Three original text nodes were concatenated by 'normalize' in testElement
	if (! compare.equals(text.getNodeValue()))
		{
			System.out.println("First part of Text's split text failed!" );
			OK = false;
		}
	compare = "de11dBodyLevel31'sChildTextNode12dBodyLevel31'sChildTextNode13";// Three original text nodes were concatenated by 'normalize' in testElement
	if (! compare.equals(text.getNextSibling().getNodeValue()))
		{
			System.out.println("The second part of Text's split text failed!") ;
			OK = false;	
		}




//************************************************* ERROR TESTS
	DTest tests = new DTest();		
	//!! Throws INDEX_SIZE_ERR ********************
	//	text.splitText(-1);
	//	text.splitText(100);
	
// For debugging*****		println("All Text method calls worked correctly.");
	if (!OK)
		System.out.println("\n*****The Text method calls listed above failed, all others worked correctly.*****");
	
//	println("");
}
/**
 * 
 * @param node org.w3c.dom.Node
 * @param node2 org.w3c.dom.Node
 *
 * @author Philip W. Davis
 */
public boolean treeCompare(Node node, Node node2)
{
	boolean answer = true;
		
	Node kid, kid2;			// Check the subtree for equality
	kid = node.getFirstChild();
	kid2 = node2.getFirstChild();
	if (kid != null && kid2 != null)
	{
		answer = treeCompare(kid, kid2);
		if (!answer)
			return answer;
		else
			if (kid.getNextSibling() != null && kid2.getNextSibling() != null)
			{
				while (kid.getNextSibling() != null && kid2.getNextSibling() != null)
				{
					answer = treeCompare(kid.getNextSibling(), kid2.getNextSibling());
					if (!answer)
						return answer;
					else
					{
						kid = kid.getNextSibling();
						kid2 = kid2.getNextSibling();
					}
				}
			} else
				if (!(kid.getNextSibling() == null && kid2.getNextSibling() == null))
				{
					return false;
				}
	} else
		if (kid != kid2)
		{
			return false;
		}

	// Check nodes for equality, both their name and value or lack thereof
	if (!(node.getNodeName().equals(node2.getNodeName()) &&		    // Compares node names for equality
	     (node.getNodeValue() != null && node2.getNodeValue() != null)  // Checks to make sure each node has a value node
	    ? node.getNodeValue().equals(node2.getNodeValue()) 		    // If both have value nodes test those value nodes for equality
	    :(node.getNodeValue() == null && node2.getNodeValue() == null)))// If one node doesn't have a value node make sure both don't
	{
		return false;	// Return false if "any" of the above conditions are false
	}
	return answer;
}
}
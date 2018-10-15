test("org/eclipse/xpand3/parser/node2ast/test.ttst");

package org.eclipse.xpand3.parser.node2ast;

import java.io.InputStream;
import java.util.List;

import junit.framework.TestCase;

import org.antlr.runtime.ANTLRStringStream;
import org.antlr.runtime.CommonTokenStream;
import org.antlr.runtime.RecognitionException;
import org.eclipse.emf.common.util.EList;
import org.eclipse.emf.ecore.EClass;
import org.eclipse.emf.ecore.EObject;
import org.eclipse.emf.ecore.EPackage;
import org.eclipse.emf.ecore.EStructuralFeature;
import org.eclipse.emf.ecore.resource.Resource;
import org.eclipse.emf.ecore.xmi.impl.XMIResourceFactoryImpl;
import org.eclipse.tmf.common.node.Node;
import org.eclipse.tmf.common.treetest.Body;
import org.eclipse.tmf.common.treetest.Expression;
import org.eclipse.tmf.common.treetest.NodeRef;
import org.eclipse.tmf.common.treetest.PropertyCheck;
import org.eclipse.tmf.common.treetest.PropertyList;
import org.eclipse.tmf.common.treetest.Test;
import org.eclipse.tmf.common.treetest.TestSpec;
import org.eclipse.tmf.common.treetest.TreetestPackage;
import org.eclipse.tmf.common.treetest.parser.XtextParser;
import org.eclipse.xpand3.SyntaxElement;
import org.eclipse.xpand3.parser.Xpand3NodeLexer;
import org.eclipse.xpand3.parser.Xpand3NodeParser;

public class TreetestInterpreterTest extends TestCase {

	@Override
	protected void setUp() throws Exception {
		ClassLoader classLoader = getClass().getClassLoader();
		Thread.currentThread().setContextClassLoader(classLoader);
		Resource.Factory.Registry.INSTANCE.getExtensionToFactoryMap().put(
				"ecore", new XMIResourceFactoryImpl());

		EPackage treePackage = TreetestPackage.eINSTANCE;
		EPackage.Registry.INSTANCE.put(treePackage.getNsURI(), treePackage);
	}

	public void testTree() throws RecognitionException {
		test("org/eclipse/xpand3/parser/node2ast/test.tree");
	}

	private void test(String testFileName) throws RecognitionException {
		ClassLoader classLoader = getClass().getClassLoader();
		InputStream testFile = classLoader.getResourceAsStream(testFileName);
		XtextParser treeSpecParser = new XtextParser(testFile);
		TestSpec testSpec = (TestSpec) treeSpecParser.getRootNode()
				.getModelElement();
		System.out.println("Loading test spec from " + testSpec.getName());
		EList<Test> tests = testSpec.getTest();
		for (Test test : tests) {
			System.out.println("Starting test " + test.getName());
			Expression testExpression = test.getExpr();
			SyntaxElement rootElement = parseAndTransform(testExpression);
			performTest(rootElement, test.getExpected());
		}

	}

	private SyntaxElement parseAndTransform(Expression testExpression)
			throws RecognitionException {
		String body = testExpression.getBody();
		body = body.substring(2, body.length() - 2);
		System.out.println("Expression:" + body);
		ANTLRStringStream stream = new ANTLRStringStream(body);
		Xpand3NodeLexer lexer = new Xpand3NodeLexer(stream);
		CommonTokenStream tokenStream = new CommonTokenStream(lexer);
		Xpand3NodeParser xpand3NodeParser = new Xpand3NodeParser(tokenStream);

		Node rootNode = xpand3NodeParser.r_file();
		if (rootNode == null) {
			System.out.println("Nothing parsed.");
		}
		Node2AstTransformer node2AstTransformer = new Node2AstTransformer();
		return node2AstTransformer.doSwitch(rootNode);
	}

	@SuppressWarnings("unchecked")
	protected void performTest(EObject object,
			org.eclipse.tmf.common.treetest.Node testRootNode) {
		EClass eClass = object.eClass();
		assertEquals(eClass.getName(), testRootNode.getClassName());
		PropertyList propertyList = testRootNode.getPropertyList();
		if (propertyList != null) {
			for (PropertyCheck propertyCheck : propertyList.getChecks()) {
				String name = propertyCheck.getName();
				EStructuralFeature attribute = eClass
						.getEStructuralFeature(name);
				String value = object.eGet(attribute).toString();
				assertEquals(propertyCheck.getValue(), value);
			}
		}
		Body body = testRootNode.getBody();
		if (body != null) {
			EList<NodeRef> nodeRefs = body.getChildren();
			for (int i = 0; i < nodeRefs.size(); ++i) {
				NodeRef nodeRef = nodeRefs.get(i);
				EStructuralFeature reference = eClass
						.getEStructuralFeature(nodeRefs.get(i).getRefName());
				Object value = object.eGet(reference);
				EList<org.eclipse.tmf.common.treetest.Node> refNodes = nodeRef
						.getNodes();
				if (reference.isMany()) {
					List listValue = (List) value;
					if (refNodes.isEmpty()) {
						assertTrue(listValue == null || listValue.isEmpty());
						return;
					}
					assertTrue(refNodes.size() <= listValue.size());
					for (int j = 0; j < refNodes.size(); ++j) {
						assertTrue(listValue.get(j) instanceof EObject);
						performTest((EObject) listValue.get(j), refNodes.get(j));
					}
				} else {
					if (refNodes.isEmpty()) {
						assertTrue(value == null);
						return;
					}
					assertTrue(refNodes.size() <= 1);
					org.eclipse.tmf.common.treetest.Node refNode = refNodes
							.get(0);
					assertTrue(value instanceof EObject);
					performTest((EObject) value, refNode);
				}
			}
		}
	}
}
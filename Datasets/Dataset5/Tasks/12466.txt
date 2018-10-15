String s = "foo.bar.honolulu('lola',{true,false,45}).collect(e|2.minor + 34 / (x - 2))";

package org.eclipse.xpand3.parser;

import junit.framework.TestCase;

import org.antlr.runtime.ANTLRStringStream;
import org.antlr.runtime.CommonTokenStream;
import org.eclipse.xpand3.node.Node;
import org.eclipse.xpand3.node.NodeUtil;
import static org.eclipse.xpand3.parser.SyntaxUtil.*;

public class Xpand3NodeParserTest extends TestCase {
	
	private Node parse(String s) throws Exception {
		Xpand3NodeParser parser = createParser(s);
		parser.r_file();
		return parser.getRootNode();
	}
	
	public void testname() throws Exception {
		Node x = parse(LG + "IMPORT foo" + RG
				+ "import foo; myFunction(String this) : doStuff('holla');"
				+ LG + "DEFINE foo FOR Entity" + RG + "bla" + LG + "ENDDEFINE"
				+ RG);
		System.out.println(NodeUtil.toString(x));
	}

	public void testFoo() throws Exception {
		Node node = parse("import foo; myFunction(String this) : doStuff('holla');");
		System.out.println(NodeUtil.toString(node));
		System.out.println(NodeUtil.serialize(node));
	}

	public void testXpandXtendCheckMixedUp1() throws Exception {
		Node node = parse(LG + "IMPORT foo" + RG
				+ "import foo; myFunction(String this) : doStuff('holla');"
				+ LG + "DEFINE foo FOR Entity" + RG + "bla" + LG + "ENDDEFINE"
				+ RG);
		System.out.println(NodeUtil.toString(node));
		System.out.println(NodeUtil.serialize(node));
	}
//	
	public void testPerf() throws Exception {
		String s = "foo.bar.honolulu('lola',[true,false,45]).collect(e|2.minor + 34 / (x - 2))";
		for (int i = 0; i<10;i++) {
			s = s+" -> "+s;
		}
		Xpand3Parser parser = createParser(s);
		long n = System.currentTimeMillis();
		parser.r_expression();
		long after = System.currentTimeMillis();
		System.out.println("Time : "+(after-n)/1000.+" Expressionlength was : "+s.length());
	}

	private Xpand3NodeParser createParser(String s) {
		ANTLRStringStream stream = new ANTLRStringStream(s);
		Xpand3Lexer lexer = new Xpand3Lexer(stream);
		CommonTokenStream tokenStream = new CommonTokenStream(lexer);
		Xpand3NodeParser parser = new Xpand3NodeParser(tokenStream);
		return parser;
	}
}
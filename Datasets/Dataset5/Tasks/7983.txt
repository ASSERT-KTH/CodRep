Node rootNode = xpand3NodeParser.r_file();

package org.eclipse.xpand3.parser.node2ast;

import java.io.StringReader;

import org.antlr.runtime.ANTLRStringStream;
import org.antlr.runtime.CommonTokenStream;
import org.antlr.runtime.RecognitionException;
import org.eclipse.tmf.common.node.Node;
import org.eclipse.xpand3.parser.Xpand3NodeLexer;
import org.eclipse.xpand3.parser.Xpand3NodeParser;
import org.openarchitectureware.xtend.parser.ParseFacade;

public class ParseStuff {
	private static boolean useNodeParser;

	/**
	 * @param args
	 * @throws RecognitionException
	 */
	public static void main(String[] args) throws RecognitionException {
		useNodeParser = false;
		checkFor(1);
		checkFor(10);
		checkFor(100);
		checkFor(1000);
		checkFor(5000);
		checkFor(50000);
		useNodeParser = true;
		checkFor(1);
		checkFor(10);
		checkFor(100);
		checkFor(1000);
		checkFor(5000);
		checkFor(50000);

	}

	public static void parseWithNodeParser(String s)
			throws RecognitionException {
		ANTLRStringStream stream = new ANTLRStringStream(s);
		Xpand3NodeLexer lexer = new Xpand3NodeLexer(stream);
		CommonTokenStream tokenStream = new CommonTokenStream(lexer);
		Xpand3NodeParser xpand3NodeParser = new Xpand3NodeParser(tokenStream);

		Node rootNode = xpand3NodeParser.file();
		// if (rootNode == null) {
		// System.out.println("Nothing parsed.");
		// } else {
		// System.out.println(NodeUtil.toString(rootNode));
		// }
		Node2AstTransformer node2AstTransformer = new Node2AstTransformer();
		node2AstTransformer.doSwitch(rootNode);
	}

	private static void checkFor(int extensions) throws RecognitionException {
		StringBuffer file = new StringBuffer();
		for (int i = 0; i < extensions; i++) {
			file
					.append("\nfoo")
					.append(i)
					.append(
							"(Object this, Object that) : this.toString() == that.toString();");
		}
		long before = System.currentTimeMillis();
		if (useNodeParser) {
			parseWithNodeParser(file.toString());
		} else {
			ParseFacade.file(new StringReader(file.toString()), "foo.xpt");
		}
		long after = System.currentTimeMillis();
		System.out.println("Time for " + extensions + " extensions: "
				+ (after - before));
	}

}
Node rootNode = xpand3NodeParser.r_file();

/*******************************************************************************
 * Copyright (c) 2005, 2007 committers of openArchitectureWare and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     committers of openArchitectureWare - initial API and implementation
 *******************************************************************************/

package org.eclipse.xpand3.parser;

import org.antlr.runtime.ANTLRStringStream;
import org.antlr.runtime.CommonTokenStream;
import org.eclipse.tmf.common.node.CompositeNode;
import org.eclipse.tmf.common.node.Node;
import org.eclipse.tmf.common.node.NodeUtil;

/**
 * @author Jan Khnlein
 */
public class StatementParserTest extends AbstractXpand3NodeParserTest {
	private CompositeNode parse(String s) throws Exception {
		System.out.println(s);
		ANTLRStringStream stream = new ANTLRStringStream(s);
		Xpand3NodeLexer lexer = new Xpand3NodeLexer(stream);
		CommonTokenStream tokenStream = new CommonTokenStream(lexer);
		Xpand3NodeParser xpand3NodeParser = new Xpand3NodeParser(tokenStream);

		Node rootNode = xpand3NodeParser.file();
		if (rootNode == null) {
			System.out.println("Nothing parsed.");
		} else {
			System.out.println(NodeUtil.toString(rootNode));
		}
		return (CompositeNode) rootNode;
	}

	public final void testEmptyTemplate() throws Exception {
		Node expr = parse("");
		assertNull(expr);
	}

	public final void testSimpleDefine() throws Exception {
		Node expr = parse(tag("DEFINE test FOR ecore::EClass")
				+ tag("ENDDEFINE"));
		checkIsRule(expr, "definition", 8);
		checkChildIsToken(expr, 0, LGS);
		checkChildIsToken(expr, 1, "DEFINE");
		checkChildIsIdentifier(expr, 2, "test");
		checkChildIsToken(expr, 3, "FOR");
		checkChildIsScopedType(expr, 4, "ecore", "EClass");
		checkChildIsSequenceText(expr, 5, "", 1);
		checkChildIsToken(expr, 6, "ENDDEFINE");
		checkChildIsToken(expr, 7, RGS);

	}

	public final void testDoubleDefine() throws Exception {
		Node file = parse(tag("DEFINE test FOR ecore::EClass")
				+ tag("ENDDEFINE")
				+ tag("DEFINE test2(String txt) FOR ecore::EClass")
				+ tag("ENDDEFINE"));
		checkIsRule(file, "file", 2);
		CompositeNode expr = checkChildIsRule(file, 0, "definition", 8);
		checkChildIsToken(expr, 0, LGS);
		checkChildIsToken(expr, 1, "DEFINE");
		checkChildIsIdentifier(expr, 2, "test");
		checkChildIsToken(expr, 3, "FOR");
		checkChildIsScopedType(expr, 4, "ecore", "EClass");
		checkChildIsSequenceText(expr, 5, "", 1);
		checkChildIsToken(expr, 6, "ENDDEFINE");
		checkChildIsToken(expr, 7, RGS);

		CompositeNode expr1 = checkChildIsRule(file, 1, "definition", 11);
		checkChildIsToken(expr1, 0, LGS);
		checkChildIsToken(expr1, 1, "DEFINE");
		checkChildIsIdentifier(expr1, 2, "test2");
		checkChildIsToken(expr1, 3, "(");
		CompositeNode dpl = checkChildIsRule(expr1, 4, "declaredParameterList",
				1);
		CompositeNode dp = checkChildIsRule(dpl, 0, "declaredParameter", 2);
		checkChildIsSimpleType(dp, 0, "String");
		checkChildIsIdentifier(dp, 1, "txt");
		checkChildIsToken(expr1, 5, ")");
		checkChildIsToken(expr1, 6, "FOR");
		checkChildIsScopedType(expr1, 7, "ecore", "EClass");
		checkChildIsSequenceText(expr1, 8, "", 1);
		checkChildIsToken(expr1, 9, "ENDDEFINE");
		checkChildIsToken(expr1, 10, RGS);

	}

	public final void testMoreComplexDefine() throws Exception {
		Node expr = parse(tag("DEFINE test(ecore::EPackage a,String b) FOR ecore::EClass")
				+ tag("FILE name+\".txt\"")
				+ "Text und so "
				+ tag("name")
				+ tag("FOREACH eAllAttributes AS attr")
				+ "Attribute : "
				+ tag("attr.name")
				+ tag("ENDFOREACH")
				+ tag("ENDFILE")
				+ tag("ENDDEFINE"));
		checkIsRule(expr, "definition", 11);
		checkChildIsToken(expr, 0, LGS);
		checkChildIsToken(expr, 1, "DEFINE");
		checkChildIsIdentifier(expr, 2, "test");
		checkChildIsToken(expr, 3, "(");
		CompositeNode dpl = checkChildIsRule(expr, 4, "declaredParameterList",
				3);
		CompositeNode dp0 = checkChildIsRule(dpl, 0, "declaredParameter", 2);
		checkChildIsScopedType(dp0, 0, "ecore", "EPackage");
		checkChildIsIdentifier(dp0, 1, "a");
		checkChildIsToken(dpl, 1, ",");
		CompositeNode dp = checkChildIsRule(dpl, 2, "declaredParameter", 2);
		checkChildIsSimpleType(dp, 0, "String");
		checkChildIsIdentifier(dp, 1, "b");
		checkChildIsToken(expr, 5, ")");
		checkChildIsToken(expr, 6, "FOR");
		checkChildIsScopedType(expr, 7, "ecore", "EClass");
		CompositeNode rs = checkChildIsSequenceText(expr, 8, "", 3);
		CompositeNode fs = checkChildIsRule(rs, 1, "fileStatement", 4);
		checkChildIsToken(fs, 0, "FILE");
		CompositeNode ae = checkChildIsRule(fs, 1, "additiveExpression", 3);
		checkChildIsSimpleType(ae, 0, "name");
		checkChildIsToken(ae, 1, "+");
		checkChildIsStringLiteral(ae, 2, "\".txt\"");
		CompositeNode s0 = checkChildIsSequenceText(fs, 2, "Text und so ", 5);
		CompositeNode es = checkChildIsRule(s0, 1, "expressionStmt", 1);
		checkChildIsSimpleType(es, 0, "name");
		checkChildIsText(s0, 2, "");
		CompositeNode fes = checkChildIsRule(s0, 3, "foreachStatement", 6);
		checkChildIsToken(fes, 0, "FOREACH");
		checkChildIsSimpleType(fes, 1, "eAllAttributes");
		checkChildIsToken(fes, 2, "AS");
		checkChildIsIdentifier(fes, 3, "attr");
		CompositeNode s1 = checkChildIsSequenceText(fes, 4, "Attribute : ", 3);
		CompositeNode es1 = checkChildIsRule(s1, 1, "expressionStmt", 1);
		CompositeNode ie = checkChildIsRule(es1, 0, "infixExpression", 3);
		checkChildIsSimpleType(ie, 0, "attr");
		checkChildIsToken(ie, 1, ".");
		checkChildIsSimpleType(ie, 2, "name");
		checkChildIsText(s1, 2, "");
		checkChildIsToken(fes, 5, "ENDFOREACH");
		checkChildIsText(s0, 4, "");
		checkChildIsToken(fs, 3, "ENDFILE");
		checkChildIsText(rs, 2, "");
		checkChildIsToken(expr, 9, "ENDDEFINE");
		checkChildIsToken(expr, 10, RGS);
	}

	public final void testImportDeclaration() throws Exception {
		Node expr = parse(tag("IMPORT org::eclipse::xtend")
				+ tag("IMPORT org::eclipse::xtend::xpand")
				+ tag("DEFINE test FOR ecore::EClass") + tag("ENDDEFINE"));
		checkIsRule(expr, "file", 3);
		CompositeNode i0 = checkChildIsRule(expr, 0, "nsImport", 4);
		checkChildIsToken(i0, 0, LGS);
		checkChildIsToken(i0, 1, "IMPORT");
		checkChildIsScopedType(i0, 2, "org", "eclipse", "xtend");
		checkChildIsToken(i0, 3, RGS);

		CompositeNode i1 = checkChildIsRule(expr, 1, "nsImport", 4);
		checkChildIsToken(i1, 0, LGS);
		checkChildIsToken(i1, 1, "IMPORT");
		checkChildIsScopedType(i1, 2, "org", "eclipse", "xtend", "xpand");
		checkChildIsToken(i1, 3, RGS);

		CompositeNode d = checkChildIsRule(expr, 2, "definition", 8);
		checkChildIsToken(d, 0, LGS);
		checkChildIsToken(d, 1, "DEFINE");
		checkChildIsIdentifier(d, 2, "test");
		checkChildIsToken(d, 6, "ENDDEFINE");
		checkChildIsToken(d, 7, RGS);
	}

	public final void testFileStatement() throws Exception {
		Node expr = parse(tag("DEFINE test FOR ecore::EClass")
				+ tag("FILE \"test.txt\" ONCE") + tag("ENDFILE")
				+ tag("ENDDEFINE"));
		checkIsRule(expr, "definition", 8);
		checkChildIsToken(expr, 0, LGS);
		checkChildIsToken(expr, 1, "DEFINE");
		checkChildIsIdentifier(expr, 2, "test");
		checkChildIsToken(expr, 3, "FOR");
		checkChildIsScopedType(expr, 4, "ecore", "EClass");
		CompositeNode s = checkChildIsSequenceText(expr, 5, "", 3);
		CompositeNode fs = checkChildIsRule(s, 1, "fileStatement", 5);
		checkChildIsToken(fs, 0, "FILE");
		checkChildIsStringLiteral(fs, 1, "\"test.txt\"");
		checkChildIsIdentifier(fs, 2, "ONCE");
		checkChildIsSequenceText(fs, 3, "", 1);
		checkChildIsToken(fs, 4, "ENDFILE");
		checkChildIsText(s, 2, "");
		checkChildIsToken(expr, 6, "ENDDEFINE");
		checkChildIsToken(expr, 7, RGS);
	}

	public final void testIfStatement() throws Exception {
		Node expr = parse(tag("DEFINE test FOR ecore::EClass")
				+ tag("IF !true") + tag("ELSEIF false") + tag("ELSE")
				+ tag("ENDIF") + tag("ENDDEFINE"));
		checkIsRule(expr, "definition", 8);
		checkChildIsToken(expr, 0, LGS);
		checkChildIsToken(expr, 1, "DEFINE");
		checkChildIsIdentifier(expr, 2, "test");
		checkChildIsToken(expr, 3, "FOR");
		checkChildIsScopedType(expr, 4, "ecore", "EClass");
		CompositeNode s = checkChildIsSequenceText(expr, 5, "", 3);
		CompositeNode is = checkChildIsRule(s, 1, "ifStatement", 6);
		checkChildIsToken(is, 0, "IF");
		CompositeNode ue = checkChildIsRule(is, 1, "unaryExpression", 2);
		checkChildIsToken(ue, 0, "!");
		checkChildIsTrueLiteral(ue, 1);
		checkChildIsSequenceText(is, 2, "", 1);
		CompositeNode eis = checkChildIsRule(is, 3, "elseIfStatement", 3);
		checkChildIsToken(eis, 0, "ELSEIF");
		checkChildIsFalseLiteral(eis, 1);
		checkChildIsSequenceText(eis, 2, "", 1);
		CompositeNode es = checkChildIsRule(is, 4, "elseStatement", 2);
		checkChildIsToken(es, 0, "ELSE");
		checkChildIsSequenceText(es, 1, "", 1);
		checkChildIsText(s, 2, "");
		checkChildIsToken(expr, 6, "ENDDEFINE");
		checkChildIsToken(expr, 7, RGS);
	}

	public void testLocation() throws Exception {
		String defineStart = tag("DEFINE test FOR ecore::EClass");
		String ifStmnt = tag("IF !true") + tag("ELSEIF false") + tag("ELSE")
				+ tag("ENDIF");
		String string = defineStart + ifStmnt + tag("ENDDEFINE");
		CompositeNode expr = parse(string);
		assertEquals(0, expr.start());
		assertEquals(string.length(), expr.end());

		assertEquals(1, expr.getChildren().get(1).start());
		assertEquals(string.length() - 1, expr.getChildren().get(6).end());

		assertEquals(defineStart.length() - 1, expr.getChildren().get(5)
				.start());
		assertEquals(defineStart.length() + ifStmnt.length() + 1, expr
				.getChildren().get(5).end());
	}
}
 No newline at end of file
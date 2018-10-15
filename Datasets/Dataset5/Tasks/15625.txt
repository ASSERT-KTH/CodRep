int language = LanguageUtil.getLanguageLevel(file.getProject());

/*******************************************************************************
 * Copyright (c) 2008, 2009 28msec Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     Gabriel Petrovay (28msec) - initial API and implementation
 *******************************************************************************/
package org.eclipse.wst.xquery.internal.core.parser;

import org.antlr.runtime.ANTLRStringStream;
import org.antlr.runtime.RecognitionException;
import org.antlr.runtime.tree.CommonTree;
import org.eclipse.core.resources.IFile;
import org.eclipse.core.resources.ResourcesPlugin;
import org.eclipse.core.runtime.Path;
import org.eclipse.dltk.ast.declarations.ModuleDeclaration;
import org.eclipse.dltk.ast.parser.AbstractSourceParser;
import org.eclipse.dltk.compiler.problem.DefaultProblem;
import org.eclipse.dltk.compiler.problem.IProblem;
import org.eclipse.dltk.compiler.problem.IProblemReporter;
import org.eclipse.wst.xquery.core.XQDTCorePlugin;
import org.eclipse.wst.xquery.core.model.ast.XQueryLibraryModule;
import org.eclipse.wst.xquery.core.model.ast.XQueryMainModule;
import org.eclipse.wst.xquery.internal.core.parser.antlr.NewLazyTokenStream;
import org.eclipse.wst.xquery.internal.core.parser.antlr.XQDTCommonTree;
import org.eclipse.wst.xquery.internal.core.parser.antlr.XQDTCommonTreeAdaptor;
import org.eclipse.wst.xquery.internal.core.parser.antlr.XQueryLexer;
import org.eclipse.wst.xquery.internal.core.parser.antlr.XQueryParser;
import org.eclipse.wst.xquery.internal.core.parser.visitors.XQDTCommonTreeVisitor;
import org.eclipse.wst.xquery.internal.core.utils.LanguageUtil;

public class XQDTSourceParser extends AbstractSourceParser {

    private XQueryParser fParser;

    protected XQDTCommonTreeVisitor getASTBuilderVisitor(char[] content, IProblemReporter reporter) {
        return new XQDTCommonTreeVisitor(content, reporter);
    }

    public ModuleDeclaration parse(char[] fileName, char[] source, IProblemReporter reporter) {
        if (fileName == null || source == null) {
            return null;
        }

        ModuleDeclaration moduleDeclaration = null;
        String file = new String(fileName);

        if (XQDTCorePlugin.DEBUG_PARSER_ACTIONS) {
            XQDTCorePlugin.trace("Starting parsing file: " + file);
        }

        XQueryParser parser = prepareParser(file, source, reporter);

        if (XQDTCorePlugin.DEBUG_PARSER_ACTIONS) {
            XQDTCorePlugin.trace("Parser prepared for file: " + file);
        }

        try {
            XQueryParser.p_Module_return m = parser.p_Module();
            if (XQDTCorePlugin.DEBUG_PARSER_ACTIONS) {
                XQDTCorePlugin.trace("Parsing complete for file: " + file);
            }

            XQDTCommonTree tree = (XQDTCommonTree)m.getTree();
            if (XQDTCorePlugin.DEBUG_PARSER_RESULTS) {
                XQDTCorePlugin.trace("Parse tree for file: " + file + "\n\t" + tree.toStringTree());
            }

            XQDTCommonTreeVisitor visitor = getASTBuilderVisitor(source, reporter);
            tree.accept(visitor);
            if (XQDTCorePlugin.DEBUG_PARSER_RESULTS) {
                XQDTCorePlugin.trace("AST built for file: " + file);
            }

            if (XQDTCorePlugin.DEBUG_PARSER_RESULTS) {
                XQDTCorePlugin.trace("Pretty print parse tree for file: " + file + "\n" + printTree(tree, 0));
            }

            moduleDeclaration = visitor.getModule();
            if (moduleDeclaration instanceof XQueryLibraryModule) {
                XQueryLibraryModule module = (XQueryLibraryModule)moduleDeclaration;
                module.setKeywordPositions(parser.getKeywords());
            } else if (moduleDeclaration instanceof XQueryMainModule) {
                ((XQueryMainModule)moduleDeclaration).setKeywordPositions(parser.getKeywords());
            }

        } catch (ArrayIndexOutOfBoundsException aioobe) {
            aioobe.printStackTrace();
            reportProblem(reporter, "Error (index)");
        } catch (RecognitionException e) {
            // e.printStackTrace();
            reportProblem(reporter, "Error (recognition)");
        } catch (ClassCastException cce) {
            cce.printStackTrace();
            reportProblem(reporter, "Error (cast)");
        }

        return moduleDeclaration;
    }

    // public boolean isLibraryModule(char[] fileName, char[] source, IProblemReporter reporter) {
    // if (fileName == null)
    // return false;
    //  
    // XQueryParser parser = prepareParser(fileName, source, reporter);
    //
    // try {
    // XQueryParser.p_ModuleDecl_return md = parser.p_ModuleDecl();
    // System.out.println("parsed ModuleDecl first: " +
    // ((XQDTCommonTree)md.getTree()).toStringTree());
    //
    // parser.reset();
    //          
    // XQueryParser.p_Module_return m = parser.p_Module();
    // } catch (Exception e) {
    // // TODO: handle exception
    // }
    // }

    protected XQueryParser prepareParser(String fileName, char[] source, IProblemReporter reporter) {
        if (fParser != null) {
            return fParser;
        }

        ANTLRStringStream inputStream = new ANTLRStringStream(source, source.length);
        XQueryLexer lexer = new XQueryLexer(inputStream);
        NewLazyTokenStream tokenStream = new NewLazyTokenStream(lexer);
        tokenStream.jumpToFirstValidToken();
        XQueryParser parser = new XQueryParser(tokenStream);
        parser.setCharSource(inputStream);
        parser.setTreeAdaptor(new XQDTCommonTreeAdaptor(reporter));
        parser.setProblemReporter(reporter);
        parser.setFileName(fileName);

        IFile file = ResourcesPlugin.getWorkspace().getRoot().getFile(new Path(fileName));
        int language = LanguageUtil.getLanguageLevel(file, source);
        if (XQDTCorePlugin.DEBUG) {
            System.out.println("prepareParser (" + language + "):" + new String(fileName));
        }
        parser.setLanguageLevel(language);
        return parser;
    }

    private void reportProblem(IProblemReporter reporter, String message) {
        reporter.reportProblem(new DefaultProblem(message, 1, new String[0], IProblem.Syntax, 0, 1, 1));
    }

    private static String printTree(CommonTree tree, int i) {
        StringBuffer sb = new StringBuffer();
        for (Object oc : tree.getChildren()) {
            CommonTree child = (CommonTree)oc;
            if (child.token != null && child.token.getType() != XQueryLexer.EOF) {
                sb.append(getIndent(i) + child.token.getText() + "\n");
            } else {
                sb.append("---------EOF---------\n");
            }

            if (child.getChildren() != null) {
                sb.append(printTree(child, i + 1));
            }
        }

        return sb.toString();
    }

    private static String getIndent(int count) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < count; i++) {
            sb.append("\t");
        }
        return sb.toString();
    }

}
 No newline at end of file
execCtx.getResourceManager().setFileEncoding("ISO-8859-1");

/*******************************************************************************
 * Copyright (c) 2005, 2009 committers of openArchitectureWare and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     committers of openArchitectureWare - initial API and implementation
 *******************************************************************************/

package org.eclipse.xpand.internal.tests.analyze;

import junit.framework.TestCase;

import org.eclipse.internal.xtend.expression.parser.SyntaxConstants;
import org.eclipse.xpand.internal.tests.evaluate.OutputStringImpl;
import org.eclipse.xpand.internal.tests.evaluate.StatementEvaluatorTest;
import org.eclipse.xpand2.XpandExecutionContextImpl;
import org.eclipse.xpand2.XpandFacade;
import org.eclipse.xtend.expression.AnalysationIssue;
import org.eclipse.xtend.type.impl.java.JavaMetaModel;
import org.eclipse.xtend.type.impl.java.beans.JavaBeansStrategy;

/**
 * *
 * 
 * @author Sven Efftinge (http://www.efftinge.de) *
 */
public class StatementAnalyzationTest extends TestCase {

    private XpandExecutionContextImpl execCtx;

    @Override
    protected void setUp() throws Exception {
        super.setUp();
        execCtx = new XpandExecutionContextImpl(new OutputStringImpl(), null);
        execCtx.registerMetaModel(new JavaMetaModel("JavaBeans", new JavaBeansStrategy()));

        // ADDED encoding
        execCtx.setFileEncoding("ISO-8859-1");
    }

    public final void testAnalyzation() {
        final String id = StatementEvaluatorTest.class.getPackage().getName().replaceAll("\\.",
                SyntaxConstants.NS_DELIM)
                + SyntaxConstants.NS_DELIM + "EvaluateStart";
        final AnalysationIssue[] issues = XpandFacade.create(execCtx).analyze(id);
        dumpIssues(issues);
        assertTrue(issues.length == 0);
    }

    private void dumpIssues(final AnalysationIssue[] issues) {
        for (int i = 0; i < issues.length; i++) {
            final AnalysationIssue issue = issues[i];
            System.out
                    .println(issue.getType() + " : " + issue.getMessage() + " on line " + issue.getElement() != null ? issue
                            .getElement().getLine()
                            + ""
                            : "");
        }

    }
}
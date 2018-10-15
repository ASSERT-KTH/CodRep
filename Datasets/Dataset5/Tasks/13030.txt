public final void analyze(final XpandExecutionContext ctx, final Set<AnalysationIssue> issues) {

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

package org.eclipse.internal.xpand2.ast;

import java.util.Set;

import org.eclipse.emf.mwe.core.monitor.ProgressMonitor;
import org.eclipse.internal.xtend.expression.ast.SyntaxElement;
import org.eclipse.xpand2.XpandExecutionContext;
import org.eclipse.xtend.expression.AnalysationIssue;

public abstract class Statement extends SyntaxElement implements XpandAnalyzable, XpandEvaluatable {

	protected AbstractDefinition containingDefinition;

	public Statement() {
	}

	public final void evaluate(final XpandExecutionContext ctx) {
		try {
			ProgressMonitor monitor = ctx.getMonitor();
			if (monitor != null && monitor.isCanceled())
				return;

			if (ctx.getCallback() != null) {
				ctx.getCallback().pre(this, ctx);
			}
			ctx.getOutput().pushStatement(this, ctx);
			ctx.preTask(this);
			evaluateInternal(ctx);
			ctx.postTask(this);
			ctx.getOutput().popStatement();
		}
		catch (final RuntimeException exc) {
			ctx.handleRuntimeException(exc, this, null);
		}
		finally {
			if (ctx.getCallback() != null) {
				ctx.getCallback().post(null);
			}
		}
	}

	public void analyze(final XpandExecutionContext ctx, final Set<AnalysationIssue> issues) {
		try {
			if (ctx.getCallback() != null) {
				ctx.getCallback().pre(this, ctx);
			}
			analyzeInternal(ctx, issues);
		}
		catch (final RuntimeException ex) {
			final String message = ex.getMessage();
			if (message != null) {
				issues.add(new AnalysationIssue(AnalysationIssue.INTERNAL_ERROR, ex.getMessage(), this));
			}
			else
				throw ex;
		}
		finally {
			if (ctx.getCallback() != null) {
				ctx.getCallback().post(null);
			}
		}
	}

	protected abstract void evaluateInternal(XpandExecutionContext ctx);

	protected abstract void analyzeInternal(XpandExecutionContext ctx, final Set<AnalysationIssue> issues);

	public AbstractDefinition getContainingDefinition() {
		return containingDefinition;
	}

	public void setContainingDefinition(final AbstractDefinition definition) {
		this.containingDefinition = definition;
	}

}
public static XpandFacade create(XpandExecutionContext execCtx) {

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

package org.eclipse.xpand2;

import java.util.HashSet;
import java.util.Set;

import org.eclipse.internal.xpand2.model.XpandDefinition;
import org.eclipse.internal.xpand2.model.XpandResource;
import org.eclipse.xtend.expression.AnalysationIssue;
import org.eclipse.xtend.expression.EvaluationException;
import org.eclipse.xtend.expression.ExecutionContext;
import org.eclipse.xtend.expression.Variable;
import org.eclipse.xtend.typesystem.Type;

/**
 * *
 * 
 * @author Sven Efftinge (http://www.efftinge.de) *
 */
public class XpandFacade {
	private XpandExecutionContext ctx = null;

	/**
	 * @deprecated use XpandFacade.create instead
	 */
	@Deprecated
	public XpandFacade(final XpandExecutionContext ctx) {
		this.ctx = ctx;
	}

	public void evaluate(final String definitionName, final Object targetObject, Object... params) {
		params = params == null ? new Object[0] : params;
		final Type targetType = ctx.getType(targetObject);
		final Type[] paramTypes = new Type[params.length];
		for (int i = 0; i < paramTypes.length; i++) {
			paramTypes[i] = ctx.getType(params[i]);
		}

		final XpandDefinition def = ctx.findDefinition(definitionName, targetType, paramTypes);
		if (def == null)
			throw new EvaluationException("No Definition " + definitionName + getParamString(paramTypes) + " for "
					+ targetType.getName() + " could be found!", null, ctx);

		ctx = (XpandExecutionContext) ctx.cloneWithVariable(new Variable(ExecutionContext.IMPLICIT_VARIABLE,
				targetObject));
		for (int i = 0; i < params.length; i++) {
			final Variable v = new Variable(def.getParams()[i].getName().getValue(), params[i]);
			ctx = (XpandExecutionContext) ctx.cloneWithVariable(v);
		}
		ctx = (XpandExecutionContext) ctx.cloneWithResource(def.getOwner());
		def.evaluate(ctx);
	}

	private String getParamString(final Type[] paramTypes) {
		if (paramTypes.length == 0)
			return "";
		final StringBuffer buff = new StringBuffer("(");
		for (int i = 0; i < paramTypes.length; i++) {
			final Type t = paramTypes[i];
			buff.append(t.getName());
			if (i + 1 < paramTypes.length) {
				buff.append(",");
			}
		}
		buff.append(")");
		return buff.toString();
	}

	public AnalysationIssue[] analyze(final String templateName) {
		final Set<AnalysationIssue> issues = new HashSet<AnalysationIssue>();
		final XpandResource tpl = ctx.findTemplate(templateName);
		tpl.analyze(ctx, issues);
		return issues.toArray(new AnalysationIssue[issues.size()]);
	}

	public static XpandFacade create(XpandExecutionContextImpl execCtx) {
		return new XpandFacade(execCtx);
	}
}
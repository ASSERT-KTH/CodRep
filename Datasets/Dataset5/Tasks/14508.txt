if (!(o instanceof Collection<?>))

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

package org.eclipse.internal.xpand2.ast;

import java.util.ArrayList;
import java.util.Collection;
import java.util.Iterator;
import java.util.Set;

import org.eclipse.internal.xpand2.type.IteratorType;
import org.eclipse.internal.xpand2.type.XpandIterator;
import org.eclipse.internal.xtend.expression.ast.Expression;
import org.eclipse.internal.xtend.expression.ast.Identifier;
import org.eclipse.xpand2.XpandExecutionContext;
import org.eclipse.xtend.expression.AnalysationIssue;
import org.eclipse.xtend.expression.EvaluationException;
import org.eclipse.xtend.expression.ExecutionContext;
import org.eclipse.xtend.expression.Variable;
import org.eclipse.xtend.typesystem.ParameterizedType;
import org.eclipse.xtend.typesystem.Type;

/**
 * *
 * 
 * @author Sven Efftinge (http://www.efftinge.de) *
 */
public class ForEachStatement extends StatementWithBody {

	private Expression target;

	private Expression separator;

	private Identifier variable;

	private Identifier iteratorName;

	public ForEachStatement(final Identifier variable, final Expression target,
			final Statement[] body, final Expression separator, final Identifier iterator) {
		super(body);
		this.variable = variable;
		this.target = target;
		this.separator = separator;
		iteratorName = iterator;
	}

	public Expression getSeparator() {
		return separator;
	}

	public Expression getTarget() {
		return target;
	}

	public Identifier getVariable() {
		return variable;
	}

	public Identifier getIteratorName() {
		return iteratorName;
	}

	@Override
	public void analyzeInternal(XpandExecutionContext ctx, final Set<AnalysationIssue> issues) {
		Type t = getTarget().analyze(ctx, issues);
		if (getSeparator() != null) {
			final Type sepT = getSeparator().analyze(ctx, issues);
			if (!ctx.getStringType().isAssignableFrom(sepT)) {
				issues.add(new AnalysationIssue(AnalysationIssue.INCOMPATIBLE_TYPES, "String expected!", target));
			}
		}
		if (t != null) {
			if (ctx.getCollectionType(ctx.getObjectType()).isAssignableFrom(t)) {
				if (t instanceof ParameterizedType) {
					t = ((ParameterizedType) t).getInnerType();
				} else {
					t = ctx.getObjectType();
				}
			} else {
				issues.add(new AnalysationIssue(AnalysationIssue.INCOMPATIBLE_TYPES, "Collection type expected!", target));
				return;
			}
		}
		ctx = (XpandExecutionContext) ctx.cloneWithVariable(new Variable(getVariable().getValue(), t));
		if (iteratorName != null) {
			ctx = (XpandExecutionContext) ctx.cloneWithVariable(new Variable(iteratorName.getValue(), ctx.getTypeForName(IteratorType.TYPE_NAME)));
		}
		for (int i = 0; i < getBody().length; i++) {
			getBody()[i].analyze(ctx, issues);
		}
	}

	@Override
	public void evaluateInternal(XpandExecutionContext ctx) {
		Object o = getTarget().evaluate(ctx);
		if (o == null)
			o = new ArrayList<Object>();

		if (!(o instanceof Collection))
			throw new EvaluationException("Collection expected!", getTarget(), ctx);
		final Collection<?> col = (Collection<?>) o;
		final String sep = (String) (getSeparator() != null ? getSeparator().evaluate(ctx) : null);
		final XpandIterator iterator = new XpandIterator(col.size());

		if (iteratorName != null) {
			ctx = (XpandExecutionContext) ctx.cloneWithVariable(new Variable(iteratorName.getValue(), iterator));
		}
		for (final Iterator<?> iter = col.iterator(); iter.hasNext();) {
			final Object element = iter.next();
			ctx = (XpandExecutionContext) ctx.cloneWithVariable(new Variable(getVariable().getValue(), element));
			ctx.preTask(this);
			for (int i = 0; i < getBody().length; i++) {
				getBody()[i].evaluate(ctx);
			}
			ctx.postTask(this);
			if (sep != null && iter.hasNext()) {
				ctx.getOutput().write(sep);
			}
			iterator.increment();
		}
	}

	@Override
	public String getNameString(ExecutionContext context) {
		return "FOREACH";
	}


}
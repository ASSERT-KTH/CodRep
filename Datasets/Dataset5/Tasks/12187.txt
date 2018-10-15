if (targetObj != null ) /* f and obj can only be null here */

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

package org.eclipse.internal.xtend.expression.ast;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Set;

import org.eclipse.internal.xtend.util.ProfileCollector;
import org.eclipse.internal.xtend.xtend.ast.Extension;
import org.eclipse.xtend.expression.AnalysationIssue;
import org.eclipse.xtend.expression.EvaluationException;
import org.eclipse.xtend.expression.ExecutionContext;
import org.eclipse.xtend.expression.Variable;
import org.eclipse.xtend.typesystem.Operation;
import org.eclipse.xtend.typesystem.ParameterizedType;
import org.eclipse.xtend.typesystem.Type;

/**
 * @author Sven Efftinge (http://www.efftinge.de)
 * @author Arno Haase
 * @author Bernd Kolb
 */
public class OperationCall extends FeatureCall {

	private Expression[] params;

	public OperationCall(final Identifier name, final Expression target, final Expression... params) {
		super(name, target);
		this.params = params;
	}

	public Expression[] getParams() {
		return params;
	}

	public List<Expression> getParamsAsList() {
		return Arrays.asList(params);
	}

	@Override
	public Object evaluateInternal(final ExecutionContext ctx) {
		// evaluate from left to right
		// first the target
		Object targetObj = null;
		if (getTarget()!=null) {
			targetObj = getTarget().evaluate(ctx);
		}
		// then the parameters in the defined order
		final Object[] evaluatedParams = new Object[getParams().length];
		if (getParams().length > 0) {
			for (int i = 0; i < getParams().length; i++) {
				evaluatedParams[i] = getParams()[i].evaluate(ctx);
			}
		}
		
		if (getTarget() == null) {
			// extension
			final Extension f = ctx.getExtension(getName().getValue(), evaluatedParams);
			if (f != null) {
				ProfileCollector.getInstance().enter(f.toString());
				try {
					return evaluate(f, evaluatedParams, ctx);
				} catch (EvaluationException e) {
					e.addStackElement(this, ctx);
					throw e;
				} finally {
					ProfileCollector.getInstance().leave();
				}
			}

			// implicit
			final Variable var = ctx.getVariable(ExecutionContext.IMPLICIT_VARIABLE);
			if (var == null)
				throw new EvaluationException("Couldn't find extension '" + getName().getValue() + getParamTypes(evaluatedParams, ctx) + "'!", this, ctx);
			targetObj = var.getValue();
		} 
		
		// operation
		Operation op = ctx.findOperation(getName().getValue(), targetObj, evaluatedParams);
		if (op != null)
			return evaluate(op, targetObj, evaluatedParams, ctx);
		// extension as members
		Object[] ps = new Object[evaluatedParams.length + 1];
		ps[0] = targetObj;
		System.arraycopy(evaluatedParams, 0, ps, 1, evaluatedParams.length);
		Extension f = ctx.getExtension(getName().getValue(), ps);
		if (f != null) {
			try {
				ProfileCollector.getInstance().enter(f.toString());
				return evaluate(f, ps, ctx);
			} catch (EvaluationException e) {
				e.addStackElement(this, ctx);
				throw e;
			} finally {
				ProfileCollector.getInstance().leave();
			}
		}

		if (targetObj instanceof Collection<?>) {
			final List<Object> result = new ArrayList<Object>();
			final Collection<?> col = (Collection<?>) targetObj;
			for (final Iterator<?> iter = col.iterator(); iter.hasNext();) {
				final Object element = iter.next();
				// operation
				op = ctx.findOperation(getName().getValue(), element, evaluatedParams);
				if (op != null) {
					final Object r = evaluate(op, element, evaluatedParams, ctx);
					if (r instanceof Collection<?>) {
						result.addAll((Collection<?>) r);
					} else {
						result.add(r);
					}
				} else {
					// extension as members
					ps = new Object[evaluatedParams.length + 1];
					ps[0] = element;
					System.arraycopy(evaluatedParams, 0, ps, 1, evaluatedParams.length);
					f = ctx.getExtension(getName().getValue(), ps);
					if (f != null) {
						Object r = null;
						try {
							r = evaluate(f, ps, ctx);
						} catch (EvaluationException e) {
							e.addStackElement(this, ctx);
							throw e;
						}
						if (r instanceof Collection<?>) {
							result.addAll((Collection<?>) r);
						} else {
							result.add(r);
						}
					} else
						throw new EvaluationException("Couldn't find operation '" + getName().getValue() + getParamTypes(evaluatedParams, ctx) + "' for "
								+ ctx.getType(targetObj).getName() + "!", this, ctx);
				}
			}
			return result;
		}

		if (targetObj != null && f == null && op == null)
			throw new EvaluationException("Couldn't find operation '" + getName().getValue() + getParamTypes(evaluatedParams, ctx) + "' for "
					+ ctx.getType(targetObj).getName() + ".", this, ctx);
		return ctx.handleNullEvaluation(this);

	}

	private String getParamTypes(final Object[] params2, final ExecutionContext ctx) {
		final StringBuffer buff = new StringBuffer("(");
		for (int i = 0; i < params2.length; i++) {
			final Type type = ctx.getType(params2[i]);
			buff.append(type.getName());
			if (i + 1 < params2.length) {
				buff.append(",");
			}
		}
		return buff.append(")").toString();
	}

	@Override
	public Type analyzeInternal(final ExecutionContext ctx, final Set<AnalysationIssue> issues) {
		final Type[] paramTypes = new Type[getParams().length];
		if (getParams().length > 0) {
			for (int i = 0; i < getParams().length; i++) {
				paramTypes[i] = getParams()[i].analyze(ctx, issues);
				if (paramTypes[i] == null)
					return null;
			}
		}

		// extension
		Type targetType = null;
		if (getTarget() == null) {
			Extension f = null;
			try {
				f = ctx.getExtensionForTypes(getName().getValue(), paramTypes);
			} catch (final Exception e) {
				issues.add(new AnalysationIssue(AnalysationIssue.INTERNAL_ERROR, "Error parsing extensions : " + e.getMessage(), this));
			}
			if (f != null)
				return ctx.getReturnType(f, paramTypes, issues);
			final Variable var = ctx.getVariable(ExecutionContext.IMPLICIT_VARIABLE);
			if (var != null) {
				targetType = (Type) var.getValue();
			} else {
				issues.add(new AnalysationIssue(AnalysationIssue.FEATURE_NOT_FOUND, "Couldn't find extensions : " + toString(), this));
			}
		} else {
			targetType = getTarget().analyze(ctx, issues);
		}
		if (targetType == null)
			return null;
		// operation
		Operation op = targetType.getOperation(getName().getValue(), paramTypes);
		if (op != null)
			return op.getReturnType(targetType, paramTypes);
		// extension as members
		final int issueSize = issues.size();
		Type rt = getExtensionsReturnType(ctx, issues, paramTypes, targetType);
		if (rt != null)
			return rt;
		else if (issueSize < issues.size())
			return null;
		String additionalMsg = "";
		if (targetType instanceof ParameterizedType) {
			final Type innerType = ((ParameterizedType) targetType).getInnerType();
			op = innerType.getOperation(getName().getValue(), paramTypes);
			if (op != null) {
				rt = op.getReturnType();
				if (rt instanceof ParameterizedType) {
					rt = ((ParameterizedType) rt).getInnerType();
				}
				return ctx.getListType(rt);
			}
			rt = getExtensionsReturnType(ctx, issues, paramTypes, innerType);
			if (rt != null) {
				if (rt instanceof ParameterizedType) {
					rt = ((ParameterizedType) rt).getInnerType();
				}
				return ctx.getListType(rt);
			}
			additionalMsg = " or type '" + innerType + "'";
		}

		issues.add(new AnalysationIssue(AnalysationIssue.FEATURE_NOT_FOUND, "Couldn't find operation '" + getName().getValue()
				+ getParamsString(paramTypes) + "' for type '" + targetType.getName() + "'" + additionalMsg, this));
		return null;

	}

	private Type getExtensionsReturnType(final ExecutionContext ctx, final Set<AnalysationIssue> issues, final Type[] paramTypes,
			final Type targetType) {
		final Type[] pts = new Type[paramTypes.length + 1];
		pts[0] = targetType;
		System.arraycopy(paramTypes, 0, pts, 1, paramTypes.length);
		Extension f = null;
		try {
			f = ctx.getExtensionForTypes(getName().getValue(), pts);
		} catch (final Exception e) {
			issues.add(new AnalysationIssue(AnalysationIssue.INTERNAL_ERROR, "Error parsing extensions : " + e.getMessage(), this));
		}
		if (f != null) {
			final Set<AnalysationIssue> temp = new HashSet<AnalysationIssue>();
			final Type rt = ctx.getReturnType(f, pts, temp);
			if (rt == null) {
				issues.add(new AnalysationIssue(AnalysationIssue.INTERNAL_ERROR, "couldn't resolve return type for extension " + f + "! Errors : "
						+ temp.toString(), this));
			}
			return rt;
		} else if (getTarget() == null) { // try without implicite this
			try {
				f = ctx.getExtensionForTypes(getName().getValue(), paramTypes);
			} catch (final Exception e) {
				issues.add(new AnalysationIssue(AnalysationIssue.INTERNAL_ERROR, "Error parsing extensions : " + e.getMessage(), this));
			}
			if (f != null) {
				final Set<AnalysationIssue> temp = new HashSet<AnalysationIssue>();
				final Type rt = ctx.getReturnType(f, pts, temp);
				if (rt == null) {
					issues.add(new AnalysationIssue(AnalysationIssue.INTERNAL_ERROR, "couldn't resolve return type for extension " + f
							+ "! Errors : " + temp.toString(), this));
				}
				return rt;
			}
		}
		return null;
	}

	private String getParamsString(final Type[] paramTypes) {
		final StringBuffer buff = new StringBuffer("(");
		for (int i = 0; i < paramTypes.length; i++) {
			final Type type = paramTypes[i];
			buff.append(type.getName());
			if (i + 1 < paramTypes.length) {
				buff.append(",");
			}
		}
		return buff.append(")").toString();
	}

	@Override
	protected String toStringInternal() {
		return (getTarget() != null ? getTarget().toStringInternal() + "." : "") + getName() + getParamsExpressionString(getParams());
	}

	@Override
	public String getNameString(ExecutionContext context) {
		final StringBuffer buff = new StringBuffer();
		buff.append(getName().getValue());
		buff.append("(");
		if (params.length > 0)
			if (context != null)
				buff.append(getParamTypesString(context));
			else
				// TODO: CK low: Get parameter types from OawModelManager for Breakpoints
				buff.append("..");
		return buff.append(")").toString();
	}

	private String getParamTypesString(ExecutionContext context) {
		final ExecutionContext ctx = context.cloneWithoutMonitor();
		final StringBuffer buff = new StringBuffer();
		for (int i = 0; i < getParams().length; i++) {
			Type type = ctx.getType(params[i].evaluate(ctx));
			String name = type.getName();
			int pos = name.lastIndexOf("::");
			if (pos < 0)
				buff.append(name);
			else
				buff.append(name.substring(pos + 2));
			if (i + 1 < params.length)
				buff.append(",");
		}
		return buff.toString();
	}

	private String getParamsExpressionString(final Expression[] params2) {
		final StringBuffer buff = new StringBuffer("(");
		for (int i = 0; i < params2.length; i++) {
			buff.append(params2[i]);
			if (i + 1 < params2.length) {
				buff.append(",");
			}
		}
		return buff.append(")").toString();
	}

	private Object evaluate(Extension ext, Object[] params, ExecutionContext ctx) {
		ctx.preTask(this);
		Object result = ext.evaluate(params, ctx);
		ctx.postTask(this);
		return result;
	}

	private Object evaluate(Operation op, Object targetObj, Object[] params, ExecutionContext ctx) {
		ctx.preTask(this);
		Object result = op.evaluate(targetObj, params);
		ctx.postTask(this);
		return result;
	}
}
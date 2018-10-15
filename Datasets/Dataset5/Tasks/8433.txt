_stringRepresentation = getName() + getParamString(false)

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

import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.eclipse.internal.xpand2.model.XpandAdvice;
import org.eclipse.internal.xpand2.model.XpandDefinition;
import org.eclipse.internal.xpand2.type.DefinitionType;
import org.eclipse.internal.xtend.expression.ast.DeclaredParameter;
import org.eclipse.internal.xtend.expression.ast.Identifier;
import org.eclipse.xpand2.XpandExecutionContext;
import org.eclipse.xtend.expression.AnalysationIssue;
import org.eclipse.xtend.expression.ExecutionContext;
import org.eclipse.xtend.expression.Variable;
import org.eclipse.xtend.typesystem.Type;

/**
 * @author Sven Efftinge (http://www.efftinge.de) *
 */
public class Advice extends AbstractDefinition implements XpandAdvice {

	public final static String DEF_VAR_NAME = "targetDef";

	public Advice(final Identifier pointCut, final Identifier type, final DeclaredParameter[] params, final boolean wildParams, final Statement[] body) {
		super(pointCut, type, params, body);
		this.wildParams = wildParams;
	}

	public Identifier getPointCut() {
		return getDefName();
	}

	@Override
	public void analyze(XpandExecutionContext ctx, final Set<AnalysationIssue> issues) {
		ctx = (XpandExecutionContext) ctx.cloneWithVariable(new Variable(DEF_VAR_NAME, ctx.getTypeForName(DefinitionType.TYPE_NAME)));
		super.analyze(ctx, issues);
	}

	private Pattern p = null;

	public boolean isWildcardParams () {
	    return wildParams;
	}
	
	public boolean matches(final XpandDefinition def, XpandExecutionContext ctx) {
		if (p == null) {
			p = Pattern.compile(getName().replaceAll("\\*", ".*"));
		}
		final Matcher m = p.matcher(def.getQualifiedName());
		if (m.matches()) {
			ctx = (XpandExecutionContext) ctx.cloneWithResource(def.getOwner());
			final Type t = ctx.getTypeForName(def.getTargetType());
			final Type[] paramTypes = new Type[def.getParams().length];
			for (int i = 0; i < paramTypes.length; i++) {
				paramTypes[i] = ctx.getTypeForName(def.getParams()[i].getType().getValue());
			}
			if (getParams().length == paramTypes.length || (wildParams && getParams().length <= paramTypes.length)) {

				ctx = (XpandExecutionContext) ctx.cloneWithResource(def.getOwner());
				final Type at = ctx.getTypeForName(getTargetType());
				if (at.isAssignableFrom(t)) {
					for (int i = 0; i < getParams().length; i++) {
						final Type pt = ctx.getTypeForName(getParams()[i].getType().getValue());
						if (!pt.isAssignableFrom(paramTypes[i]))
							return false;
					}
					return true;
				}
			}
		}
		return false;
	}

	@Override
	public String getNameString(ExecutionContext context) {
		return "AROUND";
	}

	@Override
	public String toString() {
		if (_stringRepresentation == null) {
			_stringRepresentation = getOwner().getFullyQualifiedName() + ": " + getName() + getParamString(false)
					+ " : " + getType().getValue();
		}

		return _stringRepresentation;
	}

}
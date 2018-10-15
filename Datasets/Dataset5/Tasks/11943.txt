throw new EvaluationException(ite.getCause(), this, ctx);

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

package org.eclipse.internal.xtend.xtend.ast;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Set;

import org.eclipse.emf.mwe.core.resources.ResourceLoaderFactory;
import org.eclipse.internal.xtend.expression.ast.DeclaredParameter;
import org.eclipse.internal.xtend.expression.ast.Identifier;
import org.eclipse.xtend.expression.AnalysationIssue;
import org.eclipse.xtend.expression.EvaluationException;
import org.eclipse.xtend.expression.ExecutionContext;
import org.eclipse.xtend.expression.IExecutionContextAware;
import org.eclipse.xtend.typesystem.Type;

/**
 * @author Sven Efftinge (http://www.efftinge.de)
 * @author Arno Haase
 * @author Heiko Behrens
 */
public class JavaExtensionStatement extends AbstractExtension {

    protected Identifier javaType;

    protected Identifier javaMethod;

    protected List<Identifier> javaParamTypes;
    
    private Method method = null;

    public JavaExtensionStatement(final Identifier name,
            final List<DeclaredParameter> formalParameters, final Identifier returnType, final Identifier javaType,
            final Identifier javaMethod, final List<Identifier> javaParamTypes, final boolean cached, final boolean isPrivate) {
        super(name, returnType, formalParameters, cached, isPrivate);
        this.javaType = javaType;
        this.javaMethod = javaMethod;
        this.javaParamTypes = javaParamTypes;
    }

    public Identifier getJavaType() {
        return javaType;
    }
    
    public String getJavaMethodName () {
        return javaMethod.getValue();
    }

    @Override
    public Object evaluateInternal(final Object[] parameters, final ExecutionContext ctx) {
        final HashSet<AnalysationIssue> issues = new HashSet<AnalysationIssue>();
        try {
            final Method method = getJavaMethod(ctx, issues);
            if (method == null) {
                final StringBuilder b = new StringBuilder();
                for (final Iterator<AnalysationIssue> iter = issues.iterator(); iter.hasNext();) {
                    final AnalysationIssue element = iter.next();
                    b.append(element.toString()).append("\n");
                }
                throw new EvaluationException(javaMethodToString() + " not found, problems were: \n" + b, this, ctx);
            }
            convertTypesToMethodSignature(ctx, method, parameters);
            if (Modifier.isStatic(method.getModifiers())) {
                return method.invoke(null, parameters);
            } else {
            	Object instance = method.getDeclaringClass().newInstance();
            	if (IExecutionContextAware.class.isAssignableFrom(method.getDeclaringClass())) {
            		((IExecutionContextAware)instance).setExecutionContext(ctx);
            	}
            	return method.invoke(instance, parameters);
            }
        } catch (final InvocationTargetException ite) {
            throw new RuntimeException(ite.getCause());
        } catch (final Exception e) {
            throw new EvaluationException(e, this, ctx);
        }
    }

	private void convertTypesToMethodSignature(ExecutionContext ctx, Method method, Object[] parameters) {
		Class<?>[] paramTypes = method.getParameterTypes();
		for(int i = 0; i < parameters.length; i++) {
			Object param = parameters[i];
			parameters[i] = ctx.getType(param).convert(param, paramTypes[i]);
		}
	}

	private String javaMethodToString() {
        final StringBuffer buff = new StringBuffer();
        for (final Iterator<Identifier> iter = javaParamTypes.iterator(); iter.hasNext();) {
            buff.append(iter.next());
            if (iter.hasNext()) {
                buff.append(",");
            }
        }

        return javaType + "." + javaMethod + "(" + buff + ")";
    }

	public Method getJavaMethod(final ExecutionContext ctx, final Set<AnalysationIssue> issues) {
		if (method != null) {
			return method;
			}
		try {
            Class<?> clazz = null;
            clazz = ResourceLoaderFactory.createResourceLoader().loadClass(javaType.getValue());
            if (clazz == null) {
                issues.add(new AnalysationIssue(AnalysationIssue.TYPE_NOT_FOUND, "Couldn't find Java type "+javaType.getValue(), javaType));
                return null;
            }
            final Class<?>[] paramTypes = new Class[javaParamTypes.size()];
            for (int i = 0, x = javaParamTypes.size(); i < x; i++) {
                final Identifier javaParamType = javaParamTypes.get(i);

                paramTypes[i] = ResourceLoaderFactory.createResourceLoader().loadClass(javaParamType.getValue());
                if (paramTypes[i] == null) {
                    issues.add(new AnalysationIssue(AnalysationIssue.TYPE_NOT_FOUND, javaParamType.getValue(), javaParamType));
                    return null;
                }
            }
            final Method m = clazz.getMethod(javaMethod.getValue(), paramTypes);

            if (!Modifier.isPublic(m.getModifiers())) {
                issues.add(new AnalysationIssue(AnalysationIssue.FEATURE_NOT_FOUND, javaMethod.getValue() + " must be public!", javaMethod));
            }
            method = m;
        } catch (final NoSuchMethodException e) {
            issues.add(new AnalysationIssue(AnalysationIssue.FEATURE_NOT_FOUND, javaMethod.getValue(), javaMethod));
        }
        return method;
    }

    @Override
    public void analyzeInternal(final ExecutionContext ctx, final Set<AnalysationIssue> issues) {
        if (returnType == null) {
            issues.add(new AnalysationIssue(AnalysationIssue.SYNTAX_ERROR, "A return type must be specified for java extensions!", this));
        }
        getJavaMethod(ctx, issues);
    }

    @Override
    protected Type internalGetReturnType(final Type[] parameters, final ExecutionContext ctx, final Set<AnalysationIssue> issues) {
        if (returnType == null) {
            issues.add(new AnalysationIssue(AnalysationIssue.SYNTAX_ERROR, "A return type must be specified for java extensions!", this));
            return null;
        } else
            return ctx.getTypeForName(returnType.getValue());
    }

}
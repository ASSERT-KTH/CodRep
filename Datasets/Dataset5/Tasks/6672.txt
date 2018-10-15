.compile("context\\s+([\\[\\]:\\w\\]]+)(#|\\s+)[^;]*\\z");

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

package org.eclipse.internal.xtend.check.codeassist;

import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Set;
import java.util.Stack;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.eclipse.internal.xtend.expression.codeassist.LazyVar;
import org.eclipse.internal.xtend.xtend.codeassist.FastAnalyzer;
import org.eclipse.internal.xtend.xtend.codeassist.Partition;
import org.eclipse.xtend.expression.AnalysationIssue;
import org.eclipse.xtend.expression.ExecutionContext;
import org.eclipse.xtend.expression.ExpressionFacade;
import org.eclipse.xtend.expression.Resource;
import org.eclipse.xtend.expression.Variable;
import org.eclipse.xtend.typesystem.ParameterizedType;
import org.eclipse.xtend.typesystem.Type;

public class CheckFastAnalyzer {

    private final static Pattern VALIDATE_PATTERN = Pattern
            .compile("context\\s+([\\[\\]:\\w\\]]+)\\s+[^;]*\\z");

    private final static Pattern TYPEDECL_PATTERN = Pattern.compile("context\\s+[\\[\\]:\\w\\]]*\\z");

    private CheckFastAnalyzer() {
    }

    protected static boolean isTypeDeclaration(final String s) {
        final Matcher m = TYPEDECL_PATTERN.matcher(s);
        return m.find();
    }

    public final static Stack<Set<LazyVar>> computeStack(final String toAnalyze) {
        final Matcher m = VALIDATE_PATTERN.matcher(toAnalyze);
        final Stack<Set<LazyVar>> stack = new Stack<Set<LazyVar>>();
        if (!m.find())
            return stack;
        final Set<LazyVar> vars = new HashSet<LazyVar>();
        stack.push(vars);
        final LazyVar v = new LazyVar();
        v.typeName = m.group(1);
        v.name = ExecutionContext.IMPLICIT_VARIABLE;
        vars.add(v);
        return stack;
    }

    public final static Partition computePartition(final String str) {
        if (FastAnalyzer.isInsideImport(str))
            return Partition.NAMESPACE_IMPORT;

        if (FastAnalyzer.isInsideExtensionImport(str))
            return Partition.EXTENSION_IMPORT;

        if (isTypeDeclaration(str))
            return Partition.TYPE_DECLARATION;

        final Stack<Set<LazyVar>> s = computeStack(str);
        if (!s.isEmpty())
            return Partition.EXPRESSION;

        return Partition.DEFAULT;
    }

    public final static ExecutionContext computeExecutionContext(final String str, ExecutionContext ctx) {
        final Partition p = computePartition(str);
        if (p == Partition.EXPRESSION || p == Partition.TYPE_DECLARATION) {

            final List<String> imports = FastAnalyzer.findImports(str);
            final List<String> extensionImports = FastAnalyzer.findExtensions(str);
            final Resource res = new Resource() {

                private String fqn;

                public String getFullyQualifiedName() {
                    return fqn;
                }

                public void setFullyQualifiedName(String fqn) {
                    this.fqn = fqn;
                }

                public String[] getImportedNamespaces() {
                    return imports.toArray(new String[imports.size()]);
                }

                public String[] getImportedExtensions() {
                    return extensionImports.toArray(new String[extensionImports.size()]);
                }

            };

            ctx = ctx.cloneWithResource(res);

            for (final Iterator<Set<LazyVar>> iter = computeStack(str).iterator(); iter.hasNext();) {
                final Set<LazyVar> vars = iter.next();
                for (final Iterator<LazyVar> iterator = vars.iterator(); iterator.hasNext();) {
                    final LazyVar v = iterator.next();
                    Type vType = null;
                    if (v.typeName != null) {
                        vType = ctx.getTypeForName(v.typeName);
                    } else {
                        vType = new ExpressionFacade(ctx).analyze(v.expression, new HashSet<AnalysationIssue>());
                        if (v.forEach) {
                            if (vType instanceof ParameterizedType) {
                                vType = ((ParameterizedType) vType).getInnerType();
                            } else {
                                vType = null;
                            }
                        }
                    }
                    ctx = ctx.cloneWithVariable(new Variable(v.name, vType));
                }
            }
        }
        return ctx;

    }

}
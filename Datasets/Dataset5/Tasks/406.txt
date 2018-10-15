return handle(new PluginJavaExtensionStatement(jp,

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

package org.eclipse.xtend.ui.core.internal.builder;

import java.util.List;

import org.eclipse.internal.xtend.expression.ast.DeclaredParameter;
import org.eclipse.internal.xtend.expression.ast.Identifier;
import org.eclipse.internal.xtend.xtend.ast.JavaExtensionStatement;
import org.eclipse.internal.xtend.xtend.parser.ExtensionFactory;
import org.eclipse.jdt.core.IJavaProject;

public class PluginExtensionFactory extends ExtensionFactory {

    private IJavaProject jp;

    public PluginExtensionFactory(final IJavaProject jp, final String name) {
        super(name);
        this.jp = jp;
    }

    @Override
    public JavaExtensionStatement createJavaExtension(Identifier name, Identifier type, List<DeclaredParameter> params, 
    		Identifier javaType, Identifier javaMethod, List<Identifier> javaParamTypes, Identifier cached, Identifier priv) {
        return (JavaExtensionStatement) handle(new PluginJavaExtensionStatement(jp,
                name, nonNull(params), type, javaType, javaMethod, nonNull(javaParamTypes), cached != null,
                priv != null));
    }
}
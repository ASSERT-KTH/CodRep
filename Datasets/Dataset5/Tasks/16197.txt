public VetoableCallback getCallback();

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

package org.eclipse.xtend.expression;

import java.util.List;
import java.util.Map;
import java.util.Set;

import org.eclipse.emf.mwe.core.monitor.ProgressMonitor;
import org.eclipse.internal.xtend.expression.ast.SyntaxElement;
import org.eclipse.internal.xtend.xtend.ast.Around;
import org.eclipse.internal.xtend.xtend.ast.Extension;
import org.eclipse.xtend.typesystem.Type;

/**
 * @author Sven Efftinge (http://www.efftinge.de)
 * @author Arno Haase
 */
public interface ExecutionContext extends TypeSystem {
    String IMPLICIT_VARIABLE = "this";

    ExecutionContext cloneWithVariable(Variable v);

    ExecutionContext cloneWithoutVariables();

    Variable getVariable(String name);

    Map<String, Variable> getVisibleVariables();

    /** 
     * accessible only through special extension methods
     */
    Map<String, Variable> getGlobalVariables();
    
    ExecutionContext cloneWithResource(Resource ns);

    ExecutionContext cloneWithoutResource();
    
    ExecutionContext cloneWithoutMonitor();

    Resource currentResource();

    Extension getExtensionForTypes(String functionName, Type[] parameterTypes);

    Extension getExtension(String functionName, Object[] actualParameters);

    Set<? extends Extension> getAllExtensions();
    
    List<Around> getExtensionAdvices();
    
    void preTask(Object element);

	void postTask(Object element);
	
	/**
	 * Retrieves the associated ResourceManager
	 * @since 4.1.2
	 */
	ResourceManager getResourceManager ();
	
	/**
	 * Retrieves the associated ProgressMonitor
	 * @since 4.1.2
	 */
	ProgressMonitor getMonitor ();
	void handleRuntimeException (RuntimeException ex, SyntaxElement element, Map<String,Object> additionalContextInfo);
	Object handleNullEvaluation(SyntaxElement element);

	public Callback getCallback();

	Type getReturnType(Extension extension, Type[] paramTypes,
			Set<AnalysationIssue> issues);

}
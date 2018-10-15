package org.eclipse.xtend.middleend.javaannotations;

/*
Copyright (c) 2008 Arno Haase.
All rights reserved. This program and the accompanying materials
are made available under the terms of the Eclipse Public License v1.0
which accompanies this distribution, and is available at
http://www.eclipse.org/legal/epl-v10.html

Contributors:
    Arno Haase - initial API and implementation
 */
package org.eclipse.xtend.backend.functions.java;

import org.eclipse.xtend.backend.common.ExecutionContext;


/**
 * This marker interface gives Java extensions access to the execution context.
 *  if the class providing a Java extension implements this interface, the executor
 *  calls the setExecutionContext method to ensure that the method has access to 
 *  the current ExecutionContext.
 *  
 * @author Arno Haase (http://www.haase-consulting.com)
 */
public interface ExecutionContextAware {
    void setExecutionContext (ExecutionContext ctx);
}
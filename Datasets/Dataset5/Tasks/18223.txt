void register (Collection <? extends NamedFunction> f);

/*
Copyright (c) 2008 Arno Haase.
All rights reserved. This program and the accompanying materials
are made available under the terms of the Eclipse Public License v1.0
which accompanies this distribution, and is available at
http://www.eclipse.org/legal/epl-v10.html

Contributors:
    Arno Haase - initial API and implementation
 */
package org.eclipse.xtend.backend.functions;

import java.util.Collection;

import org.eclipse.xtend.backend.common.FunctionDefContext;
import org.eclipse.xtend.backend.common.NamedFunction;



/**
 * This interface provides additional access to the Fdc for use during initialization,
 *  e.g. in the middle ends.
 *  
 * @author Arno Haase (http://www.haase-consulting.com)
 */
public interface FunctionDefContextInternal extends FunctionDefContext {
    void register (NamedFunction f);
    void register (Collection <NamedFunction> f);
}
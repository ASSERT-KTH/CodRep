Map<String, ? extends Property> getProperties (ExecutionContext ctx);

/*
Copyright (c) 2008 Arno Haase.
All rights reserved. This program and the accompanying materials
are made available under the terms of the Eclipse Public License v1.0
which accompanies this distribution, and is available at
http://www.eclipse.org/legal/epl-v10.html

Contributors:
    Arno Haase - initial API and implementation
 */
package org.eclipse.xtend.backend.common;

import java.util.Collection;
import java.util.Map;


/**
 * 
 * @author Arno Haase (http://www.haase-consulting.com)
 */
public interface BackendType {
    Object create ();
    
    boolean isAssignableFrom (BackendType other);
    
    Object getProperty (ExecutionContext ctx, Object o, String name);
    void setProperty (ExecutionContext ctx, Object o, String name, Object value);

    Collection<? extends NamedFunction> getBuiltinOperations ();
    
    // stuff required for reflection / meta programming
    String getName ();
    Collection<? extends BackendType> getSuperTypes ();
    Map<String, ? extends Property> getProperties ();
    Map<String, ? extends StaticProperty> getStaticProperties ();
    
    String getUniqueRepresentation ();
}
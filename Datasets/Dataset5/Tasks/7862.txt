package org.eclipse.xtend.backend.types.java.internal;

/*
Copyright (c) 2008 Arno Haase.
All rights reserved. This program and the accompanying materials
are made available under the terms of the Eclipse Public License v1.0
which accompanies this distribution, and is available at
http://www.eclipse.org/legal/epl-v10.html

Contributors:
    Arno Haase - initial API and implementation
 */
package org.eclipse.xtend.backend.types.java;


/**
 * This type system feels responsible for any Java class and treats it as a Java bean.
 * 
 * @author Arno Haase (http://www.haase-consulting.com)
 */
public final class GlobalJavaBeansTypesystem extends AbstractJavaBeansTypesystem {
    @Override
    public boolean matchesScope (Class<?> cls) {
        return true;
    }
}
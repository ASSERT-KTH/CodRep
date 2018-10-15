private VoidType () {super ("Void", "{builtin}Void"); }

/*
Copyright (c) 2008 Arno Haase.
All rights reserved. This program and the accompanying materials
are made available under the terms of the Eclipse Public License v1.0
which accompanies this distribution, and is available at
http://www.eclipse.org/legal/epl-v10.html

Contributors:
    Arno Haase - initial API and implementation
 */
package org.eclipse.xtend.backend.types.builtin;

import org.eclipse.xtend.backend.common.BackendType;
import org.eclipse.xtend.backend.types.AbstractType;


/**
 * This type receives special treatment because it is the only type that can not
 * be determined based on the Java class of an object.
 * 
 * @author Arno Haase (http://www.haase-consulting.com)
 */
public final class VoidType extends AbstractType {
    public static final VoidType INSTANCE = new VoidType();

    private VoidType () {super ("Void"); }

    @Override
    public boolean isAssignableFrom (BackendType other) {
        return other == this;
    }
}
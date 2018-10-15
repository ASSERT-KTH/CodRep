private ListType () {super ("List", "{builtin}List", CollectionType.INSTANCE); }

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

import java.util.ArrayList;

import org.eclipse.xtend.backend.types.AbstractType;


/**
 * 
 * @author Arno Haase (http://www.haase-consulting.com)
 */
public final class ListType extends AbstractType {
    private ListType () {super ("List", CollectionType.INSTANCE); }
    
    public static final ListType INSTANCE = new ListType ();
    
    @Override
    public Object create() {
        return new ArrayList<Object>();
    }
}
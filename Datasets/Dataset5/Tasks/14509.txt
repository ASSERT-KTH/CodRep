return o instanceof Set<?>;

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

package org.eclipse.internal.xtend.type.baseimpl.types;

import java.util.Collections;
import java.util.LinkedHashSet;
import java.util.Set;

import org.eclipse.xtend.expression.TypeSystem;
import org.eclipse.xtend.typesystem.Feature;
import org.eclipse.xtend.typesystem.ParameterizedType;
import org.eclipse.xtend.typesystem.Type;

/**
 * @author Sven Efftinge (http://www.efftinge.de)
 * @author Arno Haase
 */
public class SetTypeImpl extends CollectionTypeImpl {

    public SetTypeImpl(final Type innerType, final TypeSystem ts, final String name) {
        super(innerType, ts, name);
    }

    @Override
    public boolean isInstance(final Object o) {
        return o instanceof Set;
    }

    @Override
    public Feature[] getContributedFeatures() {
        return new Feature[] {};
    }

    @Override
    public Set<Type> getSuperTypes() {
        return Collections.singleton(getTypeSystem().getCollectionType(getInnerType()));
    }

    @Override
    public Object newInstance() {
        return new LinkedHashSet<Object>();
    }

    @Override
    public ParameterizedType cloneWithInnerType(final Type innerType) {
        return (ParameterizedType) getTypeSystem().getSetType(innerType);
    }

}
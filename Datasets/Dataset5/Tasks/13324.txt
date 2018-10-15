public class VoidType extends AbstractTypeImpl {

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
import java.util.Set;

import org.eclipse.xtend.expression.TypeSystem;
import org.eclipse.xtend.typesystem.AbstractTypeImpl;
import org.eclipse.xtend.typesystem.Feature;
import org.eclipse.xtend.typesystem.Type;

/**
 * @author Sven Efftinge (http://www.efftinge.de)
 * @author Arno Haase
 */
public class VoidType extends AbstractTypeImpl implements Type {

    public VoidType(final TypeSystem ts, final String name) {
        super(ts, name);
    }

    @Override
    public Feature[] getContributedFeatures() {
        return new Feature[0];
    }

    public boolean isInstance(final Object o) {
        return o == null;
    }

    public Object newInstance() {
        throw new UnsupportedOperationException();
    }

    @Override
    public boolean isAbstract() {
        return true;
    }

    @Override
    public Set<Type> getSuperTypes() {
        return Collections.singleton(getTypeSystem().getObjectType());
    }

    @Override
    public String getDocumentation() {
        return "Void is used as an undefined type. It's only instance is the null reference.";
    }

}
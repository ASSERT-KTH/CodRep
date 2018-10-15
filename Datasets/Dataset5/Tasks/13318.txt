public class FeatureTypeImpl extends BuiltinBaseType {

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

import org.eclipse.internal.xtend.type.baseimpl.PropertyImpl;
import org.eclipse.xtend.expression.TypeSystem;
import org.eclipse.xtend.typesystem.Feature;
import org.eclipse.xtend.typesystem.Type;

/**
 * @author Sven Efftinge (http://www.efftinge.de)
 * @author Arno Haase
 */
public class FeatureTypeImpl extends BuiltinBaseType implements Type {

    public FeatureTypeImpl(final TypeSystem ts, final String name) {
        super(ts, name);
    }

    public boolean isInstance(final Object o) {
        return o instanceof Feature;
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
    public Feature[] getContributedFeatures() {
        return new Feature[] { new PropertyImpl(this, "name", getTypeSystem().getStringType()) {
            public Object get(final Object target) {
                return ((Feature) target).getName();
            }

            @Override
            public void set(final Object target, final Object val) {
                throw new UnsupportedOperationException("property name is unsettable!");
            }

        }, new PropertyImpl(this, "returnType", getTypeSystem().getTypeType()) {
            public Object get(final Object target) {
                return ((Feature) target).getReturnType();
            }

            @Override
            public void set(final Object target, final Object val) {
                throw new UnsupportedOperationException("property name is unsettable!");
            }

        }, new PropertyImpl(this, "owner", getTypeSystem().getTypeType()) {
            public Object get(final Object target) {
                return ((Feature) target).getOwner();
            }

            @Override
            public void set(final Object target, final Object val) {
                throw new UnsupportedOperationException("property name is unsettable!");
            }

        }, new PropertyImpl(this, "documentation", getTypeSystem().getStringType()) {

            public Object get(final Object target) {
                return ((Feature) target).getDocumentation();
            }
        } };
    }

}
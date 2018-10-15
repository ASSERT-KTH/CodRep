public final class OperationTypeImpl extends FeatureTypeImpl {

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
import java.util.List;
import java.util.Set;

import org.eclipse.internal.xtend.type.baseimpl.OperationImpl;
import org.eclipse.xtend.expression.TypeSystem;
import org.eclipse.xtend.typesystem.Feature;
import org.eclipse.xtend.typesystem.Operation;
import org.eclipse.xtend.typesystem.Type;

public final class OperationTypeImpl extends FeatureTypeImpl implements Type {

    public OperationTypeImpl(final TypeSystem ts, final String name) {
        super(ts, name);
    }

    @Override
    public boolean isInstance(final Object o) {
        return o instanceof Operation;
    }

    @Override
    public Object newInstance() {
        throw new UnsupportedOperationException();
    }

    @Override
    public boolean isAbstract() {
        return true;
    }

    @Override
    public Set<Type> getSuperTypes() {
        return Collections.singleton(getTypeSystem().getFeatureType());
    }

    @Override
    public Feature[] getContributedFeatures() {
        return new Feature[] {
                new OperationImpl(this, "evaluate", getTypeSystem().getObjectType(),
                        getTypeSystem().getObjectType(), getTypeSystem().getListType(null)) {

                    @Override
                    public Object evaluateInternal(final Object target, final Object[] params) {
                        return ((Operation) target).evaluate(target, ((List<?>) params[0]).toArray());
                    }

                },
                new OperationImpl(this, "getParameterTypes",
                        getTypeSystem().getListType(getTypeSystem().getTypeType())) {

                    @Override
                    public Object evaluateInternal(final Object target, final Object[] params) {
                        return ((Operation) target).getParameterTypes();
                    }

                } };
    }
}
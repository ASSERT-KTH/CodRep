public class RealTypeImpl extends BuiltinBaseType {

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

import java.math.BigDecimal;
import java.util.Collections;
import java.util.Set;

import org.eclipse.internal.xtend.type.baseimpl.OperationImpl;
import org.eclipse.xtend.expression.TypeSystem;
import org.eclipse.xtend.typesystem.Feature;
import org.eclipse.xtend.typesystem.Type;

/**
 * @author Sven Efftinge (http://www.efftinge.de)
 * @author Arno Haase
 */
public class RealTypeImpl extends BuiltinBaseType implements Type {

    public RealTypeImpl(final TypeSystem ts, final String name) {
        super(ts, name);
    }

    @Override
    public Feature[] getContributedFeatures() {
        return new Feature[] {
                new OperationImpl(this, "+", RealTypeImpl.this, new Type[] { RealTypeImpl.this }) {
                    @Override
                    public Object evaluateInternal(final Object target, final Object[] params) {
                        if (params[0] == null)
                            return null;

                        return new Double(((Number) target).doubleValue() + ((Number) params[0]).doubleValue());
                    }
                },
                new OperationImpl(this, "-", RealTypeImpl.this, new Type[] { RealTypeImpl.this }) {
                    @Override
                    public Object evaluateInternal(final Object target, final Object[] params) {
                        if (params[0] == null)
                            return null;

                        return new Double(((Number) target).doubleValue() - ((Number) params[0]).doubleValue());
                    }
                },
                new OperationImpl(this, "-", RealTypeImpl.this, new Type[] {}) {
                    @Override
                    public Object evaluateInternal(final Object target, final Object[] params) {
                        return new Double(((Number) target).doubleValue() * -1.0d);
                    }
                },
                new OperationImpl(this, "*", RealTypeImpl.this, new Type[] { RealTypeImpl.this }) {
                    @Override
                    public Object evaluateInternal(final Object target, final Object[] params) {
                        if (params[0] == null)
                            return null;

                        return new Double(((Number) target).doubleValue() * ((Number) params[0]).doubleValue());
                    }
                },
                new OperationImpl(this, "/", RealTypeImpl.this, new Type[] { RealTypeImpl.this }) {
                    @Override
                    public Object evaluateInternal(final Object target, final Object[] params) {
                        if (params[0] == null)
                            return null;

                        return new Double(((Number) target).doubleValue() / ((Number) params[0]).doubleValue());
                    }
                },
                new OperationImpl(this, "==", getTypeSystem().getBooleanType(), new Type[] { getTypeSystem()
                        .getObjectType() }) {
                    @Override
                    public Object evaluateInternal(final Object target, final Object[] params) {
                        if (target == null)
                            return new Boolean(target == params[0]);
                        
                        try {
                            return toDouble(target).equals(toDouble(params[0]));
                        }
                        catch (Exception exc) {
                            return false;
                        }
                    }

                },
                new OperationImpl(this, "!=", getTypeSystem().getBooleanType(), new Type[] { getTypeSystem()
                        .getObjectType() }) {
                    @Override
                    public Object evaluateInternal(final Object target, final Object[] params) {
                        if (target == null)
                            return new Boolean(target != params[0]);
                        
                        try {
                            return !toDouble(target).equals(toDouble(params[0]));
                        }
                        catch (Exception exc) {
                            return true;
                        }
                    }
                },
                new OperationImpl(this, ">", getTypeSystem().getBooleanType(), new Type[] { getTypeSystem()
                        .getObjectType() }) {
                    @Override
                    public Object evaluateInternal(final Object target, final Object[] params) {
                        if (target == null)
                            return Boolean.FALSE;
                        if (params[0] == null)
                            return Boolean.FALSE;
                        return new Boolean(((Comparable<Double>) toDouble(target)).compareTo(toDouble(params[0])) > 0);
                    }
                },
                new OperationImpl(this, ">=", getTypeSystem().getBooleanType(), new Type[] { getTypeSystem()
                        .getObjectType() }) {
                    @Override
                    public Object evaluateInternal(final Object target, final Object[] params) {
                        if (target == null)
                            return params[0] == null ? Boolean.TRUE : Boolean.FALSE;
                        if (params[0] == null)
                            return Boolean.FALSE;
                        return new Boolean(((Comparable<Double>) toDouble(target)).compareTo(toDouble(params[0])) >= 0);
                    }
                },
                new OperationImpl(this, "<", getTypeSystem().getBooleanType(), new Type[] { getTypeSystem()
                        .getObjectType() }) {
                    @Override
                    public Object evaluateInternal(final Object target, final Object[] params) {
                        if (target == null)
                            return Boolean.FALSE;
                        if (params[0] == null)
                            return Boolean.FALSE;
                        return new Boolean(((Comparable<Double>) toDouble(target)).compareTo(toDouble(params[0])) < 0);
                    }
                },
                new OperationImpl(this, "<=", getTypeSystem().getBooleanType(), new Type[] { getTypeSystem()
                        .getObjectType() }) {
                    @Override
                    public Object evaluateInternal(final Object target, final Object[] params) {
                        if (target == null)
                            return params[0] == null ? Boolean.TRUE : Boolean.FALSE;
                        if (params[0] == null)
                            return Boolean.FALSE;
                        return new Boolean(((Comparable<Double>) toDouble(target)).compareTo(toDouble(params[0])) <= 0);
                    }
                } };
    }

    @Override
    public Set<Type> getSuperTypes() {
        return Collections.singleton(getTypeSystem().getObjectType());
    }

    public boolean isInstance(final Object o) {
        return o instanceof Double || o instanceof Float || o instanceof BigDecimal;
    }

    public Object newInstance() {
        return new Double(1);
    }

    private Double toDouble(final Object o) {
        if (o == null)
            return null;
        
        if (o instanceof Number)
            return ((Number) o).doubleValue();

        throw new IllegalArgumentException(o.getClass().getName() + " not supported");
    }

    @Override
    public Object convert(final Object src, final Class<?> targetType) {
        final Double l = toDouble(src);
        if (targetType.isAssignableFrom(Double.class) || targetType.isAssignableFrom(Double.TYPE))
            return l;
        else if (targetType.isAssignableFrom(Float.class) || targetType.isAssignableFrom(Float.TYPE))
            return new Float(l.doubleValue());
        else if (targetType.isAssignableFrom(BigDecimal.class))
            return new BigDecimal(l.doubleValue());
        return super.convert(src, targetType);
    }

}
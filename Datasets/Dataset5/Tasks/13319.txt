public final class IntegerTypeImpl extends BuiltinBaseType {

/*******************************************************************************
 * Copyright (c) 2005, 2009 committers of openArchitectureWare and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     committers of openArchitectureWare - initial API and implementation
 *******************************************************************************/

package org.eclipse.internal.xtend.type.baseimpl.types;

import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Set;

import org.eclipse.internal.xtend.type.baseimpl.OperationImpl;
import org.eclipse.xtend.expression.TypeSystem;
import org.eclipse.xtend.typesystem.Feature;
import org.eclipse.xtend.typesystem.Type;

/**
 * @author Sven Efftinge (http://www.efftinge.de)
 * @author Arno Haase
 * @author Heiko Behrens
 */
public final class IntegerTypeImpl extends BuiltinBaseType implements Type {

    public IntegerTypeImpl(final TypeSystem ts, final String name) {
        super(ts, name);
    }

    public boolean isInstance(final Object o) {
        return o instanceof BigInteger || o instanceof Integer || o instanceof Byte || o instanceof Long
                || o instanceof Short;
    }

    public Object newInstance() {
        return new BigInteger("-1");
    }

    @Override
    public Feature[] getContributedFeatures() {
        return new Feature[] {
                new OperationImpl(this, "+", IntegerTypeImpl.this, new Type[] { IntegerTypeImpl.this }) {
                    @Override
                    public Object evaluateInternal(final Object target, final Object[] params) {
                        if (params[0] == null)
                            return null;
                        return toInt(target).add(toInt(params[0]));
                    }
                },
                new OperationImpl(this, "-", IntegerTypeImpl.this, new Type[] { IntegerTypeImpl.this }) {
                    @Override
                    public Object evaluateInternal(final Object target, final Object[] params) {
                        if (params[0] == null)
                            return null;
                        return toInt(target).subtract(toInt(params[0]));
                    }
                },
                new OperationImpl(this, "-", IntegerTypeImpl.this, new Type[] {}) {
                    @Override
                    public Object evaluateInternal(final Object target, final Object[] params) {
                    	return toInt(target).negate();
                    }
                },
                new OperationImpl(this, "*", IntegerTypeImpl.this, new Type[] { IntegerTypeImpl.this }) {
                    @Override
                    public Object evaluateInternal(final Object target, final Object[] params) {
                        if (params[0] == null)
                            return null;

                        return toInt(target).multiply(toInt(params[0]));
                    }
                },
                new OperationImpl(this, "/", IntegerTypeImpl.this, new Type[] { IntegerTypeImpl.this }) {
                    @Override
                    public Object evaluateInternal(final Object target, final Object[] params) {
                        if (params[0] == null)
                            return null;

                        return toInt(target).divide(toInt(params[0]));
                    }
                },
                new OperationImpl(this, "==", getTypeSystem().getBooleanType(), new Type[] { IntegerTypeImpl.this }) {
                    @Override
                    public Object evaluateInternal(final Object target, final Object[] params) {
                        if (target == null)
                            return new Boolean(target == params[0]);
                        try {
                        	return toInt(target).equals(toInt(params[0]));
                        }
                        catch (Exception exc) {
                            return false;
                        }
                    }

                },
                new OperationImpl(this, "!=", getTypeSystem().getBooleanType(), new Type[] { IntegerTypeImpl.this }) {
                    @Override
                    public Object evaluateInternal(final Object target, final Object[] params) {
                        if (target == null)
                            return params[0] != null;

                        try {
                            return ! toInt(target).equals(toInt(params[0]));
                        }
                        catch (Exception exc) {
                            return true;
                        }
                    }
                },
                new OperationImpl(this, ">", getTypeSystem().getBooleanType(), new Type[] { IntegerTypeImpl.this }) {
                    @Override
                    public Object evaluateInternal(final Object target, final Object[] params) {
                        if (target == null)
                            return Boolean.FALSE;
                        if (params[0] == null)
                            return Boolean.FALSE;
                        
                        try {
                        	return toInt(target).compareTo(toInt(params[0])) > 0;
                        }
                        catch (Exception exc) {
                            return Boolean.FALSE; 
                        }
                    }
                },
                new OperationImpl(this, ">=", getTypeSystem().getBooleanType(), new Type[] { IntegerTypeImpl.this }) {
                    @Override
                    public Object evaluateInternal(final Object target, final Object[] params) {
                        if (target == null)
                            return params[0] == null ? Boolean.TRUE : Boolean.FALSE;
                        if (params[0] == null)
                            return Boolean.FALSE;
                        
                        try {
                        	return toInt(target).compareTo(toInt(params[0])) >= 0;
                        }
                        catch (Exception exc) {
                            return Boolean.FALSE; 
                        }
                    }
                },
                new OperationImpl(this, "<", getTypeSystem().getBooleanType(), new Type[] { IntegerTypeImpl.this }) {
                    @Override
                    public Object evaluateInternal(final Object target, final Object[] params) {
                        if (target == null)
                            return Boolean.FALSE;
                        if (params[0] == null)
                            return Boolean.FALSE;

                        try {
                        	return toInt(target).compareTo(toInt(params[0])) < 0;
                        }
                        catch (Exception exc) {
                            return Boolean.FALSE; 
                        }
                    }
                },
                new OperationImpl(this, "<=", getTypeSystem().getBooleanType(), new Type[] { IntegerTypeImpl.this }) {
                    @Override
                    public Object evaluateInternal(final Object target, final Object[] params) {
                        if (target == null)
                            return params[0] == null ? Boolean.TRUE : Boolean.FALSE;
                        if (params[0] == null)
                            return Boolean.FALSE;

                        try {
                        	return toInt(target).compareTo(toInt(params[0])) <= 0;
                        }
                        catch (Exception exc) {
                            return Boolean.FALSE; 
                        }
                    }
                }, new OperationImpl(this, "upTo", getTypeSystem().getListType(this), new Type[] { this }) {

                    @Override
                    public String getDocumentation() {
                        return "returns a List of Integers starting with the value of the target expression, up to "
                                + "the value of the specified Integer, incremented by one.<br/>"
                                + "e.g. '1.upTo(5)' evaluates to {1,2,3,4,5}";
                    }

                    @Override
                    public Object evaluateInternal(final Object target, final Object[] params) {
                        final List<BigInteger> result = new ArrayList<BigInteger>();
                        BigInteger l1 = toInt(target);
                        final BigInteger l2 = toInt(params[0]);

                        while (l1.compareTo(l2) <= 0) {
                            result.add(l1);
                            l1 = l1.add(BigInteger.ONE);
                        }
                        return result;
                    }
                }, new OperationImpl(this, "upTo", getTypeSystem().getListType(this), new Type[] { this, this }) {

                    @Override
                    public String getDocumentation() {
                        return "returns a List of Integers starting with the value of the target expression, up to "
                                + "the value of the first paramter, incremented by the second parameter.<br/>"
                                + "e.g. '1.upTo(10, 2)' evaluates to {1,3,5,7,9}";
                    }

                    @Override
                    public Object evaluateInternal(final Object target, final Object[] params) {
                        final List<BigInteger> result = new ArrayList<BigInteger>();
                        BigInteger l1 = toInt(target);
                        final BigInteger l2 = toInt(params[0]);
                        final BigInteger l3 = toInt(params[1]);

                        while (l1.compareTo(l2) <= 0) {
                            result.add(l1);
                            l1 = l1.add(l3);
                        }
                        return result;
                    }
                } };
    }

	@Override
    public Set<Type> getSuperTypes() {
        return Collections.singleton(getTypeSystem().getRealType());
    }

	protected BigInteger toInt(final Object o) {
		if(o == null)
			return null;
		
		if (o instanceof BigInteger)
			return (BigInteger) o;
		
        if (o instanceof Integer)
            return BigInteger.valueOf(((Integer)o).longValue()); 
        else if (o instanceof Byte)
        	return BigInteger.valueOf(((Byte)o).longValue());
        else if (o instanceof Long)
        	return BigInteger.valueOf((Long)o);
        else if (o instanceof Short)
            return BigInteger.valueOf(((Short) o).longValue());
		
		throw new IllegalArgumentException(o.getClass().getName() + " not supported");
	}
    
    @Override
    public Object convert(final Object src, final Class<?> targetType) {
        final BigInteger value = toInt(src);
        
        if (targetType.isAssignableFrom(BigInteger.class))
        	return value;
        else if (targetType.isAssignableFrom(Long.class) || targetType.isAssignableFrom(Long.TYPE))
        	return value.longValue();
        else if (targetType.isAssignableFrom(Integer.class) || targetType.isAssignableFrom(Integer.TYPE))
            return value.intValue();
        else if (targetType.isAssignableFrom(Byte.class) || targetType.isAssignableFrom(Byte.TYPE))
            return value.byteValue();
        else if (targetType.isAssignableFrom(Short.class) || targetType.isAssignableFrom(Short.TYPE))
            return value.shortValue();
        return super.convert(src, targetType);
    }

}
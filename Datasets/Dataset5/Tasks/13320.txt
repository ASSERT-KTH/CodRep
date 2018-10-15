public class ListTypeImpl extends CollectionTypeImpl {

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

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Set;

import org.eclipse.internal.xtend.type.baseimpl.OperationImpl;
import org.eclipse.xtend.expression.TypeSystem;
import org.eclipse.xtend.typesystem.Feature;
import org.eclipse.xtend.typesystem.ParameterizedType;
import org.eclipse.xtend.typesystem.Type;

/**
 * @author Sven Efftinge (http://www.efftinge.de)
 * @author Arno Haase
 */
public class ListTypeImpl extends CollectionTypeImpl implements Type {

	public ListTypeImpl(final Type innerType, final TypeSystem ts, final String name) {
		super(innerType, ts, name);
	}

	@Override
	@SuppressWarnings("unchecked")
	public boolean isInstance(final Object o) {
		return o instanceof List;
	}

	@Override
	public Object newInstance() {
		return new ArrayList<Object>();
	}

	@Override
	public ParameterizedType cloneWithInnerType(final Type innerType) {
		return (ParameterizedType) getTypeSystem().getListType(innerType);
	}

	@Override
	public Feature[] getContributedFeatures() {
		return new Feature[] { new OperationImpl(this, "get", getInnerType(), new Type[] { getTypeSystem().getIntegerType() }) {
			@Override
			public Object evaluateInternal(final Object target, final Object[] params) {
				return ((List<?>) target).get(((Number) params[0]).intValue());
			}
		}, new OperationImpl(this, "indexOf", getTypeSystem().getIntegerType(), new Type[] { getTypeSystem().getObjectType() }) {
			@Override
			public Object evaluateInternal(final Object target, final Object[] params) {
				return new Long(((List<?>) target).indexOf(params[0]));
			}
		}, new OperationImpl(this, "first", getInnerType(), new Type[0]) {
			@Override
			@SuppressWarnings("unchecked")
			public Object evaluateInternal(final Object target, final Object[] params) {
				if (target instanceof List) {
					List<?> l = (List<?>) target;
					if (l.size() > 0)
						return l.get(0);
				}
				return null;
			}
		}, new OperationImpl(this, "reverse", getTypeSystem().getCollectionType(getInnerType()), new Type[0]) {
			@Override
			@SuppressWarnings("unchecked")
			public Object evaluateInternal(final Object target, final Object[] params) {
				if (target instanceof List) {
					List<?> l = new ArrayList ((List<?>) target);
					Collections.reverse(l);
					return l;
				}
				return null;
			}
		}, new OperationImpl(this, "last", getInnerType(), new Type[0]) {
			@Override
			@SuppressWarnings("unchecked")
			public Object evaluateInternal(final Object target, final Object[] params) {
				if (target instanceof List) {
					List<?> l = (List<?>) target;
					if (l.size() > 0)
						return l.get(l.size() - 1);
				}
				return null;
			}
		}, new OperationImpl(this, "withoutFirst", this, new Type[0]) {
			@SuppressWarnings("unchecked")
			@Override
			public Object evaluateInternal(final Object target, final Object[] params) {
				if (target instanceof List) {
					List l = (List) target;
					List r = new ArrayList();
					for (int i = 1; i < l.size(); i++) {
						r.add(l.get(i));
					}
					return r;
				}
				return null;
			}
		}, new OperationImpl(this, "withoutLast", this, new Type[0]) {
			@SuppressWarnings("unchecked")
			@Override
			public Object evaluateInternal(final Object target, final Object[] params) {
				if (target instanceof List) {
					List l = (List) target;
					List r = new ArrayList();
					for (int i = 0; i < l.size() - 1; i++) {
						r.add(l.get(i));
					}
					return r;
				}
				return null;
			}
		}

		};
	}

	@Override
	public Set<Type> getSuperTypes() {
		return Collections.singleton(getTypeSystem().getCollectionType(getInnerType()));
	}

}
new OperationImpl(this, "removeAll", this, getTypeSystem().getCollectionType(getTypeSystem().getObjectType())) {

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
import java.util.Collection;
import java.util.Collections;
import java.util.Iterator;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.eclipse.internal.xtend.type.baseimpl.OperationImpl;
import org.eclipse.internal.xtend.type.baseimpl.PropertyImpl;
import org.eclipse.xtend.expression.TypeSystem;
import org.eclipse.xtend.typesystem.Feature;
import org.eclipse.xtend.typesystem.ParameterizedType;
import org.eclipse.xtend.typesystem.Type;

/**
 * @author Sven Efftinge (http://www.efftinge.de)
 * @author Arno Haase
 */
@SuppressWarnings("unchecked")
public class CollectionTypeImpl extends BuiltinBaseType implements ParameterizedType {
	private static final Log LOG = LogFactory.getLog(CollectionTypeImpl.class);

	private final Type innerType;

	public CollectionTypeImpl(final Type innerType, final TypeSystem ts, final String name) {
		super(ts, name);
		this.innerType = innerType;
	}

	public Type getInnerType() {
		return innerType;
	}
	
	private Type getInnerTypeRec(Type type) {
		Type result = type;
		if (result instanceof CollectionTypeImpl)
			return getInnerTypeRec(((ParameterizedType) result).getInnerType());
		return result;
	}

	public ParameterizedType cloneWithInnerType(final Type innerType) {
		return (ParameterizedType) getTypeSystem().getCollectionType(innerType);
	}

	@Override
	protected boolean internalIsAssignableFrom(final Type t) {
		return super.internalIsAssignableFrom(t);
	}

	public boolean isInstance(final Object o) {
		return o instanceof Collection;
	}

	public Object newInstance() {
		return new ArrayList<Object>();
	}

	@Override
	public Feature[] getContributedFeatures() {
		return new Feature[] {
				new OperationImpl(this, "toList", getTypeSystem().getListType(getInnerType())) {

					@Override
					public String getDocumentation() {
						return "converts this collection to List";
					}

					@Override
					public Object evaluateInternal(final Object target, final Object[] params) {
						if (target==null) {
							LOG.warn("toList called with Null argument. Will return an empty list.");
							return new ArrayList<Object>(0);
						}
						return new ArrayList<Object>(((Collection<?>) target));
					}

					@Override
					public Type getReturnType(final Type targetType, final Type[] paramTypes) {
						if (!(targetType instanceof ParameterizedType))
							return getReturnType();
						final TypeSystem ts = getTypeSystem();
						return ts.getListType(((ParameterizedType) targetType).getInnerType());
					}
				},

				new OperationImpl(this, "toSet", getTypeSystem().getSetType(getInnerType())) {

					@Override
					public String getDocumentation() {
						return "converts this collection to Set";
					}

					@Override
					public Object evaluateInternal(final Object target, final Object[] params) {
						if (target==null) {
							LOG.warn("toSet called with Null argument. Will return an empty set.");
							return new LinkedHashSet<Object>(0);
						}
						return new LinkedHashSet<Object>((Collection<?>) target);
					}

					@Override
					public Type getReturnType(final Type targetType, final Type[] paramTypes) {
						if (!(targetType instanceof ParameterizedType))
							return getReturnType();
						final TypeSystem ts = getTypeSystem();
						return ts.getSetType(((ParameterizedType) targetType).getInnerType());
					}
				},

				new OperationImpl(this, "toString", getTypeSystem().getStringType(), getTypeSystem().getStringType()) {

					@Override
					public String getDocumentation() {
						return "concatenates each contained element (using toString()), separated by the specified String.";
					}

					@Override
					public Object evaluateInternal(final Object target, final Object[] params) {
						final StringBuffer buff = new StringBuffer();
						for (final Iterator<?> iter = ((Collection<?>) target).iterator(); iter.hasNext();) {
							buff.append(iter.next().toString());
							if (iter.hasNext()) {
								buff.append(params[0].toString());
							}
						}
						return buff.toString();
					}
				},

				new PropertyImpl(this, "size", getTypeSystem().getIntegerType()) {

					@Override
					public String getDocumentation() {
						return "returns the size of this Collection";
					}

					public Object get(final Object target) {
						return new Long(((Collection<?>) target).size());
					}
				},

				new PropertyImpl(this, "isEmpty", getTypeSystem().getBooleanType()) {

					@Override
					public String getDocumentation() {
						return "returns true if this Collection is empty";
					}

					public Object get(final Object target) {
						if (target==null) {
							LOG.warn("isEmpty called with Null argument. Will return true.");
							return Boolean.TRUE;
						}
						return new Boolean(((Collection<?>) target).size() == 0);
					}
				},

				new OperationImpl(this, "add", this, getInnerType()) {

					@Override
					public String getDocumentation() {
						return "adds an element to the Collection (modifies it!). returns this Collection.";
					}

					@Override
					public Object evaluateInternal(final Object target, final Object[] params) {
						((Collection<Object>) target).add(params[0]);
						return target;
					}
				},

				new OperationImpl(this, "addAll", this, getTypeSystem().getCollectionType(getInnerType())) {

					@Override
					public String getDocumentation() {
						return "adds all elements to the Collection (modifies it!). returns this Collection.";
					}

					@Override
					public Object evaluateInternal(final Object target, final Object[] params) {
						((Collection<?>) target).addAll((Collection) params[0]);
						return target;
					}
				},

				new OperationImpl(this, "contains", getTypeSystem().getBooleanType(), getTypeSystem().getObjectType()) {

					@Override
					public String getDocumentation() {
						return "returns true if this collection contains the specified object. otherwise false. returns this Collection.";
					}

					@Override
					public Object evaluateInternal(final Object target, final Object[] params) {
						return Boolean.valueOf(((Collection) target).contains(params[0]));
					}
				},

				new OperationImpl(this, "containsAll", getTypeSystem().getBooleanType(), getTypeSystem()
						.getCollectionType(getTypeSystem().getObjectType())) {

					@Override
					public String getDocumentation() {
						return "returns true if this collection contains each element contained in the specified collection. otherwise false. returns this Collection.";
					}

					@Override
					public Object evaluateInternal(final Object target, final Object[] params) {
						return Boolean.valueOf(((Collection) target).containsAll((Collection) params[0]));
					}
				},

				new OperationImpl(this, "remove", this, getTypeSystem().getObjectType()) {

					@Override
					public String getDocumentation() {
						return "removes the specified element from this Collection if contained (modifies it!). returns this Collection.";
					}

					@Override
					public Object evaluateInternal(final Object target, final Object[] params) {
						((Collection) target).remove(params[0]);
						return target;
					}
				},

				new OperationImpl(this, "removeAll", this, getTypeSystem().getObjectType()) {

					@Override
					public String getDocumentation() {
						return "removes all elements contained in the specified collection from this Collection if contained (modifies it!). returns this Collection.";
					}

					@Override
					public Object evaluateInternal(final Object target, final Object[] params) {
						((Collection) target).removeAll((Collection) params[0]);
						return target;
					}
				},

				new OperationImpl(this, "union", getTypeSystem().getSetType(getInnerType()), getTypeSystem()
						.getCollectionType(getTypeSystem().getObjectType())) {

					@Override
					public String getDocumentation() {
						return "returns a new Set, containing all elements from this and the specified Collection";
					}

					@Override
					public Object evaluateInternal(final Object target, final Object[] params) {
						final Set r = new LinkedHashSet((Collection) target);
						if (params!=null && params[0]!=null) {
							r.addAll((Collection) params[0]);
						} else {
							LOG.warn ("Invoking union() with Null as argument. Will return the source collection.");
						}
						return r;
					}
				},

				new OperationImpl(this, "without", getTypeSystem().getSetType(getInnerType()), getTypeSystem()
						.getCollectionType(getTypeSystem().getObjectType())) {

					@Override
					public String getDocumentation() {
						return "returns a new Set, containing all elements from this Collection without the elements from specified Collection";
					}

					@Override
					public Object evaluateInternal(final Object target, final Object[] params) {
						final Set r = new LinkedHashSet((Collection) target);
						r.removeAll((Collection) params[0]);
						return r;
					}
				},

				new OperationImpl(this, "intersect", getTypeSystem().getSetType(getInnerType()), getTypeSystem()
						.getCollectionType(getTypeSystem().getObjectType())) {

					@Override
					public String getDocumentation() {
						return "returns a new Set, containing only the elements contained in this and the specified Collection";
					}

					@Override
					public Object evaluateInternal(final Object target, final Object[] params) {
						final Set r = new LinkedHashSet((Collection) target);
						r.retainAll((Collection) params[0]);
						return r;
					}
				},

				new OperationImpl(this, "flatten", getTypeSystem().getListType(getInnerTypeRec(CollectionTypeImpl.this)),
						new Type[0]) {

					@Override
					public String getDocumentation() {
						return "returns a flattened List.";
					}

					@Override
					public Object evaluateInternal(final Object target, final Object[] params) {
						final List<Object> result = new ArrayList<Object>();
						flattenRec(result, (Collection) target);
						return result;
					}

					public void flattenRec(final List<Object> result, final Collection col) {
						for (final Object element : col) {
							if (element instanceof Collection) {
								flattenRec(result, (Collection) element);
							}
							else {
								result.add(element);
							}
						}
					}
				}

		};
	}

	@Override
	public Set<Type> getSuperTypes() {
		return Collections.singleton(getTypeSystem().getObjectType());
	}

	@Override
	public String toString() {
		String s = getName();
		if (innerType != null) {
			s += "[" + innerType + "]";
		}
		return s;
	}
	
	
//	@Override
//	public boolean equals(Object obj) {
//		if (this == obj)
//			return true;
//
//		if (obj == null)
//			return false;
//
//		if (getClass() != obj.getClass())
//			return false;
//		
//		CollectionTypeImpl other = (CollectionTypeImpl) obj;
//		
//		if (!innerType.equals(other.innerType)) {
//			return false;
//		}
//		
//		return true;
//	}
}
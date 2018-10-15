public final class BooleanTypeImpl extends BuiltinBaseType {

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

import org.eclipse.internal.xtend.type.baseimpl.OperationImpl;
import org.eclipse.xtend.expression.TypeSystem;
import org.eclipse.xtend.typesystem.Feature;
import org.eclipse.xtend.typesystem.Type;

public final class BooleanTypeImpl extends BuiltinBaseType implements Type {
	public BooleanTypeImpl(final TypeSystem ts, final String name) {
		super(ts, name);
	}

	public boolean isInstance(final Object o) {
		return o instanceof Boolean;
	}

	@SuppressWarnings("unchecked")
	@Override
	public Object convert(final Object src, final Class targetType) {
		if (targetType == Boolean.class || targetType == Boolean.TYPE)
			return src;
		return super.convert(src, targetType);
	}

	public Object newInstance() {
		return Boolean.FALSE;
	}

	@Override
	public Feature[] getContributedFeatures() {
		return new Feature[] { 
			new OperationImpl(this, "!",BooleanTypeImpl.this) {
			@Override
			public Object evaluateInternal(final Object target,
					final Object[] params) {
				return target == null ? null : new Boolean(!((Boolean) target)
						.booleanValue());
			}
		}

		};
	}

	@Override
	public Set<Type> getSuperTypes() {
		return Collections.singleton(getTypeSystem().getObjectType());
	}

}
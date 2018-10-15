register(new QualifiedName(mtd.getName()), new JavaOperation(mtd, paramTypes, ts.findType (mtd.getReturnType()), null));

/*
Copyright (c) 2008 Arno Haase, André Arnold.
All rights reserved. This program and the accompanying materials
are made available under the terms of the Eclipse Public License v1.0
which accompanies this distribution, and is available at
http://www.eclipse.org/legal/epl-v10.html

Contributors:
    Arno Haase - initial API and implementation
    André Arnold
 */
package org.eclipse.xtend.backend.types.java.internal;

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import org.eclipse.xtend.backend.common.BackendType;
import org.eclipse.xtend.backend.common.BackendTypesystem;
import org.eclipse.xtend.backend.common.QualifiedName;
import org.eclipse.xtend.backend.functions.java.internal.JavaBuiltinConverterFactory;
import org.eclipse.xtend.backend.types.AbstractType;
import org.eclipse.xtend.backend.util.ErrorHandler;

/**
 * 
 * @author Arno Haase (http://www.haase-consulting.com)
 * @author André Arnold
 */
public final class JavaBeansType extends AbstractType {
	private final Class<?> _javaClass;

	public JavaBeansType(Class<?> javaCls, BackendTypesystem ts) {
		super(javaCls.getName().replace(".", "::"), AbstractJavaBeansTypesystem.UNIQUE_REPRESENTATION_PREFIX
				+ javaCls.getName(), superTypes(javaCls, ts));

		_javaClass = javaCls;
	}

	private static BackendType[] superTypes(Class<?> javaCls, BackendTypesystem ts) {
		final List<Class<?>> resultRaw = new ArrayList<Class<?>>(Arrays.<Class<?>> asList(javaCls.getInterfaces()));
		Class<?> superClass = javaCls.getSuperclass();
		if (superClass != null)
			resultRaw.add(superClass);

		final List<BackendType> result = new ArrayList<BackendType>();
		for (Class<?> cls : resultRaw)
			result.add(ts.getRootTypesystem().findType(cls));

		return result.toArray(new BackendType[result.size()]);
	}

	/**
	 * the actual initialization is separated to deal with circular dependencies
	 * of operations and/or properties referring to this very same type.
	 */
	void init(BackendTypesystem ts) {
		for (Method mtd : _javaClass.getMethods()) {
			if (mtd.getDeclaringClass() == Object.class) // toString is added as
				// a syslib function
				continue;

			final List<BackendType> paramTypes = new ArrayList<BackendType>();

			paramTypes.add(this); // first parameter is the object on which the
			// method is called
			for (Class<?> cls : mtd.getParameterTypes()) {
				paramTypes.add(ts.getRootTypesystem().findType(cls));
			}

			register(new QualifiedName(mtd.getName()), new JavaOperation(mtd, paramTypes, null));
		}

		// static properties
		for (Field field : _javaClass.getFields()) {
			final int mod = field.getModifiers();
			if (Modifier.isPublic(mod) && Modifier.isStatic(mod) && Modifier.isFinal(mod)) {
				try {
					register(new JavaBeansStaticProperty(field, this, ts.getRootTypesystem().findType(field.getType()),
							JavaBuiltinConverterFactory.getConverter(field.getType())));
				}
				catch (Exception e) {
					ErrorHandler.handle(e);
				}
			}
		}

		// Java 5 enums
		final Object[] enumValues = _javaClass.getEnumConstants();
		if (enumValues != null) {
			for (Object o : enumValues) {
				final Enum<?> curEnum = (Enum<?>) o;
				register(new JavaBeansStaticProperty(this, ts.getRootTypesystem().findType(curEnum), curEnum.name(),
						curEnum));
			}
		}
	}

	@Override
	public Object create() {
		try {
			return _javaClass.newInstance();
		}
		catch (Exception e) {
			ErrorHandler.handle(e);
			return null; // to make the compiler happy - this is never executed
		}
	}

	@Override
	public String toString() {
		return "JavaBeansType[" + _javaClass.getName() + "]";
	}

	@Override
	public boolean equals(Object other) {
		if (other == null || !(other instanceof JavaBeansType))
			return false;

		return ((JavaBeansType) other)._javaClass.equals(_javaClass);
	}
}
public class JdtTypeImpl extends AbstractTypeImpl {

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

package org.eclipse.xtend.shared.ui.core.metamodel.jdt;

import java.util.HashSet;
import java.util.Iterator;
import java.util.Set;

import org.eclipse.internal.xtend.expression.parser.SyntaxConstants;
import org.eclipse.jdt.core.IField;
import org.eclipse.jdt.core.IMethod;
import org.eclipse.jdt.core.IType;
import org.eclipse.jdt.core.JavaModelException;
import org.eclipse.jdt.core.Signature;
import org.eclipse.xtend.shared.ui.internal.XtendLog;
import org.eclipse.xtend.typesystem.AbstractTypeImpl;
import org.eclipse.xtend.typesystem.Feature;
import org.eclipse.xtend.typesystem.Type;

public class JdtTypeImpl extends AbstractTypeImpl implements Type {
	private IType type;

	private Set<Type> superTypes = null;

	private final Feature[] features = null;

	private JdtTypeStrategy strategy = null;

	private JdtMetaModel metamodel = null;

	public JdtTypeImpl(final JdtMetaModel meta, final IType clazz, final String name, final JdtTypeStrategy strategy) {
		super(meta.getTypeSystem(), name);
		type = clazz;
		metamodel = meta;
		this.strategy = strategy;
	}

	public IType getJdtType() {
		if (!type.exists()) {
			// maybe the project has been closed or opend, so we need to recalculate the type
			try {
				type = metamodel.findType(type.getJavaProject(), type.getFullyQualifiedName());
			}
			catch (JavaModelException e) {
				// ignore, since caller will deal with not existing types and log an error
			}
		}
		return type;
	}

	@Override
	public Feature[] getContributedFeatures() {
		if (features == null) {
			try {
				final IMethod[] ms = type.getMethods();
				final Set<Feature> features = new HashSet<Feature>();
				for (int i = 0; i < ms.length; i++) {
					final IMethod method = ms[i];
					if (strategy.isGetter(method)) {
						final String sig = strategy.getPropertiesInnerType(method);
						Type type = null;
						if (sig != null) {
							type = metamodel.getTypeSystem().getListType(getTypeForSignature(sig));
						} else {
							type = getTypeForSignature(method.getReturnType());
						}
						if (type != null && !type.equals(metamodel.getTypeSystem().getVoidType())) {
							features.add(new JdtPropertyImpl(this, strategy.propertyName(method), type));
						} else if (type == null) {
							XtendLog.logInfo("Couldn't resolve return type of " + method.toString());
						}
					} else if (strategy.isOperation(method)) {
						final String[] paramSigns = method.getParameterTypes();
						final Type[] params = new Type[paramSigns.length];
						boolean unkownType = false;
						final Type rType = getTypeForSignature(method.getReturnType());
						if (rType == null) {
							unkownType = true;
						}
						for (int j = 0; !unkownType && j < paramSigns.length; j++) {
							params[j] = getTypeForSignature(paramSigns[j]);
							if (params[j] == null) {
								unkownType = true;
							}
						}
						if (!unkownType) {
							features.add(new JdtOperationImpl(this, method.getElementName(), rType, params));
						}
					}
				}

				// Collect constants as StaticProperty
				for (IField field : type.getFields()) {
					if (strategy.isConstant(field)) {
						Type type = getTypeForField(field);
						if (field.isEnumConstant()) {
							features.add(new JdtStaticPropertyImpl(this, strategy.propertyName(field), type, field.getElementName()));
						} else {
							features.add(new JdtStaticPropertyImpl(this, strategy.propertyName(field), type, field.getConstant()));
						}
					}
				}

				return features.toArray(new Feature[features.size()]);
			} catch (final Exception e) {
				XtendLog.logError(e);
				return new Feature[0];
			}
		}
		return features;
	}

	/**
	 * Returns the Xtend Type instance for an IField instance.
	 * 
	 * @param field
	 * @return
	 * @throws JavaModelException
	 * @throws IllegalArgumentException
	 */
	private Type getTypeForField(IField field) throws JavaModelException, IllegalArgumentException {
		Type type = null;
		if (field.isEnumConstant()) {
			type = metamodel.getTypeSystem().getTypeForName(field.getDeclaringType().getFullyQualifiedName().replaceAll("\\.", SyntaxConstants.NS_DELIM));
		} else {
			// it is possible to define a constant like this:
			// public static class MyClass {
			// public static final int MYCONST = '.';
			//
			// unfortunately this returns null for field.getConstant()
			// see org.eclipse.jdt.core.Signature
			if (field.getConstant() != null) {
				type = metamodel.getTypeSystem().getTypeForName(field.getConstant().getClass().getName().replaceAll("\\.", SyntaxConstants.NS_DELIM));
			} else if (Signature.getElementType(field.getTypeSignature()).matches("B|C|D|F|I|J|S|Z")) {
				XtendLog.logInfo("constant value for field " + field.getElementName() + " not resolvable");
			} else {
				String typeName = Signature.getElementType(field.getTypeSignature());
				type = metamodel.getTypeSystem().getTypeForName(typeName.replaceAll("\\.", SyntaxConstants.NS_DELIM));
			}
		}
		return type;
	}

	private Type getTypeForSignature(final String signature) {
		if (Signature.SIG_VOID.equals(signature))
			return metamodel.getTypeSystem().getVoidType();
		final String name = metamodel.getFullyQualifiedName(signature, type);
		if (name == null)
			return null;
		return metamodel.getTypeSystem().getTypeForName(name);
	}

	@Override
	public Set<? extends Type> getSuperTypes() {
		if (superTypes == null) {
			superTypes = new HashSet<Type>();
			try {
				final IType[] jdtSuperTypes = strategy.getSuperTypes(type);
				for (int i = 0; i < jdtSuperTypes.length; i++) {
					final IType type = jdtSuperTypes[i];
					final Type t = metamodel.getTypeForClass(type);
					if (t == null) {
						XtendLog.logInfo("Couldn't resolve type for " + type);
					} else {
						superTypes.add(t);
					}
				}
			} catch (final Exception e) {
				XtendLog.logError(e);
			}
			if (superTypes.isEmpty()) {
				superTypes.add(getTypeSystem().getObjectType());
			}
		}
		return superTypes;
	}

	public final Set<? extends Type> getAllSuperTypes() {
		final Set<Type> result = new HashSet<Type>(getSuperTypes());
		for (final Iterator<? extends Type> iter = getSuperTypes().iterator(); iter.hasNext();) {
			final Type element = iter.next();
			if (element instanceof JdtTypeImpl) {
				result.addAll(((JdtTypeImpl) element).getAllSuperTypes());
			}
		}
		return result;
	}

	public boolean isInstance(final Object o) {
		throw new UnsupportedOperationException();
	}

	@Override
	protected boolean internalIsAssignableFrom(final Type t) {
		if (t instanceof JdtTypeImpl) {
			try {
				return strategy.isAssignable(getJdtType(), ((JdtTypeImpl) t).getJdtType());
			} catch (final Exception e) {
				XtendLog.logError(e);
			}
		}
		return false;
	}

	public Object newInstance() {
		throw new UnsupportedOperationException();
	}

	@Override
	public boolean equals(final Object obj) {
		if (obj instanceof JdtTypeImpl) {
			final JdtTypeImpl t = (JdtTypeImpl) obj;
			return type.equals(t.type) && strategy.equals(t.strategy);
		}
		return super.equals(obj);
	}

	@Override
	public int hashCode() {
		return type.hashCode();
	}
}
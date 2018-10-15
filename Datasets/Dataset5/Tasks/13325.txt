public class JavaTypeImpl extends AbstractTypeImpl {

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

package org.eclipse.xtend.type.impl.java;

import java.lang.reflect.Modifier;
import java.util.HashSet;
import java.util.Set;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.eclipse.xtend.typesystem.AbstractTypeImpl;
import org.eclipse.xtend.typesystem.Feature;
import org.eclipse.xtend.typesystem.Type;

/**
 * @author Sven Efftinge
 * @author Arno Haase
 */
public class JavaTypeImpl extends AbstractTypeImpl implements Type {

    private final static Log log = LogFactory.getLog(JavaTypeImpl.class);

    private Class<?> clazz;

    private Set<Type> superTypes = null;

    private Feature[] features = null;

    private JavaTypeStrategy strategy = null;

    private JavaMetaModel metamodel = null;

    public JavaTypeImpl(final JavaMetaModel meta, final Class<?> clazz, final String name, final JavaTypeStrategy strategy) {
        super(meta.getTypeSystem(), name);
        this.clazz = clazz;
        metamodel = meta;
        this.strategy = strategy;
    }

    @Override
    public Feature[] getContributedFeatures() {
        if (features == null) {
            features = strategy.getFeatures(metamodel, clazz, this);
        }
        return features;
    }

    @SuppressWarnings("unchecked")
	@Override
    public Set<Type> getSuperTypes() {
        if (superTypes == null) {
            final Set<Type> result = new HashSet<Type>();
            if (clazz.getSuperclass() != null && !clazz.getSuperclass().equals(Object.class)) {
                final Type beanType = metamodel.builtinAwareGetTypeForClass(clazz.getSuperclass());
                if (beanType != null) {
                    result.add(beanType);
                }
            }
            final Class[] interfaces = clazz.getInterfaces();
            for (int i = 0; i < interfaces.length; i++) {
                final Type beanType = metamodel.builtinAwareGetTypeForClass(interfaces[i]);
                if (beanType != null) {
                    result.add(beanType);
                }
            }
            if (result.isEmpty()) {
                result.add(metamodel.getTypeSystem().getObjectType());
            }
            superTypes = result;
        }
        return superTypes;
    }

    public boolean isInstance(final Object o) {
        return clazz.isInstance(o);
    }

    @Override
    protected boolean internalIsAssignableFrom(final Type t) {
        if (t instanceof JavaTypeImpl)
            return clazz.isAssignableFrom(((JavaTypeImpl) t).clazz);
        return false;
    }

    public Object newInstance() {
        try {
            return clazz.newInstance();
        } catch (final Exception e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public boolean isAbstract() {
        try {
            return clazz.getConstructor(new Class[0]) == null || Modifier.isAbstract (clazz.getModifiers());
        } catch (final SecurityException e) {
            log.error(e.getMessage(), e);
        } catch (final NoSuchMethodException e) {
            log.error(e.getMessage(), e);
        }
        return true;
    }

}
if (cls == Long.class || cls == Long.TYPE || cls == Integer.TYPE || cls == Integer.class)

/**
 * <copyright> 
 *
 * Copyright (c) 2002-2007 itemis AG and others.
 * All rights reserved.   This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: 
 *   itemis AG - Initial API and implementation
 *
 * </copyright>
 *
 */
package org.eclipse.xpand3.analyzation.typesystem.builtin;

import java.io.IOException;
import java.io.InputStream;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.eclipse.emf.common.util.URI;
import org.eclipse.emf.ecore.EFactory;
import org.eclipse.emf.ecore.resource.Resource;
import org.eclipse.emf.ecore.resource.impl.ResourceSetImpl;
import org.eclipse.emf.ecore.xmi.impl.XMIResourceFactoryImpl;
import org.eclipse.xpand3.analyzation.TypeSystem;
import org.eclipse.xpand3.analyzation.TypeSystemFactory;
import org.eclipse.xpand3.staticTypesystem.AbstractTypeReference;
import org.eclipse.xpand3.staticTypesystem.DeclaredFunction;
import org.eclipse.xpand3.staticTypesystem.DeclaredType;
import org.eclipse.xpand3.staticTypesystem.Model;
import org.eclipse.xpand3.staticTypesystem.StaticTypesystemPackage;
import org.eclipse.xpand3.util.LoaderFactory;
import org.eclipse.xtend.backend.common.BackendType;
import org.eclipse.xtend.backend.common.Function;
import org.eclipse.xtend.backend.common.Property;
import org.eclipse.xtend.backend.common.StaticProperty;

/**
 * @author Sven Efftinge
 *
 */
public class BuiltinTypeSystem implements TypeSystem {
	private static Map<String, DeclaredType> types = new HashMap<String, DeclaredType>();
	static {
		Resource.Factory.Registry.INSTANCE.getExtensionToFactoryMap().put("xmi", new XMIResourceFactoryImpl());
		@SuppressWarnings("unused")
		EFactory factoryInstance = StaticTypesystemPackage.eINSTANCE.getEFactoryInstance();
		// TODO use classpath: URI
		InputStream resourceAsStream = LoaderFactory.getClassLoader(BuiltinTypeSystem.class).getResourceAsStream("built-in.xmi");
		Resource resource = new ResourceSetImpl().createResource(URI.createURI("classpath:/built-in.xmi"));
		try {
			resource.load(resourceAsStream, null);
			Model m = (Model) resource.getContents().get(0);
			for (DeclaredType dt : m.getDeclarations()) {
				types.put(dt.getName(), dt);
			}
		} catch (IOException e) {
			throw new RuntimeException(e);
		}
	}
	
	public DeclaredType getBuiltinTypeForJavaClass(Class<?> cls) {
		if (List.class.isAssignableFrom (cls))
            return types.get(LIST);
        if (Set.class.isAssignableFrom(cls))
        	return types.get(SET);
        if (Collection.class.isAssignableFrom(cls))
        	return types.get(COLLECTION);
        
        if (Map.class.isAssignableFrom(cls))
        	return types.get(MAP);
        
        if (CharSequence.class.isAssignableFrom(cls))
        	return types.get(STRING);
        
        if (cls == Boolean.class || cls == Boolean.TYPE)
        	return types.get(BOOLEAN);
        
        if (cls == Long.class || cls == Long.TYPE)
        	return types.get(INTEGER);
        if (cls == Double.class || cls == Double.TYPE)
        	return types.get(REAL);

        if (Function.class.isAssignableFrom(cls))
        	return types.get(FUNCTION);
        
        if (BackendType.class.isAssignableFrom(cls))
            return types.get(TYPE);
        if (Property.class.isAssignableFrom(cls))
        	return types.get(PROPERTY);
        if (StaticProperty.class.isAssignableFrom(cls))
        	return types.get(STATIC_PROPERTY);
        if (Object.class.equals(cls))
        	return types.get(OBJECT);
		return null;
	}

	/* (non-Javadoc)
	 * @see org.eclipse.xpand3.analyzation.TypeSystem#functionForName(java.lang.String, org.eclipse.xpand3.staticTypesystem.AbstractTypeReference[])
	 */
	public DeclaredFunction functionForName(String name,
			AbstractTypeReference... parameterTypes) {
		return null;
	}

	/* (non-Javadoc)
	 * @see org.eclipse.xpand3.analyzation.TypeSystem#setTypeSystemFactory(org.eclipse.xpand3.analyzation.TypeSystemFactory)
	 */
	public void setTypeSystemFactory(TypeSystemFactory tsf) {
	}

	/* (non-Javadoc)
	 * @see org.eclipse.xpand3.analyzation.TypeSystem#typeForName(java.lang.String)
	 */
	public DeclaredType typeForName(String name) {
		return types.get(name);
	}

}	
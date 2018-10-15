package org.eclipse.xpand3.analyzation;

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
package org.eclipse.xand3.analyzation;

import org.eclipse.xpand3.staticTypesystem.AbstractTypeReference;
import org.eclipse.xpand3.staticTypesystem.DeclaredFunction;
import org.eclipse.xpand3.staticTypesystem.DeclaredType;

/**
 * @author Sven Efftinge
 * 
 */
public interface DeclarationsContributor {
	/**
	 * used to construct the type system scoped by the imports
	 * @return
	 */
	String[] getReferencedContributors(); //TODO aliasing
	
	/**
	 * this method is invoked during setup of this contributor.
	 * @param the type system to be used for resolving type and function references.
	 */
	void setTypeSystem(TypeSystem ts);
	
	
	/**
	 * if this contributor has a type with the declared name, the respective DeclareTpye should be returned.
	 * This method is only invoked once per name, so caching is done by the framework
	 * @param name
	 * @return the declared type with the given name or null if there is no such type declared in this Resource.
	 */
	DeclaredType typeForName(String name);
	
	/**
	 * if this contributor has a type with the declared name, the respective DeclareTpye should be returned.
	 * This method is only invoked once per name.
	 * @param name
	 * @return
	 */
	DeclaredFunction functionForName(String name, AbstractTypeReference...parameterTypes);
}
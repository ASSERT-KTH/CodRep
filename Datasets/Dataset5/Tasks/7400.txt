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

import java.util.List;

import org.eclipse.xpand3.staticTypesystem.AbstractTypeReference;
import org.eclipse.xpand3.staticTypesystem.FunctionType;
import org.eclipse.xpand3.staticTypesystem.Type;
import org.eclipse.xpand3.staticTypesystem.WildcardType;
import org.eclipse.xtend.backend.common.BackendTypesystem;

/**
 * @author Sven Efftinge
 * 
 */
public interface TypeSystem {
	String OBJECT = "Object";
	String VOID = "Void";
	
	// Collection types
	String COLLECTION = "Collection";
	String SET = "Set";
	String LIST = "List";
	
	// Datatypes
	String BOOLEAN = "Boolean";
	String INTEGER = "Integer";
	String REAL = "Real";
	String STRING = "String";
	
	// reflection layer types
	String FEATURE = "Feature";
	String TYPE = "Type";
	String OPERATION = "Operation";
	String PROPERTY = "Property";
	String STATIC_PROPERTY = "StaticProperty";
	
	WildcardType wildCard(AbstractTypeReference...upperBounds);
	WildcardType wildCardWithLower(AbstractTypeReference...lowerBounds);
	
	Type typeForName(String name, AbstractTypeReference...typeArguments);
	
	FunctionType functionForNameAndParameterTypes(String name, AbstractTypeReference...parameterTypes);
	FunctionType functionForName(String name, List<AbstractTypeReference> parameterTypes, AbstractTypeReference...typeArguments);
	
}
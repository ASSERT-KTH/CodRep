if (dt != null) {

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
package org.eclipse.xpand3.analyzation.typesystem;

import java.util.Arrays;
import java.util.List;

import org.eclipse.xpand3.analyzation.DeclarationsContributor;
import org.eclipse.xpand3.analyzation.TypeSystem;
import org.eclipse.xpand3.staticTypesystem.AbstractTypeReference;
import org.eclipse.xpand3.staticTypesystem.DeclaredFunction;
import org.eclipse.xpand3.staticTypesystem.DeclaredType;
import org.eclipse.xpand3.staticTypesystem.FunctionType;
import org.eclipse.xpand3.staticTypesystem.Type;

/**
 * @author Sven Efftinge
 * 
 */
public class TypeSystemImpl extends AbstractTypeSystemImpl implements TypeSystem {


	private DeclarationsContributor contr = null;
	
	/**
	 * 
	 */
	public TypeSystemImpl(DeclarationsContributor contributor) {
		if (contributor==null)
			throw new NullPointerException("contributor was null");
		this.contr = contributor;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.xand3.analyzation.TypeSystem#typeForName(java.lang.String,
	 *      org.eclipse.xpand3.staticTypesystem.AbstractTypeReference[])
	 */
	public Type typeForName(String name, AbstractTypeReference... typeArguments) {
		DeclaredType dt = contr.typeForName(name);
		if (dt == null) {
			//TODO CACHING
			Type t = FACTORY.createType();
			t.setDeclaredType(dt);
			t.getActualTypeArguments().addAll(Arrays.asList(typeArguments));
			return t;
		}
		return null;
	}


	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.xand3.analyzation.TypeSystem#functionForName(java.lang.String,
	 *      java.util.List,
	 *      org.eclipse.xpand3.staticTypesystem.AbstractTypeReference[])
	 */
	public FunctionType functionForName(String name,
			List<AbstractTypeReference> parameterTypes,
			AbstractTypeReference... typeArguments) {
		DeclaredFunction func = contr.functionForName(name, parameterTypes.toArray(new AbstractTypeReference[parameterTypes.size()]));
		if (func == null) {
			//TODO CACHING
			FunctionType funcType = FACTORY.createFunctionType();
			funcType.setDeclaredFunction(func);
			funcType.getActualTypeArguments().addAll(Arrays.asList(typeArguments));
			return funcType;
		}
		return null;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.xand3.analyzation.TypeSystem#functionForNameAndParameterTypes(java.lang.String,
	 *      org.eclipse.xpand3.staticTypesystem.AbstractTypeReference[])
	 */
	public FunctionType functionForNameAndParameterTypes(String name,
			AbstractTypeReference... parameterTypes) {
		return functionForName(name, Arrays.asList(parameterTypes));
	}

}
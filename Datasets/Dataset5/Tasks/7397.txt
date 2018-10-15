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

import java.util.HashMap;

import org.eclipse.xpand3.staticTypesystem.AbstractTypeReference;

/**
 * @author Sven Efftinge
 * @author Bernd Kolb
 */
public interface AnalyzeContext {

	public final static String IMPLICIT_VARIABLE = "this";

	boolean hasThis();
	Var getThis();
	Var getVariable(String varName);
	AnalyzeContext cloneWith(Var var);
	
	public final static AnalyzeContext EMPTY_CTX = new AnalyzeContextImpl(); 
	
	class AnalyzeContextImpl implements AnalyzeContext {
		private HashMap<String, Var> scope = new HashMap<String, Var>();
		public AnalyzeContextImpl() {
		}
		/**
		 * 
		 */
		public AnalyzeContextImpl(AnalyzeContextImpl old) {
			scope.putAll(old.scope);
		}
		/* (non-Javadoc)
		 * @see org.eclipse.xand3.analyzation.AnalyzeContext#cloneWith(org.eclipse.xand3.analyzation.AnalyzeContext.Var)
		 */
		public AnalyzeContext cloneWith(Var var) {
			AnalyzeContextImpl newOne = new AnalyzeContextImpl(this);
			newOne.scope.put(var.name, var);
			return newOne;
		}

		/* (non-Javadoc)
		 * @see org.eclipse.xand3.analyzation.AnalyzeContext#getThis()
		 */
		public Var getThis() {
			return scope.get(IMPLICIT_VARIABLE);
		}

		/* (non-Javadoc)
		 * @see org.eclipse.xand3.analyzation.AnalyzeContext#getVariable(java.lang.String)
		 */
		public Var getVariable(String varName) {
			return scope.get(varName);
		}

		/* (non-Javadoc)
		 * @see org.eclipse.xand3.analyzation.AnalyzeContext#hasThis()
		 */
		public boolean hasThis() {
			return scope.containsKey(IMPLICIT_VARIABLE);
		}
		
	}


	public class Var {
		public Var(AbstractTypeReference value) {
			this(IMPLICIT_VARIABLE, value);
		}

		public Var(String name, AbstractTypeReference value) {
			this.name = name;
			this.value = value;
		}

		private final String name;
		private final AbstractTypeReference value;

		/**
		 * @return the name
		 */
		public String getName() {
			return name;
		}

		/**
		 * @return the value
		 */
		public AbstractTypeReference getValue() {
			return value;
		}
	}
}
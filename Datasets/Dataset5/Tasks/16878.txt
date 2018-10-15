public static String qualify(Identifier name) {

/**
 * <copyright> 
 *
 * Copyright (c) 2002-2007 Kolbware and others.
 * All rights reserved.   This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: 
 *   Kolbware, Bernd Kolb - Initial API and implementation
 *
 * </copyright>
 *
 */
package org.eclipse.xtend.middleend.internal.xpand3;

import org.eclipse.xpand3.Identifier;
import org.eclipse.xtend.backend.common.BackendType;
import org.eclipse.xtend.backend.common.StaticProperty;

/**
 * @author Bernd Kolb
 * 
 */
public class BackendTypeConverter {

	public BackendType convertToBackendType(Object ex) {
		throw new UnsupportedOperationException("Not yet implemented");
	}

	public StaticProperty getEnumLiteral(String value) {
		throw new UnsupportedOperationException("Not yet implemented");
	}

	public StaticProperty getEnumLiteral(Identifier name) {
		return getEnumLiteral(qualify(name));
	}

	private String qualify(Identifier name) {
		String value = name.getValue();
		if (name.getNext() != null) {
			value += SyntaxConstants.NS_DELIM + qualify(name.getNext());
		}
		return value;
	}

}
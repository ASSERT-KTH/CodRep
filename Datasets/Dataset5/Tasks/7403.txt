package org.eclipse.xpand3.ast;

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
package org.eclipse.xand3.ast;

import org.eclipse.xpand3.Identifier;

/**
 * @author Sven Efftinge
 *
 */
public class AstUtil {

	/**
	 * @param importedId
	 * @return
	 */
	public static String toString(Identifier id) {
		return id.getValue();
	}

}
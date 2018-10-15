import org.eclipse.ecf.core.identity.IIdentifiable;

/****************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Composent, Inc. - initial API and implementation
 *****************************************************************************/
package org.eclipse.ecf.core.user;

import java.io.Serializable;
import java.util.Map;
import org.eclipse.core.runtime.IAdaptable;
import org.eclipse.ecf.core.IIdentifiable;

/**
 * Interface for arbitrary ECF system user. Instances represent a user within
 * ECF providers and/or clients.
 */
public interface IUser extends IIdentifiable, Serializable, IAdaptable {
	/**
	 * Get basic name for user
	 */
	public String getName();

	/**
	 * Get map of properties associated with this user.
	 * 
	 * @return Map
	 */
	public Map getProperties();
}
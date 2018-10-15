public IRosterItem getParent();

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
package org.eclipse.ecf.presence.roster;

import org.eclipse.core.runtime.IAdaptable;

public interface IRosterItem extends IAdaptable {
	/**
	 * Return name of item.
	 * 
	 * @return String name of item. May return <code>null</code>.
	 */
	public String getName();

	/**
	 * Return parent of item
	 * 
	 * @return Object parent of roster item. May be <code>null</code>.
	 */
	public Object getParent();
}
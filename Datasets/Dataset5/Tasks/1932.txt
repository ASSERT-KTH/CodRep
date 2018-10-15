package org.eclipse.ecf.remoteservice.client;

/*******************************************************************************
* Copyright (c) 2009 Composent, Inc. and others. All rights reserved. This
* program and the accompanying materials are made available under the terms of
* the Eclipse Public License v1.0 which accompanies this distribution, and is
* available at http://www.eclipse.org/legal/epl-v10.html
*
* Contributors:
*   Composent, Inc. - initial API and implementation
******************************************************************************/
package org.eclipse.ecf.remoteservice;

/**
 * A representation of a remote call parameter, with a name and value.
 * 
 * @since 3.3
 */
public interface IRemoteCallParameter {

	/**
	 * Get the name of the remote call parameter.  Should not be <code>null</code>.
	 * @return String name for the parameter.  Should not be <code>null</code>.
	 */
	public String getName();

	/**
	 * Get the value associated with this remote call parameter.  May be <code>null</code>.
	 * @return Object value associated with the name given above.
	 */
	public Object getValue();

}
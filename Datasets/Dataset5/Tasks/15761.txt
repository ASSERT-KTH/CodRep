public interface IRemoteServiceContainerAdapter {

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

package org.eclipse.ecf.remoteservice;

import java.util.Dictionary;

import org.eclipse.ecf.core.identity.ID;

/**
 * Container for remote service access.  This is the entry point innterface for accessing 
 * remote services through ECF containers.  
 *
 */
public interface IRemoteServiceContainer {

	/**
	 * Add listener for remote service registration/unregistration for this
	 * container
	 * @param listener notified of service registration/unregistration events
	 */
	public void addRemoteServiceListener(IRemoteServiceListener listener);
	/**
	 * Remove remote service registration/unregistration listener for this
	 * container.
	 * @param listener
	 */
	public void removeRemoteServiceListener(IRemoteServiceListener listener);

	/**
	 * Register a new remote service.  This method is to be called by the service
	 * server...i.e. the client that wishes to make available a service to other
	 * client within this container.
	 * 
	 * @param clazzes the interface classes that the service exposes to remote 
	 * clients.  Must not be null and must not be an empty array.
	 * @param service the service object itself.  This object must implement
	 * all of the classes specified by the first parameter
	 * @param properties to be associated with service
	 * @return IRemoteServiceRegistration the service registration.  Will not return null.
	 */
	public IRemoteServiceRegistration registerRemoteService(String[] clazzes,
			Object service, Dictionary properties);
	/**
	 * Get IRemoteServiceReference for desired service
	 * 
	 * @param idFilter an array of ID instances that will restrict the search for matching 
	 * classes to those from remote containers with specified ID.  If null, all remote containers
	 * will be considered in search for matching IRemoteServiceReference instances
	 * 
	 * @param clazz the fully qualified name of the interface class that describes the desired service
	 * @param filter 
	 * @return IRemoteServiceReference [] the matching IRemoteServiceReferences
	 */
	public IRemoteServiceReference[] getRemoteServiceReferences(ID[] idFilter,
			String clazz, String filter);

	/**
	 * Get remote service for given IRemoteServiceReference.  
	 * 
	 * @param reference the IRemoteServiceReference for the desired service
	 * @return IRemoteService representing the remote service. If remote service no longer exists
	 * for reference, then null is returned.
	 */
	public IRemoteService getRemoteService(IRemoteServiceReference reference);

	/**
	 * Unget IRemoteServiceReference
	 * 
	 * @param reference the IRemoteServiceReference to unget
	 * @return true if unget successful, false if not
	 */
	public boolean ungetRemoteService(IRemoteServiceReference reference);

}
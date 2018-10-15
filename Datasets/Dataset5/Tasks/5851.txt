public ContainerTypeDescription[] getDescriptionsForContainerAdapter(Class containerAdapter);

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.core;

import java.util.List;

/**
 * Container factory contract {@link ContainerFactory} for default
 * implementation.
 */
public interface IContainerFactory {
	/**
	 * Add a ContainerTypeDescription to the set of known ContainerDescriptions.
	 * 
	 * @param description
	 *            the ContainerTypeDescription to add to this factory. Must not
	 *            be null.
	 * @return ContainerTypeDescription the old description of the same name,
	 *         null if none found
	 */
	public ContainerTypeDescription addDescription(ContainerTypeDescription description);

	/**
	 * Get a collection of the ContainerDescriptions currently known to this
	 * factory. This allows clients to query the factory to determine what if
	 * any other ContainerDescriptions are currently registered with the
	 * factory, and if so, what they are.
	 * 
	 * @return List of ContainerTypeDescription instances
	 */
	public List /* ContainerTypeDescription */ getDescriptions();

	/**
	 * Check to see if a given named description is already contained by this
	 * factory
	 * 
	 * @param description
	 *            the ContainerTypeDescription to look for
	 * @return true if description is already known to factory, false otherwise
	 */
	public boolean containsDescription(ContainerTypeDescription description);

	/**
	 * Get the known ContainerTypeDescription given it's name.
	 * 
	 * @param name
	 *            the name to use as key to find ContainerTypeDescription
	 * @return ContainerTypeDescription found. Null if not found.
	 */
	public ContainerTypeDescription getDescriptionByName(String name);

	/**
	 * Make IContainer instance. Given a ContainerTypeDescription object, a
	 * String [] of argument types, and an Object [] of parameters, this method
	 * will
	 * <p>
	 * <ul>
	 * <li>lookup the known ContainerDescriptions to find one of matching name</li>
	 * <li>if found, will retrieve or create an IContainerInstantiator for that
	 * description</li>
	 * <li>Call the IContainerInstantiator.createInstance method to return an
	 * instance of IContainer</li>
	 * </ul>
	 * 
	 * @param description
	 *            the ContainerTypeDescription to use to create the instance
	 * @param parameters
	 *            an Object [] of parameters passed to the createInstance method
	 *            of the IContainerInstantiator
	 * @return a valid instance of IContainer
	 * @throws ContainerCreateException
	 */
	public IContainer createContainer(ContainerTypeDescription description,
			Object[] parameters) throws ContainerCreateException;

	/**
	 * Make IContainer instance. Given a ContainerTypeDescription name, this
	 * method will
	 * <p>
	 * <ul>
	 * <li>lookup the known ContainerDescriptions to find one of matching name</li>
	 * <li>if found, will retrieve or create an IContainerInstantiator for that
	 * description</li>
	 * <li>Call the IContainerInstantiator.createInstance method to return an
	 * instance of IContainer</li>
	 * </ul>
	 * 
	 * @param descriptionName
	 *            the ContainerTypeDescription name to lookup
	 * @return a valid instance of IContainer
	 * @throws ContainerCreateException
	 */
	public IContainer createContainer(String descriptionName)
			throws ContainerCreateException;

	/**
	 * Make IContainer instance. Given a ContainerTypeDescription name, this
	 * method will
	 * <p>
	 * <ul>
	 * <li>lookup the known ContainerDescriptions to find one of matching name</li>
	 * <li>if found, will retrieve or create an IContainerInstantiator for that
	 * description</li>
	 * <li>Call the IContainerInstantiator.createInstance method to return an
	 * instance of IContainer</li>
	 * </ul>
	 * 
	 * @param descriptionName
	 *            the ContainerTypeDescription name to lookup
	 * @param parameters
	 *            the Object [] of parameters passed to the
	 *            IContainerInstantiator.createInstance method
	 * @return a valid instance of IContainer
	 * @throws ContainerCreateException
	 */
	public IContainer createContainer(String descriptionName, Object[] parameters)
			throws ContainerCreateException;

	/**
	 * Remove given description from set known to this factory.
	 * 
	 * @param description
	 *            the ContainerTypeDescription to remove
	 * @return the removed ContainerTypeDescription, null if nothing removed
	 */
	public ContainerTypeDescription removeDescription(
			ContainerTypeDescription description);
	
	/**
	 * Get container type descriptions that support the given containerAdapter
	 * 
	 * @param containerAdapter the container adapter.  Must not be null.
	 * @return ContainerTypeDescription[] of descriptions that support the given container adapter.  If no 
	 * ContainerTypeDescriptions found that support the given adapter, an empty array will be returned.
	 */
	public ContainerTypeDescription[] getDescriptionsForAdapter(Class containerAdapter);
	
}
 No newline at end of file
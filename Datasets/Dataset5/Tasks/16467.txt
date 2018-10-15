//assertTrue(containers.length == 1);

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

package org.eclipse.ecf.tests.core;

import org.eclipse.ecf.core.AbstractContainer;
import org.eclipse.ecf.core.ContainerConnectException;
import org.eclipse.ecf.core.ContainerCreateException;
import org.eclipse.ecf.core.ContainerTypeDescription;
import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.core.IContainerManager;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDCreateException;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.ecf.core.provider.IContainerInstantiator;
import org.eclipse.ecf.core.security.IConnectContext;
import org.eclipse.ecf.internal.tests.Activator;

public class ContainerManagerServiceTest extends ContainerFactoryServiceAbstractTestCase {

	protected static final String CONTAINER_TYPE_NAME = ContainerManagerServiceTest.class.getName();
	
	protected IContainerManager containerManager = null;
	
	protected IContainer containers = null;
	
	protected IContainer[] createContainers(int length) throws Exception {
		IContainer [] result = new IContainer[length];
		for(int i=0; i < length; i++) {
			result[i] = Activator.getDefault().getContainerFactory().createContainer(CONTAINER_TYPE_NAME);
		}
		return result;
	}
	
	/* (non-Javadoc)
	 * @see org.eclipse.ecf.tests.core.ContainerFactoryAbstractTestCase#setUp()
	 */
	protected void setUp() throws Exception {
		super.setUp();
		getFixture().addDescription(createContainerTypeDescription());
		containerManager = Activator.getDefault().getContainerManager();
	}
	
	/* (non-Javadoc)
	 * @see org.eclipse.ecf.tests.core.ContainerFactoryAbstractTestCase#tearDown()
	 */
	protected void tearDown() throws Exception {
		getFixture().removeDescription(createContainerTypeDescription());
		containerManager = null;
		containers = null;
		super.tearDown();
	}
	
	protected ContainerTypeDescription createContainerTypeDescription() {
		return new ContainerTypeDescription(CONTAINER_TYPE_NAME,
				new IContainerInstantiator() {
					public IContainer createInstance(
							ContainerTypeDescription description,
							Object[] parameters)
							throws ContainerCreateException {
						return new AbstractContainer() {
							
							protected ID id = null;
							
							public void connect(ID targetID,
									IConnectContext connectContext)
									throws ContainerConnectException {
							}

							public void disconnect() {
							}

							public Namespace getConnectNamespace() {
								return null;
							}

							public ID getConnectedID() {
								return null;
							}

							public ID getID() {
								if (id == null) {
									try {
										id = IDFactory.getDefault().createGUID();
									} catch (IDCreateException e) {
										// TODO Auto-generated catch block
										e.printStackTrace();
									}
								}
								return id;
							}

						};
					}

					public String[] getSupportedAdapterTypes(
							ContainerTypeDescription description) {
						return new String[] { "one" };
					}

					public Class[][] getSupportedParameterTypes(
							ContainerTypeDescription description) {
						return new Class[][] { { String.class , Class.class }};
					}
				}, DESCRIPTION);
	}
	
	public void testGetContainerManager() throws Exception {
		assertNotNull(containerManager);
	}
	
	public void testGetContainersOne() throws Exception {
		IContainer[] c = createContainers(1);
		assertNotNull(c);
		IContainer [] containers = containerManager.getAllContainers();
		assertNotNull(containers);
		assertTrue(containers.length == 1);
	}
	
	public void testGetContainerOne() throws Exception {
		IContainer[] c = createContainers(1);
		assertNotNull(c);
		IContainer container = containerManager.getContainer(c[0].getID());
		assertNotNull(container);
		assertTrue(container.getID().equals(c[0].getID()));
	}
	
	public void testGetContainerN() throws Exception {
		IContainer[] c = createContainers(10);
		assertNotNull(c);
		for(int i=0; i < 10; i++) {
			IContainer container = containerManager.getContainer(c[i].getID());
			assertNotNull(container);
			assertTrue(container.getID().equals(c[i].getID()));
		}
	}
	
	public void testHasContainerN() throws Exception {
		IContainer[] c = createContainers(10);
		assertNotNull(c);
		for(int i=0; i < 10; i++) {
			assertTrue(containerManager.hasContainer(c[i].getID()));
		}
	}

}
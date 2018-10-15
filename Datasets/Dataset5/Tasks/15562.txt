protected static final String BASE_CONTAINER_TYPE_NAME = "ecf.base";

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
import org.eclipse.ecf.core.ContainerFactory;
import org.eclipse.ecf.core.ContainerTypeDescription;
import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.ecf.core.provider.IContainerInstantiator;
import org.eclipse.ecf.core.security.IConnectContext;

public class ContainerFactoryServiceCreateTest extends ContainerFactoryServiceAbstractTestCase {

	protected static final String CONTAINER_TYPE_NAME = ContainerFactoryServiceCreateTest.class.getName();

	protected static final String BASE_CONTAINER_TYPE_NAME = "ecf.root";

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.tests.core.ContainerFactoryAbstractTestCase#setUp()
	 */
	protected void setUp() throws Exception {
		super.setUp();
		getFixture().addDescription(createContainerTypeDescription());
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.tests.core.ContainerFactoryAbstractTestCase#tearDown()
	 */
	protected void tearDown() throws Exception {
		getFixture().removeDescription(createContainerTypeDescription());
		super.tearDown();
	}

	protected ContainerTypeDescription createContainerTypeDescription() {
		return new ContainerTypeDescription(CONTAINER_TYPE_NAME, new IContainerInstantiator() {
			public IContainer createInstance(ContainerTypeDescription description, Object[] parameters) throws ContainerCreateException {
				return new AbstractContainer() {
					public void connect(ID targetID, IConnectContext connectContext) throws ContainerConnectException {
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
						return null;
					}

				};
			}

			public String[] getSupportedAdapterTypes(ContainerTypeDescription description) {
				return new String[] {"one"};
			}

			public Class[][] getSupportedParameterTypes(ContainerTypeDescription description) {
				return new Class[][] {{String.class, Class.class}};
			}
		}, DESCRIPTION);
	}

	public void testCreateContainer0() throws Exception {
		final IContainer container = ContainerFactory.getDefault().createContainer();
		assertNotNull(container);
	}

	public void testCreateContainer1() throws Exception {
		final IContainer container = ContainerFactory.getDefault().createContainer(CONTAINER_TYPE_NAME);
		assertNotNull(container);
	}

	public void testCreateContainer2() throws Exception {
		final IContainer container = ContainerFactory.getDefault().createContainer(CONTAINER_TYPE_NAME, null);
		assertNotNull(container);
	}

	public void testCreateContainer3() throws Exception {
		final ContainerTypeDescription desc = ContainerFactory.getDefault().getDescriptionByName(CONTAINER_TYPE_NAME);
		assertNotNull(desc);
		final IContainer container = ContainerFactory.getDefault().createContainer(desc, null);
		assertNotNull(container);
	}

	public void testCreateContainer4() throws Exception {
		try {
			ContainerFactory.getDefault().createContainer((String) null, null);
			fail();
		} catch (final ContainerCreateException e) {
		}
	}

	public void testCreateContainer5() throws Exception {
		try {
			ContainerFactory.getDefault().createContainer((ContainerTypeDescription) null, null);
			fail();
		} catch (final ContainerCreateException e) {
		}
	}

	public void testCreateBaseContainer() throws Exception {
		final IContainer base = ContainerFactory.getDefault().createContainer();
		assertNotNull(base);
	}

	public void testCreateBaseContainer0() throws Exception {
		final ContainerTypeDescription desc = ContainerFactory.getDefault().getDescriptionByName(BASE_CONTAINER_TYPE_NAME);
		assertNotNull(desc);
		final IContainer base = ContainerFactory.getDefault().createContainer(desc, new Object[] {IDFactory.getDefault().createGUID()});
		assertNotNull(base);
	}

	public void testCreateBaseContainer1() throws Exception {
		final ContainerTypeDescription desc = ContainerFactory.getDefault().getDescriptionByName(BASE_CONTAINER_TYPE_NAME);
		assertNotNull(desc);
		final IContainer base = ContainerFactory.getDefault().createContainer(desc, new Object[] {IDFactory.getDefault().createGUID().getName()});
		assertNotNull(base);
	}

	public void testContainerTypeDescriptionGetName() {
		final ContainerTypeDescription desc = ContainerFactory.getDefault().getDescriptionByName(CONTAINER_TYPE_NAME);
		assertTrue(desc.getName().equals(CONTAINER_TYPE_NAME));
	}

	public void testContainerTypeDescriptionGetDescription() {
		final ContainerTypeDescription desc = ContainerFactory.getDefault().getDescriptionByName(CONTAINER_TYPE_NAME);
		assertTrue(desc.getDescription().equals(DESCRIPTION));
	}

	public void testContainerTypeDescriptionGetSupportedAdapterTypes() {
		final ContainerTypeDescription desc = ContainerFactory.getDefault().getDescriptionByName(CONTAINER_TYPE_NAME);
		final String[] adapterTypes = desc.getSupportedAdapterTypes();
		assertTrue(adapterTypes.length == 1);
		assertTrue(adapterTypes[0] == "one");
	}

	public void testContainerTypeDescriptionGetSupportedParemeterTypes() {
		final ContainerTypeDescription desc = ContainerFactory.getDefault().getDescriptionByName(CONTAINER_TYPE_NAME);
		final Class[][] parameterTypes = desc.getSupportedParameterTypes();
		assertTrue(parameterTypes.length == 1);
		assertTrue(parameterTypes[0].length == 2);
		assertTrue(parameterTypes[0][0].equals(String.class));
		assertTrue(parameterTypes[0][1].equals(Class.class));

	}

}
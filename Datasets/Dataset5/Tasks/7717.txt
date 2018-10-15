public class R_OSGiServicePublicationTest extends AbstractServicePublicationTest {

/****************************************************************************
 * Copyright (c) 2009 Jan S. Rellermeyer and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Jan S. Rellermeyer - initial API and implementation
 *****************************************************************************/
package org.eclipse.ecf.tests.osgi.services.distribution.r_osgi;


import org.eclipse.ecf.core.ContainerFactory;
import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.tests.osgi.services.distribution.AbstractServicePublicationTest;
import org.eclipse.ecf.tests.osgi.services.distribution.TestServiceInterface1;

public class ServicePublicationTest extends AbstractServicePublicationTest {

	protected IContainer createContainer() throws Exception {
		final ID containerID = IDFactory.getDefault().createStringID(
				"r-osgi://localhost:9278");
		return ContainerFactory.getDefault().createContainer("ecf.r_osgi.peer",
				new Object[] { containerID });
	}

	protected String[] createInterfaces() throws Exception {
		return new String[] { TestServiceInterface1.class.getName() };
	}

}
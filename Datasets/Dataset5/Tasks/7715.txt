public class GenericServicePublicationTest extends AbstractServicePublicationTest {

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
package org.eclipse.ecf.tests.osgi.services.distribution.generic;


import org.eclipse.ecf.core.ContainerFactory;
import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.tests.osgi.services.distribution.AbstractServicePublicationTest;
import org.eclipse.ecf.tests.osgi.services.distribution.TestServiceInterface1;

public class ServicePublicationTest extends AbstractServicePublicationTest {

	protected IContainer createContainer() throws Exception {
		return ContainerFactory.getDefault().createContainer("ecf.generic.client");
	}

	protected String[] createInterfaces() throws Exception {
		return new String[] { TestServiceInterface1.class.getName() };
	}

}
container = getContainerFactory().createContainer(Generic.CONSUMER_CONTAINER_TYPE);

/*******************************************************************************
* Copyright (c) 2010 Composent, Inc. and others. All rights reserved. This
* program and the accompanying materials are made available under the terms of
* the Eclipse Public License v1.0 which accompanies this distribution, and is
* available at http://www.eclipse.org/legal/epl-v10.html
*
* Contributors:
*   Composent, Inc. - initial API and implementation
******************************************************************************/
package org.eclipse.ecf.tests.remoteservice.generic;

import org.eclipse.ecf.remoteservice.IRemoteServiceContainerAdapter;
import org.eclipse.ecf.tests.remoteservice.AbstractLocalRemoteServiceTest;

public class GenericLocalRemoteServiceTest extends
		AbstractLocalRemoteServiceTest {

	protected void setUp() throws Exception {
		super.setUp();
		container = getContainerFactory().createContainer(Generic.HOST_CONTAINER_TYPE);
		containerAdapter = (IRemoteServiceContainerAdapter) container.getAdapter(IRemoteServiceContainerAdapter.class);
	}
	
	protected void tearDown() throws Exception {
		container.disconnect();
		container.dispose();
		getContainerManager().removeAllContainers();
		super.tearDown();
	}
}
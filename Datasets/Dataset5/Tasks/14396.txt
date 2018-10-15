protected String getServerContainerTypeName() {

/*******************************************************************************
* Copyright (c) 2009 EclipseSource and others. All rights reserved. This
* program and the accompanying materials are made available under the terms of
* the Eclipse Public License v1.0 which accompanies this distribution, and is
* available at http://www.eclipse.org/legal/epl-v10.html
*
* Contributors:
*   EclipseSource - initial API and implementation
******************************************************************************/
package org.eclipse.ecf.tests.osgi.services.distribution.generic;


import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.tests.osgi.services.distribution.AbstractRemoteServiceRegisterTest;

public class GenericRemoteServiceRegisterTest extends AbstractRemoteServiceRegisterTest {

	protected String getServerContainerName() {
		return "ecf.generic.server";
	}

	protected String getClientContainerName() {
		return "ecf.generic.client";
	}

	protected ID getServerCreateID() {
		return IDFactory.getDefault().createStringID("ecftcp://localhost:3282/server");
	}
}
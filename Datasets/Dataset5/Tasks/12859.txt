props.put(Constants.SERVICE_CONTAINER_ID, serverContainer.getID());

/*******************************************************************************
* Copyright (c) 2009 EclipseSource and others. All rights reserved. This
* program and the accompanying materials are made available under the terms of
* the Eclipse Public License v1.0 which accompanies this distribution, and is
* available at http://www.eclipse.org/legal/epl-v10.html
*
* Contributors:
*   EclipseSource - initial API and implementation
******************************************************************************/
package org.eclipse.ecf.tests.osgi.services.distribution;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Properties;

import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.osgi.services.distribution.ServiceConstants;
import org.eclipse.ecf.remoteservice.Constants;
import org.eclipse.ecf.tests.remoteservice.IConcatService;
import org.osgi.framework.BundleContext;
import org.osgi.framework.ServiceRegistration;


public class RegisterTest extends AbstractDistributionTest implements ServiceConstants {

	List /* ServiceRegistration */ registrations = new ArrayList();
	
	/*
	 * (non-Javadoc)
	 * 
	 * @see junit.framework.TestCase#setUp()
	 */
	protected void setUp() throws Exception {
		super.setUp();
		setClientCount(1);
		createServerAndClients();
		connectClients();
	}

	
	protected void tearDown() throws Exception {
		super.tearDown();
		for(Iterator i=registrations.iterator(); i.hasNext(); ) {
			ServiceRegistration reg = (ServiceRegistration) i.next();
			reg.unregister();
		}
		cleanUpServerAndClients();
	}

	protected String getClientContainerName() {
		return "ecf.generic.client";
	}
	
	protected void registerConcatService(Properties props) throws Exception {
		BundleContext bc = Activator.getDefault().getContext();
		registrations.add(bc.registerService(new String[] { IConcatService.class.getName() }, createService(), props));
	}
	
	public void testRegisterAllRSContainers() throws Exception {
		Properties props = new Properties();
		props.put(OSGI_REMOTE_INTERFACES, new String[] {OSGI_REMOTE_INTERFACES_WILDCARD});
		props.put(OSGI_REMOTE_CONFIGURATION_TYPE,new String[] { ECF_REMOTE_CONFIGURATION_TYPE });
		registerConcatService(props);
	}
	
	public void testRegisterServerContainer() throws Exception {
		Properties props = new Properties();
		props.put(OSGI_REMOTE_INTERFACES, new String[] {OSGI_REMOTE_INTERFACES_WILDCARD});
		props.put(OSGI_REMOTE_CONFIGURATION_TYPE,new String[] { ECF_REMOTE_CONFIGURATION_TYPE });
		IContainer serverContainer = getServer();
		props.put(Constants.REMOTE_SERVICE_CONTAINER_ID, serverContainer.getID());
		registerConcatService(props);
	}

}
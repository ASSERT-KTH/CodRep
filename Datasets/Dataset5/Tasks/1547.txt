public abstract class AbstractServiceRegisterListenerTest extends AbstractRemoteServiceAccessTest {

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

import org.eclipse.ecf.osgi.services.discovery.IRemoteServiceEndpointDescription;
import org.eclipse.ecf.osgi.services.distribution.IHostDistributionListener;
import org.eclipse.ecf.osgi.services.distribution.IProxyDistributionListener;
import org.eclipse.ecf.remoteservice.IRemoteServiceContainer;
import org.eclipse.ecf.remoteservice.IRemoteServiceReference;
import org.eclipse.ecf.remoteservice.IRemoteServiceRegistration;
import org.eclipse.ecf.tests.internal.osgi.services.distribution.Activator;
import org.osgi.framework.ServiceReference;
import org.osgi.framework.ServiceRegistration;

public abstract class AbstractServiceRegisterListenerTest extends AbstractServiceRegisterTest {

	ServiceRegistration hostDistributionListenerRegistration;
	ServiceRegistration proxyDistributionListenerRegistration;
	
	protected IHostDistributionListener createHostDistributionListener() {
		return new IHostDistributionListener() {

			public void registered(ServiceReference serviceReference,
					IRemoteServiceContainer remoteServiceContainer, IRemoteServiceRegistration remoteRegistration) {
				System.out.println("hostRegistered\n\tserviceReference="+serviceReference+"\n\tremoteServiceContainer="+remoteServiceContainer+"\n\tremoteRegistration="+remoteRegistration);
			}

			public void unregistered(ServiceReference serviceReference, IRemoteServiceRegistration remoteRegistration) {
				System.out.println("hostUnregistered\n\tserviceReference="+serviceReference+"\n\tremoteRegistration="+remoteRegistration);
			}
			
		};
	}

	protected IProxyDistributionListener createProxyDistributionListener() {
		return new IProxyDistributionListener() {

			public void registered(
					IRemoteServiceEndpointDescription endpointDescription,
					IRemoteServiceContainer remoteServiceContainer,
					IRemoteServiceReference remoteServiceReference,
					ServiceRegistration proxyServiceRegistration) {
				System.out.println("proxyRegistered\n\tendpointDescription="+endpointDescription+"\n\tremoteServiceContainer="+remoteServiceContainer+"\n\tremoteServiceReference="+remoteServiceReference+"\n\tproxyServiceRegistration="+proxyServiceRegistration);		
			}

			public void retrievingRemoteServiceReferences(
					IRemoteServiceEndpointDescription endpointDescription,
					IRemoteServiceContainer remoteServiceContainer) {
				System.out.println("proxyRetrievingRemoteServiceReferences\n\tendpointDescription="+endpointDescription+"\n\tremoteServiceContainer="+remoteServiceContainer);
			}

			public void registering(
					IRemoteServiceEndpointDescription endpointDescription,
					IRemoteServiceContainer remoteServiceContainer,
					IRemoteServiceReference remoteServiceReference) {
				System.out.println("proxyRegistering\n\tendpointDescription="+endpointDescription+"\n\tremoteServiceContainer="+remoteServiceContainer+"\n\tremoteServiceReference="+remoteServiceReference);		
			}

			public void unregistered(
					IRemoteServiceEndpointDescription endpointDescription,
					ServiceRegistration proxyServiceRegistration) {
				System.out.println("proxyUnregistered\n\tendpointDescription="+endpointDescription+"\n\tproxyServiceRegistration="+proxyServiceRegistration);		
			}
			
		};
	}

	protected void setUp() throws Exception {
		// Register listeners
		hostDistributionListenerRegistration = Activator.getDefault().getContext().registerService(IHostDistributionListener.class.getName(), createHostDistributionListener(), null);
		proxyDistributionListenerRegistration = Activator.getDefault().getContext().registerService(IProxyDistributionListener.class.getName(), createProxyDistributionListener(), null);
		super.setUp();
	}
	
	protected void tearDown() throws Exception {
		super.tearDown();
		hostDistributionListenerRegistration.unregister();
		proxyDistributionListenerRegistration.unregister();
	}
}
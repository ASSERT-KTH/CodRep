st.open(true);

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

import java.util.Dictionary;
import java.util.Enumeration;
import java.util.Properties;

import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.util.Trace;
import org.eclipse.ecf.osgi.services.discovery.RemoteServicePublication;
import org.eclipse.ecf.osgi.services.distribution.IDistributionConstants;
import org.eclipse.ecf.remoteservice.IRemoteService;
import org.eclipse.ecf.remoteservice.IRemoteServiceContainerAdapter;
import org.eclipse.ecf.remoteservice.IRemoteServiceListener;
import org.eclipse.ecf.remoteservice.IRemoteServiceProxy;
import org.eclipse.ecf.remoteservice.IRemoteServiceReference;
import org.eclipse.ecf.remoteservice.IRemoteServiceRegistration;
import org.eclipse.ecf.remoteservice.events.IRemoteServiceEvent;
import org.eclipse.ecf.tests.ContainerAbstractTestCase;
import org.eclipse.ecf.tests.internal.osgi.services.distribution.Activator;
import org.eclipse.ecf.tests.remoteservice.IConcatService;
import org.osgi.framework.BundleContext;
import org.osgi.framework.InvalidSyntaxException;
import org.osgi.framework.ServiceReference;
import org.osgi.framework.ServiceRegistration;
import org.osgi.util.tracker.ServiceTracker;
import org.osgi.util.tracker.ServiceTrackerCustomizer;

public abstract class AbstractDistributionTest extends
		ContainerAbstractTestCase implements IDistributionConstants,
		RemoteServicePublication {

	protected IRemoteServiceContainerAdapter[] adapters = null;

	/*
	 * (non-Javadoc)
	 * 
	 * @see
	 * org.eclipse.ecf.tests.ContainerAbstractTestCase#getClientContainerName()
	 */
	protected abstract String getClientContainerName();

	protected void tearDown() throws Exception {
		super.tearDown();
		if (adapters != null) {
			for (int i = 0; i < adapters.length; i++) {
				adapters[i] = null;
			}
			adapters = null;
		}
	}

	protected void setClientCount(int count) {
		super.setClientCount(count);
		adapters = new IRemoteServiceContainerAdapter[count];
	}

	protected void setupRemoteServiceAdapters() throws Exception {
		final int clientCount = getClientCount();
		for (int i = 0; i < clientCount; i++) {
			adapters[i] = (IRemoteServiceContainerAdapter) getClients()[i]
					.getAdapter(IRemoteServiceContainerAdapter.class);
		}
	}

	protected BundleContext getContext() {
		return Activator.getDefault().getContext();
	}

	protected IRemoteServiceContainerAdapter[] getRemoteServiceAdapters() {
		return adapters;
	}

	protected IRemoteServiceListener createRemoteServiceListener(
			final boolean server) {
		return new IRemoteServiceListener() {
			public void handleServiceEvent(IRemoteServiceEvent event) {
				System.out.println((server ? "server" : "client")
						+ "handleServiceEvent(" + event + ")");
			}
		};
	}

	protected void addRemoteServiceListeners() {
		for (int i = 0; i < adapters.length; i++) {
			adapters[i]
					.addRemoteServiceListener(createRemoteServiceListener(i == 0));
		}
	}

	protected IRemoteServiceRegistration registerRemoteService(
			IRemoteServiceContainerAdapter adapter, String serviceInterface,
			Object service, Dictionary serviceProperties, int sleepTime) {
		final IRemoteServiceRegistration result = adapter
				.registerRemoteService(new String[] { serviceInterface },
						service, serviceProperties);
		sleep(sleepTime);
		return result;
	}

	protected IRemoteServiceReference[] getRemoteServiceReferences(
			IRemoteServiceContainerAdapter adapter, String clazz, String filter) {
		try {
			return adapter.getRemoteServiceReferences((ID[]) null, clazz,
					filter);
		} catch (final InvalidSyntaxException e) {
			fail("should not happen");
		}
		return null;
	}

	protected IRemoteService getRemoteService(
			IRemoteServiceContainerAdapter adapter, String clazz, String filter) {
		final IRemoteServiceReference[] refs = getRemoteServiceReferences(
				adapter, clazz, filter);
		if (refs == null || refs.length == 0)
			return null;
		return adapter.getRemoteService(refs[0]);
	}

	protected String getFilterFromServiceProperties(Dictionary serviceProperties) {
		StringBuffer filter = null;
		if (serviceProperties != null && serviceProperties.size() > 0) {
			filter = new StringBuffer("(&");
			for (final Enumeration e = serviceProperties.keys(); e
					.hasMoreElements();) {
				final Object key = e.nextElement();
				final Object val = serviceProperties.get(key);
				if (key != null && val != null) {
					filter.append("(").append(key).append("=").append(val)
							.append(")");
				}
			}
			filter.append(")");
		}
		return (filter == null) ? null : filter.toString();
	}

	protected String[] getDefaultServiceClasses() {
		return new String[] { IConcatService.class.getName() };
	}

	protected Object getDefaultService() {
		return new IConcatService() {
			public String concat(String string1, String string2) {
				final String result = string1.concat(string2);
				System.out.println("SERVICE.concat(" + string1 + "," + string2
						+ ") returning " + result);
				return string1.concat(string2);
			}
		};
	}

	protected ServiceRegistration registerService(String[] clazzes,
			Object service, Properties props) throws Exception {
		return getContext().registerService(clazzes, service, (Dictionary) props);
	}

	protected ServiceRegistration registerService(String clazz, Object service,
			Properties props) throws Exception {
		return registerService(new String[] { clazz }, service, props);
	}

	protected ServiceRegistration registerDefaultService(Properties props)
			throws Exception {
		return registerService(getDefaultServiceClasses(), getDefaultService(),
				props);
	}

	public ServiceReference getReference() {
		return null;
	}

	protected void assertReferenceHasCorrectType(ServiceReference sr,
			String classname) {
		String[] classes = (String[]) sr
				.getProperty(org.osgi.framework.Constants.OBJECTCLASS);
		assertTrue(classes != null);
		// Check object class
		assertTrue(classname.equals(classes[0]));
	}

	protected void assertReferencesValidAndFirstHasCorrectType(
			ServiceReference[] references, String classname) {
		assertReferencesValid(references);
		assertReferenceHasCorrectType(references[0], classname);
	}

	protected void assertReferencesValid(ServiceReference[] references) {
		assertTrue(references != null);
		assertTrue(references.length > 0);
	}

	protected void assertStringResultValid(Object result, String compare) {
		assertNotNull(result);
		assertTrue(result instanceof String);
		assertTrue(compare.equals(result));
	}

	protected void assertProxyValid(Object proxy) {
		assertNotNull(proxy);
		assertTrue(proxy instanceof TestServiceInterface1);
	}

	protected ServiceTracker createProxyServiceTracker(String clazz)
			throws InvalidSyntaxException {
		ServiceTracker st = new ServiceTracker(getContext(), getContext()
				.createFilter(
						"(&(" + org.osgi.framework.Constants.OBJECTCLASS + "="
								+ clazz + ")(" + SERVICE_IMPORTED + "=*))"),
				new ServiceTrackerCustomizer() {

					public Object addingService(ServiceReference reference) {
						Trace.trace(Activator.PLUGIN_ID, "addingService="
								+ reference);
						return getContext().getService(reference);
					}

					public void modifiedService(ServiceReference reference,
							Object service) {
						Trace.trace(Activator.PLUGIN_ID, "modifiedService="
								+ reference);
					}

					public void removedService(ServiceReference reference,
							Object service) {
						Trace.trace(Activator.PLUGIN_ID, "removedService="
								+ reference + ",svc=" + service);
					}
				});
		st.open();
		return st;
	}

	protected IRemoteService getRemoteServiceFromProxy(Object proxy) {
		assertTrue(proxy instanceof IRemoteServiceProxy);
		return ((IRemoteServiceProxy) proxy).getRemoteService();
	}
	

}
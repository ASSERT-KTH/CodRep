.getProperty(org.eclipse.ecf.remoteservice.Constants.SERVICE_CONTAINER_ID);

/*******************************************************************************
 * Copyright (c) 2009 EclipseSource and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *   EclipseSource - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.internal.osgi.services.distribution;

import java.util.*;
import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.core.IContainerManager;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.util.Trace;
import org.eclipse.ecf.remoteservice.IRemoteServiceContainerAdapter;
import org.eclipse.ecf.remoteservice.IRemoteServiceRegistration;
import org.osgi.framework.BundleContext;
import org.osgi.framework.ServiceReference;
import org.osgi.service.discovery.ServicePublication;

public class EventHookImpl extends AbstractEventHookImpl {

	public EventHookImpl(DistributionProviderImpl distributionProvider) {
		super(distributionProvider);
	}

	protected void registerRemoteService(ServiceReference serviceReference,
			String[] remoteInterfaces, String[] remoteConfigurationType) {
		Map ecfConfiguration = parseECFConfigurationType(remoteConfigurationType);
		// We get the list of ECF distribution providers
		// (IRemoteServiceContainerAdapters)
		IRemoteServiceContainerAdapter[] rscas = findRemoteServiceContainerAdapters(
				serviceReference, ecfConfiguration);
		// If there are relevant ones then actually register a remote service
		// with them.
		if (rscas == null) {
			trace("registerRemoteService",
					"No remote service container adapters found for serviceReference="
							+ serviceReference + " and configuration="
							+ ecfConfiguration);
			return;
		}
		// Now actually register remote service with remote service container
		// adapters
		final Collection identifiers = registerRemoteService(rscas,
				remoteInterfaces, serviceReference);
		publishRemoteService(serviceReference, remoteInterfaces, identifiers);
	}

	private void publishRemoteService(final ServiceReference ref,
			final String[] remoteInterfaces, final Collection /*
															 * <? extends
															 * String>
															 */identifiers) {
		final Dictionary properties = new Hashtable();
		final BundleContext context = Activator.getDefault().getContext();
		properties.put(ServicePublication.PROP_KEY_SERVICE_INTERFACE_NAME,
				remoteInterfaces);
		properties.put(ServicePublication.PROP_KEY_SERVICE_PROPERTIES,
				getServiceProperties(ref));
		final String[] ids = (String[]) identifiers
				.toArray(new String[identifiers.size()]);
		for (int i = 0; i < ids.length; i++) {
			properties.put(ServicePublication.PROP_KEY_ENDPOINT_ID, ids[i]);
			context.registerService(ServicePublication.class.getName(),
					new ServicePublication() {
					}, properties);
			trace("publishRemoteService",
					"PUBLISH REMOTE SERVICE serviceReference=" + ref + " ID="
							+ ids[i]);
		}
	}

	private Map getServiceProperties(final ServiceReference ref) {
		final String[] keys = ref.getPropertyKeys();
		final Map map = new HashMap(keys.length);
		for (int i = 0; i < keys.length; i++) {
			map.put(keys[i], ref.getProperty(keys[i]));
		}
		return map;
	}

	private Map parseECFConfigurationType(String[] remoteConfigurationType) {
		Map results = new HashMap();
		// TODO parse ecf configuration from remoteConfigurationType
		return results;
	}

	protected Collection /* <? extends String> */registerRemoteService(
			IRemoteServiceContainerAdapter[] rscas, String[] remoteInterfaces,
			ServiceReference sr) {
		final ArrayList result = new ArrayList();
		for (int i = 0; i < rscas.length; i++) {
			IRemoteServiceRegistration remoteRegistration = rscas[i]
					.registerRemoteService(remoteInterfaces, getService(sr),
							createPropertiesForRemoteService(rscas[i],
									remoteInterfaces, sr));
			trace("registerRemoteService",
					"REGISTERED REMOTE SERVICE serviceReference=" + sr
							+ " remoteRegistration=" + remoteRegistration);
			result.add(remoteRegistration.getContainerID().toString());
			fireRemoteServiceRegistered(sr, remoteRegistration);
		}
		return result;
	}

	protected Dictionary createPropertiesForRemoteService(
			IRemoteServiceContainerAdapter iRemoteServiceContainerAdapter,
			String[] remotes, ServiceReference sr) {
		String[] propKeys = sr.getPropertyKeys();
		Properties newProps = new Properties();
		for (int i = 0; i < propKeys.length; i++) {
			newProps.put(propKeys[i], sr.getProperty(propKeys[i]));
		}
		return newProps;
	}

	protected IRemoteServiceContainerAdapter[] findRemoteServiceContainerAdapters(
			ServiceReference serviceReference, Map ecfConfiguration) {
		IContainerManager containerManager = Activator.getDefault()
				.getContainerManager();
		return (containerManager != null) ? getRSCAsFromContainers(
				containerManager.getAllContainers(), serviceReference,
				ecfConfiguration) : null;
	}

	private IRemoteServiceContainerAdapter[] getRSCAsFromContainers(
			IContainer[] containers, ServiceReference serviceReference,
			Map ecfConfiguration) {
		if (containers == null)
			return null;
		List rscas = new ArrayList();
		for (int i = 0; i < containers.length; i++) {
			IRemoteServiceContainerAdapter rsca = (IRemoteServiceContainerAdapter) containers[i]
					.getAdapter(IRemoteServiceContainerAdapter.class);
			if (rsca == null) {
				Trace
						.trace(
								Activator.PLUGIN_ID,
								DebugOptions.DEBUG,
								this.getClass(),
								"getRCSAsFromContainers",
								"Container="
										+ containers[i]
										+ " not an IRemoteServiceContainerAdapter. Excluding rsca="
										+ rsca + " from remote registration");
				continue;
			} else if (includeContainer(containers[i], rsca, serviceReference,
					ecfConfiguration))
				rscas.add(rsca);
		}
		return (IRemoteServiceContainerAdapter[]) rscas
				.toArray(new IRemoteServiceContainerAdapter[] {});
	}

	protected boolean includeContainer(IContainer container,
			IRemoteServiceContainerAdapter rsca,
			ServiceReference serviceReference, Map ecfConfiguration) {
		Object cID = serviceReference
				.getProperty(org.eclipse.ecf.remoteservice.Constants.REMOTE_SERVICE_CONTAINER_ID);
		if (cID == null || !(cID instanceof ID)) {
			Trace
					.trace(
							Activator.PLUGIN_ID,
							DebugOptions.DEBUG,
							this.getClass(),
							"includeContainer",
							"serviceReference="
									+ serviceReference
									+ " does not set remote service container id service property.  INCLUDING containerID="
									+ container.getID()
									+ " in remote registration");
			return true;
		}
		ID containerID = (ID) cID;
		if (container.getID().equals(containerID)) {
			Trace.trace(Activator.PLUGIN_ID, DebugOptions.DEBUG, this
					.getClass(), "includeContainer", "serviceReference="
					+ serviceReference + " has MATCHING container id="
					+ containerID + ".  INCLUDING rsca=" + rsca
					+ " in remote registration");
			return true;
		}
		Trace.trace(Activator.PLUGIN_ID, DebugOptions.DEBUG, this.getClass(),
				"includeContainer", "serviceReference=" + serviceReference
						+ " has non-matching container id=" + containerID
						+ ".  EXCLUDING rsca=" + rsca
						+ " in remote registration");
		return false;
	}

}
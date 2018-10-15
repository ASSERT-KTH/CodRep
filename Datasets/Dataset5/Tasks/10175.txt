Object remoteInterfaces = serviceReference.getProperty(ServiceConstants.OSGI_REMOTE_INTERFACES);

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

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.Dictionary;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Properties;

import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.core.IContainerManager;
import org.eclipse.ecf.core.util.Trace;
import org.eclipse.ecf.osgi.services.distribution.ServiceConstants;
import org.eclipse.ecf.remoteservice.IRemoteServiceContainerAdapter;
import org.eclipse.ecf.remoteservice.IRemoteServiceRegistration;
import org.osgi.framework.Constants;
import org.osgi.framework.ServiceEvent;
import org.osgi.framework.ServiceReference;
import org.osgi.framework.hooks.service.EventHook;

public class EventHookImpl implements EventHook {

	private final static String[] EMPTY_STRING_ARRAY = new String[0];
	private final static String REMOTE_INTERFACES_WILDCARD = "*";
	public final static String ECF_RS_PROVIDER_CONFIGURATION = "ecf";
	
	private final DistributionProviderImpl distributionProvider;
	
	private final Map remoteServiceReferences = new HashMap();
	
	public EventHookImpl(DistributionProviderImpl distributionProvider) {
		this.distributionProvider = distributionProvider;
	}

	public void event(ServiceEvent event, Collection contexts) {
		switch (event.getType()) {
		case ServiceEvent.MODIFIED:
			handleModifiedServiceEvent(event.getServiceReference(),contexts);
			break;
		case ServiceEvent.MODIFIED_ENDMATCH:
			break;
		case ServiceEvent.REGISTERED:
			handleRegisteredServiceEvent(event.getServiceReference(),contexts);
			break;
		case ServiceEvent.UNREGISTERING:
			handleUnregisteringServiceEvent(event.getServiceReference(),contexts);
			break;
		default:
			break;
		}
	}

	private void handleUnregisteringServiceEvent(
			ServiceReference serviceReference, Collection contexts) {
		traceEntering("handleUnregisteringServiceEvent");
		// TODO
		traceExiting("handleUnregisteringServiceEvent");
	}

	private void handleRegisteredServiceEvent(
			ServiceReference serviceReference, Collection contexts) {
		// This checkes to see if the serviceReference has any remote interfaces declared via
		// osgi.remote.interfaces
		Object remoteInterfaces = serviceReference.getProperty(ServiceConstants.OSGI_REMOTE_INTERFACES_KEY);
		// If so then we handle further, if not then ignore
		if (remoteInterfaces != null) {
			// get configuration determines whether we are the correct distribution provider,
			// as there could be others.  If we are, then getConfiguration returns a non-null Map.
			Map configuration = getConfiguration(serviceReference);
			if (configuration != null) {
				trace("handleRegisteredServiceEvent","serviceReference="+serviceReference+" has remoteInterfaces="+remoteInterfaces);
				// The osgi.remote.interfaces should be of type String []
				String [] remoteInterfacesArr = (String []) ((remoteInterfaces instanceof String[])?remoteInterfaces:null);
				// We compare the osgi.remote.interfaces with those exposed by the service reference and 
				// make sure that the agree
				String [] remotes = (remoteInterfacesArr != null)?getInterfacesForServiceReference(remoteInterfacesArr, serviceReference):null;
				// If they do, then remotes != null
				if (remotes != null) {
					// We get the list of ECF distribution providers (IRemoteServiceContainerAdapters)
					IRemoteServiceContainerAdapter [] rscas = findRemoteServiceContainerAdapters(remotes,serviceReference,configuration);
					// If there are relevant ones then actually register a remote service with them.
					if (rscas != null) registerRemoteService(rscas,remotes,serviceReference);
				} else trace("handleRegisteredServiceEvent","serviceReference="+serviceReference+" has no remote interfaces");
			} else trace("handleRegisteredServiceEvent","serviceReference="+serviceReference+" is not recognized as ecf configuration");
		}
	}

	private Map getConfiguration(ServiceReference serviceReference) {
		// Get property osgi.remote.configuration.type
		String[] remoteConfigurationType = (String []) serviceReference.getProperty(ServiceConstants.OSGI_REMOTE_CONFIGURATION_TYPE);
		if (remoteConfigurationType != null && remoteConfigurationType[0].equals(ECF_RS_PROVIDER_CONFIGURATION)) {
			return parseECFConfigurationType(remoteConfigurationType);
		}
		return null;
	}

	private Map parseECFConfigurationType(String[] remoteConfigurationType) {
		Map results = new HashMap();
		// TODO parse ecf configuration from remoteConfigurationType
		return results;
	}

	protected Object getService(ServiceReference sr) {
		return Activator.getDefault().getContext().getService(sr);
	}
	
	protected void registerRemoteService(IRemoteServiceContainerAdapter[] rscas, String[] remoteInterfaces, ServiceReference sr) {
		for(int i=0; i < rscas.length; i++) {
			trace("registerRemoteService","registering sr="+sr+" with rsca="+rscas[i]);
			notifyRemoteServiceRegistered(sr,rscas[i].registerRemoteService(remoteInterfaces, getService(sr), createPropertiesForRemoteService(rscas[i],remoteInterfaces,sr)));
		}
	}
	
	protected Dictionary createPropertiesForRemoteService(
			IRemoteServiceContainerAdapter iRemoteServiceContainerAdapter,
			String[] remotes, ServiceReference sr) {
		String [] propKeys = sr.getPropertyKeys();
		Properties newProps = new Properties();
		for(int i=0; i < propKeys.length; i++) {
			newProps.put(propKeys[i], sr.getProperty(propKeys[i]));
		}
		return newProps;
	}

	private void notifyRemoteServiceRegistered(ServiceReference serviceReference, IRemoteServiceRegistration remoteServiceRegistration) {
		remoteServiceReferences.put(serviceReference, remoteServiceRegistration);
		distributionProvider.addExposedService(serviceReference);
	}

	protected IRemoteServiceContainerAdapter[] findRemoteServiceContainerAdapters(
			String[] remotes, ServiceReference serviceReference, Map ecfConfiguration) {
		IContainerManager containerManager = Activator.getDefault().getContainerManager();
		return (containerManager != null)?getRSCAsFromContainers(containerManager.getAllContainers()):null;
	}

	private IRemoteServiceContainerAdapter[] getRSCAsFromContainers(
			IContainer[] containers) {
		if (containers == null) return null;
		List rscas = new ArrayList();
		for(int i=0; i < containers.length; i++) {
			IRemoteServiceContainerAdapter rsca = (IRemoteServiceContainerAdapter) containers[i].getAdapter(IRemoteServiceContainerAdapter.class);
			if (rsca != null) rscas.add(rsca);
		}
		return (IRemoteServiceContainerAdapter[]) rscas.toArray(new IRemoteServiceContainerAdapter[] {});
	}

	private String[] getInterfacesForServiceReference(
			String[] remoteInterfaces, ServiceReference serviceReference) {
		if (remoteInterfaces == null || remoteInterfaces.length == 0) return EMPTY_STRING_ARRAY;
		List results = new ArrayList();
		List interfaces = Arrays.asList((String []) serviceReference.getProperty(Constants.OBJECTCLASS));
		for(int i=0; i < remoteInterfaces.length; i++) {
			String intf = remoteInterfaces[i];
			if (REMOTE_INTERFACES_WILDCARD.equals(intf)) return (String []) interfaces.toArray(new String[] {});
			if (intf != null && interfaces.contains(intf)) results.add(intf);
		}
		return (String []) results.toArray(new String [] {});
	}

	private void handleModifiedServiceEvent(ServiceReference serviceReference, Collection contexts) {
		traceEntering("handleModifiedServiceEvent");
		// TODO
		traceExiting("handleModifiedServiceEvent");
	}

	
	private void traceEntering(String methodName) {
		Trace.entering(Activator.PLUGIN_ID, DebugOptions.METHODS_ENTERING, this.getClass(), methodName);
	}
	
	private void traceExiting(String methodName) {
		Trace.exiting(Activator.PLUGIN_ID, DebugOptions.METHODS_EXITING, this.getClass(), "handleUnregisteringServiceEvent");		
	}

	private void trace(String methodName, String message) {
		Trace.trace(Activator.PLUGIN_ID, DebugOptions.DEBUG, this.getClass(), methodName, message);
	}
	
}
Map availableServices = Activator.getDefault().getLocator().getServiceURLs();

/*******************************************************************************
 * Copyright (c) 2007 Versant Corp.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     Markus Kuppe (mkuppe <at> versant <dot> com) - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.internal.provider.jslp;

import ch.ethz.iks.slp.ServiceLocationException;
import ch.ethz.iks.slp.ServiceURL;
import java.util.*;
import org.eclipse.core.runtime.*;
import org.eclipse.core.runtime.jobs.Job;
import org.eclipse.ecf.core.util.Trace;
import org.eclipse.ecf.discovery.IServiceInfo;
import org.eclipse.ecf.provider.jslp.container.JSLPDiscoveryContainer;
import org.eclipse.ecf.provider.jslp.container.JSLPServiceInfo;
import org.osgi.framework.Bundle;

public final class JSLPDiscoveryJob extends Job {

	private JSLPDiscoveryContainer discoveryContainer;
	private Map services;

	public JSLPDiscoveryJob(JSLPDiscoveryContainer container) {
		super(Messages.JSLPDiscoveryJob_TITLE);
		discoveryContainer = container;
		services = Collections.synchronizedMap(new HashMap());
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.core.runtime.jobs.Job#run(org.eclipse.core.runtime.IProgressMonitor)
	 */
	protected IStatus run(IProgressMonitor monitor) {
		Assert.isNotNull(monitor);
		try {
			Map availableServices = Activator.getDefault().getServiceURLs();
			Map removedServices = new HashMap(services);
			for (Iterator itr = availableServices.entrySet().iterator(); itr.hasNext() && !monitor.isCanceled();) {
				Map.Entry entry = (Map.Entry) itr.next();
				ServiceURL url = (ServiceURL) entry.getKey();
				// do we know the service already?
				if (removedServices.containsKey(url)) {
					removedServices.remove(url);
				} else { // we don't know the service, so we need to create the
					// service discovery object
					//TODO-mkuppe do we get meaningful values for ServiceProperties (SLP attributes?), priority and weight from SLP?
					IServiceInfo serviceInfo = new JSLPServiceInfo(new ServiceURLAdapter(url), -1, -1, new ServicePropertiesAdapter((List) entry.getValue()));
					services.put(url, serviceInfo);
					discoveryContainer.fireServiceDiscovered(serviceInfo);
				}
				monitor.worked(1);
			}
			// at this point removedServices only contains stale services
			for (Iterator itr = removedServices.keySet().iterator(); itr.hasNext() && !monitor.isCanceled();) {
				Object key = itr.next();
				discoveryContainer.fireServiceUndiscovered((IServiceInfo) removedServices.get(key));
				services.remove(key);
				monitor.worked(1);
			}

		} catch (ServiceLocationException e) {
			// TODO-mkuppe if the advertiser is gone, we run into this exception
			// but we have to let the listeners know about the gone services
			// too
			Trace.catching(Activator.PLUGIN_ID, JSLPDebugOptions.EXCEPTIONS_CATCHING, this.getClass(), "run", e); //$NON-NLS-1$
		}

		this.schedule(JSLPDiscoveryContainer.REDISCOVER);
		return Status.OK_STATUS;
	}

	/* (non-Javadoc)
	 * @see org.eclipse.core.runtime.jobs.Job#shouldRun()
	 */
	public boolean shouldRun() {
		if (Activator.getDefault() != null) {// system went down, no bundle
			int state = Activator.getDefault().getBundle().getState();
			return (state == Bundle.ACTIVE || state == Bundle.STARTING);
		}
		return false;
	}
}
}).start();

/*******************************************************************************
 * Copyright (c) 2010 Markus Alexander Kuppe.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     Markus Alexander Kuppe (ecf-dev_eclipse.org <at> lemmster <dot> de) - initial API and implementation
 ******************************************************************************/
package ch.ethz.iks.slp.test;

import java.util.Arrays;

import org.osgi.framework.BundleContext;
import org.osgi.framework.Constants;
import org.osgi.framework.ServiceEvent;
import org.osgi.framework.ServiceListener;
import org.osgi.framework.ServiceReference;

import ch.ethz.iks.slp.Advertiser;
import ch.ethz.iks.slp.Locator;

public class DistributedTestActivator extends TestActivator implements ServiceListener {

	private BundleContext context;

	/* (non-Javadoc)
	 * @see org.osgi.framework.BundleActivator#start(org.osgi.framework.BundleContext)
	 */
	public void start(BundleContext aContext) throws Exception {
		context = aContext;
		final String filter = "(|" + "(" + Constants.OBJECTCLASS
				+ "=" + Advertiser.class.getName() + ")" + "("
				+ Constants.OBJECTCLASS + "=" + Locator.class.getName() + ")"
				+ ")";
		context.addServiceListener(this, filter);
		
		// get the previously active services
		ServiceReference[] serviceReferences = context.getServiceReferences(null, filter);
		for (int i = 0; i < serviceReferences.length; i++) {
			handleServiceAdded(serviceReferences[i]);
		}
	}

	/* (non-Javadoc)
	 * @see org.osgi.framework.BundleActivator#stop(org.osgi.framework.BundleContext)
	 */
	public void stop(BundleContext context) throws Exception {
		context = null;
		super.stop(context);
	}

	/* (non-Javadoc)
	 * @see org.osgi.framework.ServiceListener#serviceChanged(org.osgi.framework.ServiceEvent)
	 */
	public void serviceChanged(ServiceEvent event) {
		if (context == null) {
			return;
		}

		switch (event.getType()) {
		case ServiceEvent.REGISTERED:
			ServiceReference serviceReference = event.getServiceReference();
			handleServiceAdded(serviceReference);
			break;
		}

		if (advertiser != null && locator != null) {
			new Thread(new Runnable() {
				/* (non-Javadoc)
				 * @see java.lang.Runnable#run()
				 */
				public void run() {
					startTests();
				}
			});
		}
	}

	private void handleServiceAdded(final ServiceReference aServiceReference) {
		// check if its Advertiser or Locator
		final Object objectClass = aServiceReference.getProperty(Constants.OBJECTCLASS);
		final boolean adv = Arrays.equals((String[]) objectClass, new String[]{Advertiser.class.getName()});
		
		// r-OSGi also registers the same service with this framework, however we want to explicitly use the services remoted by ecf distribution
		final String symbolicName = (String) aServiceReference.getBundle().getHeaders().get("Bundle-SymbolicName");
		final boolean remote = symbolicName.equals("org.eclipse.ecf.osgi.services.distribution");
//		final boolean remote = symbolicName.startsWith("R-OSGi Proxy Bundle generated for Endpoint");
		
		// remote Advertiser
		if (remote && adv) {
			advertiser = (Advertiser) context.getService(aServiceReference);
		} 
		
		// local Locator
		if (!adv && !remote){
			locator = (Locator) context.getService(aServiceReference);
		}
	}
}
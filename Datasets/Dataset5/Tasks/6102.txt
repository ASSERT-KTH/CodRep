package org.eclipse.ecf.tests.internal.osgi.services.distribution;

package org.eclipse.ecf.tests.osgi.services.distribution;

import org.osgi.framework.BundleActivator;
import org.osgi.framework.BundleContext;

public class Activator implements BundleActivator {

	private static Activator plugin;
	private BundleContext context;
	
	public static final Activator getDefault() {
		return plugin;
	}
	
	/*
	 * (non-Javadoc)
	 * @see org.osgi.framework.BundleActivator#start(org.osgi.framework.BundleContext)
	 */
	public void start(BundleContext context) throws Exception {
		plugin = this;
		this.context = context;
	}

	/*
	 * (non-Javadoc)
	 * @see org.osgi.framework.BundleActivator#stop(org.osgi.framework.BundleContext)
	 */
	public void stop(BundleContext context) throws Exception {
		context = null;
		plugin = null;
	}

	public BundleContext getContext() {
		return context;
	}

}
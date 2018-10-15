String prop = (String) refs[i].getProperty(IServiceConstants.SYNCSTRATEGY_PROVIDER_PROPETY);

package org.eclipse.ecf.internal.tests.sync;

import org.eclipse.ecf.sync.IServiceConstants;
import org.eclipse.ecf.sync.doc.IDocumentSynchronizationStrategyFactory;
import org.osgi.framework.BundleActivator;
import org.osgi.framework.BundleContext;
import org.osgi.framework.ServiceReference;
import org.osgi.util.tracker.ServiceTracker;

public class Activator implements BundleActivator {

	private BundleContext context;
	private ServiceTracker serviceTracker;
	
	private static Activator plugin;
	
	public static Activator getDefault() {
		return plugin;
	}
	
	/*
	 * (non-Javadoc)
	 * @see org.osgi.framework.BundleActivator#start(org.osgi.framework.BundleContext)
	 */
	public void start(BundleContext ctxt) throws Exception {
		plugin = this;
		this.context = ctxt;
	}

	/*
	 * (non-Javadoc)
	 * @see org.osgi.framework.BundleActivator#stop(org.osgi.framework.BundleContext)
	 */
	public void stop(BundleContext context) throws Exception {
		if (serviceTracker != null) {
			serviceTracker.close();
			serviceTracker = null;
		}
		plugin = null;
		this.context = null;
	}

	public IDocumentSynchronizationStrategyFactory [] getSynchStrategyFactories() {
		if (serviceTracker == null) {
			serviceTracker = new ServiceTracker(context,IDocumentSynchronizationStrategyFactory.class.getName(),null);
			serviceTracker.open();
		}
		ServiceReference [] refs = serviceTracker.getServiceReferences();
		if (refs == null) return null;
		IDocumentSynchronizationStrategyFactory [] strats = new IDocumentSynchronizationStrategyFactory [refs.length];
		for(int i =0; i < refs.length; i++) {
			strats[i] = (IDocumentSynchronizationStrategyFactory) serviceTracker.getService(refs[i]);
		}
		return strats;
	}
	
	public IDocumentSynchronizationStrategyFactory getSynchStrategyFactory(String serviceProvider) {
		if (serviceTracker == null) {
			serviceTracker = new ServiceTracker(context,IDocumentSynchronizationStrategyFactory.class.getName(),null);
			serviceTracker.open();
		}
		ServiceReference [] refs = serviceTracker.getServiceReferences();
		if (refs == null) return null;
		IDocumentSynchronizationStrategyFactory result = null;
		for(int i =0; i < refs.length; i++) {
			String prop = (String) refs[i].getProperty(IServiceConstants.SYNCSTRATEGY_TYPE_PROPERTY);
			if (prop != null && prop.equals(serviceProvider)) {
				result = (IDocumentSynchronizationStrategyFactory) serviceTracker.getService(refs[i]);
			}
		}
		return result;
	}

	public IDocumentSynchronizationStrategyFactory getColaSynchronizationStrategyFactory() {
		return getSynchStrategyFactory("org.eclipse.ecf.internal.sync.doc.cola");
	}
	
	public IDocumentSynchronizationStrategyFactory getIdentitySynchronizationStrategy() {
		return getSynchStrategyFactory("org.eclipse.ecf.sync.doc.identity");
	}
}
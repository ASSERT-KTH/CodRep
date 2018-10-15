static final boolean DEBUG = Boolean.getBoolean("org.eclipse.ecf.remoteservice.util.tracker.RemoteServiceTracker.debug"); //$NON-NLS-1$

/****************************************************************************
 * Copyright (c) 2008 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Composent, Inc. - initial API and implementation
 *****************************************************************************/

package org.eclipse.ecf.remoteservice.util.tracker;

import java.util.*;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.remoteservice.*;
import org.eclipse.ecf.remoteservice.events.*;
import org.eclipse.ecf.remoteservice.util.RemoteFilterImpl;
import org.osgi.framework.InvalidSyntaxException;
import org.osgi.framework.ServiceEvent;

/**
 * Remote service tracker
 * 
 * @since 3.0
 *
 */
public class RemoteServiceTracker implements IRemoteServiceTrackerCustomizer {

	/* set this to true to compile in debug messages */
	static final boolean DEBUG = true;

	/**
	 * IRemoteServiceContainerAdapter containerAdapter against which 
	 * this <code>RemoteServiceTracker</code></code> is tracking.
	 */
	protected final IRemoteServiceContainerAdapter containerAdapter;
	/**
	 * Container IDs that provide the context for tracking.
	 */
	protected final ID[] containerIDs;
	/**
	 * Filter specifying search criteria for the services to track.
	 * 
	 */
	protected final IRemoteFilter filter;
	/**
	 * <code>ServiceTrackerCustomizer</code> object for this tracker.
	 */
	final IRemoteServiceTrackerCustomizer customizer;
	/**
	 * Filter string for use when adding the ServiceListener.
	 */
	private final String listenerFilter;
	/**
	 * Class name to be tracked. If this field is set, then we are tracking by
	 * class name.
	 */
	private final String trackClass;
	/**
	 * Reference to be tracked. If this field is set, then we are tracking a
	 * single IRemoteServiceReference.
	 */
	private final IRemoteServiceReference trackReference;
	/**
	 * True if no Filter object was supplied in a constructor or we are not
	 * using the supplied filter.
	 */
	final boolean noUserFilter;
	/**
	 * Tracked services: <code>ServiceReference</code> object -> customized
	 * Object and <code>ServiceListener</code> object
	 */
	private volatile Tracked tracked;
	/**
	 * Modification count. This field is initialized to zero by open, set to -1
	 * by close and incremented by modified.
	 * 
	 * This field is volatile since it is accessed by multiple threads.
	 */
	private volatile int trackingCount = -1;
	/**
	 * Cached ServiceReference for getServiceReference.
	 * 
	 * This field is volatile since it is accessed by multiple threads.
	 */
	private volatile IRemoteServiceReference cachedReference;
	/**
	 * Cached service object for getService.
	 * 
	 * This field is volatile since it is accessed by multiple threads.
	 */
	private volatile IRemoteService cachedService;

	/**
	 * Create a <code>RemoteServiceTracker</code></code> on the specified
	 * <code>IRemoteServiceReference</code>.
	 * 
	 * <p>
	 * The remote service referenced by the specified <code>IRemoteServiceReference</code>
	 * object will be tracked by this <code>RemoteServiceTracker</code></code> object.
	 * 
	 * @param containerAdapter <code>IRemoteServiceContainerAdapter</code> against which the
	 *        tracking is done.
	 * @param reference <code>IRemoteServiceReference</code> for the remote service
	 *        to be tracked.
	 * @param customizer The customizer object to call when services are added,
	 *        modified, or removed in this <code>RemoteServiceTracker</code> object.
	 *        If customizer is <code>null</code>, then this
	 *        <code>RemoteServiceTracker</code> object will be used as the
	 *        <code>ServiceTrackerCustomizer</code> object and the
	 *        <code>RemoteServiceTracker</code> object will call the
	 *        <code>ServiceTrackerCustomizer</code> methods on itself.
	 */
	public RemoteServiceTracker(IRemoteServiceContainerAdapter containerAdapter, ID[] containerIDs, IRemoteServiceReference reference, IRemoteServiceTrackerCustomizer customizer) {
		this.containerAdapter = containerAdapter;
		this.trackReference = reference;
		this.containerIDs = containerIDs;
		this.trackClass = null;
		this.customizer = (customizer == null) ? this : customizer;
		this.listenerFilter = "(&(" + Constants.OBJECTCLASS + "=" + ((String[]) reference.getProperty(Constants.OBJECTCLASS))[0] //$NON-NLS-1$ //$NON-NLS-2$
				+ ")(" + Constants.SERVICE_ID + "=" + reference.getProperty(Constants.SERVICE_ID).toString() + "))"; //$NON-NLS-1$ //$NON-NLS-2$ //$NON-NLS-3$
		this.noUserFilter = true;
		try {
			this.filter = new RemoteFilterImpl(listenerFilter);
		} catch (InvalidSyntaxException e) { // we could only get this exception
			// if the ServiceReference was
			// invalid
			throw new IllegalArgumentException("unexpected InvalidSyntaxException: " + e.getMessage()); //$NON-NLS-1$
		}
	}

	/**
	 * Create a <code>RemoteServiceTracker</code> object on the specified class
	 * name.
	 * 
	 * <p>
	 * Services registered under the specified class name will be tracked by
	 * this <code>RemoteServiceTracker</code> object.
	 * 
	 * @param containerAdapter <code>BundleContext</code> object against which the
	 *        tracking is done.
	 * @param clazz Class name of the services to be tracked.
	 * @param customizer The customizer object to call when services are added,
	 *        modified, or removed in this <code>RemoteServiceTracker</code> object.
	 *        If customizer is <code>null</code>, then this
	 *        <code>RemoteServiceTracker</code> object will be used as the
	 *        <code>ServiceTrackerCustomizer</code> object and the
	 *        <code>RemoteServiceTracker</code> object will call the
	 *        <code>ServiceTrackerCustomizer</code> methods on itself.
	 */
	public RemoteServiceTracker(IRemoteServiceContainerAdapter containerAdapter, ID[] containerIDs, String clazz, IRemoteServiceTrackerCustomizer customizer) {
		this.containerAdapter = containerAdapter;
		this.trackReference = null;
		this.trackClass = clazz;
		this.containerIDs = containerIDs;
		this.customizer = (customizer == null) ? this : customizer;
		this.listenerFilter = "(" + Constants.OBJECTCLASS + "=" + clazz.toString() + ")"; //$NON-NLS-1$ //$NON-NLS-2$ //$NON-NLS-3$
		this.noUserFilter = true;
		try {
			this.filter = new RemoteFilterImpl(listenerFilter);
		} catch (InvalidSyntaxException e) { // we could only get this exception
			// if the clazz argument was
			// malformed
			throw new IllegalArgumentException("unexpected InvalidSyntaxException: " + e.getMessage()); //$NON-NLS-1$
		}
	}

	/**
	 * Open this <code>RemoteServiceTracker</code> object and begin tracking
	 * services.
	 * 
	 * <p>
	 * Services which match the search criteria specified when this
	 * <code>RemoteServiceTracker</code> object was created are now tracked by this
	 * <code>RemoteServiceTracker</code> object.
	 * 
	 * @throws java.lang.IllegalStateException if the <code>BundleContext</code>
	 *         object with which this <code>RemoteServiceTracker</code> object was
	 *         created is no longer valid.
	 * @since 1.3
	 */
	public synchronized void open() {
		if (tracked != null) {
			return;
		}
		if (DEBUG) {
			System.out.println("RemoteServiceTracker.open: " + filter); //$NON-NLS-1$
		}
		tracked = new Tracked();
		trackingCount = 0;
		synchronized (tracked) {
			try {
				containerAdapter.addRemoteServiceListener(tracked);
				IRemoteServiceReference[] references;

				if (trackReference != null) { // tracking a single reference 
					references = new IRemoteServiceReference[] {trackReference};
				} else { // tracking a set of references
					references = getInitialReferences(containerIDs, trackClass, noUserFilter ? null : filter.toString());
				}
				tracked.setInitialServices(references); // set tracked with
				// the initial
				// references
			} catch (InvalidSyntaxException e) {
				throw new RuntimeException("unexpected InvalidSyntaxException: " + e.getMessage()); //$NON-NLS-1$
			}
		}
		/* Call tracked outside of synchronized region */
		tracked.trackInitialServices(); // process the initial references
	}

	/**
	 * Returns the list of initial <code>ServiceReference</code> objects that
	 * will be tracked by this <code>RemoteServiceTracker</code> object.
	 * 
	 * @param trackClass the class name with which the service was registered,
	 *        or null for all services.
	 * @param filterString the filter criteria or null for all services.
	 * @return the list of initial <code>ServiceReference</code> objects.
	 * @throws InvalidSyntaxException if the filter uses an invalid syntax.
	 */
	private IRemoteServiceReference[] getInitialReferences(ID[] ids, String clazz, String filterString) throws InvalidSyntaxException {
		return containerAdapter.getRemoteServiceReferences(ids, clazz, filterString);
	}

	/**
	 * Close this <code>RemoteServiceTracker</code>.
	 * 
	 * <p>
	 * This method should be called when this <code>RemoteServiceTracker</code>
	 * object should end the tracking of services.
	 */
	public synchronized void close() {
		if (tracked == null) {
			return;
		}
		if (DEBUG) {
			System.out.println("RemoteServiceTracker.close: " + filter); //$NON-NLS-1$
		}
		tracked.close();
		IRemoteServiceReference[] references = getRemoteServiceReferences();
		Tracked outgoing = tracked;
		tracked = null;
		try {
			containerAdapter.removeRemoteServiceListener(outgoing);
		} catch (IllegalStateException e) {
			/* In case the containerAdapter was stopped. */
		}
		if (references != null) {
			for (int i = 0; i < references.length; i++) {
				outgoing.untrack(references[i]);
			}
		}
		trackingCount = -1;
		if (DEBUG) {
			if ((cachedReference == null) && (cachedService == null)) {
				System.out.println("RemoteServiceTracker.close[cached cleared]: " + filter); //$NON-NLS-1$
			}
		}
	}

	/**
	 * Default implementation of the
	 * <code>IRemoteServiceTrackerCustomizer.addingService</code> method.
	 * 
	 * <p>
	 * This method is only called when this <code>RemoteServiceTracker</code></code> object
	 * has been constructed with a <code>null IRemoteServiceTrackerCustomizer</code>
	 * argument.
	 * 
	 * The default implementation returns the result of calling
	 * <code>getService</code>, on the <code>BundleContext</code> object
	 * with which this <code>RemoteServiceTracker</code> object was created, passing
	 * the specified <code>ServiceReference</code> object.
	 * <p>
	 * This method can be overridden in a subclass to customize the service
	 * object to be tracked for the service being added. In that case, take care
	 * not to rely on the default implementation of removedService that will
	 * unget the service.
	 * 
	 * @param reference Reference to service being added to this
	 *        <code>RemoteServiceTracker</code> object.
	 * @return The IRemoteService object to be tracked for the service added to this
	 *         <code>RemoteServiceTracker</code></code> object.
	 * @see IRemoteServiceTrackerCustomizer
	 */
	public IRemoteService addingService(IRemoteServiceReference reference) {
		return containerAdapter.getRemoteService(reference);
	}

	/**
	 * Default implementation of the
	 * <code>ServiceTrackerCustomizer.modifiedService</code> method.
	 * 
	 * <p>
	 * This method is only called when this <code>RemoteServiceTracker</code> object
	 * has been constructed with a <code>null ServiceTrackerCustomizer</code>
	 * argument.
	 * 
	 * The default implementation does nothing.
	 * 
	 * @param reference Reference to modified service.
	 * @param remoteService The service object for the modified service.
	 * @see IRemoteServiceTrackerCustomizer
	 */
	public void modifiedService(IRemoteServiceReference reference, IRemoteService remoteService) {
		// nothing to do.  Subclasses may override
	}

	/**
	 * Default implementation of the
	 * <code>ServiceTrackerCustomizer.removedService</code> method.
	 * 
	 * <p>
	 * This method is only called when this <code>RemoteServiceTracker</code> object
	 * has been constructed with a <code>null ServiceTrackerCustomizer</code>
	 * argument.
	 * 
	 * The default implementation calls <code>ungetService</code>, on the
	 * <code>BundleContext</code> object with which this
	 * <code>RemoteServiceTracker</code> object was created, passing the specified
	 * <code>ServiceReference</code> object.
	 * <p>
	 * This method can be overridden in a subclass. If the default
	 * implementation of <code>addingService</code> method was used, this
	 * method must unget the service.
	 * 
	 * @param reference Reference to removed service.
	 * @param remoteService The service object for the removed service.
	 * @see IRemoteServiceTrackerCustomizer
	 */
	public void removedService(IRemoteServiceReference reference, IRemoteService remoteService) {
		containerAdapter.ungetRemoteService(reference);
	}

	/**
	 * Wait for at least one service to be tracked by this
	 * <code>RemoteServiceTracker</code> object.
	 * <p>
	 * It is strongly recommended that <code>waitForService</code> is not used
	 * during the calling of the <code>BundleActivator</code> methods.
	 * <code>BundleActivator</code> methods are expected to complete in a
	 * short period of time.
	 * 
	 * @param timeout time interval in milliseconds to wait. If zero, the method
	 *        will wait indefinitely.
	 * @return Returns the result of <code>getService()</code>.
	 * @throws InterruptedException If another thread has interrupted the
	 *         current thread.
	 * @throws IllegalArgumentException If the value of timeout is negative.
	 */
	public IRemoteService waitForRemoteService(long timeout) throws InterruptedException {
		if (timeout < 0) {
			throw new IllegalArgumentException("timeout value is negative"); //$NON-NLS-1$
		}
		IRemoteService object = getRemoteService();
		while (object == null) {
			Tracked t = this.tracked;
			/*
			 * use local var since we are not
			 * synchronized	
			 */
			if (t == null) { /* if ServiceTracker is not open */
				return null;
			}
			synchronized (t) {
				if (t.size() == 0) {
					t.wait(timeout);
				}
			}
			object = getRemoteService();
			if (timeout > 0) {
				return object;
			}
		}
		return object;
	}

	/**
	 * Return an array of <code>ServiceReference</code> objects for all
	 * services being tracked by this <code>RemoteServiceTracker</code> object.
	 * 
	 * @return Array of <code>ServiceReference</code> objects or
	 *         <code>null</code> if no service are being tracked.
	 */
	public IRemoteServiceReference[] getRemoteServiceReferences() {
		Tracked t = this.tracked;
		/*
		 * use local var since we are not
		 * synchronized
		 */
		if (t == null) { /* if ServiceTracker is not open */
			return null;
		}
		synchronized (t) {
			int length = t.size();
			if (length == 0) {
				return null;
			}
			IRemoteServiceReference[] references = new IRemoteServiceReference[length];
			Enumeration keys = t.keys();
			for (int i = 0; i < length; i++) {
				references[i] = (IRemoteServiceReference) keys.nextElement();
			}
			return references;
		}
	}

	/**
	 * Returns a <code>ServiceReference</code> object for one of the services
	 * being tracked by this <code>RemoteServiceTracker</code> object.
	 * 
	 * <p>
	 * If multiple services are being tracked, the service with the highest
	 * ranking (as specified in its <code>service.ranking</code> property) is
	 * returned.
	 * 
	 * <p>
	 * If there is a tie in ranking, the service with the lowest service ID (as
	 * specified in its <code>service.id</code> property); that is, the
	 * service that was registered first is returned.
	 * <p>
	 * This is the same algorithm used by
	 * <code>BundleContext.getServiceReference</code>.
	 * 
	 * @return <code>ServiceReference</code> object or <code>null</code> if
	 *         no service is being tracked.
	 * @since 1.1
	 */
	public IRemoteServiceReference getRemoteServiceReference() {
		IRemoteServiceReference reference = cachedReference;
		if (reference != null) {
			if (DEBUG) {
				System.out.println("RemoteServiceTracker.getRemoteServiceReference[cached]: " + filter); //$NON-NLS-1$
			}
			return reference;
		}
		if (DEBUG) {
			System.out.println("RemoteServiceTracker.getRemoteServiceReference: " + filter); //$NON-NLS-1$
		}
		IRemoteServiceReference[] references = getRemoteServiceReferences();
		int length = (references == null) ? 0 : references.length;
		if (length == 0) /* if no service is being tracked */
		{
			return null;
		}
		int index = 0;
		if (length > 1) /* if more than one service, select highest ranking */
		{
			int rankings[] = new int[length];
			int count = 0;
			int maxRanking = Integer.MIN_VALUE;
			for (int i = 0; i < length; i++) {
				Object property = references[i].getProperty(Constants.SERVICE_RANKING);
				int ranking = (property instanceof Integer) ? ((Integer) property).intValue() : 0;
				rankings[i] = ranking;
				if (ranking > maxRanking) {
					index = i;
					maxRanking = ranking;
					count = 1;
				} else {
					if (ranking == maxRanking) {
						count++;
					}
				}
			}
			if (count > 1) /* if still more than one service, select lowest id */
			{
				long minId = Long.MAX_VALUE;
				for (int i = 0; i < length; i++) {
					if (rankings[i] == maxRanking) {
						long id = ((Long) (references[i].getProperty(Constants.SERVICE_ID))).longValue();
						if (id < minId) {
							index = i;
							minId = id;
						}
					}
				}
			}
		}
		return cachedReference = references[index];
	}

	/**
	 * Returns the service object for the specified
	 * <code>ServiceReference</code> object if the referenced service is being
	 * tracked by this <code>RemoteServiceTracker</code> object.
	 * 
	 * @param reference Reference to the desired service.
	 * @return Service object or <code>null</code> if the service referenced
	 *         by the specified <code>ServiceReference</code> object is not
	 *         being tracked.
	 */
	public IRemoteService getRemoteService(IRemoteServiceReference reference) {
		Tracked t = this.tracked;
		/*
		 * use local var since we are not
		 * synchronized
		 */
		if (t == null) { /* if ServiceTracker is not open */
			return null;
		}
		synchronized (t) {
			return (IRemoteService) t.get(reference);
		}
	}

	/**
	 * Return an array of service objects for all services being tracked by this
	 * <code>RemoteServiceTracker</code> object.
	 * 
	 * @return Array of service objects or <code>null</code> if no service are
	 *         being tracked.
	 */
	public IRemoteService[] getRemoteServices() {
		Tracked t = this.tracked;
		/*
		 * use local var since we are not
		 * synchronized
		 */
		if (t == null) { /* if ServiceTracker is not open */
			return null;
		}
		synchronized (t) {
			IRemoteServiceReference[] references = getRemoteServiceReferences();
			int length = (references == null) ? 0 : references.length;
			if (length == 0) {
				return null;
			}
			IRemoteService[] objects = new IRemoteService[length];
			for (int i = 0; i < length; i++) {
				objects[i] = getRemoteService(references[i]);
			}
			return objects;
		}
	}

	/**
	 * Returns a service object for one of the services being tracked by this
	 * <code>RemoteServiceTracker</code> object.
	 * 
	 * <p>
	 * If any services are being tracked, this method returns the result of
	 * calling <code>getService(getServiceReference())</code>.
	 * 
	 * @return Service object or <code>null</code> if no service is being
	 *         tracked.
	 */
	public IRemoteService getRemoteService() {
		IRemoteService service = cachedService;
		if (service != null) {
			if (DEBUG) {
				System.out.println("RemoteServiceTracker.getRemoteService[cached]: " + filter); //$NON-NLS-1$
			}
			return service;
		}
		if (DEBUG) {
			System.out.println("RemoteServiceTracker.getRemoteService: " + filter); //$NON-NLS-1$
		}
		IRemoteServiceReference reference = getRemoteServiceReference();
		if (reference == null) {
			return null;
		}
		return cachedService = getRemoteService(reference);
	}

	/**
	 * Remove a service from this <code>RemoteServiceTracker</code> object.
	 * 
	 * The specified service will be removed from this
	 * <code>RemoteServiceTracker</code> object. If the specified service was being
	 * tracked then the <code>ServiceTrackerCustomizer.removedService</code>
	 * method will be called for that service.
	 * 
	 * @param reference Reference to the service to be removed.
	 */
	public void remove(IRemoteServiceReference reference) {
		Tracked t = this.tracked;
		/*
		 * use local var since we are not
		 * synchronized
		 */
		if (t == null) { /* if ServiceTracker is not open */
			return;
		}
		t.untrack(reference);
	}

	/**
	 * Return the number of services being tracked by this
	 * <code>RemoteServiceTracker</code> object.
	 * 
	 * @return Number of services being tracked.
	 */
	public int size() {
		Tracked t = this.tracked;
		/*
		 * use local var since we are not
		 * synchronized
		 */
		if (t == null) { /* if ServiceTracker is not open */
			return 0;
		}
		return t.size();
	}

	/**
	 * Returns the tracking count for this <code>RemoteServiceTracker</code> object.
	 * 
	 * The tracking count is initialized to 0 when this
	 * <code>RemoteServiceTracker</code> object is opened. Every time a service is
	 * added, modified or removed from this <code>RemoteServiceTracker</code> object
	 * the tracking count is incremented.
	 * 
	 * <p>
	 * The tracking count can be used to determine if this
	 * <code>RemoteServiceTracker</code> object has added, modified or removed a
	 * service by comparing a tracking count value previously collected with the
	 * current tracking count value. If the value has not changed, then no
	 * service has been added, modified or removed from this
	 * <code>RemoteServiceTracker</code> object since the previous tracking count
	 * was collected.
	 * 
	 * @since 1.2
	 * @return The tracking count for this <code>RemoteServiceTracker</code> object
	 *         or -1 if this <code>RemoteServiceTracker</code> object is not open.
	 */
	public int getTrackingCount() {
		return trackingCount;
	}

	/**
	 * Called by the Tracked object whenever the set of tracked services is
	 * modified. Increments the tracking count and clears the cache.
	 * 
	 * @GuardedBy tracked
	 */
	/*
	 * This method must not be synchronized since it is called by Tracked while
	 * Tracked is synchronized. We don't want synchronization interactions
	 * between the ServiceListener thread and the user thread.
	 */
	void modified() {
		trackingCount++; /* increment modification count */
		cachedReference = null; /* clear cached value */
		cachedService = null; /* clear cached value */
		if (DEBUG) {
			System.out.println("RemoteServiceTracker.modified: " + filter); //$NON-NLS-1$
		}
	}

	class Tracked extends Hashtable implements IRemoteServiceListener {

		private static final long serialVersionUID = 1457902368711966642L;

		public static final boolean TRACKED_DEBUG = true;

		/**
		 * List of ServiceReferences in the process of being added. This is used
		 * to deal with nesting of ServiceEvents. Since ServiceEvents are
		 * synchronously delivered, ServiceEvents can be nested. For example,
		 * when processing the adding of a service and the customizer causes the
		 * service to be unregistered, notification to the nested call to
		 * untrack that the service was unregistered can be made to the track
		 * method.
		 * 
		 * Since the ArrayList implementation is not synchronized, all access to
		 * this list must be protected by the same synchronized object for
		 * thread-safety.
		 * 
		 * @GuardedBy this
		 */
		private final ArrayList adding;

		/**
		 * true if the tracked object is closed.
		 * 
		 * This field is volatile because it is set by one thread and read by
		 * another.
		 */
		private volatile boolean closed;

		/**
		 * Initial list of ServiceReferences for the tracker. This is used to
		 * correctly process the initial services which could become
		 * unregistered before they are tracked. This is necessary since the
		 * initial set of tracked services are not "announced" by ServiceEvents
		 * and therefore the ServiceEvent for unregistration could be delivered
		 * before we track the service.
		 * 
		 * A service must not be in both the initial and adding lists at the
		 * same time. A service must be moved from the initial list to the
		 * adding list "atomically" before we begin tracking it.
		 * 
		 * Since the LinkedList implementation is not synchronized, all access
		 * to this list must be protected by the same synchronized object for
		 * thread-safety.
		 * 
		 * @GuardedBy this
		 */
		private final LinkedList initial;

		/**
		 * Tracked constructor.
		 */
		protected Tracked() {
			super();
			closed = false;
			adding = new ArrayList(6);
			initial = new LinkedList();
		}

		/**
		 * Set initial list of services into tracker before ServiceEvents begin
		 * to be received.
		 * 
		 * This method must be called from ServiceTracker.open while
		 * synchronized on this object in the same synchronized block as the
		 * addServiceListener call.
		 * 
		 * @param references The initial list of services to be tracked.
		 * @GuardedBy this
		 */
		protected void setInitialServices(IRemoteServiceReference[] references) {
			if (references == null) {
				return;
			}
			int size = references.length;
			for (int i = 0; i < size; i++) {
				if (TRACKED_DEBUG) {
					System.out.println("RemoteServiceTracker.Tracked.setInitialServices: " + references[i]); //$NON-NLS-1$
				}
				initial.add(references[i]);
			}
		}

		/**
		 * Track the initial list of services. This is called after
		 * ServiceEvents can begin to be received.
		 * 
		 * This method must be called from ServiceTracker.open while not
		 * synchronized on this object after the addServiceListener call.
		 * 
		 */
		protected void trackInitialServices() {
			while (true) {
				IRemoteServiceReference reference;
				synchronized (this) {
					if (initial.size() == 0) {
						/*
						 * if there are no more inital services
						 */
						return; /* we are done */
					}
					/*
					 * move the first service from the initial list to the
					 * adding list within this synchronized block.
					 */
					reference = (IRemoteServiceReference) initial.removeFirst();
					if (this.get(reference) != null) {
						/* if we are already tracking this service */
						if (TRACKED_DEBUG) {
							System.out.println("RemoteServiceTracker.Tracked.trackInitialServices[already tracked]: " + reference); //$NON-NLS-1$
						}
						continue; /* skip this service */
					}
					if (adding.contains(reference)) {
						/*
						 * if this service is already in the process of being
						 * added.
						 */
						if (TRACKED_DEBUG) {
							System.out.println("RemoteServiceTracker.Tracked.trackInitialServices[already adding]: " + reference); //$NON-NLS-1$
						}
						continue; /* skip this service */
					}
					adding.add(reference);
				}
				if (TRACKED_DEBUG) {
					System.out.println("RemoteServiceTracker.Tracked.trackInitialServices: " + reference); //$NON-NLS-1$
				}
				trackAdding(reference);
				/*
				 * Begin tracking it. We call
				 * trackAdding since we have already put
				 * the reference in the adding list.
				 */
			}
		}

		/**
		 * Called by the owning <code>RemoteServiceTracker</code> object when it is
		 * closed.
		 */
		protected void close() {
			closed = true;
		}

		/**
		 * <code>ServiceListener</code> method for the
		 * <code>RemoteServiceTracker</code> class. This method must NOT be
		 * synchronized to avoid deadlock potential.
		 * 
		 * @param event <code>ServiceEvent</code> object from the framework.
		 */
		public void handleServiceEvent(IRemoteServiceEvent event) {
			/*
			 * Check if we had a delayed call (which could happen when we
			 * close).
			 */
			if (closed) {
				return;
			}
			int type = ServiceEvent.MODIFIED;
			if (event instanceof IRemoteServiceRegisteredEvent) {
				type = ServiceEvent.REGISTERED;
			} else if (event instanceof IRemoteServiceUnregisteredEvent) {
				type = ServiceEvent.UNREGISTERING;
			}
			IRemoteServiceReference reference = event.getReference();
			if (TRACKED_DEBUG) {
				System.out.println("RemoteServiceTracker.Tracked.serviceChanged[" + event.getClass() + "]: " + reference); //$NON-NLS-1$ //$NON-NLS-2$
			}

			switch (type) {
				case ServiceEvent.REGISTERED :
				case ServiceEvent.MODIFIED :
					if (noUserFilter) { // no user supplied filter to be checked
						track(reference);
						/*
						 * If the customizer throws an unchecked exception, it
						 * is safe to let it propagate
						 */
					} else { // filter supplied by user must be checked
						if (filter.match(reference)) {
							track(reference);
							/*
							 * If the customizer throws an unchecked exception,
							 * it is safe to let it propagate
							 */
						} else {
							untrack(reference);
							/*
							 * If the customizer throws an unchecked exception,
							 * it is safe to let it propagate
							 */
						}
					}
					break;
				case ServiceEvent.UNREGISTERING :
					untrack(reference);
					/*
					 * If the customizer throws an unchecked exception, it is
					 * safe to let it propagate
					 */
					break;
			}
		}

		/**
		 * Begin to track the referenced service.
		 * 
		 * @param reference IRemoteServiceReference to a service to be tracked.
		 */
		private void track(IRemoteServiceReference reference) {
			IRemoteService object;
			synchronized (this) {
				object = (IRemoteService) this.get(reference);
			}
			if (object != null) /* we are already tracking the service */
			{
				if (TRACKED_DEBUG) {
					System.out.println("RemoteServiceTracker.Tracked.track[modified]: " + reference); //$NON-NLS-1$
				}
				synchronized (this) {
					modified(); /* increment modification count */
				}
				/* Call customizer outside of synchronized region */
				customizer.modifiedService(reference, object);
				/*
				 * If the customizer throws an unchecked exception, it is safe
				 * to let it propagate
				 */
				return;
			}
			synchronized (this) {
				if (adding.contains(reference)) {
					/*
					 * if this service is
					 * already in the process of
					 * being added.
					 */
					if (TRACKED_DEBUG) {
						System.out.println("RemoteServiceTracker.Tracked.track[already adding]: " + reference); //$NON-NLS-1$
					}
					return;
				}
				adding.add(reference); /* mark this service is being added */
			}

			trackAdding(reference);
			/*
			 * call trackAdding now that we have put the
			 * reference in the adding list
			 */
		}

		/**
		 * Common logic to add a service to the tracker used by track and
		 * trackInitialServices. The specified reference must have been placed
		 * in the adding list before calling this method.
		 * 
		 * @param reference IRemoteServiceReference to a service to be tracked.
		 */
		private void trackAdding(IRemoteServiceReference reference) {
			if (TRACKED_DEBUG) {
				System.out.println("RemoteServiceTracker.Tracked.trackAdding: " + reference); //$NON-NLS-1$
			}
			IRemoteService object = null;
			boolean becameUntracked = false;
			/* Call customizer outside of synchronized region */
			try {
				object = customizer.addingService(reference);
				/*
				 * If the customizer throws an unchecked exception, it will
				 * propagate after the finally
				 */
			} finally {
				synchronized (this) {
					if (adding.remove(reference)) {
						/*
						 * if the service was not
						 * untracked during the
						 * customizer callback
						 */
						if (object != null) {
							this.put(reference, object);
							modified(); /* increment modification count */
							notifyAll();
							/*
							 * notify any waiters in
							 * waitForService
							 */
						}
					} else {
						becameUntracked = true;
					}
				}
			}
			/*
			 * The service became untracked during the customizer callback.
			 */
			if (becameUntracked) {
				if (TRACKED_DEBUG) {
					System.out.println("RemoteServiceTracker.Tracked.trackAdding[removed]: " + reference); //$NON-NLS-1$
				}
				/* Call customizer outside of synchronized region */
				customizer.removedService(reference, object);
				/*
				 * If the customizer throws an unchecked exception, it is safe
				 * to let it propagate
				 */
			}
		}

		/**
		 * Discontinue tracking the referenced service.
		 * 
		 * @param reference Reference to the tracked service.
		 */
		protected void untrack(IRemoteServiceReference reference) {
			IRemoteService object;
			synchronized (this) {
				if (initial.remove(reference)) {
					/*
					 * if this service is
					 * already in the list of
					 * initial references to
					 * process
					 */
					if (TRACKED_DEBUG) {
						System.out.println("RemoteServiceTracker.Tracked.untrack[removed from initial]: " + reference); //$NON-NLS-1$
					}
					return;
					/*
					 * we have removed it from the list and it will not
					 * be processed
					 */
				}
				if (adding.remove(reference)) {
					/*
					 * if the service is in the
					 * process of being added
					 */
					if (TRACKED_DEBUG) {
						System.out.println("RemoteServiceTracker.Tracked.untrack[being added]: " + reference); //$NON-NLS-1$
					}
					return;
					/*
					 * in case the service is untracked while in the
					 * process of adding
					 */
				}
				object = (IRemoteService) this.remove(reference);
				/*
				 * must remove from tracker
				 * before calling customizer
				 * callback
				 */
				if (object == null) { /* are we actually tracking the service */
					return;
				}
				modified(); /* increment modification count */
			}
			if (TRACKED_DEBUG) {
				System.out.println("RemoteServiceTracker.Tracked.untrack[removed]: " + reference); //$NON-NLS-1$
			}
			customizer.removedService(reference, object);
		}
	}

	class AllTracked extends Tracked {

		private static final long serialVersionUID = 9135607806678825054L;

		protected AllTracked() {
			super();
		}
	}

}
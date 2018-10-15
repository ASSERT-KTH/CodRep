if (multiplexer == null || !multiplexer.isConnected()) {

/* Copyright (c) 2006-2008 Jan S. Rellermeyer
 * Systems Group,
 * Department of Computer Science, ETH Zurich.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *    - Redistributions of source code must retain the above copyright notice,
 *      this list of conditions and the following disclaimer.
 *    - Redistributions in binary form must reproduce the above copyright
 *      notice, this list of conditions and the following disclaimer in the
 *      documentation and/or other materials provided with the distribution.
 *    - Neither the name of ETH Zurich nor the names of its contributors may be
 *      used to endorse or promote products derived from this software without
 *      specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 */
package ch.ethz.iks.r_osgi.impl;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.lang.reflect.Method;
import java.net.InetAddress;
import java.net.URL;
import java.net.UnknownHostException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.Dictionary;
import java.util.Enumeration;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.jar.JarEntry;
import java.util.jar.JarOutputStream;
import java.util.jar.Manifest;
import java.util.zip.CRC32;

import org.osgi.framework.Bundle;
import org.osgi.framework.BundleContext;
import org.osgi.framework.Constants;
import org.osgi.framework.Filter;
import org.osgi.framework.InvalidSyntaxException;
import org.osgi.framework.ServiceReference;
import org.osgi.service.event.EventAdmin;
import org.osgi.service.event.EventConstants;
import org.osgi.service.event.EventHandler;
import org.osgi.service.log.LogService;
import org.osgi.service.packageadmin.PackageAdmin;
import org.osgi.util.tracker.ServiceTracker;
import org.osgi.util.tracker.ServiceTrackerCustomizer;

import ch.ethz.iks.r_osgi.AsyncRemoteCallCallback;
import ch.ethz.iks.r_osgi.RemoteOSGiException;
import ch.ethz.iks.r_osgi.RemoteOSGiService;
import ch.ethz.iks.r_osgi.RemoteServiceEvent;
import ch.ethz.iks.r_osgi.RemoteServiceListener;
import ch.ethz.iks.r_osgi.RemoteServiceReference;
import ch.ethz.iks.r_osgi.Remoting;
import ch.ethz.iks.r_osgi.SurrogateRegistration;
import ch.ethz.iks.r_osgi.URI;
import ch.ethz.iks.r_osgi.channels.ChannelEndpoint;
import ch.ethz.iks.r_osgi.channels.ChannelEndpointManager;
import ch.ethz.iks.r_osgi.channels.NetworkChannel;
import ch.ethz.iks.r_osgi.channels.NetworkChannelFactory;
import ch.ethz.iks.r_osgi.messages.LeaseUpdateMessage;
import ch.ethz.iks.r_osgi.service_discovery.ServiceDiscoveryHandler;
import ch.ethz.iks.util.CollectionUtils;

/**
 * <p>
 * The R-OSGi core class. Handles remote channels and subscriptions from the
 * local framework. Local services can be released for remoting and then
 * discovered by remote peers.
 * </p>
 * 
 * @author Jan S. Rellermeyer, ETH Zurich
 * @since 0.1
 */
final class RemoteOSGiServiceImpl implements RemoteOSGiService, Remoting {

	static boolean IS_JAVA5 = false;

	static boolean IS_R4 = false;

	private final static Method getEntry;
	private final static Method getEntryPaths;
	private final static File base;

	static {
		final String verString = System.getProperty("java.class.version"); //$NON-NLS-1$
		if (verString != null && Float.parseFloat(verString) >= 49) {
			IS_JAVA5 = true;
		}
		final String osgiVerString = System
				.getProperty(Constants.FRAMEWORK_VERSION);
		if (osgiVerString != null && (!osgiVerString.trim().startsWith("1.3"))) { //$NON-NLS-1$
			IS_R4 = true;
		}
		Method m = null;
		Method n = null;
		try {
			m = Bundle.class
					.getMethod("getEntry", new Class[] { String.class });
			n = Bundle.class.getMethod("getEntryPaths",
					new Class[] { String.class });
		} catch (SecurityException e) {
			e.printStackTrace();
		} catch (NoSuchMethodException e) {
		}
		getEntry = m;
		getEntryPaths = n;

		base = getEntry == null ? RemoteOSGiActivator.getActivator()
				.getContext().getDataFile("../..") : null;
	}

	/**
	 * the R-OSGi standard port.
	 */
	static int R_OSGI_PORT = 9278;

	/**
	 * the R-OSGi port property.
	 */
	static final String R_OSGi_PORT_PROPERTY = "ch.ethz.iks.r_osgi.port"; //$NON-NLS-1$

	/**
	 * register the default tcp channel? If not set to "false", the channel gets
	 * registered.
	 */
	static final String REGISTER_DEFAULT_TCP_CHANNEL = "ch.ethz.iks.r_osgi.registerDefaultChannel"; //$NON-NLS-1$

	/**
	 * register the default tcp channel? If not set to "false", the channel gets
	 * registered.
	 */
	static final String THREADS_PER_ENDPOINT = "ch.ethz.iks.r_osgi.threadsPerEndpoint"; //$NON-NLS-1$

	/**
	 * constant that holds the property string for proxy debug option.
	 */
	static final String PROXY_DEBUG_PROPERTY = "ch.ethz.iks.r_osgi.debug.proxyGeneration"; //$NON-NLS-1$

	/**
	 * constant that holds the property string for message debug option.
	 */
	static final String MSG_DEBUG_PROPERTY = "ch.ethz.iks.r_osgi.debug.messages"; //$NON-NLS-1$

	/**
	 * constant that holds the property string for internal debug option.
	 */
	static final String DEBUG_PROPERTY = "ch.ethz.iks.r_osgi.debug.internal"; //$NON-NLS-1$

	/**
	 * marker for channel-registered event handlers so that they don't
	 * contribute to the peer's topic space.
	 */
	static final String R_OSGi_INTERNAL = "internal"; //$NON-NLS-1$

	/**
	 * file name of the manifest
	 */
	private static final String MANIFEST_FILE_NAME = "META-INF/MANIFEST.MF"; //$NON-NLS-1$

	/**
	 * We don't want it platform dependent because the Jars will always use the
	 * unix variant
	 */
	private static final String SEPARATOR_CHAR = "/"; //$NON-NLS-1$

	/**
	 * the buffer size
	 */
	private static final int BUFFER_SIZE = 2048;

	/**
	 * how many worker threads per endpoint?
	 */
	static final int MAX_THREADS_PER_ENDPOINT = Integer.getInteger(
			THREADS_PER_ENDPOINT, 2).intValue();

	/**
	 * log proxy generation debug output.
	 */
	static boolean PROXY_DEBUG;

	/**
	 * log message traffic.
	 */
	static boolean MSG_DEBUG;

	/**
	 * log method invocation debug output.
	 */
	static boolean DEBUG;

	/**
	 * the address of this peer.
	 */
	static String MY_ADDRESS;

	/**
	 * service reference -> remote service registration.
	 */
	static Map serviceRegistrations = new HashMap(1);

	/**
	 * next transaction id.
	 */
	private static int nextXid;

	/**
	 * OSGi log service instance.
	 */
	static LogService log;

	/**
	 * the event admin tracker
	 */
	static ServiceTracker eventAdminTracker;

	/**
	 * 
	 */
	private static ServiceTracker eventHandlerTracker;

	/**
	 * 
	 */
	private static ServiceTracker remoteServiceTracker;

	/**
	 * 
	 */
	private static ServiceTracker remoteServiceListenerTracker;

	/**
	 * 
	 */
	private static ServiceTracker networkChannelFactoryTracker;

	/**
	 * 
	 */
	private static ServiceTracker serviceDiscoveryHandlerTracker;

	/**
	 * Channel ID --> ChannelEndpoint.
	 */
	private static Map channels = new HashMap(0);

	/**
	 * Channel ID --> ChannelEndpointMultiplexer
	 */
	private static Map multiplexers = new HashMap(0);

	/**
	 * The package admin
	 */
	private static PackageAdmin pkgAdmin;

	/**
	 * creates a new RemoteOSGiServiceImpl instance.
	 * 
	 * @throws IOException
	 *             in case of IO problems.
	 */
	RemoteOSGiServiceImpl() throws IOException {
		// find out own IP address
		try {
			MY_ADDRESS = InetAddress.getAllByName(InetAddress.getLocalHost()
					.getHostName())[0].getHostAddress();
		} catch (final Throwable t) {
			MY_ADDRESS = System.getProperty("ch.ethz.iks.r_osgi.ip", //$NON-NLS-1$
					"127.0.0.1"); //$NON-NLS-1$
		}

		// set the debug switches
		final BundleContext context = RemoteOSGiActivator.getActivator()
				.getContext();
		String prop = context.getProperty(PROXY_DEBUG_PROPERTY);
		PROXY_DEBUG = prop != null ? Boolean.valueOf(prop).booleanValue()
				: false;
		prop = context.getProperty(MSG_DEBUG_PROPERTY);
		MSG_DEBUG = prop != null ? Boolean.valueOf(prop).booleanValue() : false;
		prop = context.getProperty(DEBUG_PROPERTY);
		DEBUG = prop != null ? Boolean.valueOf(prop).booleanValue() : false;

		if (log != null) {
			if (PROXY_DEBUG) {
				log.log(LogService.LOG_INFO, "PROXY DEBUG OUTPUTS ENABLED"); //$NON-NLS-1$
			}
			if (MSG_DEBUG) {
				log.log(LogService.LOG_INFO, "MESSAGE DEBUG OUTPUTS ENABLED"); //$NON-NLS-1$
			}
			if (DEBUG) {
				log.log(LogService.LOG_INFO, "INTERNAL DEBUG OUTPUTS ENABLED"); //$NON-NLS-1$
			}
		} else {
			if (PROXY_DEBUG || MSG_DEBUG || DEBUG) {
				System.err
						.println("WARNING: NO LOG SERVICE PRESENT, DEBUG PROPERTIES HAVE NO EFFECT ..."); //$NON-NLS-1$
				PROXY_DEBUG = false;
				MSG_DEBUG = false;
				DEBUG = false;
			}
		}

		// set port
		prop = context.getProperty(R_OSGi_PORT_PROPERTY);
		R_OSGI_PORT = prop != null ? Integer.parseInt(prop) : 9278;

		// initialize the transactionID with a random value
		nextXid = (short) Math.round(Math.random() * Short.MAX_VALUE);

		// get the package admin
		final ServiceReference ref = context
				.getServiceReference(PackageAdmin.class.getName());
		if (ref == null) {
			// TODO: handle this more gracefully
			throw new RuntimeException(
					"No package admin service available, R-OSGi terminates."); //$NON-NLS-1$
		}
		pkgAdmin = (PackageAdmin) context.getService(ref);

		setupTrackers(context);
	}

	private void setupTrackers(final BundleContext context) throws IOException {

		// initialize service trackers
		eventAdminTracker = new ServiceTracker(context, EventAdmin.class
				.getName(), null);
		eventAdminTracker.open();
		if (eventAdminTracker.getTrackingCount() == 0 && log != null) {
			log
					.log(LogService.LOG_WARNING,
							"NO EVENT ADMIN FOUND. REMOTE EVENT DELIVERY TEMPORARILY DISABLED."); //$NON-NLS-1$
		}

		try {
			eventHandlerTracker = new ServiceTracker(context, context
					.createFilter("(&(" + Constants.OBJECTCLASS + "=" //$NON-NLS-1$ //$NON-NLS-2$
							+ EventHandler.class.getName() + ")(!(" //$NON-NLS-1$
							+ R_OSGi_INTERNAL + "=*)))"), //$NON-NLS-1$
					new ServiceTrackerCustomizer() {

						public Object addingService(
								final ServiceReference reference) {

							// https://bugs.eclipse.org/bugs/show_bug.cgi?id=326033
							final String[] theTopics;
							Object topic = reference
									.getProperty(EventConstants.EVENT_TOPIC);
							if (topic instanceof String)
								theTopics = new String[] { (String) topic };
							else
								theTopics = (String[]) topic;

							final LeaseUpdateMessage lu = new LeaseUpdateMessage();
							lu.setType(LeaseUpdateMessage.TOPIC_UPDATE);
							lu.setServiceID(""); //$NON-NLS-1$
							lu.setPayload(new Object[] { theTopics, null });
							updateLeases(lu);

							return Arrays.asList(theTopics);
						}

						public void modifiedService(
								final ServiceReference reference,
								final Object oldTopics) {

							final List oldTopicList = (List) oldTopics;

							// https://bugs.eclipse.org/bugs/show_bug.cgi?id=326033
							final List newTopicList;
							Object topic = reference
									.getProperty(EventConstants.EVENT_TOPIC);
							if (topic instanceof String)
								newTopicList = Arrays
										.asList(new String[] { (String) topic });
							else
								newTopicList = Arrays.asList((String[]) topic);

							final Collection removed = CollectionUtils
									.rightDifference(newTopicList, oldTopicList);
							final Collection added = CollectionUtils
									.leftDifference(newTopicList, oldTopicList);
							final String[] addedTopics = (String[]) added
									.toArray(new String[removed.size()]);
							final String[] removedTopics = (String[]) removed
									.toArray(addedTopics);
							oldTopicList.removeAll(removed);
							oldTopicList.addAll(added);
							final LeaseUpdateMessage lu = new LeaseUpdateMessage();
							lu.setType(LeaseUpdateMessage.TOPIC_UPDATE);
							lu.setServiceID(""); //$NON-NLS-1$
							lu.setPayload(new Object[] { addedTopics,
									removedTopics });
							updateLeases(lu);
						}

						public void removedService(
								final ServiceReference reference,
								final Object oldTopics) {
							final List oldTopicsList = (List) oldTopics;
							final String[] removedTopics = (String[]) oldTopicsList
									.toArray(new String[oldTopicsList.size()]);
							final LeaseUpdateMessage lu = new LeaseUpdateMessage();
							lu.setType(LeaseUpdateMessage.TOPIC_UPDATE);
							lu.setServiceID(""); //$NON-NLS-1$
							lu.setPayload(new Object[] { null, removedTopics });
							updateLeases(lu);
						}
					});
			eventHandlerTracker.open();

			if (DEBUG) {
				log.log(LogService.LOG_DEBUG, "Local topic space " //$NON-NLS-1$
						+ Arrays.asList(getTopics()));
			}

			remoteServiceListenerTracker = new ServiceTracker(context,
					RemoteServiceListener.class.getName(), null);
			remoteServiceListenerTracker.open();

			serviceDiscoveryHandlerTracker = new ServiceTracker(context,
					ServiceDiscoveryHandler.class.getName(),
					new ServiceTrackerCustomizer() {

						public Object addingService(
								final ServiceReference reference) {
							// register all known services for discovery
							final ServiceDiscoveryHandler handler = (ServiceDiscoveryHandler) context
									.getService(reference);

							final RemoteServiceRegistration[] regs = (RemoteServiceRegistration[]) serviceRegistrations
									.values()
									.toArray(
											new RemoteServiceRegistration[serviceRegistrations
													.size()]);

							for (int i = 0; i < regs.length; i++) {
								handler
										.registerService(
												regs[i].getReference(),
												regs[i].getProperties(),
												URI
														.create("r-osgi://" //$NON-NLS-1$
																+ RemoteOSGiServiceImpl.MY_ADDRESS
																+ ":" //$NON-NLS-1$
																+ RemoteOSGiServiceImpl.R_OSGI_PORT
																+ "#" //$NON-NLS-1$
																+ regs[i]
																		.getServiceID()));
							}
							return handler;
						}

						public void modifiedService(
								final ServiceReference reference,
								final Object service) {

						}

						public void removedService(
								final ServiceReference reference,
								final Object service) {

						}

					});
			serviceDiscoveryHandlerTracker.open();

			remoteServiceTracker = new ServiceTracker(
					context,
					context.createFilter("(" //$NON-NLS-1$
							+ RemoteOSGiService.R_OSGi_REGISTRATION + "=*)"), new ServiceTrackerCustomizer() { //$NON-NLS-1$

						public Object addingService(
								final ServiceReference reference) {

							// FIXME: Surrogates have to be monitored
							// separately!!!
							final ServiceReference service = Arrays
									.asList(
											(String[]) reference
													.getProperty(Constants.OBJECTCLASS))
									.contains(
											SurrogateRegistration.class
													.getName()) ? (ServiceReference) reference
									.getProperty(SurrogateRegistration.SERVICE_REFERENCE)
									: reference;

							try {
								final RemoteServiceRegistration reg = new RemoteServiceRegistration(
										reference, service);

								if (log != null) {
									log.log(LogService.LOG_INFO, "REGISTERING " //$NON-NLS-1$
											+ reference
											+ " AS PROXIED SERVICES"); //$NON-NLS-1$
								}

								serviceRegistrations.put(service, reg);

								registerWithServiceDiscovery(reg);

								final LeaseUpdateMessage lu = new LeaseUpdateMessage();
								lu.setType(LeaseUpdateMessage.SERVICE_ADDED);
								lu.setServiceID(String.valueOf(reg
										.getServiceID()));
								lu.setPayload(new Object[] {
										reg.getInterfaceNames(),
										reg.getProperties() });
								updateLeases(lu);
								return service;
							} catch (final ClassNotFoundException e) {
								e.printStackTrace();
								throw new RemoteOSGiException(
										"Cannot find class " + service, e); //$NON-NLS-1$
							}
						}

						public void modifiedService(
								final ServiceReference reference,
								final Object service) {
							if (reference.getProperty(R_OSGi_REGISTRATION) == null) {
								removedService(reference, service);
								return;
							}
							final RemoteServiceRegistration reg = (RemoteServiceRegistration) serviceRegistrations
									.get(reference);

							registerWithServiceDiscovery(reg);

							final LeaseUpdateMessage lu = new LeaseUpdateMessage();
							lu.setType(LeaseUpdateMessage.SERVICE_MODIFIED);
							lu.setServiceID(String.valueOf(reg.getServiceID()));
							lu.setPayload(new Object[] { null,
									reg.getProperties() });
							updateLeases(lu);
						}

						public void removedService(
								final ServiceReference reference,
								final Object service) {

							final ServiceReference sref = Arrays
									.asList(
											(String[]) reference
													.getProperty(Constants.OBJECTCLASS))
									.contains(
											SurrogateRegistration.class
													.getName()) ? (ServiceReference) reference
									.getProperty(SurrogateRegistration.SERVICE_REFERENCE)
									: reference;

							final RemoteServiceRegistration reg = (RemoteServiceRegistration) serviceRegistrations
									.remove(sref);

							unregisterFromServiceDiscovery(reg);

							final LeaseUpdateMessage lu = new LeaseUpdateMessage();
							lu.setType(LeaseUpdateMessage.SERVICE_REMOVED);
							lu.setServiceID(String.valueOf(reg.getServiceID()));
							lu.setPayload(new Object[] { null, null });
							updateLeases(lu);
						}

					});
			remoteServiceTracker.open();

			networkChannelFactoryTracker = new ServiceTracker(
					context,
					context.createFilter("(" + Constants.OBJECTCLASS + "=" //$NON-NLS-1$ //$NON-NLS-2$
							+ NetworkChannelFactory.class.getName() + ")"), new ServiceTrackerCustomizer() { //$NON-NLS-1$

						public Object addingService(
								final ServiceReference reference) {
							final NetworkChannelFactory factory = (NetworkChannelFactory) context
									.getService(reference);
							try {
								factory.activate(RemoteOSGiServiceImpl.this);
							} catch (final IOException ioe) {
								if (log != null) {
									log.log(LogService.LOG_ERROR, ioe
											.getMessage(), ioe);
								}
							}
							return factory;
						}

						public void modifiedService(
								final ServiceReference reference,
								final Object factory) {
						}

						public void removedService(
								final ServiceReference reference,
								final Object factory) {
						}
					});
			networkChannelFactoryTracker.open();

		} catch (final InvalidSyntaxException ise) {
			ise.printStackTrace();
		}

	}

	private NetworkChannelFactory getNetworkChannelFactory(final String protocol)
			throws RemoteOSGiException {
		try {
			final Filter filter = RemoteOSGiActivator.getActivator()
					.getContext().createFilter(
							"(" //$NON-NLS-1$
									+ NetworkChannelFactory.PROTOCOL_PROPERTY
									+ "=" + protocol //$NON-NLS-1$
									+ ")"); //$NON-NLS-1$
			final ServiceReference[] refs = networkChannelFactoryTracker
					.getServiceReferences();

			if (refs != null) {
				for (int i = 0; i < refs.length; i++) {
					if (filter.match(refs[i])) {
						return (NetworkChannelFactory) networkChannelFactoryTracker
								.getService(refs[i]);
					}
				}
			}
			throw new RemoteOSGiException("No NetworkChannelFactory for " //$NON-NLS-1$
					+ protocol + " found."); //$NON-NLS-1$

		} catch (final InvalidSyntaxException e) {
			// does not happen
			e.printStackTrace();
			return null;
		}
	}

	/**
	 * connect to a remote OSGi host.
	 * 
	 * @param uri
	 *            the uri of the remote OSGi peer.
	 * @return the array of service urls of services offered by the remote peer.
	 * @throws RemoteOSGiException
	 *             in case of errors.
	 * @throws IOException
	 *             in case of IO problems.
	 * @since 0.6
	 */
	public RemoteServiceReference[] connect(final URI uri)
			throws RemoteOSGiException, IOException {

		final URI endpoint = URI.create(getChannelURI(uri));
		final ChannelEndpointImpl test = (ChannelEndpointImpl) channels
				.get(endpoint.toString());
		if (test != null) {
			test.usageCounter++;
			return test.getAllRemoteReferences(null);
		}

		final ChannelEndpointImpl channel;
		final String protocol = endpoint.getScheme();

		final NetworkChannelFactory factory = getNetworkChannelFactory(protocol);
		channel = new ChannelEndpointImpl(factory, endpoint);

		return channel.sendLease(getServices(), getTopics());
	}

	/**
	 * 
	 * @see ch.ethz.iks.r_osgi.RemoteOSGiService#getListeningPort(java.lang.String)
	 * @category RemoteOSGiService
	 */
	public int getListeningPort(final String protocol)
			throws RemoteOSGiException {
		final NetworkChannelFactory factory = getNetworkChannelFactory(protocol);
		return factory.getListeningPort(protocol);
	}

	/**
	 * @param endpoint
	 * @throws RemoteOSGiException
	 * 
	 */
	public void disconnect(final URI endpoint) throws RemoteOSGiException {
		final String channelURI = getChannelURI(endpoint).toString();
		final ChannelEndpointImpl channel = (ChannelEndpointImpl) channels
				.get(channelURI);
		if (channel != null) {
			if (channel.usageCounter == 1) {
				channel.dispose();
				multiplexers.remove(channelURI);
			} else {
				channel.usageCounter--;
			}
		}
	}

	/**
	 * 
	 * @see ch.ethz.iks.r_osgi.RemoteOSGiService#getRemoteServiceReference(ch.ethz.iks.r_osgi.URI)
	 */
	public RemoteServiceReference getRemoteServiceReference(final URI serviceURI) {
		final String uri = getChannelURI(serviceURI);
		ChannelEndpointImpl channel = (ChannelEndpointImpl) channels
				.get(getChannelURI(serviceURI));
		if (channel == null) {
			try {
				connect(serviceURI);
				channel = (ChannelEndpointImpl) channels.get(uri);
			} catch (final IOException ioe) {
				throw new RemoteOSGiException("Cannot connect to " + uri); //$NON-NLS-1$
			}
		}
		return channel.getRemoteReference(serviceURI.toString());
	}

	/**
	 * 
	 * @see ch.ethz.iks.r_osgi.RemoteOSGiService#getRemoteServiceReferences(ch.ethz.iks.r_osgi.URI,
	 *      java.lang.String, org.osgi.framework.Filter)
	 */
	public RemoteServiceReference[] getRemoteServiceReferences(
			final URI service, final String clazz, final Filter filter) {
		final String uri = getChannelURI(service);
		ChannelEndpointImpl channel = (ChannelEndpointImpl) channels.get(uri);
		if (channel == null) {
			try {
				connect(service);
				channel = (ChannelEndpointImpl) channels.get(uri);
			} catch (final IOException ioe) {
				throw new RemoteOSGiException("Cannot connect to " + uri); //$NON-NLS-1$
			}
		}
		if (clazz == null) {
			return channel.getAllRemoteReferences(null);
		}
		try {
			return channel.getAllRemoteReferences(RemoteOSGiActivator
					.getActivator().getContext()
					.createFilter(filter != null ? "(&" + filter + "(" //$NON-NLS-1$ //$NON-NLS-2$
							+ Constants.OBJECTCLASS + "=" + clazz + "))" : "(" //$NON-NLS-1$ //$NON-NLS-2$ //$NON-NLS-3$
							+ Constants.OBJECTCLASS + "=" + clazz + ")")); //$NON-NLS-1$ //$NON-NLS-2$
		} catch (final InvalidSyntaxException ise) {
			ise.printStackTrace();
			return null;
		}
	}

	/**
	 * 
	 * @param ref
	 *            the <code>RemoteServiceReference</code>.
	 * @return the service object or <code>null</code> if the service is not
	 *         (yet) present.
	 * @see ch.ethz.iks.r_osgi.RemoteOSGiService#getRemoteService(ch.ethz.iks.r_osgi.RemoteServiceReference)
	 * @category RemoteOSGiService
	 * @since 0.6
	 */
	public Object getRemoteService(final RemoteServiceReference ref) {
		if (ref == null) {
			throw new IllegalArgumentException("Remote Reference is null."); //$NON-NLS-1$
		}
		ServiceReference sref = getFetchedServiceReference(ref);
		if (sref == null) {
			fetchService(ref);
			sref = getFetchedServiceReference(ref);
		}
		return sref == null ? null : RemoteOSGiActivator.getActivator()
				.getContext().getService(sref);
	}

	/**
	 * 
	 * @throws InterruptedException
	 * @see ch.ethz.iks.r_osgi.RemoteOSGiService#getRemoteServiceBundle(ch.ethz.iks.r_osgi.RemoteServiceReference,
	 *      int)
	 * @since 1.0.0.RC4
	 */
	public Object getRemoteServiceBundle(final RemoteServiceReference ref,
			final int timeout) throws InterruptedException {
		if (ref == null) {
			throw new IllegalArgumentException("Remote Reference is null."); //$NON-NLS-1$
		}
		getChannel(ref.getURI()).getCloneBundle(ref);
		if (timeout < 0) {
			return null;
		}
		// TODO: FIXME use at least all service interfaces
		final ServiceTracker tracker = new ServiceTracker(RemoteOSGiActivator
				.getActivator().getContext(), ref.getServiceInterfaces()[0],
				null);
		tracker.open();
		tracker.waitForService(0);
		// TODO: FIXME compare that the service is actually the one from the
		// fetched
		// bundle!
		return tracker.getService();
	}

	/**
	 * 
	 * @param ref
	 *            the <code>RemoteServiceReference</code> to the service.
	 * @return the service reference of the service (or service proxy) or
	 *         <code>null</code> if the service is not (yet) present.
	 * @see ch.ethz.iks.r_osgi.RemoteOSGiService#getFetchedServiceReference(ch.ethz.iks.r_osgi.RemoteServiceReference)
	 * @category RemoteOSGiService
	 * @since 0.6
	 */
	private ServiceReference getFetchedServiceReference(
			final RemoteServiceReference ref) {
		try {
			final ServiceReference[] refs = RemoteOSGiActivator.getActivator()
					.getContext().getServiceReferences(
							ref.getServiceInterfaces()[0], "(" //$NON-NLS-1$
									+ SERVICE_URI + "=" + ref.getURI() + ")"); //$NON-NLS-1$ //$NON-NLS-2$
			if (refs != null) {
				return refs[0];
			}
		} catch (final InvalidSyntaxException doesNotHappen) {
			doesNotHappen.printStackTrace();
		}
		return null;
	}

	/**
	 * fetch the discovered remote service. The service will be fetched from the
	 * service providing host and a proxy bundle is registered with the local
	 * framework.
	 * 
	 * @param service
	 *            the <code>ServiceURL</code>.
	 * @throws RemoteOSGiException
	 *             if the fetching fails.
	 * @see ch.ethz.iks.r_osgi.RemoteOSGiService#getProxyBundle(ch.ethz.iks.slp.ServiceURL)
	 * @since 0.1
	 * @category RemoteOSGiService
	 */
	private void fetchService(final RemoteServiceReference ref)
			throws RemoteOSGiException {
		try {
			ChannelEndpointImpl channel;
			channel = ((RemoteServiceReferenceImpl) ref).getChannel();
			channel.getProxyBundle(ref);
		} catch (final UnknownHostException e) {
			throw new RemoteOSGiException(
					"Cannot resolve host " + ref.getURI(), e); //$NON-NLS-1$
		} catch (final IOException ioe) {
			throw new RemoteOSGiException("Proxy generation error", ioe); //$NON-NLS-1$
		}
	}

	static ChannelEndpointImpl getChannel(final URI uri) {
		return (ChannelEndpointImpl) channels.get(getChannelURI(uri));
	}

	/**
	 * 
	 * @see ch.ethz.iks.r_osgi.Remoting#getEndpoint(java.lang.String)
	 * @category Remoting
	 */
	public ChannelEndpoint getEndpoint(final String uri) {
		return getMultiplexer(uri);
	}

	/**
	 * 
	 * @see ch.ethz.iks.r_osgi.RemoteOSGiService#getEndpointManager(ch.ethz.iks.r_osgi.URI)
	 * @category Remoting
	 */
	public ChannelEndpointManager getEndpointManager(
			final URI remoteEndpointAddress) {
		return getMultiplexer(remoteEndpointAddress.toString());
	}

	/**
	 * 
	 * @param uri
	 * @return
	 */
	private ChannelEndpointMultiplexer getMultiplexer(final String uri) {
		final String channel = getChannelURI(URI.create(uri));
		ChannelEndpointMultiplexer multiplexer = (ChannelEndpointMultiplexer) multiplexers
				.get(channel);
		if (multiplexer == null || multiplexer.isConnected()) {
			multiplexer = new ChannelEndpointMultiplexer(
					(ChannelEndpointImpl) channels.get(channel));
			multiplexers.put(channel, multiplexer);
		}
		return multiplexer;
	}

	/**
	 * 
	 * @param serviceURI
	 * @return
	 */
	private static String getChannelURI(final URI serviceURI) {
		return URI.create(
				serviceURI.getScheme() + "://" + serviceURI.getHost() + ":" //$NON-NLS-1$ //$NON-NLS-2$
						+ serviceURI.getPort()).toString();
	}

	/**
	 * the method is called when the R-OSGi bundle is about to be stopped.
	 * removes all registered proxy bundles.
	 */
	void cleanup() {
		final ChannelEndpoint[] c = (ChannelEndpoint[]) channels.values()
				.toArray(new ChannelEndpoint[channels.size()]);
		channels.clear();
		for (int i = 0; i < c.length; i++) {
			c[i].dispose();
		}
		final Object[] factories = networkChannelFactoryTracker.getServices();
		if (factories != null) {
			for (int i = 0; i < factories.length; i++) {
				try {
					((NetworkChannelFactory) factories[i]).deactivate(this);
				} catch (final IOException ioe) {
					if (log != null) {
						log.log(LogService.LOG_ERROR, ioe.getMessage(), ioe);
					}
				}
			}
		}
		eventAdminTracker.close();
		remoteServiceTracker.close();
		serviceDiscoveryHandlerTracker.close();
		remoteServiceListenerTracker.close();
		networkChannelFactoryTracker.close();
	}

	/**
	 * get all provided (remote-enabled) services of this peer.
	 * 
	 * @return return the services.
	 */
	static RemoteServiceRegistration[] getServices() {
		return (RemoteServiceRegistration[]) serviceRegistrations.values()
				.toArray(
						new RemoteServiceRegistration[serviceRegistrations
								.size()]);
	}

	/**
	 * 
	 * @param serviceID
	 * @return
	 */
	static RemoteServiceRegistration getServiceRegistration(
			final String serviceID) {

		final String filter = "".equals(serviceID) ? null : '(' //$NON-NLS-1$
				+ Constants.SERVICE_ID + "=" + serviceID + ")"; //$NON-NLS-1$ //$NON-NLS-2$

		try {
			final ServiceReference[] refs = RemoteOSGiActivator.getActivator()
					.getContext().getServiceReferences(null, filter);
			if (refs == null) {
				if (log != null) {
					log.log(LogService.LOG_WARNING, "COULD NOT FIND " + filter); //$NON-NLS-1$
				}
				return null;
			}
			return (RemoteServiceRegistration) serviceRegistrations
					.get(refs[0]);
		} catch (final InvalidSyntaxException e) {
			e.printStackTrace();
			return null;
		}
	}

	/**
	 * get all topics for which event handlers are registered.
	 * 
	 * @return the topics.
	 */
	static String[] getTopics() {
		final Object[] topicLists = eventHandlerTracker.getServices();
		final List topics = new ArrayList();
		if (topicLists != null) {
			for (int i = 0; i < topicLists.length; i++) {
				topics.addAll((List) topicLists[i]);
			}
		}
		return (String[]) topics.toArray(new String[topics.size()]);
	}

	/**
	 * get the next transaction id.
	 * 
	 * @return the next xid.
	 */
	static synchronized int nextXid() {
		if (nextXid == -1) {
			nextXid = 0;
		}
		return (++nextXid);
	}

	/**
	 * register a channel.
	 * 
	 * @param channel
	 *            the local endpoint of the channel.
	 */
	static void registerChannelEndpoint(final ChannelEndpoint channel) {
		channels.put(channel.getRemoteAddress().toString(), channel);
	}

	/**
	 * unregister a channel.
	 * 
	 * @param channel
	 *            the local endpoint of the channel.
	 */
	static void unregisterChannelEndpoint(final String channelURI) {
		channels.remove(channelURI);
	}

	/**
	 * update the leases.
	 */
	static void updateLeases(final LeaseUpdateMessage msg) {
		final ChannelEndpointImpl[] endpoints = (ChannelEndpointImpl[]) channels
				.values().toArray(new ChannelEndpointImpl[channels.size()]);
		for (int i = 0; i < endpoints.length; i++) {
			endpoints[i].sendLeaseUpdate(msg);
		}
	}

	/**
	 * 
	 * @param event
	 */
	static void notifyRemoteServiceListeners(final RemoteServiceEvent event) {
		final ServiceReference[] refs = remoteServiceListenerTracker
				.getServiceReferences();
		if (refs == null) {
			return;
		}
		final Set serviceIfaces = new HashSet(Arrays.asList(event
				.getRemoteReference().getServiceInterfaces()));
		for (int i = 0; i < refs.length; i++) {
			final String[] ifaces = (String[]) refs[i]
					.getProperty(RemoteServiceListener.SERVICE_INTERFACES);
			if (ifaces == null) {
				match(refs[i], event);
			} else {
				for (int j = 0; j < ifaces.length; j++) {
					if (serviceIfaces.contains(ifaces[j])) {
						match(refs[i], event);
						break;
					}
				}
			}
		}
	}

	/**
	 * 
	 * @param ref
	 * @param event
	 */
	private static void match(final ServiceReference ref,
			final RemoteServiceEvent event) {
		final Filter filter = (Filter) ref
				.getProperty(RemoteServiceListener.FILTER);
		if (filter == null
				|| filter.match(((RemoteServiceReferenceImpl) event
						.getRemoteReference()).getProperties())) {
			final RemoteServiceListener listener = (RemoteServiceListener) remoteServiceListenerTracker
					.getService(ref);
			if (listener != null) {
				listener.remoteServiceEvent(event);
			}
		}
	}

	/**
	 * register a service with the remote service discovery layer.
	 */
	void registerWithServiceDiscovery(final RemoteServiceRegistration reg) {
		// register the service with all service
		// discovery handler
		final Object[] handler = serviceDiscoveryHandlerTracker.getServices();

		if (handler != null) {
			for (int i = 0; i < handler.length; i++) {
				final Dictionary props = reg.getProperties();
				((ServiceDiscoveryHandler) handler[i]).registerService(reg
						.getReference(), props, URI.create("r-osgi://" //$NON-NLS-1$
						+ RemoteOSGiServiceImpl.MY_ADDRESS + ":" //$NON-NLS-1$
						+ RemoteOSGiServiceImpl.R_OSGI_PORT + "#" //$NON-NLS-1$
						+ reg.getServiceID()));
			}
		}

	}

	/**
	 * unregister a service from the service discovery layer.
	 * 
	 * @param reg
	 *            the remote service registration.
	 */
	void unregisterFromServiceDiscovery(final RemoteServiceRegistration reg) {
		final Object[] handler = serviceDiscoveryHandlerTracker.getServices();
		if (handler != null) {
			for (int i = 0; i < handler.length; i++) {
				((ServiceDiscoveryHandler) handler[i]).unregisterService(reg
						.getReference());
			}
		}
	}

	static byte[] getBundle(final Bundle bundle) throws IOException {
		final byte[] buffer = new byte[BUFFER_SIZE];
		final CRC32 crc = getEntry == null ? null : new CRC32();
		final ByteArrayOutputStream out = getEntry == null ? new ByteArrayOutputStream(
				BUFFER_SIZE)
				: null;

		if (getEntry == null) {
			return getBundleConcierge(bundle, buffer, out);
		}

		try {
			// workaround for Eclipse
			final String prefix = getEntry.invoke(bundle,
					new Object[] { pkgAdmin.getExportedPackages(bundle)[0]
							.getName().replace('.', '/') }) == null ? "/bin" //$NON-NLS-1$
					: ""; //$NON-NLS-1$

			return generateBundle(bundle, prefix, buffer, crc);
		} catch (Exception e) {
			e.printStackTrace();
			throw new IOException(e.getMessage());
		}
	}

	static byte[][] getBundlesForPackages(final String[] packages)
			throws IOException {
		final HashSet visitedBundles = new HashSet(packages.length);
		final ArrayList bundleBytes = new ArrayList(packages.length);

		// we reuse the buffer and other objects during the iteration over
		// bundles and entries to improve
		// the performance on smaller VMs.
		final byte[] buffer = new byte[BUFFER_SIZE];
		final CRC32 crc = getEntry == null ? null : new CRC32();
		final ByteArrayOutputStream out = getEntry == null ? new ByteArrayOutputStream(
				BUFFER_SIZE)
				: null;

		// TODO: for R4, handle multiple versions
		for (int i = 0; i < packages.length; i++) {
			final Bundle bundle = pkgAdmin.getExportedPackage(packages[i])
					.getExportingBundle();
			if (visitedBundles.contains(bundle)) {
				continue;
			}
			visitedBundles.add(bundle);

			if (getEntry == null) {
				bundleBytes.add(getBundleConcierge(bundle, buffer, out));
			} else {

				// workaround for Eclipse
				try {
					final String prefix = getEntry.invoke(bundle,
							new Object[] { packages[i].replace('.', '/') }) == null ? "/bin" //$NON-NLS-1$
							: ""; //$NON-NLS-1$
					bundleBytes
							.add(generateBundle(bundle, prefix, buffer, crc));
				} catch (Exception e) {
					e.printStackTrace();
					throw new IOException(e.getMessage());
				}
			}

		}
		return (byte[][]) bundleBytes.toArray(new byte[bundleBytes.size()][]);
	}

	private static byte[] getBundleConcierge(final Bundle bundle,
			final byte[] buffer, final ByteArrayOutputStream out)
			throws IOException {
		FileInputStream in = new FileInputStream(new File(base, bundle
				.getBundleId()
				+ "/bundle"));
		out.reset();

		int read;
		while ((read = in.read(buffer, 0, 2048)) > -1) {
			out.write(buffer, 0, read);
		}

		return out.toByteArray();
	}

	static boolean checkPackageImport(final String pkg) {
		// TODO: use versions if on R4
		if (pkg.startsWith("org.osgi")) {
			return true;
		}
		return pkgAdmin.getExportedPackage(pkg) != null;
	}

	private static byte[] generateBundle(final Bundle bundle,
			final String prefix, final byte[] buffer, final CRC32 crc)
			throws Exception {

		final URL url = (URL) getEntry.invoke(bundle,
				new Object[] { SEPARATOR_CHAR + MANIFEST_FILE_NAME });
		final Manifest mf = new Manifest();
		mf.read(url.openStream());

		final ByteArrayOutputStream bout = new ByteArrayOutputStream();
		final JarOutputStream out = new JarOutputStream(bout, mf);

		scan(bundle, prefix, "", out, buffer, crc); //$NON-NLS-1$

		out.flush();
		out.finish();
		out.close();
		return bout.toByteArray();
	}

	private static void scan(final Bundle bundle, final String prefix,
			final String path, final JarOutputStream out, final byte[] buffer,
			final CRC32 crc) throws Exception {

		final Enumeration e = (Enumeration) getEntryPaths.invoke(bundle,
				new Object[] { prefix + SEPARATOR_CHAR + path });
		if (e == null) {
			return;
		}
		while (e.hasMoreElements()) {
			final String entry = ((String) e.nextElement()).substring(prefix
					.length());
			if (entry.equals(MANIFEST_FILE_NAME)) {
				continue;
			} else if (entry.endsWith(SEPARATOR_CHAR)) {
				scan(bundle, prefix, entry, out, buffer, crc);
			} else {
				final URL url = bundle.getResource(prefix + "/" + entry);
				final InputStream in = url.openStream();
				int read;
				int totallyRead = 0;

				final JarEntry jarEntry = new JarEntry(entry);
				out.putNextEntry(jarEntry);
				crc.reset();

				while ((read = in.read(buffer, 0, 2048)) > -1) {
					totallyRead += read;
					out.write(buffer, 0, read);
					crc.update(buffer, 0, read);
				}

				jarEntry.setSize(totallyRead);
				jarEntry.setCrc(crc.getValue());
				out.flush();
				out.closeEntry();
			}
		}
	} 

	/**
	 * 
	 * 
	 * @see ch.ethz.iks.r_osgi.Remoting#createEndpoint(ch.ethz.iks.r_osgi.channels.NetworkChannel)
	 * @category RemoteOSGiService
	 */
	public void createEndpoint(final NetworkChannel channel) {
		new ChannelEndpointImpl(channel);
	}

	/**
	 * 
	 * @see ch.ethz.iks.r_osgi.RemoteOSGiService#ungetRemoteService(ch.ethz.iks.r_osgi.RemoteServiceReference)
	 * @category RemoteOSGiService
	 */
	public void ungetRemoteService(
			final RemoteServiceReference remoteServiceReference) {
		((RemoteServiceReferenceImpl) remoteServiceReference).getChannel()
				.ungetRemoteService(remoteServiceReference.getURI());

	}

	public void asyncRemoteCall(URI service, String methodSignature,
			Object[] args, AsyncRemoteCallCallback callback) {
		final ChannelEndpointImpl endpoint = getChannel(service);
		endpoint.asyncRemoteCall(service.getFragment(), methodSignature, args,
				callback);
	}

}
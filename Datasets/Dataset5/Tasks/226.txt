return URI.create(serviceURI.getScheme() + "://" + serviceURI.getHost() + ":" + serviceURI.getPort()).toString();

/* Copyright (c) 2006-2008 Jan S. Rellermeyer
 * Information and Communication Systems Research Group (IKS),
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

import java.io.IOException;
import java.net.InetAddress;
import java.net.UnknownHostException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.Dictionary;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.osgi.framework.Constants;
import org.osgi.framework.Filter;
import org.osgi.framework.InvalidSyntaxException;
import org.osgi.framework.ServiceReference;
import org.osgi.service.event.EventAdmin;
import org.osgi.service.event.EventConstants;
import org.osgi.service.event.EventHandler;
import org.osgi.service.log.LogService;
import org.osgi.util.tracker.ServiceTracker;
import org.osgi.util.tracker.ServiceTrackerCustomizer;

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
	private static Map serviceRegistrations = new HashMap(1);

	/**
	 * next transaction id.
	 */
	private static short nextXid;

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
	 * creates a new RemoteOSGiServiceImpl instance.
	 * 
	 * @throws IOException
	 *             in case of IO problems.
	 */
	RemoteOSGiServiceImpl() throws IOException {
		// find out own IP address
		// TODO: allow configuration
		MY_ADDRESS = InetAddress.getAllByName(InetAddress.getLocalHost().getHostName())[0].getHostAddress();

		// set the debug switches
		String prop = RemoteOSGiActivator.context.getProperty(PROXY_DEBUG_PROPERTY);
		PROXY_DEBUG = prop != null ? Boolean.valueOf(prop).booleanValue() : false;
		prop = RemoteOSGiActivator.context.getProperty(MSG_DEBUG_PROPERTY);
		MSG_DEBUG = prop != null ? Boolean.valueOf(prop).booleanValue() : false;
		prop = RemoteOSGiActivator.context.getProperty(DEBUG_PROPERTY);
		DEBUG = prop != null ? Boolean.valueOf(prop).booleanValue() : false;

		if (log != null) {
			if (PROXY_DEBUG) {
				log.log(LogService.LOG_INFO, "PROXY DEBUG OUTPUTS ENABLED");
			}
			if (MSG_DEBUG) {
				log.log(LogService.LOG_INFO, "MESSAGE DEBUG OUTPUTS ENABLED");
			}
			if (DEBUG) {
				log.log(LogService.LOG_INFO, "INTERNAL DEBUG OUTPUTS ENABLED");
			}
		} else {
			if (PROXY_DEBUG || MSG_DEBUG || DEBUG) {
				System.err.println("NO LOG SERVICE PRESENT, DEBUG PROPERTIES HAVE NO EFFECT ...");
				PROXY_DEBUG = false;
				MSG_DEBUG = false;
				DEBUG = false;
			}
		}

		// set port
		prop = RemoteOSGiActivator.context.getProperty(R_OSGi_PORT_PROPERTY);
		R_OSGI_PORT = prop != null ? Integer.parseInt(prop) : 9278;

		// initialize the transactionID with a random value
		nextXid = (short) Math.round(Math.random() * Short.MAX_VALUE);

		setupTrackers();
	}

	private void setupTrackers() throws IOException {

		// initialize service trackers
		eventAdminTracker = new ServiceTracker(RemoteOSGiActivator.context, EventAdmin.class.getName(), null);
		eventAdminTracker.open();
		if (eventAdminTracker.getTrackingCount() == 0 && log != null) {
			log.log(LogService.LOG_WARNING, "NO EVENT ADMIN FOUND. REMOTE EVENT DELIVERY TEMPORARILY DISABLED.");
		}

		try {
			eventHandlerTracker = new ServiceTracker(RemoteOSGiActivator.context, RemoteOSGiActivator.context.createFilter("(&(" + Constants.OBJECTCLASS + "=" + EventHandler.class.getName() + ")(!(" + R_OSGi_INTERNAL + "=*)))"), new ServiceTrackerCustomizer() {

				public Object addingService(ServiceReference reference) {
					final String[] theTopics = (String[]) reference.getProperty(EventConstants.EVENT_TOPIC);
					final LeaseUpdateMessage lu = new LeaseUpdateMessage();
					lu.setType(LeaseUpdateMessage.TOPIC_UPDATE);
					lu.setServiceID("");
					lu.setPayload(new Object[] {theTopics, null});
					updateLeases(lu);

					return Arrays.asList(theTopics);
				}

				public void modifiedService(ServiceReference reference, Object oldTopics) {

					final List oldTopicList = (List) oldTopics;
					final List newTopicList = Arrays.asList((String[]) reference.getProperty(EventConstants.EVENT_TOPIC));
					final Collection removed = CollectionUtils.rightDifference(newTopicList, oldTopicList);
					final Collection added = CollectionUtils.leftDifference(newTopicList, oldTopicList);
					final String[] addedTopics = (String[]) added.toArray(new String[removed.size()]);
					final String[] removedTopics = (String[]) removed.toArray(addedTopics);
					oldTopicList.removeAll(removed);
					oldTopicList.addAll(added);
					final LeaseUpdateMessage lu = new LeaseUpdateMessage();
					lu.setType(LeaseUpdateMessage.TOPIC_UPDATE);
					lu.setServiceID("");
					lu.setPayload(new Object[] {addedTopics, removedTopics});
					updateLeases(lu);
				}

				public void removedService(ServiceReference reference, Object oldTopics) {
					final List oldTopicsList = (List) oldTopics;
					final String[] removedTopics = (String[]) oldTopicsList.toArray(new String[oldTopicsList.size()]);
					final LeaseUpdateMessage lu = new LeaseUpdateMessage();
					lu.setType(LeaseUpdateMessage.TOPIC_UPDATE);
					lu.setServiceID("");
					lu.setPayload(new Object[] {null, removedTopics});
					updateLeases(lu);
				}
			});
			eventHandlerTracker.open();

			if (DEBUG) {
				log.log(LogService.LOG_DEBUG, "Local topic space " + Arrays.asList(getTopics()));
			}

			remoteServiceListenerTracker = new ServiceTracker(RemoteOSGiActivator.context, RemoteServiceListener.class.getName(), null);
			remoteServiceListenerTracker.open();

			serviceDiscoveryHandlerTracker = new ServiceTracker(RemoteOSGiActivator.context, ServiceDiscoveryHandler.class.getName(), new ServiceTrackerCustomizer() {

				public Object addingService(ServiceReference reference) {
					// register all known services for discovery
					final ServiceDiscoveryHandler handler = (ServiceDiscoveryHandler) RemoteOSGiActivator.context.getService(reference);

					final RemoteServiceRegistration[] regs = (RemoteServiceRegistration[]) serviceRegistrations.values().toArray(new RemoteServiceRegistration[serviceRegistrations.size()]);

					for (int i = 0; i < regs.length; i++) {
						handler.registerService(regs[i].getReference(), regs[i].getProperties(), URI.create("r-osgi://" + RemoteOSGiServiceImpl.MY_ADDRESS + ":" + RemoteOSGiServiceImpl.R_OSGI_PORT + "#" + regs[i].getServiceID()));
					}
					return handler;
				}

				public void modifiedService(ServiceReference reference, Object service) {

				}

				public void removedService(ServiceReference reference, Object service) {

				}

			});
			serviceDiscoveryHandlerTracker.open();

			remoteServiceTracker = new ServiceTracker(RemoteOSGiActivator.context, RemoteOSGiActivator.context.createFilter("(" + RemoteOSGiService.R_OSGi_REGISTRATION + "=*)"), new ServiceTrackerCustomizer() {

				public Object addingService(final ServiceReference reference) {

					// FIXME: Surrogates have to be monitored
					// separately!!!
					final ServiceReference service = Arrays.asList((String[]) reference.getProperty(Constants.OBJECTCLASS)).contains(SurrogateRegistration.class.getName()) ? (ServiceReference) reference.getProperty(SurrogateRegistration.SERVICE_REFERENCE) : reference;

					try {
						final RemoteServiceRegistration reg = new RemoteServiceRegistration(reference, service);

						if (log != null) {
							log.log(LogService.LOG_INFO, "REGISTERING " + reg + " AS PROXIED SERVICES");
						}

						serviceRegistrations.put(service, reg);

						registerWithServiceDiscovery(reg);

						final LeaseUpdateMessage lu = new LeaseUpdateMessage();
						lu.setType(LeaseUpdateMessage.SERVICE_ADDED);
						lu.setServiceID(String.valueOf(reg.getServiceID()));
						lu.setPayload(new Object[] {reg.getInterfaceNames(), reg.getProperties()});
						updateLeases(lu);
						return service;
					} catch (final ClassNotFoundException e) {
						e.printStackTrace();
						throw new RemoteOSGiException("Cannot find class " + service, e);
					}
				}

				public void modifiedService(ServiceReference reference, Object service) {
					if (reference.getProperty(R_OSGi_REGISTRATION) == null) {
						removedService(reference, service);
						return;
					}
					final RemoteServiceRegistration reg = (RemoteServiceRegistration) serviceRegistrations.get(reference);

					registerWithServiceDiscovery(reg);

					final LeaseUpdateMessage lu = new LeaseUpdateMessage();
					lu.setType(LeaseUpdateMessage.SERVICE_MODIFIED);
					lu.setServiceID(String.valueOf(reg.getServiceID()));
					lu.setPayload(new Object[] {null, reg.getProperties()});
					updateLeases(lu);
				}

				public void removedService(ServiceReference reference, Object service) {

					final ServiceReference sref = Arrays.asList((String[]) reference.getProperty(Constants.OBJECTCLASS)).contains(SurrogateRegistration.class.getName()) ? (ServiceReference) reference.getProperty(SurrogateRegistration.SERVICE_REFERENCE) : reference;

					final RemoteServiceRegistration reg = (RemoteServiceRegistration) serviceRegistrations.remove(sref);

					unregisterFromServiceDiscovery(reg);

					final LeaseUpdateMessage lu = new LeaseUpdateMessage();
					lu.setType(LeaseUpdateMessage.SERVICE_REMOVED);
					lu.setServiceID(String.valueOf(reg.getServiceID()));
					lu.setPayload(new Object[] {null, null});
					updateLeases(lu);
				}

			});
			remoteServiceTracker.open();

			networkChannelFactoryTracker = new ServiceTracker(RemoteOSGiActivator.context, RemoteOSGiActivator.context.createFilter("(" + Constants.OBJECTCLASS + "=" + NetworkChannelFactory.class.getName() + ")"), new ServiceTrackerCustomizer() {

				public Object addingService(ServiceReference reference) {
					final NetworkChannelFactory factory = (NetworkChannelFactory) RemoteOSGiActivator.context.getService(reference);
					try {
						factory.activate(RemoteOSGiServiceImpl.this);
					} catch (final IOException ioe) {
						if (log != null) {
							log.log(LogService.LOG_ERROR, ioe.getMessage(), ioe);
						}
					}
					return factory;
				}

				public void modifiedService(ServiceReference reference, Object factory) {
				}

				public void removedService(ServiceReference reference, Object factory) {
				}
			});
			networkChannelFactoryTracker.open();

		} catch (final InvalidSyntaxException ise) {
			ise.printStackTrace();
		}

	}

	/**
	 * connect to a remote OSGi host.
	 * @param uri uri of endpoint to connect to.
	 * 
	 * @return the array of service urls of services offered by the remote peer.
	 * @throws RemoteOSGiException
	 *             in case of errors.
	 * @since 0.6
	 */
	public RemoteServiceReference[] connect(final URI uri) throws RemoteOSGiException {

		final URI endpoint = URI.create(getChannelURI(uri));
		final ChannelEndpointImpl test = (ChannelEndpointImpl) channels.get(endpoint.toString());
		if (test != null) {
			test.usageCounter++;
			return test.getAllRemoteReferences(null);
		}

		try {
			final ChannelEndpointImpl channel;
			final String protocol = endpoint.getScheme();

			final Filter filter = RemoteOSGiActivator.context.createFilter("(" + NetworkChannelFactory.PROTOCOL_PROPERTY + "=" + protocol + ")");
			final ServiceReference[] refs = networkChannelFactoryTracker.getServiceReferences();
			if (refs != null) {
				for (int i = 0; i < refs.length; i++) {
					if (filter.match(refs[i])) {
						final NetworkChannelFactory factory = (NetworkChannelFactory) networkChannelFactoryTracker.getService(refs[i]);
						channel = new ChannelEndpointImpl(factory, endpoint);
						return channel.sendLease(getServices(), getTopics());
					}
				}
			}
			throw new RemoteOSGiException("No NetworkChannelFactory for " + protocol + " found.");
		} catch (final IOException ioe) {
			ioe.printStackTrace();
			throw new RemoteOSGiException("Connection to " + endpoint + " failed", ioe);
		} catch (final InvalidSyntaxException e) {
			// does not happen
			e.printStackTrace();
			return null;
		}
	}

	/**
	 * @param endpoint 
	 * @throws RemoteOSGiException 
	 * 
	 */
	public void disconnect(final URI endpoint) throws RemoteOSGiException {
		final String channelURI = getChannelURI(endpoint).toString();
		final ChannelEndpointImpl channel = (ChannelEndpointImpl) channels.get(channelURI);
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
		ChannelEndpointImpl channel = (ChannelEndpointImpl) channels.get(getChannelURI(serviceURI));
		if (channel == null) {
			connect(serviceURI);
			channel = (ChannelEndpointImpl) channels.get(uri);
		}
		return channel.getRemoteReference(serviceURI.toString());
	}

	/**
	 * 
	 * @see ch.ethz.iks.r_osgi.RemoteOSGiService#getRemoteServiceReferences(ch.ethz.iks.r_osgi.URI,
	 *      java.lang.String, org.osgi.framework.Filter)
	 */
	public RemoteServiceReference[] getRemoteServiceReferences(final URI service, final String clazz, final Filter filter) {
		final String uri = getChannelURI(service);
		ChannelEndpointImpl channel = (ChannelEndpointImpl) channels.get(uri);
		if (channel == null) {
			connect(service);
			channel = (ChannelEndpointImpl) channels.get(uri);
		}
		if (clazz == null) {
			return channel.getAllRemoteReferences(null);
		}
		try {
			return channel.getAllRemoteReferences(RemoteOSGiActivator.context.createFilter(filter != null ? "(&" + filter + "(" + Constants.OBJECTCLASS + "=" + clazz + "))" : "(" + Constants.OBJECTCLASS + "=" + clazz + ")"));
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
			throw new IllegalArgumentException("Remote Reference is null.");
		}
		ServiceReference sref = getFetchedServiceReference(ref);
		if (sref == null) {
			fetchService(ref);
			sref = getFetchedServiceReference(ref);
		}
		return sref == null ? null : RemoteOSGiActivator.context.getService(sref);
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
	private ServiceReference getFetchedServiceReference(final RemoteServiceReference ref) {
		try {
			final ServiceReference[] refs = RemoteOSGiActivator.context.getServiceReferences(ref.getServiceInterfaces()[0], "(" + SERVICE_URI + "=" + ref.getURI() + ")");
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
	 * @see ch.ethz.iks.r_osgi.RemoteOSGiService#fetchService(ch.ethz.iks.slp.ServiceURL)
	 * @since 0.1
	 * @category RemoteOSGiService
	 */
	private void fetchService(final RemoteServiceReference ref) throws RemoteOSGiException {
		try {
			ChannelEndpointImpl channel;
			channel = ((RemoteServiceReferenceImpl) ref).getChannel();
			channel.fetchService(ref);
		} catch (final UnknownHostException e) {
			throw new RemoteOSGiException("Cannot resolve host " + ref.getURI(), e);
		} catch (final IOException ioe) {
			throw new RemoteOSGiException("Proxy generation error", ioe);
		}
	}

	static ChannelEndpoint getChannel(final URI uri) {
		return (ChannelEndpoint) channels.get(getChannelURI(uri));
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
	public ChannelEndpointManager getEndpointManager(final URI remoteEndpointAddress) {
		return getMultiplexer(remoteEndpointAddress.toString());
	}

	/**
	 * 
	 * @param uri
	 * @return
	 */
	private ChannelEndpointMultiplexer getMultiplexer(final String uri) {
		final String channel = getChannelURI(URI.create(uri));
		ChannelEndpointMultiplexer multiplexer = (ChannelEndpointMultiplexer) multiplexers.get(channel);
		if (multiplexer == null) {
			multiplexer = new ChannelEndpointMultiplexer((ChannelEndpointImpl) channels.get(channel));
			multiplexers.put(channel, multiplexer);
		}
		return multiplexer;
	}

	/**
	 * 
	 * @param serviceURI
	 * @return
	 */
	private static String getChannelURI(URI serviceURI) {
		return URI.create(serviceURI.getScheme() + "://" + serviceURI.getHostName() + ":" + serviceURI.getPort()).toString();
	}

	/**
	 * the method is called when the R-OSGi bundle is about to be stopped.
	 * removes all registered proxy bundles.
	 */
	void cleanup() {
		final ChannelEndpoint[] c = (ChannelEndpoint[]) channels.values().toArray(new ChannelEndpoint[channels.size()]);
		channels.clear();
		for (int i = 0; i < c.length; i++) {
			c[i].dispose();
		}
		final Object[] factories = networkChannelFactoryTracker.getServices();
		for (int i = 0; i < factories.length; i++) {
			try {
				((NetworkChannelFactory) factories[i]).deactivate(this);
			} catch (final IOException ioe) {
				if (log != null) {
					log.log(LogService.LOG_ERROR, ioe.getMessage(), ioe);
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
		return (RemoteServiceRegistration[]) serviceRegistrations.values().toArray(new RemoteServiceRegistration[serviceRegistrations.size()]);
	}

	/**
	 * 
	 * @param serviceID
	 * @return
	 */
	static RemoteServiceRegistration getServiceRegistration(final String serviceID) {

		final String filter = "".equals(serviceID) ? null : '(' + Constants.SERVICE_ID + "=" + serviceID + ")";

		try {
			final ServiceReference[] refs = RemoteOSGiActivator.context.getServiceReferences(null, filter);
			if (refs == null) {
				if (log != null) {
					log.log(LogService.LOG_WARNING, "COULD NOT FIND " + filter);
				}
				return null;
			}
			return (RemoteServiceRegistration) serviceRegistrations.get(refs[0]);
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
	static synchronized short nextXid() {
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
		final ChannelEndpointImpl[] endpoints = (ChannelEndpointImpl[]) channels.values().toArray(new ChannelEndpointImpl[channels.size()]);
		for (int i = 0; i < endpoints.length; i++) {
			endpoints[i].sendLeaseUpdate(msg);
		}
	}

	/**
	 * 
	 * @param event
	 */
	static void notifyRemoteServiceListeners(final RemoteServiceEvent event) {
		final ServiceReference[] refs = remoteServiceListenerTracker.getServiceReferences();
		if (refs == null) {
			return;
		}
		final Set serviceIfaces = new HashSet(Arrays.asList(event.getRemoteReference().getServiceInterfaces()));
		for (int i = 0; i < refs.length; i++) {
			final String[] ifaces = (String[]) refs[i].getProperty(RemoteServiceListener.SERVICE_INTERFACES);
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
	private static void match(final ServiceReference ref, final RemoteServiceEvent event) {
		final Filter filter = (Filter) ref.getProperty(RemoteServiceListener.FILTER);
		if (filter == null || filter.match(((RemoteServiceReferenceImpl) event.getRemoteReference()).getProperties())) {
			final RemoteServiceListener listener = (RemoteServiceListener) remoteServiceListenerTracker.getService(ref);
			if (listener != null) {
				listener.remoteServiceEvent(event);
			}
		}
	}

	/**
	 * register a service with the remote service discovery layer.
	 */
	private void registerWithServiceDiscovery(final RemoteServiceRegistration reg) {
		// register the service with all service
		// discovery
		// handler
		final Dictionary props = reg.getProperties();
		final Object[] handler = serviceDiscoveryHandlerTracker.getServices();

		if (handler != null) {
			for (int i = 0; i < handler.length; i++) {
				((ServiceDiscoveryHandler) handler[i]).registerService(reg.getReference(), props, URI.create("r-osgi://" + RemoteOSGiServiceImpl.MY_ADDRESS + ":" + RemoteOSGiServiceImpl.R_OSGI_PORT + "#" + reg.getServiceID()));
			}
		}

	}

	/**
	 * unregister a service from the service discovery layer.
	 * 
	 * @param reg
	 *            the remote service registration.
	 */
	private void unregisterFromServiceDiscovery(final RemoteServiceRegistration reg) {
		final Object[] handler = serviceDiscoveryHandlerTracker.getServices();
		if (handler != null) {
			for (int i = 0; i < handler.length; i++) {
				((ServiceDiscoveryHandler) handler[i]).unregisterService(reg.getReference());
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
	public void ungetRemoteService(RemoteServiceReference remoteServiceReference) {
		((RemoteServiceReferenceImpl) remoteServiceReference).getChannel().ungetRemoteService(remoteServiceReference.getURI());

	}

}
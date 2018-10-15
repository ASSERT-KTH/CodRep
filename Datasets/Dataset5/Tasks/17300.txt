return primary.isConnected();

/* Copyright (c) 2006-2009 Jan S. Rellermeyer
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

import java.util.ArrayList;
import java.util.Dictionary;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;

import org.osgi.framework.ServiceRegistration;
import org.osgi.service.log.LogService;

import ch.ethz.iks.r_osgi.RemoteOSGiException;
import ch.ethz.iks.r_osgi.URI;
import ch.ethz.iks.r_osgi.channels.ChannelEndpoint;
import ch.ethz.iks.r_osgi.channels.ChannelEndpointManager;
import ch.ethz.iks.r_osgi.messages.RemoteOSGiMessage;
import ch.ethz.iks.r_osgi.types.Timestamp;

/**
 * Channel endpoint multiplexer. <i>EXPERIMENTAL</i>
 * 
 * @author Jan S. Rellermeyer, ETH Zurich
 */
final class ChannelEndpointMultiplexer implements ChannelEndpoint,
		ChannelEndpointManager {

	/**
	 * the primary channel.
	 */
	ChannelEndpointImpl primary;

	/**
	 * the policies.
	 */
	private final HashMap policies = new HashMap(0);

	/**
	 * the service registration.
	 */
	private ServiceRegistration reg;

	/**
	 * the mappings.
	 */
	private final Map mappings = new HashMap();

	/**
	 * create a new channel endpoint multiplexer.
	 * 
	 * @param primary
	 *            the primary channel endpoint.
	 */
	ChannelEndpointMultiplexer(final ChannelEndpointImpl primary) {
		if (primary == null) {
			throw new IllegalArgumentException(
					"Multiplexer must not be constructed from NULL primary endpoint"); //$NON-NLS-1$
		}
		this.primary = primary;
	}

	/**
	 * dispose the multiplexer.
	 */
	public void dispose() {

	}

	/**
	 * 
	 * @see ch.ethz.iks.r_osgi.channels.ChannelEndpoint#getPresentationProperties(java.lang.String)
	 */
	public Dictionary getPresentationProperties(final String service) {
		return primary.getPresentationProperties(service);
	}

	/**
	 * 
	 * @see ch.ethz.iks.r_osgi.channels.ChannelEndpoint#getProperties(java.lang.String)
	 */
	public Dictionary getProperties(final String service) {
		return primary.getProperties(service);
	}

	/**
	 * 
	 * @see ch.ethz.iks.r_osgi.channels.ChannelEndpoint#getRemoteAddress()
	 */
	public URI getRemoteAddress() {
		return primary.getRemoteAddress();
	}

	/**
	 * 
	 * @see ch.ethz.iks.r_osgi.channels.ChannelEndpoint#invokeMethod(java.lang.String,
	 *      java.lang.String, java.lang.Object[])
	 */
	public Object invokeMethod(final String serviceURI,
			final String methodSignature, final Object[] args) throws Throwable {
		final Mapping mapping = (Mapping) mappings.get(serviceURI);
		if (mapping == null) {
			return primary.invokeMethod(serviceURI, methodSignature, args);
		} else {
			final Integer p = (Integer) policies.get(serviceURI);
			if (p == null) {
				return primary.invokeMethod(mapping.getMapped(primary),
						methodSignature, args);
			} else {
				final int policy = p.intValue();
				if (policy == LOADBALANCING_ANY_POLICY) {
					final ChannelEndpoint endpoint = mapping.getAny();
					try {
						return endpoint.invokeMethod(mapping
								.getMapped(endpoint), methodSignature, args);
					} catch (final RemoteOSGiException e) {
						final ChannelEndpointImpl next = mapping.getNext();
						if (next != null) {
							primary.untrackRegistration(serviceURI);
							primary = next;
							primary.trackRegistration(serviceURI, reg);
							if (RemoteOSGiServiceImpl.DEBUG) {
								RemoteOSGiServiceImpl.log.log(
										LogService.LOG_INFO,
										"DOING FAILOVER TO " //$NON-NLS-1$
												+ primary.getRemoteAddress());
							}
							return primary.invokeMethod(mapping
									.getMapped(primary), methodSignature, args);
						}
						dispose();
						throw e;
					}
				} else {
					try {
						if (!primary.isConnected()) {
							throw new RemoteOSGiException("channel went down"); //$NON-NLS-1$
						}
						return primary.invokeMethod(mapping.getMapped(primary),
								methodSignature, args);
					} catch (final RemoteOSGiException e) {
						if (policy == FAILOVER_REDUNDANCY_POLICY) {
							// do the failover
							final ChannelEndpointImpl next = mapping.getNext();
							if (next != null) {
								primary.untrackRegistration(serviceURI);
								primary = next;
								primary.trackRegistration(serviceURI, reg);
								if (RemoteOSGiServiceImpl.DEBUG) {
									RemoteOSGiServiceImpl.log
											.log(
													LogService.LOG_INFO,
													"DOING FAILOVER TO " //$NON-NLS-1$
															+ primary
																	.getRemoteAddress());
								}
								return primary.invokeMethod(mapping
										.getMapped(primary), methodSignature,
										args);
							}
						}
						dispose();
						throw e;
					}
				}
			}
		}
	}

	/**
	 * 
	 * @see ch.ethz.iks.r_osgi.channels.ChannelEndpoint#receivedMessage(ch.ethz.iks.r_osgi.messages.RemoteOSGiMessage)
	 */
	public void receivedMessage(final RemoteOSGiMessage msg) {
		throw new IllegalArgumentException(
				"Not supported through endpoint multiplexer"); //$NON-NLS-1$
	}

	/**
	 * 
	 * @see ch.ethz.iks.r_osgi.channels.ChannelEndpoint#trackRegistration(java.lang.String,
	 *      org.osgi.framework.ServiceRegistration)
	 */
	public void trackRegistration(final String service,
			final ServiceRegistration sreg) {
		reg = sreg;
		primary.trackRegistration(service, sreg);
	}

	/**
	 * 
	 * @see ch.ethz.iks.r_osgi.channels.ChannelEndpoint#untrackRegistration(java.lang.String)
	 */
	public void untrackRegistration(final String service) {
		primary.untrackRegistration(service);
	}

	public boolean isConnected() {
		return true;
	}

	/**
	 * Mapping.
	 * 
	 */
	private class Mapping {

		private final Random random = new Random(System.currentTimeMillis());
		private final List redundant = new ArrayList(0);
		private final Map uriMapping = new HashMap(0);

		Mapping(final String serviceURI) {
			uriMapping.put(primary, serviceURI);
		}

		void addRedundant(final String redundantServiceURI,
				final ChannelEndpoint endpoint) {
			redundant.add(endpoint);
			uriMapping.put(endpoint, redundantServiceURI);
		}

		void removeRedundant(final ChannelEndpoint endpoint) {
			redundant.remove(endpoint);
			uriMapping.remove(endpoint);
		}

		String getMapped(final ChannelEndpoint endpoint) {
			return (String) uriMapping.get(endpoint);
		}

		ChannelEndpointImpl getNext() {
			return (ChannelEndpointImpl) redundant.remove(0);
		}

		boolean isEmpty() {
			return redundant.size() == 0;
		}

		ChannelEndpoint getAny() {
			final int ran = random.nextInt(redundant.size() + 1);
			if (ran == 0) {
				return primary;
			} else {
				return (ChannelEndpoint) redundant.get(ran - 1);
			}
		}

	}

	/**
	 * 
	 * @see ch.ethz.iks.r_osgi.channels.ChannelEndpointManager#addRedundantEndpoint(ch.ethz.iks.r_osgi.URI,
	 *      ch.ethz.iks.r_osgi.URI)
	 */
	public void addRedundantEndpoint(final URI service,
			final URI redundantService) {
		final ChannelEndpoint redundantEndpoint = RemoteOSGiServiceImpl
				.getChannel(redundantService);
		primary.hasRedundantLinks = true;
		Mapping mapping = (Mapping) mappings.get(service);
		if (mapping == null) {
			mapping = new Mapping(service.toString());
			mappings.put(service.toString(), mapping);
		}
		mapping.addRedundant(redundantService.toString(), redundantEndpoint);
	}

	/**
	 * 
	 * @see ch.ethz.iks.r_osgi.channels.ChannelEndpointManager#getLocalAddress()
	 */
	public URI getLocalAddress() {
		return primary.getLocalAddress();
	}

	/**
	 * 
	 * @see ch.ethz.iks.r_osgi.channels.ChannelEndpointManager#removeRedundantEndpoint(ch.ethz.iks.r_osgi.URI,
	 *      ch.ethz.iks.r_osgi.URI)
	 */
	public void removeRedundantEndpoint(final URI service,
			final URI redundantService) {
		final ChannelEndpoint redundantEndpoint = RemoteOSGiServiceImpl
				.getChannel(redundantService);
		final Mapping mapping = (Mapping) mappings.get(service.toString());
		mapping.removeRedundant(redundantEndpoint);
		if (mapping.isEmpty()) {
			mappings.remove(service);
			primary.hasRedundantLinks = false;
		}
	}

	/**
	 * 
	 * @see ch.ethz.iks.r_osgi.channels.ChannelEndpointManager#setEndpointPolicy(ch.ethz.iks.r_osgi.URI,
	 *      int)
	 */
	public void setEndpointPolicy(final URI service, final int policy) {
		policies.put(service.toString(), new Integer(policy));
	}

	/**
	 * transform a timestamp into the peer's local time.
	 * 
	 * @param timestamp
	 *            the Timestamp.
	 * @return the transformed timestamp.
	 * @throws RemoteOSGiException
	 *             if the transformation fails.
	 * @since 0.2
	 */
	public Timestamp transformTimestamp(final Timestamp timestamp)
			throws RemoteOSGiException {
		return primary.getOffset().transform(timestamp);
	}

}
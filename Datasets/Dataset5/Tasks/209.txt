out.write(reply.getBytes());

/* Copyright (c) 2005-2008 Jan S. Rellermeyer
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
package ch.ethz.iks.slp.impl;

import java.io.BufferedInputStream;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.net.InetAddress;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.UnknownHostException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.SortedMap;
import java.util.TreeMap;

import ch.ethz.iks.slp.ServiceLocationException;
import ch.ethz.iks.slp.ServiceType;
import ch.ethz.iks.slp.ServiceURL;

/**
 * the jSLP daemon class. This class is only required, if the peer is configured
 * as a SA and no other SLP daemon is running on the machine. UA-only
 * configurations or distributions that are intended to run on a machine with
 * OpenSLP <i>slpd</i> can be packaged without this class.
 * 
 * @author Jan S. Rellermeyer, ETH Zurich
 * @since 0.6
 */
public final class SLPDaemonImpl implements SLPDaemon {

	/**
	 * thread loop variable.
	 */
	private boolean running = true;

	/**
	 * Map of registered services:
	 * 
	 * String scope -> List of ServiceURLs services.
	 */
	private Map registeredServices = new HashMap();

	/**
	 * Sorted set for disposal of services which lifetimes have expired:
	 * 
	 * Long expirationTimestamp -> ServiceURL service.
	 */
	private SortedMap serviceDisposalQueue = new TreeMap();

	/**
	 * create a new SLPDaemon instance.
	 * 
	 * @param tcpSocket
	 *            the server socket.
	 * @throws Exception
	 *             if something goes wrong.
	 */
	public SLPDaemonImpl() throws Exception {
		new TcpServerThread();
		new ServiceDisposalThread();
		SLPCore.platform.logDebug("jSLP daemon starting ...");
	}

	/**
	 * register a service with the SLP framework. For the scopes, where DAs are
	 * known, the service will be registered with all DAs.
	 * 
	 * @param reg
	 *            the ServiceRegistration.
	 */
	private void registerService(final ServiceRegistration reg) {

		Service service = new Service(reg);

		for (Iterator scopeIter = reg.scopeList.iterator(); scopeIter.hasNext();) {
			String scope = (String) scopeIter.next();
			scope = scope.toLowerCase();
			synchronized (registeredServices) {
				SLPUtils.addValue(registeredServices, scope, service);
			}
			if (reg.url.getLifetime() > ServiceURL.LIFETIME_PERMANENT) {
				synchronized (serviceDisposalQueue) {
					long next = System.currentTimeMillis()
							+ (reg.url.getLifetime() * 1000);
					ArrayList keys = new ArrayList(serviceDisposalQueue
							.keySet());
					for (Iterator iter = keys.iterator(); iter.hasNext();) {
						Object key = iter.next();
						if (serviceDisposalQueue.get(key).equals(reg.url)) {
							serviceDisposalQueue.remove(key);
						}
					}
					serviceDisposalQueue.put(new Long(next), reg.url);
					serviceDisposalQueue.notifyAll();
				}
			}

			SLPCore.platform.logTraceReg("REGISTERED " + reg.url);

			// register the service with all known DAs in the scopes
			List daList = (List) SLPCore.dAs.get(scope);

			// no DA for the scope known ?
			// try to find one
			if ((daList == null || daList.isEmpty()) && !SLPCore.noDiscovery) {
				try {
					SLPCore.daLookup(Arrays
							.asList(new String[] { (String) scope }));

					// wait a short time for incoming replies
					synchronized (SLPCore.dAs) {
						try {
							SLPCore.dAs.wait(SLPCore.CONFIG.getWaitTime());
						} catch (InterruptedException e) {
						}
					}
					daList = (List) SLPCore.dAs.get(scope);
				} catch (ServiceLocationException sle) {
					SLPCore.platform.logError(sle.getMessage(), sle
								.fillInStackTrace());
				}
			}

			if (daList != null && !daList.isEmpty()) {
				final String[] dAs = (String[]) daList
						.toArray(new String[daList.size()]);
				final ServiceRegistration announcement = new ServiceRegistration(
						reg.url, reg.serviceType, reg.scopeList, reg.attList,
						reg.locale);
				announcement.authBlocks = reg.authBlocks;
				for (int i = 0; i < dAs.length; i++) {
					try {
						announceService(dAs[i], announcement);
						SLPCore.platform.logTraceReg("ANNOUNCED "
									+ announcement.url + " to " + dAs[i]);
					} catch (ServiceLocationException e) {
						// remove DA from list
						SLPUtils.removeValueFromAll(SLPCore.dAs, dAs[i]);
						SLPCore.dASPIs.remove(dAs[i]);
						SLPCore.platform.logError(e.getMessage(), e
									.fillInStackTrace());
					}
				}
			}
		}

	}

	/**
	 * deregister a service from the SLP framework. Deregisters from all DAs
	 * within the scopes and from the local service cache.
	 * 
	 * @param dereg
	 *            the service deregistration.
	 * @throws ServiceLocationException
	 */
	private void deregisterService(final ServiceDeregistration dereg)
			throws ServiceLocationException {

		final String[] scopes = (String[]) registeredServices.keySet().toArray(
				new String[registeredServices.size()]);
		for (int i = 0; i < scopes.length; i++) {
			final List tmp = (List) registeredServices.get(scopes[i]);
			final Service[] services = (Service[]) tmp.toArray(new Service[tmp
					.size()]);

			for (int j = 0; j < services.length; j++) {
				if (dereg.url.matches(services[j].url)) {
					List daList = (List) SLPCore.dAs.get(scopes[i].toLowerCase());
					if (daList != null) {
						for (Iterator daIter = daList.iterator(); daIter
								.hasNext();) {
							try {
								String dA = (String) daIter.next();
								dereg.address = InetAddress.getByName(dA);
								dereg.port = SLPCore.SLP_RESERVED_PORT;
								dereg.xid = SLPCore.nextXid();
								if (SLPCore.CONFIG.getSecurityEnabled()) {
									List spiList = (List) SLPCore.dASPIs
											.get(dA);
									dereg.sign(spiList);
								}
								ReplyMessage reply = SLPCore.sendMessage(dereg,
										true);
								if (reply.errorCode != 0) {
									throw new ServiceLocationException(
											(short) reply.errorCode,
											"Error during deregistration: "
													+ reply.errorCode);
								}
							} catch (UnknownHostException uhe) {
								throw new ServiceLocationException(
										ServiceLocationException.NETWORK_ERROR,
										uhe.getMessage());
							}
						}
					}
					synchronized (registeredServices) {
						SLPUtils.removeValue(registeredServices, scopes[i],
								services[j]);
					}
					break;
				}
			}
		}
	}

	/**
	 * all incoming messages are handled here.
	 * 
	 * @param msg
	 *            the message to be processed.
	 * @return the reply if the handled message came in via TCP. Otherwise null
	 *         will be returned.
	 * @throws ServiceLocationException
	 *             for various reasons like authentication failures etc.
	 */
	public ReplyMessage handleMessage(final SLPMessage msg)
			throws ServiceLocationException {
		if (msg == null) {
			return null;
		}

		String via = msg.tcp ? " (tcp)" : " (udp)";

		SLPCore.platform.logTraceMessage("RECEIVED (" + msg.address + ":"
					+ msg.port + ") " + msg.toString() + via);

		ReplyMessage reply = null;

		switch (msg.funcID) {
		case SLPMessage.SRVRQST:
			ServiceRequest req = (ServiceRequest) msg;

			List results = new ArrayList();
			for (Iterator scopes = req.scopeList.iterator(); scopes.hasNext();) {
				String scope = (String) scopes.next();
				List services = (List) registeredServices.get(scope.toLowerCase());
				if (services == null) {
					continue;
				}

				for (Iterator srvs = services.iterator(); srvs.hasNext();) {
					Service service = (Service) srvs.next();
					if (service.url.getServiceType().matches(req.serviceType)) {
						if (req.predicate == null) {
							results.add(service.url);
							continue;
						}
						if (req.predicate.match(service.attributes)) {
							results.add(service.url);
						}
					}
				}
			}

			/*
			 * if there is no result, don't send a reply. This causes the SA to
			 * get the same message at least two more times but the RFC strictly
			 * demands this for multicast requests
			 */
			if (results.size() == 0 && req.multicast) {
				return null;
			}

			reply = new ServiceReply(req, results);

			if (SLPCore.CONFIG.getSecurityEnabled()) {
				((ServiceReply) reply).sign(req.spi);
			}

			return reply;

		case SLPMessage.ATTRRQST:
			AttributeRequest attreq = (AttributeRequest) msg;

			List attResult = new ArrayList();
			for (Iterator scopes = attreq.scopeList.iterator(); scopes
					.hasNext();) {
				String scope = (String) scopes.next();
				List services = (List) registeredServices.get(scope.toLowerCase());
				if (services == null) {
					continue;
				}
				// the request can either be for a ServiceURL or a ServiceType
				Object reqService;
				boolean fullurl = false;
				if (attreq.url.indexOf("//") == -1) {
					reqService = new ServiceType(attreq.url);
				} else {
					fullurl = true;
					reqService = new ServiceURL(attreq.url, 0);
				}

				// if spi is sent, the request must be for a full url and
				// the tag list has to be empty
				if (attreq.spi.equals("")
						|| (fullurl && attreq.tagList.isEmpty())) {
					for (Iterator srvs = services.iterator(); srvs.hasNext();) {
						Service service = (Service) srvs.next();
						if (service.url.matches(reqService)) {
							attResult.addAll(SLPUtils.findMatches(
									attreq.tagList, service.attributes));
						}
					}
				}

			}
			reply = new AttributeReply(attreq, attResult);

			if (SLPCore.CONFIG.getSecurityEnabled()) {
				((AttributeReply) reply).sign(attreq.spi);
			}

			return reply;
		case SLPMessage.SRVTYPERQST:
			ServiceTypeRequest streq = (ServiceTypeRequest) msg;

			ArrayList result = new ArrayList();

			// iterate over scopes
			for (Iterator scopeIter = streq.scopeList.iterator(); scopeIter
					.hasNext();) {

				// iterate over the registered services
				String scope = (String) scopeIter.next();
				List services = ((List) registeredServices
						.get(scope.toLowerCase()));
				if (services == null) {
					continue;
				}
				for (Iterator iter = services.iterator(); iter.hasNext();) {
					Service service = (Service) iter.next();
					ServiceType type = service.url.getServiceType();
					if (streq.namingAuthority.equals("*")
							|| streq.namingAuthority.equals("")
							|| type.getNamingAuthority().equals(
									streq.namingAuthority)) {
						if (!result.contains(type)) {
							result.add(type);
						}
					}
				}
			}
			reply = new ServiceTypeReply(streq, result);

			return reply;

		case SLPMessage.SRVREG:
			registerService((ServiceRegistration) msg);
			reply = new ServiceAcknowledgement(msg, 0);
			return reply;

		case SLPMessage.SRVDEREG:
			deregisterService((ServiceDeregistration) msg);

			reply = new ServiceAcknowledgement(msg, 0);

			return reply;

		case SLPMessage.SRVACK:
			final ReplyMessage rep = (ReplyMessage) msg;
			if (rep.errorCode != 0) {
				SLPCore.platform.logWarning(msg.address
							+ " replied with error code " + rep.errorCode
							+ " (" + rep + ")");
			}
			return null;

		default:
			// this should never happen, message should already cause an
			// exception during parsing
			throw new ServiceLocationException(
					ServiceLocationException.NOT_IMPLEMENTED,
					"The message type " + SLPMessage.getType(msg.funcID)
							+ " is not implemented");
		}

	}

	/**
	 * get informed about a new discovered DA. Registers all services in the
	 * scopes of the new DA.
	 * 
	 * @param advert
	 *            the DA advertisement.
	 */
	public void newDaDiscovered(final DAAdvertisement advert) {
		// so find all services within the scopes of the new DA:
		for (Iterator iter = advert.scopeList.iterator(); iter.hasNext();) {
			String scope = (String) iter.next();
			List services = (List) registeredServices.get(scope.toLowerCase());
			if (services != null) {
				for (Iterator serviceIter = services.iterator(); serviceIter
						.hasNext();) {
					// and try to register it with the new DA
					try {
						Service service = (Service) serviceIter.next();
						ServiceRegistration reg = new ServiceRegistration(
								service.url, service.url.getServiceType(),
								Arrays.asList(new Object[] { scope }), SLPUtils
										.dictToAttrList(service.attributes),
								SLPCore.DEFAULT_LOCALE);
						SLPCore.platform.logDebug("Registering "
									+ service.url + " with new DA "
									+ advert.url);
						announceService(advert.url, reg);
					} catch (ServiceLocationException e) {
						SLPCore.platform.logError(e.getMessage(), e
									.fillInStackTrace());
					}
				}
			}
		}
	}

	/**
	 * register a service with a DA.
	 * 
	 * @param dAAddress
	 *            the IP address of the DA as <code>String</code>
	 * @param reg
	 *            the <code>ServiceRegistration</code> message.
	 * @throws ServiceLocationException
	 *             in case of network errors.
	 */
	private void announceService(final String dAAddress,
			final ServiceRegistration reg) throws ServiceLocationException {
		try {
			reg.address = InetAddress.getByName(dAAddress);
			reg.port = SLPCore.SLP_RESERVED_PORT;
			reg.xid = SLPCore.nextXid();
			if (SLPCore.CONFIG.getSecurityEnabled()) {
				List spiList = (List) SLPCore.dASPIs.get(dAAddress);
				reg.sign(spiList);
			}
			handleMessage(SLPCore.sendMessage(reg, true));
		} catch (UnknownHostException e) {
			SLPCore.platform.logError("Service announcement to "
						+ dAAddress + " failed. ", e.fillInStackTrace());
		}
	}

	/**
	 * TCP server thread.
	 */
	private final class TcpServerThread extends Thread {
		private ServerSocket socket;

		/**
		 * creates and starts a new TCP server thread.
		 * 
		 * @throws IOException
		 *             if socket creation fails.
		 */
		private TcpServerThread() throws IOException {
			socket = new ServerSocket(SLPCore.SLP_PORT);
			start();
		}

		/**
		 * thread loop.
		 */
		public void run() {
			while (running) {
				try {
					Socket con = socket.accept();
					DataInputStream in = new DataInputStream(
							new BufferedInputStream(con.getInputStream()));
					SLPMessage msg = SLPMessage.parse(con.getInetAddress(), con
							.getPort(), in, true);

					ReplyMessage reply = handleMessage(msg);
					if (reply != null) {
						SLPCore.platform.logTraceMessage("SEND REPLY ("
									+ reply.address + ":" + reply.port + ") "
									+ reply);

						DataOutputStream out = new DataOutputStream(con
								.getOutputStream());
						reply.writeTo(out);
						/*
						 * TODO the RFC encourages to keep the connection open
						 * to allow the other side to send multiple requests per
						 * connection. So start a server thread for every
						 * incoming connection instead of closing the connection
						 * after the first request
						 */
						out.close();
					}
					in.close();
					con.close();
				} catch (Exception ioe) {
					SLPCore.platform.logError(
								"Exception in TCP receiver thread", ioe);
				}
			}
		}
	}

	/**
	 * service disposal thread. Removes services from the local registry when
	 * their lifetime has expired.
	 */
	private final class ServiceDisposalThread extends Thread {

		/**
		 * create and start a new instance of this thread.
		 * 
		 */
		private ServiceDisposalThread() {
			start();
		}

		/**
		 * thread's main loop.
		 */
		public void run() {
			try {
				while (running) {
					synchronized (serviceDisposalQueue) {
						if (serviceDisposalQueue.isEmpty()) {
							// nothing to do, sleep until something arrives
							SLPCore.platform
										.logDebug("ServiceDisposalThread sleeping ...");
							serviceDisposalQueue.wait();
						} else {
							// we have work, do everything that is due
							Long nextActivity;
							while (!serviceDisposalQueue.isEmpty()
									&& (nextActivity = ((Long) serviceDisposalQueue
											.firstKey())).longValue() <= System
											.currentTimeMillis()) {
								ServiceURL service = (ServiceURL) serviceDisposalQueue
										.get(nextActivity);

								ServiceDeregistration dereg = new ServiceDeregistration(
										service, null, null,
										SLPCore.DEFAULT_LOCALE);
								try {
									deregisterService(dereg);
								} catch (ServiceLocationException sle) {
									SLPCore.platform.logError(sle
												.getMessage(), sle
												.fillInStackTrace());
								}
								SLPCore.platform
											.logTraceReg("disposed service "
													+ service);
								serviceDisposalQueue.remove(nextActivity);
							}
							if (!serviceDisposalQueue.isEmpty()) {
								/*
								 * there are some activities in the future,
								 * sleep until the first activity becomes due
								 */
								nextActivity = ((Long) serviceDisposalQueue
										.firstKey());
								long waitTime = nextActivity.longValue()
										- System.currentTimeMillis();
								if (waitTime > 0) {
									SLPCore.platform
												.logDebug("sleeping for "
														+ waitTime / 1000
														+ " seconds.");
									serviceDisposalQueue.wait(waitTime);
								}
							}
						}
					}
				}
			} catch (InterruptedException ie) {
				// let the thread stop.
			}
		}
	}
}
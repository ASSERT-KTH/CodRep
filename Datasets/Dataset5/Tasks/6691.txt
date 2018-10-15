String[] rrs = new String[] {BnRDnsSdServiceTypeID.BROWSE_DOMAINS, BnRDnsSdServiceTypeID.DEFAULT_BROWSE_DOMAIN};

/*******************************************************************************
 * Copyright (c) 2009 Markus Alexander Kuppe.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     Markus Alexander Kuppe (ecf-dev_eclipse.org <at> lemmster <dot> de) - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.provider.dnssd;

import java.net.URI;
import java.net.UnknownHostException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Properties;
import java.util.Set;

import org.eclipse.core.runtime.Assert;
import org.eclipse.ecf.core.ContainerConnectException;
import org.eclipse.ecf.core.events.ContainerConnectedEvent;
import org.eclipse.ecf.core.events.ContainerConnectingEvent;
import org.eclipse.ecf.core.events.ContainerDisconnectedEvent;
import org.eclipse.ecf.core.events.ContainerDisconnectingEvent;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.security.IConnectContext;
import org.eclipse.ecf.discovery.AbstractDiscoveryContainerAdapter;
import org.eclipse.ecf.discovery.DiscoveryContainerConfig;
import org.eclipse.ecf.discovery.IServiceInfo;
import org.eclipse.ecf.discovery.ServiceInfo;
import org.eclipse.ecf.discovery.ServiceProperties;
import org.eclipse.ecf.discovery.identity.IServiceID;
import org.eclipse.ecf.discovery.identity.IServiceTypeID;
import org.xbill.DNS.Lookup;
import org.xbill.DNS.Name;
import org.xbill.DNS.PTRRecord;
import org.xbill.DNS.Record;
import org.xbill.DNS.Resolver;
import org.xbill.DNS.ResolverConfig;
import org.xbill.DNS.SRVRecord;
import org.xbill.DNS.SimpleResolver;
import org.xbill.DNS.TXTRecord;
import org.xbill.DNS.Type;

public class DnsSdDiscoveryLocator extends AbstractDiscoveryContainerAdapter {

	private static final String DNS_SD_PATH = "path";
	private static final String DNS_SD_PTCL = "dns-sd.ptcl";
	private DnsSdServiceTypeID targetID;
	private Resolver resolver;

	public DnsSdDiscoveryLocator() {
		super(DnsSdNamespace.NAME, new DiscoveryContainerConfig(IDFactory
				.getDefault().createStringID(
						DnsSdDiscoveryLocator.class.getName())));
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see
	 * org.eclipse.ecf.discovery.IDiscoveryLocator#getServiceInfo(org.eclipse
	 * .ecf.discovery.identity.IServiceID)
	 */
	public IServiceInfo getServiceInfo(IServiceID aServiceId) {
		Assert.isNotNull(aServiceId);
		IServiceInfo[] services = getServices(aServiceId.getServiceTypeID());
		for (int i = 0; i < services.length; i++) {
			//TODO This can be a lot faster if done directly instead of via org.eclipse.ecf.provider.dnssrv.DnsSrvDisocoveryLocator.getServices(IServiceTypeID)
			IServiceInfo iServiceInfo = services[i];
			if(iServiceInfo.getServiceID().equals(aServiceId)) {
				return iServiceInfo;
			}
		}
		return null;
	}

	/**
	 * This always returns the service type found for our local domain
	 * Use org.eclipse.ecf.provider.dnssrv.DnsSrvDisocoveryLocator.getServices(IServiceTypeID) with a wildcard query instead.
	 * 
	 * @see org.eclipse.ecf.discovery.IDiscoveryLocator#getServiceTypes()
	 */
	public IServiceTypeID[] getServiceTypes() {
		// technically can't do anything without a scope (domain) -> falling back to local domain (mDNS?)
		DnsSdServiceTypeID serviceTypeId = (DnsSdServiceTypeID) targetID;
		return getServiceTypes(serviceTypeId);
	}

	private IServiceTypeID[] getServiceTypes(final DnsSdServiceTypeID serviceTypeId) {
		List result = new ArrayList();
		Record[] queryResult = getRecords(serviceTypeId);
		for (int j = 0; j < queryResult.length; j++) {
			Record record = queryResult[j];
			if(record instanceof PTRRecord) {
				PTRRecord ptrRecord = (PTRRecord) record;
				result.add(new DnsSdServiceTypeID(getServicesNamespace(), ptrRecord.getTarget()));
			} else if (record instanceof SRVRecord) {
				SRVRecord srvRecord = (SRVRecord) record;
				result.add(new DnsSdServiceTypeID(getServicesNamespace(), srvRecord.getName()));
			}
		}
		return (IServiceTypeID[]) result.toArray(new IServiceTypeID[result.size()]);
	}
	
	private Record[] getRecords(final DnsSdServiceTypeID serviceTypeId) {
		List result = new ArrayList();
		Lookup[] queries = serviceTypeId.getInternalQueries();
		for (int i = 0; i < queries.length; i++) {
			Lookup query = queries[i];
			query.setResolver(resolver);
			Record[] queryResult = query.run();
			if(queryResult != null) {
				result.addAll(Arrays.asList(queryResult));
			}
		}
		return (Record[]) result.toArray(new Record[result.size()]);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.discovery.IDiscoveryLocator#getServices()
	 */
	public IServiceInfo[] getServices() {
		// technically can't do anything without a scope (domain) -> falling back to local domain (mDNS?)
		return getServices(targetID);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see
	 * org.eclipse.ecf.discovery.IDiscoveryLocator#getServices(org.eclipse.ecf
	 * .discovery.identity.IServiceTypeID)
	 */
	public IServiceInfo[] getServices(IServiceTypeID aServiceTypeId) {
		Assert.isNotNull(aServiceTypeId);
		DnsSdServiceTypeID serviceTypeId = (DnsSdServiceTypeID) aServiceTypeId;
		List srvRecords = getSRVRecords(serviceTypeId.getInternalQueries());
		List serviceInfos = getServiceInfos(srvRecords);
		return (IServiceInfo[]) serviceInfos.toArray(new IServiceInfo[serviceInfos.size()]);
	}
	
	private List getSRVRecords(Lookup[] queries) {
		List srvRecords = new ArrayList();
		for (int i = 0; i < queries.length; i++) {
			Lookup query = queries[i];
			query.setResolver(resolver);
			Record[] queryResult = query.run();
			//TODO file bug upstream that queryResult may never be null
			int length = queryResult == null ? 0 : queryResult.length;
			for (int j = 0; j < length; j++) {
				Record[] srvQueryResult = null;
				Record record = queryResult[j];
				if(record instanceof PTRRecord) {
					PTRRecord ptrRecord = (PTRRecord) record;
					Name target = ptrRecord.getTarget();
					Lookup srvQuery = new Lookup(target, Type.SRV);
					srvQuery.setResolver(resolver);
					srvQueryResult = srvQuery.run();
				} else if (record instanceof SRVRecord) {
					srvQueryResult = new SRVRecord[]{(SRVRecord) record};
				}
				srvRecords.addAll(Arrays.asList(srvQueryResult));
			}
		}
		return srvRecords;
	}
	
	private List getServiceInfos(List srvQueryResult) {
		List infos = new ArrayList();
		for (Iterator iterator = srvQueryResult.iterator(); iterator.hasNext();) {
			SRVRecord srvRecord = (SRVRecord) iterator.next();
			int priority = srvRecord.getPriority();
			int weight = srvRecord.getWeight();
			int port = srvRecord.getPort();
			Name target = srvRecord.getTarget();
			String host = target.toString();
			host = host.substring(0, host.length() - 1);
			
			IServiceTypeID aServiceTypeID = new DnsSdServiceTypeID(getConnectNamespace(), srvRecord.getName());
			
			// query for txt records (attributes)
			Properties props = new Properties();
			Lookup txtQuery = new Lookup(srvRecord.getName(), Type.TXT);
			txtQuery.setResolver(resolver);
			Record[] txtQueryResults = txtQuery.run();
			int length = txtQueryResults == null ? 0 : txtQueryResults.length;
			for (int l = 0; l < length; l++) {
				TXTRecord txtResult = (TXTRecord) txtQueryResults[l];
				List strings = txtResult.getStrings();
				for (Iterator itr = strings.iterator(); itr.hasNext();) {
					String str = (String) itr.next();
					String[] split = str.split("=");
					props.put(split[0], split[1]);
				}
			}
			String path = props.getProperty(DNS_SD_PATH);
			String proto = props.getProperty(DNS_SD_PTCL) == null ? aServiceTypeID.getProtocols()[0] : props.getProperty(DNS_SD_PTCL);
			
			URI uri = URI.create(proto + "://" + host + ":" + port + (path == null ? "" : path));
			IServiceInfo info =new ServiceInfo(uri, host, aServiceTypeID, priority, weight, new ServiceProperties(props));
			infos.add(info);
		}
		return infos;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see
	 * org.eclipse.ecf.discovery.IDiscoveryAdvertiser#registerService(org.eclipse
	 * .ecf.discovery.IServiceInfo)
	 */
	public void registerService(IServiceInfo serviceInfo) {
		Assert.isNotNull(serviceInfo);
		// nop, we are just a Locator but AbstractDiscoveryContainerAdapter
		// doesn't support this yet
		throw new UnsupportedOperationException(
				"This is not an IDiscoveryAdvertiser");
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see
	 * org.eclipse.ecf.discovery.IDiscoveryAdvertiser#unregisterService(org.
	 * eclipse.ecf.discovery.IServiceInfo)
	 */
	public void unregisterService(IServiceInfo serviceInfo) {
		Assert.isNotNull(serviceInfo);
		// nop, we are just a Locator but AbstractDiscoveryContainerAdapter
		// doesn't support this yet
		throw new UnsupportedOperationException(
				"This is not an IDiscoveryAdvertiser");
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see
	 * org.eclipse.ecf.core.IContainer#connect(org.eclipse.ecf.core.identity.ID,
	 * org.eclipse.ecf.core.security.IConnectContext)
	 */
	public void connect(ID aTargetID, IConnectContext connectContext)
			throws ContainerConnectException {

		// connect can only be called once
		if (targetID != null || getConfig() == null) {
			throw new ContainerConnectException("Already connected");
		}
		
		// fall back to the search path as last resort 
		if(aTargetID == null || !(aTargetID instanceof DnsSdServiceTypeID)) {
			ResolverConfig config = new ResolverConfig();
			Name[] searchPaths = config.searchPath();
			if(searchPaths.length >= 0) {
				targetID = new DnsSdServiceTypeID();
				targetID.setSearchPath(searchPaths);
			} else {
				throw new ContainerConnectException("No target id given");
			}
		} else {
			targetID = (DnsSdServiceTypeID) aTargetID;
		}
		
		// instantiate a default resolver
		if(resolver == null) {
			try {
				resolver = new SimpleResolver();
			} catch (UnknownHostException e) {
				throw new ContainerConnectException(e);
			}
		}
		
		// read browsing domains for the given targetID/searchpath and merge with existing
		targetID.addSearchPath(getBrowsingDomains(targetID));

		// done setting up this provider, send event
		fireContainerEvent(new ContainerConnectingEvent(this.getID(), targetID,
				connectContext));
		fireContainerEvent(new ContainerConnectedEvent(this.getID(), targetID));
	}

	private String[] getBrowsingDomains(IServiceTypeID aServiceTypeId) {
		Set res = new HashSet();
		
		String[] rrs = new String[] {BnRDnsSdServiceTypeID.BROWSE_DOMAIN, BnRDnsSdServiceTypeID.DEFAULT_BROWSE_DOMAIN};
		for (int i = 0; i < rrs.length; i++) {
			BnRDnsSdServiceTypeID serviceType = 
				new BnRDnsSdServiceTypeID(aServiceTypeId, rrs[i]);
			
			Record[] defaultBrowsing = getRecords(serviceType);
			for (int j = 0; j < defaultBrowsing.length; j++) {
				PTRRecord record = (PTRRecord) defaultBrowsing[j];
				res.add(record.getTarget().toString());
			}
		}
		
		return (String[]) res.toArray(new String[res.size()]);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.IContainer#disconnect()
	 */
	public void disconnect() {
		fireContainerEvent(new ContainerDisconnectingEvent(this.getID(),
				getConnectedID()));
		targetID = null;
		fireContainerEvent(new ContainerDisconnectedEvent(this.getID(),
				getConnectedID()));
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.IContainer#getConnectedID()
	 */
	public ID getConnectedID() {
		return targetID;
	}

	/**
	 * @param searchPaths The default search path used for discovery 
	 */
	public void setSearchPath(String[] searchPaths) {
		targetID.setSearchPath(searchPaths);
	}
	
	/**
	 * @return The default search path used by this discovery provider
	 */
	public String[] getSearchPath() {
		return targetID.getSearchPath();
	}

	/**
	 * @param aResolver The resolver to use
	 * @throws DnsSdDiscoveryException if hostname cannot be resolved
	 */
	public void setResolver(String aResolver) {
		try {
			resolver = new SimpleResolver(aResolver);
		} catch (UnknownHostException e) {
			throw new DnsSdDiscoveryException(e);
		}
	}
}
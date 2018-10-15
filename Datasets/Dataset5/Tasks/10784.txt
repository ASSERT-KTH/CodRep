publishedServices.put(getServiceID().getName(),

/*******************************************************************************
 *  Copyright (c)2010 REMAIN B.V. The Netherlands. (http://www.remainsoftware.com).
 *  All rights reserved. This program and the accompanying materials
 *  are made available under the terms of the Eclipse Public License v1.0
 *  which accompanies this distribution, and is available at
 *  http://www.eclipse.org/legal/epl-v10.html
 * 
 *  Contributors:
 *    Wim Jongman - initial API and implementation 
 *    Ahmed Aadel - initial API and implementation     
 *******************************************************************************/
package org.eclipse.ecf.provider.zookeeper.core;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.ObjectOutputStream;
import java.net.URI;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

import org.eclipse.core.runtime.Assert;
import org.eclipse.ecf.discovery.IServiceInfo;
import org.eclipse.ecf.discovery.ServiceInfo;
import org.eclipse.ecf.discovery.ServiceProperties;
import org.eclipse.ecf.discovery.identity.IServiceID;
import org.eclipse.ecf.discovery.identity.IServiceTypeID;
import org.eclipse.ecf.discovery.identity.ServiceIDFactory;
import org.eclipse.ecf.provider.zookeeper.core.internal.Configurator;
import org.eclipse.ecf.provider.zookeeper.core.internal.IService;
import org.eclipse.ecf.provider.zookeeper.node.internal.INode;
import org.eclipse.ecf.provider.zookeeper.util.Geo;
import org.eclipse.ecf.provider.zookeeper.util.Logger;
import org.osgi.framework.Constants;
import org.osgi.framework.ServiceReference;
import org.osgi.service.log.LogService;

/**
 * Encapsulate a service to be advertised and made visible for discovery. An
 * object of <code>AdvertisedService</code> is build either with an OSGi service
 * reference <code>ServiceReference</code> or <code>ServiceInfo</code> object.<br>
 * 
 */

public class AdvertisedService extends ServiceInfo implements INode, IService {

	private static final long serialVersionUID = 1001026250299416572L;
	private String uuid;
	private Map<String, Object> nodeProperties = new HashMap<String, Object>();
	private static Map<String, IServiceInfo> publishedServices = new HashMap<String, IServiceInfo>();
	private ServiceReference serviceReference;

	public AdvertisedService(ServiceReference ref) {
		Assert.isNotNull(ref);
		this.serviceReference = ref;
		this.uuid = UUID.randomUUID().toString();
		super.properties = new ServiceProperties();
		String services[] = (String[]) this.serviceReference
				.getProperty(Constants.OBJECTCLASS);
		for (String propertyKey : this.serviceReference.getPropertyKeys()) {
			super.properties.setProperty(propertyKey,
					this.serviceReference.getProperty(propertyKey));
		}
		IServiceTypeID serviceTypeID = ServiceIDFactory.getDefault()
				.createServiceTypeID(
						ZooDiscoveryContainer.getSingleton()
								.getConnectNamespace(), services,
						IServiceTypeID.DEFAULT_PROTO);
		serviceTypeID = new ZooDiscoveryServiceTypeID(
				(ZooDiscoveryNamespace) ZooDiscoveryContainer.getSingleton()
						.getConnectNamespace(), serviceTypeID,
				this.serviceReference.getProperty(Constants.SERVICE_ID)
						.toString());
		serviceID = new ZooDiscoveryServiceID(ZooDiscoveryContainer
				.getSingleton().getConnectNamespace(), serviceTypeID,
				Geo.getLocation());
		setNodeProperties();
	}

	public AdvertisedService(IServiceInfo serviceInfo) {
		super(serviceInfo.getLocation(), serviceInfo.getServiceName(),
				serviceInfo.getServiceID().getServiceTypeID(), serviceInfo
						.getPriority(), serviceInfo.getWeight(), serviceInfo
						.getServiceProperties());
		this.uuid = UUID.randomUUID().toString();
		setNodeProperties();
	}

	private void setNodeProperties() {
		this.nodeProperties.put(NODE_PROPERTY_SERVICE_NAME, getServiceName());
		this.nodeProperties.put(NODE_SERVICE_PROPERTIES, super.properties);
		this.nodeProperties.put(NODE_PROPERTY_NAME_PROTOCOLS, getServiceID()
				.getServiceTypeID().getProtocols());
		this.nodeProperties.put(NODE_PROPERTY_NAME_SCOPE, getServiceID()
				.getServiceTypeID().getScopes());
		this.nodeProperties.put(NODE_PROPERTY_SERVICES, getServiceID()
				.getServiceTypeID().getServices());
		this.nodeProperties.put(NODE_PROPERTY_NAME_NA, getServiceID()
				.getServiceTypeID().getNamingAuthority());
		this.nodeProperties.put(LOCATION, getLocation());
		this.nodeProperties.put(WEIGHT, getWeight());
		this.nodeProperties.put(PRIORITY, getPriority());
		publishedServices.put(getServiceID().getServiceTypeID().getInternal(),
				this);
	}

	public static Map<String, IServiceInfo> getPublishedServices() {
		return Collections.unmodifiableMap(publishedServices);
	}

	public synchronized static IServiceInfo removePublished(String id) {
		return publishedServices.remove(id);
	}

	public String getNodeId() {
		return this.uuid;
	}

	public void regenerateNodeId() {
		this.uuid = UUID.randomUUID().toString();
	}

	public URI getLocation() {
		return serviceID.getLocation();
	}

	public IServiceID getServiceID() {
		return serviceID;
	}

	public int compareTo(Object o) {
		Assert.isTrue(o != null && o instanceof IServiceInfo,
				"incompatible types for compare"); //$NON-NLS-1$
		return this.getServiceID().getName()
				.compareTo(((IServiceInfo) o).getServiceID().getName());
	}

	/**
	 * @return ServiceReference may be null if this
	 *         <code>AdvertisedService</code> instance is not <code>built</code>
	 *         calling constructor
	 *         <code>AdvertisedService(ServiceReference ref)</code>.
	 */
	public ServiceReference getServiceReference() {
		return this.serviceReference;
	}

	public byte[] getPropertiesAsBytes() {
		ByteArrayOutputStream baout = new ByteArrayOutputStream();
		ObjectOutputStream oout = null;
		byte[] bytes = null;
		try {
			oout = new ObjectOutputStream(baout);
			oout.writeObject(nodeProperties);
			oout.flush();
			bytes = baout.toByteArray();
		} catch (IOException e) {
			Logger.log(LogService.LOG_ERROR,
					"Error while serializing node data ", e);//$NON-NLS-1$
		} finally {
			if (oout != null) {
				try {
					oout.close();
				} catch (IOException e) {
					// ignore
				}
			}
			if (baout != null) {
				try {
					baout.close();
				} catch (IOException e) {
					// ignore
				}
			}
		}
		return bytes;
	}

	public String getPath() {
		return getNodeId() + INode._URI_ + Geo.getHost()
				+ INode._ZOODISCOVERYID_
				+ Configurator.INSTANCE.getID().getName();
	}

	public String getAbsolutePath() {
		return INode.ROOT_SLASH + getPath();
	}

	public boolean isLocalNode() {
		return Geo.isLocal(getAbsolutePath());
	}

	public IService getWrappedService() {
		return this;
	}
}
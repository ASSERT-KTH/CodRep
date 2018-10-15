WatchManager.this.writeRoot = new WriteRoot(Geo.getHost() + ":" + getConfig().getClientPort() ,

/*******************************************************************************
 *  Copyright (c)2010 REMAIN B.V. The Netherlands. (http://www.remainsoftware.com).
 *  All rights reserved. This program and the accompanying materials
 *  are made available under the terms of the Eclipse Public License v1.0
 *  which accompanies this distribution, and is available at
 *  http://www.eclipse.org/legal/epl-v10.html
 * 
 *  Contributors:
 *     Ahmed Aadel - initial API and implementation     
 *******************************************************************************/
package org.eclipse.ecf.provider.zookeeper.node.internal;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.apache.zookeeper.ZooKeeper;
import org.eclipse.core.runtime.Assert;
import org.eclipse.ecf.discovery.IServiceInfo;
import org.eclipse.ecf.provider.zookeeper.DiscoveryActivator;
import org.eclipse.ecf.provider.zookeeper.core.AdvertisedService;
import org.eclipse.ecf.provider.zookeeper.core.ZooDiscoveryContainer;
import org.eclipse.ecf.provider.zookeeper.core.internal.BundleStoppingListener;
import org.eclipse.ecf.provider.zookeeper.core.internal.Configuration;
import org.eclipse.ecf.provider.zookeeper.util.Geo;
import org.eclipse.ecf.provider.zookeeper.util.Logger;
import org.osgi.framework.Constants;
import org.osgi.framework.ServiceReference;
import org.osgi.service.log.LogService;

/**
 * @author Ahmed Aadel
 * @since 0.1
 */
public class WatchManager implements BundleStoppingListener {

	private List<ZooKeeper> zooKeepers = new ArrayList<ZooKeeper>();
	private Map<String, NodeWriter> nodeWriters = new HashMap<String, NodeWriter>();
	private static Map<String, IServiceInfo> allKnownServices = new HashMap<String, IServiceInfo>();
	private Configuration config;
	private WriteRoot writeRoot;
	private Lock writeRootLock = new Lock().lock();

	public WatchManager(Configuration config) {
		this.config = config;
		DiscoveryActivator.registerBundleStoppingListner(this);
	}

	public synchronized void publish(final ServiceReference ref) {
		Assert.isNotNull(ref);
		String serviceid = ref.getProperty(Constants.SERVICE_ID).toString();
		if (WatchManager.this.getNodeWriters().containsKey(serviceid))
			return;
		if (!WatchManager.this.writeRootLock.isOpen()) {
			synchronized (WatchManager.this.writeRootLock) {
				try {
					/* wait for the server to get ready */
					WatchManager.this.writeRootLock.wait();
				} catch (InterruptedException e) {
					Logger.log(LogService.LOG_DEBUG, e.getMessage(), e);
				}
			}
		}
		AdvertisedService published = new AdvertisedService(ref);
		allKnownServices.put(published.getServiceID().getName(), published);
		NodeWriter nodeWriter = new NodeWriter(published,
				WatchManager.this.writeRoot);
		WatchManager.this.getNodeWriters().put(serviceid, nodeWriter);
		nodeWriter.publish();
	}

	public synchronized void publish(final AdvertisedService published) {
		Assert.isNotNull(published);
		String serviceid = published.getServiceID().getServiceTypeID()
				.getInternal();
		if (WatchManager.this.getNodeWriters().containsKey(serviceid))
			return;
		if (!WatchManager.this.writeRootLock.isOpen()) {
			synchronized (WatchManager.this.writeRootLock) {
				try {
					/* wait for the server to get ready */
					WatchManager.this.writeRootLock.wait();
				} catch (InterruptedException e) {
					Logger.log(LogService.LOG_DEBUG, e.getMessage(), e);
				}
			}
		}
		NodeWriter nodeWriter = new NodeWriter(published,
				WatchManager.this.writeRoot);
		WatchManager.this.getNodeWriters().put(serviceid, nodeWriter);
		allKnownServices.put(published.getServiceID().getName(), published);
		nodeWriter.publish();
	}

	public synchronized void unpublish(final String id) {
		Assert.isNotNull(id);
		IServiceInfo p = AdvertisedService.removePublished(id);
		if (p == null) {
			return;
		}
		NodeWriter nw = getNodeWriters().remove(id);
		allKnownServices.remove(nw.getNode().getWrappedService().getServiceID()
				.getName());
		if (nw != null) {
			nw.remove();
		}
		nw = null;
	}

	public synchronized void update(ServiceReference ref) {
		Assert.isNotNull(ref);
		unpublish((String) ref.getProperty(Constants.SERVICE_ID).toString());
		publish(ref);
	}

	public void watch() {
		switch (getConfig().getFlavor()) {
		case CENTRALIZED:
			ZooDiscoveryContainer.CACHED_THREAD_POOL.execute(new Runnable() {
				public void run() {
					WatchManager.this.writeRoot = new WriteRoot(getConfig()
							.getServerIps(), WatchManager.this);
					synchronized (WatchManager.this.writeRootLock) {
						WatchManager.this.writeRootLock.unlock();
						WatchManager.this.writeRootLock.notifyAll();
					}
				}
			});
			ZooDiscoveryContainer.CACHED_THREAD_POOL.execute(new Runnable() {
				public void run() {
					new ReadRoot(getConfig().getServerIps(), WatchManager.this);
				}
			});

			break;
		case REPLICATED:
			ZooDiscoveryContainer.CACHED_THREAD_POOL.execute(new Runnable() {
				public void run() {
					WatchManager.this.writeRoot = new WriteRoot(getConfig()
							.getServerIps(),
							WatchManager.this);
					synchronized (WatchManager.this.writeRootLock) {
						WatchManager.this.writeRootLock.unlock();
						WatchManager.this.writeRootLock.notifyAll();
					}
				}
			});
			ZooDiscoveryContainer.CACHED_THREAD_POOL.execute(new Runnable() {
				public void run() {
					new ReadRoot(getConfig().getServerIps(), WatchManager.this);
				}
			});

			break;
		case STANDALONE:
			ZooDiscoveryContainer.CACHED_THREAD_POOL.execute(new Runnable() {
				public void run() {
					WatchManager.this.writeRoot = new WriteRoot(Geo.getHost(),
							WatchManager.this);
					if (!WatchManager.this.writeRoot.isConnected()) {
						synchronized (WatchManager.this.writeRoot) {
							try {
								/*
								 * wait for connection with the server to write
								 * to.
								 */
								WatchManager.this.writeRoot.wait();
							} catch (InterruptedException e) {
								Logger.log(LogService.LOG_DEBUG,
										e.getMessage(), e);
							}
						}
					}
					synchronized (WatchManager.this.writeRootLock) {
						/* resume publication */
						WatchManager.this.writeRootLock.unlock();
						WatchManager.this.writeRootLock.notifyAll();
					}
				}
			});
			ZooDiscoveryContainer.CACHED_THREAD_POOL.execute(new Runnable() {
				public void run() {
					for (String ip : getConfig().getServerIps().split(",")) { //$NON-NLS-1$
						new ReadRoot(ip, WatchManager.this);
					}
				}
			});
			break;
		}
	}

	public void bundleStopping() {
		try {
			Set<NodeWriter> copy = new HashSet<NodeWriter>();
			copy.addAll(this.getNodeWriters().values());
			for (NodeWriter nw : copy) {
				if (nw.getNode().isLocalNode())
					nw.remove();
			}
			copy.clear();
			for (ZooKeeper zk : this.zooKeepers) {
				if (zk != null)
					zk.close();
			}
		} catch (InterruptedException e) {
			// Ignore. We're already down at this point.
		}
	}

	public void setConfig(Configuration config) {
		this.config = config;
	}

	public Configuration getConfig() {
		return this.config;
	}

	public void addZooKeeper(ZooKeeper zooKeeper) {
		Assert.isNotNull(zooKeeper);
		this.zooKeepers.add(zooKeeper);
	}

	public void removeZooKeeper(ZooKeeper zooKeeper) {
		this.zooKeepers.remove(zooKeeper);
	}

	public WriteRoot getWriteRoot() {
		return this.writeRoot;
	}

	public Map<String, NodeWriter> getNodeWriters() {
		return this.nodeWriters;
	}

	private class Lock {
		boolean state;

		boolean isOpen() {
			return this.state;
		}

		Lock unlock() {
			this.state = true;
			return this;
		}

		Lock lock() {
			this.state = false;
			return this;
		}
	}

	public void unpublishAll() {
		for (NodeWriter nw : getNodeWriters().values()) {
			nw.remove();
			allKnownServices.remove(nw.getNode().getWrappedService()
					.getServiceID().getName());
		}
	}

	public void republishAll() {
		NodeWriter nws[] = getNodeWriters().values().toArray(
				new NodeWriter[getNodeWriters().size()]);
		for (int i = 0; i < nws.length; i++) {
			nws[i].getNode().regenerateNodeId();
			nws[i].publish();
			allKnownServices.put(nws[i].getNode().getWrappedService()
					.getServiceID().getName(), nws[i].getNode()
					.getWrappedService());
		}
	}

	public static Map<String, IServiceInfo> getAllKnownServices() {
		return allKnownServices;
	}

	public void dipose() {
		unpublishAll();
		try {
			getWriteRoot().getWriteKeeper().close();
		} catch (Throwable e) {
			// ignore
		}
	}
}
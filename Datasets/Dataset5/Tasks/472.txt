if (sotypedesc.getName() != null) {

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc., Peter Nehrer, Boris Bokowski. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.provider.datashare;

import java.lang.reflect.Constructor;
import java.util.HashMap;
import java.util.Map;
import org.eclipse.ecf.core.ISharedObject;
import org.eclipse.ecf.core.ISharedObjectContainerConfig;
import org.eclipse.ecf.core.ISharedObjectTransactionConfig;
import org.eclipse.ecf.core.ISharedObjectTransactionParticipantsFilter;
import org.eclipse.ecf.core.SharedObjectCreateException;
import org.eclipse.ecf.core.SharedObjectDescription;
import org.eclipse.ecf.core.SharedObjectFactory;
import org.eclipse.ecf.core.SharedObjectTypeDescription;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.identity.IDInstantiationException;
import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.ecf.core.identity.StringID;
import org.eclipse.ecf.core.util.ECFException;
import org.eclipse.ecf.datashare.IChannel;
import org.eclipse.ecf.datashare.IChannelConfig;
import org.eclipse.ecf.datashare.IChannelContainer;
import org.eclipse.ecf.datashare.IChannelListener;
import org.eclipse.ecf.provider.generic.TCPClientSOContainer;

public class DatashareContainer extends TCPClientSOContainer implements
		IChannelContainer {
	protected static final int DEFAULT_CONTAINER_KEEP_ALIVE = 30000;
	protected static final int DEFAULT_TRANSACTION_WAIT = 30000;
	
	public DatashareContainer(ISharedObjectContainerConfig config) {
		super(config, DEFAULT_CONTAINER_KEEP_ALIVE);
	}
	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.datashare.IChannelContainer#createChannel(org.eclipse.ecf.datashare.IChannelConfig)
	 */
	public IChannel createChannel(final ID newID,
			final IChannelListener listener, final Map properties)
			throws ECFException {
		return createChannel(new IChannelConfig() {
			public IChannelListener getListener() {
				return listener;
			}
			public ISharedObjectTransactionConfig getTransactionConfig() {
				return new ISharedObjectTransactionConfig() {
					public int getTimeout() {
						return DEFAULT_TRANSACTION_WAIT;
					}
					public ISharedObjectTransactionParticipantsFilter getParticipantsFilter() {
						return null;
					}};
			}
			public Object getAdapter(Class adapter) {
				return null;
			}
			public SharedObjectDescription getHostDescription() {
				return new SharedObjectDescription(BaseChannel.class, newID,
						properties);
			}
		});
	}
	protected SharedObjectDescription getDefaultChannelDescription()
			throws IDInstantiationException {
		return new SharedObjectDescription(BaseChannel.class, IDFactory
				.getDefault().createGUID(), new HashMap());
	}
	protected ISharedObject createSharedObject(
			SharedObjectTypeDescription typeDescription,
			ISharedObjectTransactionConfig transactionConfig,
			IChannelListener listener) throws SharedObjectCreateException {
		Class clazz;
		try {
			clazz = Class.forName(typeDescription.getClassName());
		} catch (ClassNotFoundException e) {
			throw new SharedObjectCreateException(
					"No constructor for shared object of class "
							+ typeDescription.getClassName(), e);
		}
		Constructor cons = null;
		try {
			cons = clazz.getDeclaredConstructor(new Class[] {
					ISharedObjectTransactionConfig.class,
					IChannelListener.class });
		} catch (NoSuchMethodException e) {
			throw new SharedObjectCreateException(
					"No constructor for shared object of class "
							+ typeDescription.getClassName(), e);
		}
		ISharedObject so = null;
		try {
			so = (ISharedObject) cons.newInstance(new Object[] {
					transactionConfig, listener });
		} catch (Exception e) {
			throw new SharedObjectCreateException(
					"Cannot create instance of class "
							+ typeDescription.getClassName(), e);
		}
		return so;
	}
	public IChannel createChannel(IChannelConfig newChannelConfig)
			throws ECFException {
		SharedObjectDescription sodesc = newChannelConfig.getHostDescription();
		if (sodesc == null)
			sodesc = getDefaultChannelDescription();
		SharedObjectTypeDescription sotypedesc = sodesc.getTypeDescription();
		IChannelListener listener = newChannelConfig.getListener();
		ISharedObjectTransactionConfig transactionConfig = newChannelConfig
				.getTransactionConfig();
		ISharedObject so = null;
		if (sotypedesc.getDescription() != null) {
			so = SharedObjectFactory
					.getDefault()
					.createSharedObject(
							sotypedesc,
							new String[] {
									ISharedObjectTransactionConfig.class
											.getName(),
									IChannelListener.class.getName() },
							new Object[] { transactionConfig, listener });
		} else {
			so = createSharedObject(sotypedesc, transactionConfig, listener);
		}
		IChannel channel = (IChannel) so.getAdapter(IChannel.class);
		if (channel == null)
			throw new SharedObjectCreateException("Cannot coerce object "
					+ channel + " to be of type IChannel");
		ID newID = sodesc.getID();
		if (newID == null)
			newID = IDFactory.getDefault().createGUID();
		Map properties = sodesc.getProperties();
		if (properties == null)
			properties = new HashMap();
		// Now add channel to container...this will block
		getSharedObjectManager().addSharedObject(newID, so, properties);
		return channel;
	}
	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.datashare.IChannelContainer#getChannel(org.eclipse.ecf.core.identity.ID)
	 */
	public IChannel getChannel(ID channelID) {
		return (IChannel) getSharedObjectManager().getSharedObject(channelID);
	}
	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.datashare.IChannelContainer#disposeChannel(org.eclipse.ecf.core.identity.ID)
	 */
	public boolean removeChannel(ID channelID) {
		ISharedObject o = getSharedObjectManager()
				.removeSharedObject(channelID);
		return (o != null);
	}
	/*
	 * (non-Javadoc)
	 * @see org.eclipse.ecf.datashare.IChannelContainer#getChannelNamespace()
	 */
	public Namespace getChannelNamespace() {
		return IDFactory.getDefault().getNamespaceByName(StringID.class.getName());
	}
}
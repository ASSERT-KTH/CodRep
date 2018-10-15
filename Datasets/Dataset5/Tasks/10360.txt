//IChannelMessageEvent cme = (IChannelMessageEvent) event;

/****************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Composent, Inc. - initial API and implementation
 *****************************************************************************/

package org.eclipse.ecf.tests.datashare;

import java.util.Hashtable;

import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDCreateException;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.datashare.IChannel;
import org.eclipse.ecf.datashare.IChannelContainerAdapter;
import org.eclipse.ecf.datashare.IChannelListener;
import org.eclipse.ecf.datashare.events.IChannelEvent;
import org.eclipse.ecf.datashare.events.IChannelMessageEvent;
import org.eclipse.ecf.tests.ContainerAbstractTestCase;

public class ChannelTest extends ContainerAbstractTestCase {

	/**
	 * 
	 */
	private static final String CHANNEL_NAME = "channel";
	private static final String CHANNEL_NAME_1 = "channel1";

	protected Hashtable messageEvents = new Hashtable();
	
	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.tests.connect.ContainerConnectTestCase#createServerAndClients()
	 */
	protected void createServerAndClients() throws Exception {
		clientCount = 5;
		super.createServerAndClients();
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see junit.framework.TestCase#setUp()
	 */
	protected void setUp() throws Exception {
		super.setUp();
		createServerAndClients();
		addChannelToClients();
		connectClients();
	}

	/**
	 * 
	 */
	private void addChannelToClients() throws Exception {
		for(int i=0; i < clientCount; i++) {
			IChannelContainerAdapter channelContainer = getChannelContainer(i);
			channelContainer.createChannel(getNewID(CHANNEL_NAME),getIChannelListener(getContainerID(i)),null);
		}
	}

	protected void clearClientEvents() {
		messageEvents.clear();
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see junit.framework.TestCase#tearDown()
	 */
	protected void tearDown() throws Exception {
		cleanUpServerAndClients();
		super.tearDown();
		clearClientEvents();
	}

	protected ID getContainerID(int clientIndex) {
		return getClients()[clientIndex].getID();
	}
	
	protected IChannelContainerAdapter getChannelContainer(int clientIndex) {
		return (IChannelContainerAdapter) getClients()[clientIndex].getAdapter(IChannelContainerAdapter.class);
	}
	
	public void testGetChannelContainerAdapter() throws Exception {
		IChannelContainerAdapter channelContainer = getChannelContainer(0);
		assertNotNull(channelContainer);
	}
	
	public void testCreateChannel() throws Exception {
		IChannelContainerAdapter channelContainer = getChannelContainer(0);
		IChannel channel = channelContainer.createChannel(getNewID(CHANNEL_NAME_1),getIChannelListener(getContainerID(0)),null);
		assertNotNull(channel);
		assertNotNull(channel.getID());
		assertNotNull(channel.getListener());
	}

	public void testGetChannelFromContainer() throws Exception {
		IChannelContainerAdapter channelContainer = getChannelContainer(0);
		channelContainer.createChannel(getNewID(CHANNEL_NAME_1),getIChannelListener(getContainerID(0)),null);
		assertNotNull(channelContainer.getChannel(getNewID(CHANNEL_NAME_1)));
	}

	public void testGetChannelNamespace() throws Exception {
		IChannelContainerAdapter channelContainer = getChannelContainer(0);
		assertNotNull(channelContainer.getChannelNamespace());
	}
	
	public void testSender() throws Exception {
		IChannelContainerAdapter senderContainer = getChannelContainer(0);
		IChannel sender = senderContainer.getChannel(getNewID(CHANNEL_NAME));
		assertNotNull(sender);
		sender.sendMessage(new String("hello").getBytes());
		sleep(3000);
		assertNotNull(messageEvents.get(getContainerID(1)));
		assertNotNull(messageEvents.get(getContainerID(2)));
		assertNotNull(messageEvents.get(getContainerID(3)));
		assertNotNull(messageEvents.get(getContainerID(4)));
	}
	/**
	 * @return
	 */
	private IChannelListener getIChannelListener(final ID id) throws Exception {
		return new IChannelListener() {
			public void handleChannelEvent(IChannelEvent event) {
				if (event instanceof IChannelMessageEvent) {
					IChannelMessageEvent cme = (IChannelMessageEvent) event;
					messageEvents.put(id,event);
				}
			}};
	}

	/**
	 * @return
	 */
	private ID getNewID(String id) throws IDCreateException {
		return IDFactory.getDefault().createStringID(id);
	}

}
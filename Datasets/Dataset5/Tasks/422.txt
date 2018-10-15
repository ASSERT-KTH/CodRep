import org.eclipse.ecf.tests.provider.xmpp.XMPP;

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

package org.eclipse.ecf.tests.provider.xmpp.datashare;

import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDCreateException;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.datashare.IChannel;
import org.eclipse.ecf.datashare.IChannelContainerAdapter;
import org.eclipse.ecf.datashare.IChannelListener;
import org.eclipse.ecf.datashare.events.IChannelEvent;
import org.eclipse.ecf.datashare.events.IChannelMessageEvent;
import org.eclipse.ecf.tests.ContainerAbstractTestCase;
import org.ecllpse.ecf.tests.provider.xmpp.XMPP;

public class ChannelTest extends ContainerAbstractTestCase {

	private static final String CHANNEL_NAME = "channel";

	private static final int SEND_MESSAGE_COUNT = 5;

	private ID channelID;
	
	/* (non-Javadoc)
	 * @see org.eclipse.ecf.tests.presence.AbstractPresenceTestCase#getClientContainerName()
	 */
	protected String getClientContainerName() {
		return XMPP.CONTAINER_NAME;
	}

	protected void setUp() throws Exception {
		super.setUp();
		setClientCount(2);
		clients = createClients();
		channelID = IDFactory.getDefault().createStringID(CHANNEL_NAME);
		connectClients();
		for (int i = 0; i < clientCount; i++) {
			final IChannelContainerAdapter channelContainer = getChannelContainer(i);
			channelContainer.createChannel(channelID, getIChannelListener(getContainerID(i)), null);
		}
	}

	protected ID getServerConnectID(int client) {
		try {
			return IDFactory.getDefault().createID(getClient(client).getConnectNamespace(), getUsername(client));
		} catch (final IDCreateException e) {
			fail("Could not create server connect ID");
			return null;
		}
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see junit.framework.TestCase#tearDown()
	 */
	protected void tearDown() throws Exception {
		cleanUpClients();
		super.tearDown();
	}

	public void testSendMessage() throws Exception {
		final IChannel ch0 = getChannelContainer(0).getChannel(channelID);
		ID target1 = getClient(1).getConnectedID();
		ch0.sendMessage(target1, new String("hello").getBytes());
		sleep(3000);
	}

	public void testBiSendMessage() throws Exception {
		final IChannel ch0 = getChannelContainer(0).getChannel(channelID);
		final IChannel ch1 = getChannelContainer(1).getChannel(channelID);
		
		ID target1 = getClient(1).getConnectedID();
		ID target0 = getClient(0).getConnectedID();
		
		ch0.sendMessage(target1, new String("hello").getBytes());
		ch1.sendMessage(target0, new String("hello").getBytes());
		sleep(3000);
	}


	public void testSendMessages() throws Exception {
		final IChannel ch0 = getChannelContainer(0).getChannel(channelID);
		ID target1 = getClient(1).getConnectedID();
		for(int i=0; i < SEND_MESSAGE_COUNT; i++) {
			ch0.sendMessage(target1, new String("hello.  msg#="+i).getBytes());
			sleep(500);
		}
		sleep(3000);
	}

	public void testBiSendMessages() throws Exception {
		final IChannel ch0 = getChannelContainer(0).getChannel(channelID);
		final IChannel ch1 = getChannelContainer(1).getChannel(channelID);
		
		ID target1 = getClient(1).getConnectedID();
		ID target0 = getClient(0).getConnectedID();
				
		for(int i=0; i < SEND_MESSAGE_COUNT; i++) {
			ch0.sendMessage(target1, new String("hello.  msg#="+i).getBytes());
			sleep(500);
			ch1.sendMessage(target0, new String("hello.  msg#="+i).getBytes());
		}
		sleep(3000);
	}

	protected IChannelListener getIChannelListener(final ID containerid) throws Exception {
		return new IChannelListener() {
			public void handleChannelEvent(IChannelEvent event) {
				if (event instanceof IChannelMessageEvent) {
					IChannelMessageEvent cme = (IChannelMessageEvent) event;
					System.out.println("receivercontainerid="+containerid+"; fromcontainerid="+cme.getFromContainerID()+"; channelid="+cme.getChannelID());
					System.out.println("   event="+event);
					System.out.println("   message="+new String(cme.getData()));
				}
			}
		};
	}

	private ID getContainerID(int clientIndex) {
		return getClients()[clientIndex].getID();
	}

	private IChannelContainerAdapter getChannelContainer(int clientIndex) {
		return (IChannelContainerAdapter) getClients()[clientIndex].getAdapter(IChannelContainerAdapter.class);
	}


}
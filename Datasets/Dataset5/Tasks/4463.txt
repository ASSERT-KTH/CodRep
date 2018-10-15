private static final String PASSWORD_ATT = "connectpassword"; //$NON-NLS-1$

/*******************************************************************************
 * Copyright (c) 2007 IBM Corporation and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     IBM Corporation - initial API and implementation
 *******************************************************************************/
package org.eclipse.ecf.internal.presence.bot;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.IConfigurationElement;
import org.eclipse.core.runtime.IExtensionRegistry;
import org.eclipse.ecf.presence.bot.IChatRoomBotEntry;
import org.eclipse.ecf.presence.bot.IChatRoomMessageHandler;
import org.eclipse.ecf.presence.bot.IIMBotEntry;
import org.eclipse.ecf.presence.bot.IIMMessageHandler;
import org.osgi.framework.BundleActivator;
import org.osgi.framework.BundleContext;
import org.osgi.util.tracker.ServiceTracker;

/**
 * The activator class controls the plug-in life cycle
 */
public class Activator implements BundleActivator {

	private static final String CHATROOMPASSWORD_ATT = "chatroompassword"; //$NON-NLS-1$
	private static final String CHATROOM_ATT = "chatroom"; //$NON-NLS-1$
	private static final String PASSWORD_ATT = "password"; //$NON-NLS-1$
	private static final String CONNECT_ID_ATT = "connectID"; //$NON-NLS-1$
	private static final String CONTAINER_FACTORY_NAME_ATT = "containerFactoryName"; //$NON-NLS-1$
	private static final String NAME_ATT = "name"; //$NON-NLS-1$
	private static final String ID_ATT = "id"; //$NON-NLS-1$
	private static final String CLASS_ATT = "class"; //$NON-NLS-1$
	private static final String FILTEREXPRESSION_ATT = "filterexpression"; //$NON-NLS-1$
	private static final String CHATROOMROBOTID_ATT = "chatroomrobotid"; //$NON-NLS-1$
	private static final String IMROBOTID_ATT = "imrobotid"; //$NON-NLS-1$
	// The plug-in ID
	public static final String PLUGIN_ID = "org.eclipse.ecf.presence.bot"; //$NON-NLS-1$
	public static final String CHATROOM_COMMAND_HANDLER_EPOINT_NAME = "chatroommessagehandler"; //$NON-NLS-1$
	public static final String CHATROOM_COMMAND_HANDLER_EPOINT = PLUGIN_ID
			+ "." //$NON-NLS-1$
			+ CHATROOM_COMMAND_HANDLER_EPOINT_NAME;

	public static final String IM_COMMAND_HANDLER_EPOINT_NAME = "immessagehandler"; //$NON-NLS-1$
	public static final String IM_COMMAND_HANDLER_EPOINT = PLUGIN_ID + "." //$NON-NLS-1$
			+ IM_COMMAND_HANDLER_EPOINT_NAME;

	public static final String CHATROOM_BOT_EPOINT_NAME = "chatroomrobot"; //$NON-NLS-1$
	public static final String CHATROOM_BOT_EPOINT = PLUGIN_ID
			+ "." + CHATROOM_BOT_EPOINT_NAME; //$NON-NLS-1$

	public static final String IM_BOT_EPOINT_NAME = "imrobot"; //$NON-NLS-1$
	public static final String IM_BOT_EPOINT = PLUGIN_ID
			+ "." + IM_BOT_EPOINT_NAME; //$NON-NLS-1$

	// The shared instance
	private static Activator plugin;

	private BundleContext context = null;

	private ServiceTracker extensionRegistryTracker = null;

	private Map chatroombots = new HashMap();
	private Map chatbotcommands = new HashMap();

	private Map imbots = new HashMap();
	private Map imbotcommands = new HashMap();

	/**
	 * The constructor
	 */
	public Activator() {
	}

	public IExtensionRegistry getExtensionRegistry() {
		if (extensionRegistryTracker == null) {
			this.extensionRegistryTracker = new ServiceTracker(context,
					IExtensionRegistry.class.getName(), null);
			this.extensionRegistryTracker.open();
		}
		return (IExtensionRegistry) extensionRegistryTracker.getService();
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.core.runtime.Plugins#start(org.osgi.framework.BundleContext)
	 */
	public void start(BundleContext context) throws Exception {
		plugin = this;
		this.context = context;
		loadChatBotExtensions();
		loadIMBotExtensions();
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.core.runtime.Plugin#stop(org.osgi.framework.BundleContext)
	 */
	public void stop(BundleContext context) throws Exception {
		if (extensionRegistryTracker != null) {
			extensionRegistryTracker.close();
			extensionRegistryTracker = null;
		}
		plugin = null;
		this.context = null;
	}

	/**
	 * Returns the shared instance
	 * 
	 * @return the shared instance
	 */
	public static Activator getDefault() {
		return plugin;
	}

	public Map getChatRoomBots() {
		return this.chatroombots;
	}

	public Map getIMBots() {
		return this.imbots;
	}

	private void loadChatBotExtensions() throws CoreException {
		// load the command handlers
		IExtensionRegistry reg = getExtensionRegistry();
		if (reg != null) {
			IConfigurationElement[] elements = reg
					.getConfigurationElementsFor(CHATROOM_COMMAND_HANDLER_EPOINT);
			for (int i = 0; i < elements.length; i++) {
				String id = elements[i].getAttribute(CHATROOMROBOTID_ATT);
				String expression = elements[i]
						.getAttribute(FILTEREXPRESSION_ATT);
				IChatRoomMessageHandler handler = (IChatRoomMessageHandler) elements[i]
						.createExecutableExtension(CLASS_ATT);
				List c = (List) chatbotcommands.get(id);
				if (c == null) {
					c = new ArrayList();
					c.add(new ChatRoomMessageHandlerEntry(expression, handler));
					chatbotcommands.put(id, c);
				} else {
					c.add(new ChatRoomMessageHandlerEntry(expression, handler));
					chatbotcommands.put(id, c);
				}
			}

			// load the chat room bots
			elements = reg.getConfigurationElementsFor(CHATROOM_BOT_EPOINT);
			for (int i = 0; i < elements.length; i++) {
				String id = elements[i].getAttribute(ID_ATT);
				String name = elements[i].getAttribute(NAME_ATT);
				String containerFactoryName = elements[i]
						.getAttribute(CONTAINER_FACTORY_NAME_ATT);
				String connectID = elements[i].getAttribute(CONNECT_ID_ATT);
				String password = elements[i].getAttribute(PASSWORD_ATT);
				String chatroom = elements[i].getAttribute(CHATROOM_ATT);
				String chatroompassword = elements[i]
						.getAttribute(CHATROOMPASSWORD_ATT);
				List c = (List) chatbotcommands.get(id);
				if (c == null)
					c = new ArrayList();
				IChatRoomBotEntry bot = new ChatRoomBotEntry(id, name,
						containerFactoryName, connectID, password, chatroom,
						chatroompassword, c);
				chatroombots.put(id, bot);
			}
		}

	}

	private void loadIMBotExtensions() throws CoreException {
		// load the command handlers
		IExtensionRegistry reg = getExtensionRegistry();
		if (reg != null) {
			IConfigurationElement[] elements = reg
					.getConfigurationElementsFor(IM_COMMAND_HANDLER_EPOINT);
			for (int i = 0; i < elements.length; i++) {
				String id = elements[i].getAttribute(IMROBOTID_ATT);
				String expression = elements[i]
						.getAttribute(FILTEREXPRESSION_ATT);
				IIMMessageHandler handler = (IIMMessageHandler) elements[i]
						.createExecutableExtension(CLASS_ATT);
				List c = (List) imbotcommands.get(id);
				if (c == null) {
					c = new ArrayList();
					c.add(new IMMessageHandlerEntry(expression, handler));
					imbotcommands.put(id, c);
				} else {
					c.add(new IMMessageHandlerEntry(expression, handler));
					imbotcommands.put(id, c);
				}
			}

			// load the im bots
			elements = reg.getConfigurationElementsFor(IM_BOT_EPOINT);
			for (int i = 0; i < elements.length; i++) {
				String id = elements[i].getAttribute(ID_ATT);
				String name = elements[i].getAttribute(NAME_ATT);
				String containerFactoryName = elements[i]
						.getAttribute(CONTAINER_FACTORY_NAME_ATT);
				String connectID = elements[i].getAttribute(CONNECT_ID_ATT);
				String password = elements[i].getAttribute(PASSWORD_ATT);
				List c = (List) imbotcommands.get(id);
				if (c == null)
					c = new ArrayList();
				IIMBotEntry bot = new IMBotEntry(id, name,
						containerFactoryName, connectID, password, c);
				imbots.put(id, bot);
			}
		}

	}

}
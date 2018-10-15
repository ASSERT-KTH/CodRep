protected static String CONTAINER_TYPE = "ecf.xmpp.smack";

package org.eclipse.ecf.example.clients;

import org.eclipse.ecf.core.ContainerFactory;
import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.identity.IDInstantiationException;
import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.ecf.core.security.ConnectContextFactory;
import org.eclipse.ecf.core.util.ECFException;
import org.eclipse.ecf.presence.IMessageListener;
import org.eclipse.ecf.presence.IMessageSender;
import org.eclipse.ecf.presence.IPresenceContainer;

public class XMPPClient {
	
	protected static String CONTAINER_TYPE = "ecf.xmpp";
	
	Namespace namespace = null;
	IContainer container = null;
	IPresenceContainer presence = null;
	IMessageSender sender = null;
	ID userID = null;
	
	// Interface for receiving messages
	IMessageReceiver receiver = null;
	
	public XMPPClient() {
		this(null);
	}
	
	public XMPPClient(IMessageReceiver receiver) {
		super();
		this.receiver = receiver;
	}
	public void connect(String account, String password) throws ECFException {
		container = ContainerFactory.getDefault().makeContainer(CONTAINER_TYPE);
		namespace = container.getConnectNamespace();
		ID targetID = IDFactory.getDefault().makeID(namespace, account);
		presence = (IPresenceContainer) container
				.getAdapter(IPresenceContainer.class);
		sender = presence.getMessageSender();
		presence.addMessageListener(new IMessageListener() {
			public void handleMessage(ID fromID, ID toID, Type type, String subject, String messageBody) {
				if (receiver != null) {
					receiver.handleMessage(fromID.getName(), messageBody);
				}
			}
		});
		// Now connect
		container.connect(targetID,ConnectContextFactory.makePasswordConnectContext(password));
		userID = getID(account);
	}
	private ID getID(String name) {
		try {
			return IDFactory.getDefault().makeID(namespace, name);
		} catch (IDInstantiationException e) {
			e.printStackTrace();
			return null;
		}
	}
	public void sendMessage(String jid, String msg) {
		if (sender != null) {
			sender.sendMessage(userID, getID(jid),
					IMessageListener.Type.NORMAL, "", msg);
		}
	}
	public synchronized boolean isConnected() {
		if (container == null) return false;
		return (container.getConnectedID() != null);
	}
	public synchronized void close() {
		if (container != null) {
			container.dispose();
			container = null;
			presence = null;
			sender = null;
			receiver = null;
			userID = null;
		}
	}
}
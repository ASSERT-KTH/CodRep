ConnectionFactory.getDefault().addDescription(cd);

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.provider.app;

import java.util.HashMap;
import java.util.Random;
import org.eclipse.ecf.core.ContainerTypeDescription;
import org.eclipse.ecf.core.ContainerFactory;
import org.eclipse.ecf.core.comm.ConnectionTypeDescription;
import org.eclipse.ecf.core.comm.ConnectionFactory;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.sharedobject.ISharedObject;
import org.eclipse.ecf.core.sharedobject.ISharedObjectContainer;
import org.eclipse.ecf.core.sharedobject.SharedObjectContainerFactory;
import org.eclipse.ecf.provider.generic.ContainerInstantiator;
import org.eclipse.ecf.provider.generic.TCPServerSOContainer;

/**
 * An ECF client container implementation that runs as an application.
 * <p>
 * Usage: java org.eclipse.ecf.provider.app.ClientApplication &lt;serverid&gt
 * <p>
 * If &lt;serverid&gt; is omitted or "-" is specified,
 * ecftcp://localhost:3282/server" is used.  
 *  
 */
public class ClientApplication {

	public static final int DEFAULT_WAITTIME = 40000;

	public static final int DEFAULT_TIMEOUT = TCPServerSOContainer.DEFAULT_KEEPALIVE;
	
	public static final String CONNECTION_NAME = org.eclipse.ecf.provider.comm.tcp.Client.class.getName();
	public static final String CONNECTION_CLASS = org.eclipse.ecf.provider.comm.tcp.Client.Creator.class.getName();
	
	public static final String CONTAINER_FACTORY_NAME = ContainerInstantiator.class.getName();
	public static final String CONTAINER_FACTORY_CLASS = CONTAINER_FACTORY_NAME;
	
	public static final String COMPOSENT_CONTAINER_NAME = ContainerInstantiator.class.getName();

	// Number of clients to create
	static int clientCount = 1;
	// Array of client instances
	ISharedObjectContainer [] sm = new ISharedObjectContainer[clientCount];
	// ServerApplication name to connect to
	String serverName = null;
	// Class names of any sharedObjects to be created.  If null, no sharedObjects created.
	String [] sharedObjectClassNames = null;
	// IDs of sharedObjects created
	ID [] sharedObjects = null;
	
	static ContainerTypeDescription contd = null;
	static Random aRan = new Random();
	public ClientApplication() {
		super();
	}
	
	public void init(String [] args) throws Exception {
		serverName = TCPServerSOContainer.getDefaultServerURL();
		if (args.length > 0) {
			if (!args[0].equals("-")) serverName = args[0];
		}
		if (args.length > 1) {
			sharedObjectClassNames = new String[args.length - 1];
			for (int i = 0; i < args.length - 1; i++) {
				sharedObjectClassNames[i] = args[i + 1];
			}
		}
		// Setup factory descriptions since Eclipse does not do this for us
		ConnectionTypeDescription cd = new ConnectionTypeDescription(ClientApplication.class.getClassLoader(),CONNECTION_NAME,CONNECTION_CLASS,null);
		ConnectionFactory.addDescription(cd);
		contd = new ContainerTypeDescription(ClientApplication.class.getClassLoader(),CONTAINER_FACTORY_NAME,CONTAINER_FACTORY_CLASS,null);
		ContainerFactory.getDefault().addDescription(contd);
		for(int i=0; i < clientCount; i++) {
			sm[i] = createClient();
		}
	}
	
	protected ISharedObjectContainer createClient() throws Exception {
		// Make identity instance for the new container
		ID newContainerID = IDFactory.getDefault().createGUID();
		ISharedObjectContainer result =  SharedObjectContainerFactory.getDefault().createSharedObjectContainer(contd,null,new Object[] { newContainerID, new Integer(DEFAULT_TIMEOUT)});
		return result;
	}
	
	public void connect(ID server) throws Exception {
		for(int i = 0; i < clientCount; i++) {
			System.out.print("ClientApplication "+sm[i].getID().getName()+" joining "+server.getName()+"...");
			sm[i].connect(server,null);
			System.out.println("completed.");
		}
	}

	public void disconnect() {
		for(int i = 0; i < clientCount; i++) {
			System.out.print("ClientApplication "+sm[i].getID().getName()+" leaving...");
			sm[i].disconnect();
			System.out.println("completed.");
		}
	}
	
	public void createSharedObjects() throws Exception {
		if (sharedObjectClassNames != null) {
			for(int j=0; j < clientCount; j++) {
				ISharedObjectContainer scg = sm[j];
				sharedObjects = new ID[sharedObjectClassNames.length];
				for(int i=0; i < sharedObjectClassNames.length; i++) {
					System.out.println("Creating sharedObject: "+sharedObjectClassNames[i]+" for client "+scg.getID().getName());
					ISharedObject so = (ISharedObject) Class.forName(sharedObjectClassNames[i]).newInstance();
					sharedObjects[i] = IDFactory.getDefault().createStringID(sharedObjectClassNames[i] + "_" +  i);
					scg.getSharedObjectManager().addSharedObject(sharedObjects[i], so, new HashMap());
					System.out.println("Created sharedObject for client "+scg.getID().getName());
				}
			}
		}

	}
	public void removeSharedObjects() throws Exception {
		if (sharedObjects == null) return;
		for(int j=0; j < clientCount; j++) {
			for(int i=0; i < sharedObjects.length; i++) {
				System.out.println("Removing sharedObject: "+sharedObjects[i].getName()+" for client "+sm[j].getID().getName());
				sm[j].getSharedObjectManager().removeSharedObject(sharedObjects[i]);
			}
		}
	}
	/**
	 * An ECF client container implementation that runs as an application.
	 * <p>
	 * Usage: java org.eclipse.ecf.provider.app.ClientApplication &lt;serverid&gt
	 * <p>
	 * If &lt;serverid&gt; is omitted or "-" is specified,
	 * ecftcp://localhost:3282/server" is used.  
	 *  
	 */
	public static void main(String[] args) throws Exception {
		ClientApplication st = new ClientApplication();
		st.init(args);
		// Get server id to join
		ID serverID = IDFactory.getDefault().createStringID(st.serverName);
		st.connect(serverID);
		st.createSharedObjects();
		System.out.println("Waiting "+DEFAULT_WAITTIME+" ms...");
		Thread.sleep(DEFAULT_WAITTIME);
		st.removeSharedObjects();
		st.disconnect();
		System.out.println("Exiting.");
	}

}
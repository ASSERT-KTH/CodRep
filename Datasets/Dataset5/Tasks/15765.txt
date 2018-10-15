scg.getSharedObjectManager().createSharedObject(sd);

package org.eclipse.ecf.provider.app;

import java.util.Random;
import org.eclipse.ecf.core.ISharedObjectContainer;
import org.eclipse.ecf.core.SharedObjectContainerDescription;
import org.eclipse.ecf.core.SharedObjectContainerFactory;
import org.eclipse.ecf.core.SharedObjectDescription;
import org.eclipse.ecf.core.comm.ConnectionDescription;
import org.eclipse.ecf.core.comm.ConnectionFactory;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDFactory;
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
	
	static SharedObjectContainerDescription contd = null;
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
		ConnectionDescription cd = new ConnectionDescription(ClientApplication.class.getClassLoader(),CONNECTION_NAME,CONNECTION_CLASS,null);
		ConnectionFactory.addDescription(cd);
		contd = new SharedObjectContainerDescription(ClientApplication.class.getClassLoader(),CONTAINER_FACTORY_NAME,CONTAINER_FACTORY_CLASS,null);
		SharedObjectContainerFactory.getDefault().addDescription(contd);
		for(int i=0; i < clientCount; i++) {
			sm[i] = makeClient();
		}
	}
	
	protected ISharedObjectContainer makeClient() throws Exception {
		// Make identity instance for the new container
		ID newContainerID = IDFactory.makeGUID();
		ISharedObjectContainer result =  SharedObjectContainerFactory.getDefault().makeSharedObjectContainer(contd,null,new Object[] { newContainerID, new Integer(DEFAULT_TIMEOUT)});
		return result;
	}
	
	public void joinGroup(ID server) throws Exception {
		for(int i = 0; i < clientCount; i++) {
			System.out.print("ClientApplication "+sm[i].getConfig().getID().getName()+" joining "+server.getName()+"...");
			sm[i].joinGroup(server,null);
			System.out.println("completed.");
		}
	}

	public void leaveGroup() {
		for(int i = 0; i < clientCount; i++) {
			System.out.print("ClientApplication "+sm[i].getConfig().getID().getName()+" leaving...");
			sm[i].leaveGroup();
			System.out.println("completed.");
		}
	}
	
	public void createStages() throws Exception {
		if (sharedObjectClassNames != null) {
			for(int j=0; j < clientCount; j++) {
				ISharedObjectContainer scg = sm[j];
				for(int i=0; i < sharedObjectClassNames.length; i++) {
					System.out.println("Creating sharedObject: "+sharedObjectClassNames[i]+" for client "+scg.getConfig().getID().getName());
					SharedObjectDescription sd = new SharedObjectDescription(IDFactory.makeStringID(String.valueOf(aRan.nextInt())),sharedObjectClassNames[i]);
					scg.getSharedObjectManager().createSharedObject(sd,null);
					System.out.println("Created sharedObject for client "+scg.getConfig().getID().getName());
				}
			}
		}

	}
	public void removeStages() throws Exception {
		if (sharedObjects == null) return;
		for(int j=0; j < clientCount; j++) {
			for(int i=0; i < sharedObjects.length; i++) {
				System.out.println("Removing stage: "+sharedObjects[i].getName()+" for client "+sm[j].getConfig().getID().getName());
				sm[j].getSharedObjectManager().removeSharedObject(sharedObjects[i]);
			}
		}
	}
	public static void main(String[] args) throws Exception {
		ClientApplication st = new ClientApplication();
		st.init(args);
		// Get server id to join
		ID serverID = IDFactory.makeStringID(st.serverName);
		st.joinGroup(serverID);
		st.createStages();
		System.out.println("Waiting "+DEFAULT_WAITTIME+" ms...");
		Thread.sleep(DEFAULT_WAITTIME);
		st.removeStages();
		st.leaveGroup();
		System.out.println("Exiting.");
	}

}
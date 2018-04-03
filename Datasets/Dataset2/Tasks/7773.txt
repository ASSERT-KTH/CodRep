"Testing JMX RMI-Connector from client to server\n" +

/*
* JBoss, the OpenSource J2EE webOS
* Distributable under LGPL license.
* See terms of license at gnu.org.
*/
package org.jboss.jmx.connector.rmi;

import java.util.Collection;
import java.util.Hashtable;
import java.util.Iterator;
import java.util.Vector;

import javax.management.MBeanAttributeInfo;
import javax.management.MBeanException;
import javax.management.MBeanInfo;
import javax.management.MBeanOperationInfo;
import javax.management.MBeanServer;
import javax.management.MBeanServerFactory;
import javax.management.Notification;
import javax.management.NotificationFilter;
import javax.management.NotificationListener;
import javax.management.ObjectInstance;
import javax.management.ObjectName;
import javax.management.ReflectionException;
import javax.management.RuntimeErrorException;
import javax.management.RuntimeMBeanException;
import javax.management.RuntimeOperationsException;
import javax.naming.InitialContext; 

import org.jboss.jmx.connector.ConnectorFactoryImpl;
import org.jboss.jmx.connector.JMXConnector;

/**
* Test Client for the JMX Client Connector. It cretes a local MBeanServer and
* adds the ConnectorFactory as first MBean. Then it will use the ConnectorFactory
* to local servers on the net and then to locate its offered protocols (Server
* side Connectors). After the user selected and server and a protocol its
* client-side connector will be loaded through the ConnectorFactory and a
* connection to the server will be established. Now the offered MBean on the
* remote server and its attributes and operations will be listed and at
* the end this test client will add a notification listener to all MBeans
* on the remote server. The user can now wait for a notification because
* the client will be up and running. If the user stops the client by
* <CTRL>-C it will stop and deregister the selected Connector (locally)
* and this will remove all the registered listeners.
*
*   @see <related>
*   @author Andreas Schaefer (andreas.schaefer@madplanet.com)
**/
public class TestClient {
	// Constants -----------------------------------------------------> 
	// Attributes ----------------------------------------------------> 
	// Static --------------------------------------------------------
	public static void main(String[] args)
		throws Exception
	{
		try {
			System.out.println(  );
			getUserInput(
				"Testing JMX Connector from client to server\n" +
				"===========================================\n\n" +
				"1. Instantiate local MBeanServer and add connector " +
				"factory as first MBean to search your net\n" +
				"=> hit any key to proceed"
			);
			// First create a MBeanServer and let it start
			final MBeanServer lLocalServer = MBeanServerFactory.createMBeanServer();
			// Then register the connector factory
			final ObjectInstance lFactoryInstance = lLocalServer.createMBean(
				"org.jboss.jmx.connector.ConnectorFactoryService",
				new ObjectName( lLocalServer.getDefaultDomain(), "name", "ConnectorFactory" )
			);
			System.out.println( "Found Factory: " + lFactoryInstance.getObjectName() );
			lLocalServer.invoke(
				lFactoryInstance.getObjectName(),
				"init",
				new Object[] {},
				new String[] {}
			);
			lLocalServer.invoke(
				lFactoryInstance.getObjectName(),
				"start",
				new Object[] {},
				new String[] {}
			);
			getUserInput(
				"\n" +
				"2. Lookup for all available connectors with the JNDI defined by jndi.properties\n" +
				"=> hit any key to proceed"
			);
			// Now let's list the available JMX Connectors
         InitialContext lContext = null;
         try {
            lContext = new InitialContext();
         }
         catch( Exception e ) {
            e.printStackTrace();
         }
         Hashtable lProperties = lContext.getEnvironment();
         ConnectorFactoryImpl.JBossConnectorTester lTester = new ConnectorFactoryImpl.JBossConnectorTester();
			Iterator lConnectors = (Iterator) lLocalServer.invoke(
				lFactoryInstance.getObjectName(),
				"getConnectors",
				new Object[] {
					lProperties,
               lTester
				},
				new String[] {
               Hashtable.class.getName(),
               ConnectorFactoryImpl.IConnectorTester.class.getName()
				}
			);
			int lCount = 0;
			StringBuffer lMessage = new StringBuffer();
			lMessage.append( "List of all available connectors on your net\n" );
			lMessage.append( "=========================================\n" );
         Vector lTemp = new Vector();
			while( lConnectors.hasNext() ) {
            ConnectorFactoryImpl.ConnectorName lName = (ConnectorFactoryImpl.ConnectorName) lConnectors.next();
            lTemp.addElement( lName );
				lMessage.append( " - " + ( lCount++ ) + ". connector is: " + lName + "\n" );
			}
			lMessage.append( "\n" );
			lMessage.append( "3. Select your connector by entering its number\n" );
			lMessage.append( "=> hit any key to proceed" );
			int lChoice = getUserInput( lMessage.toString() );
			Iterator i = lTemp.iterator();
			lCount = 0;
			while( i.hasNext() ) {
				if( ( lCount++ ) == lChoice ) {
					break;
				}
			}
			final ConnectorFactoryImpl.ConnectorName lConnectorName = (ConnectorFactoryImpl.ConnectorName) i.next();
			lMessage.setLength( 0 );
			lMessage.append(
				"\n" +
				"You selected connector: " + lConnectorName + "\n\n"
			);
			getUserInput(
				"5. Connect to the given connector\n" +
				"=> hit any key to proceed"
			);
			// Take the first server and its first protoccol and create a
			// connection to the remote MBeanServer
			JMXConnector lConnector = (JMXConnector) lLocalServer.invoke(
				lFactoryInstance.getObjectName(),
				"createConnection",
				new Object[] {
					lConnectorName
				},
				new String[] {
               lConnectorName.getClass().getName()
				}
			);
			getUserInput(
				"\n" +
				"6. List all available MBeans and its attributes\n" +
				"=> hit any key to proceed"
			);
			// List all services
			listServices( lConnector );
			getUserInput(
				"\n" +
				"7. Try to add a listener to all available MBeans.\n" +
				"Please note that this will keep this test client up and running waiting\n" +
				"for an event from the server. If there is no event comming then try\n" +
				"to shutdown the JBoss server.\n" +
				"To end this test client just hit <CTRL>-C\n"+
				"=> hit any key to proceed"
			);
			// Try to register to all available, remote MBeans
			registerListeners( lConnector );
			// Add shutdown hook to remove the connection before shut down
			try {
				Runtime.getRuntime().addShutdownHook(
					new Thread() {
						public void run() {
							System.err.println( "Shutdown" );
							try {
								lLocalServer.invoke(
									lFactoryInstance.getObjectName(),
									"removeConnection",
									new Object[] {
										lConnectorName
									},
									new String[] {
                              lConnectorName.getClass().getName()
									}
								);
								System.err.println("Shutting done");
							}
							catch( Throwable e ) {
								e.printStackTrace();
							}
						}
					}
				);
				System.out.println ("Shutdown hook added");
			}
			catch ( Throwable e ) {
				System.out.println( "Could not add shutdown hook" );
				// JDK 1.2.. ignore!
			}
		}
		catch( RuntimeMBeanException rme ) {
			System.err.println( "TestClient.main(), caught: " + rme +
				", target: " + rme.getTargetException() );
			rme.printStackTrace();
		}
		catch( MBeanException me ) {
			System.err.println( "TestClient.main(), caught: " + me +
				", target: " + me.getTargetException() );
			me.printStackTrace();
		}
		catch( RuntimeErrorException rte ) {
			System.err.println( "TestClient.main(), caught: " + rte +
				", target: " + rte.getTargetError() );
			rte.printStackTrace();
		}
		catch( ReflectionException re ) {
			System.err.println( "TestClient.main(), caught: " + re +
				", target: " + re.getTargetException() );
			re.printStackTrace();
		}
		catch( Exception e ) {
			System.err.println( "TestClient.main(), caught: " + e );
			e.printStackTrace();
		}
	}
	
	// Constructors --------------------------------------------------> 
	// Public --------------------------------------------------------
	public static void listServices( JMXConnector pConnector )
		throws Exception
	{
		try {
			Iterator i = pConnector.queryMBeans( null, null ).iterator();
			while( i.hasNext() ) {
				MBeanInfo info = pConnector.getMBeanInfo( ( (ObjectInstance) i.next() ).getObjectName() );
				System.out.println( "MBean: " + info.getClassName() );
				MBeanAttributeInfo[] aInfos = info.getAttributes();
				for( int k = 0; k < aInfos.length; k++ ) {
					System.out.println( "\t" + k + ". Attribute: " +
					aInfos[ k ].getName() );
				}
				MBeanOperationInfo[] oInfos = info.getOperations();
				for( int k = 0; k < oInfos.length; k++ ) {
					System.out.println( "\t" + k + ". Operation: " +
					oInfos[ k ].getName() );
				}
			}
		}
		catch (Exception e) {
			e.printStackTrace();
		}
	}
	public static void registerListeners( JMXConnector pConnector )
		throws Exception
	{
		try {
			// Add a listener to all of the available MBeans
			Iterator i = pConnector.queryMBeans( null, null ).iterator();
			int j = 0;
			while( i.hasNext() ) {
				ObjectInstance lBean = (ObjectInstance) i.next();
				try {
					pConnector.addNotificationListener(
						lBean.getObjectName(),
						(NotificationListener) new Listener(),
						(NotificationFilter) null,
						new NotSerializableHandback(
							lBean.getObjectName() + "" + j++
						)
					);
					System.out.println( "Added notification listener to: " + lBean.getObjectName() );
				}
				catch( RuntimeOperationsException roe ) {
					System.out.println( "Could not add listener to: " + lBean.getObjectName() +
						", reason could be that it is not a broadcaster" );
				}
				catch( Exception e ) {
					e.printStackTrace();
				}
			}
		}
		catch (Exception e) {
			e.printStackTrace();
		}
	}
	// Protected -----------------------------------------------------

	// Private -------------------------------------------------------
	
	private static int getUserInput( String lMessage ) {
		int lReturn = -1;
		try {
			System.out.println( lMessage );
			lReturn = System.in.read();
			System.in.skip( System.in.available() );
		}
		catch( Exception e ) {
			e.printStackTrace();
		}
		return lReturn;
	}
	
	private static class Listener implements NotificationListener {
		
		public void handleNotification(
			Notification pNotification,
			Object pHandback
		) {
			System.out.println( "Got notification: " + pNotification +
				", from: " + pHandback );
		}
	}
	
	private static class NotSerializableHandback {
		
		private static int			miCounter = 0;
		
		private String				mName;
		
		public NotSerializableHandback( String pName ) {
			mName = pName + "[ " + miCounter++ + " ]";
		}
		
		public String toString() {
			return "NotSerializableHandback[ " + mName + " ]";
		}
	}
}
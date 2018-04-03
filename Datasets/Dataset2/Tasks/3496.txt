import org.jboss.system.ServiceMBeanSupport;

/*
 * JBoss, the OpenSource J2EE webOS
 *
 * Distributable under LGPL license.
 * See terms of license at gnu.org.
 */

package org.jboss.jmx.client;

// import java.util.Arrays;
// import java.util.Collection;
import java.util.Iterator;
import java.util.Hashtable;

import javax.management.DynamicMBean;
import javax.management.ObjectName;
import javax.management.MBeanServer;

import javax.naming.InitialContext;

import org.jboss.jmx.interfaces.JMXConnector;
import org.jboss.util.ServiceMBeanSupport;

/**
* Factory delivering a list of servers and its available protocol connectors
* and after selected to initiate the connection
*
* This is just the (incomplete) interface of it
*
* @author <A href="mailto:andreas.schaefer@madplanet.com">Andreas &quot;Mad&quot; Schaefer</A>
**/
public class ConnectorFactoryService
	extends ServiceMBeanSupport
	implements ConnectorFactoryServiceMBean
{

	// Constants -----------------------------------------------------
	private static final String				JNDI_NAME = "jxm:connector:factory";
	
	// Static --------------------------------------------------------

	// Attributes ----------------------------------------------------
	/** Local MBeanServer this service is registered to **/
	private MBeanServer				mServer;
	/** Connector Factory instance **/
	private ConnectorFactoryImpl	mFactory;

	// Public --------------------------------------------------------
	
	public ConnectorFactoryService(
	) {
	}
	
   public Iterator getConnectors( Hashtable pProperties, ConnectorFactoryImpl.IConnectorTester pTester ) {
		return mFactory.getConnectors( pProperties, pTester );
   }

   public JMXConnector createConnection(
      ConnectorFactoryImpl.ConnectorName pConnector
   ) {
		return mFactory.createConnection( pConnector );
   }

   public void removeConnection(
      ConnectorFactoryImpl.ConnectorName pConnector
   ) {
		mFactory.removeConnection( pConnector );
   }

	public ObjectName getObjectName(
		MBeanServer pServer, 
		ObjectName pName
	) throws javax.management.MalformedObjectNameException {
		mServer = pServer;
		System.out.println( "ConnectorFactoryService.getObjectName(), server: " + mServer +
			", object name: " + OBJECT_NAME +
			", instance: " + new ObjectName( OBJECT_NAME ) );
		return new ObjectName( OBJECT_NAME );
	}
	
	public String getName() {
		return "JMX Client Connector Factory";
	}
	
	// Protected -----------------------------------------------------
	protected void initService() throws Exception {
            mFactory = new ConnectorFactoryImpl( mServer );
	}
	
	protected void startService() throws Exception {
//AS		new InitialContext().bind( JNDI_NAME, mFactory );
	}
	
	protected void stopService() {
/* AS
		try {
			new InitialContext().unbind(JNDI_NAME);
		}
		catch( Exception e )	{
			log.exception( e );
		}
*/
	}
}
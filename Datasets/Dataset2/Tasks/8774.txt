import org.jboss.system.ServiceMBean;

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
import javax.management.MBeanServer;

import org.jboss.jmx.interfaces.JMXConnector;
import org.jboss.util.ServiceMBean;

/**
* Factory delivering a list of servers and its available protocol connectors
* and after selected to initiate the connection
*
* This is just the (incomplete) interface of it
*
* @author <A href="mailto:andreas.schaefer@madplanet.com">Andreas &quot;Mad&quot; Schaefer</A>
**/
public interface ConnectorFactoryServiceMBean
	extends ServiceMBean
{

	// Constants -----------------------------------------------------
	public static final String OBJECT_NAME = "Factory:name=JMX";
	
	// Public --------------------------------------------------------

   /**
    * Look up for all registered JMX Connector at a given JNDI server
    *
    * @param pProperties List of properties defining the JNDI server
    * @param pTester Connector Tester implementation to be used
    *
    * @return An iterator on the list of ConnectorNames representing
    *         the found JMX Connectors
    **/
   public Iterator getConnectors( Hashtable pProperties, ConnectorFactoryImpl.IConnectorTester pTester );

   /**
    * Initiate a connection to the given server with the given protocol
    *
    * @param pConnector Connector Name used to identify the remote JMX Connector
    *
    * @return JMX Connector or null if server or protocol is not supported
    **/
   public JMXConnector createConnection(
      ConnectorFactoryImpl.ConnectorName pConnector
   );

   /**
    * Removes the given connection and frees the resources
    *
    * @param pConnector Connector Name used to identify the remote JMX Connector
    **/
   public void removeConnection(
      ConnectorFactoryImpl.ConnectorName pConnector
   );
}
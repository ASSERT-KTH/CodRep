extends org.jboss.system.ServiceMBean

/*
 * JBoss, the OpenSource J2EE webOS
 *
 * Distributable under LGPL license.
 * See terms of license at gnu.org.
 */

package org.jboss.jmx.server;

/**
* Server side MBean for the RMI connector
*
* @author <a href="mailto:rickard.oberg@telkel.com">Rickard Öberg</a>
* @author <A href="mailto:andreas.schaefer@madplanet.com">Andreas &quot;Mad&quot; Schaefer</A>
**/
public interface RMIConnectorServiceMBean
	extends org.jboss.util.ServiceMBean
{
	// Constants -----------------------------------------------------
	public static final String OBJECT_NAME = "Connector:name=RMI";

	// Public --------------------------------------------------------
    public String getJNDIName();
}
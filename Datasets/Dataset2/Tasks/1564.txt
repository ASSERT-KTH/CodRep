return OBJECT_NAME;

/*
* JBoss, the OpenSource J2EE webOS
*
* Distributable under LGPL license.
* See terms of license at gnu.org.
*/
package org.jboss.jmx.adaptor.rmi;

import java.io.File;
import java.net.InetAddress;
import java.net.URL;
import java.rmi.server.UnicastRemoteObject;
import java.rmi.RemoteException;
import java.rmi.ServerException;
import java.util.ArrayList;
import java.util.Iterator;

import javax.management.Attribute;
import javax.management.ObjectName;
import javax.management.QueryExp;
import javax.management.ObjectInstance;
import javax.management.AttributeNotFoundException;
import javax.management.InstanceNotFoundException;
import javax.management.InvalidAttributeValueException;
import javax.management.MBeanException;
import javax.management.ReflectionException;
import javax.management.MBeanServer;
import javax.naming.InitialContext;

// import org.jboss.logging.Log;
import org.jboss.system.ServiceMBeanSupport;

/**
*   <description>
*
* @author <a href="mailto:rickard.oberg@telkel.com">Rickard Öberg</a>
* @author <A href="mailto:andreas.schaefer@madplanet.com">Andreas &quot;Mad&quot; Schaefer</A>
**/
public class RMIAdaptorService
   extends ServiceMBeanSupport
   implements RMIAdaptorServiceMBean
{
   // Constants -----------------------------------------------------
   //AS I am not quite sure if this works but somehow the protocol should become
   //AS part of the JNDI name because there could be more than one protcol
   public static String JNDI_NAME = "jmx:rmi";
   public static String JMX_NAME = "jmx";
   public static String PROTOCOL_NAME = "rmi";

   // Attributes ----------------------------------------------------
   private MBeanServer server;
   private RMIAdaptorImpl adaptor;
   private String mHost;
   private String mName;

   // Static --------------------------------------------------------

   // Constructors --------------------------------------------------

   public RMIAdaptorService() {
      mName = null;
   }

   public RMIAdaptorService(
      String name
   ) {
      mName = name;
   }

   // Public --------------------------------------------------------
   public ObjectName getObjectName(
      MBeanServer server,
      ObjectName name
   ) throws javax.management.MalformedObjectNameException {
      this.server = server;
      return new ObjectName( OBJECT_NAME );
   }

   public String getName() {
      return "JMX RMI Connector";
   }

    public String getJNDIName() {
        if (mName != null)
        {
            return JMX_NAME + ":" + mHost + ":" + PROTOCOL_NAME + ":" + mName;
        }
        else
        {
            return JMX_NAME + ":" + mHost + ":" + PROTOCOL_NAME;
        }
    }

   // Protected -----------------------------------------------------

   protected void startService() throws Exception {
      mHost = InetAddress.getLocalHost().getHostName();
      adaptor = new RMIAdaptorImpl( server );
      new InitialContext().bind( getJNDIName(), adaptor );
   }

   protected void stopService() {
      try {
         new InitialContext().unbind( getJNDIName() );
      }
      catch( Exception e )   {
// AS ToDo
//         log.exception( e );
      }
   }
}
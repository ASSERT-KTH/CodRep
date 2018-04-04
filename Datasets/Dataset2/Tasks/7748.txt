catch (Exception e)

/*
 * jBoss, the OpenSource EJB server
 *
 * Distributable under GPL license.
 * See terms of license at gnu.org.
 */
 
package org.jboss.security;

import java.io.File;
import java.net.URL;
import java.rmi.server.UnicastRemoteObject;
import java.rmi.RemoteException;
import java.rmi.ServerException;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.Hashtable;

import javax.naming.InitialContext;
import javax.naming.Context;
import javax.naming.Reference;
import javax.naming.Name;
import javax.naming.spi.ObjectFactory;
import javax.naming.CommunicationException;

import javax.management.MBeanServer;
import javax.management.ObjectName;


import org.jboss.logging.Log;
import org.jboss.util.ServiceMBeanSupport;

import org.jboss.system.EJBSecurityManager;

/**
 *   This is a JMX service which manages the EJBSecurityManager.
 *	  The service creates it and binds a Reference to it into JNDI.
 *	  The EJBSecurityManager is responsible for validating credentials
 *	  associated with principals.
 *      
 *   @see EJBSecurityManager
 *   @author Daniel O'Connor docodan@nycap.rr.com
 *   @author <a href="mailto:hugo@hugopinto.com">Hugo Pinto</a>
 */
public class EJBSecurityManagerService
   extends ServiceMBeanSupport
   implements EJBSecurityManagerServiceMBean, ObjectFactory
{
   // Constants -----------------------------------------------------
   public static String JNDI_NAME = "EJBSecurityManager";
    
   // Attributes ----------------------------------------------------
    MBeanServer server;
   
   // Static --------------------------------------------------------
   static EJBSecurityManager sm;

   // ServiceMBeanSupport overrides ---------------------------------
   public String getName()
   {
      return "Security manager";
    }
   
   protected ObjectName getObjectName(MBeanServer server, ObjectName name)
      throws javax.management.MalformedObjectNameException
   {
    this.server = server;
      return new ObjectName(OBJECT_NAME);
   }
    
   protected void initService()
      throws Exception
   {
       // Create a new SM
       sm = new EJBSecurityManagerDefaultImpl();
       
       // Bind reference to SM in JNDI
       Reference ref = new Reference(sm.getClass().toString(), getClass().getName(), null);
       new InitialContext().bind(JNDI_NAME, ref);
   }
    
   protected void startService()
      throws Exception
   {
   }
   
   protected void stopService()
   {
       try
       {
         // Remove SM from JNDI
         new InitialContext().unbind(JNDI_NAME);
        } catch (CommunicationException e) {
            // Do nothing, the naming services is already stopped   
        }
        
       } catch (Exception e)
       {
         log.exception(e);
       }
   }
    
    // ObjectFactory implementation ----------------------------------
    public Object getObjectInstance(Object obj,
                                Name name,
                                Context nameCtx,
                                Hashtable environment)
                         throws Exception
    {
       // Return the security manager
       return sm;
    }
}

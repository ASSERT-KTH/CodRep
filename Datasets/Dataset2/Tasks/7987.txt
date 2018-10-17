public static String JNDI_NAME = "java:/CacheRealmMapping";

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

import javax.management.MBeanServer;
import javax.management.ObjectName;


import org.jboss.logging.Log;
import org.jboss.util.ServiceMBeanSupport;

/**
 *   This is a JMX service which manages access to security realms for a bean.
 *	  The service creates it and binds a Reference to it into JNDI.
 *      
 *   @see EJBSecurityManager
 *   @author Daniel O'Connor docodan@nycap.rr.com
 */
public class CacheRealmMappingService
   extends ServiceMBeanSupport
   implements EJBSecurityManagerServiceMBean, ObjectFactory
{
   // Constants -----------------------------------------------------
   public static String JNDI_NAME = "CacheRealmMapping";
    
   // Attributes ----------------------------------------------------
	MBeanServer server;
   
   // Static --------------------------------------------------------

   // ServiceMBeanSupport overrides ---------------------------------
   public String getName()
   {
      return "Cache Realm Mapping";
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
   }
	
   protected void startService()
      throws Exception
   {
		
	   // Bind reference to JNDI
	   Reference ref = new Reference(CacheRealmMapping.class.toString(), getClass().getName(), null);
	   new InitialContext().bind(JNDI_NAME, ref);
   }
   
   protected void stopService()
   {
		try
		{
			// Remove mapping from JNDI
			new InitialContext().unbind(JNDI_NAME);
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
		// Return the cache realm mapping manager
		return new CacheRealmMapping();
	}
}

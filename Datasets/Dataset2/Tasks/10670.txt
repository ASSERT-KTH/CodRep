import org.jboss.system.ServiceMBeanSupport;

/*
 * JBoss, the OpenSource J2EE webOS
 *
 * Distributable under LGPL license.
 * See terms of license at gnu.org.
 */
 
package org.jboss.security.plugins.samples;

import java.io.File;
import java.net.URL;
import java.rmi.server.UnicastRemoteObject;
import java.rmi.RemoteException;
import java.rmi.ServerException;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.Hashtable;

import java.security.Principal;

import javax.naming.InitialContext;
import javax.naming.Context;
import javax.naming.Reference;
import javax.naming.Name;
import javax.naming.spi.ObjectFactory;

import javax.management.MBeanServer;
import javax.management.ObjectName;

import javax.transaction.TransactionManager;

import org.jboss.logging.Log;
import org.jboss.util.ServiceMBeanSupport;

import org.jboss.security.EJBSecurityManager;

/**
 *	  The EJBSecurityManager is responsible for validating credentials
 *	  associated with principals. Right now it is a "demo" that just
 *    ensures name == credential
 *      
 *   @see EJBSecurityManager
 *   @author Daniel O'Connor docodan@nycap.rr.com
 */
public class EJBSecurityManagerDefaultImpl implements EJBSecurityManager
{
	public boolean isValid( Principal principal, Object credential )
	{
		return credential != null && principal.getName().equals( credential.toString() );
	}
}

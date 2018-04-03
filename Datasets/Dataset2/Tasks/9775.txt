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
import java.util.Set;
import java.util.LinkedList;
import java.util.Iterator;

import java.security.Principal;

import javax.naming.InitialContext;
import javax.naming.Context;
import javax.naming.Reference;
import javax.naming.Name;
import javax.naming.spi.ObjectFactory;

import javax.management.MBeanServer;
import javax.management.ObjectName;

import org.jboss.logging.Log;
import org.jboss.util.ServiceMBeanSupport;

import org.jboss.security.RealmMapping;

/**
 *  SimpleRealmMapping removes the level of indirection
 *  in the specification between roles and principals/groups
 *  for the standard "deploy without configuring"
 *      
 *   @see EJBSecurityManager
 *   @author Daniel O'Connor docodan@nycap.rr.com
 */
public class SimpleRealmMapping implements RealmMapping
{

  public Principal getPrincipal( Principal principal ) {
    return principal;
  }

  public boolean doesUserHaveRole( Principal principal, Set roleNames )
  {
    if (roleNames == null)
      return true;
    Iterator iter = roleNames.iterator();
    while (iter.hasNext())
    {
      String roleName = (String) iter.next();
      if (principal.getName().equals( roleName ))
        return true;
    }
    return false;
  }
    
}

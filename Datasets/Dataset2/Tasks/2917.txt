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
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;

import java.security.Principal;

import javax.naming.InitialContext;
import javax.naming.Context;
import javax.naming.Reference;
import javax.naming.Name;
import javax.naming.spi.ObjectFactory;
import javax.sql.DataSource;
import javax.ejb.EJBException;

import javax.management.MBeanServer;
import javax.management.ObjectName;

import org.jboss.logging.Log;
import org.jboss.util.ServiceMBeanSupport;

import org.jboss.security.RealmMapping;

/**
 *      
 *   @see EJBSecurityManager
 *   @author Daniel O'Connor docodan@nycap.rr.com
 */
public class DatabaseRealmMapping implements RealmMapping
{

  public Principal getPrincipal( Principal principal ) {
    return principal;
  }

  public boolean doesUserHaveRole( Principal principal, Set roleNames )
  {
    Connection con = null;
    if (roleNames == null)
      return false;
    try
    {
      InitialContext initial = new InitialContext();
      DataSource ds = (DataSource) initial.lookup( "java:/SecurityDS" );
      con = ds.getConnection();
      PreparedStatement statement = con.prepareStatement(
        "select rolename from sec_roles where principal=? and setname=?");
      statement.setString(1, principal.getName());
      statement.setString(2, "basic");
      ResultSet rs = statement.executeQuery();
      boolean hasRole = false;
      while (rs.next() && !hasRole)
      {
        String roleName = rs.getString(1).trim();
        if (roleNames.contains(roleName))
          hasRole = true;
      }
      rs.close();
      statement.close();
      return hasRole;
    }
    catch (Exception e)
    {
      e.printStackTrace();
      throw new EJBException( e );
    }
    finally
    {
      try
      {
        if (con != null)
          con.close();
      }
      catch (Exception e)
      {
      }
    }
  }

    
}

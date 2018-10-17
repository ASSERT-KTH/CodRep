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
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;

import java.security.Principal;

import javax.naming.InitialContext;
import javax.naming.Context;
import javax.naming.Reference;
import javax.naming.Name;
import javax.naming.spi.ObjectFactory;
import javax.ejb.EJBException;

import javax.management.MBeanServer;
import javax.management.ObjectName;

import javax.transaction.TransactionManager;
import javax.sql.DataSource;


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
public class EJBSecurityManagerDatabaseImpl implements EJBSecurityManager
{
	public boolean isValid( Principal principal, Object credential )
	{
    if (credential == null)
      return false;

    Connection con = null;
    try
    {
      InitialContext initial = new InitialContext();
      DataSource ds = (DataSource) initial.lookup( "java:/SecurityDS" );
      con = ds.getConnection();
      PreparedStatement statement = con.prepareStatement(
        "select pass from sec_access where name=?");
      statement.setString(1, principal.getName());
      ResultSet rs = statement.executeQuery();
      String dbCredential = null;
      if (rs.next())
        dbCredential = rs.getString(1);
      rs.close();
      statement.close();
      if (dbCredential == null)
        return false;
      return dbCredential.trim().equals( credential.toString().trim() );
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

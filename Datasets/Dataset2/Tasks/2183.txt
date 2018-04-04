vrol.addElement(rs.getString(1));

/*
 * The Apache Software License, Version 1.1
 *
 * Copyright (c) 1999 The Apache Software Foundation.  All rights 
 * reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer. 
 *
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in
 *    the documentation and/or other materials provided with the
 *    distribution.
 *
 * 3. The end-user documentation included with the redistribution, if
 *    any, must include the following acknowlegement:  
 *       "This product includes software developed by the 
 *        Apache Software Foundation (http://www.apache.org/)."
 *    Alternately, this acknowlegement may appear in the software itself,
 *    if and wherever such third-party acknowlegements normally appear.
 *
 * 4. The names "The Jakarta Project", "Tomcat", and "Apache Software
 *    Foundation" must not be used to endorse or promote products derived
 *    from this software without prior written permission. For written 
 *    permission, please contact apache@apache.org.
 *
 * 5. Products derived from this software may not be called "Apache"
 *    nor may "Apache" appear in their names without prior written
 *    permission of the Apache Group.
 *
 * THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESSED OR IMPLIED
 * WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
 * OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED.  IN NO EVENT SHALL THE APACHE SOFTWARE FOUNDATION OR
 * ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
 * USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
 * OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
 * OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
 * SUCH DAMAGE.
 * ====================================================================
 *
 * This software consists of voluntary contributions made by many
 * individuals on behalf of the Apache Software Foundation.  For more
 * information on the Apache Software Foundation, please see
 * <http://www.apache.org/>.
 *
 * [Additional notices, if required by prior licensing conditions]
 *
 */


package org.apache.tomcat.request;

import org.apache.tomcat.core.*;
import org.apache.tomcat.util.*;
import org.apache.tomcat.util.xml.*;


import java.beans.PropertyChangeListener;
import java.beans.PropertyChangeSupport;
import java.security.Principal;
import java.io.File;
import java.util.Enumeration;
import java.util.Hashtable;
import java.util.Vector;
import java.io.*;
import java.net.*;
import java.util.*;
import javax.servlet.http.*;

import java.sql.*;


/**
 *
 * Implmentation of <b>Realm</b> that works with any JDBC supported database.
 * See the JDBCRealm.howto for more details on how to set up the database and
 * for configuration options.
 *
 * TODO:
 *    - Work on authentication with non-plaintext passwords
 *    - Make sure no bad chars can get in and trick the auth and hasrole
 *
 * @author Craig R. McClanahan
 * @author Carson McDonald
 *
 */

public final class JDBCRealm extends BaseInterceptor {


    ContextManager cm;
    int reqRolesNote;

    // ----------------------------------------------------- Instance Variables



    /**
     * The debugging detail level for this component.
     */
    private int debug = 0;

    /**
     * The connection to the database.
     */
    private Connection dbConnection = null;

    /**
     * The connection URL to use when trying to connect to the databse
     */
    private String connectionURL = null;

    /**
     * The table that holds user data.
     */
    private String userTable = null;

    /**
     * The column in the user table that holds the user's name
     */
    private String userNameCol = null;

    /**
     * The column in the user table that holds the user's credintials
     */
    private String userCredCol = null;

    /**
     * The table that holds the relation between user's and roles
     */
    private String userRoleTable = null;

    /**
     * The column in the user role table that names a role
     */
    private String roleNameCol = null;

    /**
     * The JDBC driver to use.
     */
    private String driverName = null;

    /**
     * The string manager for this package.
     */
    private static StringManager sm = StringManager.getManager("org.apache.tomcat.request");


    /**
     * Has this component been started?
     */
    private boolean started = false;


    /**
     * The property change support for this component.
     */


    // ------------------------------------------------------------- Properties



    /**
     * Return the debugging detail level for this component.
     */
    public int getDebug() {
	    return (this.debug);
    }


    /**
     * Set the debugging detail level for this component.
     *
     * @param debug The new debugging detail level
     */
    public void setDebug(int debug) {
	this.debug = debug;
    }

    /**
     * Set the JDBC driver that will be used.
     *
     * @param driverName The driver name
     */
    public void setDriverName( String driverName ) {
      this.driverName = driverName;
    }

    /**
     * Set the URL to use to connect to the database.
     *
     * @param connectionURL The new connection URL
     */
    public void setConnectionURL( String connectionURL ) {
      this.connectionURL = connectionURL;
    }

    /**
     * Set the table that holds user data.
     *
     * @param userTable The table name
     */
    public void setUserTable( String userTable ) {
      this.userTable = userTable;
    }

    /**
     * Set the column in the user table that holds the user's name
     *
     * @param userNameCol The column name
     */
    public void setUserNameCol( String userNameCol ) {
       this.userNameCol = userNameCol;
    }

    /**
     * Set the column in the user table that holds the user's credintials
     *
     * @param userCredCol The column name
     */
    public void setUserCredCol( String userCredCol ) {
       this.userCredCol = userCredCol;
    }

    /**
     * Set the table that holds the relation between user's and roles
     *
     * @param userRoleTable The table name
     */
    public void setUserRoleTable( String userRoleTable ) {
        this.userRoleTable = userRoleTable;
    }

    /**
     * Set the column in the user role table that names a role
     *
     * @param userRoleNameCol The column name
     */
    public void setRoleNameCol( String roleNameCol ) {
        this.roleNameCol = roleNameCol;
    }

    /**
     * If there are any errors with the JDBC connection, executing
     * the query or anything we return false (don't authenticate). This
     * event is also logged.
     *
     * If there is some SQL exception the connection is set to null.
     * This will allow a retry on the next auth attempt. This might not
     * be the best thing to do but it will keep tomcat from needing a
     * restart if the database goes down.
     *
     * @param username Username of the Principal to look up
     * @param credentials Password or other credentials to use in
     *  authenticating this username
     */
    public boolean authenticate(String username, String credentials) {
        try {
          if( (dbConnection == null) || dbConnection.isClosed() ) {
            log(sm.getString("jdbcRealm.authDBClosed"));

            dbConnection = DriverManager.getConnection(connectionURL);
            if( (dbConnection == null) || dbConnection.isClosed() ) {
              log(sm.getString("jdbcRealm.authDBReOpenFail"));
              return false;
            }
          }

          Statement statement = dbConnection.createStatement();

          if( debug > 1 ) {
             log( "JDBCRealm.authenticate: SELECT " + userCredCol +
                  " FROM " + userTable +
                  " WHERE " + userNameCol + " = '" + username + "'" );
          }

          ResultSet rs = statement.executeQuery( "SELECT " + userCredCol +
               " FROM " + userTable +
               " WHERE " + userNameCol + " = '" + username + "'" );

          // If we found a user by this name check the credentials
          if( rs.next() ) {
            if( rs.getString(userCredCol).equals(credentials) ) {
               if (debug > 1)
                  log(sm.getString("jdbcRealm.authenticateSuccess", username));
                  // Good to go. Return a Principal.
                  return true;
            }
          }
        }
        catch( SQLException ex ) {
          // Set the connection to null. Next time we will try to get a new connection.
          dbConnection = null;

          if (debug > 1)
            log(sm.getString("jdbcRealm.authenticateSQLException", ex.getMessage()));
        }

        if (debug > 1)
             log(sm.getString("jdbcRealm.authenticateFailure", username));

        return false;
    }

    public String[] getUserRoles(String username) {
        try {
          if( (dbConnection == null) || dbConnection.isClosed() ) {
            log(sm.getString("jdbcRealm.getUserRolesDBClosed"));

            dbConnection = DriverManager.getConnection(connectionURL);

            if( dbConnection == null || dbConnection.isClosed() ) {
              log(sm.getString("jdbcRealm.getUserRolesDBReOpenFail"));
              return null;
            }
          }

          Statement statement = dbConnection.createStatement();

          if( debug > 1 ) {
              log( "jdbcRealm.getUserRoles: SELECT 1 FROM " + userRoleTable +
                   " WHERE " + userNameCol + " = '" + username +"'" );
          }

          ResultSet rs = statement.executeQuery( "SELECT "+roleNameCol+" FROM " + userRoleTable +
                                                 " WHERE " + userNameCol + " = '" + username +"'" );
          // Next we convert the resultset into a String[]
              Vector vrol=new Vector();
              while (rs.next()) {
                  vrol.add(rs.getString(1));
              }
              String[] res=new String[vrol.size()];
              for(int i=0 ; i<vrol.size() ; i++ )
                  res[i]=(String)vrol.elementAt(i);
              return res;
        }
        catch( SQLException ex ) {
          // Set the connection to null. Next time we will try to get a new connection.
          dbConnection = null;

          if (debug > 1)
            log(sm.getString("jdbcRealm.getUserRolesSQLException", ex.getMessage()));
        }

	      return null;
    }


    public void contextInit(Context ctx) throws org.apache.tomcat.core.TomcatException {
	// Validate and update our current component state
      if (!started) {
          started = true;
          try {
            Class.forName(driverName);
            dbConnection = DriverManager.getConnection(connectionURL);
          }
          catch( ClassNotFoundException ex ) {
            throw new RuntimeException("JDBCRealm.start.readXml: " + ex);
          }
          catch( SQLException ex ) {
            throw new RuntimeException("JDBCRealm.start.readXml: " + ex);
          }
      }
    }

    public void contextShutdown(Context ctx) throws org.apache.tomcat.core.TomcatException {
      // Validate and update our current component state
      if (started) {
            if( dbConnection != null ) {
              try {
                dbConnection.close();
              }
              catch( SQLException ex ) {
                log("dbConnection.close Exception!!!");
              }
           }
      }
    }


    void log( String s ) {
	    cm.log("JDBCRealm: " + s );
    }
    public void setContextManager( ContextManager cm ) {
      super.setContextManager( cm );

      this.cm=cm;
      // set-up a per/container note for maps
      try {
          // XXX make the name a "global" static - after everything is stable!
          reqRolesNote = cm.getNoteId( ContextManager.REQUEST_NOTE, "required.roles");
      } catch( TomcatException ex ) {
          ex.printStackTrace();
          throw new RuntimeException( "Invalid state ");
      }
    }

    public int authorize( Request req, Response response )
    {
        String roles[]=(String[]) req.getNote( reqRolesNote );

        if( roles==null ) {
            // request doesn't need authentication
            return 0;
        }

        Context ctx=req.getContext();

        // Extract the credentials
        Hashtable cred=new Hashtable();
        SecurityTools.credentials( req, cred );
        // This realm will use only username and password callbacks
        String user=(String)cred.get("username");
        String password=(String)cred.get("password");
        String userRoles[]=null;
        if( debug > 0 ) log( "Controled access for " + user + " " + req + " " + req.getContainer() );

        if( authenticate( user, password ) ) {
            req.setRemoteUser( user );
            userRoles = getUserRoles( user );
            req.setUserRoles( userRoles );
            // else - don't set it
        } else {
            // not authorized - this request needs a specific role,
            // and we can't authorize
            return HttpServletResponse.SC_UNAUTHORIZED;
        }


        if( debug > 0 ) log( "Auth ok, first role=" + userRoles[0] );

        if( SecurityTools.haveRole( userRoles, roles ))
            return 0;

        if( debug > 0 ) log( "UnAuthorized " + roles[0] );
            return HttpServletResponse.SC_UNAUTHORIZED;
        // XXX check transport
    }


    }



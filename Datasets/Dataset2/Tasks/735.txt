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
 *  CacheRealmMapping has two purposes (one of them currently unimplemented.)
 *  It allows beans to have mappings for multiple security realms, and it
 *  (eventually) will cache data from realms that allow it. 
 *      
 *   @see EJBSecurityManager
 *   @author Daniel O'Connor docodan@nycap.rr.com
 */
public class CacheRealmMapping implements RealmMapping
{
    private LinkedList realms = new LinkedList();

    public Principal getPrincipal( Principal principal ) {
        return principal;
    }

    public void addRealmMapping( RealmMapping realmMapping )
    {
        realms.add( realmMapping );
    }

    public boolean doesUserHaveRole( Principal principal, Set roleNames )
    {
        Iterator iter=realms.iterator();
        while( iter.hasNext() )
        {
            RealmMapping realmMapping = (RealmMapping) iter.next();
            if (realmMapping.doesUserHaveRole( principal, roleNames ))
                return true;
        }
        return false;
    }
    
}

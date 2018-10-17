//ic.destroySubcontext(JNDI_SM_CONTEXT_NAME); - OperationNotSupportedException

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
import java.util.Hashtable;
import java.util.ArrayList;
import java.util.Iterator;

import javax.naming.InitialContext;
import javax.naming.Context;
import javax.naming.Reference;
import javax.naming.Name;
import javax.naming.spi.ObjectFactory;
import javax.naming.CommunicationException;

import javax.management.MBeanServer;
import javax.management.ObjectName;

import javax.security.auth.login.Configuration;

import org.jboss.logging.Log;
import org.jboss.util.ServiceMBeanSupport;

import org.jboss.system.EJBSecurityManager;

/**
 *   This is a JMX service which manages the EJBSecurityManager.
 *    The service creates it and binds a Reference to it into JNDI.
 *    The EJBSecurityManager is responsible for validating credentials
 *    associated with principals.
 *      
 *   @see EJBSecurityManager
 *   @author <a href="on@ibis.odessa.ua">Oleg Nitz</a>
 */
public class JaasSecurityManagerService
        extends ServiceMBeanSupport
        implements JaasSecurityManagerServiceMBean, ObjectFactory {

    private static String JNDI_NAME = "jaas";
    
    private static String JNDI_SM_CONTEXT_NAME = "jaas.sm";

    MBeanServer server;
        
    // smJndiNames and smContext must be static: they are used by
    // ObjectFactory instances
    private static ArrayList smJndiNames = new ArrayList();

    private static Context smContext;

    public String getName() {
        return "JAAS Security Manager";
    }
   
    protected ObjectName getObjectName(MBeanServer server, ObjectName name)
            throws javax.management.MalformedObjectNameException {
        this.server = server;
        return new ObjectName(OBJECT_NAME);
    }
    
    protected void initService() throws Exception {
        InitialContext ic = new InitialContext();

        // Bind reference to SM in JNDI
        Reference ref = new Reference(JaasSecurityManager.class.getName(), getClass().getName(), null);
        ic.bind(JNDI_NAME, ref);
        if (smContext == null) {
            smContext = ic.createSubcontext(JNDI_SM_CONTEXT_NAME);
        }
    }
    
    protected void startService()
            throws Exception {
    }
   
    protected void stopService() {
        InitialContext ic;
        try {
            ic = new InitialContext();
            // Remove all SMs from JNDI
            if (smContext != null) {
                for (Iterator it = smJndiNames.iterator(); it.hasNext(); ) {
                    smContext.unbind((String) it.next());
                    it.remove();
                }
                ic.destroySubcontext(JNDI_SM_CONTEXT_NAME);
                smContext = null;
            }
            ic.unbind(JNDI_NAME);
        } catch (CommunicationException e) {
            // Do nothing, the naming services is already stopped   
        } catch (Exception e) {
            log.exception(e);
        }
    }
    
    // ObjectFactory implementation ----------------------------------
    public Object getObjectInstance(Object obj,
                                    Name name,
                                    Context nameCtx,
                                    Hashtable environment)
            throws Exception {
        String smName = name.get(name.size() - 1);

        if (!smJndiNames.contains(smName)) {
            smContext.bind(smName, new JaasSecurityManager(smName));
            smJndiNames.add(smName);
        }
        return smContext;
    }
}

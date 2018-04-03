import org.jboss.mx.util.ObjectNameFactory;

/***************************************
 *                                     *
 *  JBoss: The OpenSource J2EE WebOS   *
 *                                     *
 *  Distributable under LGPL license.  *
 *  See terms of license at gnu.org.   *
 *                                     *
 ***************************************/
package org.jboss.invocation.trunk.client;



import java.io.IOException;
import java.io.InvalidObjectException;
import java.io.ObjectStreamException;
import java.rmi.RemoteException;
import javax.management.Attribute;
import javax.management.ObjectName;
import javax.transaction.Transaction;
import org.jboss.invocation.Invocation;
import org.jboss.invocation.InvocationResponse;
import org.jboss.invocation.Invoker;
import org.jboss.invocation.ServerID;
import org.jboss.logging.Logger;
import org.jboss.system.client.ClientServiceMBeanSupport;
import org.jboss.util.jmx.ObjectNameFactory;

/**
 * This is the proxy object of the TrunkInvoker that lives on the server.
 * This object will use the ConnectionManager to create a Client to connect to the
 * server and then use that client to send Invocations to the server.
 *
 * @author <a href="mailto:hiram.chirino@jboss.org">Hiram Chirino</a>
 * @author <a href="mailto:d_jencks@users.sourceforge.net">David Jencks</a>
 *
 * @jmx.mbean extends="org.jboss.system.ServiceMBean"
 */
public final class TrunkInvokerProxy
   extends ClientServiceMBeanSupport
   implements java.io.Serializable, Invoker, TrunkInvokerProxyMBean
{
   private static final Object[] noArgs = new Object[0];
   private static final String[] noTypes = new String[0];

   //   private final static Logger log = Logger.getLogger(TrunkInvokerProxy.class);

   static final int DEFAULT_TX_TIMEOUT = 6;//seconds?

   private ServerID serverID;
   private transient AbstractClient connection;

   private ObjectName connectionManagerName;

   private transient ConnectionManager connectionManager;

   public TrunkInvokerProxy(ServerID serverID)
   {
      this.serverID = serverID;
      //This kind of sucks, name should be set on server and serialized
      serviceName = ObjectNameFactory.create("jboss.client:service=TrunkInvokerProxy," + serverID.toObjectNameClause());
   }

   // TODO Remove this!!
   protected void internalSetServiceName() throws Exception
   {
      serviceName = ObjectNameFactory.create("jboss.client:service=TrunkInvokerProxy," + getServerID().toObjectNameClause());
   }

   //Does the superclass readResolve method work for us also? NO!!
   private Object readResolve() throws ObjectStreamException
   {
      return internalReadResolve();
   }


   protected void internalSetup() throws Exception
   {
      //register ourselves
      super.internalSetup();

      String serverIdObjectNameClause = getServerID().toObjectNameClause();
      ObjectName workManagerName = ObjectNameFactory.create("jboss.client:service=TrunkInvokerWorkManager," + serverIdObjectNameClause);
      if (!getServer().isRegistered(workManagerName))
      {
         getServer().createMBean("org.jboss.resource.work.BaseWorkManager",
                            workManagerName);
      }
      getServer().setAttribute(workManagerName, new Attribute("MaxThreads", new Integer(50)));

      ObjectName trunkInvokerConnectionManagerName = ObjectNameFactory.create("jboss.client:service=TrunkInvokerConnectionManager," + serverIdObjectNameClause);
      if (!getServer().isRegistered(trunkInvokerConnectionManagerName))
      {
         getServer().createMBean(ConnectionManager.class.getName(), trunkInvokerConnectionManagerName);
      }
      getServer().setAttribute(trunkInvokerConnectionManagerName, new Attribute("WorkManagerName", workManagerName));

      setConnectionManagerName(trunkInvokerConnectionManagerName);

      //create everything
      getServer().invoke(workManagerName, "create", noArgs, noTypes);
      getServer().invoke(trunkInvokerConnectionManagerName, "create", noArgs, noTypes);
      getServer().invoke(getServiceName(), "create", noArgs, noTypes);

      //start everything
      getServer().invoke(workManagerName, "start", noArgs, noTypes);
      getServer().invoke(trunkInvokerConnectionManagerName, "start", noArgs, noTypes);
      getServer().invoke(getServiceName(), "start", noArgs, noTypes);
      log.info("Just started TrunkInvokerProxy in internalSetup");
   }

   public ServerID getServerID()
   {
      return serverID;
   }

   public org.jboss.remoting.ident.Identity getIdentity() {return null;}

   /**
    * Get this instance.
    * @return the This value.
    *
    * @jmx.managed-attribute
    */
   public TrunkInvokerProxy getTrunkInvokerProxy() {
      return this;
   }



   /**
    * Get the ConnectionManagerName value.
    * @return the ConnectionManagerName value.
    *
    * @jmx.managed-attribute
    */
   public ObjectName getConnectionManagerName() {
      return connectionManagerName;
   }

   /**
    * Set the ConnectionManagerName value.
    * @param newConnectionManagerName The new ConnectionManagerName value.
    *
    * @jmx.managed-attribute
    */
   public void setConnectionManagerName(ObjectName connectionManagerName) {
      this.connectionManagerName = connectionManagerName;
   }


   protected void startService() throws Exception
   {
      connectionManager = (ConnectionManager)getServer().getAttribute(connectionManagerName, "ConnectionManager");
   }

   protected void stopService() throws Exception
   {
      connectionManager = null;
   }


   /**
    * The <code>invoke</code> method sends the invocation over the
    * wire. The tx conversion should be in an invoker
    * interceptor/aspect.
    *
    * @param invocation an <code>Invocation</code> value
    * @return an <code>Object</code> value
    * @exception Exception if an error occurs
    */
   public InvocationResponse invoke(Invocation invocation) throws Exception
   {
      boolean trace = log.isTraceEnabled();
      if (trace) {
         log.trace("Invoking, invocation: " + invocation);
      } // end of if ()
      TrunkRequest request = new TrunkRequest();
      request.setOpInvoke(invocation);
      if (trace) {
         log.trace("No tx, request: " + request);
      }
      return (InvocationResponse)issue(request);
   }

   public Object issue(TrunkRequest request) throws Exception
   {
      checkConnection();
      TrunkResponse response;
      try
      {
         response = connection.synchRequest(request);
      }
      catch (IOException e)
      {
         throw new RemoteException("Connection to the server failed.", e);
      }
      return response.evalThrowsException();
   }

   public void sendResponse(TrunkResponse response) throws IOException
   {
      connection.sendResponse(response);
   }

   protected void checkConnection() throws RemoteException
   {
      if (connection == null || !connection.isValid())
      {
         try
         {
            connection = connectionManager.connect(serverID);
            if (log.isTraceEnabled())
               log.trace("I will use this connection for requests: " + connection);
         }
         catch (IOException e)
         {
            throw new RemoteException("Could not establish a connection to the server.", e);
         }
      }
   }

   public Integer addRequestListener(ITrunkListener rl) throws RemoteException
   {
      checkConnection();
      return connection.addRequestListener(rl);
   }

   public void removeRequestListener(Integer requestListenerID) throws RemoteException
   {
      checkConnection();
      connection.removeRequestListener(requestListenerID);
   }
}
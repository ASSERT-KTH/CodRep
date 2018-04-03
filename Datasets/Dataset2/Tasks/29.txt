Object obj = getServer().invoke(mbean, "invoke", new Object[] { invocation }, Invocation.INVOKE_SIGNATURE);

/***************************************
 *                                     *
 *  JBoss: The OpenSource J2EE WebOS   *
 *                                     *
 *  Distributable under LGPL license.  *
 *  See terms of license at gnu.org.   *
 *                                     *
 ***************************************/

package org.jboss.invocation.trunk.server;



import java.io.IOException;
import java.net.InetAddress;
import java.net.ServerSocket;
import java.rmi.MarshalledObject;
import javax.management.ObjectName;
import javax.naming.Context;
import javax.naming.InitialContext;
import javax.naming.Name;
import javax.naming.NameNotFoundException;
import javax.naming.NamingException;
import javax.resource.spi.work.WorkManager;
import javax.transaction.Transaction;
import javax.transaction.TransactionManager;
import org.jboss.invocation.Invocation;
import org.jboss.invocation.MarshalledInvocation;
import org.jboss.invocation.PayloadKey;
import org.jboss.invocation.ServerID;
import org.jboss.invocation.jrmp.interfaces.JRMPInvokerProxy;
import org.jboss.invocation.trunk.client.ICommTrunk;
import org.jboss.invocation.trunk.client.ITrunkListener;
import org.jboss.invocation.trunk.client.TrunkInvokerProxy;
import org.jboss.invocation.trunk.client.TrunkRequest;
import org.jboss.invocation.trunk.client.TrunkResponse;
import org.jboss.invocation.trunk.server.bio.BlockingServer;
import org.jboss.logging.Logger;
import org.jboss.proxy.TransactionInterceptor;
import org.jboss.system.Registry;
import org.jboss.system.ServiceMBeanSupport;
import org.jboss.tm.TransactionPropagationContextFactory;
import org.jboss.tm.TransactionPropagationContextImporter;
import org.jboss.util.naming.Util;
import org.jboss.invocation.Invoker;
import org.jboss.invocation.InvokerXAResource;

/**
 * Provides the MBean used by the JBoss JMX system to start this
 * Invoker.
 *
 * @author    <a href="mailto:hiram.chirino@jboss.org">Hiram Chirino</a>
 * @jmx:mbean extends="org.jboss.system.ServiceMBean"
 */
public final class TrunkInvoker extends ServiceMBeanSupport implements ITrunkListener, TrunkInvokerMBean
{

   /**
    * logger instance.
    */
   final static private Logger log = Logger.getLogger(TrunkInvoker.class);

   public final static String COMM_TRUNK_INVOCATION_PAYLOAD_KEY = "CommTrunk";

   /**
    * If the TcpNoDelay option should be used on the socket.
    */
   private boolean enableTcpNoDelay = false;

   /**
    * The internet address to bind to by default.
    */
   private String serverBindAddress = null;

   /**
    * The server port to bind to.
    */
   private int serverBindPort = 0;

   /**
    * The variable <code>timeoutMillis</code> is the client connect
    * timeout in milliseconds.
    *
    */
   private int timeoutMillis = 0;

   /**
    * The internet address client will use to connect to the sever.
    */
   private String clientConnectAddress = null;

   /**
    * The port a client will use to connect to the sever.
    */
   private int clientConnectPort = 0;

   /**
    * The object that will be in charge of maintaing the sockets.
    */
   private IServer serverProtocol;

   /**
    * object name of the  <code>workManager</code> thread pool used.
    *
    */
   private ObjectName workManagerName;

   private WorkManager workManager;

   /**
    * ObjectName of the <code>transactionManagerService</code> we use.
    * Probably should not be here -- used to set txInterceptor tx mananger.
    */
   private ObjectName transactionManagerService;

   /**
    * The proxy object that will sent to clients so that they 
    * know how to connect to the server.
    */
   private Invoker invoker;


   ////////////////////////////////////////////////////////////////////////
   //
   // The following methods Override the ServiceMBeanSupport base class
   //
   ////////////////////////////////////////////////////////////////////////
   /**
    * Gives this JMX service a name.
    * @return   The Name value
    */
   public String getName()
   {
      return "Trunk-Invoker";
   }

   /**
    * Starts this IL, and binds it to JNDI
    *
    * @exception Exception  Description of Exception
    */
   public void startService() throws Exception
   {



      ///////////////////////////////////////////////////////////      
      // Setup the socket level stuff
      ///////////////////////////////////////////////////////////      

      InetAddress bindAddress =
         (serverBindAddress == null || serverBindAddress.length() == 0)
            ? null
            : InetAddress.getByName(serverBindAddress);

      clientConnectAddress =
         (clientConnectAddress == null || clientConnectAddress.length() == 0)
            ? InetAddress.getLocalHost().getHostName()
            : clientConnectAddress;


      Class serverClass = BlockingServer.class;
      
      // Try to use the NonBlockingServer if possible
      if( "true".equals( System.getProperty("org.jboss.invocation.trunk.enable_nbio", "true") ) ) {
         try {
            serverClass = Class.forName("org.jboss.invocation.trunk.server.nbio.NonBlockingServer");
            log.debug("Using the Non Blocking version of the server");
         } catch ( Throwable e ) {
            if( log.isTraceEnabled() )
               log.trace("Cannot used NBIO: "+e);
            log.debug("Using the Blocking version of the server");
         }
      }
      
      serverProtocol = (IServer)serverClass.newInstance();
      WorkManager workManager = (WorkManager)getServer().getAttribute(workManagerName, "WorkManager");

      ServerSocket serverSocket = serverProtocol.bind(this, bindAddress, serverBindPort, 50, enableTcpNoDelay, workManager);
      serverProtocol.start();

      clientConnectPort = (clientConnectPort == 0) ? serverSocket.getLocalPort() : clientConnectPort;

      ServerID sa = new ServerID(clientConnectAddress, clientConnectPort, enableTcpNoDelay, timeoutMillis);
      Invoker transport = new TrunkInvokerProxy(sa);
      InvokerXAResource xares = new InvokerXAResource();
      xares.setInvoker(transport);
      invoker = xares;

      log.info("Invoker service available at: " + serverSocket.getInetAddress() + ":" + serverSocket.getLocalPort());
      log.info("Invoker clients will connect to: " + clientConnectAddress + ":" + clientConnectPort);

      ///////////////////////////////////////////////////////////      
      // Register the service with the rest of the JBoss Kernel
      ///////////////////////////////////////////////////////////      
      // Export references to the bean
      Registry.bind(getServiceName(), invoker);
      // Bind the invoker in the JNDI invoker naming space
      // It should look like so "invokers/<hostname>/trunk" 
      InitialContext ctx = new InitialContext();
      Util.rebind(ctx, "invokers/" + clientConnectAddress + "/trunk", invoker);

      log.debug("Bound invoker for JMX node");
      ctx.close();

   }

   /**
    * Stops this service, and unbinds it from JNDI.
    */
   public void stopService() throws Exception
   {

      InitialContext ctx = new InitialContext();

      try
      {
         serverProtocol.stop();
         ctx.unbind("invokers/" + clientConnectAddress + "/trunk");
      }
      finally
      {
         ctx.close();
      }
   }

   protected void destroyService() throws Exception
   {
      // Unexport references to the bean
      Registry.unbind(getServiceName());
   }

   ////////////////////////////////////////////////////////////////////////
   //
   // The following methods implement the ITrunkListener interface
   //
   ////////////////////////////////////////////////////////////////////////

   public void exceptionEvent(ICommTrunk trunk, Exception e)
   {
      log.debug(trunk.toString() + " disconnected: " + e);
   }

   public void requestEvent(ICommTrunk trunk, TrunkRequest request)
   {
      if (log.isTraceEnabled())
         log.trace("Request: " + request);
      MarshalledObject result = null;
      MarshalledObject resultException = null;

      try
      {
         // Save over which CommTrunk the request came over, in case the server wants
         // to send asynch requests back to the client via the same trunk.
         request.invocation.setValue(COMM_TRUNK_INVOCATION_PAYLOAD_KEY, trunk, PayloadKey.TRANSIENT);
         result = invoke(request.invocation);
      }
      catch (Exception e)
      {
         try
         {
            resultException = new MarshalledObject(e);
         }
         catch (IOException e2)
         {
            exceptionEvent(trunk, e2);
         }
      }

      try
      {
	 //log.info("returned from invoke, setting up response");
         TrunkResponse response = new TrunkResponse(request);
         response.result = result;
         response.exception = resultException;
	 //log.info("sending response: " + response);
         trunk.sendResponse(response);
	 //log.info("sent response");
      }
      catch (IOException e)
      {
         exceptionEvent(trunk, e);
      }
   }

   /**
    * The ServerProtocol will use this method to service an invocation 
    * request.
    */
   public MarshalledObject invoke(Invocation invocation) throws Exception
   {
      //log.info("in invoke, finally! invocation: " + invocation);
      ClassLoader oldCl = Thread.currentThread().getContextClassLoader();
      try
      {

         // This is bad it should at least be using a sub set of the Registry 
         // store a map of these names under a specific entry (lookup("ObjecNames")) and look on 
         // that subset FIXME it will speed up lookup times
	 //Prove it before you do it -- david.  Should be constant time lookup in a hashmap.
         ObjectName mbean = (ObjectName) Registry.lookup(invocation.getObjectName());

         // The cl on the thread should be set in another interceptor
         Object obj = getServer().invoke(mbean, "", new Object[] { invocation }, Invocation.INVOKE_SIGNATURE);
	 //log.info("got return object: " + obj);

         return new MarshalledObject(obj);
      }
      catch (Exception e)
      {
         org.jboss.util.jmx.JMXExceptionDecoder.rethrow(e);

         // the compiler does not know an exception is thrown by the above
         throw new org.jboss.util.UnreachableStatementException();
      }
      finally
      {
         Thread.currentThread().setContextClassLoader(oldCl);
      }
   }


   //The following are the mbean attributes for TrunkInvoker

   /**
    * Getter for property serverBindPort.
    *
    * @return Value of property serverBindPort.
    * @jmx:managed-attribute
    */
   public int getServerBindPort()
   {
      return serverBindPort;
   }

   /**
    * Setter for property serverBindPort.
    *
    * @param serverBindPort New value of property serverBindPort.
    * @jmx:managed-attribute
    */
   public void setServerBindPort(int serverBindPort)
   {
      this.serverBindPort = serverBindPort;
   }

   /**
    * @jmx:managed-attribute
    */
   public String getClientConnectAddress()
   {
      return clientConnectAddress;
   }

   /**
    * @jmx:managed-attribute
    */
   public void setClientConnectAddress(String clientConnectAddress)
   {
      this.clientConnectAddress = clientConnectAddress;
   }

   /**
    * @jmx:managed-attribute
    */
   public int getClientConnectPort()
   {
      return clientConnectPort;
   }

   /**
    * @jmx:managed-attribute
    */
   public void setClientConnectPort(int clientConnectPort)
   {
      this.clientConnectPort = clientConnectPort;
   }

   /**
    * @jmx:managed-attribute
    */
   public boolean isEnableTcpNoDelay()
   {
      return enableTcpNoDelay;
   }

   /**
    * @jmx:managed-attribute
    */
   public void setEnableTcpNoDelay(boolean enableTcpNoDelay)
   {
      this.enableTcpNoDelay = enableTcpNoDelay;
   }

   /**
    * @jmx:managed-attribute
    */
   public String getServerBindAddress()
   {
      return serverBindAddress;
   }

   /**
    * @jmx:managed-attribute
    */
   public void setServerBindAddress(String serverBindAddress)
   {
      this.serverBindAddress = serverBindAddress;
   }


   /**
    * Get the ClientConnectTimeoutMilliseconds value.
    * @return the ClientConnectTimeoutMilliseconds value.
    *
    * @jmx:managed-attribute
    */
   public int getClientConnectTimeoutMilliseconds() {
      return timeoutMillis;
   }

   /**
    * Set the ClientConnectTimeoutMilliseconds value.
    * @param newClientConnectTimeoutMilliseconds The new ClientConnectTimeoutMilliseconds value.
    *
    * @jmx:managed-attribute
    */
   public void setClientConnectTimeoutMilliseconds(int timeoutMillis) {
      this.timeoutMillis = timeoutMillis;
   }

   
   
   /**
    * mbean get-set pair for field workManager
    * Get the value of workManager
    * @return value of workManager
    *
    * @jmx:managed-attribute
    */
   public ObjectName getWorkManager()
   {
      return workManagerName;
   }
   
   
   /**
    * Set the value of workManager
    * @param workManager  Value to assign to workManager
    *
    * @jmx:managed-attribute
    */
   public void setWorkManager(final ObjectName workManagerName)
   {
      this.workManagerName = workManagerName;
   }
   
   
   
   /**
    * mbean get-set pair for field transactionManagerService
    * Get the value of transactionManagerService
    * @return value of transactionManagerService
    *
    * @jmx:managed-attribute
    */
   public ObjectName getTransactionManagerService()
   {
      return transactionManagerService;
   }
   
   
   /**
    * Set the value of transactionManagerService
    * @param transactionManagerService  Value to assign to transactionManagerService
    *
    * @jmx:managed-attribute
    */
   public void setTransactionManagerService(ObjectName transactionManagerService)
   {
      this.transactionManagerService = transactionManagerService;
   }
   
   



   /**
    * @jmx:managed-attribute
    * /
   public Invoker getInvokerProxy()
   {
      return invoker;
   }
   */
}
// vim:expandtab:tabstop=3:shiftwidth=3
import org.jboss.mx.util.ObjectNameFactory;


/*
 * JBoss, the OpenSource J2EE webOS
 *
 * Distributable under LGPL license.
 * See terms of license at gnu.org.
 *
 */

package org.jboss.invocation;


import java.io.ObjectStreamException;
import java.lang.ThreadLocal;
import java.lang.reflect.Method;
import javax.management.Attribute;
import javax.management.ObjectName;
import javax.naming.InitialContext;
import javax.resource.spi.XATerminator;
import javax.transaction.Transaction;
import javax.transaction.TransactionManager;
import javax.transaction.xa.XAException;
import javax.transaction.xa.XAResource;
import javax.transaction.xa.Xid;
import org.jboss.invocation.Invocation;
import org.jboss.invocation.Invocation;
import org.jboss.invocation.InvocationKey;
import org.jboss.invocation.Invoker;
import org.jboss.invocation.Invoker;
import org.jboss.invocation.PayloadKey;
import org.jboss.invocation.ServerID;
import org.jboss.remoting.ident.Identity;
import org.jboss.system.client.Client;
import org.jboss.system.client.ClientServiceMBeanSupport;
import org.jboss.tm.JBossXidFactory;
import org.jboss.tm.NoLogTxLogger;
import org.jboss.tm.TransactionManagerService;
import org.jboss.tm.UserTransactionImpl;
import org.jboss.tm.XAResourceFactory;
import org.jboss.tm.XATerminatorMethods;
import org.jboss.util.jmx.ObjectNameFactory;
import org.jboss.util.naming.Util;
import org.jboss.system.Registry;


/**
 * InvokerXAResource.java
 *
 * Contrary to popular opinion, this class is far easier to implement
 * if it is a interceptor attached to an invoker rather than one
 * interceptor in the client invoker chain.  There needs to be one
 * XAResource for each remote server we attach to.  This is because
 * the XAResource needs to know what server it is attached to so it
 * can answer isSameRM at any time, whether or not an invocation is
 * present.  Since each client interceptor chain can send invocations
 * to many remote servers (due to load balancing and HA), the
 * XAResource cannot be in the client interceptor chain.
 *
 * Created: Thu Oct  3 21:04:01 2002
 *
 * @author <a href="mailto:d_jencks@users.sourceforge.net">David Jencks</a>
 * @version
 *
 * @jmx.mbean extends="org.jboss.system.ServiceMBean"
 */

public class InvokerXAResource
   extends ClientServiceMBeanSupport
   implements Invoker, XAResource, XAResourceFactory, InvokerXAResourceMBean
{


   private static final ObjectName TRANSACTION_MANAGER_SERVICE = ObjectNameFactory.create("jboss.tm:service=TransactionManagerService");

   private static final ObjectName XID_FACTORY = ObjectNameFactory.create("jboss.tm:service=XidFactory");

   private static final ObjectName TX_LOGGER = ObjectNameFactory.create("jboss.tm:service=NoLogTxLogger");

   private static final ObjectName USER_TRANSACTION = ObjectNameFactory.create("jboss.tm:service=UserTransaction");

   private static final ObjectName XATERMINATOR_CONTAINER = ObjectNameFactory.create("jboss.invoker:service=XATerminatorContainer");

   private static final Object[] noArgs = new Object[0];
   private static final String[] noTypes = new String[0];


   /**
    * The variable <code>xaTerminatorNameHash</code> here.
    * @todo set xaTerminatorNameHash rather than hardcode it.
    */
   private static Integer xaTerminatorNameHash = new Integer(XATERMINATOR_CONTAINER.hashCode());

   private transient ThreadLocal xids = new ThreadLocal();

   private transient ThreadLocal invocations = new ThreadLocal();

   private int transactionTimeout = 6;//Gotta pick something for a default

   private ObjectName transactionManagerService;

   private transient TransactionManager tm;

   private ObjectName invokerName;
   /**
    * Actually this is "next"
    * The variable <code>invoker</code> tells the prepare/commit
    * etc. methods where to send their invocation.  It can't be put in
    * a threadlocal to share one InvokerXAResource among many invokers
    * because the TransactionManager needs to be able to ask if two
    * InvokerXAResources represent the same resource manager.  Without
    * this variable there is no basis for answering.
    *
    */
   private Invoker invoker;

   public InvokerXAResource()
   {
   }

   /**
    * The <code>getIdentityNameClause</code> method converts the
    * remoting identity into two name-value pairs for use in the
    * client side object name.
    *
    * @return a <code>String</code> value
    * @exception Exception if an error occurs
    */
   private String getIdentityNameClause() throws Exception
   {
      return "domain=" + getIdentity().getDomain() + ",instanceid=" + getIdentity().getInstanceId();
   }


   // TODO Remove this!!
   protected void internalSetServiceName() throws Exception
   {
      serviceName = ObjectNameFactory.create("jboss.client:service=InvokerXAResource," + getIdentityNameClause());
   }

   private Object readResolve() throws ObjectStreamException
   {
      return internalReadResolve();
   }


   /**
    * The <code>internalSetup</code> method sets up the transaction
    * manager and xid factory for this XAResource.
    *
    * @exception Exception if an error occurs
    */
   protected void internalSetup() throws Exception
   {
      //register ourselves
      if (!server.isRegistered(getServiceName()))
      {
         super.internalSetup();
      } // end of if ()
      else
      {
         log.info("Got to internal setup even though already registered");
      } // end of else


      if (xids == null)
      {
         xids = new ThreadLocal();
      } // end of if ()
      if (invocations == null)
      {
         invocations = new ThreadLocal();
      } // end of if ()

      //This part is independent of which invoker we are using...
      //Set up the client transaction manager for this vm and remote server, if there is no "real" jboss tm.
      //ObjectName tmName = TRANSACTION_MANAGER_SERVICE;
      if (!getServer().isRegistered(TRANSACTION_MANAGER_SERVICE))
      {

         //No recovery on clients by default
         if (!getServer().isRegistered(TX_LOGGER))
         {
            Client.createXMBean(NoLogTxLogger.class.getName(), TX_LOGGER, "org/jboss/tm/NoLogTxLogger.xml");
            //no attributes
         } // end of if ()

         if (!getServer().isRegistered(XID_FACTORY))
         {
            Client.createXMBean(JBossXidFactory.class.getName(), XID_FACTORY, "org/jboss/tm/JBossXidFactory.xml");
            getServer().setAttribute(XID_FACTORY, new Attribute("TxLoggerName", TX_LOGGER));
            //leave pad at default
         } // end of if ()

         Client.createXMBean(TransactionManagerService.class.getName(), TRANSACTION_MANAGER_SERVICE, "org/jboss/tm/TransactionManagerService.xml");
         getServer().setAttribute(TRANSACTION_MANAGER_SERVICE, new Attribute("TransactionLogger", TX_LOGGER));
         getServer().setAttribute(TRANSACTION_MANAGER_SERVICE, new Attribute("XidFactory", XID_FACTORY));

         if (!getServer().isRegistered(USER_TRANSACTION))
         {
            //getServer().createMBean(UserTransactionImpl.class.getName(), USER_TRANSACTION);
            Client.createXMBean(UserTransactionImpl.class.getName(), USER_TRANSACTION, "org/jboss/tm/UserTransactionImpl.xml");
            getServer().setAttribute(USER_TRANSACTION, new Attribute("TransactionManagerServiceName", TRANSACTION_MANAGER_SERVICE));
         } // end of if ()

         //create everything
         getServer().invoke(TX_LOGGER, "create", noArgs, noTypes);
         getServer().invoke(XID_FACTORY, "create", noArgs, noTypes);
         getServer().invoke(TRANSACTION_MANAGER_SERVICE, "create", noArgs, noTypes);
         getServer().invoke(USER_TRANSACTION, "create", noArgs, noTypes);

         //start everything
         getServer().invoke(TX_LOGGER, "start", noArgs, noTypes);
         getServer().invoke(XID_FACTORY, "start", noArgs, noTypes);
         getServer().invoke(TRANSACTION_MANAGER_SERVICE, "start", noArgs, noTypes);
         getServer().invoke(USER_TRANSACTION, "start", noArgs, noTypes);
      }
      getServer().setAttribute(getServiceName(), new Attribute("TransactionManagerService", TRANSACTION_MANAGER_SERVICE));
      getServer().invoke(getServiceName(), "create", noArgs, noTypes);
      getServer().invoke(getServiceName(), "start", noArgs, noTypes);
   }

   /**
    * Get the TransactionManagerService value.
    * @return the TransactionManagerService value.
    *
    * @jmx.managed-attribute
    */
   public ObjectName getTransactionManagerService() {
      return transactionManagerService;
   }



   /**
    * Set the TransactionManagerService value.
    * @param newTransactionManagerService The new TransactionManagerService value.
    * @return the TransactionManagerService value.
    *
    * @jmx.managed-attribute
    */
   public void setTransactionManagerService(ObjectName transactionManagerService) {
      this.transactionManagerService = transactionManagerService;
   }


   /**
    * Get the Invoker value.
    * @return the Invoker value.
    *
    * @jmx.managed-attribute
    */
   public ObjectName getInvokerName() {
      return invokerName;
   }

   /**
    * Set the Invoker value.
    * @param newInvoker The new Invoker value.
    *
    * @jmx.managed-attribute
    */
   public void setInvokerName(ObjectName invokerName) {
      this.invokerName = invokerName;
   }


   // Implementation of org.jboss.invocation.Invoker
   //deprecated
   public ServerID getServerID() throws Exception
   {
      return invoker.getServerID();
   }

   /**
    * The <code>getIdentity</code> method returns the remoting
    * identity of the server we are connected to, as returned by the
    * invokers further down the chain.
    *
    * @return an <code>Identity</code> value
    * @exception Exception if an error occurs
    */
   public Identity getIdentity() throws Exception
   {
      return invoker.getIdentity();
   }

   /**
    * The <code>invoke</code> method uses the transaction manager to
    * convert the current transaction (if it exists) to an xid for use
    * as the branch id on the target server transaction manager.
    *
    * @param invocation an <code>Invocation</code> value
    * @return an <code>InvocationResponse</code> value
    * @exception Throwable if an error occurs
    */
   public InvocationResponse invoke(Invocation invocation) throws Throwable
   {
      Transaction tx = invocation.getTransaction();
      if (tx == null)
      {
         return invoker.invoke(invocation);
      }
      else
      {
         invocations.set(invocation);
         tx.enlistResource(this);
         //dont' try to send the tx
         invocation.setTransaction(null);
         try
         {
            return invoker.invoke(invocation);
         }
         finally
         {
            if (log.isTraceEnabled()) {
               log.trace("Returned from invocation");
            }
            //restore the tx.
            invocation.setTransaction(tx);
            tx.delistResource(this, XAResource.TMSUSPEND);
         } // end of try-catch
      } // end of else
   }


   /**
    * The <code>startService</code> method has different functionality
    * on the originating server and on the client.  On the server, it
    * binds to the Registry and jndi tree.  Both of these should be
    * unnecessary.  On the client, it registers with the client-side
    * transaction manager.
    *
    * @exception Exception if an error occurs
    */
   protected void startService() throws Exception
   {

      if (invoker == null)
      {
         invoker = (Invoker)getManagedResource(invokerName);
      } // end of if ()
      //Determine if we are on the server or client jmx server.
      Identity serverId = getIdentity();
      Identity localId = Identity.get(getServer());
      if (localId.equals(serverId))
      {
         Registry.bind(getServiceName(), this);
         //we are on our server... bind ourselves
         String bindAddress = "invokers/" + serverId.getInstanceId() + "/remoting";

         InitialContext ctx = new InitialContext();
         Util.rebind(ctx, bindAddress, this);
      }
      else
      {
         //we are on the client, register with the transaction manager.
         try
         {
            tm = (TransactionManager)getServer().getAttribute(transactionManagerService,
                                                              "TransactionManager");
         }
         catch (Exception e)
         {
            getLog().info("Could not find transaction manager, transactions will not work.", e);
         }
         try
         {
            getServer().invoke(transactionManagerService,
                               "registerXAResourceFactory",
                               new Object[] {this},
                               new String[] {XAResourceFactory.class.getName()});
         }
         catch (Exception e)
         {
            getLog().info("Could not register with transaction manager service, recovery impossible", e);
         }

      } // end of else

   }

   /**
    * The <code>stopService</code> method on the server unregisters
    * from the Registry and jndi (both should be unnecessary).  On the
    * client, it unregisters from the client side transaction manager.
    *
    * @exception Exception if an error occurs
    */
   protected void stopService() throws Exception
   {
      Identity serverId = getIdentity();
      Identity localId = Identity.get(getServer());
      if (localId.equals(serverId))
      {
         Registry.unbind(getServiceName());

         //we are on our server... bind ourselves
         String bindAddress = "invokers/" + serverId.getInstanceId() + "/remoting";

         InitialContext ctx = new InitialContext();
         Util.unbind(ctx, bindAddress);
         invoker = null;
      }
      else
      {
         tm = null;
         try
         {
            getServer().invoke(transactionManagerService,
                               "unregisterXAResourceFactory",
                               new Object[] {this},
                               new String[] {XAResourceFactory.class.getName()});
         }
         catch (Exception e)
         {
            getLog().info("Could not unregister with transaction manager service");
         }

      } // end of else


   }

   //XAResourceFactory interface
   /**
    * The <code>getXAResource</code> method is used by the
    * TransactionManager to get a XAResource for recovery.  Here,we
    * are also abusing it by using it from the invoker to get instance
    * to call.  This should not really be a managed attribute, this
    * xaresource should be an interceptor at the invoker, so when the
    * call goes through it gets the invocation directly.
    *
    * @return a <code>XAResource</code> value
    *
    * @jmx.managed-attribute
    */
   public XAResource getXAResource()
   {
      return this;
   }

   /**
    * The <code>returnXAResource</code> method is called by the tm
    * when it is done with an XAResource after recovery is complete.
    *
    */
   public void returnXAResource()
   {
   }


   // implementation of javax.transaction.xa.XAResource interface

   /**
    *
    * @param param1 <description>
    * @param param2 <description>
    * @exception javax.transaction.xa.XAException <description>
    */
   public void start(Xid xid, int flags) throws XAException
   {
      log.info("Starting xid: " + xid);
      if (xids.get() != null)
      {
         throw new XAException("Trying to start a second tx!, old: " + xids.get() + ", new: " + xid);
      }
      xids.set(xid);
      Invocation invocation = (Invocation)invocations.get();
      invocation.setValue(InvocationKey.XID, xid, PayloadKey.PAYLOAD);
      invocation.setValue(InvocationKey.TX_TIMEOUT, new Integer(transactionTimeout), PayloadKey.AS_IS);
   }

   /**
    *
    * @param param1 <description>
    * @param param2 <description>
    * @exception javax.transaction.xa.XAException <description>
    */
   public void end(Xid xid, int flags) throws XAException
   {
      log.info("Ending xid; " + xid);
      if (xid.equals(xids.get()))
      {
         xids.set(null);
      }
      //What do we do about ending TMSUCCESS a suspended tx? Do we
      //send a end message?  It's not supported by XATerminator
      //interface, maybe it is unnecessary
   }

   /**
    *
    * @param param1 <description>
    * @return <description>
    * @exception javax.transaction.xa.XAException <description>
    */
   public int prepare(Xid xid) throws XAException
   {
      log.info("preparing xid: " + xid);
      Invocation invocation = new Invocation();
      invocation.setObjectName(xaTerminatorNameHash);
      invocation.setMethod(XATerminatorMethods.PREPARE_METHOD);
      invocation.setArguments(new Object[] {xid});
      try
      {
         InvocationResponse response = invoker.invoke(invocation);
         Integer result = (Integer)response.getResponse();
         return result.intValue();
      }
      catch (Throwable e)
      {
         if (e instanceof XAException)
         {
            throw (XAException)e;
         }
         throw new RuntimeException("Unexpected exception in prepare of xid: " + xid + ", exception: " + e);
      }
   }

   /**
    *
    * @param param1 <description>
    * @param param2 <description>
    * @exception javax.transaction.xa.XAException <description>
    */
   public void commit(Xid xid, boolean onePhase) throws XAException
   {
      log.info("Committing xid: " + xid);
      Invocation invocation = new Invocation();
      invocation.setObjectName(xaTerminatorNameHash);
      invocation.setMethod(XATerminatorMethods.COMMIT_METHOD);
      invocation.setArguments(new Object[] {xid, new Boolean(onePhase)});
      try
      {
         invoker.invoke(invocation);
      }
      catch (Throwable e)
      {
         if (e instanceof XAException)
         {
            throw (XAException)e;
         }
         getLog().info("Unexpected exception in commit of xid: " + xid, e);
         throw new RuntimeException("Unexpected exception in commit of xid: " + xid + ", exception: " + e);
      }

   }

   /**
    *
    * @param param1 <description>
    * @exception javax.transaction.xa.XAException <description>
    */
   public void rollback(Xid xid) throws XAException
   {
      log.info("Rolling back xid: " + xid);
      Invocation invocation = new Invocation();
      invocation.setObjectName(xaTerminatorNameHash);
      invocation.setMethod(XATerminatorMethods.ROLLBACK_METHOD);
      invocation.setArguments(new Object[] {xid});
      try
      {
         invoker.invoke(invocation);
      }
      catch (Throwable e)
      {
         if (e instanceof XAException)
         {
            throw (XAException)e;
         }
         throw new RuntimeException("Unexpected exception in rollback of xid: " + xid + ", exception: " + e);
      }

   }

   /**
    *
    * @param param1 <description>
    * @exception javax.transaction.xa.XAException <description>
    */
   public void forget(Xid xid) throws XAException
   {
      Invocation invocation = new Invocation();
      invocation.setObjectName(xaTerminatorNameHash);
      invocation.setMethod(XATerminatorMethods.FORGET_METHOD);
      invocation.setArguments(new Object[] {xid});
      try
      {
         invoker.invoke(invocation);
      }
      catch (Throwable e)
      {
         if (e instanceof XAException)
         {
            throw (XAException)e;
         }
         throw new RuntimeException("Unexpected exception in forget of xid: " + xid + ", exception: " + e);
      }

   }

   /**
    *
    * @param param1 <description>
    * @return <description>
    * @exception javax.transaction.xa.XAException <description>
    * @todo implement recover.
    */
   public Xid[] recover(int flag) throws XAException
   {
      Invocation invocation = new Invocation();
      invocation.setObjectName(xaTerminatorNameHash);
      invocation.setMethod(XATerminatorMethods.RECOVER_METHOD);
      invocation.setArguments(new Object[] {new Integer(flag)});
      try
      {
         InvocationResponse response = invoker.invoke(invocation);
         return (Xid[])response.getResponse();
      }
      catch (Throwable e)
      {
         if (e instanceof XAException)
         {
            throw (XAException)e;
         }
         throw new RuntimeException("Unexpected exception in recover, exception: " + e);
      }

   }

   /**
    *
    * @param param1 <description>
    * @return <description>
    * @exception javax.transaction.xa.XAException <description>
    */
   public boolean isSameRM(XAResource otherRM)
   {
      //this could be object name equality? or just ==.
      return otherRM == this;
   }

   /**
    *
    * @return <description>
    * @exception javax.transaction.xa.XAException <description>
    */
   public int getTransactionTimeout()
   {
      return transactionTimeout;
   }

   /**
    * @todo should tx timeout be in a ThreadLocal??
    *
    * @param param1 <description>
    * @return <description>
    * @exception javax.transaction.xa.XAException <description>
    */
   public boolean setTransactionTimeout(int transactionTimeout)
   {
      this.transactionTimeout = transactionTimeout;
      return true;
   }

}// ProxyXAResource
import org.jboss.mx.util.JMXExceptionDecoder;


/*
 * JBoss, the OpenSource J2EE webOS
 *
 * Distributable under LGPL license.
 * See terms of license at gnu.org.
 *
 */

package org.jboss.invocation.remoting;

import javax.management.MBeanServer;
import javax.management.ObjectName;
import javax.naming.InitialContext;
import javax.resource.spi.work.ExecutionContext;
import javax.resource.spi.work.Work;
import javax.resource.spi.work.WorkManager;
import javax.transaction.xa.Xid;
import org.jboss.invocation.Invocation;
import org.jboss.invocation.InvocationKey;
import org.jboss.invocation.Invoker;
import org.jboss.invocation.InvokerXAResource;
import org.jboss.remoting.InvocationRequest;
import org.jboss.remoting.InvokerCallbackHandler;
import org.jboss.remoting.ServerInterceptor;
import org.jboss.remoting.ServerInterceptorChain;
import org.jboss.remoting.ServerInvoker;
import org.jboss.remoting.ident.Identity;
import org.jboss.system.Registry;
import org.jboss.system.ServiceMBean;
import org.jboss.system.ServiceMBeanSupport;
import org.jboss.util.UnreachableStatementException;
import org.jboss.util.jmx.JMXExceptionDecoder;
import org.jboss.util.naming.Util;
import java.util.Map;



/**
 * EJBSubsystemInvocationHandler.java
 *
 *
 * Created: Wed Apr 23 19:19:31 2003
 *
 * @author <a href="mailto:d_jencks@users.sourceforge.net">David Jencks</a>
 * @version 1.0
 *
 * @jmx.mbean extends="org.jboss.system.ServiceMBean"
 */
public class EJBSubsystemInvocationHandler
   extends ServiceMBeanSupport
   implements ServerInterceptor, EJBSubsystemInvocationHandlerMBean
{


   public EJBSubsystemInvocationHandler()
   {

   } // EJBSubsystemInvocationHandler constructor



   /**
    * The <code>invoke</code> method translates the remoting
    * invocation into the appropraite mbean invocation.  It uses the
    * WorkManager to import the transaction context.  This should be
    * refactored so the transport endpoint uses the thread pool.
    *
    * @param invocationRequest an <code>InvocationRequest</code> value
    * @return an <code>Object</code> value
    * @exception Throwable if an error occurs
    */
   public Object invoke(ServerInterceptorChain.InterceptorIterator i, InvocationRequest invocationRequest) throws Throwable
   {
      Invocation invocation = (Invocation)invocationRequest.getParameter();
      Map requestPayload = invocationRequest.getRequestPayload();
      if (requestPayload != null)
      {
         invocation.setValue(RemotingAdapter.REMOTING_CONTEXT, requestPayload);
      } // end of if ()

      Thread currentThread = Thread.currentThread();
      ClassLoader oldCl = currentThread.getContextClassLoader();
      try
      {
         ObjectName mbean = (ObjectName) Registry.lookup(invocation.getObjectName());

         return  getServer().invoke(mbean,
                                    "invoke",
                                    new Object[] { invocation },
                                    Invocation.INVOKE_SIGNATURE);

      }
      catch (Exception e)
      {
         JMXExceptionDecoder.rethrow(e);
         throw new UnreachableStatementException();
      }
      finally
      {
         currentThread.setContextClassLoader(oldCl);
      }
   }

   /**
    * The <code>getInstance</code> method
    *
    * @return a <code>ServerInterceptor</code> value
    * @jmx.managed-attribute description="Returns this instance"
    *      access="read-only"
    */
   public ServerInterceptor getInstance()
   {
      return this;
   }


} // EJBSubsystemInvocationHandler
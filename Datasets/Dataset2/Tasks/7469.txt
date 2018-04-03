return cacheKey.getId();

/*
 * JBoss, the OpenSource EJB server
 *
 * Distributable under LGPL license.
 * See terms of license at gnu.org.
 */
package org.jboss.ejb.plugins.local;

import java.awt.Component;
import java.beans.beancontext.BeanContextChildComponentProxy;
import java.io.File;
import java.io.IOException;
import java.lang.reflect.Method;
import java.lang.reflect.Constructor;
import java.security.Principal;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Iterator;
import java.util.Map;
import java.util.HashMap;
import java.util.Properties;
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Proxy;

import javax.ejb.EJBMetaData;
import javax.ejb.EJBLocalHome;
import javax.ejb.EJBLocalObject;
import javax.ejb.AccessLocalException;
import java.rmi.AccessException;
import javax.ejb.NoSuchObjectLocalException;
import java.rmi.NoSuchObjectException;
import javax.ejb.TransactionRequiredLocalException;
import javax.transaction.TransactionRequiredException;
import javax.ejb.TransactionRolledbackLocalException;
import javax.transaction.TransactionRolledbackException;
import javax.naming.Name;
import javax.naming.InitialContext;
import javax.naming.Context;
import javax.naming.NamingException;
import javax.naming.NameNotFoundException;
import javax.transaction.Transaction;
import javax.transaction.TransactionManager;

import org.jboss.ejb.MethodInvocation;
import org.jboss.ejb.plugins.jrmp.interfaces.RemoteMethodInvocation;

import org.jboss.ejb.Container;
import org.jboss.ejb.ContainerInvokerContainer;
import org.jboss.ejb.Interceptor;
import org.jboss.ejb.LocalContainerInvoker;
import org.jboss.ejb.plugins.jrmp.interfaces.EJBMetaDataImpl;
import org.jboss.ejb.CacheKey;

import org.jboss.tm.TransactionPropagationContextFactory;

import org.jboss.security.SecurityAssociation;

import org.jboss.logging.Logger;

import org.jboss.ejb.DeploymentException;
import org.jboss.metadata.MetaData;
import org.jboss.metadata.EntityMetaData;
import org.jboss.metadata.SessionMetaData;


/**
 *      <description>
 *
 *      @author Daniel OConnor (docodan@mvcsoft.com)
 */
public class BaseLocalContainerInvoker implements LocalContainerInvoker
{
   // Attributes ----------------------------------------------------
   protected Container container;
   protected String jndiName;
   protected TransactionManager transactionManager;
   // The home can be one.
   protected EJBLocalHome home;
   // The Stateless Object can be one.
   protected EJBLocalObject statelessObject;

   protected Map beanMethodInvokerMap;
   protected Map homeMethodInvokerMap;
   
   // Static --------------------------------------------------------

   private static TransactionPropagationContextFactory tpcFactory;

   // Constructors --------------------------------------------------

   // Public --------------------------------------------------------

   
   public String getJndiName()
   {
      return jndiName;
   }

   // ContainerService implementation -------------------------------
   public void setContainer(Container con)
   {
      this.container = con;
   }

   public void init()
   throws Exception
   {
      if (((ContainerInvokerContainer)container).getLocalClass() == null)
         return;
      
      Context ctx = new InitialContext();

      jndiName = container.getBeanMetaData().getJndiName();

      // Set the transaction manager and transaction propagation
      // context factory of the GenericProxy class
      transactionManager = ((TransactionManager)ctx.lookup("java:/TransactionManager"));

      // Create method mappings for container invoker
      Method[] methods = ((ContainerInvokerContainer)container).getLocalClass().getMethods();
      beanMethodInvokerMap = new HashMap();
      for (int i = 0; i < methods.length; i++)
         beanMethodInvokerMap.put(new Long(RemoteMethodInvocation.calculateHash(methods[i])), methods[i]);
      
      methods = ((ContainerInvokerContainer)container).getLocalHomeClass().getMethods();
      homeMethodInvokerMap = new HashMap();
      for (int i = 0; i < methods.length; i++)
         homeMethodInvokerMap.put(new Long(RemoteMethodInvocation.calculateHash(methods[i])), methods[i]);
   }

   public void start()
   throws Exception
   {
      // put in the static hashmap
   }

   public void stop()
   {
      // remove from the static hashmap
   }

   public void destroy()
   {
   }
     
   
   // ContainerInvoker implementation -------------------------------
   public EJBLocalHome getEJBLocalHome()
   {
      ContainerInvokerContainer cic = (ContainerInvokerContainer) container;
      return (EJBLocalHome) Proxy.newProxyInstance( 
         cic.getLocalHomeClass().getClassLoader(),
         new Class[]{cic.getLocalHomeClass()}, new HomeProxy() );
   }

   public EJBLocalObject getStatelessSessionEJBLocalObject()
   {
      ContainerInvokerContainer cic = (ContainerInvokerContainer) container;
      return (EJBLocalObject) Proxy.newProxyInstance( 
         cic.getLocalClass().getClassLoader(),
         new Class[]{cic.getLocalClass()}, new StatelessSessionProxy() );
   }

   public EJBLocalObject getStatefulSessionEJBLocalObject(Object id)
   {
      ContainerInvokerContainer cic = (ContainerInvokerContainer) container;
      return (EJBLocalObject) Proxy.newProxyInstance( 
         cic.getLocalClass().getClassLoader(),
         new Class[]{cic.getLocalClass()}, new StatefulSessionProxy(id) );
   }

   public EJBLocalObject getEntityEJBLocalObject(Object id)
   {
      ContainerInvokerContainer cic = (ContainerInvokerContainer) container;
      return (EJBLocalObject) Proxy.newProxyInstance( 
         cic.getLocalClass().getClassLoader(),
         new Class[]{cic.getLocalClass()}, new EntityProxy(id ) );
   }

   public Collection getEntityLocalCollection(Collection ids)
   {
      ArrayList list = new ArrayList( ids.size() );
      Iterator iter = ids.iterator();
      while (iter.hasNext())
      {
         list.add( getEntityEJBLocalObject(iter.next()) );
      }
      return list;
   }

   /**
    *  Invoke a Home interface method.
    */
   public Object invokeHome(Method m, Object[] args)
   throws Exception
   {
      // Set the right context classloader
      ClassLoader oldCl = Thread.currentThread().getContextClassLoader();
      Thread.currentThread().setContextClassLoader(container.getClassLoader());

      try
      {
         return container.invokeHome(new MethodInvocation(null, m, args, 
            getTransaction(), getPrincipal(), getCredential()));
      }
      catch (AccessException ae)
      {
         throw new AccessLocalException( ae.getMessage(), ae );
      }
      catch (NoSuchObjectException nsoe)
      {
         throw new NoSuchObjectLocalException( nsoe.getMessage(), nsoe );
      }
      catch (TransactionRequiredException tre)
      {
         throw new TransactionRequiredLocalException( tre.getMessage() );
      }
      catch (TransactionRolledbackException trbe)
      {
         throw new TransactionRolledbackLocalException( trbe.getMessage(), trbe );
      }
      finally
      {
         Thread.currentThread().setContextClassLoader(oldCl);
      }
   }

   /**
    *  Return the principal to use for invocations with this proxy.
    */
   Principal getPrincipal()
   {
      return SecurityAssociation.getPrincipal();
   }

   /**
    *  Return the credentials to use for invocations with this proxy.
    */
   Object getCredential()
   {
      return SecurityAssociation.getCredential();
   }

   /**
    *  Return the transaction associated with the current thread.
    *  Returns <code>null</code> if the transaction manager was never
    *  set, or if no transaction is associated with the current thread.
    */
   Transaction getTransaction()
      throws javax.transaction.SystemException
   {
      return (transactionManager == null) ? null : transactionManager.getTransaction();
   }

   
   /**
    *  Invoke a local interface method.
    */
   public Object invoke(Object id, Method m, Object[] args )
   throws Exception
   {
      // Set the right context classloader
      ClassLoader oldCl = Thread.currentThread().getContextClassLoader();
      Thread.currentThread().setContextClassLoader(container.getClassLoader());

      try
      {
         return container.invoke(new MethodInvocation(id, m, args, getTransaction(), 
            getPrincipal(), getCredential()));
      }
      catch (AccessException ae)
      {
         throw new AccessLocalException( ae.getMessage(), ae );
      }
      catch (NoSuchObjectException nsoe)
      {
         throw new NoSuchObjectLocalException( nsoe.getMessage(), nsoe );
      }
      catch (TransactionRequiredException tre)
      {
         throw new TransactionRequiredLocalException( tre.getMessage() );
      }
      catch (TransactionRolledbackException trbe)
      {
         throw new TransactionRolledbackLocalException( trbe.getMessage(), trbe );
      }
      finally
      {
         Thread.currentThread().setContextClassLoader(oldCl);
      }
   }
   
    
   class HomeProxy extends LocalHomeProxy
      implements InvocationHandler
   {
       protected String getJndiName()
       {
           return jndiName;
       }
       
       protected Object getId()
       {
           return jndiName;
       }

       public final Object invoke(final Object proxy,
                               final Method m,
                               Object[] args)
        throws Throwable
       {
          if (args == null)
              args = EMPTY_ARGS;
          
          Object retValue = super.invoke( proxy, m, args );
          if (retValue != null)
             return retValue;
          
        else if (m.equals(REMOVE_BY_PRIMARY_KEY)) {
            // The trick is simple we trick the container in believe it
            // is a remove() on the instance
            Object id = new CacheKey(args[0]);
            return BaseLocalContainerInvoker.this.invoke(
               id, REMOVE_OBJECT, EMPTY_ARGS);
        }
          // If not taken care of, go on and call the container
          else {
              return BaseLocalContainerInvoker.this.invokeHome(
               m, args);
          }
       }
   }

   class EntityProxy extends LocalProxy 
      implements InvocationHandler
   {
      CacheKey cacheKey;
      
      EntityProxy( Object id )
      {
         if (!(id instanceof CacheKey))
            id = new CacheKey( id );
         cacheKey = (CacheKey) id;
      }
      
       protected String getJndiName()
       {
           return jndiName;
       }
       
       protected Object getId()
       {
           return cacheKey.id;
       }
      
      
      public final Object invoke(final Object proxy,
                               final Method m,
                               Object[] args)
        throws Throwable
       {
          if (args == null)
              args = EMPTY_ARGS;
          
          Object retValue = super.invoke( proxy, m, args );
          if (retValue != null)
             return retValue;
          // If not taken care of, go on and call the container
          else {
              return BaseLocalContainerInvoker.this.invoke(
               cacheKey, m, args);
          }
       }
      
    }
   
   class StatefulSessionProxy extends LocalProxy 
      implements InvocationHandler
   {
      Object id;
      
      StatefulSessionProxy( Object id )
      {
         this.id = id;
      }

       protected String getJndiName()
       {
           return jndiName;
       }
       
       protected Object getId()
       {
           return id;
       }  
      
      public final Object invoke(final Object proxy,
                               final Method m,
                               Object[] args)
        throws Throwable
       {
          if (args == null)
              args = EMPTY_ARGS;
          
          Object retValue = super.invoke( proxy, m, args );
          if (retValue != null)
             return retValue;
          // If not taken care of, go on and call the container
          else {
              return BaseLocalContainerInvoker.this.invoke(
               id, m, args);
          }
       }
   }
   
   class StatelessSessionProxy extends LocalProxy 
      implements InvocationHandler
   {
       protected String getJndiName()
       {
           return jndiName;
       }
       
       protected Object getId()
       {
           return jndiName;
       }
      
      
      public final Object invoke(final Object proxy,
                               final Method m,
                               Object[] args)
        throws Throwable
     {
        if (args == null)
           args = EMPTY_ARGS;
          
       // Implement local methods
       if (m.equals(TO_STRING)) {
               return jndiName + ":Stateless";
       }
       else if (m.equals(EQUALS)) {
               return invoke(proxy, IS_IDENTICAL, args);
       }
       else if (m.equals(HASH_CODE)) {
               // We base the stateless hash on the hash of the proxy...
               // MF XXX: it could be that we want to return the hash of the name?
               return new Integer(this.hashCode());
       }
       else if (m.equals(GET_PRIMARY_KEY)) {
               // MF FIXME 
               // The spec says that SSB PrimaryKeys should not be returned and the call should throw an exception
               // However we need to expose the field *somehow* so we can check for "isIdentical"
               // For now we use a non-spec compliant implementation and just return the key as is
               // See jboss1.0 for the PKHolder and the hack to be spec-compliant and yet solve the problem

               // This should be the following call 
               //throw new RemoteException("Session Beans do not expose their keys, RTFS");

               // This is how it can be solved with a PKHolder (extends RemoteException)
               // throw new PKHolder("RTFS", name);

               // This is non-spec compliant but will do for now
               // We can consider the name of the container to be the primary key, since all stateless beans
               // are equal within a home
               return jndiName;
       }
        else if (m.equals(GET_EJB_HOME)) {
         throw new UnsupportedOperationException();
        }
		else if (m.equals(IS_IDENTICAL)) {
			// All stateless beans are identical within a home,
			// if the names are equal we are equal
            return isIdentical(args[0], jndiName);
		}
          // If not taken care of, go on and call the container
          else {
              return BaseLocalContainerInvoker.this.invoke(
               jndiName, m, args);
          }
       }
   }

}

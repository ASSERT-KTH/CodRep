class SecurityActions

package org.jboss.ejb;

import java.security.PrivilegedAction;
import java.security.AccessController;
import javax.security.jacc.PolicyContext;

import org.jboss.security.RunAsIdentity;
import org.jboss.security.SecurityAssociation;

/** A collection of privileged actions for this package
 * 
 * @author Scott.Stark@jboss.org
 * @version $Revison:$
 */
public class SecurityActions
{
   private static class SetContextID implements PrivilegedAction
   {
      String contextID;
      SetContextID(String contextID)
      {
         this.contextID = contextID;
      }
      public Object run()
      {
         String previousID = PolicyContext.getContextID();
         PolicyContext.setContextID(contextID);
         return previousID;
      }
   }

   private static class PeekRunAsRoleAction implements PrivilegedAction
   {
      int depth;
      PeekRunAsRoleAction(int depth)
      {
         this.depth = depth;
      }
      public Object run()
      {
         RunAsIdentity principal = SecurityAssociation.peekRunAsIdentity(depth);
         return principal;
      }
   }

   static ClassLoader getContextClassLoader()
   {
      return TCLAction.UTIL.getContextClassLoader();
   }

   static ClassLoader getContextClassLoader(Thread thread)
   {
      return TCLAction.UTIL.getContextClassLoader(thread);
   }

   static void setContextClassLoader(ClassLoader loader)
   {
      TCLAction.UTIL.setContextClassLoader(loader);
   }

   static void setContextClassLoader(Thread thread, ClassLoader loader)
   {
      TCLAction.UTIL.setContextClassLoader(thread, loader);
   }

   static String setContextID(String contextID)
   {
      PrivilegedAction action = new SetContextID(contextID);
      String previousID = (String) AccessController.doPrivileged(action);
      return previousID;
   }
   static RunAsIdentity peekRunAsIdentity(int depth)
   {
      PrivilegedAction action = new PeekRunAsRoleAction(depth);
      RunAsIdentity principal = (RunAsIdentity) AccessController.doPrivileged(action);
      return principal;
   }

   interface TCLAction
   {
      class UTIL
      {
         static TCLAction getTCLAction()
         {
            return System.getSecurityManager() == null ? NON_PRIVILEGED : PRIVILEGED;
         }

         static ClassLoader getContextClassLoader()
         {
            return getTCLAction().getContextClassLoader();
         }

         static ClassLoader getContextClassLoader(Thread thread)
         {
            return getTCLAction().getContextClassLoader(thread);
         }

         static void setContextClassLoader(ClassLoader cl)
         {
            getTCLAction().setContextClassLoader(cl);
         }

         static void setContextClassLoader(Thread thread, ClassLoader cl)
         {
            getTCLAction().setContextClassLoader(thread, cl);
         }
      }

      TCLAction NON_PRIVILEGED = new TCLAction()
      {
         public ClassLoader getContextClassLoader()
         {
            return Thread.currentThread().getContextClassLoader();
         }

         public ClassLoader getContextClassLoader(Thread thread)
         {
            return thread.getContextClassLoader();
         }

         public void setContextClassLoader(ClassLoader cl)
         {
            Thread.currentThread().setContextClassLoader(cl);
         }

         public void setContextClassLoader(Thread thread, ClassLoader cl)
         {
            thread.setContextClassLoader(cl);
         }
      };

      TCLAction PRIVILEGED = new TCLAction()
      {
         private final PrivilegedAction getTCLPrivilegedAction = new PrivilegedAction()
         {
            public Object run()
            {
               return Thread.currentThread().getContextClassLoader();
            }
         };

         public ClassLoader getContextClassLoader()
         {
            return (ClassLoader)AccessController.doPrivileged(getTCLPrivilegedAction);
         }

         public ClassLoader getContextClassLoader(final Thread thread)
         {
            return (ClassLoader)AccessController.doPrivileged(new PrivilegedAction()
            {
               public Object run()
               {
                  return thread.getContextClassLoader();
               }
            });
         }

         public void setContextClassLoader(final ClassLoader cl)
         {
            AccessController.doPrivileged(
               new PrivilegedAction()
               {
                  public Object run()
                  {
                     Thread.currentThread().setContextClassLoader(cl);
                     return null;
                  }
               }
            );
         }

         public void setContextClassLoader(final Thread thread, final ClassLoader cl)
         {
            AccessController.doPrivileged(
               new PrivilegedAction()
               {
                  public Object run()
                  {
                     thread.setContextClassLoader(cl);
                     return null;
                  }
               }
            );
         }
      };

      ClassLoader getContextClassLoader();

      ClassLoader getContextClassLoader(Thread thread);

      void setContextClassLoader(ClassLoader cl);

      void setContextClassLoader(Thread thread, ClassLoader cl);
   }
}
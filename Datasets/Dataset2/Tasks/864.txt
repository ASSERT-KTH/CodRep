if( key.equalsIgnoreCase(EJB_ARGS_KEY) == true )

package org.jboss.ejb;

import javax.security.jacc.PolicyContextException;
import javax.security.jacc.PolicyContextHandler;
import javax.ejb.EnterpriseBean;

/** A PolicyContextHandler for the EJB invocation arguments.
 * @author Scott.Stark@jboss.org
 * @version $Revison:$
 */
public class EJBArgsPolicyContextHandler implements PolicyContextHandler
{
   public static final String EJB_ARGS_KEY = "javax.ejb.arguments";
   private static ThreadLocal ejbContext = new ThreadLocal();

   static void setArgs(Object[] args)
   {
      ejbContext.set(args);
   }

   /** Access the EJB policy context data.
    * @param key  "javax.ejb.arguments"
    * @param data currently unused
    * @return Object[] for the active invocation args
    * @throws javax.security.jacc.PolicyContextException
    */ 
   public Object getContext(String key, Object data)
      throws PolicyContextException
   {
      Object context = null;
      if( key.equalsIgnoreCase(EJB_ARGS_KEY) == false )
         context = ejbContext.get();
      return context;
   }

   public String[] getKeys()
      throws PolicyContextException
   {
      String[] keys = {EJB_ARGS_KEY};
      return keys;
   }

   public boolean supports(String key)
      throws PolicyContextException
   {
      return key.equalsIgnoreCase(EJB_ARGS_KEY);
   }
}
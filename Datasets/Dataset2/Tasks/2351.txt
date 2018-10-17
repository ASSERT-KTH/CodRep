if( key.equalsIgnoreCase(EJB_CONTEXT_KEY) == true )

package org.jboss.ejb.plugins;

import javax.security.jacc.PolicyContextException;
import javax.security.jacc.PolicyContextHandler;
import javax.ejb.EnterpriseBean;

/** A PolicyContextHandler for the active EnterpriseBean
 * @author Scott.Stark@jboss.org
 * @version $Revison:$
 */
public class EnterpriseBeanPolicyContextHandler implements PolicyContextHandler
{
   public static final String EJB_CONTEXT_KEY = "javax.ejb.EnterpriseBean";
   private static ThreadLocal ejbContext = new ThreadLocal();

   static void setEnterpriseBean(Object bean)
   {
      ejbContext.set(bean);
   }

   /** Access the EJB policy context data.
    * @param key - "javax.ejb.EnterpriseBean"
    * @param data currently unused
    * @return The active EnterpriseBean
    * @throws PolicyContextException
    */ 
   public Object getContext(String key, Object data)
      throws PolicyContextException
   {
      Object context = null;
      if( key.equalsIgnoreCase(EJB_CONTEXT_KEY) == false )
         context = ejbContext.get();
      return context;
   }

   public String[] getKeys()
      throws PolicyContextException
   {
      String[] keys = {EJB_CONTEXT_KEY};
      return keys;
   }

   public boolean supports(String key)
      throws PolicyContextException
   {
      return key.equalsIgnoreCase(EJB_CONTEXT_KEY);
   }
}
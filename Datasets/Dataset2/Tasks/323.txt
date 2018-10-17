if( key.equalsIgnoreCase(SEI_ARGS_KEY) == true )

package org.jboss.ejb;

import javax.security.jacc.PolicyContextException;
import javax.security.jacc.PolicyContextHandler;
import javax.xml.soap.SOAPMessage;

/** A PolicyContextHandler for EJB SEI invocation SOAPMessages
 * @author Scott.Stark@jboss.org
 * @version $Revison:$
 */
public class SOAPMsgPolicyContextHandler implements PolicyContextHandler
{
   public static final String SEI_ARGS_KEY = "javax.xml.soap.SOAPMessage";
   private static ThreadLocal ejbContext = new ThreadLocal();

   static void setMessage(SOAPMessage msg)
   {
      ejbContext.set(msg);
   }

   /** Access the EJB SEI policy context data.
    * @param key  "javax.xml.soap.SOAPMessage"
    * @param data currently unused
    * @return SOAPMessage for the active invocation
    * @throws javax.security.jacc.PolicyContextException
    */ 
   public Object getContext(String key, Object data)
      throws PolicyContextException
   {
      Object context = null;
      if( key.equalsIgnoreCase(SEI_ARGS_KEY) == false )
         context = ejbContext.get();
      return context;
   }

   public String[] getKeys()
      throws PolicyContextException
   {
      String[] keys = {SEI_ARGS_KEY};
      return keys;
   }

   public boolean supports(String key)
      throws PolicyContextException
   {
      return key.equalsIgnoreCase(SEI_ARGS_KEY);
   }

}
@version $Revision: 1.4 $

package test.jboss.naming;

import java.net.InetAddress;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.Set;
import javax.management.MBeanServer;
import javax.management.ObjectInstance;
import javax.management.ObjectName;
import javax.management.RuntimeMBeanException;
import javax.naming.Context;
import javax.naming.InitialContext;
import javax.naming.NamingEnumeration;
import javax.naming.NamingException;

import org.jboss.system.ServiceMBeanSupport;

/** A test of the ExternalContext naming mbean. To test there needs to be
one or more ExternalContex mbeans setup. An example filesystem context
setup would be:

  <mbean code="org.jboss.naming.ExternalContext" name="JBOSS-SYSTEM:service=ExternalContext,jndiName=external/fs/tmp">
    <attribute name="JndiName">external/fs/Scott</attribute>
    <attribute name="Properties">tmp.fs</attribute>
  </mbean>

where tmp.fs is a Properties file containing:
# JNDI properties for /Scott filesystem directory
java.naming.factory.initial=com.sun.jndi.fscontext.RefFSContextFactory
java.naming.provider.url=file:/tmp

@author <a href="mailto:Scott_Stark@displayscape.com">Scott Stark</a>.
@version $Revision: 1.3 $
*/
public class TestExternalContext extends ServiceMBeanSupport implements TestExternalContextMBean
{
    private ObjectName[] contextNames;

    public String getName()
    {
        return "TestExternalContext";
    }

    public void startService() throws Exception
    {
        try
        {
            contextNames = null;
            ObjectName pattern = new ObjectName("*:service=ExternalContext,*");
            MBeanServer server = super.getServer();
            Set names = server.queryMBeans(pattern, null);
            Iterator iter = names.iterator();
            ArrayList tmp = new ArrayList();
            while( iter.hasNext() )
            {
                ObjectInstance oi = (ObjectInstance) iter.next();
                ObjectName name = oi.getObjectName();
                System.out.println(name);
                tmp.add(name);
            }
            if( tmp.size() > 0 )
            {
                contextNames = new ObjectName[tmp.size()];
                tmp.toArray(contextNames);
            }
        }
        catch(Exception x)
        {
            x.printStackTrace();
            if (x instanceof RuntimeMBeanException)
            {
                ((RuntimeMBeanException)x).getTargetException().printStackTrace();
            }
        }
        testExternalContexts();
    }

    public void testExternalContexts() throws Exception
    {
        if( contextNames == null )
        {
            System.out.println("No ExternalContext names exist");
            return;
        }

        InitialContext iniCtx = new InitialContext();
        for(int n = 0; n < contextNames.length; n ++)
        {
            ObjectName name = contextNames[n];
            String jndiName = name.getKeyProperty("jndiName");
            if( jndiName == null )
            {
                System.out.println("Skipping "+name+" as it has no jndiName property");
                continue;
            }
            Context ctx = (Context) iniCtx.lookup(jndiName);
            System.out.println("+++ Listing for: "+jndiName+", "+ctx);
            list(ctx);
            ctx.close();
        }
        // Repeat the lookups to test for side-effects of closing the ctx
        for(int n = 0; n < contextNames.length; n ++)
        {
            ObjectName name = contextNames[n];
            String jndiName = name.getKeyProperty("jndiName");
            if( jndiName == null )
            {
                System.out.println("Skipping "+name+" as it has no jndiName property");
                continue;
            }
            Context ctx = (Context) iniCtx.lookup(jndiName);
            System.out.println("+++ Listing for: "+jndiName+", "+ctx);
            list(ctx);
            ctx.close();
        }
        
    }

    private void list(Context ctx) throws NamingException
    {
        NamingEnumeration enum = ctx.list("");
        while( enum.hasMore() )
            System.out.println(enum.next());
        enum.close();
    }    
}
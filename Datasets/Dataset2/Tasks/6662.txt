@version $Revision: 1.4 $

package test.jboss.naming;

/** 

@author <a href="mailto:Scott_Stark@displayscape.com">Scott Stark</a>.
@version $Revision: 1.3 $
*/
public interface TestExternalContextMBean extends org.jboss.system.ServiceMBean
{
    public void testExternalContexts() throws Exception;
}
@version $Revision: 1.8 $

/*
 * JBoss, the OpenSource J2EE webOS
 *
 * Distributable under LGPL license.
 * See terms of license at gnu.org.
 */
package org.jboss.naming;

import java.io.IOException;
import javax.naming.NamingException;

/** The ExternalContext mbean interface.

@author <a href="mailto:Scott_Stark@displayscape.com">Scott Stark</a>.
@version $Revision: 1.7 $
*/
public interface ExternalContextMBean extends org.jboss.system.ServiceMBean
{
    /** Get the jndi name under which the external context is bound.
    */
    public String getJndiName();
    /** Set the jndi name under which the external context is bound.
    */
    public void setJndiName(String jndiName) throws NamingException;
    /** Get the remote access flag. If true, the external context is bound using
        Serializable object that allows the InitialContext to be recreated
        remotely.
    */
    public boolean getRemoteAccess();
    /** Set the remote access flag. If true, the external context is bound using
        Serializable object that allows the InitialContext to be recreated
        remotely.
    */
    public void setRemoteAccess(boolean remoteAccess);

    /** Get the cacheContext flag.
    */
    public boolean getCacheContext();
    /** set the cacheContext flag. When set to true, the external Context
        is only created when the mbean is started and then stored as an in
        memory object until the mbean is stopped. If cacheContext if set to
        false, the external Context is created on each lookup using the
        mbean Properties and InitialContext class. When the uncached Context
        is looked up by a client, the client should invoke close() on the
        Context to prevent resource leaks.
    */
    public void setCacheContext(boolean flag);

    /** Get the class name of the InitialContext implementation to
	use. Should be one of:
	javax.naming.InitialContext
	javax.naming.directory.InitialDirContext
	javax.naming.ldap.InitialLdapContext
    @return the classname of the InitialContext to use 
     */
    public String getInitialContext();

    /** Set the class name of the InitialContext implementation to
	use. Should be one of:
	javax.naming.InitialContext
	javax.naming.directory.InitialDirContext
	javax.naming.ldap.InitialLdapContext
	The default is javax.naming.InitialContex.
     @param contextClass, the classname of the InitialContext to use
    */
    public void setInitialContext(String contextClass) throws ClassNotFoundException;

    /** Set the jndi.properties information for the external InitialContext.
    This is either a URL string or a classpath resource name. Examples:
        file:///config/myldap.properties
        http://config.mycompany.com/myldap.properties
        /conf/myldap.properties
        myldap.properties

    @param contextPropsURL, either a URL string to a jndi.properties type of
        content or a name of a resource to locate via the current thread
        context classpath.
    @throws IOException, thrown if the url/resource cannot be loaded.
    */
    public void setProperties(String contextPropsURL) throws IOException;
}
@version $Revision: 1.5 $

/*
 * JBoss, the OpenSource J2EE webOS
 *
 * Distributable under LGPL license.
 * See terms of license at gnu.org.
 */
package org.jboss.naming;

import javax.naming.NamingException;

/** A simple utility mbean that allows one to create an alias in
the form of a LinkRef from one JNDI name to another.

@author <a href="mailto:Scott_Stark@displayscape.com">Scott Stark</a>.
@version $Revision: 1.4 $
*/
public interface NamingAliasMBean extends org.jboss.system.ServiceMBean
{
    /** Get the from name of the alias. This is the location where the
        LinkRef is bound under JNDI.
    @return the location of the LinkRef
    */
    public String getFromName();
    /** Set the from name of the alias. This is the location where the
        LinkRef is bound under JNDI.
    @param name, the location where the LinkRef will be bound
    */
    public void setFromName(String name) throws NamingException;
    /** Get the to name of the alias. This is the target name to
        which the LinkRef refers. The name is a URL, or a name to be resolved
        relative to the initial context, or if the first character of the name
        is ".", the name is relative to the context in which the link is bound.
    @return the target JNDI name of the alias.
    */
    public String getToName();
    /** Set the to name of the alias. This is the target name to
        which the LinkRef refers. The name is a URL, or a name to be resolved
        relative to the initial context, or if the first character of the name
        is ".", the name is relative to the context in which the link is bound.
    @param name, the target JNDI name of the alias.
    */
    public void setToName(String name) throws NamingException;
}
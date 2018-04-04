@version $Revision: 1.3 $

/*
 * JBoss, the OpenSource EJB server
 *
 * Distributable under LGPL license.
 * See terms of license at gnu.org.
 */
 
package org.jboss.security;

import javax.security.auth.Subject;


/** An extension of the EJBSecurityManager that adds the notion of the active
Subject and security domain.

@author Scott_Stark@displayscape.com
@version $Revision: 1.2 $
*/
public interface SubjectSecurityManager extends EJBSecurityManager
{
    /** Get the security domain from which the security manager is from. Every
        security manager belongs to a named domain. The meaning of the security
        domain name depends on the implementation. Examples range from as fine
        grained as the name of EJBs to J2EE application names to DNS domain names.
    @return the security domain name. May be null in which case the security
        manager belongs to the logical default domain.
    */
    public String getSecurityDomain();
    /** Get the currently authenticated subject. After a successful isValid()
        call, a SubjectSecurityManager has a Subject associated with the current
        thread. This Subject will typically contain the Principal passed to isValid
        as well as any number of additional Principals, and credentials.
    @see EJBSecurityManager#isValid(Principal, Object)
    @return The previously authenticated Subject if isValid succeeded, null if
        isValid failed or has not been called for the active thread.
    */
    public Subject getActiveSubject();
}
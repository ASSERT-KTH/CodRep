@version $Revision: 1.9 $

/*
 * JBoss, the OpenSource J2EE WebOS
 *
 * Distributable under LGPL license.
 * See terms of license at gnu.org.
 */

package org.jboss.web;

import java.util.Iterator;

import org.w3c.dom.Element;

import org.jboss.deployment.SubDeployerMBean;
import org.jboss.deployment.DeploymentException;

/** A template pattern for web container integration into JBoss.

@author  Scott.Stark@jboss.org
@version $Revision: 1.8 $
*/
public interface AbstractWebContainerMBean 
   extends SubDeployerMBean
{
    public boolean isDeployed(String warUrl);
   /** Returns the applications deployed by the container factory
    @return An Iterator of WebApplication objects for the deployed wars.
    */
   public Iterator getDeployedApplications();
    /** An accessor for any configuration element set via setConfig. This
     method always returns null and must be overriden by subclasses to
     return a valid value.
     */
    public Element getConfig();
    /** This method is invoked to import an arbitrary XML configuration tree.
     Subclasses should override this method if they support such a configuration
     capability. This implementation does nothing.
     */
   public void setConfig(Element config);
}
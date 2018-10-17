import org.jboss.deployment.DeploymentException;

/*
 * JBoss, the OpenSource J2EE webOS
 *
 * Distributable under LGPL license.
 * See terms of license at gnu.org.
 */
package org.jboss.metadata;

import org.w3c.dom.Element;

import org.jboss.ejb.DeploymentException;

/**
 *   <description> 
 *      
 *   @see <related>
 *   @author <a href="mailto:docodan@mvcsoft.com">Daniel OConnor</a>
 */
public class EjbLocalRefMetaData extends MetaData {
    // Constants -----------------------------------------------------
    
    // Attributes ----------------------------------------------------
	
   // the name used in the bean code
   private String name;
	
   // entity or session
   private String type;
	
	// the 2 interfaces
   private String localHome;
   private String local;
	
	// internal link: map name to link
   private String link;
	

    // Static --------------------------------------------------------
    
    // Constructors --------------------------------------------------
	
    // Public --------------------------------------------------------
	
   public String getName() { return name; }
	
   public String getType() { return type; }
	
   public String getLocalHome() { return localHome; }
	
   public String getLocal() { return local; }
	
   public String getLink() { return link; }

    public void importEjbJarXml(Element element) throws DeploymentException {
      name = getElementContent(getUniqueChild(element, "ejb-ref-name"));
      type = getElementContent(getUniqueChild(element, "ejb-ref-type"));
      localHome = getElementContent(getUniqueChild(element, "local-home"));
      local = getElementContent(getUniqueChild(element, "local"));
      link = getElementContent(getOptionalChild(element, "ejb-link"));
   }		
    
}
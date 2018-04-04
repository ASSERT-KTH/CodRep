extends ContainerPlugin

/*
 * JBoss, the OpenSource EJB server
 *
 * Distributable under LGPL license.
 * See terms of license at gnu.org.
 */
package org.jboss.ejb;

import java.util.Collection;

import javax.ejb.EJBLocalHome;
import javax.ejb.EJBLocalObject;

/**
 *	This is an extension to the ContainerInvoker interface. Although some
 *      implementations of the ContainerInvoker interface may provide access
 *      to local interfaces, others (e.g. which provide remote distribution)
 *      will not. Good example: the JRMP delegates do not need to implement
 *      this interface.
 *
 *	@see ContainerInvoker
 *	@author Daniel OConnor (docodan@mvcsoft.com)
 */
public interface LocalContainerInvoker
   extends ContainerInvoker
{
   // Public --------------------------------------------------------

	/**
	 *	This method is called whenever the EJBLocalHome implementation for this
	 *	container is needed.
	 *
	 * @return     an implementation of the local home interface for this container
	 */
   public EJBLocalHome getEJBLocalHome();

        /**
	 *	This method is called whenever an EJBLocalObject implementation for a stateless
	 *	session bean is needed.
	 *
	 * @return     an implementation of the local interface for this container
	 */
   public EJBLocalObject getStatelessSessionEJBLocalObject();

	/**
	 *	This method is called whenever an EJBLocalObject implementation for a stateful
	 *	session bean is needed.
	 *
	 * @param   id  the id of the session
	 * @return     an implementation of the local interface for this container
	 */
   public EJBLocalObject getStatefulSessionEJBLocalObject(Object id);
      
	/**
	 *	This method is called whenever an EJBLocalObject implementation for an entitybean
	 * is needed.
	 *
	 * @param   id  the primary key of the entity
	 * @return     an implementation of the local interface for this container
	 */
   public EJBLocalObject getEntityEJBLocalObject(Object id);
	/**
	 *	This method is called whenever a collection of EJBLocalObjects for a collection of primary keys
	 * is needed.
	 *
	 * @param   enum  enumeration of primary keys
	 * @return     a collection of EJBLocalObjects implementing the remote interface for this container
	 */
   public Collection getEntityLocalCollection(Collection enum);
   
}




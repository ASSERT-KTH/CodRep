import org.jboss.system.ServiceMBeanSupport;

/*
 * JBoss, the OpenSource J2EE webOS
 *
 * Distributable under LGPL license.
 * See terms of license at gnu.org.
 */

package org.jboss.jmx.server;

import java.io.ObjectInputStream;
import java.rmi.server.UnicastRemoteObject;
import java.rmi.RemoteException;
import java.rmi.ServerException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Hashtable;
import java.util.Iterator;
import java.util.Set;
import java.util.Vector;

import javax.management.Attribute;
import javax.management.AttributeList;
import javax.management.ObjectName;
import javax.management.QueryExp;
import javax.management.ObjectInstance;
import javax.management.Notification;
import javax.management.NotificationFilter;
import javax.management.NotificationListener;
import javax.management.MBeanServer;
import javax.management.MBeanInfo;

import javax.management.AttributeNotFoundException;
import javax.management.InstanceAlreadyExistsException;
import javax.management.InstanceNotFoundException;
import javax.management.IntrospectionException;
import javax.management.InvalidAttributeValueException;
import javax.management.ListenerNotFoundException;
import javax.management.MBeanException;
import javax.management.MBeanRegistrationException;
import javax.management.NotCompliantMBeanException;
import javax.management.OperationsException;
import javax.management.ReflectionException;

import javax.naming.InitialContext;

import org.jboss.logging.Log;
import org.jboss.util.ServiceMBeanSupport;

import org.jboss.jmx.interfaces.RMIConnector;
import org.jboss.jmx.interfaces.RMINotificationListener;

/**
* RMI Interface for the server side Connector which
* is nearly the same as the MBeanServer Interface but
* has an additional RemoteException.
* <BR>
* AS 8/18/00
* <BR>
* Add the ObjectHandler to enable this server-side implementation to instantiate
* objects locally but enable the client to use them as parameter from the
* client side transparently (except that the user cannot invoke a method on this
* instance).
*
* @author <a href="mailto:rickard.oberg@telkel.com">Rickard Öberg</a>
* @author <A href="mailto:andreas.schaefer@madplanet.com">Andreas &quot;Mad&quot; Schaefer</A>
**/
public class RMIConnectorImpl
	extends UnicastRemoteObject
	implements RMIConnector
{

	// Constants -----------------------------------------------------
	
	// Attributes ----------------------------------------------------
	/**
	* Reference to the MBeanServer all the methods of this Connector are
	* forwarded to
	**/
	private MBeanServer					mServer;
	/** Pool of object referenced by an object handler **/
	private Hashtable					mObjectPool = new Hashtable();
	/** Pool of registered listeners **/
	private Vector						mListeners = new Vector();
	
	// Static --------------------------------------------------------
	
	// Public --------------------------------------------------------

	// Constructors --------------------------------------------------
	public RMIConnectorImpl(
		MBeanServer pServer
	) throws RemoteException {
		super();
		mServer = pServer;
	}
	
	// RMIConnector implementation -------------------------------------

	public Object instantiate(
		String pClassName
	) throws
		ReflectionException,
		MBeanException,
		RemoteException
	{
		return assignObjectHandler(
			mServer.instantiate( pClassName )
		);
	}
		

	public Object instantiate(
		String pClassName,
		ObjectName pLoaderName
	) throws
		ReflectionException,
		MBeanException,
		InstanceNotFoundException,
		RemoteException
	{
		return assignObjectHandler(
			mServer.instantiate( pClassName, pLoaderName )
		);
	}

	public Object instantiate(
		String pClassName,
		Object[] pParams,
		String[] pSignature
	) throws
		ReflectionException,
		MBeanException,
		RemoteException
	{
		// First check the given parameters to see if there is an ObjectHandler
		// to be replaced
		checkForObjectHandlers(
			pParams,
			pSignature
		);
		return assignObjectHandler(
			mServer.instantiate(
				pClassName,
				pParams, 
				pSignature 
			)
		);
	}

	public Object instantiate(
		String pClassName,
		ObjectName pLoaderName,
		Object[] pParams,
		String[] pSignature
	) throws
		ReflectionException,
		MBeanException,
		InstanceNotFoundException,
		RemoteException
	{
		// First check the given parameters to see if there is an ObjectHandler
		// to be replaced
		checkForObjectHandlers(
			pParams,
			pSignature
		);
		return assignObjectHandler(
			mServer.instantiate( 
				pClassName, 
				pLoaderName, 
				pParams, 
				pSignature 
			)
		);
	}

	public ObjectInstance createMBean(
		String pClassName,
		ObjectName pName
	) throws
		ReflectionException,
		InstanceAlreadyExistsException,
		MBeanRegistrationException,
		MBeanException,
		NotCompliantMBeanException,
		RemoteException
	{
		return mServer.createMBean( pClassName, pName );
	}

	public ObjectInstance createMBean(
		String pClassName,
		ObjectName pName,
		ObjectName pLoaderName
	) throws
		ReflectionException,
		InstanceAlreadyExistsException,
		MBeanRegistrationException,
		MBeanException,
		NotCompliantMBeanException,
		InstanceNotFoundException,
		RemoteException
	{
		return mServer.createMBean( pClassName, pName, pLoaderName );
	}

	public ObjectInstance createMBean(
		String pClassName,
		ObjectName pName,
		Object[] pParams,
		String[] pSignature
	) throws
		ReflectionException,
		InstanceAlreadyExistsException,
		MBeanRegistrationException,
		MBeanException,
		NotCompliantMBeanException,
		RemoteException
	{
		// First check the given parameters to see if there is an ObjectHandler
		// to be replaced
		checkForObjectHandlers(
			pParams,
			pSignature
		);
		return mServer.createMBean( pClassName, pName, pParams, pSignature );
	}

	public ObjectInstance createMBean(
		String pClassName,
		ObjectName pName,
		ObjectName pLoaderName,
		Object[] pParams,
		String[] pSignature
	) throws
		ReflectionException,
		InstanceAlreadyExistsException,
		MBeanRegistrationException,
		MBeanException,
		NotCompliantMBeanException,
		InstanceNotFoundException,
		RemoteException
	{
		// First check the given parameters to see if there is an ObjectHandler
		// to be replaced
		checkForObjectHandlers(
			pParams,
			pSignature
		);
		return mServer.createMBean( pClassName, pName, pLoaderName, pParams, pSignature );
	}

	public ObjectInstance registerMBean(
		Object pObjectHandler,
		ObjectName pNameToAssign
	) throws
		InstanceAlreadyExistsException,
		MBeanRegistrationException,
		NotCompliantMBeanException,
		RemoteException
	{
		if( !( pObjectHandler instanceof ObjectHandler ) ) {
			throw new IllegalArgumentException(
				"You can only register local objects referenced by ObjectHandler"
			);
		}
		return mServer.registerMBean(
			checkForObjectHandler( pObjectHandler ),
			pNameToAssign
		);
	}

	public void unregisterMBean(
		ObjectName pName
	) throws
		InstanceNotFoundException,
		MBeanRegistrationException,
		RemoteException
	{
		mServer.unregisterMBean( pName );
	}

	public ObjectInstance getObjectInstance(
		ObjectName pName
	) throws
		InstanceNotFoundException,
		RemoteException
	{
		return mServer.getObjectInstance( pName );
	}

	public Set queryMBeans(
		ObjectName pName,
		QueryExp pQuery
	) throws
		RemoteException
	{
		return mServer.queryMBeans( pName, pQuery );
	}

	public Set queryNames(
		ObjectName pName,
		QueryExp pQuery
	) throws
		RemoteException
	{
		return mServer.queryNames( pName, pQuery );
	}

	public boolean isRegistered(
		ObjectName pName
	) throws
		RemoteException
	{
		return mServer.isRegistered( pName );
	}

	public boolean isInstanceOf(
		ObjectName pName,
		String pClassName
	) throws
		InstanceNotFoundException,
		RemoteException
	{
		return mServer.isInstanceOf( pName, pClassName );
	}

	public Integer getMBeanCount(
	) throws
		RemoteException
	{
		return mServer.getMBeanCount();
	}

	public Object getAttribute(
		ObjectName pName,
		String pAttribute
	) throws
		MBeanException,
		AttributeNotFoundException,
		InstanceNotFoundException,
		ReflectionException,
		RemoteException
	{
		return mServer.getAttribute( pName, pAttribute );
	}

	public AttributeList getAttributes(
		ObjectName pName,
		String[] pAttributes
	) throws
		InstanceNotFoundException,
		ReflectionException,
		RemoteException
	{
		return mServer.getAttributes( pName, pAttributes );
	}

	public void setAttribute(
		ObjectName pName,
		Attribute pAttribute
	) throws
		InstanceNotFoundException,
		AttributeNotFoundException,
		InvalidAttributeValueException,
		MBeanException,
		ReflectionException,
		RemoteException
	{
		mServer.setAttribute( pName, pAttribute );
	}

	public AttributeList setAttributes(
		ObjectName pName,
		AttributeList pAttributes
	) throws
		InstanceNotFoundException,
		ReflectionException,
		RemoteException
	{
		return mServer.setAttributes( pName, pAttributes );
	}

	public Object invoke(
		ObjectName pName,
		String pActionName,
		Object[] pParams,
		String[] pSignature
	) throws
		InstanceNotFoundException,
		MBeanException,
		ReflectionException,
		RemoteException
	{
		// First check the given parameters to see if there is an ObjectHandler
		// to be replaced
		checkForObjectHandlers(
			pParams,
			pSignature
		);
		return mServer.invoke( pName, pActionName, pParams, pSignature );
	}

	public String getDefaultDomain(
	) throws
		RemoteException
	{
		return mServer.getDefaultDomain();
	}

	/**
	* Adds a given remote notification listeners to the given
	* Broadcaster.
	* Please note that this is not the same as within the
	* MBeanServer because it is protocol specific.
	*/
	public void addNotificationListener(
		ObjectName pName,
		RMINotificationListener pListener,
		NotificationFilter pFilter,
		Object pHandback		
	) throws
		InstanceNotFoundException,
		RemoteException
	{
		NotificationListener lRemoteListener = new Listener( pListener );
		mServer.addNotificationListener(
			pName,
			lRemoteListener,
			pFilter,
			pHandback
		);
		mListeners.addElement( lRemoteListener );
	}

	public void removeNotificationListener(
		ObjectName pName,
		RMINotificationListener pListener
	) throws
		InstanceNotFoundException,
		ListenerNotFoundException,
		RemoteException
	{
		int lIndex = mListeners.indexOf(
			new Listener(
				pListener
			)
		);
		if( lIndex >= 0 ) {
			mServer.removeNotificationListener(
				pName,
				(Listener) mListeners.elementAt( lIndex )
			);
		}
	}

	public MBeanInfo getMBeanInfo(
		ObjectName pName
	) throws
		InstanceNotFoundException,
		IntrospectionException,
		ReflectionException,
		RemoteException
	{
		return mServer.getMBeanInfo( pName );
	}

	/**
	* Checks in the given list of object if there is one of type ObjectHandler
	* and if it will replaced by the referenced object. In addition it checks
	* if the given signature is of type ObjectHandler and if then it replace
	* it by the type of the referenced object.
	* <BR>
	* Please note that this method works directly on the given arrays!
	*
	* @param pListOfObjects					Array of object to be checked
	* @param pSignature						Array of class names (full paht)
	*										beeing the signature for the object
	*										on the according object (list above)
	*/
	private void checkForObjectHandlers(
		Object[] pListOfObjects,
		String[] pSignature
	) {
		for( int i = 0; i < pListOfObjects.length; i++ ) {
			Object lEffective = checkForObjectHandler( pListOfObjects[ i ] );
			if( pListOfObjects[ i ] != lEffective ) {
				// Replace the Object Handler by the effective object
				pListOfObjects[ i ] = lEffective;
				if( i < pSignature.length ) {
					if( pSignature[ i ].equals( ObjectHandler.class.getName() ) ) {
						pSignature[ i ] = lEffective.getClass().getName();
					}
				}
			}
		}
	}
	/**
	* Checks if the given object is of type ObjectHandler and if then
	* it replaces by the object referenced by the ObjectHandler
	*
	* @param pObjectToCheck					Object to be checked
	*
	* @return								The given object if not a reference or
	*										or the referenced object
	*/
	private Object checkForObjectHandler( Object pObjectToCheck ) {
		if( pObjectToCheck instanceof ObjectHandler ) {
			return mObjectPool.get(
				pObjectToCheck
			);
		}
		else {
			return pObjectToCheck;
		}
	}
	
	/**
	* Creates an ObjectHandler for the given object and store it on
	* this side
	*
	* @param pNewObject						New object to be referenced by an
	*										ObjectHandler
	*
	* @return								Object Handler which stands for a
	*										remote reference to an object created
	*										and only usable on this side
	*/
	private ObjectHandler assignObjectHandler( Object pNewObject ) {
		ObjectHandler lObjectHandler = new ObjectHandler(
			this.toString()
		);
		mObjectPool.put(
			lObjectHandler,
			pNewObject
		);
		return lObjectHandler;
	}
		
	/**
	* Listener wrapper around the remote RMI Notification Listener
	*/
	private class Listener implements NotificationListener {
		
		private RMINotificationListener		mRemoteListener;
		
		public Listener( RMINotificationListener pRemoteListener ) {
			mRemoteListener = pRemoteListener;
		}

		/**
		* Handles the given notification by sending this to the remote
		* client listener
		*
		* @param pNotification				Notification to be send
		* @param pHandback					Handback object
		*/
		public void handleNotification(
			Notification pNotification,
			Object pHandback
		) {
			try {
				mRemoteListener.handleNotification( pNotification, pHandback );
			}
			catch( RemoteException re ) {
				re.printStackTrace();
			}
		}
		/**
		* Test if this and the given Object are equal. This is true if the given
		* object both refer to the same local listener
		*
		* @param pTest						Other object to test if equal
		*
		* @return							True if both are of same type and
		*									refer to the same local listener
		**/
		public boolean equals( Object pTest ) {
			if( pTest instanceof Listener ) {
				return mRemoteListener.equals(
					( (Listener) pTest).mRemoteListener
				);
			}
			return false;
		}
		/**
		* @return							Hashcode of the remote listener
		**/
		public int hashCode() {
			return mRemoteListener.hashCode();
		}
	}
}

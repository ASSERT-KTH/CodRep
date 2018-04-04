import org.jboss.system.ServiceMBeanSupport;

/*
 * JBoss, the OpenSource J2EE webOS
 *
 * Distributable under LGPL license.
 * See terms of license at gnu.org.
 */
 
package org.jboss.jmx.client;

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

import org.jboss.jmx.interfaces.JMXConnectorMBean;
import org.jboss.jmx.interfaces.RMIConnector;
import org.jboss.jmx.interfaces.RMINotificationListener;
import org.jboss.jmx.server.ObjectHandler;

/**
* Implementation of the JMX Connector over the RMI protocol 
*      
* @author <a href="mailto:rickard.oberg@telkel.com">Rickard Öberg</a>
* @author <A href="mailto:andreas.schaefer@madplanet.com">Andreas &quot;Mad&quot; Schaefer</A>
*/
public class RMIClientConnectorImpl
	implements JMXConnectorMBean, RMIClientConnectorImplMBean
{
	// Constants -----------------------------------------------------
	
	// Attributes ----------------------------------------------------
	private RMIConnector		mRemoteConnector;
	private Object				mServer = "";
	private Hashtable			mHandbackPool = new Hashtable();
	private Vector				mListeners = new Vector();
	
	// Static --------------------------------------------------------
	
	// Constructors --------------------------------------------------
	public RMIClientConnectorImpl(
		String pServerName
	) {
		super();
		start( pServerName );
	}
	
	// JMXClientConnector implementation -------------------------------
	public void start(
		Object pServer
	) throws IllegalArgumentException {
		if( pServer == null ) {
			throw new IllegalArgumentException( "Server cannot be null. "
				+ "To close the connection use stop()" );
		}
		try {
			InitialContext lNamingContext = new InitialContext();
			System.out.println( "RMIClientConnectorImp.start(), got Naming Context: " +	lNamingContext +
				", environment: " + lNamingContext.getEnvironment() +
				", name in namespace: " + lNamingContext.getNameInNamespace()
			);
			// This has to be adjusted later on to reflect the given parameter
			mRemoteConnector = (RMIConnector) new InitialContext().lookup( "jmx:" + pServer + ":rmi" );
			System.err.println( "RMIClientConnectorImpl.start(), got remote connector: " + mRemoteConnector );
			mServer = pServer;
		}
		catch( Exception e ) {
			e.printStackTrace();
		}
	}

	public void stop() {
		System.out.println( "RMIClientConnectorImpl.stop(), start" );
		// First go through all the reistered listeners and remove them
		Iterator i = mListeners.iterator();
		while( i.hasNext() ) {
			try {
				Listener lRemoteListener = (Listener) i.next();
				System.out.println( "RMIClientConnectorImpl.stop(), remove listener: " +
					lRemoteListener
				);
				try {
					mRemoteConnector.removeNotificationListener(
						lRemoteListener.getObjectName(),
						lRemoteListener
					);
				}
				catch( RemoteException re ) {
					re.printStackTrace();
				}
				finally {
					i.remove();
				}
			}
			catch( Exception e ) {
				e.printStackTrace();
			}
		}
		mRemoteConnector = null;
		mServer = "";
	}
	
	public boolean isAlive() {
		return mRemoteConnector != null;
	}

	public String getServerDescription() {
		return "" + mServer;
	}

	// JMXConnector implementation -------------------------------------
	public Object instantiate(
		String pClassName
	) throws
		ReflectionException,
		MBeanException
	{
		try {
			return mRemoteConnector.instantiate( pClassName );
		}
		catch( RemoteException re ) {
			//AS Not a good style but for now
			return null;
		}
	}
		

	public Object instantiate(
		String pClassName,
		ObjectName pLoaderName
	) throws
		ReflectionException,
		MBeanException,
		InstanceNotFoundException
	{
		try {
			return mRemoteConnector.instantiate( pClassName, pLoaderName );
		}
		catch( RemoteException re ) {
			//AS Not a good style but for now
			return null;
		}
	}

	public Object instantiate(
		String pClassName,
		Object[] pParams,
		String[] pSignature
	) throws
		ReflectionException,
		MBeanException
	{
		try {
			return mRemoteConnector.instantiate( pClassName, pParams, pSignature );
		}
		catch( RemoteException re ) {
			//AS Not a good style but for now
			return null;
		}
	}

	public Object instantiate(
		String pClassName,
		ObjectName pLoaderName,
		Object[] pParams,
		String[] pSignature
	) throws
		ReflectionException,
		MBeanException,
		InstanceNotFoundException
	{
		try {
			return mRemoteConnector.instantiate( pClassName, pLoaderName, pParams, pSignature );
		}
		catch( RemoteException re ) {
			//AS Not a good style but for now
			return null;
		}
	}

	public ObjectInstance createMBean(
		String pClassName,
		ObjectName pName
	) throws
		ReflectionException,
		InstanceAlreadyExistsException,
		MBeanRegistrationException,
		MBeanException,
		NotCompliantMBeanException
	{
		try {
			return mRemoteConnector.createMBean( pClassName, pName );
		}
		catch( RemoteException re ) {
			//AS Not a good style but for now
			return null;
		}
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
		InstanceNotFoundException
	{
		try {
			return mRemoteConnector.createMBean( pClassName, pName, pLoaderName );
		}
		catch( RemoteException re ) {
			//AS Not a good style but for now
			return null;
		}
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
		NotCompliantMBeanException
	{
		try {
			return mRemoteConnector.createMBean( pClassName, pName, pParams, pSignature );
		}
		catch( RemoteException re ) {
			//AS Not a good style but for now
			return null;
		}
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
		InstanceNotFoundException
	{
		try {
			return mRemoteConnector.createMBean( pClassName, pName, pLoaderName, pParams, pSignature );
		}
		catch( RemoteException re ) {
			//AS Not a good style but for now
			return null;
		}
	}

	public ObjectInstance registerMBean(
		Object pObject,
		ObjectName pName
	) throws
		InstanceAlreadyExistsException,
		MBeanRegistrationException,
		NotCompliantMBeanException
	{
		try {
			return mRemoteConnector.registerMBean( pObject, pName );
		}
		catch( RemoteException re ) {
			//AS Not a good style but for now
			return null;
		}
	}

	public void unregisterMBean(
		ObjectName pName
	) throws
		InstanceNotFoundException,
		MBeanRegistrationException
	{
		try {
			mRemoteConnector.unregisterMBean( pName );
		}
		catch( RemoteException re ) {
		}
	}

	public ObjectInstance getObjectInstance(
		ObjectName pName
	) throws
		InstanceNotFoundException
	{
		try {
			return mRemoteConnector.getObjectInstance( pName );
		}
		catch( RemoteException re ) {
			//AS Not a good style but for now
			return null;
		}
	}

	public Set queryMBeans(
		ObjectName pName,
		QueryExp pQuery
	) {
		try {
			return mRemoteConnector.queryMBeans( pName, pQuery );
		}
		catch( RemoteException re ) {
			re.printStackTrace();
			//AS Not a good style but for now
			return null;
		}
	}

	public Set queryNames(
		ObjectName pName,
		QueryExp pQuery
	) {
		try {
			return mRemoteConnector.queryNames( pName, pQuery );
		}
		catch( RemoteException re ) {
			//AS Not a good style but for now
			return null;
		}
	}

	public boolean isRegistered(
		ObjectName pName
	) {
		try {
			return mRemoteConnector.isRegistered( pName );
		}
		catch( RemoteException re ) {
			//AS Not a good style but for now
			return false;
		}
	}

	public boolean isInstanceOf(
		ObjectName pName,
		String pClassName
	) throws
		InstanceNotFoundException
	{
		try {
			return mRemoteConnector.isInstanceOf( pName, pClassName );
		}
		catch( RemoteException re ) {
			//AS Not a good style but for now
			return false;
		}
	}

	public Integer getMBeanCount(
	) {
		try {
			return mRemoteConnector.getMBeanCount();
		}
		catch( RemoteException re ) {
			//AS Not a good style but for now
			return null;
		}
	}

	public Object getAttribute(
		ObjectName pName,
		String pAttribute
	) throws
		MBeanException,
		AttributeNotFoundException,
		InstanceNotFoundException,
		ReflectionException
	{
		try {
			return mRemoteConnector.getAttribute( pName, pAttribute );
		}
		catch( RemoteException re ) {
			//AS Not a good style but for now
			return null;
		}
	}

	public AttributeList getAttributes(
		ObjectName pName,
		String[] pAttributes
	) throws
		InstanceNotFoundException,
		ReflectionException
	{
		try {
			return mRemoteConnector.getAttributes( pName, pAttributes );
		}
		catch( RemoteException re ) {
			//AS Not a good style but for now
			return null;
		}
	}

	public void setAttribute(
		ObjectName pName,
		Attribute pAttribute
	) throws
		InstanceNotFoundException,
		AttributeNotFoundException,
		InvalidAttributeValueException,
		MBeanException,
		ReflectionException
	{
		try {
			mRemoteConnector.setAttribute( pName, pAttribute );
		}
		catch( RemoteException re ) {
		}
	}

	public AttributeList setAttributes(
		ObjectName pName,
		AttributeList pAttributes
	) throws
		InstanceNotFoundException,
		ReflectionException
	{
		try {
			return mRemoteConnector.setAttributes( pName, pAttributes );
		}
		catch( RemoteException re ) {
			//AS Not a good style but for now
			return null;
		}
	}

	public Object invoke(
		ObjectName pName,
		String pActionName,
		Object[] pParams,
		String[] pSignature
	) throws
		InstanceNotFoundException,
		MBeanException,
		ReflectionException
	{
		try {
			return mRemoteConnector.invoke( pName, pActionName, pParams, pSignature );
		}
		catch( RemoteException re ) {
			//AS Not a good style but for now
         re.printStackTrace();
			return null;
		}
	}

	public String getDefaultDomain(
	) {
		try {
			return mRemoteConnector.getDefaultDomain();
		}
		catch( RemoteException re ) {
			//AS Not a good style but for now
			return null;
		}
	}

	public void addNotificationListener(
		ObjectName pName,
		NotificationListener pListener,
		NotificationFilter pFilter,
		Object pHandback		
	) throws
		InstanceNotFoundException
	{
		try {
			Listener lRemoteListener = new Listener(
				pListener,
				pHandback,
				pName
			);
			UnicastRemoteObject.exportObject( lRemoteListener );
			mRemoteConnector.addNotificationListener(
				pName,
				lRemoteListener,
				pFilter,
				lRemoteListener.getHandback()
			);
			mListeners.addElement( lRemoteListener );
		}
		catch( RemoteException re ) {
			re.printStackTrace();
		}
	}

	public void addNotificationListener(
		ObjectName pName,
		ObjectName pListener,
		NotificationFilter pFilter,
		Object pHandback		
	) throws
		InstanceNotFoundException,
		UnsupportedOperationException
	{
		throw new UnsupportedOperationException(
			"A connector cannot support this method"
		);
	}

	public void removeNotificationListener(
		ObjectName pName,
		NotificationListener pListener
	) throws
		InstanceNotFoundException,
		ListenerNotFoundException
	{
		// Lookup if the given listener is registered
		Iterator i = mListeners.iterator();
		while( i.hasNext() ) {
			Listener lListener = (Listener) i.next();
			if(
				new Listener(
					pListener,
					null,
					pName
				).equals( lListener )
			) {
				// If found then get the remote listener and remove it from the
				// the Connector
				try {
					mRemoteConnector.removeNotificationListener(
						pName,
						lListener
					);
				}
				catch( RemoteException re ) {
					re.printStackTrace();
				}
				finally {
					i.remove();
				}
			}
		}
	}

	public void removeNotificationListener(
		ObjectName pName,
		ObjectName pListener
	) throws
		InstanceNotFoundException,
		ListenerNotFoundException,
		UnsupportedOperationException
	{
		throw new UnsupportedOperationException(
			"A connector cannot support this method"
		);
	}

	public MBeanInfo getMBeanInfo(
		ObjectName pName
	) throws
		InstanceNotFoundException,
		IntrospectionException,
		ReflectionException
	{
		try {
			return mRemoteConnector.getMBeanInfo( pName );
		}
		catch( RemoteException re ) {
			//AS Not a good style but for now
			return null;
		}
	}

	public ObjectInputStream deserialize(
		ObjectName pName,
		byte[] pData
	) throws
		InstanceNotFoundException,
		OperationsException,
		UnsupportedOperationException
	{
		throw new UnsupportedOperationException(
			"Remotely this method cannot be supported"
		);
	}

	public ObjectInputStream deserialize(
		String pClassName,
		byte[] pData
	) throws
		OperationsException,
		ReflectionException,
		UnsupportedOperationException
	{
		throw new UnsupportedOperationException(
			"Remotely this method cannot be supported"
		);
	}

	public ObjectInputStream deserialize(
		String pClassName,
		ObjectName pLoaderName,
		byte[] pData
	) throws
		InstanceNotFoundException,
		OperationsException,
		ReflectionException,
		UnsupportedOperationException
	{
		throw new UnsupportedOperationException(
			"Remotely this method cannot be supported"
		);
	}

	// Protected -----------------------------------------------------

	// Private -------------------------------------------------------

	/**
	* Listener wrapper around the remote RMI Notification Listener
	*/
	public class Listener implements RMINotificationListener {

		private NotificationListener			mLocalListener;
		private ObjectHandler					mHandbackHandler;
		private Object							mHandback;
		//AS This is necessary becasue to remove all of the registered
		//AS listeners when the connection is going down.
		//AS But maybe this is the wrong place !!
		private ObjectName						mObjectName;
		
		public Listener(
			NotificationListener pLocalListener,
			Object pHandback,
			ObjectName pName
		) {
			mLocalListener = pLocalListener;
			mHandback = pHandback;
			mHandbackHandler = new ObjectHandler( this.toString() );
			mObjectName = pName;
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
		) throws
			RemoteException
		{
			Object lHandback;
			// Take the given handback object (which should be the same object
			// as the stored one. If yes then replace it by the stored object
			if( mHandbackHandler.equals( pHandback ) ) {
				lHandback = mHandback;
			}
			else {
				lHandback = pHandback;
			}
			mLocalListener.handleNotification(
				pNotification,
				lHandback
			);
		}
		
		/**
		* @return							Object Handler of the given Handback
		*									object
		*/
		public ObjectHandler getHandback() {
			return mHandbackHandler;
		}
		/** Redesign it (AS) **/
		public ObjectName getObjectName() {
			return mObjectName;
		}
		/** Redesign it (AS) **/
		public NotificationListener getLocalListener() {
			return mLocalListener;
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
				return mLocalListener.equals(
					( (Listener) pTest).mLocalListener
				);
			}
			return false;
		}
		/**
		* @return							Hashcode of the local listener
		**/
		public int hashCode() {
			return mLocalListener.hashCode();
		}
	}
}	

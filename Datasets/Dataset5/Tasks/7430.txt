buf.append("properties=").append(properties).append("]"); //$NON-NLS-1$ //$NON-NLS-2$

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.provider.remoteservice.generic;

import java.io.Serializable;
import java.lang.reflect.Array;
import java.util.*;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.internal.provider.remoteservice.Messages;
import org.eclipse.ecf.remoteservice.IRemoteServiceReference;
import org.eclipse.ecf.remoteservice.IRemoteServiceRegistration;

public class RemoteServiceRegistrationImpl implements IRemoteServiceRegistration, Serializable {

	private static final long serialVersionUID = -3206899332723536545L;

	transient Object service;

	/** service classes for this registration. */
	protected String[] clazzes;

	/** service id. */
	protected long serviceid;

	/** properties for this registration. */
	protected Properties properties;

	/** service ranking. */
	protected int serviceranking;

	/* internal object to use for synchronization */
	transient protected Object registrationLock = new Object();

	/** The registration state */
	protected int state = REGISTERED;

	protected ID containerID = null;

	public static final int REGISTERED = 0x00;

	public static final int UNREGISTERING = 0x01;

	public static final int UNREGISTERED = 0x02;

	protected transient RemoteServiceReferenceImpl reference = null;

	protected transient RegistrySharedObject sharedObject = null;

	public RemoteServiceRegistrationImpl() {
		//

	}

	public void publish(RegistrySharedObject sharedObject1, RemoteServiceRegistryImpl registry, Object svc, String[] clzzes, Dictionary props) {
		this.sharedObject = sharedObject1;
		this.service = svc;
		this.clazzes = clzzes;
		this.containerID = registry.getContainerID();
		this.reference = new RemoteServiceReferenceImpl(this);
		synchronized (registry) {
			serviceid = registry.getNextServiceId();
			this.properties = createProperties(props);
			registry.publishService(this);
		}
	}

	public Object getService() {
		return service;
	}

	public ID getContainerID() {
		return containerID;
	}

	protected String[] getClasses() {
		return clazzes;
	}

	public IRemoteServiceReference getReference() {
		if (reference == null) {
			synchronized (this) {
				reference = new RemoteServiceReferenceImpl(this);
			}
		}
		return reference;
	}

	public void setProperties(Dictionary properties) {
		synchronized (registrationLock) {
			/* in the process of unregistering */
			if (state != REGISTERED) {
				throw new IllegalStateException(Messages.RemoteServiceRegistrationImpl_EXCEPTION_SERVICE_ALREADY_REGISTERED);
			}
			this.properties = createProperties(properties);
		}

		// XXX Need to notify that registration modified
	}

	public void unregister() {
		if (sharedObject != null) {
			sharedObject.sendUnregister(this);
		}
	}

	/**
	 * Construct a properties object from the dictionary for this
	 * ServiceRegistration.
	 * 
	 * @param props
	 *            The properties for this service.
	 * @return A Properties object for this ServiceRegistration.
	 */
	protected Properties createProperties(Dictionary props) {
		final Properties resultProps = new Properties(props);

		resultProps.setProperty(RemoteServiceRegistryImpl.REMOTEOBJECTCLASS, clazzes);

		resultProps.setProperty(RemoteServiceRegistryImpl.REMOTESERVICE_ID, new Long(serviceid));

		final Object ranking = resultProps.getProperty(RemoteServiceRegistryImpl.REMOTESERVICE_RANKING);

		serviceranking = (ranking instanceof Integer) ? ((Integer) ranking).intValue() : 0;

		return (resultProps);
	}

	static class Properties extends Hashtable {

		/**
		 * 
		 */
		private static final long serialVersionUID = -3684607010228779249L;

		/**
		 * Create a properties object for the service.
		 * 
		 * @param props
		 *            The properties for this service.
		 */
		private Properties(int size, Dictionary props) {
			super((size << 1) + 1);

			if (props != null) {
				synchronized (props) {
					final Enumeration keysEnum = props.keys();

					while (keysEnum.hasMoreElements()) {
						final Object key = keysEnum.nextElement();

						if (key instanceof String) {
							final String header = (String) key;

							setProperty(header, props.get(header));
						}
					}
				}
			}
		}

		/**
		 * Create a properties object for the service.
		 * 
		 * @param props
		 *            The properties for this service.
		 */
		protected Properties(Dictionary props) {
			this((props == null) ? 2 : Math.max(2, props.size()), props);
		}

		/**
		 * Get a clone of the value of a service's property.
		 * 
		 * @param key
		 *            header name.
		 * @return Clone of the value of the property or <code>null</code> if
		 *         there is no property by that name.
		 */
		protected Object getProperty(String key) {
			return (cloneValue(get(key)));
		}

		/**
		 * Get the list of key names for the service's properties.
		 * 
		 * @return The list of property key names.
		 */
		protected synchronized String[] getPropertyKeys() {
			final int size = size();

			final String[] keynames = new String[size];

			final Enumeration keysEnum = keys();

			for (int i = 0; i < size; i++) {
				keynames[i] = (String) keysEnum.nextElement();
			}

			return (keynames);
		}

		/**
		 * Put a clone of the property value into this property object.
		 * 
		 * @param key
		 *            Name of property.
		 * @param value
		 *            Value of property.
		 * @return previous property value.
		 */
		protected synchronized Object setProperty(String key, Object value) {
			return (put(key, cloneValue(value)));
		}

		/**
		 * Attempt to clone the value if necessary and possible.
		 * 
		 * For some strange reason, you can test to see of an Object is
		 * Cloneable but you can't call the clone method since it is protected
		 * on Object!
		 * 
		 * @param value
		 *            object to be cloned.
		 * @return cloned object or original object if we didn't clone it.
		 */
		protected static Object cloneValue(Object value) {
			if (value == null) {
				return null;
			}
			if (value instanceof String) {
				return (value);
			}

			final Class clazz = value.getClass();
			if (clazz.isArray()) {
				// Do an array copy
				final Class type = clazz.getComponentType();
				final int len = Array.getLength(value);
				final Object clonedArray = Array.newInstance(type, len);
				System.arraycopy(value, 0, clonedArray, 0, len);
				return clonedArray;
			}
			// must use reflection because Object clone method is protected!!
			try {
				return (clazz.getMethod("clone", (Class[]) null).invoke(value, (Object[]) null)); //$NON-NLS-1$
			} catch (final Exception e) {
				/* clone is not a public method on value's class */
			} catch (final Error e) {
				/* JCL does not support reflection; try some well known types */
				if (value instanceof Vector) {
					return (((Vector) value).clone());
				}
				if (value instanceof Hashtable) {
					return (((Hashtable) value).clone());
				}
			}
			return (value);
		}

		public synchronized String toString() {
			final String keys[] = getPropertyKeys();

			final int size = keys.length;

			final StringBuffer sb = new StringBuffer(20 * size);

			sb.append('{');

			int n = 0;
			for (int i = 0; i < size; i++) {
				final String key = keys[i];
				if (!key.equals(RemoteServiceRegistryImpl.REMOTEOBJECTCLASS)) {
					if (n > 0) {
						sb.append(", "); //$NON-NLS-1$
					}

					sb.append(key);
					sb.append('=');
					final Object value = get(key);
					if (value.getClass().isArray()) {
						sb.append('[');
						final int length = Array.getLength(value);
						for (int j = 0; j < length; j++) {
							if (j > 0) {
								sb.append(',');
							}
							sb.append(Array.get(value, j));
						}
						sb.append(']');
					} else {
						sb.append(value);
					}
					n++;
				}
			}

			sb.append('}');

			return (sb.toString());
		}
	}

	public Object getProperty(String key) {
		return properties.getProperty(key);
	}

	public String[] getPropertyKeys() {
		return properties.getPropertyKeys();
	}

	public long getServiceId() {
		return serviceid;
	}

	public Object callService(RemoteCallImpl call) throws Exception {
		return call.invoke(service);
	}

	public String toString() {
		StringBuffer buf = new StringBuffer("RemoteServiceRegistrationImpl["); //$NON-NLS-1$
		buf.append("containerID=").append(containerID).append(";"); //$NON-NLS-1$ //$NON-NLS-2$
		buf.append("serviceid=").append(serviceid).append(";"); //$NON-NLS-1$ //$NON-NLS-2$
		buf.append("serviceranking=").append(serviceranking).append(";"); //$NON-NLS-1$ //$NON-NLS-2$
		buf.append("classes=").append(Arrays.asList(clazzes)).append(";"); //$NON-NLS-1$ //$NON-NLS-2$
		buf.append("state=").append(state).append(";"); //$NON-NLS-1$ //$NON-NLS-2$
		buf.append("sharedobject=").append(sharedObject).append("]"); //$NON-NLS-1$ //$NON-NLS-2$
		return buf.toString();
	}

}
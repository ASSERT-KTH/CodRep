return type.getName() + "@" + name;

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.discovery.identity;

import org.eclipse.core.runtime.Assert;
import org.eclipse.ecf.core.identity.BaseID;
import org.eclipse.ecf.core.identity.Namespace;

/**
 * Service identity type.  ServiceIDs are IDs that uniquely identify
 * a remote service.  Subclasses may be created as appropriate.
 * 
 */
public class ServiceID extends BaseID implements IServiceID {

	private static final long serialVersionUID = 4362768703249025783L;

	protected IServiceTypeID type;

	protected String name;

	protected ServiceID(Namespace namespace, IServiceTypeID type, String name) {
		super(namespace);
		Assert.isNotNull(type);
		this.type = type;
		this.name = name;
	}

	protected String getFullyQualifiedName() {
		if (name == null)
			return type.getName();
		else
			return type.getName() + name;
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.core.identity.BaseID#namespaceCompareTo(org.eclipse.ecf.core.identity.BaseID)
	 */
	protected int namespaceCompareTo(BaseID o) {
		if (o instanceof ServiceID) {
			final ServiceID other = (ServiceID) o;
			final String typename = other.getFullyQualifiedName();
			return getFullyQualifiedName().compareTo(typename);
		} else {
			return 1;
		}
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.core.identity.BaseID#namespaceEquals(org.eclipse.ecf.core.identity.BaseID)
	 */
	protected boolean namespaceEquals(BaseID o) {
		if (o == null)
			return false;
		if (o instanceof ServiceID) {
			final ServiceID other = (ServiceID) o;
			if (other.getName().equals(getName())) {
				return true;
			}
		}
		return false;
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.core.identity.BaseID#namespaceGetName()
	 */
	protected String namespaceGetName() {
		return getFullyQualifiedName();
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.core.identity.BaseID#namespaceHashCode()
	 */
	protected int namespaceHashCode() {
		return getFullyQualifiedName().hashCode();
	}

	/**
	 * Get service type for this ID.
	 * @return String service type.  Will not be <code>null</code>.
	 */
	public String getServiceType() {
		return type.getName();
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.discovery.identity.IServiceID#getServiceTypeID()
	 */
	public IServiceTypeID getServiceTypeID() {
		return type;
	}

	/**
	 * Get service name for this ID.  
	 * 
	 * @return String service name.  May be <code>null</code>.
	 */
	public String getServiceName() {
		return name;
	}

	/* (non-Javadoc)
	 * @see java.lang.Object#toString()
	 */
	public String toString() {
		final StringBuffer buf = new StringBuffer("ServiceID["); //$NON-NLS-1$
		buf.append("type=").append(type).append(";name=").append(name).append( //$NON-NLS-1$ //$NON-NLS-2$
				";full=" + getFullyQualifiedName()).append("]"); //$NON-NLS-1$ //$NON-NLS-2$
		return buf.toString();
	}
}
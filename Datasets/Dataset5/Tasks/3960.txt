protected Namespace namespace;

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.core.identity;

import org.eclipse.core.runtime.Assert;

/**
 * Base class for ID implementation classes
 * 
 * Extensions for the <b>org.eclipse.ecf.namespace</b> extension point that
 * expose new Namespace subclasses and their own ID implementations are
 * recommended (but not required) to use this class as a superclass.
 * 
 */
public abstract class BaseID implements ID {

	private static final long serialVersionUID = -6242599410460002514L;

	Namespace namespace;

	protected BaseID() {
	}

	protected BaseID(Namespace namespace) {
		Assert.isNotNull(namespace, "namespace cannot be null"); //$NON-NLS-1$
		this.namespace = namespace;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see java.lang.Comparable#compareTo(T)
	 */
	public int compareTo(Object o) {
		Assert.isTrue(o != null && o instanceof BaseID,
				"incompatible types for compare"); //$NON-NLS-1$
		return namespace.getCompareToForObject(this, (BaseID) o);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see java.lang.Object#equals(java.lang.Object)
	 */
	public boolean equals(Object o) {
		if (o == null)
			return false;
		if (!(o instanceof BaseID)) {
			return false;
		}
		return namespace.testIDEquals(this, (BaseID) o);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.identity.ID#getName()
	 */
	public String getName() {
		return namespace.getNameForID(this);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.identity.ID#getNamespace()
	 */
	public Namespace getNamespace() {
		return namespace;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see java.lang.Object#hashCode()
	 */
	public int hashCode() {
		return namespace.getHashCodeForID(this);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.identity.ID#toExternalForm()
	 */
	public String toExternalForm() {
		return namespace.toExternalForm(this);
	}

	protected abstract int namespaceCompareTo(BaseID o);

	protected abstract boolean namespaceEquals(BaseID o);

	protected abstract String namespaceGetName();

	protected abstract int namespaceHashCode();

	protected String namespaceToExternalForm() {
		return namespace.getScheme() + Namespace.SCHEME_SEPARATOR
				+ namespaceGetName();
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.core.runtime.IAdaptable#getAdapter(java.lang.Class)
	 */
	public Object getAdapter(Class clazz) {
		return null;
	}
}
 No newline at end of file
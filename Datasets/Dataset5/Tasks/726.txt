package org.eclipse.ecf.internal.discovery.ui;

/****************************************************************************
 * Copyright (c) 2008 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Composent, Inc. - initial API and implementation
 *****************************************************************************/

package org.eclipse.ecf.discovery.ui.views;

import java.util.*;
import org.eclipse.ecf.discovery.IServiceProperties;
import org.eclipse.ui.views.properties.*;

/**
 *
 */
public class ServicePropertiesPropertySource implements IPropertySource, IPropertySource2 {

	class ServicePropertyDescriptor extends TextPropertyDescriptor {

		String value;

		/**
		 * @param name
		 * @param value
		 */
		public ServicePropertyDescriptor(String name, String value) {
			super(name, name);
			this.value = value;
		}

		public String getValue() {
			return value;
		}

	}

	List propertyDescriptors;

	private String createStringFromBytes(byte[] bytes) {
		StringBuffer buf = new StringBuffer("["); //$NON-NLS-1$
		for (int i = 0; i < bytes.length; i++) {
			buf.append(bytes[i]);
			if ((i + 1) != bytes.length)
				buf.append(","); //$NON-NLS-1$
		}
		buf.append("]"); //$NON-NLS-1$
		return buf.toString();
	}

	/**
	 * @param serviceProperties
	 */
	public ServicePropertiesPropertySource(IServiceProperties serviceProperties) {
		this.propertyDescriptors = new ArrayList();
		for (Enumeration e = serviceProperties.getPropertyNames(); e.hasMoreElements();) {
			String key = (String) e.nextElement();
			String value = null;
			Object val = serviceProperties.getProperty(key);
			if (val != null) {
				if (val instanceof String)
					value = (String) val;
				else if (val instanceof byte[])
					value = createStringFromBytes((byte[]) val);
				else
					value = val.toString();
			}
			propertyDescriptors.add(new ServicePropertyDescriptor(key, value));
		}
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ui.views.properties.IPropertySource#getEditableValue()
	 */
	public Object getEditableValue() {
		return null;
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ui.views.properties.IPropertySource#getPropertyDescriptors()
	 */
	public IPropertyDescriptor[] getPropertyDescriptors() {
		return (IPropertyDescriptor[]) propertyDescriptors.toArray(new IPropertyDescriptor[] {});
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ui.views.properties.IPropertySource#getPropertyValue(java.lang.Object)
	 */
	public Object getPropertyValue(Object id) {
		ServicePropertyDescriptor desc = findServicePropertyDescriptor(id);
		if (desc != null)
			return desc.getValue();
		return null;
	}

	/**
	 * @param id
	 * @return ServicePropertyDescriptor
	 */
	private ServicePropertyDescriptor findServicePropertyDescriptor(Object id) {
		for (Iterator i = propertyDescriptors.iterator(); i.hasNext();) {
			ServicePropertyDescriptor desc = (ServicePropertyDescriptor) i.next();
			if (desc.getId().equals(id))
				return desc;
		}
		return null;
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ui.views.properties.IPropertySource#isPropertySet(java.lang.Object)
	 */
	public boolean isPropertySet(Object id) {
		return false;
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ui.views.properties.IPropertySource#resetPropertyValue(java.lang.Object)
	 */
	public void resetPropertyValue(Object id) {
		// nothing
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ui.views.properties.IPropertySource#setPropertyValue(java.lang.Object, java.lang.Object)
	 */
	public void setPropertyValue(Object id, Object value) {
		// nothing
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ui.views.properties.IPropertySource2#isPropertyResettable(java.lang.Object)
	 */
	public boolean isPropertyResettable(Object id) {
		return false;
	}

}
if (p1.size() != p2.size())

/*******************************************************************************
 * Copyright (c) 2007 Versant Corp.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     Markus Kuppe (mkuppe <at> versant <dot> com) - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.tests.discovery;

import java.net.URI;
import java.util.Comparator;
import java.util.Enumeration;

import org.eclipse.ecf.discovery.IServiceInfo;
import org.eclipse.ecf.discovery.IServiceProperties;

/**
 * Used for testing equality 
 */
public class ServiceInfoComparator implements Comparator {

	private boolean compareServiceProperties(IServiceProperties p1, IServiceProperties p2) {
		if (p1.asProperties().size() != p2.asProperties().size())
			return false;
		for (final Enumeration e = p1.getPropertyNames(); e.hasMoreElements();) {
			final String key = (String) e.nextElement();
			final Object o1 = p1.getProperty(key);
			final Object o2 = p2.getProperty(key);
			if ((o1 instanceof byte[]) && (o2 instanceof byte[])) {
				final byte[] b1 = (byte[]) o1;
				final byte[] b2 = (byte[]) o2;
				for (int i = 0; i < b1.length; i++)
					if (b1[i] != b2[i])
						return false;
			} else if (!o1.equals(o2))
				return false;
		}
		return true;
	}

	/* (non-Javadoc)
	 * @see java.util.Comparator#compare(java.lang.Object, java.lang.Object)
	 */
	public int compare(Object arg0, Object arg1) {
		if (arg0 instanceof IServiceInfo && arg1 instanceof IServiceInfo) {
			final IServiceInfo first = (IServiceInfo) arg0;
			final IServiceInfo second = (IServiceInfo) arg1;
			final URI uri1 = first.getLocation();
			final URI uri2 = second.getLocation();
			final boolean result = (first.getServiceID().equals(second.getServiceID()) && uri1.getHost().equals(uri2.getHost()) && uri1.getPort() == uri2.getPort() && first.getPriority() == second.getPriority() && first.getWeight() == second.getWeight() && compareServiceProperties(first.getServiceProperties(), second.getServiceProperties()));
			if (result == true) {
				return 0;
			}
		}
		return -1;
	}

}
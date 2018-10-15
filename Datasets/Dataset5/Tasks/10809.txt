static final String NAMESPACE_ID = "ecf.msn.gokigenyou"; //$NON-NLS-1$

/****************************************************************************
 * Copyright (c) 2006, 2007 Remy Suen, Composent Inc., and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Remy Suen <remy.suen@gmail.com> - initial API and implementation
 *****************************************************************************/
package org.eclipse.ecf.internal.provider.msn;

import org.osgi.framework.BundleActivator;
import org.osgi.framework.BundleContext;

public final class Activator implements BundleActivator {

	public static final String PLUGIN_ID = "org.eclipse.ecf.provider.msn"; //$NON-NLS-1$
	
	static final String NAMESPACE_ID = "ecf.msn.gokigenyou";

	private static Activator plugin;

	public Activator() {
		plugin = this;
	}

	public void start(BundleContext context) throws Exception {
	}

	public void stop(BundleContext context) throws Exception {
		plugin = null;
	}

	public static Activator getDefault() {
		return plugin;
	}

}
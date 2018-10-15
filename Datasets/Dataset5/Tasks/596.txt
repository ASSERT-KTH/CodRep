public final class Messages extends NLS {

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
package org.eclipse.ecf.internal.provider.jslp;

import org.eclipse.osgi.util.NLS;

public class Messages extends NLS {
	private static final String BUNDLE_NAME = "org.eclipse.ecf.internal.provider.jslp.messages"; //$NON-NLS-1$
	public static String ContainerInstantiator_0;
	public static String JSLPDiscoveryContainer_0;
	public static String JSLPDiscoveryContainer_ContainerIsDisposed;
	public static String JSLPDiscoveryJob_NO_JSLP_BUNDLE;
	public static String JSLPDiscoveryJob_TITLE;
	public static String JSLPNamespace_2;
	public static String JSLPNamespace_3;
	public static String JSLPNamespace_4;
	public static String JSLPServiceTypeID_4;
	static {
		// initialize resource bundle
		NLS.initializeMessages(BUNDLE_NAME, Messages.class);
	}

	private Messages() {
		// nothing
	}
}
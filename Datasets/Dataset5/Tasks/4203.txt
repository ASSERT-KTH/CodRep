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
package org.eclipse.ecf.internal.provider.discovery;

import org.eclipse.osgi.util.NLS;

public class Messages extends NLS {
	private static final String BUNDLE_NAME = "org.eclipse.ecf.internal.provider.discovery.messages"; //$NON-NLS-1$
	public static String CompositeDiscoveryContainer_AlreadyConnected;
	public static String CompositeDiscoveryContainer_DEPRECATED;
	public static String CompositeDiscoveryContainerInstantiator;
	public static String CompositeNamespace_WrongParameterCount;
	public static String CompositeNamespace_WrongParameters;
	static {
		// initialize resource bundle
		NLS.initializeMessages(BUNDLE_NAME, Messages.class);
	}

	private Messages() {
		// do nothing
	}
}
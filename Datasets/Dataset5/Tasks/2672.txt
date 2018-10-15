private static final String BUNDLE_NAME = "org.eclipse.ecf.internal.remoteservice.rpc.messages"; //$NON-NLS-1$

/*******************************************************************************
 * Copyright (c) 2010 Naumen. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors: Pavel Samolisov - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.internal.remoteservice.rpc;

import org.eclipse.osgi.util.NLS;

public class Messages extends NLS {

	private static final String BUNDLE_NAME = "org.eclipse.ecf.internal.remoteservice.rpc"; //$NON-NLS-1$

	public static String RPC_INVALID_PARAMETERS_TO_ID_CREATION;
	public static String RPC_COULD_NOT_CREATE_ID;
	public static String RPC_COULD_NOT_CREATE_CONTAINER;
	public static String RPC_EXCEPTION_WHILE_EXECUTION_METHOD;

	static {
		// initialize resource bundle
		NLS.initializeMessages(BUNDLE_NAME, Messages.class);
	}

	private Messages() {
		// empty constructor
	}
}
public interface IJoinContext {

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/

package org.eclipse.ecf.core.security;

import javax.security.auth.callback.CallbackHandler;

public interface IJoinAuthorizationContext {
	/**
	 * Get the callbackhandler instance used by the provider to
	 * callback into application code.  The provider will typically use the
	 * callback handler to provide a set of callbacks for getting/retrieving
	 * authorization info
	 * 
	 * @return CallbackHandler
	 */
	public CallbackHandler getCallbackHandler();
}
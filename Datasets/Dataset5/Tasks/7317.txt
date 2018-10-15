public void helloAsync(String from, IAsyncCallback<Void> callback);

/*******************************************************************************
* Copyright (c) 2010 Composent, Inc. and others. All rights reserved. This
* program and the accompanying materials are made available under the terms of
* the Eclipse Public License v1.0 which accompanies this distribution, and is
* available at http://www.eclipse.org/legal/epl-v10.html
*
* Contributors:
*   Composent, Inc. - initial API and implementation
******************************************************************************/
package org.eclipse.ecf.examples.remoteservices.hello;

import org.eclipse.ecf.remoteservice.IAsyncCallback;
import org.eclipse.ecf.remoteservice.IAsyncRemoteServiceProxy;
import org.eclipse.equinox.concurrent.future.IFuture;

/**
 * @since 1.1
 */
public interface IHelloAsync extends IAsyncRemoteServiceProxy {

	public void helloAsync(String from, IAsyncCallback callback);
	public IFuture helloAsync(String from);

}
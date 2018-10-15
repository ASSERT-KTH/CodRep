public void addListener(IContainerListener l) {

/*******************************************************************************
 * Copyright (c) 2006 IBM, Inc and Composent, Inc. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Chris Aniszczyk <zx@us.ibm.com> - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.core;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

import org.eclipse.core.runtime.Platform;
import org.eclipse.ecf.core.events.IContainerEvent;
import org.eclipse.ecf.core.security.Callback;
import org.eclipse.ecf.core.security.CallbackHandler;
import org.eclipse.ecf.core.security.IConnectContext;
import org.eclipse.ecf.core.security.ObjectCallback;

/**
 * Abstract implementer of IContainer. Provides implementations of listener
 * methods that subsclasses may use to avoid having to implement them
 * themselves. This class may be subclassed as needed.
 * 
 */
public abstract class AbstractContainer implements IContainer {

	protected List containerListeners = new ArrayList();

	public void addListener(IContainerListener l, String filter) {
		containerListeners.add(l);
	}

	public void removeListener(IContainerListener l) {
		containerListeners.remove(l);
	}

	public void dispose() {
	}

	/**
	 * Fires a container event
	 * 
	 * @param event
	 */
	protected void fireContainerEvent(IContainerEvent event) {
		for (Iterator i = containerListeners.iterator(); i.hasNext();) {
			IContainerListener l = (IContainerListener) i.next();
			l.handleEvent(event);
		}
	}

	public Object getAdapter(Class serviceType) {
		return Platform.getAdapterManager().getAdapter(this, serviceType);
	}

	protected String getPasswordFromConnectContext(
			IConnectContext connectContext) throws ContainerConnectException {
		String pw = null;
		try {
			Callback[] callbacks = new Callback[1];
			callbacks[0] = new ObjectCallback();
			if (connectContext != null) {
				CallbackHandler handler = connectContext.getCallbackHandler();
				if (handler != null) {
					handler.handle(callbacks);
				}
			}
			ObjectCallback cb = (ObjectCallback) callbacks[0];
			pw = (String) cb.getObject();
		} catch (Exception e) {
			throw new ContainerConnectException(
					"Exception in CallbackHandler.handle(<callbacks>)", e);
		}
		return pw;
	}

}
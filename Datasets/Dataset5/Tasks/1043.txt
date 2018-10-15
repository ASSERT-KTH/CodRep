activator.getLog().log(new Status(IStatus.INFO, Activator.PLUGIN_ID, IStatus.INFO, NLS.bind(Messages.ECFStart_ERROR_DOCUMENT_SHARE_NOT_CREATED, container.getID()), null));

/****************************************************************************
 * Copyright (c) 20047 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Composent, Inc. - initial API and implementation
 *****************************************************************************/

package org.eclipse.ecf.internal.docshare;

import org.eclipse.core.runtime.*;
import org.eclipse.ecf.core.*;
import org.eclipse.ecf.core.events.*;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.start.IECFStart;
import org.eclipse.ecf.core.util.ECFException;
import org.eclipse.ecf.datashare.IChannelContainerAdapter;
import org.eclipse.osgi.util.NLS;

public class ECFStart implements IECFStart {

	IContainerListener containerListener = new IContainerListener() {

		/* (non-Javadoc)
		 * @see org.eclipse.ecf.core.IContainerListener#handleEvent(org.eclipse.ecf.core.events.IContainerEvent)
		 */
		public void handleEvent(IContainerEvent event) {
			Activator activator = Activator.getDefault();
			if (activator == null)
				return;
			final IContainerManager containerManager = activator.getContainerManager();
			if (containerManager == null)
				return;
			IContainer container = containerManager.getContainer(event.getLocalContainerID());
			if (container == null)
				return;
			if (event instanceof IContainerConnectedEvent || event instanceof IContainerDisconnectedEvent) {
				// connected
				IChannelContainerAdapter cca = (IChannelContainerAdapter) container.getAdapter(IChannelContainerAdapter.class);
				if (cca == null)
					return;
				ID containerID = container.getID();
				if (event instanceof IContainerConnectedEvent) {
					try {
						activator.addDocShare(containerID, cca);
					} catch (ECFException e) {
						activator.getLog().log(new Status(IStatus.WARNING, Activator.PLUGIN_ID, IStatus.WARNING, NLS.bind(Messages.ECFStart_ERROR_DOCUMENT_SHARE_NOT_CREATED, container.getID()), null));
					}
				} else if (event instanceof IContainerDisconnectedEvent) {
					// disconnected
					Activator.getDefault().removeDocShare(containerID);
				}
			} else if (event instanceof IContainerDisposeEvent) {
				containerManager.removeListener(containerManagerListener);
				container.removeListener(containerListener);
			}
		}

	};

	IContainerManagerListener containerManagerListener = new IContainerManagerListener() {

		/* (non-Javadoc)
		 * @see org.eclipse.ecf.core.IContainerManagerListener#containerAdded(org.eclipse.ecf.core.IContainer)
		 */
		public void containerAdded(IContainer container) {
			IChannelContainerAdapter cca = (IChannelContainerAdapter) container.getAdapter(IChannelContainerAdapter.class);
			if (cca == null)
				return;
			container.addListener(containerListener);
		}

		/* (non-Javadoc)
		 * @see org.eclipse.ecf.core.IContainerManagerListener#containerRemoved(org.eclipse.ecf.core.IContainer)
		 */
		public void containerRemoved(IContainer container) {
			container.removeListener(containerListener);
		}
	};

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.core.start.IECFStart#run(org.eclipse.core.runtime.IProgressMonitor)
	 */
	public IStatus run(IProgressMonitor monitor) {
		final IContainerManager containerManager = Activator.getDefault().getContainerManager();
		if (containerManager == null)
			return new Status(IStatus.WARNING, Activator.PLUGIN_ID, IStatus.WARNING, Messages.ECFStart_ERROR_CONTAINER_MANAGER_NOT_AVAILABLE, null);
		containerManager.addListener(containerManagerListener);
		return Status.OK_STATUS;
	}

}
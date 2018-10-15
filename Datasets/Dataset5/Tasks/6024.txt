public IStatus run(IProgressMonitor monitor) {

/****************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Composent, Inc. - initial API and implementation
 *****************************************************************************/
package org.eclipse.ecf.internal.example.collab.start;

import java.util.Collection;
import java.util.Iterator;
import org.eclipse.core.resources.ResourcesPlugin;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.ecf.core.start.IECFStart;
import org.eclipse.ecf.internal.example.collab.ClientPlugin;
import org.eclipse.ecf.internal.example.collab.CollabClient;

public class CollabStart implements IECFStart {
	Discovery discovery = null;

	public IStatus startup(IProgressMonitor monitor) {
		try {
			AccountStart as = new AccountStart();
			as.loadConnectionDetailsFromPreferenceStore();
			Collection c = as.getConnectionDetails();
			for (Iterator i = c.iterator(); i.hasNext();) {
				startConnection((ConnectionDetails) i.next());
			}
		} catch (Exception e) {
			return new Status(IStatus.ERROR, ClientPlugin.PLUGIN_ID, 200,
					"Exception in starting connection", e);
		}
		return new Status(IStatus.OK, ClientPlugin.PLUGIN_ID, 100, "OK", null);
	}

	private void startConnection(ConnectionDetails details) throws Exception {
		CollabClient client = new CollabClient();
		// ClientPlugin.log("ECF: Autostarting
		// containerType="+details.getContainerType()+",uri="+details.getTargetURI()+",nickname="+details.getNickname());
		client.createAndConnectClient(details.getContainerType(), details
				.getTargetURI(), details.getNickname(), details.getPassword(),
				ResourcesPlugin.getWorkspace().getRoot());
	}
}
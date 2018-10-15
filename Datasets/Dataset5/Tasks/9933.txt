//ClientPlugin.log("ECF: Autostarting containerType="+details.getContainerType()+",uri="+details.getTargetURI()+",nickname="+details.getNickname());

package org.eclipse.ecf.example.collab.start;

import java.util.Collection;
import java.util.Iterator;
import org.eclipse.core.resources.ResourcesPlugin;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.ecf.core.start.IECFStart;
import org.eclipse.ecf.example.collab.ClientPlugin;
import org.eclipse.ecf.example.collab.CollabClient;

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
		ClientPlugin.log("ECF: Autostarting containerType="+details.getContainerType()+",uri="+details.getTargetURI()+",nickname="+details.getNickname());
		client.createAndConnectClient(details.getContainerType(), details
				.getTargetURI(), details.getNickname(), details.getPassword(),
				ResourcesPlugin.getWorkspace().getRoot());
	}
}
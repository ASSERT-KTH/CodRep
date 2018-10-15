package org.eclipse.ecf.internal.examples.webinar.dnd;

package org.eclipse.ecf.internal.examples.webinar;

import org.eclipse.ecf.presence.roster.IRosterEntry;
import org.eclipse.ecf.presence.roster.IRosterItem;
import org.eclipse.ecf.presence.ui.dnd.IRosterViewerDropTarget;
import org.eclipse.swt.dnd.TransferData;
public class RosterViewerDropTarget1 implements IRosterViewerDropTarget {

	protected TransferData transferData = null;
	protected IRosterEntry rosterEntry = null;
	
	public boolean performDrop(Object data) {
		if (data instanceof String) {
			System.out.println("performDrop("+data+") to "+rosterEntry.getName());
			// Right here, send data to channel
			// sendString(rosterEntry.getUser().getID(),(String) data);
			return true;
		}
		return false;
	}

	public boolean validateDrop(IRosterItem rosterItem, int operation,
			TransferData transferType) {
		if (rosterItem instanceof IRosterEntry) {
			transferData = transferType;
			return true;
		} else {
			transferData = null;
			rosterEntry = null;
		}
		return false;
	}

}
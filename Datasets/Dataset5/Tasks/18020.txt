package org.eclipse.ecf.internal.presence.collab.ui;

package org.eclipse.ecf.presence.collab.ui;

import org.eclipse.ecf.presence.roster.IRosterEntry;
import org.eclipse.ecf.presence.roster.IRosterItem;
import org.eclipse.ecf.presence.ui.dnd.IRosterViewerDropTarget;
import org.eclipse.swt.dnd.TransferData;

public class RosterViewerDropTargetText implements IRosterViewerDropTarget {

	public boolean performDrop(Object data) {
		// TODO Auto-generated method stub
		return true;
	}

	public boolean validateDrop(IRosterItem rosterItem, int operation,
			TransferData transferType) {
		// TODO Auto-generated method stub
		System.out.println("RosterViewerDropTargetText.validateDrop("+rosterItem+","+operation+","+transferType+")");
		if (rosterItem != null && rosterItem instanceof IRosterEntry) return true;
		return false;
	}

}
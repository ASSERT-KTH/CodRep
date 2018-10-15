package org.eclipse.ecf.internal.ui.deprecated.views;

/**
 * 
 */
package org.eclipse.ecf.ui.views;

import org.eclipse.jface.viewers.LabelProvider;
import org.eclipse.swt.graphics.Image;

public class RosterViewLabelProvider extends LabelProvider {
	/**
	 * @param rosterView
	 */
	RosterViewLabelProvider(RosterView rosterView) {
	}

	public String getText(Object obj) {
		if (obj instanceof RosterGroup) {
			RosterGroup tg = (RosterGroup) obj;
			return tg.getLabel();
		} else
			return obj.toString();
	}

	public Image getImage(Object obj) {
		Image image = null; // By default, no image exists for obj, but if
		// found to be a specific instance, load from
		// plugin repository.
		if (obj instanceof RosterBuddy) {
			RosterBuddy o = (RosterBuddy) obj;
			if (o.getID() != null)
				image = o.getImage();
		} else if (obj instanceof RosterGroup) {
			image = ((RosterGroup) obj).getImage();
		}
		return image;
	}
}
 No newline at end of file
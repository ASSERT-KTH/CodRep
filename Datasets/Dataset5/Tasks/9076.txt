package org.eclipse.ecf.presence.collab.ui.view;

package org.eclipse.ecf.presence.collab.ui;

import org.eclipse.jface.viewers.Viewer;
import org.eclipse.jface.viewers.ViewerFilter;
import org.eclipse.ui.views.IViewDescriptor;

/**
 *
 */
public class ShowViewDialogViewerFilter extends ViewerFilter {
	public boolean select(Viewer viewer, Object parentElement,
			Object element) {
		if (element instanceof IViewDescriptor
				&& "org.eclipse.ui.internal.introview"
						.equals(((IViewDescriptor) element)
								.getId()))
			return false;
		else
			return true;
	}
}
 No newline at end of file
if (item.getMarker() == null)

package org.eclipse.ui.ide.examples.markers.markerSupport;

import org.eclipse.core.resources.IMarker;
import org.eclipse.jface.resource.JFaceResources;
import org.eclipse.jface.viewers.ViewerCell;
import org.eclipse.swt.SWT;
import org.eclipse.swt.graphics.Image;
import org.eclipse.swt.widgets.Control;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.ide.IDE;
import org.eclipse.ui.ide.examples.markers.MarkerExampleActivator;
import org.eclipse.ui.views.markers.MarkerField;
import org.eclipse.ui.views.markers.MarkerItem;
import org.eclipse.ui.views.markers.MarkerSupportConstants;

public class ExampleMarkerField extends MarkerField {

	public ExampleMarkerField() {
		// TODO Auto-generated constructor stub
	}

	@Override
	public String getValue(MarkerItem item) {

		String message = item.getAttributeValue(IMarker.MESSAGE,
				MarkerSupportConstants.EMPTY_STRING);
		String prefix = getFixablePrefix(item);

		if (prefix == null)
			return message;

		return prefix.concat(message);
	}

	private String getFixablePrefix(MarkerItem item) {

		if (!item.isConcrete())
			return null;

		IMarker marker = item.getMarker();
		// If there is no image get the full image rather than the decorated
		// one
		if (marker != null) {
			if (IDE.getMarkerHelpRegistry().hasResolutions(marker)) {
				return "[Fixable] ";
			}

		}

		return null;

	}

	@Override
	public String getColumnHeaderText() {
		return "Alternate Description";
	}

	@Override
	public int getDefaultColumnWidth(Control control) {
		return 250;
	}

	/**
	 * Get the image for the receiver.
	 * 
	 * @param item
	 * @return Image
	 */
	private Image getImage(MarkerItem item) {
		return JFaceResources.getResources().createImageWithDefault(
				MarkerExampleActivator.imageDescriptorFromPlugin(
						MarkerExampleActivator.PLUGIN_ID,
						"$nl$/icons/eclipse.png"));
	}

	@Override
	public void update(ViewerCell cell) {
		super.update(cell);
		MarkerItem item = (MarkerItem) cell.getElement();
		cell.setImage(annotateImage(item, getImage(item)));
		cell.setFont(JFaceResources.getFontRegistry().getBold(
				JFaceResources.BANNER_FONT));
		cell.setBackground(PlatformUI.getWorkbench().getDisplay()
				.getSystemColor(SWT.COLOR_INFO_BACKGROUND));
		cell.setForeground(PlatformUI.getWorkbench().getDisplay()
				.getSystemColor(SWT.COLOR_INFO_FOREGROUND));
	}
}
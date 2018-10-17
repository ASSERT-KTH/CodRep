boolean maximized = viewItem.getBoolean("window", "maximized", true);

package org.columba.core.gui;

import java.awt.BorderLayout;
import java.awt.Dimension;
import java.awt.event.WindowEvent;
import java.awt.event.WindowListener;

import javax.swing.JFrame;
import javax.swing.JPanel;

import org.columba.core.config.ViewItem;
import org.columba.core.config.WindowItem;
import org.columba.core.gui.util.ImageLoader;
import org.columba.core.util.WindowMaximizer;

/**
 * @author freddy
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class FrameView extends JFrame implements WindowListener {
	FrameController frameController;

	public FrameView(FrameController frameController) {
		this.frameController = frameController;

		this.setIconImage(
			ImageLoader.getImageIcon("ColumbaIcon.png").getImage());

		setTitle("Columba - version: " + org.columba.core.main.MainInterface.version);

		JPanel panel = (JPanel) this.getContentPane();
		panel.setLayout(new BorderLayout());
		panel.add(frameController.getStatusBar(), BorderLayout.SOUTH);

		addWindowListener(this);
	}

	public void maximize() {
		WindowMaximizer.maximize(this);

		/*
		Dimension screenSize = Toolkit.getDefaultToolkit().getScreenSize();
		setSize(screenSize);
		*/

		// FIXME: this works only with JDK1.4
		// has to be added with org.columba.core.util.Compatibility-class
		//setExtendedState(MAXIMIZED_BOTH);
	}

	public void saveWindowPosition(ViewItem viewItem) {

		java.awt.Dimension d = getSize();

		WindowItem item = viewItem.getWindowItem();

		item.set("x", 0);
		item.set("y", 0);
		item.set("width", d.width);
		item.set("height", d.height);
		
		boolean isMaximized = WindowMaximizer.isWindowMaximized(this);
		
		item.set("maximized", isMaximized );
	}

	public void loadWindowPosition(ViewItem viewItem) {
		int x = viewItem.getInteger("window", "width");
		int y = viewItem.getInteger("window", "height");
		boolean maximized = viewItem.getBoolean("window", "maximized");
		
		if (maximized)
			maximize();
		else {

			Dimension dim = new Dimension(x, y);
			setSize(dim);

			validate();
		}
	}
	/**
	 * @see java.awt.event.WindowListener#windowActivated(java.awt.event.WindowEvent)
	 */
	public void windowActivated(WindowEvent arg0) {
	}

	/**
	 * @see java.awt.event.WindowListener#windowClosed(java.awt.event.WindowEvent)
	 */
	public void windowClosed(WindowEvent arg0) {

	}

	/**
	 * @see java.awt.event.WindowListener#windowClosing(java.awt.event.WindowEvent)
	 */
	public void windowClosing(WindowEvent arg0) {
		frameController.close();
	}

	/**
	 * @see java.awt.event.WindowListener#windowDeactivated(java.awt.event.WindowEvent)
	 */
	public void windowDeactivated(WindowEvent arg0) {
	}

	/**
	 * @see java.awt.event.WindowListener#windowDeiconified(java.awt.event.WindowEvent)
	 */
	public void windowDeiconified(WindowEvent arg0) {
	}

	/**
	 * @see java.awt.event.WindowListener#windowIconified(java.awt.event.WindowEvent)
	 */
	public void windowIconified(WindowEvent arg0) {
	}

	/**
	 * @see java.awt.event.WindowListener#windowOpened(java.awt.event.WindowEvent)
	 */
	public void windowOpened(WindowEvent arg0) {
	}

}
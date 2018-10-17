return browser.isInitialized();

package org.columba.core.gui.htmlviewer;

import java.awt.BorderLayout;
import java.awt.event.ComponentEvent;
import java.awt.event.ComponentListener;
import java.util.logging.Logger;

import javax.swing.JComponent;
import javax.swing.JPanel;

import org.columba.core.logging.Logging;
import org.jdesktop.jdic.browser.WebBrowser;

/**
 * JDIC-enabled web browser component used by the Message Viewer in component
 * mail.
 * <p>
 * Note: Java Proxy support/configuration doesn't has any effect. This component
 * uses your system's proxy settings. For example, when using Firefox, you have
 * to set your proxy in Firefox and these same options are also used in Columba.
 * <p>
 * Javascript support can be used to access DOM. This way we can for example
 * print the HTML page using:
 * <code>webBrowser.executeScript("window.print();");</code>
 * <p>
 * TODO (@author fdietz): how to use images in Message Viewer, we can't set a base URL and load
 * images from columba.jar?
 * 
 * @author Frederik Dietz
 * 
 */
public class JDICHTMLViewerPlugin extends JPanel implements IHTMLViewerPlugin {

	/** JDK 1.4+ logging framework logger, used for logging. */
	private static final Logger LOG = Logger
			.getLogger("org.columba.core.gui.htmlviewer");

	private WebBrowser browser;

	public JDICHTMLViewerPlugin() {
		super();

		try {
			WebBrowser.setDebug(true);

			browser = new WebBrowser();

			// turn of focus stealing (workaround should be removed in the
			// future!)
			browser.setFocusable(false);

			setLayout(new BorderLayout());
			add(browser, BorderLayout.CENTER);
		} catch (Error e) {
			LOG.severe("Error while initializing JDIC native browser: "
					+ e.getMessage());
			if (Logging.DEBUG)
				e.printStackTrace();
		} catch (Exception e) {
			LOG
					.severe("Exception error while initializing JDIC native browser: "
							+ e.getMessage());
			if (Logging.DEBUG)
				e.printStackTrace();
		}

		addComponentListener(new ComponentListener() {

			public void componentHidden(ComponentEvent e) {
				browser.setVisible(false);
				browser = null;
			}

			public void componentMoved(ComponentEvent e) {
				// TODO Auto-generated method stub

			}

			public void componentResized(ComponentEvent e) {
				// TODO Auto-generated method stub

			}

			public void componentShown(ComponentEvent e) {
				// TODO Auto-generated method stub

			}

		});

	}

	public void view(String htmlSource) {
		browser.setContent(htmlSource);
	}

	public JComponent getComponent() {
		return this;
	}

	public String getSelectedText() {
		return "getSelected() not yet supported by JDIC";
	}

	public boolean initialized() {
		return true;
	}

	public JComponent getContainer() {
		return this;
	}
}
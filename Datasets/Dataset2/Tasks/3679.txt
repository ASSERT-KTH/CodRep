import org.columba.api.plugin.IExtensionInterface;

package org.columba.core.gui.htmlviewer;

import java.io.IOException;
import java.io.InputStream;
import java.net.URL;

import javax.swing.JComponent;

import org.columba.core.plugin.IExtensionInterface;

/**
 * HTML Viewer interface. 
 * 
 * @author Frederik Dietz
 */
public interface IHTMLViewerPlugin extends IExtensionInterface{

	/**
	 * View HTML page using the source string.
	 * 
	 * @param htmlSource	HTML source string
	 */
	void view(String body);
	
	
	/**
	 * Get selected text.
	 * 
	 * @return	selected text
	 */
	String getSelectedText();
	
	/**
	 * Check if HTML viewer was initialized correctly.
	 * 
	 * @return	true, if initialized correctly. False, otherwise.
	 * 
	 */
	boolean initialized();
	
	/**
	 * Get view.
	 * 
	 * @return	view
	 */
	JComponent getView();
}
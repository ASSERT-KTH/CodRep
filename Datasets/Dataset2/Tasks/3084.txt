super("org.columba.core.frame", "org/columba/core/plugin/frame.xml");

/*
 * Created on 05.04.2003
 *
 * To change the template for this generated file go to
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
package org.columba.core.plugin;

import org.columba.core.xml.XmlElement;

/**
 * @author frd
 *
 * To change the template for this generated type comment go to
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
public class FramePluginHandler extends AbstractPluginHandler {

	public FramePluginHandler() {
		super("org.columba.core.frame", "org/columba/core/frame/frame.xml");

		parentNode = getConfig().getRoot().getElement("framelist");
	}
	
	

	/* (non-Javadoc)
		 * @see org.columba.core.plugin.AbstractPluginHandler#addExtension(java.lang.String, org.columba.core.xml.XmlElement)
		 */
	public void addExtension(String id, XmlElement extension) {

	}
}
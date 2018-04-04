"org/columba/mail/plugin/pop3preprocessingfilter.xml");

/*
 * Created on Apr 13, 2003
 *
 * To change the template for this generated file go to
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
package org.columba.mail.plugin;

import java.util.ListIterator;

import org.columba.core.plugin.AbstractPluginHandler;
import org.columba.core.xml.XmlElement;

/**
 * @author frd
 *
 * To change the template for this generated type comment go to
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
public class POP3PreProcessingFilterPluginHandler
	extends AbstractPluginHandler {


	/**
	 * @param id
	 * @param config
	 */
	public POP3PreProcessingFilterPluginHandler() {
		super(
			"org.columba.mail.pop3preprocessingfilter",
			"org/columba/mail/filter/pop3preprocessingfilter.xml");

		parentNode =
			getConfig().getRoot().getElement("pop3preprocessingfilterlist");

	}

	
	/* (non-Javadoc)
	 * @see org.columba.core.plugin.AbstractPluginHandler#addExtension(java.lang.String, org.columba.core.xml.XmlElement)
	 */
	public void addExtension(String id, XmlElement extension) {
		ListIterator iterator = extension.getElements().listIterator();
		XmlElement action;
		while (iterator.hasNext()) {
			action = (XmlElement) iterator.next();
			action.addAttribute("name", id + '$' + action.getAttribute("name"));
			parentNode.addElement(action);
		}
	}

}
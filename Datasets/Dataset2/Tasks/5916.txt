setTooltipText("Context-specific help");

//The contents of this file are subject to the Mozilla Public License Version 1.1
//(the "License"); you may not use this file except in compliance with the 
//License. You may obtain a copy of the License at http://www.mozilla.org/MPL/
//
//Software distributed under the License is distributed on an "AS IS" basis,
//WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License 
//for the specific language governing rights and
//limitations under the License.
//
//The Original Code is "The Columba Project"
//
//The Initial Developers of the Original Code are Frederik Dietz and Timo Stich.
//Portions created by Frederik Dietz and Timo Stich are Copyright (C) 2003. 
//
//All Rights Reserved.

package org.columba.core.gui.action;

import javax.help.CSH;

import org.columba.core.action.FrameAction;
import org.columba.core.gui.frame.AbstractFrameController;
import org.columba.core.gui.util.ImageLoader;
import org.columba.core.help.HelpManager;
import org.columba.core.util.GlobalResourceLoader;

/**
 * @author frd
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
public class ShowContextSpecificHelpAction extends FrameAction {

	/**
	 * @param frameController
	 * @param name
	 */
	public ShowContextSpecificHelpAction(AbstractFrameController frameController) {
		super(
			frameController,
			GlobalResourceLoader.getString(null, null, "Context Specific Help"));
			
		
		setSmallIcon(ImageLoader.getSmallImageIcon("stock_extended-help-16.png"));
		setLargeIcon(ImageLoader.getImageIcon("stock_extended-help.png"));
		
		/*
		setSmallIcon(ImageLoader.getSmallImageIcon("stock_help-agent-16.png"));
		setLargeIcon(ImageLoader.getImageIcon("stock_help-agent.png"));
		*/
		
		setLongDescription("Context-specific help");
		
		enableToolBarText(false);
		
		addActionListener(new CSH.DisplayHelpAfterTracking(HelpManager.getHelpBroker()));
	}

}
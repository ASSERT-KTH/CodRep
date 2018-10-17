public abstract class FrameAction extends BasicAction implements PluginInterface {

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

package org.columba.core.action;

import org.columba.core.gui.frame.FrameMediator;
import org.columba.core.plugin.PluginInterface;

/**
 * FrameAction has an additional reference to its frame
 * controller.
 * <p>
 * This is necessary because actions have to know in which
 * frame they are, to provide visual feedback for the user
 * in the correct frame.
 * 
 * <p>
 * Note: Most constructors of this class are depreceated.
 * 
 * The preferred way should be to use methods instead to add
 * additional information to the action.
 * 
 * Example: @see org.columba.core.gui.action.CancelAction
 *
 * @author fdietz
 */
public class FrameAction extends BasicAction implements PluginInterface {

	protected FrameMediator frameMediator;

	/**
	 * 
	 * default constructor 
	 * 
	 * @param frameMediator		frame controller 
	 * @param name					i18n name
	 * 
	 */
	public FrameAction(FrameMediator frameController, String name) {
		super(name);
		this.frameMediator = frameController;
	}

	/**
	 * Returns the frame controller
	 * 
	 * @return FrameController
	 */
	public FrameMediator getFrameMediator() {
		return frameMediator;
	}

	/**
	 * Sets the frameMediator.
	 * 
	 * @param frameMediator 
	 */
	public void setFrameMediator(FrameMediator frameController) {
		this.frameMediator = frameController;
	}

}
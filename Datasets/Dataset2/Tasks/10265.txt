import org.columba.core.gui.frame.FrameController;

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
package org.columba.core.command;

import org.columba.core.gui.FrameController;


/**
 * @author Timo Stich (tstich@users.sourceforge.net)
 * 
 */
public abstract class SelectiveGuiUpdateCommand extends Command {
	
	private static int lastTimeStamp;

	/**
	 * Constructor for SelectiveGuiUpdateCommand.
	 * @param frameController
	 * @param references
	 */
	public SelectiveGuiUpdateCommand(
		DefaultCommandReference[] references) {
		super(references);
	}
	
	public SelectiveGuiUpdateCommand(
			FrameController frame, DefaultCommandReference[] references) {
			super(frame, references);
		}
	/**
	 * @see org.columba.core.command.Command#updateGUI()
	 */
	public void finish() throws Exception {
		if( getTimeStamp() == lastTimeStamp ) updateGUI();
	}

	/**
	 * @see org.columba.core.command.Command#setTimeStamp(int)
	 */
	public void setTimeStamp(int timeStamp) {
		super.setTimeStamp(timeStamp);
		
		if( timeStamp > lastTimeStamp ) {
			lastTimeStamp = timeStamp;
		}
	}

}
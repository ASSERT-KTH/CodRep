calendarFrame.getCalendarView().viewToday();

// The contents of this file are subject to the Mozilla Public License Version
// 1.1
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
//The Initial Developers of the Original Code are Frederik Dietz and Timo
// Stich.
//Portions created by Frederik Dietz and Timo Stich are Copyright (C) 2003.
//
//All Rights Reserved.
package org.columba.calendar.ui.action;

import java.awt.event.ActionEvent;

import org.columba.api.gui.frame.IFrameMediator;
import org.columba.calendar.ui.frame.CalendarFrameMediator;
import org.columba.core.gui.action.AbstractColumbaAction;
import org.columba.core.resourceloader.ImageLoader;

/**
 * @author fdietz
 *
 */
public class TodayAction extends AbstractColumbaAction {

	/**
	 * @param frameMediator
	 * @param name
	 */
	public TodayAction(IFrameMediator frameMediator) {
		super(frameMediator, "Show Today");
		
		putValue(AbstractColumbaAction.TOOLBAR_NAME, "Today");
		setShowToolBarText(false);
		
		putValue(AbstractColumbaAction.LARGE_ICON, ImageLoader.getImageIcon("stock_home_24.png"));
		putValue(AbstractColumbaAction.SMALL_ICON, ImageLoader.getImageIcon("stock_home_16.png"));
	}

	/**
	 * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
	 */
	public void actionPerformed(ActionEvent e) {
		CalendarFrameMediator calendarFrame = (CalendarFrameMediator) frameMediator;
		
		calendarFrame.goToday();

	}

}
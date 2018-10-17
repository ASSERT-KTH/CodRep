boolean showText = (a.isShowToolBarText() || ALIGNMENT );

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

package org.columba.core.gui.toolbar;

import java.awt.Insets;

import javax.swing.Icon;
import javax.swing.SwingConstants;

import org.columba.core.action.BasicAction;
import org.columba.core.config.Config;
import org.columba.core.config.GuiItem;
import org.columba.core.gui.menu.CButton;

public class ToolbarButton extends CButton {
	String buttonText;

	static boolean WITH_TEXT = false;
	static boolean ALIGNMENT = true;

	public ToolbarButton()
	{
		super();
		setRequestFocusEnabled(false);
	}
	
	public ToolbarButton(Icon icon)
	{
		super(icon);
		setRequestFocusEnabled(false);
	}
	
	public ToolbarButton(BasicAction a) {
		super(a);

		setRequestFocusEnabled(false);
		setMargin(new Insets(1, 1, 1, 1));

		GuiItem item = Config.getOptionsConfig().getGuiItem();
		
                WITH_TEXT = item.getBoolean("toolbar","enable_text");
                ALIGNMENT = item.getBoolean("toolbar","text_position");

		setIcon(a.getLargeIcon());
		if (WITH_TEXT) {
			boolean showText = a.isShowToolBarText();
			if (!showText) setText("");
			else setText(a.getToolBarName());
			
			if (ALIGNMENT) {
				setVerticalTextPosition(SwingConstants.BOTTOM);
				setHorizontalTextPosition(SwingConstants.CENTER);
			} else {
				setVerticalTextPosition(SwingConstants.CENTER);
				setHorizontalTextPosition(SwingConstants.RIGHT);
			}
		} else {
			setText(null);
		}
	}

	public boolean isFocusTraversable() {
		return isRequestFocusEnabled();
	}
}
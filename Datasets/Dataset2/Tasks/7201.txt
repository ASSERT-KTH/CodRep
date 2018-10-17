import org.columba.core.action.BasicAction;

// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Library General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, write to the Free Software
// Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

package org.columba.mail.gui.message.action;

import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

import org.columba.mail.gui.action.BasicAction;
import org.columba.mail.gui.message.MessageController;

/**
 * Title:
 * Description:
 * Copyright:    Copyright (c) 2001
 * Company:
 * @author
 * @version 1.0
 */

public class MessageActionListener implements ActionListener
{
	private MessageController messageController;

	public BasicAction dictAction;

	public MessageActionListener( MessageController messageController )
	{
		this.messageController = messageController;

		dictAction =
			new BasicAction(
				"Dict.org lookup selection...", "Dict lookup selection...", "Look up definition of selection with online dictionary...", "DICT",
				null,
				null,
				'0',
				null);
		dictAction.addActionListener(this);
	}

	public void actionPerformed(ActionEvent e)
	{
		String action = e.getActionCommand();

		/*
		if (action
			.equals(MainInterface.frameController.globalActionCollection.copyAction.getActionCommand()))
		{
			copy();
		}
		else if (
			action.equals(
				MainInterface.frameController.globalActionCollection.selectAllAction.getActionCommand()))
		{
			selectAll();
		}
		*/
		
		if ( action.equals( dictAction.getActionCommand() ) )
		{
			// FIXME
			/*
			String text = messageController.getView().getSelectedText();


			DictLookup dict = DictLookup.getInstance();
			dict.lookup( text );
			*/
		}

	}

	public void copy()
	{
		// FIXME
		/*
		JTextComponent c =
			(JTextComponent) messageController.getView().getActiveViewer();

		c.copy();
		*/
	}

	public void selectAll()
	{
		// FIXME
		/*
		JTextComponent c =
			(JTextComponent) messageController.getView().getActiveViewer();

		c.selectAll();
		*/
	}

}
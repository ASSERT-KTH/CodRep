scroller.setPreferredSize(new Dimension(300,0));

/*
 * OverviewOptionPane.java - Corny welcome screen
 * :tabSize=8:indentSize=8:noTabs=false:
 * :folding=explicit:collapseFolds=1:
 *
 * Copyright (C) 2001 Slava Pestov
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
 */

package org.gjt.sp.jedit.options;

//{{{ Imports
import javax.swing.*;
import java.awt.*;
import java.io.IOException;
import org.gjt.sp.jedit.*;
import org.gjt.sp.util.Log;
//}}}

public class OverviewOptionPane extends AbstractOptionPane
{
	//{{{ OverviewOptionPane constructor
	public OverviewOptionPane()
	{
		super("overview");
	} //}}}

	//{{{ _init() method
	public void _init()
	{
		setLayout(new BorderLayout());
		JEditorPane ep = new JEditorPane();
		try
		{
			ep.setPage(getClass().getResource("overview.html"));
		}
		catch(IOException io)
		{
			Log.log(Log.ERROR,this,io);
		}
		ep.setEditable(false);
		JScrollPane scroller = new JScrollPane(ep);
		scroller.setPreferredSize(new Dimension(400,0));
		add(BorderLayout.CENTER,scroller);
	} //}}}

	//{{{ _save() method
	public void _save() {}
	//}}}
}
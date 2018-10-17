} //}}}

/*
 * EnhancedMenu.java - jEdit menu
 * :tabSize=8:indentSize=8:noTabs=false:
 * :folding=explicit:collapseFolds=1:
 *
 * Copyright (C) 2001, 2003 Slava Pestov
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

package org.gjt.sp.jedit.menu;

//{{{ Imports
import javax.swing.event.*;
import javax.swing.*;
import java.util.StringTokenizer;
import org.gjt.sp.jedit.msg.*;
import org.gjt.sp.jedit.*;
//}}}

public class EnhancedMenu extends JMenu implements MenuListener
{
	//{{{ EnhancedMenu constructor
	public EnhancedMenu(String name)
	{
		this(name,jEdit.getProperty(name.concat(".label")),
			jEdit.getActionContext());
	} //}}}

	//{{{ EnhancedMenu constructor
	public EnhancedMenu(String name, String label)
	{
		this(name,label,jEdit.getActionContext());
	} //}}}

	//{{{ EnhancedMenu constructor
	public EnhancedMenu(String name, String label, ActionContext context)
	{
		this.context = context;
		if(label == null)
			label = name;

		char mnemonic;
		int index = label.indexOf('$');
		if(index != -1 && label.length() - index > 1)
		{
			mnemonic = Character.toLowerCase(label.charAt(index + 1));
			label = label.substring(0,index).concat(label.substring(++index));
		}
		else
			mnemonic = '\0';

		setText(label);
		if(!OperatingSystem.isMacOS())
			setMnemonic(mnemonic);

		String menuItems = jEdit.getProperty(name);
		if(menuItems != null)
		{
			StringTokenizer st = new StringTokenizer(menuItems);
			while(st.hasMoreTokens())
			{
				String menuItemName = st.nextToken();
				if(menuItemName.equals("-"))
					addSeparator();
				else
					add(GUIUtilities.loadMenuItem(context,menuItemName,true));
			}
		}

		initialComponentCount = getMenuComponentCount();

		providerCode = jEdit.getProperty(name + ".code");

		ebStub = new EditBusStub(name);
		ebStub.menuOutOfDate = true;

		addMenuListener(this);

		if(providerCode != null)
			EditBus.addToBus(ebStub);
	} //}}}

	//{{{ menuSelected() method
	public void menuSelected(MenuEvent evt)
	{
		init();
	} //}}}

	public void menuDeselected(MenuEvent e) {}

	public void menuCanceled(MenuEvent e) {}

	//{{{ init() method
	public void init()
	{
		if(providerCode == null)
			return;

		if(provider == null)
		{
			Object obj = BeanShell.eval(null,
				BeanShell.getNameSpace(),
				providerCode);
			provider = (DynamicMenuProvider)obj;
		}

		if(provider == null)
		{
			// error
			providerCode = null;
			return;
		}

		if(ebStub.menuOutOfDate || provider.updateEveryTime())
		{
			ebStub.menuOutOfDate = false;

			while(getMenuComponentCount() != initialComponentCount)
				remove(getMenuComponentCount() - 1);

			if(provider != null)
				provider.update(this);
		}
	} //}}}

	//{{{ Protected members
	protected int initialComponentCount;
	protected ActionContext context;

	protected String providerCode;
	protected DynamicMenuProvider provider;

	protected EditBusStub ebStub;

	//{{{ finalize() method
	protected void finalize() throws Exception
	{
		if(ebStub != null)
			EditBus.removeFromBus(ebStub);
	} //}}}

	//}}}

	//{{{ EditBusStub class
	/* EnhancedMenu has a reference to EditBusStub, but not the other
	 * way around. So when the EnhancedMenu is being garbage collected
	 * its finalize() method removes the EditBusStub from the edit bus. */
	static class EditBusStub implements EBComponent
	{
		String name;
		boolean menuOutOfDate;

		EditBusStub(String name)
		{
			this.name = name;
			menuOutOfDate = true;
		}

		public void handleMessage(EBMessage msg)
		{
			if(msg instanceof DynamicMenuChanged
				&& name.equals(((DynamicMenuChanged)msg)
				.getMenuName()))
			{
				menuOutOfDate = true;
			}
			else if(msg instanceof PropertiesChanged)
			{
				// while this might be questionable, some
				// menus depend on properties
				menuOutOfDate = true;
			}
		}
	}
}
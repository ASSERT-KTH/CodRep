if(OperatingSystem.hasJava14())

/*
 * AppearanceOptionPane.java - Appearance options panel
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
import java.awt.event.*;
import java.awt.*;
import java.io.*;
import org.gjt.sp.jedit.gui.FontSelector;
import org.gjt.sp.jedit.*;
import org.gjt.sp.util.Log;
//}}}

public class AppearanceOptionPane extends AbstractOptionPane
{
	//{{{ AppearanceOptionPane constructor
	public AppearanceOptionPane()
	{
		super("appearance");
	} //}}}

	//{{{ _init() method
	protected void _init()
	{
		/* Look and feel */
		addComponent(new JLabel(jEdit.getProperty("options.appearance.lf.note")));

		lfs = UIManager.getInstalledLookAndFeels();
		String[] names = new String[lfs.length];
		String lf = UIManager.getLookAndFeel().getClass().getName();
		int index = 0;
		for(int i = 0; i < names.length; i++)
		{
			names[i] = lfs[i].getName();
			if(lf.equals(lfs[i].getClassName()))
				index = i;
		}

		lookAndFeel = new JComboBox(names);
		lookAndFeel.setSelectedIndex(index);
		lookAndFeel.addActionListener(new ActionListener()
		{
			public void actionPerformed(ActionEvent evt)
			{
				updateEnabled();
			}
		});

		addComponent(jEdit.getProperty("options.appearance.lf"),
			lookAndFeel);

		/* Primary Metal L&F font */
		primaryFont = new FontSelector(jEdit.getFontProperty(
			"metal.primary.font"));
		addComponent(jEdit.getProperty("options.appearance.primaryFont"),
			primaryFont);

		/* Secondary Metal L&F font */
		secondaryFont = new FontSelector(jEdit.getFontProperty(
			"metal.secondary.font"));
		addComponent(jEdit.getProperty("options.appearance.secondaryFont"),
			secondaryFont);

		updateEnabled();

		/* Use jEdit colors in all text components */
		textColors = new JCheckBox(jEdit.getProperty(
			"options.appearance.textColors"));
		textColors.setSelected(jEdit.getBooleanProperty("textColors"));
		addComponent(textColors);

		/* Decorate frames with look and feel (JDK 1.4 only) */
		decorateFrames = new JCheckBox(jEdit.getProperty(
			"options.appearance.decorateFrames"));
		decorateFrames.setSelected(jEdit.getBooleanProperty("decorate.frames"));

		/* Decorate dialogs with look and feel (JDK 1.4 only) */
		decorateDialogs = new JCheckBox(jEdit.getProperty(
			"options.appearance.decorateDialogs"));
		decorateDialogs.setSelected(jEdit.getBooleanProperty("decorate.dialogs"));

		if(System.getProperty("java.version").compareTo("1.4") >= 0)
		{
			addComponent(decorateFrames);
			addComponent(decorateDialogs);
		}
	} //}}}

	//{{{ _save() method
	protected void _save()
	{
		String lf = lfs[lookAndFeel.getSelectedIndex()].getClassName();
		jEdit.setProperty("lookAndFeel",lf);
		jEdit.setFontProperty("metal.primary.font",primaryFont.getFont());
		jEdit.setFontProperty("metal.secondary.font",secondaryFont.getFont());
		jEdit.setBooleanProperty("textColors",textColors.isSelected());
		jEdit.setBooleanProperty("decorate.frames",decorateFrames.isSelected());
		jEdit.setBooleanProperty("decorate.dialogs",decorateDialogs.isSelected());
	} //}}}

	//{{{ Private members

	//{{{ Instance variables
	private UIManager.LookAndFeelInfo[] lfs;
	private JComboBox lookAndFeel;
	private FontSelector primaryFont;
	private FontSelector secondaryFont;
	private JCheckBox textColors;
	private JCheckBox decorateFrames;
	private JCheckBox decorateDialogs;
	//}}}

	//{{{ updateEnabled() method
	private void updateEnabled()
	{
		String className = lfs[lookAndFeel.getSelectedIndex()]
			.getClassName();

		if(className.equals("javax.swing.plaf.metal.MetalLookAndFeel")
			|| className.equals("com.incors.plaf.kunststoff.KunststoffLookAndFeel"))
		{
			primaryFont.setEnabled(true);
			secondaryFont.setEnabled(true);
		}
		else
		{
			primaryFont.setEnabled(false);
			secondaryFont.setEnabled(false);
		}
	} //}}}

	//}}}
}
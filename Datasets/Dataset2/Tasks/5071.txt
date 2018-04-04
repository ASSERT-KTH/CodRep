jEdit.setBooleanProperty("buffer.encodingAutodetect",

/*
 * GeneralOptionPane.java - General options panel
 * :tabSize=8:indentSize=8:noTabs=false:
 * :folding=explicit:collapseFolds=1:
 *
 * Copyright (C) 1998, 2003 Slava Pestov
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
import org.gjt.sp.jedit.*;
//}}}

public class GeneralOptionPane extends AbstractOptionPane
{
	//{{{ GeneralOptionPane constructor
	public GeneralOptionPane()
	{
		super("general");
	} //}}}

	//{{{ _init() method
	protected void _init()
	{
		/* Line separator */
		String[] lineSeps = { jEdit.getProperty("lineSep.unix"),
			jEdit.getProperty("lineSep.windows"),
			jEdit.getProperty("lineSep.mac") };
		lineSeparator = new JComboBox(lineSeps);
		String lineSep = jEdit.getProperty("buffer.lineSeparator",
			System.getProperty("line.separator"));
		if("\n".equals(lineSep))
			lineSeparator.setSelectedIndex(0);
		else if("\r\n".equals(lineSep))
			lineSeparator.setSelectedIndex(1);
		else if("\r".equals(lineSep))
			lineSeparator.setSelectedIndex(2);
		addComponent(jEdit.getProperty("options.general.lineSeparator"),
			lineSeparator);

		/* Default file encoding */
		encoding = new JComboBox(MiscUtilities.getEncodings());
		encoding.setEditable(true);
		encoding.setSelectedItem(jEdit.getProperty("buffer.encoding",
			System.getProperty("file.encoding")));
		addComponent(jEdit.getProperty("options.general.encoding"),encoding);

		/* Auto detect encoding */
		encodingAutodetect = new JCheckBox(jEdit.getProperty(
			"options.general.encodingAutodetect"));
		encodingAutodetect.setSelected(jEdit.getBooleanProperty("buffer.encodingAutodetect"));
		addComponent(encodingAutodetect);

		/* Check mod status on focus */
		String[] modCheckOptions = {
			jEdit.getProperty("options.general.checkModStatus.nothing"),
			jEdit.getProperty("options.general.checkModStatus.prompt"),
			jEdit.getProperty("options.general.checkModStatus.reload")
		};
		checkModStatus = new JComboBox(modCheckOptions);
		if(jEdit.getBooleanProperty("autoReload"))
			checkModStatus.setSelectedIndex(2);
		else if(jEdit.getBooleanProperty("autoReloadDialog"))
			checkModStatus.setSelectedIndex(1);
		else
			checkModStatus.setSelectedIndex(0);
		addComponent(jEdit.getProperty("options.general.checkModStatus"),
			checkModStatus);

		/* Recent file list size */
		recentFiles = new JTextField(jEdit.getProperty(
			"options.general.recentFiles"));
		recentFiles.setText(jEdit.getProperty("recentFiles"));
		addComponent(jEdit.getProperty("options.general.recentFiles"),
			recentFiles);

		/* Sort recent file list */
		sortRecent = new JCheckBox(jEdit.getProperty(
			"options.general.sortRecent"));
		sortRecent.setSelected(jEdit.getBooleanProperty("sortRecent"));
		addComponent(sortRecent);

		/* Save caret positions */
		saveCaret = new JCheckBox(jEdit.getProperty(
			"options.general.saveCaret"));
		saveCaret.setSelected(jEdit.getBooleanProperty("saveCaret"));
		addComponent(saveCaret);

		/* Persistent markers */
		persistentMarkers = new JCheckBox(jEdit.getProperty(
			"options.general.persistentMarkers"));
		persistentMarkers.setSelected(jEdit.getBooleanProperty(
			"persistentMarkers"));
		addComponent(persistentMarkers);

		/* Session management */
		restore = new JCheckBox(jEdit.getProperty(
			"options.general.restore"));
		restore.setSelected(jEdit.getBooleanProperty("restore"));
		restore.addActionListener(new ActionListener()
		{
			public void actionPerformed(ActionEvent evt)
			{
				restoreCLI.setEnabled(restore.isSelected());
			}
		});

		addComponent(restore);
		restoreCLI = new JCheckBox(jEdit.getProperty(
			"options.general.restore.cli"));
		restoreCLI.setSelected(jEdit.getBooleanProperty("restore.cli"));
		restoreCLI.setEnabled(restore.isSelected());
		addComponent(restoreCLI);

		/* Sort buffers */
		sortBuffers = new JCheckBox(jEdit.getProperty(
			"options.general.sortBuffers"));
		sortBuffers.setSelected(jEdit.getBooleanProperty("sortBuffers"));
		sortBuffers.addActionListener(new ActionListener()
		{
			public void actionPerformed(ActionEvent evt)
			{
				sortByName.setEnabled(sortBuffers.isSelected());
			}
		});

		addComponent(sortBuffers);

		/* Sort buffers by names */
		sortByName = new JCheckBox(jEdit.getProperty(
			"options.general.sortByName"));
		sortByName.setSelected(jEdit.getBooleanProperty("sortByName"));
		sortByName.setEnabled(sortBuffers.isSelected());
		addComponent(sortByName);

		/* Two-stage save */
		twoStageSave = new JCheckBox(jEdit.getProperty(
			"options.general.twoStageSave"));
		twoStageSave.setSelected(jEdit.getBooleanProperty(
			"twoStageSave"));
		addComponent(twoStageSave);

		/* Confirm save all */
		confirmSaveAll = new JCheckBox(jEdit.getProperty(
			"options.general.confirmSaveAll"));
		confirmSaveAll.setSelected(jEdit.getBooleanProperty(
			"confirmSaveAll"));
		addComponent(confirmSaveAll);

		/* Strip trailing EOL */
		stripTrailingEOL = new JCheckBox(jEdit.getProperty(
			"options.general.stripTrailingEOL"));
		stripTrailingEOL.setSelected(jEdit.getBooleanProperty("stripTrailingEOL"));
		addComponent(stripTrailingEOL);

	} //}}}

	//{{{ _save() method
	protected void _save()
	{
		String lineSep = null;
		switch(lineSeparator.getSelectedIndex())
		{
		case 0:
			lineSep = "\n";
			break;
		case 1:
			lineSep = "\r\n";
			break;
		case 2:
			lineSep = "\r";
			break;
		}
		jEdit.setProperty("buffer.lineSeparator",lineSep);
		jEdit.setProperty("buffer.encoding",(String)
			encoding.getSelectedItem());
		jEdit.setBooleanProperty("buffer.encodingAutodetect",(String)
			encodingAutodetect.isSelected());
		switch(checkModStatus.getSelectedIndex())
		{
		case 0:
			jEdit.setBooleanProperty("autoReloadDialog",false);
			jEdit.setBooleanProperty("autoReload",false);
			break;
		case 1:
			jEdit.setBooleanProperty("autoReloadDialog",true);
			jEdit.setBooleanProperty("autoReload",false);
			break;
		case 2:
			jEdit.setBooleanProperty("autoReloadDialog",true);
			jEdit.setBooleanProperty("autoReload",true);
			break;
		}
		jEdit.setProperty("recentFiles",recentFiles.getText());
		jEdit.setBooleanProperty("sortRecent",sortRecent.isSelected());
		jEdit.setBooleanProperty("saveCaret",saveCaret.isSelected());
		jEdit.setBooleanProperty("persistentMarkers",
			persistentMarkers.isSelected());
		jEdit.setBooleanProperty("restore",restore.isSelected());
		jEdit.setBooleanProperty("restore.cli",restoreCLI.isSelected());
		jEdit.setBooleanProperty("sortBuffers",sortBuffers.isSelected());
		jEdit.setBooleanProperty("sortByName",sortByName.isSelected());
		jEdit.setBooleanProperty("twoStageSave",twoStageSave.isSelected());
		jEdit.setBooleanProperty("confirmSaveAll",confirmSaveAll.isSelected());
		jEdit.setBooleanProperty("stripTrailingEOL", stripTrailingEOL.isSelected());
	} //}}}

	//{{{ Private members
	private JComboBox lineSeparator;
	private JComboBox encoding;
	private JCheckBox encodingAutodetect;
	private JComboBox checkModStatus;
	private JTextField recentFiles;
	private JCheckBox saveCaret;
	private JCheckBox sortRecent;
	private JCheckBox persistentMarkers;
	private JCheckBox restore;
	private JCheckBox restoreCLI;
	private JCheckBox sortBuffers;
	private JCheckBox sortByName;
	private JCheckBox twoStageSave;
	private JCheckBox confirmSaveAll;
	private JCheckBox stripTrailingEOL;
	//}}}
}
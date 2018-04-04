gutterHighlightColor.getSelectedColor());

/*
 * GutterOptionPane.java - Gutter options panel
 * :tabSize=8:indentSize=8:noTabs=false:
 * :folding=explicit:collapseFolds=1:
 *
 * Copyright (C) 2000 mike dillon
 * Portions copyright (C) 2001, 2002 Slava Pestov
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
import org.gjt.sp.jedit.gui.*;
import org.gjt.sp.jedit.*;
//}}}

public class GutterOptionPane extends AbstractOptionPane
{
	//{{{ GutterOptionPane constructor
	public GutterOptionPane()
	{
		super("gutter");
	} //}}}

	//{{{ _init() method
	public void _init()
	{
		/* Line numbering */
		lineNumbersEnabled = new JCheckBox(jEdit.getProperty(
			"options.gutter.lineNumbers"));
		lineNumbersEnabled.setSelected(jEdit.getBooleanProperty(
			"view.gutter.lineNumbers"));
		addComponent(lineNumbersEnabled);

		/* Text font */
		gutterFont = new FontSelector(
			jEdit.getFontProperty("view.gutter.font",
			new Font("Monospaced",Font.PLAIN,10)));

		addComponent(jEdit.getProperty("options.gutter.font"),gutterFont);

		/* Text color */
		addComponent(jEdit.getProperty("options.gutter.foreground"),
			gutterForeground = new ColorWellButton(
			jEdit.getColorProperty("view.gutter.fgColor")),
			GridBagConstraints.VERTICAL);

		/* Background color */
		addComponent(jEdit.getProperty("options.gutter.background"),
			gutterBackground = new ColorWellButton(
			jEdit.getColorProperty("view.gutter.bgColor")),
			GridBagConstraints.VERTICAL);

		/* Border width */
		/* gutterBorderWidth = new JTextField(jEdit.getProperty(
			"view.gutter.borderWidth"));
		addComponent(jEdit.getProperty("options.gutter.borderWidth"),
			gutterBorderWidth); */

		/* Number alignment */
		/* String[] alignments = new String[] {
			"Left", "Center", "Right"
		};
		gutterNumberAlignment = new JComboBox(alignments);
		String alignment = jEdit.getProperty("view.gutter.numberAlignment");
		if("right".equals(alignment))
			gutterNumberAlignment.setSelectedIndex(2);
		else if("center".equals(alignment))
			gutterNumberAlignment.setSelectedIndex(1);
		else
			gutterNumberAlignment.setSelectedIndex(0);
		addComponent(jEdit.getProperty("options.gutter.numberAlignment"),
			gutterNumberAlignment); */

		/* Current line highlight */
		gutterCurrentLineHighlightEnabled = new JCheckBox(jEdit.getProperty(
			"options.gutter.currentLineHighlight"));
		gutterCurrentLineHighlightEnabled.setSelected(jEdit.getBooleanProperty(
			"view.gutter.highlightCurrentLine"));
		addComponent(gutterCurrentLineHighlightEnabled,
			gutterCurrentLineHighlight = new ColorWellButton(
			jEdit.getColorProperty("view.gutter.currentLineColor")),
			GridBagConstraints.VERTICAL);

		/* Highlight interval and color */
		gutterHighlightInterval = new JTextField(jEdit.getProperty(
			"view.gutter.highlightInterval"),3);

		Box gutterHighlightBox = new Box(BoxLayout.X_AXIS);
		gutterHighlightBox.add(new JLabel(jEdit.getProperty(
			"options.gutter.interval-1")));
		gutterHighlightBox.add(Box.createHorizontalStrut(3));
		gutterHighlightBox.add(gutterHighlightInterval);
		gutterHighlightBox.add(Box.createHorizontalStrut(3));
		gutterHighlightBox.add(new JLabel(jEdit.getProperty(
			"options.gutter.interval-2")));
		gutterHighlightBox.add(Box.createHorizontalStrut(12));

		addComponent(gutterHighlightBox,gutterHighlightColor
			= new ColorWellButton(jEdit.getColorProperty(
			"view.gutter.highlightColor")),
			GridBagConstraints.VERTICAL);

		/* Bracket highlight */
		gutterBracketHighlightEnabled = new JCheckBox(jEdit.getProperty(
			"options.gutter.bracketHighlight"));
		gutterBracketHighlightEnabled.setSelected(jEdit.getBooleanProperty(
			"view.gutter.bracketHighlight"));
		addComponent(gutterBracketHighlightEnabled,
			gutterBracketHighlight = new ColorWellButton(
			jEdit.getColorProperty("view.gutter.bracketColor")),
			GridBagConstraints.VERTICAL);

		/* Marker highlight */
		gutterMarkerHighlightEnabled = new JCheckBox(jEdit.getProperty(
			"options.gutter.markerHighlight"));
		gutterMarkerHighlightEnabled.setSelected(jEdit.getBooleanProperty(
			"view.gutter.markerHighlight"));
		addComponent(gutterMarkerHighlightEnabled,
			gutterMarkerHighlight = new ColorWellButton(
			jEdit.getColorProperty("view.gutter.markerColor")),
			GridBagConstraints.VERTICAL);

		/* Fold marker color */
		addComponent(jEdit.getProperty("options.gutter.foldColor"),
			gutterFoldMarkers = new ColorWellButton(
			jEdit.getColorProperty("view.gutter.foldColor")),
			GridBagConstraints.VERTICAL);

		/* Focused border color */
		addComponent(jEdit.getProperty("options.gutter.focusBorderColor"),
			gutterFocusBorder = new ColorWellButton(
			jEdit.getColorProperty("view.gutter.focusBorderColor")),
			GridBagConstraints.VERTICAL);

		/* unfocused border color */
		addComponent(jEdit.getProperty("options.gutter.noFocusBorderColor"),
			gutterNoFocusBorder = new ColorWellButton(
			jEdit.getColorProperty("view.gutter.noFocusBorderColor")),
			GridBagConstraints.VERTICAL);

		/* Mouse actions */
		addSeparator("options.gutter.actions");

		int c = clickActionKeys.length;
		String[] clickActionNames = new String[c];
		for(int i = 0; i < c; i++)
		{
			clickActionNames[i] = jEdit.getProperty(
				"options.gutter."+clickActionKeys[i]);
		}

		c = clickModifierKeys.length;
		String[] clickModifierNames = new String[c];
		for(int i = 0; i < c; i++)
		{
			clickModifierNames[i] = jEdit.getProperty(
				"options.gutter."+clickModifierKeys[i]);
		}

		gutterClickActions = new JComboBox[c];

		for(int i = 0; i < c; i++)
		{
			JComboBox cb = new JComboBox(clickActionNames);
			gutterClickActions[i] = cb;

			String val = jEdit.getProperty("view.gutter."+clickModifierKeys[i]);
			for(int j = 0; j < clickActionKeys.length; j++)
			{
				if(val.equals(clickActionKeys[j]))
				{
					cb.setSelectedIndex(j);
				}
			}

			addComponent(clickModifierNames[i],cb);
		}
	} //}}}

	//{{{ _save() method
	public void _save()
	{
		jEdit.setBooleanProperty("view.gutter.lineNumbers", lineNumbersEnabled
			.isSelected());

		jEdit.setFontProperty("view.gutter.font",gutterFont.getFont());
		jEdit.setColorProperty("view.gutter.fgColor",gutterForeground
			.getSelectedColor());
		jEdit.setColorProperty("view.gutter.bgColor",gutterBackground
			.getSelectedColor());

		/* jEdit.setProperty("view.gutter.borderWidth",
			gutterBorderWidth.getText());

		String alignment = null;
		switch(gutterNumberAlignment.getSelectedIndex())
		{
		case 2:
			alignment = "right";
			break;
		case 1:
			alignment = "center";
			break;
		case 0: default:
			alignment = "left";
		}
		jEdit.setProperty("view.gutter.numberAlignment", alignment); */

		jEdit.setBooleanProperty("view.gutter.highlightCurrentLine",
			gutterCurrentLineHighlightEnabled.isSelected());
		jEdit.setColorProperty("view.gutter.currentLineColor",
			gutterCurrentLineHighlight.getSelectedColor());
		jEdit.setProperty("view.gutter.highlightInterval",
			gutterHighlightInterval.getText());
		jEdit.setColorProperty("view.gutter.highlightColor",
			gutterHighlight.getSelectedColor());

		jEdit.setBooleanProperty("view.gutter.bracketHighlight",
			gutterBracketHighlightEnabled.isSelected());
		jEdit.setColorProperty("view.gutter.bracketColor",
			gutterBracketHighlight.getSelectedColor());
		jEdit.setBooleanProperty("view.gutter.markerHighlight",
			gutterMarkerHighlightEnabled.isSelected());
		jEdit.setColorProperty("view.gutter.markerColor",
			gutterMarkerHighlight.getSelectedColor());
		jEdit.setColorProperty("view.gutter.foldColor",
			gutterFoldMarkers.getSelectedColor());
		jEdit.setColorProperty("view.gutter.focusBorderColor",
			gutterFocusBorder.getSelectedColor());
		jEdit.setColorProperty("view.gutter.noFocusBorderColor",
			gutterNoFocusBorder.getSelectedColor());

		int c = clickModifierKeys.length;
		for(int i = 0; i < c; i++)
		{
			int idx = gutterClickActions[i].getSelectedIndex();
			jEdit.setProperty("view.gutter."+clickModifierKeys[i],
				clickActionKeys[idx]);
		}
	} //}}}

	//{{{ Private members
	private FontSelector gutterFont;
	private ColorWellButton gutterForeground;
	private ColorWellButton gutterBackground;
	private JTextField gutterBorderWidth;
	private JTextField gutterHighlightInterval;
	private ColorWellButton gutterHighlightColor;
	private JComboBox gutterNumberAlignment;
	private JCheckBox lineNumbersEnabled;
	private JCheckBox gutterCurrentLineHighlightEnabled;
	private ColorWellButton gutterCurrentLineHighlight;
	private JCheckBox gutterBracketHighlightEnabled;
	private ColorWellButton gutterBracketHighlight;
	private JCheckBox gutterMarkerHighlightEnabled;
	private ColorWellButton gutterMarkerHighlight;
	private ColorWellButton gutterFoldMarkers;
	private ColorWellButton gutterFocusBorder;
	private ColorWellButton gutterNoFocusBorder;

	private JComboBox[] gutterClickActions;
	
	private static final String[] clickActionKeys = new String[] {
		"toggleFold",
		"toggleFoldFully",
		"selectFold"
	};
	
	private static final String[] clickModifierKeys = new String[] {
		"gutterClick",
		"gutterShiftClick",
		"gutterControlClick",
		"gutterAltClick"
	}; //}}}
}
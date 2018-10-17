"options.textArea.stripTrailingEOL"));

/*
 * TextAreaOptionPane.java - Text area options panel
 * :tabSize=8:indentSize=8:noTabs=false:
 * :folding=explicit:collapseFolds=1:
 *
 * Copyright (C) 1998, 1999, 2000 Slava Pestov
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
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.*;
import org.gjt.sp.jedit.gui.*;
import org.gjt.sp.jedit.*;
//}}}

public class TextAreaOptionPane extends AbstractOptionPane
{
	//{{{ TextAreaOptionPane constructor
	public TextAreaOptionPane()
	{
		super("textarea");
	} //}}}

	//{{{ _init() method
	public void _init()
	{
		/* Font */
		font = new FontSelector(jEdit.getFontProperty("view.font"));

		addComponent(jEdit.getProperty("options.textarea.font"),font);

		/* Text color */
		addComponent(jEdit.getProperty("options.textarea.foreground"),
			foregroundColor = new ColorWellButton(
			jEdit.getColorProperty("view.fgColor")),
			GridBagConstraints.VERTICAL);

		/* Background color */
		addComponent(jEdit.getProperty("options.textarea.background"),
			backgroundColor = new ColorWellButton(
			jEdit.getColorProperty("view.bgColor")),
			GridBagConstraints.VERTICAL);

		/* Caret color, caret blink, block caret */
		blinkCaret = new JCheckBox(jEdit.getProperty("options.textarea"
			+ ".blinkCaret"));
		blinkCaret.setSelected(jEdit.getBooleanProperty("view.caretBlink"));

		blockCaret = new JCheckBox(jEdit.getProperty("options.textarea"
			+ ".blockCaret"));
		blockCaret.setSelected(jEdit.getBooleanProperty("view.blockCaret"));

		Box caretSettings = new Box(BoxLayout.X_AXIS);
		caretSettings.add(new JLabel(jEdit.getProperty(
			"options.textarea.caret")));
		caretSettings.add(Box.createHorizontalStrut(6));
		caretSettings.add(blinkCaret);
		caretSettings.add(blockCaret);

		addComponent(caretSettings,caretColor = new ColorWellButton(
			jEdit.getColorProperty("view.caretColor")),
			GridBagConstraints.VERTICAL);

		/* Selection color */
		addComponent(jEdit.getProperty("options.textarea.selection"),
			selectionColor = new ColorWellButton(
			jEdit.getColorProperty("view.selectionColor")),
			GridBagConstraints.VERTICAL);

		/* Multiple selection color */
		addComponent(jEdit.getProperty("options.textarea.multipleSelection"),
			multipleSelectionColor = new ColorWellButton(
			jEdit.getColorProperty("view.multipleSelectionColor")),
			GridBagConstraints.VERTICAL);

		/* Line highlight */
		lineHighlight = new JCheckBox(jEdit.getProperty("options.textarea"
			+ ".lineHighlight"));
		lineHighlight.setSelected(jEdit.getBooleanProperty("view.lineHighlight"));
		addComponent(lineHighlight,lineHighlightColor = new ColorWellButton(
			jEdit.getColorProperty("view.lineHighlightColor")),
			GridBagConstraints.VERTICAL);

		/* Structure highlight */
		structureHighlight = new JCheckBox(jEdit.getProperty("options.textarea"
			+ ".structureHighlight"));
		structureHighlight.setSelected(jEdit.getBooleanProperty(
			"view.structureHighlight"));
		addComponent(structureHighlight,structureHighlightColor = new ColorWellButton(
			jEdit.getColorProperty("view.structureHighlightColor")),
			GridBagConstraints.VERTICAL);

		/* EOL markers */
		eolMarkers = new JCheckBox(jEdit.getProperty("options.textarea"
			+ ".eolMarkers"));
		eolMarkers.setSelected(jEdit.getBooleanProperty("view.eolMarkers"));
		addComponent(eolMarkers,eolMarkerColor =new ColorWellButton(
			jEdit.getColorProperty("view.eolMarkerColor")),
			GridBagConstraints.VERTICAL);

		/* Wrap guide */
		wrapGuide = new JCheckBox(jEdit.getProperty("options.textarea"
			+ ".wrapGuide"));
		wrapGuide.setSelected(jEdit.getBooleanProperty("view.wrapGuide"));
		addComponent(wrapGuide,wrapGuideColor = new ColorWellButton(
			jEdit.getColorProperty("view.wrapGuideColor")),
			GridBagConstraints.VERTICAL);

		/* Electric borders */
		electricBorders = new JCheckBox(jEdit.getProperty("options.textarea"
			+ ".electricBorders"));
		electricBorders.setSelected(!"0".equals(jEdit.getProperty(
			"view.electricBorders")));
		addComponent(electricBorders);

		/* Anti-aliasing */
		antiAlias = new JCheckBox(jEdit.getProperty("options.textarea"
			+ ".antiAlias"));
		boolean antiAliasEnabled = jEdit.getBooleanProperty(
			"view.antiAlias");
		font.setAntiAliasEnabled(antiAliasEnabled);
		antiAlias.addActionListener(new ActionListener()
		{
			public void actionPerformed(ActionEvent evt)
			{
				font.setAntiAliasEnabled(
					antiAlias.isSelected());
				font.repaint();
			}
		});
		antiAlias.setSelected(antiAliasEnabled);
		addComponent(antiAlias);

		/* Fractional font metrics */
		fracFontMetrics = new JCheckBox(jEdit.getProperty("options.textarea"
			+ ".fracFontMetrics"));
		fracFontMetrics.setSelected(jEdit.getBooleanProperty(
			"view.fracFontMetrics"));
		addComponent(fracFontMetrics);

		/* Strip trailing EOL */
		stripTrailingEOL = new JCheckBox(jEdit.getProperty(
			"options.general.stripTrailingEOL"));
		stripTrailingEOL.setSelected(jEdit.getBooleanProperty("stripTrailingEOL"));
		addComponent(stripTrailingEOL);

	} //}}}

	//{{{ _save() method
	public void _save()
	{
		jEdit.setFontProperty("view.font",font.getFont());

		jEdit.setColorProperty("view.fgColor",foregroundColor
			.getSelectedColor());
		jEdit.setColorProperty("view.bgColor",backgroundColor
			.getSelectedColor());
		jEdit.setBooleanProperty("view.caretBlink",blinkCaret.isSelected());
		jEdit.setBooleanProperty("view.blockCaret",blockCaret.isSelected());
		jEdit.setColorProperty("view.caretColor",caretColor
			.getSelectedColor());
		jEdit.setColorProperty("view.selectionColor",selectionColor
			.getSelectedColor());
		jEdit.setColorProperty("view.multipleSelectionColor",multipleSelectionColor
			.getSelectedColor());
		jEdit.setBooleanProperty("view.lineHighlight",lineHighlight
			.isSelected());
		jEdit.setColorProperty("view.lineHighlightColor",
			lineHighlightColor.getSelectedColor());
		jEdit.setBooleanProperty("view.structureHighlight",structureHighlight
			.isSelected());
		jEdit.setColorProperty("view.structureHighlightColor",
			structureHighlightColor.getSelectedColor());
		jEdit.setBooleanProperty("view.eolMarkers",eolMarkers
			.isSelected());
		jEdit.setColorProperty("view.eolMarkerColor",
			eolMarkerColor.getSelectedColor());
		jEdit.setBooleanProperty("view.wrapGuide",wrapGuide
			.isSelected());
		jEdit.setColorProperty("view.wrapGuideColor",
			wrapGuideColor.getSelectedColor());
		jEdit.setIntegerProperty("view.electricBorders",electricBorders
			.isSelected() ? 3 : 0);
		jEdit.setBooleanProperty("view.antiAlias",antiAlias.isSelected());
		jEdit.setBooleanProperty("view.fracFontMetrics",fracFontMetrics.isSelected());
		jEdit.setBooleanProperty("stripTrailingEOL", stripTrailingEOL.isSelected());
	} //}}}

	//{{{ Private members
	private FontSelector font;
	private ColorWellButton foregroundColor;
	private ColorWellButton backgroundColor;
	private JCheckBox blinkCaret;
	private JCheckBox blockCaret;
	private ColorWellButton caretColor;
	private ColorWellButton selectionColor;
	private ColorWellButton multipleSelectionColor;
	private JCheckBox lineHighlight;
	private ColorWellButton lineHighlightColor;
	private JCheckBox structureHighlight;
	private ColorWellButton structureHighlightColor;
	private JCheckBox eolMarkers;
	private ColorWellButton eolMarkerColor;
	private JCheckBox wrapGuide;
	private ColorWellButton wrapGuideColor;
	private JCheckBox electricBorders;
	private JCheckBox antiAlias;
	private JCheckBox fracFontMetrics;
	private JCheckBox stripTrailingEOL;
	//}}}
}
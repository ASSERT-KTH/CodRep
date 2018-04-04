buttonPanel.setBorder(BorderFactory.createEmptyBorder(17, 12, 11, 11));

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

package org.columba.core.gui.config;

import java.awt.BorderLayout;
import java.awt.Component;
import java.awt.Font;
import java.awt.GridLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyEvent;
import java.util.Locale;

import javax.swing.BorderFactory;
import javax.swing.DefaultComboBoxModel;
import javax.swing.DefaultListCellRenderer;
import javax.swing.JButton;
import javax.swing.JCheckBox;
import javax.swing.JComboBox;
import javax.swing.JComponent;
import javax.swing.JDialog;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JList;
import javax.swing.JPanel;
import javax.swing.KeyStroke;
import javax.swing.SwingConstants;

import net.javaprog.ui.wizard.plaf.basic.SingleSideEtchedBorder;

import org.columba.core.config.Config;
import org.columba.core.config.GuiItem;
import org.columba.core.gui.plugin.ConfigurationDialog;
import org.columba.core.gui.themes.ThemeSwitcher;
import org.columba.core.gui.util.ButtonWithMnemonic;
import org.columba.core.gui.util.DefaultFormBuilder;
import org.columba.core.gui.util.FontProperties;
import org.columba.core.gui.util.FontSelectionDialog;
import org.columba.core.main.MainInterface;
import org.columba.core.plugin.ConfigPluginHandler;
import org.columba.core.plugin.ThemePluginHandler;
import org.columba.core.util.GlobalResourceLoader;
import org.columba.core.xml.XmlElement;
import org.columba.mail.util.MailResourceLoader;

import com.jgoodies.forms.layout.FormLayout;

public class GeneralOptionsDialog extends JDialog implements ActionListener {

	// TODO: this dialog should make use of core i18n properties only
	private static final String RESOURCE_PATH = "org.columba.mail.i18n.dialog";

	// button panel
	JButton okButton;
	JButton cancelButton;
	JButton helpButton;

	// look and feel
	JLabel lfLabel;
	JComboBox lfComboBox;
	JButton lfButton;

	private String theme = null;
	private ThemePluginHandler handler;

	// fonts
	JCheckBox overwriteCheckBox;
	JLabel mainFontLabel;
	JLabel textFontLabel;
	JButton mainFontButton;
	JButton textFontButton;
	private Font mainFont;
	private Font textFont;

	// toolbar
	JLabel toolbarLabel;
	JComboBox toolbarComboBox;

	// language
	JLabel languageLabel;
	JComboBox languageComboBox;

	JFrame frame;

	ConfigPluginHandler configHandler;
	
	// ID of configuration plugin of this theme plugin
	String configID;

	public GeneralOptionsDialog(JFrame frame) {
		super(
			frame,
			MailResourceLoader.getString("dialog", "general", "dialog_title"),
			true);

		this.frame = frame;

		try {
			// get theme plugin-handler
			handler =
				(ThemePluginHandler) MainInterface.pluginManager.getHandler(
					"org.columba.core.theme");

		} catch (Exception ex) {
			ex.printStackTrace();
		}

		try {
			// get config plugin-handler
			configHandler =
				(ConfigPluginHandler) MainInterface.pluginManager.getHandler(
					"org.columba.core.config");

		} catch (Exception ex) {
			ex.printStackTrace();
		}

		initComponents();

		layoutComponents();

		updateComponents(true);

		pack();

		setLocationRelativeTo(null);

		setVisible(true);
	}

	public void updateComponents(boolean b) {
		XmlElement options = Config.get("options").getElement("/options");
		XmlElement gui = options.getElement("gui");
		XmlElement themeElement = gui.getElement("theme");

		XmlElement fonts = gui.getElement("fonts");
		if (fonts == null)
			fonts = gui.addSubElement("fonts");

		String overwrite = fonts.getAttribute("overwrite", "false");

		XmlElement mainFontElement = fonts.getElement("main");
		if (mainFontElement == null)
			mainFontElement = fonts.addSubElement("main");

		XmlElement textFontElement = fonts.getElement("text");
		if (textFontElement == null)
			textFontElement = fonts.addSubElement("text");

		GuiItem item = Config.getOptionsConfig().getGuiItem();
		//mainFont = item.getMainFont();
		//textFont = item.getTextFont();

		theme = themeElement.getAttribute("name");

		if (b) {

			// look and feel
			lfComboBox.setSelectedItem(theme);

			// fonts
			String mainName = mainFontElement.getAttribute("name", "Default");
			String mainSize = mainFontElement.getAttribute("size", "12");
			mainFont =
				new Font(mainName, Font.PLAIN, Integer.parseInt(mainSize));

			String textName = textFontElement.getAttribute("name", "Default");
			String textSize = textFontElement.getAttribute("size", "12");
			textFont =
				new Font(textName, Font.PLAIN, Integer.parseInt(textSize));

			mainFontButton.setText(mainName);
			mainFontButton.setFont(mainFont);
			textFontButton.setText(textName);
			textFontButton.setFont(textFont);

			if (overwrite.equals("true"))
				overwriteCheckBox.setSelected(true);
			else {
				overwriteCheckBox.setSelected(false);
				// disable button, too
				textFontButton.setEnabled(false);
				mainFontButton.setEnabled(false);
			}

			/*
			actionPerformed(
				new ActionEvent(
					overwriteCheckBox,
					ActionEvent.ACTION_PERFORMED,
					null));
			*/

			// language
			Locale[] available = GlobalResourceLoader.getAvailableLocales();
			languageComboBox.setModel(new DefaultComboBoxModel(available));

			// select Locale in ComboBox
			for (int i = 0; i < available.length; i++) {
				if (available[i].equals(Locale.getDefault())) {
					languageComboBox.setSelectedIndex(i);
					break;
				}
			}

			boolean withIcon = false;
			if (item.getBoolean("toolbar", "enable_icon"))
				withIcon = true;
			boolean enableText = false;
			if (item.getBoolean("toolbar", "enable_text"))
				enableText = true;
			boolean alignment = false;
			if (item.getBoolean("toolbar", "text_position"))
				alignment = true;

			int state = -1;
			if (withIcon && !enableText)
				state = 0;
			else if (!withIcon && enableText)
				state = 1;
			else if (withIcon && enableText) {
				if (alignment)
					state = 2;
				else
					state = 3;

				toolbarComboBox.setSelectedIndex(state);

			}
		} else {

			// fonts
			textFontElement.addAttribute("name", getTextFont().getName());
			textFontElement.addAttribute(
				"size",
				new Integer(getTextFont().getSize()).toString());

			mainFontElement.addAttribute("name", getMainFont().getName());
			mainFontElement.addAttribute(
				"size",
				new Integer(getMainFont().getSize()).toString());

			fonts.addAttribute(
				"overwrite",
				Boolean.toString(overwriteCheckBox.isSelected()));

			// notify all listeners
			// @see org.columba.core.gui.util.FontProperties
			// @see org.columba.mail.gui.message.BodyTextViewer
			// @see org.columba.mail.gui.composer.text.TextEditorController
			fonts.notifyObservers();

			// look and feel
			String selection = (String) lfComboBox.getSelectedItem();

			themeElement.addAttribute("name", selection);

			// get language configuration
			XmlElement locale =
				Config.get("options").getElement("/options/locale");

			// set language config based on selected item
			Locale l = (Locale) languageComboBox.getSelectedItem();
			locale.addAttribute("language", l.getLanguage());
			locale.addAttribute("country", l.getCountry());
			locale.addAttribute("variant", l.getVariant());

			int state = toolbarComboBox.getSelectedIndex();

			if (state == 0) {
				item.set("toolbar", "enable_text", Boolean.FALSE.toString());
				item.set("toolbar", "enable_icon", Boolean.TRUE.toString());
			} else if (state == 1) {
				item.set("toolbar", "enable_text", Boolean.TRUE.toString());
				item.set("toolbar", "enable_icon", Boolean.FALSE.toString());
			} else if (state >= 2) {
				item.set("toolbar", "enable_text", Boolean.TRUE.toString());
				item.set("toolbar", "enable_icon", Boolean.TRUE.toString());

				if (state == 2)
					item.set(
						"toolbar",
						"text_position",
						Boolean.TRUE.toString());
				else
					item.set(
						"toolbar",
						"text_position",
						Boolean.FALSE.toString());

			}
		}

	}

	protected void layoutComponents() {
		JPanel contentPane = new JPanel(new BorderLayout());
		setContentPane(contentPane);

		// Create a FormLayout instance. 
		FormLayout layout =
			new FormLayout("12dlu, pref, 3dlu, max(40dlu;pref), 3dlu, pref",
			// 3 columns
	"");

		// create a form builder
		DefaultFormBuilder builder = new DefaultFormBuilder(layout);

		// create EmptyBorder between components and dialog-frame 
		builder.setDefaultDialogBorder();

		// skip the first column
		builder.setLeadingColumnOffset(1);

		// Add components to the panel:

		// TODO: LOCALIZE
		builder.appendSeparator("General");
		builder.nextLine();

		builder.append(languageLabel);
		builder.append(languageComboBox, 3);
		builder.nextLine();

		builder.append(toolbarLabel);
		builder.append(toolbarComboBox, 3);
		builder.nextLine();

		// TODO: LOCALIZE
		builder.appendSeparator("Look And Feel");
		builder.nextLine();

		builder.append(lfLabel, lfComboBox, lfButton);
		builder.nextLine();

		// TODO: LOCALIZE
		builder.appendSeparator("Fonts");
		builder.nextLine();

		builder.append(overwriteCheckBox, 5);
		builder.nextLine();

		builder.append(mainFontLabel);
		builder.append(mainFontButton, 3);
		builder.nextLine();

		builder.append(textFontLabel);
		builder.append(textFontButton, 3);
		builder.nextLine();

		contentPane.add(builder.getPanel(), BorderLayout.CENTER);

		// init bottom panel with OK, Cancel buttons

		JPanel bottomPanel = new JPanel(new BorderLayout(0, 0));
		bottomPanel.setBorder(new SingleSideEtchedBorder(SwingConstants.TOP));
		JPanel buttonPanel = new JPanel(new GridLayout(1, 2, 5, 0));
		buttonPanel.setBorder(BorderFactory.createEmptyBorder(12, 17, 11, 11));

		buttonPanel.add(okButton);

		buttonPanel.add(cancelButton);
		bottomPanel.add(buttonPanel, BorderLayout.EAST);
		contentPane.add(bottomPanel, BorderLayout.SOUTH);

		getRootPane().setDefaultButton(okButton);
		getRootPane().registerKeyboardAction(
			this,
			"CANCEL",
			KeyStroke.getKeyStroke(KeyEvent.VK_ESCAPE, 0),
			JComponent.WHEN_IN_FOCUSED_WINDOW);
	}

	protected void initComponents() {

		lfLabel = new JLabel("Look and Feel:");
		String[] plugins = handler.getPluginIdList();
		lfComboBox = new JComboBox(plugins);
		lfComboBox.setRenderer(new ThemeComboBoxRenderer());
		lfComboBox.setActionCommand("THEME");
		lfComboBox.addActionListener(this);

		// TODO: LOCALIZE
		lfButton = new JButton("Options...");
		lfButton.setActionCommand("THEME_OPTIONS");
		lfButton.addActionListener(this);

		overwriteCheckBox =
			new JCheckBox(
				GlobalResourceLoader.getString(
					RESOURCE_PATH,
					"general",
					"overwrite_main_font"));
		overwriteCheckBox.addActionListener(this);
		mainFontLabel =
			new JLabel(
				GlobalResourceLoader.getString(
					RESOURCE_PATH,
					"general",
					"main_font"));
		textFontLabel =
			new JLabel(
				GlobalResourceLoader.getString(
					RESOURCE_PATH,
					"general",
					"text_font"));

		mainFontButton = new JButton("main font");
		mainFontButton.addActionListener(this);
		textFontButton = new JButton("text font");
		textFontButton.addActionListener(this);

		toolbarLabel = new JLabel("Toolbar Style:");
		toolbarComboBox =
			new JComboBox(
				new String[] {
					MailResourceLoader.getString(
						"dialog",
						"general",
						"toolbar_icons"),
					MailResourceLoader.getString(
						"dialog",
						"general",
						"toolbar_text"),
					MailResourceLoader.getString(
						"dialog",
						"general",
						"toolbar_below"),
					MailResourceLoader.getString(
						"dialog",
						"general",
						"toolbar_beside")});
		toolbarLabel.setLabelFor(toolbarComboBox);

		languageLabel =
			new JLabel(
				MailResourceLoader.getString("dialog", "general", "locale"));
		languageComboBox = new JComboBox();
		languageComboBox.setRenderer(new DefaultListCellRenderer() {
			public Component getListCellRendererComponent(
				JList list,
				Object value,
				int index,
				boolean isSelected,
				boolean hasFocus) {

				JLabel label =
					(JLabel) super.getListCellRendererComponent(
						list,
						value,
						index,
						isSelected,
						hasFocus);
				label.setText(((Locale) value).getDisplayName());
				return label;
			}
		});

		// button panel

		okButton =
			new ButtonWithMnemonic(
				MailResourceLoader.getString("global", "ok"));
		okButton.setActionCommand("OK");
		okButton.addActionListener(this);

		cancelButton =
			new ButtonWithMnemonic(
				MailResourceLoader.getString("global", "cancel"));
		cancelButton.setActionCommand("CANCEL");
		cancelButton.addActionListener(this);

		helpButton =
			new ButtonWithMnemonic(
				MailResourceLoader.getString("global", "help"));
		helpButton.setActionCommand("HELP");
		helpButton.addActionListener(this);

	}

	public void actionPerformed(ActionEvent event) {
		String action = event.getActionCommand();
		if (action == null)
			return;

		Object source = event.getSource();

		if (action.equals("OK")) {

			setVisible(false);

			updateComponents(false);

			// TODO until we can get all the settings update immediately
			// we just open a message box, telling the user to restart

			// switch to new theme
			ThemeSwitcher.setTheme();
			// notify frame to update
			ThemeSwitcher.updateFrame(frame);

			// set fonts
			FontProperties.setFont();

			/*
			JOptionPane.showInternalMessageDialog(
				frame,
				"You have to restart Columba for the changes to take effect!");
			*/

		} else if (action.equals("CANCEL")) {

			setVisible(false);

		} else if (action.equals("THEME")) {
			// theme selection changed
			String theme = (String) lfComboBox.getSelectedItem();

			configID = handler.getAttribute(theme, "config");

			if (configID == null)
				lfButton.setEnabled(false);
			else {
				lfButton.setEnabled(true);
			}

		} else if (action.equals("THEME_OPTIONS")) {
			String theme = (String) lfComboBox.getSelectedItem();
			new ConfigurationDialog(configID);
		}

		if (source == mainFontButton) {
			FontSelectionDialog fontDialog = new FontSelectionDialog(null);
			if (fontDialog.showDialog() == FontSelectionDialog.APPROVE_OPTION) {
				mainFont = fontDialog.getSelectedFont();
				mainFontButton.setFont(mainFont);
				mainFontButton.setText(mainFont.getFontName());
			}

		} else if (source == textFontButton) {
			FontSelectionDialog fontDialog = new FontSelectionDialog(null);
			if (fontDialog.showDialog() == FontSelectionDialog.APPROVE_OPTION) {
				textFont = fontDialog.getSelectedFont();
				textFontButton.setFont(textFont);
				textFontButton.setText(textFont.getFontName());
			}
		} else if (source == overwriteCheckBox) {
			boolean enabled = overwriteCheckBox.isSelected();
			mainFontLabel.setEnabled(enabled);
			mainFontButton.setEnabled(enabled);
			textFontLabel.setEnabled(enabled);
			textFontButton.setEnabled(enabled);
		}
	}

	public Font getMainFont() {
		return mainFont;
	}

	public Font getTextFont() {
		return textFont;
	}
}
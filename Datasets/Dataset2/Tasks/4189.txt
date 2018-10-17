JFrame frame = m[i].getView().getFrame();

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
import java.awt.Font;
import java.awt.GridLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyEvent;
import java.util.Locale;
import java.util.Properties;

import javax.swing.BorderFactory;
import javax.swing.DefaultComboBoxModel;
import javax.swing.JButton;
import javax.swing.JCheckBox;
import javax.swing.JComboBox;
import javax.swing.JComponent;
import javax.swing.JDialog;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.KeyStroke;
import javax.swing.SwingConstants;

import net.javaprog.ui.wizard.plaf.basic.SingleSideEtchedBorder;

import org.columba.core.config.GuiItem;
import org.columba.core.gui.frame.FrameMediator;
import org.columba.core.gui.plugin.ConfigurationDialog;
import org.columba.core.gui.themes.ThemeSwitcher;
import org.columba.core.gui.util.ButtonWithMnemonic;
import org.columba.core.gui.util.CheckBoxWithMnemonic;
import org.columba.core.gui.util.DefaultFormBuilder;
import org.columba.core.gui.util.FontProperties;
import org.columba.core.gui.util.FontSelectionDialog;
import org.columba.core.gui.util.LabelWithMnemonic;
import org.columba.core.help.HelpManager;
import org.columba.core.main.MainInterface;
import org.columba.core.plugin.ConfigPluginHandler;
import org.columba.core.plugin.ThemePluginHandler;
import org.columba.core.util.GlobalResourceLoader;
import org.columba.core.xml.XmlElement;

import com.jgoodies.forms.layout.FormLayout;

/**
 * Shows a dialog for managing general options such as font settings.
 */
public class GeneralOptionsDialog extends JDialog implements ActionListener {
    private static final String RESOURCE_PATH = "org.columba.core.i18n.dialog";

    // button panel
    protected JButton okButton;
    protected JButton cancelButton;
    protected JButton helpButton;

    // look and feel
    protected JLabel lfLabel;
    protected JComboBox lfComboBox;
    protected JButton lfButton;
    private String theme = null;
    private ThemePluginHandler handler;

    // fonts
    protected JCheckBox overwriteCheckBox;
    protected JLabel mainFontLabel;
    protected JLabel textFontLabel;
    protected JButton mainFontButton;
    protected JButton textFontButton;
    private Font mainFont;
    private Font textFont;

    // toolbar
    protected JLabel toolbarLabel;
    protected JComboBox toolbarComboBox;

    // language
    protected JLabel languageLabel;
    protected JComboBox languageComboBox;
    protected JFrame frame;
    protected ConfigPluginHandler configHandler;
    
    // HTTP proxy
    protected JLabel proxyLabel;
    protected JButton proxyButton;
    protected String proxyHost;
    protected int proxyPort;

    // ID of configuration plugin of this theme plugin
    protected String configID;

    public GeneralOptionsDialog(JFrame frame) {
        super(frame,
            GlobalResourceLoader.getString(RESOURCE_PATH, "general",
                "dialog_title"), true);

        this.frame = frame;

        try {
            // get theme plugin-handler
            handler = (ThemePluginHandler) MainInterface.pluginManager.getHandler(
                    "org.columba.core.theme");
        } catch (Exception ex) {
            ex.printStackTrace();
        }

        try {
            // get config plugin-handler
            configHandler = (ConfigPluginHandler) MainInterface.pluginManager.getHandler(
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
        XmlElement options = MainInterface.config.get("options").getElement("/options");
        XmlElement gui = options.getElement("gui");
        XmlElement themeElement = gui.getElement("theme");

        XmlElement fonts = gui.getElement("fonts");
        if (fonts == null) {
            fonts = gui.addSubElement("fonts");
        }

        String overwrite = fonts.getAttribute("overwrite", "false");

        XmlElement mainFontElement = fonts.getElement("main");
        if (mainFontElement == null) {
            mainFontElement = fonts.addSubElement("main");
        }

        XmlElement textFontElement = fonts.getElement("text");
        if (textFontElement == null) {
            textFontElement = fonts.addSubElement("text");
        }

        GuiItem item = MainInterface.config.getOptionsConfig().getGuiItem();

        //mainFont = item.getMainFont();
        //textFont = item.getTextFont();
        theme = themeElement.getAttribute("name");

        if (b) {
            // look and feel
            lfComboBox.setSelectedItem(theme);

            // fonts
            String mainName = mainFontElement.getAttribute("name", "Default");
            String mainSize = mainFontElement.getAttribute("size", "12");
            mainFont = new Font(mainName, Font.PLAIN, Integer.parseInt(mainSize));

            String textName = textFontElement.getAttribute("name", "Default");
            String textSize = textFontElement.getAttribute("size", "12");
            textFont = new Font(textName, Font.PLAIN, Integer.parseInt(textSize));

            mainFontButton.setText(mainName);
            mainFontButton.setFont(mainFont);
            textFontButton.setText(textName);
            textFontButton.setFont(textFont);

            if (overwrite.equals("true")) {
                overwriteCheckBox.setSelected(true);
            } else {
                overwriteCheckBox.setSelected(false);

                // disable button, too
                textFontButton.setEnabled(false);
                textFontLabel.setEnabled(false);
                mainFontButton.setEnabled(false);
                mainFontLabel.setEnabled(false);
            }

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

            boolean enableText = false;
            if (item.getBoolean("toolbar", "enable_text")) {
                enableText = true;
            }

            boolean alignment = false;
            if (item.getBoolean("toolbar", "text_position")) {
                alignment = true;
            }

            int state = 0;
            if (enableText) {
                if (alignment) {
                    state = 1;
                } else {
                    state = 2;
                }
                toolbarComboBox.setSelectedIndex(state);
            }
            
            proxyHost = System.getProperty("http.proxyHost");
            String proxyPortString = System.getProperty("http.proxyPort", "-1");
            proxyPort = Integer.parseInt(proxyPortString);
            updateProxyButtonText();
        } else {
            // fonts
            textFontElement.addAttribute("name", getTextFont().getName());
            textFontElement.addAttribute("size",
                new Integer(getTextFont().getSize()).toString());

            mainFontElement.addAttribute("name", getMainFont().getName());
            mainFontElement.addAttribute("size",
                new Integer(getMainFont().getSize()).toString());

            fonts.addAttribute("overwrite",
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
            XmlElement locale = MainInterface.config.get("options").getElement("/options/locale");

            // set language config based on selected item
            Locale l = (Locale) languageComboBox.getSelectedItem();
            locale.addAttribute("language", l.getLanguage());
            locale.addAttribute("country", l.getCountry());
            locale.addAttribute("variant", l.getVariant());

            int state = toolbarComboBox.getSelectedIndex();
            if (state == 0) {
                item.set("toolbar", "enable_text", Boolean.FALSE.toString());
            } else {
                item.set("toolbar", "enable_text", Boolean.TRUE.toString());
                if (state == 1) {
                    item.set("toolbar", "text_position", Boolean.TRUE.toString());
                } else {
                    item.set("toolbar", "text_position",
                        Boolean.FALSE.toString());
                }
            }
            
            XmlElement proxy = options.getElement("proxy");
            if (proxyHost != null && proxyPort > 0) {
                System.setProperty("http.proxyHost", proxyHost);
                System.setProperty("http.proxyPort", Integer.toString(proxyPort));
                if (proxy == null) {
                    proxy = options.addSubElement("proxy");
                }
                proxy.addAttribute("host", proxyHost);
                proxy.addAttribute("port", Integer.toString(proxyPort));
            } else {
                Properties properties = System.getProperties();
                properties.remove("http.proxyHost");
                properties.remove("http.proxyPort");
                if (proxy != null) {
                    options.removeElement(proxy);
                }
            }
        }
    }

    protected void layoutComponents() {
        JPanel contentPane = new JPanel(new BorderLayout());
        setContentPane(contentPane);

        // Create a FormLayout instance. 
        FormLayout layout = new FormLayout("12dlu, pref, 3dlu, max(40dlu;pref), 3dlu, pref",
                
            // 3 columns
            "");

        // create a form builder
        DefaultFormBuilder builder = new DefaultFormBuilder(layout);

        // create EmptyBorder between components and dialog-frame 
        builder.setDefaultDialogBorder();

        // skip the first column
        builder.setLeadingColumnOffset(1);

        // Add components to the panel:
        builder.appendSeparator(GlobalResourceLoader.getString(RESOURCE_PATH,
                "general", "general"));
        builder.nextLine();

        builder.append(languageLabel);
        builder.append(languageComboBox, 3);
        builder.nextLine();

        builder.append(lfLabel, lfComboBox, lfButton);
        builder.nextLine();

        builder.append(toolbarLabel);
        builder.append(toolbarComboBox, 3);
        builder.nextLine();
        
        builder.append(proxyLabel);
        builder.append(proxyButton, 3);
        builder.nextLine();

        builder.appendSeparator(GlobalResourceLoader.getString(RESOURCE_PATH,
                "general", "fonts"));
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

        JPanel buttonPanel = new JPanel(new GridLayout(1, 3, 6, 0));
        buttonPanel.setBorder(BorderFactory.createEmptyBorder(12, 12, 12, 12));

        buttonPanel.add(okButton);
        buttonPanel.add(cancelButton);
        buttonPanel.add(helpButton);

        bottomPanel.add(buttonPanel, BorderLayout.EAST);
        contentPane.add(bottomPanel, BorderLayout.SOUTH);

        getRootPane().setDefaultButton(okButton);
        getRootPane().registerKeyboardAction(this, "CANCEL",
            KeyStroke.getKeyStroke(KeyEvent.VK_ESCAPE, 0),
            JComponent.WHEN_IN_FOCUSED_WINDOW);
    }

    protected void initComponents() {
        lfLabel = new LabelWithMnemonic(GlobalResourceLoader.getString(
                    RESOURCE_PATH, "general", "look_feel"));

        String[] plugins = handler.getPluginIdList();
        lfComboBox = new JComboBox(plugins);
        lfComboBox.setRenderer(new ThemeComboBoxRenderer());
        lfComboBox.setActionCommand("THEME");
        lfComboBox.addActionListener(this);
        lfLabel.setLabelFor(lfComboBox);

        lfButton = new ButtonWithMnemonic(GlobalResourceLoader.getString(
                    RESOURCE_PATH, "general", "look_feel_options"));
        lfButton.setActionCommand("THEME_OPTIONS");
        lfButton.addActionListener(this);

        overwriteCheckBox = new CheckBoxWithMnemonic(GlobalResourceLoader.getString(
                    RESOURCE_PATH, "general", "override_fonts"));
        overwriteCheckBox.addActionListener(this);

        mainFontLabel = new LabelWithMnemonic(GlobalResourceLoader.getString(
                    RESOURCE_PATH, "general", "main_font"));
        mainFontButton = new JButton("main font");
        mainFontButton.addActionListener(this);
        mainFontLabel.setLabelFor(mainFontButton);

        textFontLabel = new LabelWithMnemonic(GlobalResourceLoader.getString(
                    RESOURCE_PATH, "general", "text_font"));
        textFontButton = new JButton("text font");
        textFontButton.addActionListener(this);
        textFontLabel.setLabelFor(textFontButton);

        toolbarLabel = new LabelWithMnemonic(GlobalResourceLoader.getString(
                    RESOURCE_PATH, "general", "toolbar"));
        toolbarComboBox = new JComboBox(new String[] {
                    GlobalResourceLoader.getString(RESOURCE_PATH, "general",
                        "toolbar_icons"),
                    GlobalResourceLoader.getString(RESOURCE_PATH, "general",
                        "toolbar_below"),
                    GlobalResourceLoader.getString(RESOURCE_PATH, "general",
                        "toolbar_beside")
                });
        toolbarLabel.setLabelFor(toolbarComboBox);

        languageLabel = new LabelWithMnemonic(GlobalResourceLoader.getString(
                    RESOURCE_PATH, "general", "locale"));
        languageComboBox = new JComboBox();
        languageLabel.setLabelFor(languageComboBox);
        languageComboBox.setRenderer(new LocaleComboBoxRenderer());
        
        proxyLabel = new LabelWithMnemonic(GlobalResourceLoader.getString(
                    RESOURCE_PATH, "general", "proxy"));
        proxyButton = new JButton();
        proxyButton.addActionListener(this);
        proxyLabel.setLabelFor(proxyButton);

        // button panel
        okButton = new ButtonWithMnemonic(GlobalResourceLoader.getString("",
                    "global", "ok"));
        okButton.setActionCommand("OK");
        okButton.addActionListener(this);

        cancelButton = new ButtonWithMnemonic(GlobalResourceLoader.getString(
                    "", "global", "cancel"));
        cancelButton.setActionCommand("CANCEL");
        cancelButton.addActionListener(this);

        helpButton = new ButtonWithMnemonic(GlobalResourceLoader.getString("",
                    "global", "help"));

        // associate with JavaHelp
        HelpManager.getHelpManager().enableHelpOnButton(helpButton,
            "configuring_columba_8");
        HelpManager.getHelpManager().enableHelpKey(getRootPane(),
            "configuring_columba_8");
    }

    public void actionPerformed(ActionEvent event) {
        String action = event.getActionCommand();

        if (action.equals("OK")) {
            setVisible(false);

            updateComponents(false);

            // TODO until we can get all the settings update immediately
            // we just open a message box, telling the user to restart
            // switch to new theme
            ThemeSwitcher.setTheme();

            // notify frame to update
            FrameMediator[] m = MainInterface.frameModel.getOpenFrames();
            for ( int i=0; i<m.length; i++) {
                JFrame frame = (JFrame) m[i].getBaseView();
                ThemeSwitcher.updateFrame(frame);
            }
            

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

            lfButton.setEnabled(configID != null);
        } else if (action.equals("THEME_OPTIONS")) {
            String theme = (String) lfComboBox.getSelectedItem();
            new ConfigurationDialog(configID);
        }

        Object source = event.getSource();
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
        } else if (source == proxyButton) {
            ProxyConfigurationDialog dialog = new ProxyConfigurationDialog(this);
            dialog.setProxyHost(proxyHost);
            dialog.setProxyPort(proxyPort);
            if (dialog.showDialog() == ProxyConfigurationDialog.APPROVE_OPTION) {
                proxyHost = dialog.getProxyHost();
                proxyPort = dialog.getProxyPort();
                updateProxyButtonText();
            }
        }
    }
    
    protected void updateProxyButtonText() {
        if (proxyHost != null) {
            proxyButton.setText(proxyHost + ":" + Integer.toString(proxyPort));
        } else {
            proxyButton.setText(GlobalResourceLoader.getString(
                    RESOURCE_PATH, "proxy", "no_proxy"));
        }
    }

    public Font getMainFont() {
        return mainFont;
    }

    public Font getTextFont() {
        return textFont;
    }
}
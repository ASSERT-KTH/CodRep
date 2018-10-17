d.showDialog(MailResourceLoader.getString("dialog", "error", "mailimport"));

// The contents of this file are subject to the Mozilla Public License Version
// 1.1
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
//The Initial Developers of the Original Code are Frederik Dietz and Timo
// Stich.
//Portions created by Frederik Dietz and Timo Stich are Copyright (C) 2003.
//
//All Rights Reserved.
package org.columba.mail.gui.config.mailboximport;

import net.javaprog.ui.wizard.AbstractStep;
import net.javaprog.ui.wizard.DataModel;
import net.javaprog.ui.wizard.DefaultDataLookup;

import org.columba.core.gui.util.MultiLineLabel;
import org.columba.core.gui.util.NotifyDialog;
import org.columba.core.main.MainInterface;
import org.columba.core.plugin.PluginHandlerNotFoundException;

import org.columba.mail.folder.mailboximport.DefaultMailboxImporter;
import org.columba.mail.plugin.ImportPluginHandler;
import org.columba.mail.util.MailResourceLoader;

import java.awt.BorderLayout;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.Insets;

import java.lang.reflect.Method;

import javax.swing.JComponent;
import javax.swing.JList;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.event.ListSelectionEvent;
import javax.swing.event.ListSelectionListener;


class PluginStep extends AbstractStep implements ListSelectionListener {
    protected DataModel data;
    protected MultiLineLabel descriptionLabel;
    private ImportPluginHandler pluginHandler;

    public PluginStep(DataModel data) {
        super(MailResourceLoader.getString("dialog", "mailboximport", "plugin"),
            MailResourceLoader.getString("dialog", "mailboximport",
                "plugin_description"));
        this.data = data;

        try {
            pluginHandler = (ImportPluginHandler) MainInterface.pluginManager.getHandler(
                    "org.columba.mail.import");
        } catch (PluginHandlerNotFoundException ex) {
            NotifyDialog d = new NotifyDialog();

            //show neat error message here
            d.showDialog(ex);

            return;
        }
    }

    protected JComponent createComponent() {
        descriptionLabel = new MultiLineLabel("description");
        descriptionLabel.setWrapStyleWord(true);
        descriptionLabel.setLineWrap(true);

        JList list = new JList(((ImportPluginHandler) data.getData(
                    "Plugin.handler")).getPluginIdList());
        list.setCellRenderer(new PluginListCellRenderer());

        JComponent component = new JPanel(new BorderLayout(0, 30));
        component.add(new MultiLineLabel(MailResourceLoader.getString(
                    "dialog", "mailboximport", "plugin_text")),
            BorderLayout.NORTH);

        JPanel middlePanel = new JPanel();
        middlePanel.setAlignmentX(1);

        GridBagLayout layout = new GridBagLayout();
        middlePanel.setLayout(layout);

        Method method = null;

        try {
            method = list.getClass().getMethod("getSelectedValue", null);
        } catch (NoSuchMethodException nsme) {
        }

        data.registerDataLookup("Plugin.ID",
            new DefaultDataLookup(list, method, null));
        list.addListSelectionListener(this);
        list.setSelectedIndex(0);

        JScrollPane scrollPane = new JScrollPane(list);

        //scrollPane.setPreferredSize( new Dimension(200,200) );
        GridBagConstraints c = new GridBagConstraints();
        c.anchor = GridBagConstraints.NORTHWEST;
        c.gridx = 0;
        c.fill = GridBagConstraints.BOTH;
        c.weightx = 0.4;

        //c.gridwidth = GridBagConstraints.RELATIVE;
        c.weighty = 1.0;
        layout.setConstraints(scrollPane, c);
        middlePanel.add(scrollPane);

        c.gridwidth = GridBagConstraints.REMAINDER;
        c.weightx = 0.6;
        c.gridx = 1;
        c.anchor = GridBagConstraints.NORTHWEST;
        c.insets = new Insets(0, 10, 0, 0);

        JScrollPane scrollPane2 = new JScrollPane(descriptionLabel);

        //scrollPane2.setPreferredSize( new Dimension(200,100) );
        layout.setConstraints(scrollPane2, c);
        middlePanel.add(scrollPane2);
        component.add(middlePanel);

        return component;
    }

    public void valueChanged(ListSelectionEvent event) {
        try {
            //adjust description field
            DefaultMailboxImporter importer = (DefaultMailboxImporter) pluginHandler.getPlugin((String) data.getData(
                        "Plugin.ID"), null);
            String description = importer.getDescription();
            descriptionLabel.setText(description);
        } catch (Exception e) {
            NotifyDialog d = new NotifyDialog();

            //show neat error message here
            d.showDialog(e);
        }
    }

    public void prepareRendering() {
    }
}
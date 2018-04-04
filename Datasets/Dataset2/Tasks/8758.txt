destinationFolder = (IMailFolder) dialog.getSelectedFolder();

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
package org.columba.mail.gui.config.mailboximport;

import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.File;

import javax.swing.Box;
import javax.swing.BoxLayout;
import javax.swing.JButton;
import javax.swing.JComponent;
import javax.swing.JFileChooser;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.SwingUtilities;

import net.javaprog.ui.wizard.AbstractStep;
import net.javaprog.ui.wizard.DataLookup;
import net.javaprog.ui.wizard.DataModel;

import org.columba.core.gui.frame.FrameMediator;
import org.columba.core.gui.util.LabelWithMnemonic;
import org.columba.core.gui.util.MultiLineLabel;
import org.columba.core.gui.util.WizardTextField;
import org.columba.mail.folder.IMailFolder;
import org.columba.mail.gui.tree.util.SelectFolderDialog;
import org.columba.mail.util.MailResourceLoader;


class LocationStep extends AbstractStep implements ActionListener {
    protected File[] sourceFiles;
    protected IMailFolder destinationFolder;
    protected JButton sourceButton;
    protected JButton destinationButton;
    protected FrameMediator mediator;
    
    public LocationStep(FrameMediator mediator, DataModel data) {
        super(MailResourceLoader.getString("dialog", "mailboximport", "location"),
            MailResourceLoader.getString("dialog", "mailboximport",
                "location_description"));
        this.mediator = mediator;
        
        data.registerDataLookup("Location.source",
            new DataLookup() {
                public Object lookupData() {
                    return sourceFiles;
                }
            });
        data.registerDataLookup("Location.destination",
            new DataLookup() {
                public Object lookupData() {
                    return destinationFolder;
                }
            });
        setCanGoNext(false);
    }

    protected JComponent createComponent() {
        JComponent component = new JPanel();
        component.setLayout(new BoxLayout(component, BoxLayout.Y_AXIS));
        component.add(new MultiLineLabel(MailResourceLoader.getString(
                    "dialog", "mailboximport", "location_text")));
        component.add(Box.createVerticalStrut(40));

        WizardTextField middlePanel = new WizardTextField();

        LabelWithMnemonic sourceLabel = new LabelWithMnemonic(MailResourceLoader.getString(
                    "dialog", "mailboximport", "source"));
        middlePanel.addLabel(sourceLabel);
        sourceButton = new JButton("...");
        sourceLabel.setLabelFor(sourceButton);
        sourceButton.addActionListener(this);
        middlePanel.addTextField(sourceButton);
        middlePanel.addExample(new JLabel());

        LabelWithMnemonic destinationLabel = new LabelWithMnemonic(MailResourceLoader.getString(
                    "dialog", "mailboximport", "destination"));
        middlePanel.addLabel(destinationLabel);
        destinationButton = new JButton("...");
        destinationLabel.setLabelFor(destinationButton);
        destinationButton.addActionListener(this);
        middlePanel.addTextField(destinationButton);
        middlePanel.addExample(new JLabel(MailResourceLoader.getString(
                    "dialog", "mailboximport", "explanation")));
        component.add(middlePanel);

        return component;
    }

    public void actionPerformed(ActionEvent e) {
        Object source = e.getSource();

        if (source == sourceButton) {
            JFileChooser fc = new JFileChooser();
            fc.setMultiSelectionEnabled(true);
            fc.setFileSelectionMode(JFileChooser.FILES_AND_DIRECTORIES);
            fc.setFileHidingEnabled(false);

            if (fc.showOpenDialog(getComponent()) == JFileChooser.APPROVE_OPTION) {
                sourceFiles = fc.getSelectedFiles();

                if (sourceFiles.length > 1) {
                    sourceButton.setText(sourceFiles.length + " " +
                        MailResourceLoader.getString("dialog", "mailboximport",
                            "files"));

                    StringBuffer toolTip = new StringBuffer();
                    toolTip.append("<html><body>");

                    int i = 0;

                    for (; i < (sourceFiles.length - 1); i++) {
                        toolTip.append(sourceFiles[i].getPath());
                        toolTip.append("<br>");
                    }

                    toolTip.append(sourceFiles[i].getPath());
                    toolTip.append("</body></html>");
                    sourceButton.setToolTipText(toolTip.toString());
                } else {
                    sourceButton.setText(sourceFiles[0].getPath());
                    sourceButton.setToolTipText(null);
                }

                updateCanFinish();
            }
        } else if (source == destinationButton) {
            SelectFolderDialog dialog = new SelectFolderDialog(mediator);

            if (dialog.success()) {
                destinationFolder = dialog.getSelectedFolder();
                destinationButton.setText(destinationFolder.getTreePath());
                updateCanFinish();
            }
        }
    }

    protected void updateCanFinish() {
        setCanFinish((sourceFiles != null) && (destinationFolder != null));
    }

    public void prepareRendering() {
        SwingUtilities.invokeLater(new Runnable() {
                public void run() {
                    sourceButton.requestFocus();
                }
            });
    }
}
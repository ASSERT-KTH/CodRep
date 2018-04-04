icon.setIcon(ImageLoader.getMiscIcon("out-of-office-48.png"));

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
package org.columba.core.shutdown;

import java.awt.BorderLayout;
import java.awt.Dimension;
import java.awt.Font;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

import javax.swing.BorderFactory;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JProgressBar;
import javax.swing.Timer;

import org.columba.core.resourceloader.GlobalResourceLoader;
import org.columba.core.resourceloader.ImageLoader;


/**
 * Dialog shown while closing Columba.
 * <p>
 * Waits two seconds until it is visible.
 *
 * @author fdietz
 */
public class ShutdownDialog extends JFrame implements ActionListener {
    protected static final String RESOURCE_PATH = "org.columba.core.i18n.dialog";
    private JProgressBar progressBar;
    private Timer timer;

    public ShutdownDialog() throws Exception{
        super(GlobalResourceLoader.getString(RESOURCE_PATH, "session",
                "exit_title"));

        JLabel icon = new JLabel();
        icon.setIcon(ImageLoader.getImageIcon("out-of-office-48.png"));

        JLabel text = new JLabel(GlobalResourceLoader.getString(RESOURCE_PATH,
                    "session", "exit_msg"));
        text.setFont(text.getFont().deriveFont(Font.BOLD));

        JPanel panel = new JPanel();

        panel.setLayout(new BorderLayout());

        icon.setBorder(BorderFactory.createEmptyBorder(12, 12, 6, 12));
        text.setBorder(BorderFactory.createEmptyBorder(0, 6, 12, 12));

        progressBar = new JProgressBar();
        progressBar.setIndeterminate(true);
        progressBar.setPreferredSize(new Dimension(250, 20));

        JPanel bottomPanel = new JPanel(new BorderLayout());
        bottomPanel.setBorder(BorderFactory.createEmptyBorder(0, 12, 12, 12));
        bottomPanel.add(progressBar, BorderLayout.CENTER);

        getContentPane().setLayout(new BorderLayout());

        getContentPane().add(panel, BorderLayout.CENTER);

        getContentPane().add(icon, BorderLayout.WEST);

        getContentPane().add(bottomPanel, BorderLayout.SOUTH);

        panel.add(text, BorderLayout.SOUTH);

        pack();

        setLocationRelativeTo(null);

        // wait for 2 seconds until the dialog is openened
        timer = new Timer(2 * 1000, this);
        timer.start();
    }

    /**
 * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
 */
    public void actionPerformed(ActionEvent arg0) {
        setVisible(true);
        timer.stop();
    }

    public void close() {
        timer.stop();

        if (isVisible()) {
            setVisible(false);
        }
    }
}
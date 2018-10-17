if (true) {

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

package org.columba.core.gui.util;

import org.columba.core.main.MainInterface;
import org.columba.core.util.GlobalResourceLoader;

import org.columba.mail.gui.util.AddressLabel;
import org.columba.mail.gui.util.URLLabel;

import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyEvent;

import java.net.MalformedURLException;
import java.net.URL;

import java.text.NumberFormat;

import javax.swing.*;

public class AboutDialog extends JDialog implements ActionListener {
    public static final String CMD_CLOSE = "CLOSE";
    private static final String RESOURCE_BUNDLE_PATH = "org.columba.core.i18n.dialog";
    protected static AboutDialog instance;

    protected AboutDialog() {
        super((JFrame)null, GlobalResourceLoader.getString(
                    RESOURCE_BUNDLE_PATH, "about", "title") +
                MainInterface.version);

        JTabbedPane tabbedPane = new JTabbedPane();
        tabbedPane.setFocusable(false);

        JPanel authorPanel = new JPanel(new GridBagLayout());
        authorPanel.setBorder(BorderFactory.createEmptyBorder(12, 12, 11, 11));

        GridBagConstraints c = new GridBagConstraints();
        
        JLabel imageLabel = new JLabel(ImageLoader.getImageIcon("startup.png"));
        c.gridx = 0;
        c.gridy = 0;
        c.anchor = GridBagConstraints.WEST;
        c.gridwidth = GridBagConstraints.REMAINDER;
        authorPanel.add(imageLabel, c);
        
        JLabel authorLabel = new JLabel(GlobalResourceLoader.getString(
                    RESOURCE_BUNDLE_PATH, "about", "authors"));

        //Font font = MainInterface.columbaTheme.getControlTextFont();
        Font font = UIManager.getFont("Label.font");

        if (font != null) {
            font = font.deriveFont(Font.BOLD);
            authorLabel.setFont(font);
        }

        c.gridy = 1;
        c.gridwidth = 1;
        Component box = Box.createRigidArea(new Dimension(10, 10));
        authorPanel.add(box, c);
        
        c.gridy = 2;
        authorPanel.add(authorLabel, c);

        c.gridx = 1;
        box = Box.createRigidArea(new Dimension(5, 15));
        authorPanel.add(box, c);

        AddressLabel a1 = new AddressLabel(
                "Frederik Dietz <fdietz@users.sourceforge.net>");
        c.gridx = 2;
        c.gridwidth = GridBagConstraints.REMAINDER;
        authorPanel.add(a1, c);

        AddressLabel a2 = new AddressLabel(
                "Timo Stich <tstich@users.sourceforge.net>");
        c.gridy = 3;
        authorPanel.add(a2, c);

        JLabel websiteLabel = new JLabel(GlobalResourceLoader.getString(
                    RESOURCE_BUNDLE_PATH, "about", "website"));
        if (font != null) {
            websiteLabel.setFont(font);
        }

        c.gridx = 0;
        c.gridy = 4;
        c.gridwidth = 1;
        authorPanel.add(websiteLabel, c);

        URLLabel websiteUrl = null;
        try {
            websiteUrl = new URLLabel(new URL("http://columba.sourceforge.net"));
        } catch (MalformedURLException mue) {} //does not occur

        c.gridx = 2;
        c.gridwidth = GridBagConstraints.REMAINDER;
        authorPanel.add(websiteUrl, c);

        //TODO: i18n
        tabbedPane.addTab("Authors", authorPanel);
        
        JPanel contributorPanel = new JPanel(new BorderLayout(0, 5));
        contributorPanel.setBorder(BorderFactory.createEmptyBorder(12, 12, 11, 11));
        contributorPanel.add(
                new JLabel("These people have contributed to the development:"),
                BorderLayout.NORTH);
        JList contributorList = new JList(new String[]{
                "Thomas Wabner",
                "Karl Peder Olesen",
                "Eric Mattsson",
                "Riyad Kalla",
                "Michael Rudolf",
                "Luca Santarelli",
                "Eduardo P\u00E8rez",
                "John Murga",
                "Anthony Parent",
                "Jari Vuoksenranta",
                "Nicolas B\u00E9theuil",
                "Romain Guy",
                "Thomas Singer",
                "David Jeske",
                "Christopher Burkey",
                "Paul A. Golder",
                "David Brusowanking",
                "Paul Nicholls",
                "Paul E. Baclace"
        });
        contributorPanel.add(new JScrollPane(contributorList));
        
        tabbedPane.addTab("Contributors", contributorPanel);
        if (MainInterface.DEBUG) {
                tabbedPane.addTab("Memory", new MemoryPanel());
        }
        
		
		JPanel center = new JPanel();
		center.setLayout( new BorderLayout());
		center.setBorder( BorderFactory.createEmptyBorder(12,12,12,12));
		
		center.add(tabbedPane, BorderLayout.CENTER);
		
		getContentPane().add(center,BorderLayout.CENTER);
		
        JPanel buttonPanel = new JPanel(new BorderLayout(0, 0));
        buttonPanel.setBorder(BorderFactory.createEmptyBorder(5, 12, 11, 11));

        ButtonWithMnemonic closeButton = new ButtonWithMnemonic(
                GlobalResourceLoader.getString(
                    "global", "global", "close"));
        closeButton.setActionCommand(CMD_CLOSE);
        closeButton.addActionListener(this);
        buttonPanel.add(closeButton, BorderLayout.EAST);
        getContentPane().add(buttonPanel, BorderLayout.SOUTH);
        getRootPane().setDefaultButton(closeButton);
        getRootPane().registerKeyboardAction(this, CMD_CLOSE,
            KeyStroke.getKeyStroke(KeyEvent.VK_ESCAPE, 0),
            JComponent.WHEN_IN_FOCUSED_WINDOW);
        pack();
        setLocationRelativeTo(null);
    }

    public void actionPerformed(ActionEvent e) {
        if (CMD_CLOSE.equals(e.getActionCommand())) {
            setVisible(false);
        }
    }
    
    public synchronized static AboutDialog getInstance() {
        if (instance == null) {
            instance = new AboutDialog();
        }
        return instance;
    }

    protected static class MemoryPanel extends JPanel {
        protected Thread updaterThread;
        private int currentMemory = -1;
        private int totalMemory = -1;
        protected JFormattedTextField currentMemoryTextField;
        protected JFormattedTextField maxMemoryTextField;
        protected JProgressBar progressBar;
        protected JFormattedTextField totalMemoryTextField;

        public MemoryPanel() {
            super(new GridBagLayout());
            setBorder(BorderFactory.createEmptyBorder(12, 12, 11, 11));
            initComponents();

            if (updaterThread == null) {
                updaterThread = new MemoryMonitorThread(this);
                updaterThread.start();
            }
        }

        public int getCurrentMemory() {
            return currentMemory;
        }

        public void setCurrentMemory(int mem) {
            currentMemory = mem;
            currentMemoryTextField.setValue(new Integer(mem));
            progressBar.setValue(mem);
        }

        public int getTotalMemory() {
            return totalMemory;
        }

        public void setTotalMemory(int mem) {
            totalMemory = mem;
            totalMemoryTextField.setValue(new Integer(mem));
            progressBar.setMaximum(mem);
        }

        private void initComponents() {
            GridBagConstraints c = new GridBagConstraints();

            currentMemoryTextField = new JFormattedTextField(NumberFormat.getInstance());
            totalMemoryTextField = new JFormattedTextField(NumberFormat.getInstance());
            maxMemoryTextField = new JFormattedTextField();
            JButton gcButton = new JButton(ImageLoader.getImageIcon(
                        "stock_delete-16.png"));

            JLabel currentMemoryLabel = new JLabel("Used:");
            c.gridx = 0;
            c.gridy = 0;
            c.anchor = GridBagConstraints.WEST;
            add(currentMemoryLabel, c);

            currentMemoryTextField.setColumns(5);
            currentMemoryTextField.setEditable(false);
            c.gridx = 1;
            c.insets = new Insets(0, 4, 0, 4);
            add(currentMemoryTextField, c);

            JLabel currentMemoryKBLabel = new JLabel("KB");
            c.gridx = 2;
            c.insets = new Insets(0, 0, 0, 0);
            add(currentMemoryKBLabel, c);

            JLabel totalMemoryLabel = new JLabel("Total:");
            c.gridx = 3;
            c.insets = new Insets(0, 10, 0, 0);
            add(totalMemoryLabel, c);

            totalMemoryTextField.setColumns(5);
            totalMemoryTextField.setEditable(false);
            c.gridx = 4;
            c.insets = new Insets(0, 4, 0, 4);
            add(totalMemoryTextField, c);

            JLabel totalMemoryKBLabel = new JLabel("KB");
            c.gridx = 5;
            c.insets = new Insets(0, 0, 0, 0);
            add(totalMemoryKBLabel, c);

            JLabel maxMemoryLabel = new JLabel("VM Max:");
            c.gridx = 0;
            c.gridy = 1;
            c.insets = new Insets(6, 0, 0, 0);
            add(maxMemoryLabel, c);

            maxMemoryTextField.setColumns(5);
            maxMemoryTextField.setEditable(false);
            maxMemoryTextField.setValue(new Integer(
                    (int) (Runtime.getRuntime().maxMemory() / 1000)));
            c.gridx = 1;
            c.insets = new Insets(4, 4, 0, 4);
            add(maxMemoryTextField, c);

            JLabel maxMemoryKBLabel = new JLabel("KB");
            c.gridx = 2;
            c.insets = new Insets(0, 0, 0, 0);
            add(maxMemoryKBLabel, c);
            
            progressBar = new JProgressBar();
            progressBar.setPreferredSize(gcButton.getPreferredSize());
            progressBar.setStringPainted(true);
            c.gridx = 0;
            c.gridy = 2;
            c.insets = new Insets(10, 0, 0, 0);
            c.fill = GridBagConstraints.HORIZONTAL;
            c.gridwidth = 5;
            add(progressBar, c);

            gcButton.setContentAreaFilled(false);
            gcButton.addActionListener(new ActionListener() {
                    public void actionPerformed(ActionEvent evt) {
                        System.gc();
                    }
            });
            c.gridx = 5;
            c.gridwidth = 1;
            c.insets = new Insets(10, 6, 0, 0);
            c.fill = GridBagConstraints.NONE;
            add(gcButton, c);
        }
    }

    protected static class MemoryMonitorThread extends Thread {
        protected static final int MEMORY_UPDATE_THRESHOLD = 50; // 50k
        protected MemoryPanel memoryPanel;
        protected Runtime runtime = Runtime.getRuntime();
        
        public MemoryMonitorThread(MemoryPanel memoryPanel) {
            this.memoryPanel = memoryPanel;
            setPriority(Thread.MIN_PRIORITY);
            setDaemon(true);
        }

        public void run() {
            while (!isInterrupted()) {
                SwingUtilities.invokeLater(new Runnable() {
                    public void run() {
                        updateDisplay();
                    }
                });
                try {
                    Thread.sleep(750);
                } catch (InterruptedException ie) {
                    ie.printStackTrace();
                }
            }
        }
        
        protected void updateDisplay() {
            int totalMem = (int) (runtime.totalMemory() / 1000);
            int currMem = (int) (totalMem - (runtime.freeMemory() / 1000));

            if ((memoryPanel.getTotalMemory() < (totalMem -
                    MEMORY_UPDATE_THRESHOLD)) ||
                    (memoryPanel.getTotalMemory() > (totalMem +
                    MEMORY_UPDATE_THRESHOLD))) {
                memoryPanel.setTotalMemory(totalMem);
            }

            if ((memoryPanel.getCurrentMemory() < (currMem -
                    MEMORY_UPDATE_THRESHOLD)) ||
                    (memoryPanel.getCurrentMemory() > (currMem +
                    MEMORY_UPDATE_THRESHOLD))) {
                memoryPanel.setCurrentMemory(currMem);
            }
        }
    }
}
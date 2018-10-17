public static HelpManager getInstance() {

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

package org.columba.core.help;

import java.awt.Component;
import java.awt.Font;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.net.URL;
import java.util.Locale;

import javax.help.HelpBroker;
import javax.help.HelpSet;
import javax.help.JHelp;
import javax.help.TextHelpModel;
import javax.swing.JFrame;
import javax.swing.JMenu;
import javax.swing.JMenuBar;
import javax.swing.JMenuItem;
import javax.swing.JOptionPane;
import javax.swing.UIManager;

/**
 * @author fdietz
 *
 * This class manages all JavaHelp relevant helpsets, its also
 * encapsulates the broker which is used for context sensitiv help.
 * This class is a singleton.
 */
public class HelpManager {
    private static HelpManager instance;

    // name of helpset resource
    final static String helpsetName = "jhelpset";
    private JHelp jh = null;
    private HelpSet hs = null;
    private HelpBroker hb = null;
    private String hsName = null; // name for the HelpSet 
    private String hsPath = null; // URL spec to the HelpSet
    private JFrame frame;

    /**
 * Creates a new instance. This method is private because it should
 * only get called from the static getHelpManager() method.
 */
    private HelpManager() {
        ClassLoader loader = getClass().getClassLoader();
        URL url = HelpSet.findHelpSet(loader, helpsetName, "",
                Locale.getDefault());

        if (url == null) {
            url = HelpSet.findHelpSet(loader, helpsetName, ".hs",
                    Locale.getDefault());

            if (url == null) {
                // could not find it!
                JOptionPane.showMessageDialog(null, "HelpSet not found",
                    "Error", JOptionPane.ERROR_MESSAGE);

                return;
            }
        }

        try {
            hs = new HelpSet(loader, url);
        } catch (Exception ee) {
            JOptionPane.showMessageDialog(null, "HelpSet not found", "Error",
                JOptionPane.ERROR_MESSAGE);

            return;
        }

        // The JavaHelp can't be added to a BorderLayout because it
        // isnt' a component. For this demo we'll use the embeded method
        // since we don't want a Frame to be created.
        hb = hs.createHelpBroker();

        // TODO (@author fdietz): fix the font settings for the content viewer
        // setting the fonts like this doesn't seem to work
        Font font = (Font) UIManager.get("Label.font");
        hb.setFont(font);

        jh = new JHelp(hs);

        // set main font
        jh.setFont(font);

        jh.getContentViewer().setFont(font);
        jh.getCurrentNavigator().setFont(font);
    }

    /**
     * Opens the help frame.
     */
    public void openHelpFrame() {
        if (frame == null) {
            TextHelpModel m = jh.getModel();
            HelpSet hs = m.getHelpSet();
            String title = hs.getTitle();

            if (title == null || title.equals("")) {
                title = "Unnamed HelpSet"; // maybe based on HS?
            }

            frame = new JFrame(title);
            frame.getContentPane().add(jh);
            JMenuBar menuBar = new JMenuBar();
            JMenuItem mi;
            JMenu file = (JMenu) menuBar.add(new JMenu("File"));
            file.setMnemonic('F');

            mi = (JMenuItem) file.add(new JMenuItem("Exit"));
            mi.setMnemonic('x');
            mi.addActionListener(new ActionListener() {
                    public void actionPerformed(ActionEvent e) {
                        frame.setVisible(false);
                    }
                });
            //JMenu options = (JMenu) menuBar.add(new JMenu("Options"));
            //options.setMnemonic('O');
            frame.setJMenuBar(menuBar);
            frame.pack();
            frame.setExtendedState(JFrame.MAXIMIZED_BOTH);
        }
        frame.setVisible(true);
    }

    /**
 * @return
 */
    public HelpBroker getHelpBroker() {
        return hb;
    }

    /**
 * Associate button with topic ID.
 *
 * Topic ID's are listed in jhelpmap.jhm in package lib/usermanual.jar
 *
 * @param c                        component
 * @param helpID        helpID
 */
    public void enableHelpOnButton(Component c, String helpID) {
        getHelpBroker().enableHelpOnButton(c, helpID, hs);
    }

    /**
 * Enables the F1 help key on components.
 */
    public void enableHelpKey(Component c, String helpID) {
        getHelpBroker().enableHelpKey(c, helpID, hs);
    }

    /**
 * Returns the singleton help manager instance.
 */
    public static HelpManager getHelpManager() {
        if (instance == null) {
            instance = new HelpManager();
        }

        return instance;
    }
}
import org.frapuccino.awt.WindowsUtil;

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
package org.columba.core.gui.logdisplay;

import java.awt.BorderLayout;
import java.awt.Container;

import javax.swing.JFrame;

import org.frappucino.awt.WindowsUtil;


/**
 * @author redsolo
 */
public class LogDisplayFrame extends JFrame {

    private static LogDisplayFrame frameInstance;

    /**
     * @param title
     * @throws java.awt.HeadlessException
     */
    public LogDisplayFrame() {
        super("Log display");
        Container container = getContentPane();
        container.setLayout(new BorderLayout());
        container.add(new LogPanel(), BorderLayout.CENTER);
        pack();
        setDefaultCloseOperation(JFrame.HIDE_ON_CLOSE);
    }

    /**
     * Shows the Log display frame.
     * Creates only one instance of this frame.
     */
    public static void showFrame() {
        if (frameInstance == null) {
            frameInstance = new LogDisplayFrame();
            WindowsUtil.centerInScreen(frameInstance);
        }
        frameInstance.setVisible(true);
    }
}
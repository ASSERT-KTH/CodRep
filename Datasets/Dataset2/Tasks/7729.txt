window = new TransparentWindow(ImageLoader.getMiscIcon(

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

import java.awt.AWTException;
import java.awt.Dimension;
import java.awt.Frame;
import java.awt.Toolkit;
import java.awt.Window;

import org.columba.core.gui.base.TransparentWindow;
import org.columba.core.resourceloader.ImageLoader;


public class StartUpFrame extends Frame {
    private Window window;

    public StartUpFrame() {
        super();

        try {
            window = new TransparentWindow(ImageLoader.getImageIcon(
                        "startup.png"));

            Dimension screenDim = Toolkit.getDefaultToolkit().getScreenSize();
            window.setLocation((screenDim.width - window.getWidth()) / 2,
                (screenDim.height - window.getHeight()) / 2);
        } catch (AWTException e) {
            e.printStackTrace();
        }
    }

    public void setVisible(boolean b) {
        window.setVisible(b);
    }
}
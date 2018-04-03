import org.columba.core.gui.dialog.ErrorDialog;

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

package org.columba.core.facade;

import org.columba.core.gui.util.ErrorDialog;
import org.columba.core.help.HelpManager;

/**
 * Dialog factory.
 *
 * @author fdietz
 */
public class DialogFacade {
    /**
     * Open an dialog showing an exception stack-trace and offering the user the
     * choice of sending in a bug-report
     *
     * @param ex
     *            Exception class
     */
    public static void showExceptionDialog(Exception ex) {
        new ErrorDialog(ex.getLocalizedMessage(), ex);
    }
    
    /**
     * Show error with a "Show Details" button.
     *
     * @param message		error message
     * @param ex			exception
     */
    public static void showErrorDialog(String message, Exception ex) {
        new ErrorDialog(message, ex);
    }
    
    /**
     * Show help frame.
     */
    public static void showHelpFrame() {
    	HelpManager.getInstance().openHelpFrame();
    }
}
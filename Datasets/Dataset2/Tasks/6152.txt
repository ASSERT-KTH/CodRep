public static final String version = "1.0 RC1-test2";

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

package org.columba.core.main;

import org.columba.core.backgroundtask.BackgroundTaskManager;
import org.columba.core.command.CommandProcessor;
import org.columba.core.config.Config;
import org.columba.core.gui.ClipboardManager;
import org.columba.core.gui.focus.FocusManager;
import org.columba.core.gui.frame.FrameModel;
import org.columba.core.plugin.PluginManager;

/**
 * Main Interface keeping static instances of all objects
 * which need to be accessed by other subsystems.
 *
 * @author fdietz
 */
public class MainInterface {
    /** Current version */
    public static final String version = "1.0 Milestone M2";

    /** If true, enables debugging output from org.columba.core.logging */
    public static boolean DEBUG = false;

    /** Configuration file management */
    public static Config config;
    
    /** Maintains references to all open frames */
    public static FrameModel frameModel;

    /** Scheduler */
    public static CommandProcessor processor;
    public static PluginManager pluginManager;

    /**
     * Tasks which are executed by a timer in the background
     * if the program is currently in idle mode
     */
    public static BackgroundTaskManager backgroundTaskManager;

    /** Every component using cut/copy/paste/etc. uses this manager */
    public static ClipboardManager clipboardManager;

    /** Focus manager needed for cut/copy/paste/etc. */
    public static FocusManager focusManager;
    
    /** Encapsulates the system's connection state */
    public static ConnectionState connectionState;

    /** No need to create instances of this class. */
    private MainInterface() {}
}
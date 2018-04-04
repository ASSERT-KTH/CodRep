MainInterface.frameModel = new FrameModel();

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

import java.io.File;

import org.columba.addressbook.main.AddressbookMain;

import org.columba.core.backgroundtask.BackgroundTaskManager;
import org.columba.core.command.DefaultProcessor;
import org.columba.core.config.Config;
import org.columba.core.gui.ClipboardManager;
import org.columba.core.gui.focus.FocusManager;
import org.columba.core.gui.frame.FrameModel;
import org.columba.core.gui.themes.ThemeSwitcher;
import org.columba.core.gui.util.FontProperties;
import org.columba.core.gui.util.StartUpFrame;
import org.columba.core.help.HelpManager;
import org.columba.core.logging.ColumbaLogger;
import org.columba.core.plugin.ActionPluginHandler;
import org.columba.core.plugin.ConfigPluginHandler;
import org.columba.core.plugin.ExternalToolsPluginHandler;
import org.columba.core.plugin.FramePluginHandler;
import org.columba.core.plugin.InterpreterHandler;
import org.columba.core.plugin.MenuPluginHandler;
import org.columba.core.plugin.PluginManager;
import org.columba.core.plugin.ThemePluginHandler;

import org.columba.mail.config.MailConfig;
import org.columba.mail.gui.config.accountwizard.AccountWizardLauncher;
import org.columba.mail.main.MailMain;

public class Main {
    private Main() {}
    
    public static void main(String[] args) {
        ColumbaCmdLineParser cmdLineParser = new ColumbaCmdLineParser();
        try {
            cmdLineParser.parseCmdLine(args);
        } catch (IllegalArgumentException e) {
            ColumbaCmdLineParser.printUsage();
            System.exit(2);
        }

        // initialize configuration backend
        String path = cmdLineParser.getPathOption();
        MainInterface.config = new Config(path == null ? null : new File(path));

        // the configPath settings are made in the commandlineParser @see ColumbaCmdLineParser
        ColumbaClient.loadInVMInstance(args);

        StartUpFrame frame = new StartUpFrame();
        frame.setVisible(true);

        AddressbookMain addressbook = new AddressbookMain();
        addressbook.initConfiguration();

        MailMain mail = new MailMain();
        mail.initConfiguration();

        MainInterface.config.init();

        MainInterface.clipboardManager = new ClipboardManager();
        MainInterface.focusManager = new FocusManager();

        MainInterface.processor = new DefaultProcessor();
        MainInterface.processor.start();

        MainInterface.pluginManager = new PluginManager();

        MainInterface.pluginManager.registerHandler(new InterpreterHandler());

        MainInterface.pluginManager.registerHandler(new ExternalToolsPluginHandler());

        MainInterface.pluginManager.registerHandler(new ActionPluginHandler());

        MainInterface.pluginManager.registerHandler(new MenuPluginHandler(
                "org.columba.core.menu"));
        MainInterface.pluginManager.registerHandler(new ConfigPluginHandler());

        MainInterface.pluginManager.registerHandler(new FramePluginHandler());

        MainInterface.pluginManager.registerHandler(new ThemePluginHandler());

        MainInterface.backgroundTaskManager = new BackgroundTaskManager();

        addressbook.initPlugins();
        mail.initPlugins();

        MainInterface.pluginManager.initPlugins();

        ThemeSwitcher.setTheme();

        // init font configuration
        new FontProperties();

        // set application wide font
        FontProperties.setFont();

        // initialze JavaHelp manager
        new HelpManager();

        //MainInterface.frameModelManager = new FrameModelManager();
        addressbook.initGui();

        mail.initGui();

        new FrameModel();

        frame.setVisible(false);

        if (MailConfig.getAccountList().count() == 0) {
            try {
                new AccountWizardLauncher().launchWizard();
            } catch (Exception ex) {
                ColumbaLogger.log.severe(ex.getMessage());
            }
        }

        new CmdLineArgumentHandler(cmdLineParser);
    }
}
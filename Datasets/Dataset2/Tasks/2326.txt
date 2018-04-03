MainInterface.DEBUG = true;

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

import java.awt.Event;
import java.awt.event.ActionEvent;
import java.awt.event.KeyEvent;
import java.io.PrintWriter;
import java.net.Socket;

import javax.swing.AbstractAction;
import javax.swing.Action;
import javax.swing.KeyStroke;
import javax.swing.text.JTextComponent;
import javax.swing.text.Keymap;

import org.columba.addressbook.main.AddressbookMain;
import org.columba.core.action.ActionPluginHandler;
import org.columba.core.command.DefaultProcessor;
import org.columba.core.config.Config;
import org.columba.core.config.ConfigPath;
import org.columba.core.gui.ClipboardManager;
import org.columba.core.gui.frame.FrameModel;
import org.columba.core.gui.menu.MenuPluginHandler;
import org.columba.core.gui.util.ImageLoader;
import org.columba.core.gui.util.StartUpFrame;
import org.columba.core.gui.util.ThemeSwitcher;
import org.columba.core.logging.ColumbaLogger;
import org.columba.core.plugin.FramePluginHandler;
import org.columba.core.plugin.InterpreterHandler;
import org.columba.core.plugin.PluginManager;
import org.columba.core.shutdown.SaveConfigPlugin;
import org.columba.core.shutdown.ShutdownManager;
import org.columba.core.util.CharsetManager;
import org.columba.core.util.CmdLineArgumentParser;
import org.columba.core.util.TempFileStore;
import org.columba.mail.config.MailConfig;
import org.columba.mail.gui.config.accountwizard.AccountWizard;
import org.columba.mail.main.MailMain;

public class Main {
	private static ColumbaLoader columbaLoader;

	public static void loadInVMInstance(String[] arguments) {
		try {
			Socket clientSocket =
				new Socket("127.0.0.1", ColumbaLoader.COLUMBA_PORT);

			PrintWriter writer =
				new PrintWriter(clientSocket.getOutputStream());

			StringBuffer buf = new StringBuffer();
			buf.append("columba:");
			for (int i = 0; i < arguments.length; i++) {
				buf.append(arguments[i]);
				buf.append("%");
			}

			writer.write(buf.toString());
			writer.flush();
			writer.close();

			clientSocket.close();

			System.exit(5);

		} catch (Exception ex) { // we get a java.net.ConnectException: Connection refused
			//  -> this means that no server is running
			//      -> lets start one
			columbaLoader = new ColumbaLoader();
		}

	}

	public static void main(String[] arg) {
		final String[] args = arg;

		ColumbaCmdLineArgumentParser cmdLineParser =
			new ColumbaCmdLineArgumentParser();

		try {
			cmdLineParser.parse(args);
		} catch (CmdLineArgumentParser.UnknownOptionException e) {
			System.err.println(e.getMessage());
			ColumbaCmdLineArgumentParser.printUsage();
			System.exit(2);
		} catch (CmdLineArgumentParser.IllegalOptionValueException e) {
			System.err.println(e.getMessage());
			ColumbaCmdLineArgumentParser.printUsage();
			System.exit(2);
		}

		CmdLineArgumentParser.Option[] allOptions =
			new CmdLineArgumentParser.Option[] {
				ColumbaCmdLineArgumentParser.DEBUG,
				ColumbaCmdLineArgumentParser.COMPOSER,
				ColumbaCmdLineArgumentParser.RCPT,
				ColumbaCmdLineArgumentParser.MESSAGE,
				ColumbaCmdLineArgumentParser.PATH,
				};

		Object path =
			cmdLineParser.getOptionValue(ColumbaCmdLineArgumentParser.PATH);
		Object d =
			cmdLineParser.getOptionValue(ColumbaCmdLineArgumentParser.DEBUG);

		if (d != null)
			MainInterface.DEBUG = Boolean.TRUE;

		if (path != null) {
			new ConfigPath((String) path);

		} else {
			new ConfigPath();

		}

		loadInVMInstance(arg);
		
		final StartUpFrame frame = new StartUpFrame();
		frame.setVisible(true);

		// enable logging 
		new ColumbaLogger();

		new Config();

		AddressbookMain addressbook = new AddressbookMain();
		addressbook.initConfiguration();

		MailMain mail = new MailMain();
		mail.initConfiguration();

		Config.init();

		new TempFileStore();

		ThemeSwitcher.setTheme();

		doGuiInits();

		MainInterface.clipboardManager = new ClipboardManager();

		new ImageLoader();

		MainInterface.charsetManager = new CharsetManager();

		MainInterface.processor = new DefaultProcessor();
		MainInterface.processor.start();

		MainInterface.pluginManager = new PluginManager();
		MainInterface.pluginManager.registerHandler(new InterpreterHandler());

		MainInterface.pluginManager.registerHandler(new ActionPluginHandler());

		MainInterface.pluginManager.registerHandler(
			new MenuPluginHandler("org.columba.core.menu"));

		MainInterface.pluginManager.registerHandler(new FramePluginHandler());

		MainInterface.shutdownManager = new ShutdownManager();

		MainInterface.shutdownManager.register(new SaveConfigPlugin());

		addressbook.initPlugins();
		mail.initPlugins();

		MainInterface.pluginManager.initPlugins();

		frame.advance();

		//MainInterface.frameModelManager = new FrameModelManager();

		addressbook.initGui();

		frame.advance();

		mail.initGui();

		new FrameModel();

		if (MailConfig.getAccountList().count() == 0) {
			try {

				new AccountWizard(false);

			} catch (Exception ex) {
				ex.printStackTrace();
			}

		}

		new CmdLineArgumentHandler(args);
		
		frame.setVisible(false);

	

	} // main

	private static void doGuiInits() {
		Keymap keymap;
		Action action;
		KeyStroke keystroke;

		/// CHANGES TO GLOBAL JTextComponent
		keymap = JTextComponent.getKeymap(JTextComponent.DEFAULT_KEYMAP);

		// add "CTRL-INS" to "clipboard copy" functionality
		action = new AbstractAction() {
			public void actionPerformed(ActionEvent e) {
				((JTextComponent) e.getSource()).copy();
			}
		};
		keystroke = KeyStroke.getKeyStroke(KeyEvent.VK_INSERT, Event.CTRL_MASK);
		keymap.addActionForKeyStroke(keystroke, action);

		// add "SHIFT-DEL" to "clipboard cut" functionality
		action = new AbstractAction() {
			public void actionPerformed(ActionEvent e) {
				((JTextComponent) e.getSource()).cut();
			}
		};
		keystroke =
			KeyStroke.getKeyStroke(KeyEvent.VK_DELETE, Event.SHIFT_MASK);
		keymap.addActionForKeyStroke(keystroke, action);

		// add "SHIFT-INS" to "clipboard paste" functionality
		action = new AbstractAction() {
			public void actionPerformed(ActionEvent e) {
				((JTextComponent) e.getSource()).paste();
			}
		};
		keystroke =
			KeyStroke.getKeyStroke(KeyEvent.VK_INSERT, Event.SHIFT_MASK);
		keymap.addActionForKeyStroke(keystroke, action);

	} // doGuiInits

}
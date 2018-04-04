new AccountWizard(false);

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
import javax.swing.JFrame;
import javax.swing.KeyStroke;
import javax.swing.text.JTextComponent;
import javax.swing.text.Keymap;

import org.columba.addressbook.config.AddressbookConfig;
import org.columba.addressbook.main.AddressbookInterface;
import org.columba.addressbook.main.AddressbookMain;
import org.columba.addressbook.shutdown.SaveAllAddressbooksPlugin;
import org.columba.core.command.DefaultProcessor;
import org.columba.core.config.Config;
import org.columba.core.config.ConfigPath;
import org.columba.core.gui.util.ImageLoader;
import org.columba.core.gui.util.StartUpFrame;
import org.columba.core.gui.util.ThemeSwitcher;
import org.columba.core.logging.ColumbaLogger;
import org.columba.core.plugin.InterpreterHandler;
import org.columba.core.plugin.PluginManager;
import org.columba.core.shutdown.SaveConfigPlugin;
import org.columba.core.shutdown.ShutdownManager;
import org.columba.core.util.CharsetManager;
import org.columba.core.util.CmdLineArgumentParser;
import org.columba.core.util.TempFileStore;
import org.columba.mail.coder.Base64Decoder;
import org.columba.mail.coder.Base64Encoder;
import org.columba.mail.coder.CoderRouter;
import org.columba.mail.coder.QuotedPrintableDecoder;
import org.columba.mail.coder.QuotedPrintableEncoder;
import org.columba.mail.config.MailConfig;
import org.columba.mail.gui.config.accountwizard.AccountWizard;
import org.columba.mail.gui.frame.MailFrameModel;
import org.columba.mail.gui.tree.TreeModel;
import org.columba.mail.plugin.FilterActionPluginHandler;
import org.columba.mail.plugin.FolderPluginHandler;
import org.columba.mail.plugin.LocalFilterPluginHandler;
import org.columba.mail.pop3.POP3ServerCollection;
import org.columba.mail.shutdown.SaveAllFoldersPlugin;
import org.columba.mail.shutdown.SavePOP3CachePlugin;
import org.columba.mail.util.MailResourceLoader;

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


		/*
		try {
			
			
			Object[] list = new Object[3];
			list[0] = "hallo";
			list[1] = new DateFilter();
			list[2] = new Integer(3);
			Python.runScript("./plugins/HelloWorldFilterAction/HelloWorld.py", list);
			
			
		} catch (Exception ex) {
			ex.printStackTrace();
		}
		*/

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

		final StartUpWorker worker = new StartUpWorker() {
			JFrame mainFrame;

			public Object construct() {

				MainInterface.addressbookInterface = new AddressbookInterface();

				// enable logging 
				new ColumbaLogger();

				new Config();

				new MailConfig();

				new AddressbookConfig();

				Config.init();

				new TempFileStore();

				ThemeSwitcher.setTheme();

				frame.advance();

				new ImageLoader();

				new MailResourceLoader();

				MainInterface.popServerCollection = new POP3ServerCollection();

				new CoderRouter();
				new QuotedPrintableDecoder();
				new QuotedPrintableEncoder();
				new Base64Decoder();
				new Base64Encoder();

				MainInterface.charsetManager = new CharsetManager();

				MainInterface.processor = new DefaultProcessor();
				MainInterface.processor.start();

				MainInterface.pluginManager = new PluginManager();
				MainInterface.pluginManager.registerHandler( new InterpreterHandler() );
				
				MainInterface.pluginManager.registerHandler(
					new FilterActionPluginHandler());
				MainInterface.pluginManager.registerHandler(
					new LocalFilterPluginHandler());
				MainInterface.pluginManager.registerHandler(
					new FolderPluginHandler());

				MainInterface.pluginManager.initPlugins();

				frame.advance();

				AddressbookMain.main(null);

				doGuiInits();

				MainInterface.treeModel =
					new TreeModel(MailConfig.getFolderConfig());
					
				MainInterface.frameModel = new MailFrameModel(MailConfig.get("mainframeoptions").getElement(
				"/options/gui/viewlist"));

				frame.advance();

				MainInterface.shutdownManager = new ShutdownManager();
				MainInterface.shutdownManager.register( new SaveAllFoldersPlugin() );
				MainInterface.shutdownManager.register( new SaveConfigPlugin() );
				MainInterface.shutdownManager.register( new SavePOP3CachePlugin() );
				MainInterface.shutdownManager.register( new SaveAllAddressbooksPlugin() );
				
				return null;
			}

			public void finished() {
				frame.setVisible(false);

				//mainFrame.setVisible(true);

				if (MailConfig.getAccountList().count()==0)
					new AccountWizard();
				

				new CmdLineArgumentHandler(args);
			}

		}; // StartupWorker$

		worker.start();

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
consoleHandler.setLevel(Level.SEVERE);

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
package org.columba.core.logging;

import java.io.File;
import java.io.IOException;
import java.util.logging.ConsoleHandler;
import java.util.logging.FileHandler;
import java.util.logging.Handler;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.logging.SimpleFormatter;

import org.columba.ristretto.log.RistrettoLogger;

/**
 * Depending on the debug flag (--debug command line option reflected in
 * MainInterface.DEBUG) the logger will either show all debug messages or just
 * severe errors. Logging information is passed to a log file and to the
 * console.
 * <p>
 * Note, that Logging must not be called before MainInterface.DEBUG, was set.
 * Otherwise, the logger won't show the correct debug level.
 * <p>
 * If the user has defined their own logging config file, then this will take
 * precedence over Columba defined logging handlers, ie. Columba will not create
 * its own default logging handlers. All has already been defined in the system
 * property <b>java.util.logging.config.file</b>.
 * <p>
 * 
 * @see org.columba.core.main.Main
 * @see java.util.logging.Logger
 * @author redsolo
 */
public final class Logging {

	private static final Logger LOG = Logger.getLogger("org.columba");

	private static ConsoleHandler consoleHandler;

	/** If true, enables debugging output from org.columba.core.logging */
	public static boolean DEBUG = false;

	/**
	 * Don't instanciate this class.
	 */
	private Logging() {
	}

	/**
	 * Returns true if the user has defined a logging config file. The user can
	 * define a config file using the system property
	 * <code>java.util.logging.config.file</code>.
	 * 
	 * @return true if the user has defined a logging config file; false
	 *         otherwise.
	 */
	private static boolean userHasDefinedLogging() {
		return (System.getProperty("java.util.logging.config.file") != null);
	}

	/**
	 * Creates the console handler. The console handler outputs only the
	 * severest logging message unless the MainInterface.DEBUG flag is set.
	 */
	public static void createDefaultHandler() {

		if (!userHasDefinedLogging()) {

			// Since Columba is doing its own logging handlers, we should not
			// use handlers in the parent logger.
			LOG.setUseParentHandlers(false);

			// init console handler
			consoleHandler = new ConsoleHandler();

			consoleHandler.setFormatter(new OneLineFormatter());
			consoleHandler.setLevel(Level.ALL);

			LOG.addHandler(consoleHandler);
		}
	}

	public static void setDebugging(boolean debug) {
		if (debug) {
			consoleHandler.setFormatter(new DebugFormatter());
			consoleHandler.setLevel(Level.ALL);

			LOG.setLevel(Level.ALL);
			// System.setProperty("javax.net.debug",
			// "ssl,handshake,data,trustmanager"); // init java.net.ssl
			// debugging

			// TODO Ristretto should handle the logging of streams in another
			// way.
			RistrettoLogger.setLogStream(System.out);
		} else {
			consoleHandler.setFormatter(new OneLineFormatter());
			consoleHandler.setLevel(Level.SEVERE);

			LOG.setLevel(Level.SEVERE);
		}
	}

	/**
	 * Default logger configuration used by Columba.
	 * <p>
	 * If the user has not defined their own config file for the logging
	 * framework, then this will create a log file named
	 * <code>columba.log</code>, in the default config directory.
	 */
	public static void createDefaultFileHandler(File configDirectory) {

		if (!userHasDefinedLogging()) {
			String logConfigFile = System
					.getProperty("java.util.logging.config.file");
			if (logConfigFile == null) {

				// create logging file in "<users config-folder>/log"
				File file = new File(configDirectory, "log");
				if (!file.exists())
					file.mkdir();

				File loggingFile = new File(file, "columba.log");

				// Setup file logging
				try {
					Handler handler = new FileHandler(loggingFile.getPath(),
							false);
					handler.setFormatter(new SimpleFormatter()); // don't use
																	// standard
																	// XML
																	// formatting

					if (Logging.DEBUG) {
						handler.setLevel(Level.ALL);
					} else {
						handler.setLevel(Level.WARNING);
					}

					LOG.addHandler(handler);
				} catch (IOException ioe) {
					LOG.severe("Could not start the file logging due to: "
							+ ioe);
				}
			}
		}
	}
}
List<String> list = new LinkedList<String>();

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

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.SocketException;
import java.net.SocketTimeoutException;
import java.util.LinkedList;
import java.util.List;
import java.util.Random;
import java.util.StringTokenizer;

import javax.swing.JOptionPane;

import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.ParseException;
import org.columba.core.component.ComponentManager;
import org.columba.core.resourceloader.GlobalResourceLoader;
import org.columba.core.shutdown.ShutdownManager;

/**
 * Opens a server socket to manage multiple sessions of Columba capable of
 * passing commands to the main session.
 * <p>
 * This class is a singleton because there can only be one server per Columba
 * session.
 * <p>
 * Basic idea taken from www.jext.org (author Roman Guy)
 * 
 * @author fdietz
 */
public class ColumbaServer {
	static final String RESOURCE_PATH = "org.columba.core.i18n.dialog";

	/**
	 * The anonymous user for single-user systems without user name.
	 */
	protected static final String ANONYMOUS_USER = "anonymous";

	/**
	 * The singleton instance of this class.
	 */
	private static ColumbaServer instance;

	/**
	 * Random number generator for port numbers.
	 */
	private static Random random = new Random();

	/**
	 * The port range Columba should use is between LOWEST_PORT and 65536.
	 */
	private static final int LOWEST_PORT = 30000;

	/**
	 * Server runs in its own thread.
	 */
	protected Thread thread;

	/**
	 * The ServerSocket used by the server.
	 */
	protected ServerSocket serverSocket;

	/**
	 * Constructor
	 */
	protected ColumbaServer() {
		thread = new Thread(new Runnable() {
			public void run() {
				while (!Thread.currentThread().isInterrupted()) {
					try {
						handleClient(serverSocket.accept());
					} catch (SocketTimeoutException ste) {
						// do nothing here, just continue
					} catch (IOException ioe) {
						ioe.printStackTrace();

						// what to do here? we could start a new server...
					}
				}

				try {
					serverSocket.close();

					// cleanup: remove port number file
					SessionController.serializePortNumber(-1);
				} catch (IOException ioe) {
				}

				serverSocket = null;
			}
		}, "ColumbaServer");
		thread.setDaemon(true);

		// stop server when shutting down
		ShutdownManager.getInstance().register(new Runnable() {
			public void run() {
				stop();
			}
		});
	}

	/**
	 * Starts the server.
	 */
	public synchronized void start() throws IOException {
		if (!isRunning()) {
			int port;
			int count = 0;

			while (serverSocket == null) {
				// create random port number within range
				port = random.nextInt(65536 - LOWEST_PORT) + LOWEST_PORT;

				try {
					serverSocket = new ServerSocket(port);

					// store port number in file
					SessionController.serializePortNumber(port);
				} catch (SocketException se) { // port is in use, try next
					count++;

					if (count == 10) { // something is very wrong here
						JOptionPane.showMessageDialog(null,
								GlobalResourceLoader.getString(RESOURCE_PATH,
										"session", "err_10se_msg"),
								GlobalResourceLoader.getString(RESOURCE_PATH,
										"session", "err_10se_title"),
								JOptionPane.ERROR_MESSAGE);

						// this is save because the only shutdown plugin
						// to stop this server, the configuration isn't touched
						System.exit(1);
					}
				}
			}

			serverSocket.setSoTimeout(2000);
			thread.start();
		}
	}

	/**
	 * Stops the server.
	 */
	public synchronized void stop() {
		thread.interrupt();
	}

	/**
	 * Check if server is already running
	 * 
	 * @return true, if server is running. False, otherwise
	 */
	public synchronized boolean isRunning() {
		return thread.isAlive();
	}

	/**
	 * Handles a client connect and authentication.
	 */
	protected void handleClient(Socket client) {
		try {
			// only accept client from local machine
			String host = client.getLocalAddress().getHostAddress();
			if (!(host.equals("127.0.0.1"))) {
				// client isn't from local machine
				return;
			}

			BufferedReader reader = new BufferedReader(new InputStreamReader(
					client.getInputStream()));
			String line = reader.readLine();
			if (!line.startsWith("Columba ")) {
				return;
			}

			line = reader.readLine();
			if (!line.startsWith("User ")) {
				return;
			}

			PrintWriter writer = new PrintWriter(client.getOutputStream());
			if (!line.substring(5).equals(
					System.getProperty("user.name", ANONYMOUS_USER))) {
				writer.write("WRONG USER\r\n");
				writer.close();
				return;
			}
			writer.write("\r\n");
			writer.flush();

			line = reader.readLine();
			// do something with the arguments..
			List list = new LinkedList();
			StringTokenizer st = new StringTokenizer(line, "%");
			while (st.hasMoreTokens()) {
				String tok = (String) st.nextToken();
				list.add(tok);
			}

			try {
				CommandLine commandLine = ColumbaCmdLineParser.getInstance()
						.parse((String[]) list.toArray(new String[0]));

				ComponentManager.getInstance().handleCommandLineParameters(
						commandLine);

			} catch (ParseException e) {
				e.printStackTrace();
			}
		} catch (IOException ioe) {
			ioe.printStackTrace();
		} finally {
			try {
				client.close();
			} catch (IOException ioe) {
			}
		}
	}

	/**
	 * Returns the singleton instance of this class.
	 */
	public static synchronized ColumbaServer getColumbaServer() {
		if (instance == null) {
			instance = new ColumbaServer();
		}
		return instance;
	}
}
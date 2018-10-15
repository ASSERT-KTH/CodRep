System.out.println("Exception occurred:"); //$NON-NLS-1$

/*******************************************************************************
 * Copyright (c) 2005, 2008 Remy Suen
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Remy Suen <remy.suen@gmail.com> - initial API and implementation
 *    Stoyan Boshev <s.boshev@prosyst.com> - [MSN] Session and subclasses needs to handle whitespace and exceptions better
 ******************************************************************************/
package org.eclipse.ecf.protocol.msn;

import java.io.*;
import java.net.Socket;
import java.util.ArrayList;

/**
 * <p>
 * An abstract base class that all other sessions should extend. This class
 * provides common methods that a session will need to use such as reading and
 * writing information from and to a socket.
 * </p>
 * 
 * <p>
 * <b>Note:</b> This class/interface is part of an interim API that is still
 * under development and expected to change significantly before reaching
 * stability. It is being made available at this early stage to solicit feedback
 * from pioneering adopters on the understanding that any code that uses this
 * API will almost certainly be broken (repeatedly) as the API evolves.
 * </p>
 */
abstract class Session {

	/**
	 * The client that this session is attached to.
	 */
	final MsnClient client;

	/**
	 * The list of listeners that have been connected to this session.
	 */
	ArrayList listeners;

	private final byte[] buffer = new byte[1024];

	private Socket socket;

	private InputStream is;

	private OutputStream os;

	/**
	 * The number of transactions that has been transferred through this session
	 * thus far. This value will automatically increment when
	 * {@link #write(String, String)} or {@link #write(String, String, boolean)}
	 * has been invoked.
	 */
	private long transactionID = 0;

	/**
	 * A thread used to wait indefinitely for incoming messages from the server.
	 */
	private IdleThread idleThread;

	private boolean closed = false;

	Session(MsnClient client) {
		this.client = client;
	}

	/**
	 * Creates a session instance that will be connected to the given host. The
	 * string must be of the form '12.345.678.9:1234'.
	 * 
	 * @param host
	 *            the host to connect to
	 * @param client
	 *            the client to hook onto
	 * @throws IOException
	 *             If an I/O error occurred while attempting to connect to the
	 *             given host.
	 */
	Session(String host, MsnClient client) throws IOException {
		this.client = client;
		openSocket(host);
	}

	/**
	 * Creates a session instance that will be connected to the given host and
	 * port.
	 * 
	 * @param ip
	 *            the host to connect to
	 * @param port
	 *            the port to connect to
	 * @param client
	 *            the client to hook onto
	 * @throws IOException
	 *             If an I/O error occurred while attempting to connect to the
	 *             port at the given host.
	 */
	Session(String ip, int port, MsnClient client) throws IOException {
		this.client = client;
		openSocket(ip, port);
	}

	/**
	 * Opens a connection to the specified host.
	 * 
	 * @param host
	 *            the host to connect to
	 * @throws IOException
	 *             If an error occurs while attempting to connect to the host
	 */
	final void openSocket(String host) throws IOException {
		closed = false;
		int index = host.indexOf(':');
		openSocket(host.substring(0, index), Integer.parseInt(host.substring(index + 1)));
	}

	final void openSocket(String ip, int port) throws IOException {
		closed = false;
		socket = new Socket(ip, port);
		is = socket.getInputStream();
		os = socket.getOutputStream();
	}

	final InputStream getInputStream() {
		return is;
	}

	/**
	 * Reads data from the channel and returns it as a String.
	 * 
	 * @return the contents that have been read, or <code>null</code> if
	 *         nothing is currently available
	 * @throws IOException
	 *             If an I/O error occurred while reading from the channel.
	 */
	String read() throws IOException {
		int read = is.read(buffer);
		if (read < 1) {
			return null;
		}
		return new String(buffer, 0, read, "UTF-8"); //$NON-NLS-1$
	}

	/**
	 * This method writes the given string input onto the channel. The carriage
	 * return and newline characters may be appended depending on the value of
	 * <code>newline</code>.
	 * 
	 * @param input
	 *            the String to be written
	 * @param newline
	 *            <code>true</code> if a '\r\n' should be appended at the end
	 *            of the write
	 * @throws IOException
	 *             If an I/O error occurs while attempting to write to the
	 *             channel.
	 */
	private final void write(String input, boolean newline) throws IOException {
		byte[] bytes = newline ? (input + "\r\n").getBytes("UTF-8") : input.getBytes("UTF-8"); //$NON-NLS-1$ //$NON-NLS-2$ //$NON-NLS-3$
		os.write(bytes);
		os.flush();
	}

	/**
	 * This method is synonymous with {@link #write(String, boolean)} with the
	 * exception that this method will always insert the carriage return and
	 * newline characters.
	 * 
	 * @param input
	 *            the String to be written
	 * @throws IOException
	 *             If an I/O error occurs while attempting to write to the
	 *             channel.
	 */
	final void write(String input) throws IOException {
		write(input, true);
	}

	/**
	 * Writes the given command with the specified parameters to the channel. A
	 * transaction identification number will also be inserted between the
	 * command and its parameters. A carriage return and a newline character
	 * will be inserted if <tt>newline</tt> is true.
	 * 
	 * @param command
	 *            the command to be inserted
	 * @param parameters
	 *            additional parameters that are associated with the command
	 * @param newline
	 *            <tt>true</tt> if a <tt>"\r\n"</tt> should be appended at
	 *            the end of the write
	 * @throws IOException
	 *             If an I/O error occurs while attempting to write to the
	 *             channel.
	 */
	final void write(String command, String parameters, boolean newline) throws IOException {
		transactionID++;
		write(command + ' ' + transactionID + ' ' + parameters, newline);
	}

	/**
	 * This method is synonymous with {@link #write(String, String, boolean)}
	 * with the exception that this method will always insert the carriage
	 * return and newline characters.
	 * 
	 * @param command
	 *            the command to be inserted
	 * @param parameters
	 *            additional parameters that are associated with the command
	 * @throws IOException
	 *             If an I/O error occurs while attempting to write to the
	 *             channel.
	 */
	final void write(String command, String parameters) throws IOException {
		write(command, parameters, true);
	}

	void close() {
		closed = true;
		if (idleThread != null) {
			idleThread.interrupt();
			idleThread = null;
		}

		if (socket != null) {
			try {
				socket.close();
			} catch (Exception e) {
				// ignored
			}
			socket = null;
		}

		if (is != null) {
			try {
				is.close();
			} catch (Exception e) {
				// ignored
			}
			is = null;
		}

		if (os != null) {
			try {
				os.close();
			} catch (Exception e) {
				// ignored
			}
			os = null;
		}
	}

	protected void finalize() throws Throwable {
		close();
		super.finalize();
	}

	/**
	 * Wait in an infinite loop for information to be read in.
	 */
	final void idle() {
		if (idleThread == null || !idleThread.isAlive()) {
			idleThread = new IdleThread();
			idleThread.start();
		}
	}

	final boolean isClosed() {
		return closed;
	}

	/**
	 * IdleThread waits for an indefinite amount of time for incoming messages.
	 */
	class IdleThread extends Thread {

		/**
		 * Begin waiting for incoming messages indefinitely.
		 */
		public void run() {
			while (!isInterrupted()) {
				try {
					sleep(50);
					read();
				} catch (InterruptedException e) {
					return;
				} catch (IOException e) {
					return;
				} catch (RuntimeException e) {
					System.out.println("Exception occurred: ");
					e.printStackTrace();
				}
			}
		}
	}
}
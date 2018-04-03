ColumbaLogger.log.info(

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

import org.columba.core.logging.ColumbaLogger;

import java.io.BufferedReader;
import java.io.InputStreamReader;

import java.net.ServerSocket;
import java.net.Socket;

import java.util.List;
import java.util.StringTokenizer;
import java.util.Vector;


/**
 * Opens a server socket to manage multiple sessions of Columba
 * able to passing commands to the main session.
 * <p>
 *
 * ideas taken from www.jext.org (author Roman Guy)
 *
 * @author fdietz
 *
 */
public class ColumbaLoader implements Runnable {
    public final static int COLUMBA_PORT = 50000;
    private Thread thread;
    private ServerSocket serverSocket;

    public ColumbaLoader() {
        try {
            serverSocket = new ServerSocket(COLUMBA_PORT);
        } catch (Exception ex) {
            ex.printStackTrace();
        }

        thread = new Thread(this);
        thread.setDaemon(false);
        thread.start();
    }

    public synchronized void stop() {
        thread.interrupt();
        thread = null;

        try {
            if (serverSocket != null) {
                serverSocket.close();
            }
        } catch (Exception ex) {
            ex.printStackTrace();
        }
    }

    public synchronized boolean isRunning() {
        return thread != null;
    }

    public void run() {
        while (isRunning()) {
            try {
                // does a client trying to connect to server ?
                Socket client = serverSocket.accept();

                if (client == null) {
                    continue;
                }

                // only accept client from local machine
                String host = client.getLocalAddress().getHostAddress();

                if (!(host.equals("127.0.0.1"))) {
                    // client isn't from local machine
                    client.close();
                }

                // try to read possible arguments
                BufferedReader reader = new BufferedReader(new InputStreamReader(
                            client.getInputStream()));

                StringBuffer arguments = new StringBuffer();
                arguments.append(reader.readLine());

                if (!(arguments.toString().startsWith("columba:"))) {
                    // client isn't a Columba client
                    client.close();
                }

                if (MainInterface.DEBUG) {
                    ColumbaLogger.log.debug(
                        "passing to running Columba session:\n" +
                        arguments.toString());
                }

                // do something with the arguments..
                handleArgs(arguments.toString());

                client.close();
            } catch (Exception ex) {
                ex.printStackTrace();
            }
        }
    }

    /**
     * Parsing the given argumentString and split this String into a StringArray. The separator is
     * the character %, thus the whole arguments should not have this character inside. The
     * character itselfs is added in Main.java @see Main#loadInVMInstance(String[]). After splitting
     * is finished the CmdLineArgumentHandler is called, to do things with the arguments
     * @see CmdLineArgumentHandler
     * @param argumentString String which holds any arguments seperated by <br>%</br> character
     */
    protected void handleArgs(String argumentString) {
        List v = new Vector();

        // remove trailing "columba:"
        argumentString = argumentString.substring(8, argumentString.length());

        StringTokenizer st = new StringTokenizer(argumentString, "%");

        while (st.hasMoreTokens()) {
            String tok = (String) st.nextToken();
            v.add(tok);
        }

        String[] args = new String[v.size()];
        v.toArray((String[]) args);

        new CmdLineArgumentHandler(args);
    }
}
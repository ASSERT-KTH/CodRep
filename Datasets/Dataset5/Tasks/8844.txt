testUrl = new URL("http", getHost(), getPort(), "/index.html");

/*******************************************************************************
 * Copyright (c) 2008, 2009 28msec Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     Gabriel Petrovay (28msec) - initial API and implementation
 *******************************************************************************/
package org.eclipse.wst.xquery.set.internal.launching.server;

import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.URL;

import org.eclipse.core.resources.IProject;
import org.eclipse.core.runtime.CoreException;
import org.eclipse.debug.core.DebugException;
import org.eclipse.debug.core.ILaunch;
import org.eclipse.debug.core.ILaunchConfiguration;
import org.eclipse.debug.core.IStreamListener;
import org.eclipse.debug.core.model.IProcess;
import org.eclipse.debug.core.model.IStreamMonitor;
import org.eclipse.wst.xquery.set.debug.core.ISETLaunchConfigurationConstants;

public class Server implements IStreamListener {

    private IProject fProject;

    private StringBuilder fErrors;

    private String fHost;
    private int fPort;

    private ILaunch fLaunch;

    public Server(ILaunch launch, IProject project) throws CoreException {
        fProject = project;
        fLaunch = launch;

        init();
    }

    private void init() throws CoreException {
        ILaunchConfiguration config = fLaunch.getLaunchConfiguration();

        // get the socket where the application will be found
        fHost = config.getAttribute(ISETLaunchConfigurationConstants.ATTR_XQDT_SET_HOST, "127.0.0.1");
        fPort = config.getAttribute(ISETLaunchConfigurationConstants.ATTR_XQDT_SET_PORT, 8080);
    }

    public String getHost() {
        return fHost;
    }

    public void setHost(String host) {
        fHost = host;
    }

    public String getSocketString() {
        return fHost + ":" + fPort;
    }

    public int getPort() {
        return fPort;
    }

    public void setPort(int port) {
        fPort = port;
    }

    public IProcess getProcess() {
        IProcess[] processes = fLaunch.getProcesses();
        if (processes.length != 1) {
            return null;
        }
        return processes[0];
    }

    public IProject getProject() {
        return fProject;
    }

    public boolean isListening() throws DebugException {
//        IProcess process = getProcess();
//        if (process == null) {
//            return false;
//        }
//        // check is the (batch/bash) process is already terminated
//        // and report an exception if it is so
//        try {
//            if (hasErrors()) {
//                // just wait a little more in case some more errors are appended to the error buffer
//                Thread.sleep(300);
//                return false;
//            }
//
//            if (SETLaunchingPlugin.DEBUG_SERVER) {
//                System.out.println("checking exit");
//            }
//            int error = process.getExitValue();
//            if (SETLaunchingPlugin.DEBUG_SERVER) {
//                System.out.println("exited with error code: " + error);
//            }
//            return false;
//        } catch (DebugException itse) {
//            // OK: this is what we want
//            if (SETLaunchingPlugin.DEBUG_SERVER) {
//                System.out.println("did not exit");
//            }
//        } catch (InterruptedException e) {
//            return false;
//        }

        // check if apache created the pid file (someone
        // else might be listening on this server's port)
//        try {
//            if (SETLaunchingPlugin.DEBUG_SERVER) {
//                System.out.println("check pid");
//            }
//            int pid = ServerManager.getServerPid(fProject);
//            if (SETLaunchingPlugin.DEBUG_SERVER) {
//                System.out.println("pid found: " + pid);
//            }
//        } catch (DebugException de) {
//            if (SETLaunchingPlugin.DEBUG_SERVER) {
//                System.out.println("pid error");
//            }
//            return false;
//        }

        // check if a HTTP connection to this server's port is possible
        URL testUrl;
        try {
            testUrl = new URL("http", getHost(), getPort(), "/");
            HttpURLConnection conn = (HttpURLConnection)testUrl.openConnection();
            conn.setRequestMethod("HEAD");
            conn.getResponseCode();
        } catch (IOException e) {
            return false;
        }

        return true;
    }

    private boolean hasErrors() {
        return fErrors != null;
    }

//    protected Process run() throws CoreException {
//        fErrors = null;
//
//        String scriptPath = CoreSdkUtil.getCoreSDKScriptPath(fProject).toOSString();
//
//        final List<String> commandLine = new ArrayList<String>(5);
//        commandLine.add(scriptPath);
//        commandLine.add("test");
//        commandLine.add("project");
//
//        String path = fProject.getLocation().toOSString();
//        commandLine.add("-d");
//        commandLine.add(path);
//
//        // add the listening interface parameter
//        commandLine.add("-s");
//        commandLine.add(fHost + ":" + fPort);
//
//        if (fDebugMode) {
//            commandLine.add("-ds");
//        }
//
//        if (fIndentResults) {
//            commandLine.add("-i");
//        }
//        if (fClearCollections) {
//            commandLine.add("-c");
//        }
//
//        fProcess = DebugPlugin.exec(commandLine.toArray(new String[commandLine.size()]), new File(path));
//
//        return fProcess;
//    }

//    private void throwSNSE() throws ServerNotStartedException {
//        int errorCode = ServerNotStartedException.SERVER_ERROR_START_FAILED;
//        String errors = (hasErrors() ? fErrors.toString() : "");
//        String start = errors.substring(0, Math.min(30, errors.length()));
//        if (start.startsWith("(OS 10048)") || start.startsWith("(48)") || start.contains("Address already in use")) {
//            errorCode = ServerNotStartedException.SERVER_ERROR_SOCKET_IN_USE;
//        }
//        throw new ServerNotStartedException(errors, errorCode);
//    }

    public void streamAppended(String text, IStreamMonitor monitor) {
        if (!hasErrors()) {
            fErrors = new StringBuilder();
        }
        fErrors.append(text);
    }
}

class ServerNotStartedException extends Exception {

    private static final long serialVersionUID = 6900278879555009638L;

    public static final int SERVER_ERROR_SOCKET_IN_USE = 1;
    public static final int SERVER_ERROR_START_FAILED = 2;

    private int fErrorCode;

    public ServerNotStartedException(int errorCode) {
        this("Unknown error", errorCode);
    }

    public ServerNotStartedException(String message, int errorCode) {
        super(message);
        fErrorCode = errorCode;
    }

    public int getErrorCode() {
        return fErrorCode;
    }
}
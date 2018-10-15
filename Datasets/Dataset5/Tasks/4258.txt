setSocket(aSocket);

/****************************************************************************
* Copyright (c) 2004 Composent, Inc. and others.
* All rights reserved. This program and the accompanying materials
* are made available under the terms of the Eclipse Public License v1.0
* which accompanies this distribution, and is available at
* http://www.eclipse.org/legal/epl-v10.html
*
* Contributors:
*    Composent, Inc. - initial API and implementation
*****************************************************************************/

package org.eclipse.ecf.provider.comm.tcp;

import java.io.BufferedOutputStream;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.io.Serializable;
import java.net.ConnectException;
import java.net.Socket;
import java.net.SocketException;
import java.net.URI;
import java.net.URISyntaxException;
import java.security.AccessController;
import java.security.PrivilegedAction;
import java.util.Enumeration;
import java.util.Map;
import java.util.Properties;
import java.util.Random;
import java.util.Vector;
import org.eclipse.ecf.core.comm.AsynchConnectionEvent;
import org.eclipse.ecf.core.comm.ConnectionDescription;
import org.eclipse.ecf.core.comm.ConnectionEvent;
import org.eclipse.ecf.core.comm.ConnectionInstantiationException;
import org.eclipse.ecf.core.comm.DisconnectConnectionEvent;
import org.eclipse.ecf.core.comm.IConnectionEventHandler;
import org.eclipse.ecf.core.comm.ISynchAsynchConnection;
import org.eclipse.ecf.core.comm.ISynchAsynchConnectionEventHandler;
import org.eclipse.ecf.core.comm.SynchConnectionEvent;
import org.eclipse.ecf.core.comm.provider.ISynchAsynchConnectionInstantiator;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.util.SimpleQueueImpl;
import org.eclipse.ecf.provider.Trace;

public final class Client implements ISynchAsynchConnection {
    public static class Creator implements ISynchAsynchConnectionInstantiator {
        public ISynchAsynchConnection makeInstance(ConnectionDescription description,
                ISynchAsynchConnectionEventHandler handler, Class[] clazzes,
                Object[] args) throws ConnectionInstantiationException {
            try {
                String [] argVals = description.getArgDefaults();
                Integer ka = null;
                if (argVals != null && argVals.length > 0) {
                    String val = argVals[0];
                    if (val != null) {
                        ka = new Integer(val);
                    }
                }
                if (args != null && args.length > 0) {
                    if (args[0] instanceof Integer) {
                        ka = (Integer) args[0];
                    } else if (args[0] instanceof String) {
                        ka = new Integer((String) args[0]);
                    }
                }
                return new Client(handler, ka);
            } catch (Exception e) {
                throw new ConnectionInstantiationException(
                        "Exception in creating connection "
                                + Client.class.getName(), e);
            }
        }
    }

    public static final String PROTOCOL = "ecftcp";
    protected static final Trace trace = Trace.create("connection");
    public static final int SNDR_PRIORITY = Thread.NORM_PRIORITY;
    public static final int RCVR_PRIORITY = Thread.NORM_PRIORITY;
    // Default close timeout is 1.5 seconds
    public static final long CLOSE_TIMEOUT = 2000;
    public static final int DEF_MAX_MSG = 50;

    protected Socket socket;
    private String addressPort = "-1:<no endpoint>:-1";
    
    protected ObjectOutputStream outputStream;
    protected ObjectInputStream inputStream;
    
    protected ISynchAsynchConnectionEventHandler handler;
    protected SimpleQueueImpl queue = new SimpleQueueImpl();
    protected int keepAlive = 0;
    protected Thread sendThread;
    protected Thread rcvThread;
    protected Thread keepAliveThread;
    protected boolean isClosing = false;
    protected boolean waitForPing = false;
    protected PingMessage ping = new PingMessage();
    protected PingResponseMessage pingResp = new PingResponseMessage();
    protected long nextPingTime;
    protected int maxMsg = DEF_MAX_MSG;
    protected long closeTimeout = CLOSE_TIMEOUT;
    protected Vector eventNotify = null;
    protected Map properties;
    
    protected ID containerID = null;
    
    public Map getProperties() {
        return properties;
    }
    public Object getAdapter(Class clazz) {
        return null;
    }
    private String getAddressPort() {
    	return addressPort;
    }
    protected void trace(String msg) {
        if (Trace.ON && trace != null) {
            trace.msg(getAddressPort()+";"+msg);
        }
    }

    protected void dumpStack(String msg, Throwable e) {
        if (Trace.ON && trace != null) {
            trace.dumpStack(e, getAddressPort()+";"+msg);
        }
    }

    public void setProperties(Map props) {
        this.properties = props;
    }

    public Client(Socket aSocket, ObjectInputStream iStream,
            ObjectOutputStream oStream,
            ISynchAsynchConnectionEventHandler handler, int keepAlive)
            throws IOException {
        this(aSocket, iStream, oStream, handler, keepAlive, DEF_MAX_MSG);
    }
    private void setSocket(Socket s) throws SocketException {
    	socket = s;
    	if (s != null) {
    		// Set socket options
    		s.setTcpNoDelay(true);
    		addressPort = s.getLocalPort()+":"+s.getInetAddress().getHostName()+":"+s.getPort();
    	} else {
    		addressPort = "-1:<no endpoint>:-1";
    	}
    }
    public Client(Socket aSocket, ObjectInputStream iStream,
            ObjectOutputStream oStream,
            ISynchAsynchConnectionEventHandler handler, int keepAlive,
            int maxmsgs) throws IOException {
        setSocket(socket);
        inputStream = iStream;
        outputStream = oStream;
        this.handler = handler;
        containerID = handler.getEventHandlerID();
        this.keepAlive = keepAlive;
        maxMsg = maxmsgs;
        properties = new Properties();
        setupThreads();
    }

    public Client(ISynchAsynchConnectionEventHandler handler, Integer keepAlive) {
        this(handler, keepAlive.intValue());
    }

    public Client(ISynchAsynchConnectionEventHandler handler, int keepAlive) {
        this(handler, keepAlive, DEF_MAX_MSG);
    }

    public Client(ISynchAsynchConnectionEventHandler handler, int keepAlive,
            int maxmsgs) {
        this.handler = handler;
        containerID = handler.getEventHandlerID();
        this.keepAlive = keepAlive;
        maxMsg = maxmsgs;
        this.properties = new Properties();
    }

    public synchronized ID getLocalID() {
    	if (containerID != null) return containerID;
        if (socket == null)
            return null;
        ID retID = null;
        try {
            retID = IDFactory.makeStringID(PROTOCOL + "://"
                    + socket.getLocalAddress().getHostName() + ":" + socket.getLocalPort());
        } catch (Exception e) {
            return null;
        }
        return retID;
    }

    public synchronized void removeCommEventListener(IConnectionEventHandler l) {
        eventNotify.remove(l);
    }

    public synchronized void addCommEventListener(IConnectionEventHandler l) {
        if (eventNotify == null) {
            eventNotify = new Vector();
        }
        eventNotify.add(l);
    }

    public synchronized boolean isConnected() {
        if (socket != null) {
            return socket.isConnected();
        }
        return false;
    }

    public synchronized boolean isStarted() {
        if (sendThread != null) {
            return sendThread.isAlive();
        }
        return false;
    }

    protected void fireSuspect(Exception e) {
        Vector v = null;
        synchronized (this) {
            if (eventNotify == null)
                return;
            v = eventNotify;
        }
        for (Enumeration en = v.elements(); en.hasMoreElements();) {
            IConnectionEventHandler h = (IConnectionEventHandler) en
                    .nextElement();
            h.handleSuspectEvent(new ConnectionEvent(this, e));
        }
    }

    public synchronized Object connect(ID remote, Object data, int timeout)
            throws IOException {
        trace("connect(" + remote + "," + data + "," + timeout + ")");
        if (socket != null)
            throw new ConnectException("Already connected to "+getAddressPort());
        // parse URI
        URI anURI = null;
        try {
            anURI = remote.toURI();
        } catch (URISyntaxException e) {
            throw new IOException("Invalid URL");
        }
        // Get socket factory and create/connect socket
        SocketFactory fact = SocketFactory.getSocketFactory();
        if (fact == null) {
            fact = SocketFactory.getDefaultSocketFactory();
        }
        Socket s = fact.createSocket(anURI.getHost(), anURI.getPort(), timeout);
        // Now we've got a connection so set our socket
        setSocket(s);
        outputStream = new ExObjectOutputStream(new BufferedOutputStream(s
                .getOutputStream()), false);
        outputStream.flush();
        inputStream = new ExObjectInputStream(s.getInputStream(),
                false);
        trace("connect;" + anURI);
        // send connect data and get syncronous response
        sendIt(new ConnectRequestMessage(anURI, (Serializable) data));
        ConnectResultMessage res = null;
        res = (ConnectResultMessage) readObject();
        trace("connect;rcv:"+ res);
        // Setup threads
        setupThreads();
        // Return results.
        Object ret = res.getData();
        trace("connect;returning:"+ret);
        return ret;
    }

    private void setupThreads() {
        // Setup threads
    	trace("setupThreads()");
        sendThread = (Thread) AccessController
                .doPrivileged(new PrivilegedAction() {
                    public Object run() {
                        return getSendThread();
                    }
                });
        rcvThread = (Thread) AccessController
                .doPrivileged(new PrivilegedAction() {
                    public Object run() {
                        return getRcvThread();
                    }
                });
    }

    private Thread getSendThread() {
        Thread aThread = new Thread(new Runnable() {
            public void run() {
                int msgCount = 0;
                Thread me = Thread.currentThread();
                // Loop until done sending messages
                for (;;) {
                    if (me.isInterrupted())
                        break;
                    Serializable aMsg = (Serializable) queue.peekQueue();
                    if (me.isInterrupted() || aMsg == null)
                        break;
                    try {
                        // Actually send message
                        trace("send:" + aMsg);
                        sendIt(aMsg);
                        // Successful...remove message from queue
                        queue.removeHead();
                        if (msgCount > maxMsg) {
                            synchronized (outputStream) {
                                outputStream.reset();
                            }
                            msgCount = 0;
                        } else
                            msgCount++;
                    } catch (IOException e) {
                        if (isClosing) {
                            //isClosing = false;
                            dumpStack("SENDER CLOSING",e);
                            synchronized (Client.this) {
                                Client.this.notifyAll();
                            }
                        } else {
                            dumpStack("SENDER EXCEPTION",e);
                            if (!handler.handleSuspectEvent(new ConnectionEvent(
                                    Client.this, e))) {
                                handler
                                        .handleDisconnectEvent(new DisconnectConnectionEvent(
                                                Client.this, e, queue));
                            }
                        }
                        break;
                    }
                }
                trace("SENDER TERMINATING");
            }
        }, getLocalID() + ":sndr:" + getAddressPort());
        // Set priority for new thread
        aThread.setPriority(SNDR_PRIORITY);
        return aThread;
    }

    private void closeSocket() {
        try {
            if (socket != null) {
                socket.close();
                setSocket(null);
            }
        } catch (IOException e) {
        	dumpStack("socket close",e);
        }
    }

    private void sendIt(Serializable snd) throws IOException {
        // Write object to output stream
    	trace("sendIt("+snd+")");
        synchronized (outputStream) {
            outputStream.writeObject(snd);
            outputStream.flush();
            nextPingTime = System.currentTimeMillis() + (keepAlive/2);
        }
    }

    private void receiveResp() {
        synchronized (outputStream) {
            waitForPing = false;
            nextPingTime = System.currentTimeMillis() + (keepAlive/2);
            outputStream.notifyAll();
        }
    }

    public void setCloseTimeout(long t) {
        closeTimeout = t;
    }

    private void sendClose(Serializable snd) throws IOException {
        isClosing = true;
        trace("sendClose(" + snd + ")");
        sendIt(snd);
        if (isClosing) {
            try {
                wait(closeTimeout);
            } catch (InterruptedException e) {
            	dumpStack("sendClose wait",e);
            }
        }
    }

    private Thread getRcvThread() {
        Thread aThread = new Thread(new Runnable() {
            public void run() {
                Thread me = Thread.currentThread();
                // Loop forever and handle objects received.
                for (;;) {
                    if (me.isInterrupted())
                        break;
                    try {
                        handleRcv(readObject());
                    } catch (IOException e) {
                        if (isClosing) {
                            dumpStack("RCVR CLOSING",e);
                            synchronized (Client.this) {
                                Client.this.notifyAll();
                            }
                        } else {
                            dumpStack("RCVR EXCEPTION",e);
                            if (!handler.handleSuspectEvent(new ConnectionEvent(
                                    Client.this, e))) {
                                handler
                                        .handleDisconnectEvent(new DisconnectConnectionEvent(
                                                Client.this, e, queue));
                            }
                        }
                        break;
                    }
                }
                trace("RCVR TERMINATING");
            }
        }, getLocalID() + ":rcvr:" + getAddressPort());
        // Set priority and return
        aThread.setPriority(RCVR_PRIORITY);
        return aThread;
    }

    private void handleRcv(Serializable rcv) throws IOException {
        try {
            // We've received some data, so the connection is alive
            receiveResp();
            // Handle all messages
            if (rcv instanceof SynchMessage) {
                // Handle synch message. The only valid synch message is
                // 'close'.
                trace("recv:" + rcv);
                handler.handleSynchEvent(new SynchConnectionEvent(this,
                        ((SynchMessage) rcv).getData()));
            } else if (rcv instanceof AsynchMessage) {
                trace("recv:" + rcv);
                Serializable d = ((AsynchMessage) rcv).getData();
                // Handle asynch messages.
                handler.handleAsynchEvent(new AsynchConnectionEvent(this, d));
            } else if (rcv instanceof PingMessage) {
                // Handle ping by sending response back immediately
            	trace("recv:" + rcv);
                sendIt(pingResp);
            } else if (rcv instanceof PingResponseMessage) {
                // Do nothing with ping response
            } else
                throw new IOException("Invalid message received.");
        } catch (IOException e) {
            disconnect();
            throw e;
        }
    }
    public synchronized void start() {
        trace("start()");
        if (sendThread != null)
            sendThread.start();
        if (rcvThread != null)
            rcvThread.start();
        // Setup and start keep alive thread
        if (keepAlive != 0)
            keepAliveThread = setupPing();
        if (keepAliveThread != null)
            keepAliveThread.start();
    }

    public void stop() {
    	trace("stop()");
    }

    private Thread setupPing() {
    	trace("setupPing()");
    	final int pingStartWait = (new Random()).nextInt(keepAlive / 2);
        return new Thread(new Runnable() {
            public void run() {
                Thread me = Thread.currentThread();
                // Sleep a random interval to start
                try {
                	Thread.sleep(pingStartWait);
                } catch (InterruptedException e) {
                	return;
                }
                while (!queue.isStopped()) {
                    try {
                        if (me.isInterrupted())
                            break;
                        // Sleep for timeout interval divided by two
                        Thread.sleep(keepAlive / 2);
                        if (me.isInterrupted())
                            break;
                        // Check to see how long it has been since our last
                        // send.
                        synchronized (outputStream) {
                            if (System.currentTimeMillis() >= nextPingTime) {
                                // If it's been longer than our timeout
                                // interval, then ping
                                waitForPing = true;
                                // Actually send ping instance
                                sendIt(ping);
                                if (waitForPing) {
                                    try {
                                        // Wait for keepAliveInterval for
                                        // pingresp
                                        outputStream.wait(keepAlive / 2);
                                    } catch (InterruptedException e) {
                                    }
                                }
                                if (waitForPing) {
                                    throw new IOException(getAddressPort()+ " not reachable");
                                }
                            }
                        }
                    } catch (Exception e) {
                        if (isClosing) {
                            dumpStack("PING CLOSING",e);
                            synchronized (Client.this) {
                                Client.this.notifyAll();
                            }
                        } else {
                            dumpStack("PING EXCEPTION",e);
                            if (!handler.handleSuspectEvent(new ConnectionEvent(
                                    Client.this, e))) {
                                handler
                                        .handleDisconnectEvent(new DisconnectConnectionEvent(
                                                Client.this, e, queue));
                            }
                        }
                        break;
                    }
                }
                trace("PING TERMINATING");
            }
        }, getLocalID()+":ping:"+getAddressPort());
    }

    public synchronized void disconnect() throws IOException {
        trace("disconnect()");
        // Close send queue and socket
        queue.close();
        closeSocket();
        // Notify sender in case it's waiting for a response
        // Zap keep alive thread
        if (keepAliveThread != null) {
            keepAliveThread.interrupt();
            keepAliveThread = null;
        }
        if (sendThread != null) {
            sendThread.interrupt();
            sendThread = null;
        }
        if (rcvThread != null) {
            rcvThread.interrupt();
            rcvThread = null;
        }
        // Notify any threads waiting to get hold of our lock
        notifyAll();
    }

    public void sendAsynch(ID recipient, byte[] obj) throws IOException {
        queueObject(recipient, obj);
    }

    public void sendAsynch(ID recipient, Object obj) throws IOException {
        queueObject(recipient, (Serializable) obj);
    }

    public synchronized void queueObject(ID recipient, Serializable obj)
            throws IOException {
        if (queue.isStopped() || isClosing)
            throw new ConnectException("Not connected");
        trace("queueObject("+recipient+","+obj+")");
        queue.enqueue(new AsynchMessage(obj));
    }

    public synchronized Serializable sendObject(ID recipient, Serializable obj)
            throws IOException {
        if (queue.isStopped() || isClosing)
            throw new ConnectException("Not connected");
        trace("queueObject("+recipient+","+obj+")");
        sendClose(new SynchMessage(obj));
        return null;
    }

    public Object sendSynch(ID rec, Object obj) throws IOException {
        trace("sendSynch("+rec+","+obj+")");
        return sendObject(rec, (Serializable) obj);
    }

    public Object sendSynch(ID rec, byte[] obj) throws IOException {
        trace("sendSynch("+rec+","+obj+")");
        return sendObject(rec, obj);
    }

    private Serializable readObject() throws IOException {
        Serializable ret = null;
        try {
            ret = (Serializable) inputStream.readObject();
        } catch (ClassNotFoundException e) {
            dumpStack("readObject;classnotfoundexception", e);
            throw new IOException(
                    "Protocol violation due to class load failure.  "
                            + e.getMessage());
        }
        return ret;
    }
}
 No newline at end of file
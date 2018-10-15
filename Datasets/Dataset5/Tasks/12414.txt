super("Optimistic Unchoking Thread " //$NON-NLS-1$

/*******************************************************************************
 * Copyright (c) 2006, 2008 Remy Suen, Composent Inc., and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Remy Suen <remy.suen@gmail.com> - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.protocol.bittorrent.internal.net;

import java.io.UnsupportedEncodingException;
import java.net.Socket;
import java.nio.channels.SocketChannel;
import java.util.LinkedList;
import java.util.Random;
import java.util.Vector;

/**
 * A pool of threads to be allocated when a connection needs to be made with a
 * peer.
 */
class ConnectionPool {

	/**
	 * A shared <code>Random</code> instance to randomly select a piece to
	 * request from peers.
	 */
	static final Random RANDOM = new Random();

	/**
	 * The number of seconds to wait before rotating optimistic unchokes.
	 */
	private static final int OPTIMISTIC_UNCHOKE_ROTATION_TIME = 30;

	/**
	 * The maximum number of peers that are allowed to be unchoked on a
	 * persistent basis.
	 */
	private static final int MAX_UNCHOKED_PEERS = 4;

	private final Vector connections;

	private final LinkedList targets;

	/**
	 * The manager associated with this pool.
	 */
	private final TorrentManager manager;

	private Thread unchokingThread;

	/**
	 * The maximum number of connections that this pool should be managing. This
	 * can be set with the {@link #setMaxConnections(int)} method, but should be
	 * increased with caution as it may cause TCP congestions.
	 */
	private int maxConnections = 50;

	/**
	 * The number of active connections.
	 */
	private int size = 0;

	/**
	 * The number of unchoked peers.
	 */
	private int unchokedPeers = 0;

	private boolean connected = false;

	ConnectionPool(TorrentManager manager) {
		this.manager = manager;
		connections = new Vector(maxConnections);
		targets = new LinkedList();
	}

	private synchronized void unchoke() {
		if (size <= MAX_UNCHOKED_PEERS || unchokedPeers < MAX_UNCHOKED_PEERS) {
			return;
		}

		int unchoke = RANDOM.nextInt(size);
		PeerConnection connection = (PeerConnection) connections.get(unchoke);
		while (connection.isChoking()) {
			unchoke = RANDOM.nextInt(size);
			connection = (PeerConnection) connections.get(unchoke);
		}
		connection.queueUnchokeMessage();

		int choke = RANDOM.nextInt(size);
		connection = (PeerConnection) connections.get(choke);
		while (choke != unchoke && !connection.isChoking()) {
			choke = RANDOM.nextInt(size);
			connection = (PeerConnection) connections.get(choke);
		}
		connection.queueChokeMessage();
	}

	/**
	 * Creates a connection to the specified ip at the given port. If the
	 * current number of active threads is equal to the maximum number of
	 * allowed connections, <code>false</code> will be returned.
	 * 
	 * @param ip
	 *            the IP of the peer
	 * @param port
	 *            the port that the peer is listening on
	 * @throws UnsupportedEncodingException
	 *             If the <code>ISO-8859-1</code> encoding is not supported
	 */
	void connectTo(String ip, int port) throws UnsupportedEncodingException {
		if (unchokingThread == null) {
			unchokingThread = new OptimisticUnchokingThread();
			unchokingThread.start();
		} else if (size == maxConnections) {
			return;
		}
		connected = true;

		synchronized (this) {
			for (int i = 0; i < connections.size(); i++) {
				PeerConnection connection = (PeerConnection) connections.get(i);
				if (connection.isInitialized()
						&& connection.isConnectedTo(ip, port)) {
					return;
				}
			}

			targets.add(new ConnectionInfo(ip, port));
			for (int i = 0; i < connections.size(); i++) {
				if (!((PeerConnection) connections.get(i)).isInitialized()) {
					notify();
					return;
				}
			}
			PeerConnection connection = new PeerConnection(this, manager);
			connections.add(connection);
			connection.start();
		}
	}

	void connectTo(SocketChannel channel) throws UnsupportedEncodingException {
		if (unchokingThread == null) {
			unchokingThread = new OptimisticUnchokingThread();
			unchokingThread.start();
		} else if (size == maxConnections) {
			return;
		}
		connected = true;

		Socket socket = channel.socket();
		String ip = socket.getLocalAddress().getHostAddress();
		int port = socket.getLocalPort();
		synchronized (this) {
			for (int i = 0; i < connections.size(); i++) {
				PeerConnection connection = (PeerConnection) connections.get(i);
				if (connection.isConnectedTo(ip, port)) {
					return;
				}
			}

			targets.add(new ConnectionInfo(channel));
			for (int i = 0; i < connections.size(); i++) {
				if (!((PeerConnection) connections.get(i)).isInitialized()) {
					notify();
					return;
				}
			}
			PeerConnection connection = new PeerConnection(this, manager);
			connections.add(connection);
			connection.start();
		}
	}

	/**
	 * Closes all of the channels that are currently active.
	 */
	synchronized void close() {
		connected = false;
		for (int i = 0; i < connections.size(); i++) {
			((PeerConnection) connections.get(i)).close();
		}
		targets.clear();
		notifyAll();
	}

	synchronized boolean isConnected() {
		return connected;
	}

	ConnectionInfo dequeue() {
		synchronized (targets) {
			return targets.isEmpty() ? null : (ConnectionInfo) targets
					.removeFirst();
		}
	}

	/**
	 * Disconnects all connections to peers that are seeds. This is called after
	 * the downloading has completed successfully since it is no longer
	 * necessary to be connected to seeds since no pieces will be requested.
	 */
	void disconnectSeeds() {
		for (int i = 0; i < connections.size(); i++) {
			PeerConnection connection = (PeerConnection) connections.get(i);
			if (connection.isInitialized() && connection.isSeed()) {
				connection.close();
			}
		}
	}

	/**
	 * Called to inform this pool that one of the unchoked connections has been
	 * now been choked. This allows for another peer to be unchoked permanently
	 * during the next rotation.
	 */
	void unchokedPeerCleared() {
		unchokedPeers--;
	}

	/**
	 * Sets the maximum number of connections that this pool should manage.
	 * 
	 * @param maxConnections
	 *            the maximum amount of connections to manage
	 */
	synchronized void setMaxConnections(int maxConnections) {
		if (this.maxConnections < maxConnections) {
			connections.ensureCapacity(maxConnections);
		} else if (this.maxConnections > maxConnections) {
			// push back all active connections
			for (int i = 0; i < maxConnections; i++) {
				if (!((PeerConnection) connections.get(i)).isInitialized()) {
					for (int j = connections.size(); j > i; j--) {
						PeerConnection conn = (PeerConnection) connections
								.get(j);
						if (conn.isInitialized()) {
							connections.remove(i);
							connections.add(i, connections.remove(j - 1));
						}
					}
				}
			}
			// close all extraneous connections
			for (int i = maxConnections; i < this.maxConnections; i++) {
				((PeerConnection) connections.get(i)).close();
			}
		}
		this.maxConnections = maxConnections;
	}

	synchronized boolean checkUnchoke() {
		if (unchokedPeers == MAX_UNCHOKED_PEERS) {
			return false;
		}
		unchokedPeers++;
		return true;
	}

	void connectionCreated() {
		size++;
	}

	/**
	 * Indicates to the pool that a connection has ended. This means that one of
	 * the {@link PeerConnection}s are no longer running.
	 */
	void connectionClosed() {
		size--;
		if (size == 0 && unchokingThread != null) {
			unchokingThread.interrupt();
			unchokingThread = null;
		}
	}

	void connectionDestroyed(PeerConnection connection) {
		connections.remove(connection);
	}

	/**
	 * Retrieves the current number of active connections.
	 * 
	 * @return the number of active connections of this pool
	 */
	int getConnected() {
		return size;
	}

	/**
	 * Instructs all running threads to send a have message of the specified
	 * piece to the connected peer.
	 * 
	 * @param piece
	 *            the number of the piece that the have message should
	 *            correspond to
	 */
	void queueHaveMessage(int piece) {
		for (int i = 0; i < connections.size(); i++) {
			PeerConnection connection = (PeerConnection) connections.get(i);
			if (connection.isInitialized()) {
				connection.queueHaveMessage(piece);
			}
		}
	}

	boolean isEmpty() {
		return connections.isEmpty();
	}

	private class OptimisticUnchokingThread extends Thread {

		public OptimisticUnchokingThread() {
			super("Optimistic Unchoking Thread "
					+ manager.getTorrentFile().getName());
		}

		public void run() {
			while (true) {
				for (int i = 0; i < OPTIMISTIC_UNCHOKE_ROTATION_TIME; i++) {
					try {
						Thread.sleep(1000);
					} catch (InterruptedException e) {
						return;
					}
					for (int j = 0; j < connections.size(); j++) {
						PeerConnection conn = (PeerConnection) connections
								.get(j);
						if (conn.isInitialized()) {
							conn.queueSpeeds();
						}
					}
				}
				unchoke();
			}
		}
	}

}
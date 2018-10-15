package org.eclipse.ecf.provider.filetransfer.retrieve;

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

package org.eclipse.ecf.internal.provider.filetransfer.retrieve;

import java.io.IOException;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.net.UnknownHostException;

import javax.net.ssl.SSLContext;
import javax.net.ssl.TrustManager;

import org.apache.commons.httpclient.ConnectTimeoutException;
import org.apache.commons.httpclient.Credentials;
import org.apache.commons.httpclient.ProxyClient;
import org.apache.commons.httpclient.UsernamePasswordCredentials;
import org.apache.commons.httpclient.auth.AuthScope;
import org.apache.commons.httpclient.params.HttpConnectionParams;
import org.apache.commons.httpclient.protocol.ProtocolSocketFactory;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.ecf.core.util.Proxy;
import org.eclipse.ecf.internal.provider.filetransfer.Activator;

public class SslProtocolSocketFactory implements ProtocolSocketFactory {

	private SSLContext sslContext;

	private Proxy proxy;

	public SslProtocolSocketFactory(Proxy proxy) {
		this.proxy = proxy;
	}

	private SSLContext getSslContext() {
		if (sslContext == null) {
			try {
				sslContext = SSLContext.getInstance("SSL");
				sslContext.init(null,
						new TrustManager[] { new HttpClientSslTrustManager() },
						null);
			} catch (Exception e) {
				Activator.getDefault().getLog().log(
						new Status(IStatus.ERROR, Activator.PLUGIN_ID, 1111,
								"SslProtocolSocketFactory", e));
			}
		}
		return sslContext;
	}

	public Socket createSocket(String remoteHost, int remotePort)
			throws IOException, UnknownHostException {
		return getSslContext().getSocketFactory().createSocket(remoteHost,
				remotePort);
	}

	public Socket createSocket(String remoteHost, int remotePort,
			InetAddress clientHost, int clientPort) throws IOException,
			UnknownHostException {
		return getSslContext().getSocketFactory().createSocket(remoteHost,
				remotePort, clientHost, clientPort);
	}

	public Socket createSocket(String remoteHost, int remotePort,
			InetAddress clientHost, int clientPort, HttpConnectionParams params)
			throws IOException, UnknownHostException, ConnectTimeoutException {
		if (params == null || params.getConnectionTimeout() == 0)
			return getSslContext().getSocketFactory().createSocket(remoteHost,
					remotePort, clientHost, clientPort);

		if (proxy != null && !Proxy.NO_PROXY.equals(proxy)
				&& proxy.getAddress() instanceof InetSocketAddress) {
			ProxyClient proxyClient = new ProxyClient();

			InetSocketAddress address = (InetSocketAddress) proxy.getAddress();
			proxyClient.getHostConfiguration().setProxy(address.getHostName(),
					address.getPort());
			proxyClient.getHostConfiguration().setHost(remoteHost, remotePort);
			String proxyUsername = proxy.getUsername();
			String proxyPassword = proxy.getPassword();
			if (proxyUsername != null && !proxyUsername.equals("")) {
				Credentials credentials = new UsernamePasswordCredentials(
						proxyUsername, proxyPassword);
				AuthScope proxyAuthScope = new AuthScope(address.getHostName(),
						address.getPort(), AuthScope.ANY_REALM);
				proxyClient.getState().setProxyCredentials(proxyAuthScope,
						credentials);
			}

			ProxyClient.ConnectResponse response = proxyClient.connect();
			if (response.getSocket() != null) {
				// tunnel SSL via the resultant socket
				Socket sslsocket = getSslContext().getSocketFactory()
						.createSocket(response.getSocket(), remoteHost,
								remotePort, true);
				return sslsocket;
			}
		}
		// Direct connection
		Socket socket = getSslContext().getSocketFactory().createSocket();
		socket.bind(new InetSocketAddress(clientHost, clientPort));
		socket.connect(new InetSocketAddress(remoteHost, remotePort), params
				.getConnectionTimeout());
		return socket;
	}

}
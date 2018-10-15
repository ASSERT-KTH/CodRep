public static boolean supportsProtocol(String protocolString) {

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.internal.provider.filetransfer.retrieve;

import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.InetSocketAddress;
import java.util.Map;

import javax.security.auth.login.LoginException;

import org.apache.commons.httpclient.Credentials;
import org.apache.commons.httpclient.HttpClient;
import org.apache.commons.httpclient.UsernamePasswordCredentials;
import org.apache.commons.httpclient.auth.AuthScope;
import org.apache.commons.httpclient.methods.GetMethod;
import org.apache.commons.httpclient.protocol.Protocol;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.security.Callback;
import org.eclipse.ecf.core.security.CallbackHandler;
import org.eclipse.ecf.core.security.IConnectContext;
import org.eclipse.ecf.core.security.NameCallback;
import org.eclipse.ecf.core.security.ObjectCallback;
import org.eclipse.ecf.core.security.UnsupportedCallbackException;
import org.eclipse.ecf.core.util.Proxy;
import org.eclipse.ecf.filetransfer.IIncomingFileTransfer;
import org.eclipse.ecf.filetransfer.IncomingFileTransferException;
import org.eclipse.ecf.filetransfer.events.IIncomingFileTransferReceiveStartEvent;
import org.eclipse.ecf.filetransfer.identity.IFileID;
import org.eclipse.ecf.internal.provider.filetransfer.identity.FileTransferID;

public class HttpClientRetrieveFileTransfer extends
		AbstractRetrieveFileTransfer {

	private static final String HTTP_PROXY_PORT = "http.proxyPort";

	private static final String HTTP_PROXY_HOST = "http.proxyHost";

	private static final String USERNAME_PREFIX = "Username:";

	protected static final int DEFAULT_CONNECTION_TIMEOUT = 30000;

	protected static final int HTTP_PORT = 80;

	protected static final int HTTPS_PORT = 443;

	protected static final int MAX_RETRY = 2;

	protected static final String HTTPS = "https";

	protected static final String HTTP = "http";

	protected static final String[] supportedProtocols = { HTTP, HTTPS };

	private GetMethod getMethod = null;

	private HttpClient httpClient = null;

	private IConnectContext fileRequestConnectContext = null;

	private String username;

	private String password;

	private Proxy proxy;

	public HttpClientRetrieveFileTransfer(HttpClient httpClient) {
		if (httpClient == null)
			throw new NullPointerException("httpClient cannot be null"); //$NON-NLS-1$
		this.httpClient = httpClient;
	}

	protected void hardClose() {
		if (getMethod != null) {
			getMethod.releaseConnection();
			getMethod = null;
		}
		super.hardClose();
	}

	protected Credentials getFileRequestCredentials()
			throws UnsupportedCallbackException, IOException {
		if (fileRequestConnectContext == null)
			return null;
		CallbackHandler callbackHandler = fileRequestConnectContext
				.getCallbackHandler();
		if (callbackHandler == null)
			return null;
		NameCallback usernameCallback = new NameCallback(USERNAME_PREFIX);
		ObjectCallback passwordCallback = new ObjectCallback();
		callbackHandler.handle(new Callback[] { usernameCallback,
				passwordCallback });
		username = usernameCallback.getName();
		password = (String) passwordCallback.getObject();
		return new UsernamePasswordCredentials(username, password);
	}

	private Proxy getSystemProxy() {
		String systemHttpProxyHost = System.getProperty(HTTP_PROXY_HOST, null);
		String systemHttpProxyPort = System.getProperty(HTTP_PROXY_PORT, ""
				+ HTTP_PORT);
		int port = -1;
		try {
			port = Integer.parseInt(systemHttpProxyPort);
		} catch (Exception e) {

		}
		if (systemHttpProxyHost == null || systemHttpProxyHost.equals(""))
			return null;
		return new Proxy(Proxy.Type.HTTP, new InetSocketAddress(
				systemHttpProxyHost, port));
	}

	protected void setupProxy(String urlString) {
		if (proxy == null)
			proxy = getSystemProxy();
		if (proxy != null && !Proxy.NO_PROXY.equals(proxy)
				&& !urlUsesHttps(urlString)
				&& proxy.getAddress() instanceof InetSocketAddress) {
			InetSocketAddress address = (InetSocketAddress) proxy.getAddress();
			httpClient.getHostConfiguration().setProxy(
					getHostFromURL(address.getHostName()), address.getPort());
			String proxyUsername = proxy.getUsername();
			String proxyPassword = proxy.getPassword();
			if (username != null) {
				Credentials credentials = new UsernamePasswordCredentials(
						proxyUsername, proxyPassword);
				AuthScope proxyAuthScope = new AuthScope(address.getHostName(),
						address.getPort(), AuthScope.ANY_REALM);
				httpClient.getState().setProxyCredentials(proxyAuthScope,
						credentials);
			}
		}
	}

	protected void setupAuthentication(String urlString)
			throws UnsupportedCallbackException, IOException {
		Credentials credentials = null;
		if (username == null) {
			credentials = getFileRequestCredentials();
		}

		if (credentials != null && username != null) {
			AuthScope authScope = new AuthScope(getHostFromURL(urlString),
					getPortFromURL(urlString), AuthScope.ANY_REALM);
			httpClient.getState().setCredentials(authScope, credentials);
		}
	}

	protected void setupHostAndPort(String urlString) {
		if (urlUsesHttps(urlString)) {
			Protocol acceptAllSsl = new Protocol(HTTPS,
					new SslProtocolSocketFactory(proxy),
					getPortFromURL(urlString));
			httpClient.getHostConfiguration().setHost(
					getHostFromURL(urlString), getPortFromURL(urlString),
					acceptAllSsl);
		} else {
			httpClient.getHostConfiguration().setHost(
					getHostFromURL(urlString), getPortFromURL(urlString));
		}
	}

	protected void openStreams(Map options) throws IncomingFileTransferException {
		String urlString = getRemoteFileURL().toString();

		try {
			httpClient.getHttpConnectionManager().getParams().setSoTimeout(
					DEFAULT_CONNECTION_TIMEOUT);
			httpClient.getHttpConnectionManager().getParams()
					.setConnectionTimeout(DEFAULT_CONNECTION_TIMEOUT);

			setupProxy(urlString);

			setupAuthentication(urlString);

			setupHostAndPort(urlString);

			getMethod = new GetMethod(urlString);
			getMethod.setFollowRedirects(true);

			int code = httpClient.executeMethod(getMethod);

			if (code == HttpURLConnection.HTTP_OK) {
				long contentLength = getMethod.getResponseContentLength();
				setInputStream(getMethod.getResponseBodyAsStream());
				setFileLength(contentLength);

				listener
						.handleTransferEvent(new IIncomingFileTransferReceiveStartEvent() {
							private static final long serialVersionUID = -59096575294481755L;

							public IFileID getFileID() {
								return remoteFileID;
							}

							public IIncomingFileTransfer receive(
									File localFileToSave) throws IOException {
								setOutputStream(new BufferedOutputStream(
										new FileOutputStream(localFileToSave)));
								job = new FileTransferJob(getRemoteFileURL()
										.toString());
								job.schedule();
								return HttpClientRetrieveFileTransfer.this;
							}

							public String toString() {
								StringBuffer sb = new StringBuffer(
										"IIncomingFileTransferReceiveStartEvent[");
								sb.append("isdone=").append(done).append(";");
								sb.append("bytesReceived=").append(
										bytesReceived).append("]");
								return sb.toString();
							}

							public void cancel() {
								hardClose();
							}

							public IIncomingFileTransfer receive(
									OutputStream streamToStore)
									throws IOException {
								setOutputStream(new BufferedOutputStream(
										streamToStore));
								setCloseOutputStream(false);
								job = new FileTransferJob(getRemoteFileURL()
										.toString());
								job.schedule();
								return HttpClientRetrieveFileTransfer.this;
							}

						});
			} else if (code == HttpURLConnection.HTTP_UNAUTHORIZED
					|| code == HttpURLConnection.HTTP_FORBIDDEN) {
				getMethod.getResponseBody();
				// login or reauthenticate due to an expired session
				getMethod.releaseConnection();
				throw new IncomingFileTransferException("Unauthorized");
			} else if (code == HttpURLConnection.HTTP_PROXY_AUTH) {
				throw new LoginException("Proxy Authentication Required");
			} else {
				throw new IOException(
						"HttpClient connection error response code: " + code);
			}
		} catch (Exception e) {
			throw new IncomingFileTransferException("Could not connect to "
					+ urlString, e);
		}

	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.filetransfer.IRetrieveFileTransferContainerAdapter#setConnectContextForAuthentication(org.eclipse.ecf.core.security.IConnectContext)
	 */
	public void setConnectContextForAuthentication(
			IConnectContext connectContext) {
		this.fileRequestConnectContext = connectContext;
		this.username = null;
		this.password = null;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.filetransfer.IRetrieveFileTransferContainerAdapter#setProxy(org.eclipse.ecf.core.util.Proxy)
	 */
	public void setProxy(Proxy proxy) {
		this.proxy = proxy;
	}

	protected static String getHostFromURL(String url) {
		String result = url;
		int colonSlashSlash = url.indexOf("://"); //$NON-NLS-1$

		if (colonSlashSlash >= 0) {
			result = url.substring(colonSlashSlash + 3);
		}

		int colonPort = result.indexOf(':'); //$NON-NLS-1$
		int requestPath = result.indexOf('/'); //$NON-NLS-1$

		int substringEnd;

		if (colonPort > 0 && requestPath > 0)
			substringEnd = Math.min(colonPort, requestPath);
		else if (colonPort > 0)
			substringEnd = colonPort;
		else if (requestPath > 0)
			substringEnd = requestPath;
		else
			substringEnd = result.length();

		return result.substring(0, substringEnd);

	}

	protected static int getPortFromURL(String url) {
		int colonSlashSlash = url.indexOf("://"); //$NON-NLS-1$
		int colonPort = url.indexOf(':', colonSlashSlash + 1); //$NON-NLS-1$
		if (colonPort < 0)
			return urlUsesHttps(url) ? HTTPS_PORT : HTTP_PORT;

		int requestPath = url.indexOf('/', colonPort + 1); //$NON-NLS-1$

		int end;
		if (requestPath < 0)
			end = url.length();
		else
			end = requestPath;

		return Integer.parseInt(url.substring(colonPort + 1, end));
	}

	protected static boolean urlUsesHttps(String url) {
		return url.matches(HTTPS + ".*"); //$NON-NLS-1$
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.internal.provider.filetransfer.AbstractRetrieveFileTransfer#supportsProtocol(java.lang.String)
	 */
	public boolean supportsProtocol(String protocolString) {
		for (int i = 0; i < supportedProtocols.length; i++)
			if (supportedProtocols[i].equalsIgnoreCase(protocolString))
				return true;
		return false;
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.core.identity.IIdentifiable#getID()
	 */
	public ID getID() {
		return new FileTransferID(getRetrieveNamespace(),getRemoteFileURL());
	}

}
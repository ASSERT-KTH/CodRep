throw new IncomingFileTransferException("HttpClient Provider is not configured to support NTLM proxy authentication.", HttpClientOptions.NTLM_PROXY_RESPONSE_CODE); //$NON-NLS-1$

/*******************************************************************************
 * Copyright (c) 2004, 2009 Composent, Inc., IBM All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors: 
 *  Composent, Inc. - initial API and implementation
 *  Maarten Meijer - bug 237936, added gzip encoded transfer default
 *  Henrich Kraemer - bug 263869, testHttpsReceiveFile fails using HTTP proxy
 *  Henrich Kraemer - bug 263613, [transport] Update site contacting / downloading is not cancelable
 ******************************************************************************/
package org.eclipse.ecf.provider.filetransfer.httpclient;

import java.io.IOException;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.Socket;
import java.util.Iterator;
import java.util.Map;
import javax.net.SocketFactory;
import org.apache.commons.httpclient.Credentials;
import org.apache.commons.httpclient.Header;
import org.apache.commons.httpclient.HostConfiguration;
import org.apache.commons.httpclient.HttpClient;
import org.apache.commons.httpclient.HttpConnection;
import org.apache.commons.httpclient.HttpException;
import org.apache.commons.httpclient.HttpState;
import org.apache.commons.httpclient.HttpStatus;
import org.apache.commons.httpclient.HttpVersion;
import org.apache.commons.httpclient.NTCredentials;
import org.apache.commons.httpclient.UsernamePasswordCredentials;
import org.apache.commons.httpclient.auth.AuthScope;
import org.apache.commons.httpclient.auth.CredentialsProvider;
import org.apache.commons.httpclient.methods.GetMethod;
import org.apache.commons.httpclient.protocol.Protocol;
import org.apache.commons.httpclient.protocol.ProtocolSocketFactory;
import org.apache.commons.httpclient.protocol.SecureProtocolSocketFactory;
import org.apache.commons.httpclient.util.DateUtil;
import org.eclipse.core.runtime.Assert;
import org.eclipse.core.runtime.IPath;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.NullProgressMonitor;
import org.eclipse.core.runtime.Path;
import org.eclipse.core.runtime.Status;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.security.Callback;
import org.eclipse.ecf.core.security.CallbackHandler;
import org.eclipse.ecf.core.security.IConnectContext;
import org.eclipse.ecf.core.security.NameCallback;
import org.eclipse.ecf.core.security.ObjectCallback;
import org.eclipse.ecf.core.security.UnsupportedCallbackException;
import org.eclipse.ecf.core.util.Proxy;
import org.eclipse.ecf.core.util.ProxyAddress;
import org.eclipse.ecf.core.util.Trace;
import org.eclipse.ecf.filetransfer.FileTransferJob;
import org.eclipse.ecf.filetransfer.IFileRangeSpecification;
import org.eclipse.ecf.filetransfer.IFileTransferPausable;
import org.eclipse.ecf.filetransfer.IFileTransferRunnable;
import org.eclipse.ecf.filetransfer.IncomingFileTransferException;
import org.eclipse.ecf.filetransfer.InvalidFileRangeSpecificationException;
import org.eclipse.ecf.filetransfer.events.IFileTransferConnectStartEvent;
import org.eclipse.ecf.filetransfer.events.socket.ISocketEventSource;
import org.eclipse.ecf.filetransfer.events.socket.ISocketListener;
import org.eclipse.ecf.filetransfer.identity.IFileID;
import org.eclipse.ecf.internal.provider.filetransfer.httpclient.Activator;
import org.eclipse.ecf.internal.provider.filetransfer.httpclient.ConnectingSocketMonitor;
import org.eclipse.ecf.internal.provider.filetransfer.httpclient.DebugOptions;
import org.eclipse.ecf.internal.provider.filetransfer.httpclient.ECFHttpClientProtocolSocketFactory;
import org.eclipse.ecf.internal.provider.filetransfer.httpclient.ECFHttpClientSecureProtocolSocketFactory;
import org.eclipse.ecf.internal.provider.filetransfer.httpclient.HttpClientProxyCredentialProvider;
import org.eclipse.ecf.internal.provider.filetransfer.httpclient.ISSLSocketFactoryModifier;
import org.eclipse.ecf.internal.provider.filetransfer.httpclient.Messages;
import org.eclipse.ecf.provider.filetransfer.events.socket.SocketEventSource;
import org.eclipse.ecf.provider.filetransfer.identity.FileTransferID;
import org.eclipse.ecf.provider.filetransfer.retrieve.AbstractRetrieveFileTransfer;
import org.eclipse.ecf.provider.filetransfer.retrieve.HttpHelper;
import org.eclipse.ecf.provider.filetransfer.util.JREProxyHelper;
import org.eclipse.osgi.util.NLS;

public class HttpClientRetrieveFileTransfer extends AbstractRetrieveFileTransfer {

	/**
	 * gzip encoding wrapper for httpclient class. Copied from Mylyn project, bug 205708
	 *
	 */
	public class GzipGetMethod extends GetMethod {

		private static final String CONTENT_ENCODING = "Content-Encoding"; //$NON-NLS-1$
		private static final String ACCEPT_ENCODING = "Accept-encoding"; //$NON-NLS-1$
		private static final String CONTENT_ENCODING_GZIP = "gzip"; //$NON-NLS-1$

		private static final String CONTENT_ENCODING_ACCEPTED = CONTENT_ENCODING_GZIP;

		private boolean gzipReceived = false;

		public GzipGetMethod(String urlString) {
			super(urlString);
		}

		private boolean isZippedResponse() {
			// see bug https://bugs.eclipse.org/bugs/show_bug.cgi?id=269018
			boolean contentEncodingGzip = (null != this.getResponseHeader(CONTENT_ENCODING) && this.getResponseHeader(CONTENT_ENCODING).getValue().equals(CONTENT_ENCODING_GZIP));
			Trace.trace(Activator.PLUGIN_ID, "Content-Encoding: gzip header " + (contentEncodingGzip ? "PRESENT" : "ABSENT")); //$NON-NLS-1$ //$NON-NLS-2$ //$NON-NLS-3$
			boolean hasGzSuffix = targetHasGzSuffix(remoteFileName);
			return contentEncodingGzip && !hasGzSuffix;
		}

		public int execute(HttpState state, HttpConnection conn) throws HttpException, IOException {
			Trace.entering(Activator.PLUGIN_ID, DebugOptions.METHODS_ENTERING, this.getClass(), "GzipGetMethod.execute"); //$NON-NLS-1$
			// Insert accept-encoding header
			int result = super.execute(state, conn);
			// Code to deal with implications described on bug https://bugs.eclipse.org/bugs/show_bug.cgi?id=261881
			switch (result) {
				case HttpStatus.SC_MOVED_TEMPORARILY :
				case HttpStatus.SC_MOVED_PERMANENTLY :
				case HttpStatus.SC_SEE_OTHER :
				case HttpStatus.SC_TEMPORARY_REDIRECT :
					Trace.trace(Activator.PLUGIN_ID, "GzipGetMethod.execute.  Received redirect=" + result + ".  Removing gzip accept encoding"); //$NON-NLS-1$ //$NON-NLS-2$
					gzipReceived = false;
					removeRequestHeader(GzipGetMethod.ACCEPT_ENCODING);
				default :
			}
			// test what is sent back
			Trace.exiting(Activator.PLUGIN_ID, DebugOptions.METHODS_EXITING, this.getClass(), "GzipGetMethod.execute", new Integer(result)); //$NON-NLS-1$
			return result;
		}

		public InputStream getResponseBodyAsUnzippedStream() throws IOException {
			gzipReceived = isZippedResponse();
			InputStream input = super.getResponseBodyAsStream();
			try {
				if (gzipReceived) {
					Trace.trace(Activator.PLUGIN_ID, "Using gzip input stream to decode"); //$NON-NLS-1$
					// extract on the fly
					return new java.util.zip.GZIPInputStream(input);
				}
				Trace.trace(Activator.PLUGIN_ID, "Not using gzip input stream"); //$NON-NLS-1$
			} catch (IOException e) {
				Activator.getDefault().log(new Status(IStatus.WARNING, Activator.PLUGIN_ID, IStatus.WARNING, "Exception creating gzip input stream", e)); //$NON-NLS-1$ 
				throw e;
			}
			return input;
		}

		private Object releaseLock = new Object();

		// This override is a workaround for 
		// https://bugs.eclipse.org/bugs/show_bug.cgi?id=279457
		// This makes GetMethod.releaseConnection non-reentrant,
		// as with reentrancy under some circumstances a NPE can be 
		// thrown with multithreaded access
		public void releaseConnection() {
			synchronized (releaseLock) {
				super.releaseConnection();
			}
		}
	}

	static final class HostConfigHelper {
		private ISocketEventSource source;
		private ISocketListener socketListener;
		private String targetURL;
		private String targetRelativePath;

		private HostConfiguration hostConfiguration;

		public HostConfigHelper(ISocketEventSource source, ISocketListener socketListener) {
			Assert.isNotNull(source);
			this.source = source;
			this.socketListener = socketListener;
			hostConfiguration = new HostConfiguration();
		}

		public HostConfiguration getHostConfiguration() {
			return hostConfiguration;
		}

		// drops the scheme server and port (e.g http://server:8080/a/b.html -> /a/b.html
		private static String getTargetRelativePathFromURL(String url) {
			// RFC 3986
			/* 
			 *      
			 *     URI    = scheme ":" hier-part [ "?" query ] [ "#" fragment ]

			      hier-part =  "//" authority path-abempty
			                 / path-absolute
			                 / path-rootless
			                 / path-empty     
			 *      
			 *      path  = path-abempty    ; begins with "/" or is empty
			              / path-absolute   ; begins with "/" but not "//"
			              / path-noscheme   ; begins with a non-colon segment
			              / path-rootless   ; begins with a segment
			              / path-empty      ; zero characters

			 * 
			 */
			// This routine is supposed to remove authority information from the url
			// to make this a 'relative path' for
			// HttpClients method constructor (for example GetMethod(String uri)) as
			// ECF executes methods passing in a HostConfiguration which represents the
			// authority.
			final int colonSlashSlash = url.indexOf("://"); //$NON-NLS-1$
			if (colonSlashSlash < 0)
				return url;

			// '://' indicates there must be an authority.
			// the authority must not contain a '/' character.
			final int nextSlash = url.indexOf('/', colonSlashSlash + 3);
			if (nextSlash == -1) {
				// try root? or should it be empty?
				return ""; //$NON-NLS-1$ 
			}
			String relativeURL = url.substring(nextSlash); // include the slash
			// This is a workaround for multiple consecutive slashes after the authority.
			// HttpClient will parse this as another authority instead of using 
			// it as a path. In anticipation we add "//example.com" so that this will
			// be removed instead of the first path segment. 
			// See https://bugs.eclipse.org/bugs/show_bug.cgi?id=270749#c28 
			// for a full explanation
			if (relativeURL.startsWith("//")) { //$NON-NLS-1$
				final String host = "example.com"; //$NON-NLS-1$
				relativeURL = "//" + host + relativeURL; //$NON-NLS-1$

			}
			return relativeURL;
		}

		public void setTargetHostByURL(CredentialsProvider credProvider, String url) {
			this.targetURL = url;
			this.targetRelativePath = getTargetRelativePathFromURL(targetURL);
			String host = getHostFromURL(targetURL);
			int port = getPortFromURL(targetURL);

			if (HttpClientRetrieveFileTransfer.urlUsesHttps(targetURL)) {
				ISSLSocketFactoryModifier sslSocketFactoryModifier = Activator.getDefault().getSSLSocketFactoryModifier();
				if (sslSocketFactoryModifier == null) {
					sslSocketFactoryModifier = new HttpClientDefaultSSLSocketFactoryModifier();
				}
				SecureProtocolSocketFactory psf = new ECFHttpClientSecureProtocolSocketFactory(sslSocketFactoryModifier, source, socketListener);
				Protocol sslProtocol = new Protocol(HttpClientRetrieveFileTransfer.HTTPS, (ProtocolSocketFactory) psf, HTTPS_PORT);

				Trace.trace(Activator.PLUGIN_ID, "retrieve host=" + host + ";port=" + port); //$NON-NLS-1$ //$NON-NLS-2$
				hostConfiguration.setHost(host, port, sslProtocol);
				hostConfiguration.getParams().setParameter(CredentialsProvider.PROVIDER, credProvider);

			} else {
				ProtocolSocketFactory psf = new ECFHttpClientProtocolSocketFactory(SocketFactory.getDefault(), source, socketListener);
				Protocol protocol = new Protocol(HttpClientRetrieveFileTransfer.HTTP, psf, HTTP_PORT);
				Trace.trace(Activator.PLUGIN_ID, "retrieve host=" + host + ";port=" + port); //$NON-NLS-1$ //$NON-NLS-2$
				hostConfiguration.setHost(host, port, protocol);
				hostConfiguration.getParams().setParameter(CredentialsProvider.PROVIDER, credProvider);
			}
		}

		public String getTargetRelativePath() {
			return targetRelativePath;
		}

	}

	private static final String USERNAME_PREFIX = Messages.HttpClientRetrieveFileTransfer_Username_Prefix;

	// changing to 2 minutes (120000) as per bug https://bugs.eclipse.org/bugs/show_bug.cgi?id=266246
	protected static final int DEFAULT_CONNECTION_TIMEOUT = 120000;
	// changing to 2 minutes (120000) as per bug https://bugs.eclipse.org/bugs/show_bug.cgi?id=266246
	protected static final int DEFAULT_READ_TIMEOUT = 120000;

	protected static final int HTTP_PORT = 80;

	protected static final int HTTPS_PORT = 443;

	protected static final int MAX_RETRY = 2;

	protected static final String HTTPS = Messages.FileTransferNamespace_Https_Protocol;

	protected static final String HTTP = Messages.FileTransferNamespace_Http_Protocol;

	protected static final String[] supportedProtocols = {HTTP, HTTPS};

	private static final String LAST_MODIFIED_HEADER = "Last-Modified"; //$NON-NLS-1$

	private GzipGetMethod getMethod = null;

	private HttpClient httpClient = null;

	private String username;

	private String password;

	private int responseCode = -1;
	private volatile boolean doneFired = false;

	private String remoteFileName;

	protected int httpVersion = 1;

	protected IFileID fileid = null;

	protected JREProxyHelper proxyHelper = null;

	private HostConfigHelper hostConfigHelper;
	private SocketEventSource socketEventSource;

	private ConnectingSocketMonitor connectingSockets;
	private FileTransferJob connectJob;

	public HttpClientRetrieveFileTransfer(HttpClient httpClient) {
		this.httpClient = httpClient;
		Assert.isNotNull(this.httpClient);
		proxyHelper = new JREProxyHelper();
		connectingSockets = new ConnectingSocketMonitor(1);
		socketEventSource = new SocketEventSource() {
			public Object getAdapter(Class adapter) {
				if (adapter == null) {
					return null;
				}
				if (adapter.isInstance(this)) {
					return this;
				}
				return HttpClientRetrieveFileTransfer.this.getAdapter(adapter);
			}

		};

	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.provider.filetransfer.retrieve.AbstractRetrieveFileTransfer#getRemoteFileName()
	 */
	public String getRemoteFileName() {
		return remoteFileName;
	}

	public synchronized void cancel() {
		Trace.entering(Activator.PLUGIN_ID, DebugOptions.METHODS_ENTERING, this.getClass(), "cancel"); //$NON-NLS-1$
		if (isCanceled()) {
			return; // break job cancel recursion
		}
		setDoneCanceled(exception);
		boolean fireDoneEvent = true;
		if (connectJob != null) {
			Trace.trace(Activator.PLUGIN_ID, "calling connectJob.cancel()"); //$NON-NLS-1$
			connectJob.cancel();
		}
		synchronized (jobLock) {
			if (job != null) {
				// Its the transfer jobs responsibility to throw the event.
				fireDoneEvent = false;
				Trace.trace(Activator.PLUGIN_ID, "calling transfer job.cancel()"); //$NON-NLS-1$
				job.cancel();
			}
		}
		if (getMethod != null) {
			if (!getMethod.isAborted()) {
				Trace.trace(Activator.PLUGIN_ID, "calling getMethod.abort()"); //$NON-NLS-1$
				getMethod.abort();
			}
		}
		if (connectingSockets != null) {
			// this should unblock socket connect calls, if any
			for (Iterator iterator = connectingSockets.getConnectingSockets().iterator(); iterator.hasNext();) {
				Socket socket = (Socket) iterator.next();
				try {
					Trace.trace(Activator.PLUGIN_ID, "Call socket.close() for socket=" + socket.toString()); //$NON-NLS-1$
					socket.close();
				} catch (IOException e) {
					Trace.catching(Activator.PLUGIN_ID, DebugOptions.EXCEPTIONS_CATCHING, this.getClass(), "cancel", e); //$NON-NLS-1$
				}
			}
		}
		hardClose();
		if (fireDoneEvent) {
			fireTransferReceiveDoneEvent();
		}
		Trace.exiting(Activator.PLUGIN_ID, DebugOptions.METHODS_EXITING, this.getClass(), "cancel");//$NON-NLS-1$

	}

	/*
	 * (non-Javadoc)
	 *
	 * @see org.eclipse.ecf.provider.filetransfer.retrieve.AbstractRetrieveFileTransfer#hardClose()
	 */
	protected void hardClose() {
		super.hardClose();
		if (getMethod != null) {
			getMethod.releaseConnection();
			getMethod = null;
		}
		responseCode = -1;
		if (proxyHelper != null) {
			proxyHelper.dispose();
			proxyHelper = null;
		}
	}

	protected Credentials getFileRequestCredentials() throws UnsupportedCallbackException, IOException {
		if (connectContext == null)
			return null;
		final CallbackHandler callbackHandler = connectContext.getCallbackHandler();
		if (callbackHandler == null)
			return null;
		final NameCallback usernameCallback = new NameCallback(USERNAME_PREFIX);
		final ObjectCallback passwordCallback = new ObjectCallback();
		callbackHandler.handle(new Callback[] {usernameCallback, passwordCallback});
		username = usernameCallback.getName();
		password = (String) passwordCallback.getObject();
		return new UsernamePasswordCredentials(username, password);
	}

	protected void setupAuthentication(String urlString) throws UnsupportedCallbackException, IOException {
		Credentials credentials = null;
		if (username == null) {
			credentials = getFileRequestCredentials();
		}

		if (credentials != null && username != null) {
			final AuthScope authScope = new AuthScope(getHostFromURL(urlString), getPortFromURL(urlString), AuthScope.ANY_REALM);
			Trace.trace(Activator.PLUGIN_ID, "retrieve credentials=" + credentials); //$NON-NLS-1$
			httpClient.getState().setCredentials(authScope, credentials);
		}
	}

	protected void setupHostAndPort(CredentialsProvider credProvider, String urlString) {
		getHostConfiguration(); // creates hostConfigHelper if needed
		hostConfigHelper.setTargetHostByURL(credProvider, urlString);
	}

	protected void setRequestHeaderValues() throws InvalidFileRangeSpecificationException {
		final IFileRangeSpecification rangeSpec = getFileRangeSpecification();
		if (rangeSpec != null) {
			final long startPosition = rangeSpec.getStartPosition();
			final long endPosition = rangeSpec.getEndPosition();
			if (startPosition < 0)
				throw new InvalidFileRangeSpecificationException(Messages.HttpClientRetrieveFileTransfer_RESUME_START_POSITION_LESS_THAN_ZERO, rangeSpec);
			if (endPosition != -1L && endPosition <= startPosition)
				throw new InvalidFileRangeSpecificationException(Messages.HttpClientRetrieveFileTransfer_RESUME_ERROR_END_POSITION_LESS_THAN_START, rangeSpec);
			String rangeHeader = "bytes=" + startPosition + "-" + ((endPosition == -1L) ? "" : ("" + endPosition)); //$NON-NLS-1$ //$NON-NLS-2$ //$NON-NLS-3$ //$NON-NLS-4$
			Trace.trace(Activator.PLUGIN_ID, "retrieve range header=" + rangeHeader); //$NON-NLS-1$
			setRangeHeader(rangeHeader);
		}
		// set max-age for cache control to 0 for bug https://bugs.eclipse.org/bugs/show_bug.cgi?id=249990
		getMethod.addRequestHeader("Cache-Control", "max-age=0"); //$NON-NLS-1$//$NON-NLS-2$
	}

	private void setRangeHeader(String value) {
		getMethod.addRequestHeader("Range", value); //$NON-NLS-1$
	}

	private boolean isHTTP11() {
		return (httpVersion >= 1);
	}

	public int getResponseCode() {
		if (responseCode != -1)
			return responseCode;
		HttpVersion version = getMethod.getEffectiveVersion();
		if (version == null) {
			responseCode = -1;
			httpVersion = 1;
			return responseCode;
		}
		httpVersion = version.getMinor();
		responseCode = getMethod.getStatusCode();
		return responseCode;
	}

	/*
	 * (non-Javadoc)
	 *
	 * @see org.eclipse.ecf.core.identity.IIdentifiable#getID()
	 */
	public ID getID() {
		return fileid;
	}

	private long getLastModifiedTimeFromHeader() throws IOException {
		Header lastModifiedHeader = getMethod.getResponseHeader(LAST_MODIFIED_HEADER);
		if (lastModifiedHeader == null)
			throw new IOException(Messages.HttpClientRetrieveFileTransfer_INVALID_LAST_MODIFIED_TIME);

		String lastModifiedString = lastModifiedHeader.getValue();
		long lastModified = 0;
		if (lastModifiedString != null) {
			try {
				lastModified = DateUtil.parseDate(lastModifiedString).getTime();
			} catch (Exception e) {
				throw new IOException(Messages.HttpClientRetrieveFileTransfer_EXCEPITION_INVALID_LAST_MODIFIED_FROM_SERVER);
			}
		}
		return lastModified;
	}

	protected void getResponseHeaderValues() throws IOException {
		if (getResponseCode() == -1)
			throw new IOException(Messages.HttpClientRetrieveFileTransfer_INVALID_SERVER_RESPONSE_TO_PARTIAL_RANGE_REQUEST);
		Header lastModifiedHeader = getMethod.getResponseHeader(LAST_MODIFIED_HEADER);
		if (lastModifiedHeader != null) {
			setLastModifiedTime(getLastModifiedTimeFromHeader());
		}
		setFileLength(getMethod.getResponseContentLength());
		fileid = new FileTransferID(getRetrieveNamespace(), getRemoteFileURL());

		// Get content disposition header and get remote file name from it if possible.
		Header contentDispositionHeader = getMethod.getResponseHeader(HttpHelper.CONTENT_DISPOSITION_HEADER);
		if (contentDispositionHeader != null) {
			remoteFileName = HttpHelper.getRemoteFileNameFromContentDispositionHeader(contentDispositionHeader.getValue());
		}
		// If still null, get the path from httpclient.getMethod()
		if (remoteFileName == null) {
			// No name could be extracted using Content-Disposition. Let's try the
			// path from the getMethod.
			String pathStr = getMethod.getPath();
			if (pathStr != null && pathStr.length() > 0) {
				IPath path = Path.fromPortableString(pathStr);
				if (path.segmentCount() > 0)
					remoteFileName = path.lastSegment();
			}
			// If still null, use the input file name
			if (remoteFileName == null)
				// Last resort. Use the path of the initial URL request
				remoteFileName = super.getRemoteFileName();
		}
	}

	final class ECFCredentialsProvider extends HttpClientProxyCredentialProvider {

		protected Proxy getECFProxy() {
			return getProxy();
		}

		protected Credentials getNTLMCredentials(Proxy lp) {
			if (hasForceNTLMProxyOption())
				return HttpClientRetrieveFileTransfer.createNTLMCredentials(lp);
			return null;
		}

	}

	Proxy getProxy() {
		return proxy;
	}

	protected void setInputStream(InputStream ins) {
		remoteFileContents = ins;
	}

	protected InputStream wrapTransferReadInputStream(InputStream inputStream, IProgressMonitor monitor) {
		return inputStream;
	}

	protected boolean hasForceNTLMProxyOption() {
		Map localOptions = getOptions();
		if (localOptions != null && localOptions.get(HttpClientOptions.FORCE_NTLM_PROP) != null)
			return true;
		return (System.getProperties().getProperty(HttpClientOptions.FORCE_NTLM_PROP) != null);
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.provider.filetransfer.retrieve.AbstractRetrieveFileTransfer#openStreams()
	 */
	protected void openStreams() throws IncomingFileTransferException {

		Trace.entering(Activator.PLUGIN_ID, DebugOptions.METHODS_ENTERING, this.getClass(), "openStreams"); //$NON-NLS-1$
		final String urlString = getRemoteFileURL().toString();
		this.doneFired = false;

		int code = -1;

		try {
			httpClient.getHttpConnectionManager().getParams().setSoTimeout(DEFAULT_READ_TIMEOUT);
			httpClient.getHttpConnectionManager().getParams().setConnectionTimeout(DEFAULT_CONNECTION_TIMEOUT);
			httpClient.getParams().setConnectionManagerTimeout(DEFAULT_CONNECTION_TIMEOUT);

			setupAuthentication(urlString);

			CredentialsProvider credProvider = new ECFCredentialsProvider();
			setupHostAndPort(credProvider, urlString);

			getMethod = new GzipGetMethod(hostConfigHelper.getTargetRelativePath());
			getMethod.setFollowRedirects(true);
			// Define a CredentialsProvider - found that possibility while debugging in org.apache.commons.httpclient.HttpMethodDirector.processProxyAuthChallenge(HttpMethod)
			// Seems to be another way to select the credentials.
			getMethod.getParams().setParameter(CredentialsProvider.PROVIDER, credProvider);
			setRequestHeaderValues();

			Trace.trace(Activator.PLUGIN_ID, "retrieve=" + urlString); //$NON-NLS-1$
			// Set request header for possible gzip encoding, but only if
			// 1) The file range specification is null (we want the whole file)
			// 2) The target remote file does *not* end in .gz (see bug https://bugs.eclipse.org/bugs/show_bug.cgi?id=280205)
			if (getFileRangeSpecification() == null && !targetHasGzSuffix(super.getRemoteFileName())) {
				Trace.trace(Activator.PLUGIN_ID, "Accept-Encoding: gzip added to request header"); //$NON-NLS-1$
				getMethod.setRequestHeader(GzipGetMethod.ACCEPT_ENCODING, GzipGetMethod.CONTENT_ENCODING_ACCEPTED);
			} else {
				Trace.trace(Activator.PLUGIN_ID, "Accept-Encoding NOT added to header"); //$NON-NLS-1$
			}

			fireConnectStartEvent();
			if (checkAndHandleDone()) {
				return;
			}

			connectingSockets.clear();
			// Actually execute get and get response code (since redirect is set to true, then
			// redirect response code handled internally
			if (connectJob == null) {
				performConnect(new NullProgressMonitor());
			} else {
				connectJob.schedule();
				connectJob.join();
				connectJob = null;
			}
			if (checkAndHandleDone()) {
				return;
			}

			code = responseCode;
			Trace.trace(Activator.PLUGIN_ID, "retrieve resp=" + code); //$NON-NLS-1$

			// Check for NTLM proxy in response headers 
			// This check is to deal with bug https://bugs.eclipse.org/bugs/show_bug.cgi?id=252002
			boolean ntlmProxyFound = NTLMProxyDetector.detectNTLMProxy(getMethod);
			if (ntlmProxyFound && !hasForceNTLMProxyOption())
				throw new IncomingFileTransferException("NTLM Proxy Not Supported by HttpClient Provider", HttpClientOptions.NTLM_PROXY_RESPONSE_CODE); //$NON-NLS-1$

			if (code == HttpURLConnection.HTTP_PARTIAL || code == HttpURLConnection.HTTP_OK) {
				getResponseHeaderValues();
				setInputStream(getMethod.getResponseBodyAsUnzippedStream());
				fireReceiveStartEvent();
			} else if (code == HttpURLConnection.HTTP_NOT_FOUND) {
				getMethod.releaseConnection();
				throw new IncomingFileTransferException(NLS.bind("File not found: {0}", urlString), code); //$NON-NLS-1$
			} else if (code == HttpURLConnection.HTTP_UNAUTHORIZED) {
				getMethod.releaseConnection();
				throw new IncomingFileTransferException(Messages.HttpClientRetrieveFileTransfer_Unauthorized, code);
			} else if (code == HttpURLConnection.HTTP_FORBIDDEN) {
				getMethod.releaseConnection();
				throw new IncomingFileTransferException("Forbidden", code); //$NON-NLS-1$
			} else if (code == HttpURLConnection.HTTP_PROXY_AUTH) {
				getMethod.releaseConnection();
				throw new IncomingFileTransferException(Messages.HttpClientRetrieveFileTransfer_Proxy_Auth_Required, code);
			} else {
				getMethod.releaseConnection();
				throw new IncomingFileTransferException(NLS.bind(Messages.HttpClientRetrieveFileTransfer_ERROR_GENERAL_RESPONSE_CODE, new Integer(code)), code);
			}
		} catch (final Exception e) {
			Trace.throwing(Activator.PLUGIN_ID, DebugOptions.EXCEPTIONS_THROWING, this.getClass(), "openStreams", e); //$NON-NLS-1$
			if (code == -1) {
				if (!isDone()) {
					setDoneException(e);
				}
				fireTransferReceiveDoneEvent();
			} else {
				IncomingFileTransferException ex = (IncomingFileTransferException) ((e instanceof IncomingFileTransferException) ? e : new IncomingFileTransferException(NLS.bind(Messages.HttpClientRetrieveFileTransfer_EXCEPTION_COULD_NOT_CONNECT, urlString), e, code));
				throw ex;
			}
		}
		Trace.exiting(Activator.PLUGIN_ID, DebugOptions.METHODS_EXITING, this.getClass(), "openStreams"); //$NON-NLS-1$
	}

	private boolean checkAndHandleDone() {
		if (isDone()) {
			// for cancel the done event should have been fired always.
			if (!doneFired) {
				fireTransferReceiveDoneEvent();
			}
			return true;
		}
		return false;
	}

	/*
	 * (non-Javadoc)
	 *
	 * @see org.eclipse.ecf.filetransfer.IRetrieveFileTransferContainerAdapter#setConnectContextForAuthentication(org.eclipse.ecf.core.security.IConnectContext)
	 */
	public void setConnectContextForAuthentication(IConnectContext connectContext) {
		super.setConnectContextForAuthentication(connectContext);
		this.username = null;
		this.password = null;
	}

	protected static String getHostFromURL(String url) {
		String result = url;
		final int colonSlashSlash = url.indexOf("://"); //$NON-NLS-1$
		if (colonSlashSlash < 0)
			return ""; //$NON-NLS-1$
		if (colonSlashSlash >= 0) {
			result = url.substring(colonSlashSlash + 3);
		}

		final int colonPort = result.indexOf(':');
		final int requestPath = result.indexOf('/');

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
		final int colonSlashSlash = url.indexOf("://"); //$NON-NLS-1$
		if (colonSlashSlash < 0)
			return urlUsesHttps(url) ? HTTPS_PORT : HTTP_PORT;
		// This is wrong as if the url has no colonPort before '?' then it should return the default

		final int colonPort = url.indexOf(':', colonSlashSlash + 1);
		if (colonPort < 0)
			return urlUsesHttps(url) ? HTTPS_PORT : HTTP_PORT;
		// Make sure that the colonPort is not from some part of the rest of the URL
		int nextSlash = url.indexOf('/', colonSlashSlash + 3);
		if (nextSlash != -1 && colonPort > nextSlash)
			return urlUsesHttps(url) ? HTTPS_PORT : HTTP_PORT;

		final int requestPath = url.indexOf('/', colonPort + 1);

		int end;
		if (requestPath < 0)
			end = url.length();
		else
			end = requestPath;

		return Integer.parseInt(url.substring(colonPort + 1, end));
	}

	protected static boolean urlUsesHttps(String url) {
		url = url.trim();
		return url.startsWith(HTTPS);
	}

	/*
	 * (non-Javadoc)
	 *
	 * @see org.eclipse.ecf.internal.provider.filetransfer.AbstractRetrieveFileTransfer#supportsProtocol(java.lang.String)
	 */
	public static boolean supportsProtocol(String protocolString) {
		for (int i = 0; i < supportedProtocols.length; i++)
			if (supportedProtocols[i].equalsIgnoreCase(protocolString))
				return true;
		return false;
	}

	protected boolean isConnected() {
		return (getMethod != null);
	}

	/*
	 * (non-Javadoc)
	 *
	 * @see org.eclipse.ecf.provider.filetransfer.retrieve.AbstractRetrieveFileTransfer#doPause()
	 */
	protected boolean doPause() {
		if (isPaused() || !isConnected() || isDone())
			return false;
		this.paused = true;
		return this.paused;
	}

	/*
	 * (non-Javadoc)
	 *
	 * @see org.eclipse.ecf.provider.filetransfer.retrieve.AbstractRetrieveFileTransfer#doResume()
	 */
	protected boolean doResume() {
		if (!isPaused() || isConnected())
			return false;
		return openStreamsForResume();
	}

	protected void setResumeRequestHeaderValues() throws IOException {
		if (this.bytesReceived <= 0 || this.fileLength <= this.bytesReceived)
			throw new IOException(Messages.HttpClientRetrieveFileTransfer_RESUME_START_ERROR);
		setRangeHeader("bytes=" + this.bytesReceived + "-"); //$NON-NLS-1$ //$NON-NLS-2$
		// set max-age for cache control to 0 for bug https://bugs.eclipse.org/bugs/show_bug.cgi?id=249990
		getMethod.addRequestHeader("Cache-Control", "max-age=0"); //$NON-NLS-1$//$NON-NLS-2$
	}

	private boolean openStreamsForResume() {

		Trace.entering(Activator.PLUGIN_ID, DebugOptions.METHODS_ENTERING, this.getClass(), "openStreamsForResume"); //$NON-NLS-1$
		final String urlString = getRemoteFileURL().toString();
		this.doneFired = false;

		int code = -1;

		try {
			httpClient.getHttpConnectionManager().getParams().setSoTimeout(DEFAULT_READ_TIMEOUT);
			httpClient.getHttpConnectionManager().getParams().setConnectionTimeout(DEFAULT_CONNECTION_TIMEOUT);
			httpClient.getParams().setConnectionManagerTimeout(DEFAULT_CONNECTION_TIMEOUT);

			CredentialsProvider credProvider = new ECFCredentialsProvider();
			setupAuthentication(urlString);

			setupHostAndPort(credProvider, urlString);

			getMethod = new GzipGetMethod(hostConfigHelper.getTargetRelativePath());
			getMethod.setFollowRedirects(true);
			// Define a CredentialsProvider - found that possibility while debugging in org.apache.commons.httpclient.HttpMethodDirector.processProxyAuthChallenge(HttpMethod)
			// Seems to be another way to select the credentials.
			getMethod.getParams().setParameter(CredentialsProvider.PROVIDER, credProvider);
			setResumeRequestHeaderValues();

			Trace.trace(Activator.PLUGIN_ID, "resume=" + urlString); //$NON-NLS-1$

			// Gzip encoding is not an option for resume
			fireConnectStartEvent();
			if (checkAndHandleDone()) {
				return false;
			}

			connectingSockets.clear();
			// Actually execute get and get response code (since redirect is set to true, then
			// redirect response code handled internally
			if (connectJob == null) {
				performConnect(new NullProgressMonitor());
			} else {
				connectJob.schedule();
				connectJob.join();
				connectJob = null;
			}
			if (checkAndHandleDone()) {
				return false;
			}

			code = responseCode;
			Trace.trace(Activator.PLUGIN_ID, "retrieve resp=" + code); //$NON-NLS-1$

			if (code == HttpURLConnection.HTTP_PARTIAL || code == HttpURLConnection.HTTP_OK) {
				getResumeResponseHeaderValues();
				setInputStream(getMethod.getResponseBodyAsUnzippedStream());
				this.paused = false;
				fireReceiveResumedEvent();
			} else if (code == HttpURLConnection.HTTP_NOT_FOUND) {
				getMethod.releaseConnection();
				throw new IncomingFileTransferException(NLS.bind("File not found: {0}", urlString), code); //$NON-NLS-1$
			} else if (code == HttpURLConnection.HTTP_UNAUTHORIZED) {
				getMethod.releaseConnection();
				throw new IncomingFileTransferException(Messages.HttpClientRetrieveFileTransfer_Unauthorized, code);
			} else if (code == HttpURLConnection.HTTP_FORBIDDEN) {
				getMethod.releaseConnection();
				throw new IncomingFileTransferException("Forbidden", code); //$NON-NLS-1$
			} else if (code == HttpURLConnection.HTTP_PROXY_AUTH) {
				getMethod.releaseConnection();
				throw new IncomingFileTransferException(Messages.HttpClientRetrieveFileTransfer_Proxy_Auth_Required, code);
			} else {
				getMethod.releaseConnection();
				throw new IncomingFileTransferException(NLS.bind(Messages.HttpClientRetrieveFileTransfer_ERROR_GENERAL_RESPONSE_CODE, new Integer(code)), code);
			}
			Trace.exiting(Activator.PLUGIN_ID, DebugOptions.METHODS_EXITING, this.getClass(), "openStreamsForResume", Boolean.TRUE); //$NON-NLS-1$
			return true;
		} catch (final Exception e) {
			Trace.catching(Activator.PLUGIN_ID, DebugOptions.EXCEPTIONS_CATCHING, this.getClass(), "openStreamsForResume", e); //$NON-NLS-1$
			if (code == -1) {
				if (!isDone()) {
					setDoneException(e);
				}
			} else {
				setDoneException((e instanceof IncomingFileTransferException) ? e : new IncomingFileTransferException(NLS.bind(Messages.HttpClientRetrieveFileTransfer_EXCEPTION_COULD_NOT_CONNECT, urlString), e, code));
			}
			fireTransferReceiveDoneEvent();
			Trace.exiting(Activator.PLUGIN_ID, DebugOptions.METHODS_EXITING, this.getClass(), "openStreamsForResume", Boolean.FALSE); //$NON-NLS-1$
			return false;
		}
	}

	protected void getResumeResponseHeaderValues() throws IOException {
		if (getResponseCode() != HttpURLConnection.HTTP_PARTIAL)
			throw new IOException();
		if (lastModifiedTime != getLastModifiedTimeFromHeader())
			throw new IOException(Messages.HttpClientRetrieveFileTransfer_EXCEPTION_FILE_MODIFIED_SINCE_LAST_ACCESS);
	}

	/*
	 * (non-Javadoc)
	 *
	 * @see org.eclipse.ecf.provider.filetransfer.retrieve.AbstractRetrieveFileTransfer#getAdapter(java.lang.Class)
	 */
	public Object getAdapter(Class adapter) {
		if (adapter == null)
			return null;
		if (adapter.equals(IFileTransferPausable.class) && isHTTP11())
			return this;
		if (adapter.equals(ISocketEventSource.class))
			return this.socketEventSource;
		return super.getAdapter(adapter);
	}

	private HostConfiguration getHostConfiguration() {
		if (hostConfigHelper == null) {
			hostConfigHelper = new HostConfigHelper(socketEventSource, connectingSockets);
		}
		return hostConfigHelper.getHostConfiguration();
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.provider.filetransfer.retrieve.AbstractRetrieveFileTransfer#setupProxy(org.eclipse.ecf.core.util.Proxy)
	 */
	protected void setupProxy(Proxy proxy) {
		if (proxy.getType().equals(Proxy.Type.HTTP)) {
			final ProxyAddress address = proxy.getAddress();
			getHostConfiguration().setProxy(address.getHostName(), address.getPort());
		} else if (proxy.getType().equals(Proxy.Type.SOCKS)) {
			Trace.trace(Activator.PLUGIN_ID, "retrieve socksproxy=" + proxy.getAddress()); //$NON-NLS-1$
			proxyHelper.setupProxy(proxy);
		}
	}

	public static NTCredentials createNTLMCredentials(Proxy p) {
		if (p == null) {
			return null;
		}
		String un = getNTLMUserName(p);
		String domain = getNTLMDomainName(p);
		if (un == null || domain == null)
			return null;
		return new NTCredentials(un, p.getPassword(), p.getAddress().getHostName(), domain);
	}

	protected static String getNTLMDomainName(Proxy p) {
		String domainUsername = p.getUsername();
		if (domainUsername == null)
			return null;
		int slashloc = domainUsername.indexOf('\\');
		if (slashloc == -1)
			return null;
		return domainUsername.substring(0, slashloc);
	}

	protected static String getNTLMUserName(Proxy p) {
		String domainUsername = p.getUsername();
		if (domainUsername == null)
			return null;
		int slashloc = domainUsername.indexOf('\\');
		if (slashloc == -1)
			return null;
		return domainUsername.substring(slashloc + 1);
	}

	protected void fireConnectStartEvent() {
		Trace.entering(Activator.PLUGIN_ID, DebugOptions.METHODS_ENTERING, this.getClass(), "fireConnectStartEvent"); //$NON-NLS-1$ 
		// TODO: should the following be in super.fireReceiveStartEvent();
		listener.handleTransferEvent(new IFileTransferConnectStartEvent() {
			public IFileID getFileID() {
				return remoteFileID;
			}

			public void cancel() {
				HttpClientRetrieveFileTransfer.this.cancel();
			}

			public FileTransferJob prepareConnectJob(FileTransferJob j) {
				return HttpClientRetrieveFileTransfer.this.prepareConnectJob(j);
			}

			public void connectUsingJob(FileTransferJob j) {
				HttpClientRetrieveFileTransfer.this.connectUsingJob(j);
			}

			public String toString() {
				final StringBuffer sb = new StringBuffer("IFileTransferConnectStartEvent["); //$NON-NLS-1$
				sb.append(getFileID());
				sb.append("]"); //$NON-NLS-1$
				return sb.toString();
			}

			public Object getAdapter(Class adapter) {
				return HttpClientRetrieveFileTransfer.this.getAdapter(adapter);
			}
		});
	}

	protected String createConnectJobName() {
		return getRemoteFileURL().toString() + createRangeName() + Messages.HttpClientRetrieveFileTransfer_CONNECTING_JOB_NAME;
	}

	protected FileTransferJob prepareConnectJob(FileTransferJob cjob) {
		if (cjob == null) {
			// Create our own
			cjob = new FileTransferJob(createJobName());
		}
		cjob.setFileTransfer(this);
		cjob.setFileTransferRunnable(fileConnectRunnable);
		return cjob;
	}

	protected void connectUsingJob(FileTransferJob cjob) {
		Assert.isNotNull(cjob);
		this.connectJob = cjob;
	}

	private IFileTransferRunnable fileConnectRunnable = new IFileTransferRunnable() {
		public IStatus performFileTransfer(IProgressMonitor monitor) {
			return performConnect(monitor);
		}
	};

	private IStatus performConnect(IProgressMonitor monitor) {
		// there might be more ticks in the future perhaps for 
		// connect socket, certificate validation, send request, authenticate,
		int ticks = 1;
		monitor.beginTask(getRemoteFileURL().toString() + Messages.HttpClientRetrieveFileTransfer_CONNECTING_TASK_NAME, ticks);
		try {
			if (monitor.isCanceled())
				throw newUserCancelledException();
			responseCode = httpClient.executeMethod(getHostConfiguration(), getMethod);
			Trace.trace(Activator.PLUGIN_ID, "retrieve resp=" + responseCode); //$NON-NLS-1$
		} catch (final Exception e) {
			Trace.catching(Activator.PLUGIN_ID, DebugOptions.EXCEPTIONS_CATCHING, this.getClass(), "performConnect", e); //$NON-NLS-1$
			if (!isDone()) {
				setDoneException(e);
			}
		} finally {
			monitor.done();
		}
		return Status.OK_STATUS;

	}

	protected void fireReceiveResumedEvent() {
		Trace.entering(Activator.PLUGIN_ID, DebugOptions.METHODS_ENTERING, this.getClass(), "fireReceiveResumedEvent len=" + fileLength + ";rcvd=" + bytesReceived); //$NON-NLS-1$ //$NON-NLS-2$
		super.fireReceiveResumedEvent();
	}

	protected void fireTransferReceiveDataEvent() {
		Trace.entering(Activator.PLUGIN_ID, DebugOptions.METHODS_ENTERING, this.getClass(), "fireTransferReceiveDataEvent len=" + fileLength + ";rcvd=" + bytesReceived); //$NON-NLS-1$ //$NON-NLS-2$
		super.fireTransferReceiveDataEvent();
	}

	protected void fireTransferReceiveDoneEvent() {
		Trace.entering(Activator.PLUGIN_ID, DebugOptions.METHODS_ENTERING, this.getClass(), "fireTransferReceiveDoneEvent len=" + fileLength + ";rcvd=" + bytesReceived); //$NON-NLS-1$ //$NON-NLS-2$
		this.doneFired = true;
		super.fireTransferReceiveDoneEvent();
	}

	protected void fireTransferReceivePausedEvent() {
		Trace.entering(Activator.PLUGIN_ID, DebugOptions.METHODS_ENTERING, this.getClass(), "fireTransferReceivePausedEvent len=" + fileLength + ";rcvd=" + bytesReceived); //$NON-NLS-1$ //$NON-NLS-2$
		super.fireTransferReceivePausedEvent();
	}

}
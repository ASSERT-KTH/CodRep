public class RestClientService extends AbstractClientService {

/******************************************************************************* 
 * Copyright (c) 2009 EclipseSource and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *   EclipseSource - initial API and implementation
 *******************************************************************************/
package org.eclipse.ecf.remoteservice.rest.client;

import java.io.*;
import java.net.URLEncoder;
import java.util.*;
import org.apache.commons.httpclient.*;
import org.apache.commons.httpclient.auth.AuthScope;
import org.apache.commons.httpclient.methods.*;
import org.apache.commons.httpclient.params.HttpClientParams;
import org.eclipse.ecf.core.security.*;
import org.eclipse.ecf.core.util.ECFException;
import org.eclipse.ecf.remoteservice.IRemoteCall;
import org.eclipse.ecf.remoteservice.IRemoteService;
import org.eclipse.ecf.remoteservice.client.*;
import org.eclipse.ecf.remoteservice.rest.IRestCall;
import org.eclipse.ecf.remoteservice.rest.RestException;
import org.eclipse.osgi.util.NLS;

/**
 * This class represents a REST service from the client side of view. So a
 * RESTful web service can be accessed via the methods provided by this class.
 * Mostly the methods are inherited from {@link IRemoteService}.
 */
public class RestClientService extends AbstractRemoteServiceClientService {

	protected HttpClient httpClient;

	public RestClientService(RestClientContainer container, RemoteServiceClientRegistration registration) {
		super(container, registration);
		this.httpClient = new HttpClient();
	}

	/**
	 * Calls the Rest service with given URL of IRestCall. The returned value is
	 * the response body as an InputStream.
	 * 
	 * @param call
	 *            The remote call to make.  Must not be <code>null</code>.
	 * @param callable
	 *            The callable with default parameters to use to make the call.
	 * @return The InputStream of the response body or <code>null</code> if an
	 *         error occurs.
	 */
	protected Object invokeRemoteCall(final IRemoteCall call, final IRemoteCallable callable) throws ECFException {
		String uri = prepareURIForRequest(call, callable);
		HttpMethod httpMethod = createAndPrepareHttpMethod(uri, call, callable);
		// execute method
		String responseBody = null;
		int responseCode = -1;
		try {
			responseCode = httpClient.executeMethod(httpMethod);
			if (responseCode == HttpStatus.SC_OK) {
				// Get responseBody as String
				responseBody = httpMethod.getResponseBodyAsString();
				if (responseBody == null)
					throw new RestException("Invalid server response", responseCode); //$NON-NLS-1$
			} else
				handleException(NLS.bind("Http response not OK.  URL={0}, responseCode={1}", uri, new Integer(responseCode)), null, responseCode); //$NON-NLS-1$
		} catch (HttpException e) {
			handleException("Transport HttpException", e, responseCode); //$NON-NLS-1$
		} catch (IOException e) {
			handleException("Transport IOException", e, responseCode); //$NON-NLS-1$
		}
		Object result = null;
		try {
			result = processResponse(uri, call, callable, convertResponseHeaders(httpMethod.getResponseHeaders()), responseBody);
		} catch (NotSerializableException e) {
			handleException(NLS.bind("Exception deserializing response.  URL={0}, responseCode={1}", uri, new Integer(responseCode)), e, responseCode); //$NON-NLS-1$
		}
		return result;
	}

	protected void handleException(String message, Throwable e, int responseCode) throws RestException {
		throw new RestException(message, e, responseCode);
	}

	protected void setupTimeouts(HttpClient httpClient, IRemoteCall call, IRemoteCallable callable) {
		long callTimeout = call.getTimeout();
		if (callTimeout == IRemoteCall.DEFAULT_TIMEOUT)
			callTimeout = callable.getDefaultTimeout();

		int timeout = (int) callTimeout;
		httpClient.getHttpConnectionManager().getParams().setSoTimeout(timeout);
		httpClient.getHttpConnectionManager().getParams().setConnectionTimeout(timeout);
		httpClient.getParams().setConnectionManagerTimeout(timeout);
	}

	private Map convertResponseHeaders(Header[] headers) {
		Map result = new HashMap();
		if (headers == null)
			return result;
		for (int i = 0; i < headers.length; i++) {
			String name = headers[i].getName();
			String value = headers[i].getValue();
			result.put(name, value);
		}
		return result;
	}

	protected void addRequestHeaders(HttpMethod httpMethod, IRemoteCall call, IRemoteCallable callable) {
		// Add request headers from the callable
		Map requestHeaders = (callable.getRequestType() instanceof AbstractRequestType) ? ((AbstractRequestType) callable.getRequestType()).getDefaultRequestHeaders() : new HashMap();
		if (requestHeaders == null)
			requestHeaders = new HashMap();

		if (call instanceof IRestCall) {
			Map callHeaders = ((IRestCall) call).getRequestHeaders();
			if (callHeaders != null)
				requestHeaders.putAll(requestHeaders);
		}

		Set keySet = requestHeaders.keySet();
		Object[] headers = keySet.toArray();
		for (int i = 0; i < headers.length; i++) {
			String key = (String) headers[i];
			String value = (String) requestHeaders.get(key);
			httpMethod.addRequestHeader(key, value);
		}
	}

	protected HttpMethod createAndPrepareHttpMethod(String uri, IRemoteCall call, IRemoteCallable callable) throws RestException {
		HttpMethod httpMethod = null;

		IRemoteCallableRequestType requestType = callable.getRequestType();
		if (requestType == null)
			throw new RestException("Request type for call cannot be null"); //$NON-NLS-1$
		try {
			if (requestType instanceof HttpGetRequestType) {
				httpMethod = prepareGetMethod(uri, call, callable);
			} else if (requestType instanceof HttpPostRequestType) {
				httpMethod = preparePostMethod(uri, call, callable);
			} else if (requestType instanceof HttpPutRequestType) {
				httpMethod = preparePutMethod(uri, call, callable);
			} else if (requestType instanceof HttpDeleteRequestType) {
				httpMethod = prepareDeleteMethod(uri, call, callable);
			} else {
				throw new RestException(NLS.bind("HTTP method {0} not supported", requestType)); //$NON-NLS-1$
			}
		} catch (NotSerializableException e) {
			// XXX log
			throw new RestException("Could not serialize parameters for uri=" + uri + " call=" + call + " callable=" + callable); //$NON-NLS-1$ //$NON-NLS-2$ //$NON-NLS-3$
		}
		// add additional request headers
		addRequestHeaders(httpMethod, call, callable);
		// handle authentication
		setupAuthenticaton(httpClient, httpMethod);
		// needed because a resource can link to another resource
		httpClient.getParams().setParameter(HttpClientParams.ALLOW_CIRCULAR_REDIRECTS, new Boolean(true));
		setupTimeouts(httpClient, call, callable);
		return httpMethod;
	}

	/**
	 * @throws RestException  
	 */
	protected HttpMethod prepareDeleteMethod(String uri, IRemoteCall call, IRemoteCallable callable) throws RestException {
		return new DeleteMethod(uri);
	}

	protected HttpMethod preparePutMethod(String uri, IRemoteCall call, IRemoteCallable callable) throws NotSerializableException {
		PutMethod result = new PutMethod(uri);
		HttpPutRequestType putRequestType = (HttpPutRequestType) callable.getRequestType();

		IRemoteCallParameter[] defaultParameters = callable.getDefaultParameters();
		Object[] parameters = call.getParameters();

		if (putRequestType.useRequestEntity()) {
			if (defaultParameters != null && defaultParameters.length > 0 && parameters != null && parameters.length > 0) {
				RequestEntity requestEntity = putRequestType.generateRequestEntity(uri, call, callable, defaultParameters[0], parameters[0]);
				result.setRequestEntity(requestEntity);
			}
		} else {
			NameValuePair[] params = toNameValuePairs(uri, call, callable);
			if (params != null)
				result.setQueryString(params);
		}
		return result;
	}

	/**
	 * @throws ECFException  
	 */
	protected HttpMethod preparePostMethod(String uri, IRemoteCall call, IRemoteCallable callable) throws NotSerializableException {
		PostMethod result = new PostMethod(uri);
		HttpPostRequestType postRequestType = (HttpPostRequestType) callable.getRequestType();

		IRemoteCallParameter[] defaultParameters = callable.getDefaultParameters();
		Object[] parameters = call.getParameters();
		if (postRequestType.useRequestEntity()) {
			if (defaultParameters != null && defaultParameters.length > 0 && parameters != null && parameters.length > 0) {
				RequestEntity requestEntity = postRequestType.generateRequestEntity(uri, call, callable, defaultParameters[0], parameters[0]);
				result.setRequestEntity(requestEntity);
			}
		} else {
			NameValuePair[] params = toNameValuePairs(uri, call, callable);
			if (params != null)
				result.setQueryString(params);
		}
		return result;
	}

	/**
	 * @throws ECFException  
	 */
	protected HttpMethod prepareGetMethod(String uri, IRemoteCall call, IRemoteCallable callable) throws NotSerializableException {
		HttpMethod result = new GetMethod(uri);
		NameValuePair[] params = toNameValuePairs(uri, call, callable);
		if (params != null)
			result.setQueryString(params);
		return result;
	}

	protected NameValuePair[] toNameValuePairs(String uri, IRemoteCall call, IRemoteCallable callable) throws NotSerializableException {
		IRemoteCallParameter[] restParameters = prepareParametersForRequest(uri, call, callable);
		List nameValueList = new ArrayList();
		if (restParameters != null) {
			for (int i = 0; i < restParameters.length; i++) {
				try {
					String parameterValue = null;
					Object o = restParameters[i].getValue();
					if (o instanceof String) {
						parameterValue = (String) o;
					} else if (o != null) {
						parameterValue = o.toString();
					}
					if (parameterValue != null) {
						String parameterName = URLEncoder.encode(restParameters[i].getName(), "UTF-8"); //$NON-NLS-1$
						parameterValue = URLEncoder.encode(parameterValue, "UTF-8"); //$NON-NLS-1$
						nameValueList.add(new NameValuePair(parameterName, parameterValue));
					}
				} catch (UnsupportedEncodingException e) {
					// should not happen
					e.printStackTrace();
				}
			}
		}
		return (NameValuePair[]) nameValueList.toArray(new NameValuePair[nameValueList.size()]);
	}

	protected void setupAuthenticaton(HttpClient httpClient, HttpMethod method) {
		IConnectContext connectContext = container.getConnectContextForAuthentication();
		if (connectContext != null) {
			NameCallback nameCallback = new NameCallback(""); //$NON-NLS-1$
			ObjectCallback passwordCallback = new ObjectCallback();
			Callback[] callbacks = new Callback[] {nameCallback, passwordCallback};
			CallbackHandler callbackHandler = connectContext.getCallbackHandler();
			if (callbackHandler == null)
				return;
			try {
				callbackHandler.handle(callbacks);
				String username = nameCallback.getName();
				String password = (String) passwordCallback.getObject();
				AuthScope authscope = new AuthScope(null, -1);
				Credentials credentials = new UsernamePasswordCredentials(username, password);
				httpClient.getState().setCredentials(authscope, credentials);
				method.setDoAuthentication(true);
			} catch (IOException e) {
				e.printStackTrace();
			} catch (UnsupportedCallbackException e) {
				e.printStackTrace();
			}

		}
	}

}
public class URLStreamHandlerServiceTest extends

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

package org.eclipse.ecf.tests.filetransfer;

import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLConnection;

import org.osgi.service.url.AbstractURLStreamHandlerService;

/**
 *
 */
public class TestURLStreamHandlerService extends
		AbstractURLStreamHandlerService {

	class TestHttpURLConnection extends HttpURLConnection {

		/**
		 * @param u
		 */
		protected TestHttpURLConnection(URL u) {
			super(u);
		}

		/* (non-Javadoc)
		 * @see java.net.HttpURLConnection#disconnect()
		 */
		public void disconnect() {
		}

		/* (non-Javadoc)
		 * @see java.net.HttpURLConnection#usingProxy()
		 */
		public boolean usingProxy() {
			return false;
		}

		/* (non-Javadoc)
		 * @see java.net.URLConnection#connect()
		 */
		public void connect() throws IOException {
		}
		
	}
	/* (non-Javadoc)
	 * @see org.osgi.service.url.AbstractURLStreamHandlerService#openConnection(java.net.URL)
	 */
	public URLConnection openConnection(URL u) throws IOException {
		return new TestHttpURLConnection(u);
	}

}
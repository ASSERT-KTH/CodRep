import org.columba.core.connectionstate.ConnectionStateImpl;

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

package org.columba.core.url.http;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.ProtocolException;
import java.net.URL;
import java.security.Permission;
import java.util.Map;
import java.util.logging.Logger;

import org.columba.core.main.ConnectionStateImpl;

/**
 * This class acts as a proxy between clients using HTTP URLs and the underlying
 * URLConnection implementation. Depending on the system's connection state
 * it throws IOExceptions indicating that there is no internet connection
 * available.
 */
public class HttpURLConnection extends java.net.HttpURLConnection {
    private static final Logger LOG = Logger
            .getLogger("org.columba.core.url.http");
    
    protected java.net.HttpURLConnection connection;
    
    public HttpURLConnection(URL u, java.net.HttpURLConnection connection) {
        super(u);
        this.connection = connection;
        connection.setUseCaches(false);
        connection.setDefaultUseCaches(false);
    }
    
    /**
     * Checks whether a connection is available and throws a IOConnection if not.
     */
    protected void ensureConnectionAllowed() throws IOException {
        if (!ConnectionStateImpl.getInstance().isOnline()) {
            LOG.fine("Blocking HTTP connection to " + getURL().toString());
            throw new IOException("Error while connecting.");
        }
    }
    
    public OutputStream getOutputStream() throws IOException {
        ensureConnectionAllowed();
        return connection.getOutputStream();
    }
    
    public void setDefaultUseCaches(boolean param) {}
    
    public long getIfModifiedSince() {
        return connection.getIfModifiedSince();
    }
    
    public String getResponseMessage() throws IOException {
        if (!ConnectionStateImpl.getInstance().isOnline()) {
            return "Not Found";
        } else {
            return connection.getResponseMessage();
        }
    }
    
    public Permission getPermission() throws IOException {
        return connection.getPermission();
    }
    
    public void setUseCaches(boolean param) {}
    
    public void addRequestProperty(String str, String str1) {
        connection.addRequestProperty(str, str1);
    }
    
    public boolean getInstanceFollowRedirects() {
        return connection.getInstanceFollowRedirects();
    }
    
    public Map getRequestProperties() {
        return connection.getRequestProperties();
    }
    
    public void setRequestMethod(String str) throws ProtocolException {
        super.setRequestMethod(str);
    }
    
    public boolean getDefaultUseCaches() {
        return connection.getDefaultUseCaches();
    }
    
    public String getRequestMethod() {
        return connection.getRequestMethod();
    }
    
    public boolean getDoOutput() {
        return connection.getDoOutput();
    }
    
    public long getDate() {
        return connection.getDate();
    }
    
    public int getResponseCode() throws IOException {
        if (!ConnectionStateImpl.getInstance().isOnline()) {
            return HTTP_NOT_FOUND;
        } else {
            return connection.getResponseCode();
        }
    }
    
    public long getHeaderFieldDate(String str, long param) {
        return connection.getHeaderFieldDate(str, param);
    }
    
    public boolean usingProxy() {
        return connection.usingProxy();
    }
    
    public void setRequestProperty(String str, String str1) {
        connection.setRequestProperty(str, str1);
    }
    
    public String getHeaderField(int param) {
        return connection.getHeaderField(param);
    }
    
    public void setAllowUserInteraction(boolean param) {
        super.setAllowUserInteraction(param);
    }
    
    public String getHeaderField(String str) {
        return connection.getHeaderField(str);
    }
    
    public InputStream getErrorStream() {
        return connection.getErrorStream();
    }
    
    public Object getContent(Class[] clazz) throws IOException {
        ensureConnectionAllowed();
        return connection.getContent(clazz);
    }
    
    public void disconnect() {
        connection.disconnect();
    }
    
    public String getHeaderFieldKey(int param) {
        return connection.getHeaderFieldKey(param);
    }
    
    public long getExpiration() {
        return connection.getExpiration();
    }
    
    public void setDoInput(boolean param) {
        connection.setDoInput(param);
    }
    
    public Object getContent() throws IOException {
        ensureConnectionAllowed();
        return connection.getContent();
    }
    
    public boolean getUseCaches() {
        return connection.getUseCaches();
    }
    
    public long getLastModified() {
        return connection.getLastModified();
    }
    
    public boolean getDoInput() {
        return connection.getDoInput();
    }
    
    public String getContentType() {
        return connection.getContentType();
    }
    
    public Map getHeaderFields() {
        return connection.getHeaderFields();
    }
    
    public void setDoOutput(boolean param) {
        connection.setDoOutput(param);
    }
    
    public InputStream getInputStream() throws IOException {
        ensureConnectionAllowed();
        return connection.getInputStream();
    }
    
    public String getRequestProperty(String str) {
        return connection.getRequestProperty(str);
    }
    
    public int getHeaderFieldInt(String str, int param) {
        return connection.getHeaderFieldInt(str, param);
    }
    
    public void setInstanceFollowRedirects(boolean param) {
        connection.setInstanceFollowRedirects(param);
    }
    
    public void setIfModifiedSince(long param) {
        connection.setIfModifiedSince(param);
    }
    
    public String getContentEncoding() {
        return connection.getContentEncoding();
    }
    
    public void connect() throws IOException {
        ensureConnectionAllowed();
        connection.connect();
    }
    
    public int getContentLength() {
        return connection.getContentLength();
    }
    
    public boolean getAllowUserInteraction() {
        return connection.getAllowUserInteraction();
    }
}
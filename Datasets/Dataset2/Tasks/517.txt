StringManager.getManager("org.apache.tomcat.session");

/*
 * ====================================================================
 *
 * The Apache Software License, Version 1.1
 *
 * Copyright (c) 1999 The Apache Software Foundation.  All rights 
 * reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer. 
 *
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in
 *    the documentation and/or other materials provided with the
 *    distribution.
 *
 * 3. The end-user documentation included with the redistribution, if
 *    any, must include the following acknowlegement:  
 *       "This product includes software developed by the 
 *        Apache Software Foundation (http://www.apache.org/)."
 *    Alternately, this acknowlegement may appear in the software itself,
 *    if and wherever such third-party acknowlegements normally appear.
 *
 * 4. The names "The Jakarta Project", "Tomcat", and "Apache Software
 *    Foundation" must not be used to endorse or promote products derived
 *    from this software without prior written permission. For written 
 *    permission, please contact apache@apache.org.
 *
 * 5. Products derived from this software may not be called "Apache"
 *    nor may "Apache" appear in their names without prior written
 *    permission of the Apache Group.
 *
 * THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESSED OR IMPLIED
 * WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
 * OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED.  IN NO EVENT SHALL THE APACHE SOFTWARE FOUNDATION OR
 * ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
 * USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
 * OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
 * OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
 * SUCH DAMAGE.
 * ====================================================================
 *
 * This software consists of voluntary contributions made by many
 * individuals on behalf of the Apache Software Foundation.  For more
 * information on the Apache Software Foundation, please see
 * <http://www.apache.org/>.
 *
 * [Additional notices, if required by prior licensing conditions]
 *
 */ 


package org.apache.tomcat.session;

import org.apache.tomcat.core.*;
import org.apache.tomcat.util.StringManager;
import java.io.*;
import java.net.*;
import java.util.*;
import javax.servlet.*;
import javax.servlet.http.*;

/**
 * Core implementation of a server session
 *
 * @author James Duncan Davidson [duncan@eng.sun.com]
 * @author James Todd [gonzo@eng.sun.com]
 */

public class ServerSession {

    private StringManager sm =
        StringManager.getManager(Constants.Package);
    private Hashtable values = new Hashtable();
    private Hashtable appSessions = new Hashtable();
    private String id;
    private long creationTime = System.currentTimeMillis();;
    private long thisAccessTime = creationTime;
    private long lastAccessed = creationTime;
    private int inactiveInterval = -1;
    
    ServerSession(String id) {
	this.id = id;
    }

    public String getId() {
	return id;
    }

    public long getCreationTime() {
	return creationTime;
    }

    public long getLastAccessedTime() {
	return lastAccessed;
    }
    
    public ApplicationSession getApplicationSession(Context context,
        boolean create) {
	ApplicationSession appSession =
	    (ApplicationSession)appSessions.get(context);

	if (appSession == null && create) {

	    // XXX
	    // sync to ensure valid?
	    
	    appSession = new ApplicationSession(id, this, context);
	    appSessions.put(context, appSession);
	}

	// XXX
	// make sure that we haven't gone over the end of our
	// inactive interval -- if so, invalidate and create
	// a new appSession
	
	return appSession;
    }
    
    void removeApplicationSession(Context context) {
	appSessions.remove(context);
    }

    /**
     * Called by context when request comes in so that accesses and
     * inactivities can be dealt with accordingly.
     */

    void accessed() {
        // set last accessed to thisAccessTime as it will be left over
	// from the previous access

	lastAccessed = thisAccessTime;
	thisAccessTime = System.currentTimeMillis();
	
    }

    void validate() {
	// if we have an inactive interval, check to see if
        // we've exceeded it

	if (inactiveInterval != -1) {
	    int thisInterval =
		(int)(System.currentTimeMillis() - lastAccessed) / 1000;

	    if (thisInterval > inactiveInterval) {
		invalidate();

		ServerSessionManager ssm =
                    ServerSessionManager.getManager();

		ssm.removeSession(this);
	    }
	}
    }

    synchronized void invalidate() {
	Enumeration enum = appSessions.keys();

	while (enum.hasMoreElements()) {
	    Object key = enum.nextElement();
	    ApplicationSession appSession =
		(ApplicationSession)appSessions.get(key);

	    appSession.invalidate();
	}
    }
    
    public void putValue(String name, Object value) {
	if (name == null) {
            String msg = sm.getString("serverSession.value.iae");

	    throw new IllegalArgumentException(msg);
	}

	removeValue(name);  // remove any existing binding
	values.put(name, value);
    }

    public Object getValue(String name) {
	if (name == null) {
            String msg = sm.getString("serverSession.value.iae");

	    throw new IllegalArgumentException(msg);
	}

	return values.get(name);
    }

    public Enumeration getValueNames() {
	return values.keys();
    }

    public void removeValue(String name) {
	values.remove(name);
    }

    public void setMaxInactiveInterval(int interval) {
	inactiveInterval = interval;
    }

    public int getMaxInactiveInterval() {
	return inactiveInterval;
    }    

    // XXX
    // sync'd for safty -- no other thread should be getting something
    // from this while we are reaping. This isn't the most optimal
    // solution for this, but we'll determine something else later.
    
    synchronized void reap() {
	Enumeration enum = appSessions.keys();

	while (enum.hasMoreElements()) {
	    Object key = enum.nextElement();
	    ApplicationSession appSession =
		(ApplicationSession)appSessions.get(key);

	    appSession.validate();
	}
    }
}
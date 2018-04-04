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
 * Core implementation of an application level session
 *
 * @author James Duncan Davidson [duncan@eng.sun.com]
 * @author Jason Hunter [jch@eng.sun.com]
 * @author James Todd [gonzo@eng.sun.com]
 */

public class ApplicationSession implements HttpSession {

    private StringManager sm =
        StringManager.getManager(Constants.Package);
    private Hashtable values = new Hashtable();
    private String id;
    private ServerSession serverSession;
    private Context context;
    private long creationTime = System.currentTimeMillis();;
    private long thisAccessTime = creationTime;
    private long lastAccessed = creationTime;
    private int inactiveInterval = -1;
    private boolean valid = true;

    ApplicationSession(String id, ServerSession serverSession,
        Context context) {
        this.serverSession = serverSession;
	this.context = context;
        this.id = id;

	this.inactiveInterval = context.getSessionTimeOut();

        if (this.inactiveInterval != -1) {
            this.inactiveInterval *= 60;
        }
    }

    ServerSession getServerSession() {
	return serverSession;
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

	validate();
    }

    void validate() {
	// if we have an inactive interval, check to see if we've exceeded it
	if (inactiveInterval != -1) {
	    int thisInterval =
		(int)(System.currentTimeMillis() - lastAccessed) / 1000;

	    if (thisInterval > inactiveInterval) {
		invalidate();
	    }
	}
    }
    
    // HTTP SESSION IMPLEMENTATION METHODS
    
    public String getId() {
	if (valid) {
	    return id;
	} else {
	    String msg = sm.getString("applicationSession.session.ise");

	    throw new IllegalStateException(msg);
	}
    }

    public long getCreationTime() {
	if (valid) {
	    return creationTime;
	} else {
	    String msg = sm.getString("applicationSession.session.ise");

	    throw new IllegalStateException(msg);
	}
    }
    
    /**
     *
     * @deprecated
     */

    public HttpSessionContext getSessionContext() {
	return new SessionContextImpl();
    }
    
    public long getLastAccessedTime() {
	if (valid) {
	    return lastAccessed;
	} else {
	    String msg = sm.getString("applicationSession.session.ise");

	    throw new IllegalStateException(msg);
	}
    }

    public void invalidate() {
	serverSession.removeApplicationSession(context);

	// remove everything in the session

	Enumeration enum = values.keys();
	while (enum.hasMoreElements()) {
	    String name = (String)enum.nextElement();
	    removeValue(name);
	}

	valid = false;
    }

    public boolean isNew() {
	if (! valid) {
	    String msg = sm.getString("applicationSession.session.ise");

	    throw new IllegalStateException(msg);
	}

	if (thisAccessTime == creationTime) {
	    return true;
	} else {
	    return false;
	}
    }
    
    /**
     * @deprecated
     */

    public void putValue(String name, Object value) {
	setAttribute(name, value);
    }

    public void setAttribute(String name, Object value) {
        if (! valid) {
	    String msg = sm.getString("applicationSession.session.ise");

	    throw new IllegalStateException(msg);
	}

	if (name == null) {
	    String msg = sm.getString("applicationSession.value.iae");

	    throw new IllegalArgumentException(msg);
	}

	removeValue(name);  // remove any existing binding

	if (value != null && value instanceof HttpSessionBindingListener) {
	    HttpSessionBindingEvent e =
                new HttpSessionBindingEvent(this, name);

	    ((HttpSessionBindingListener)value).valueBound(e);
	}

	values.put(name, value);
    }

    /**
     * @deprecated
     */
    public Object getValue(String name) {
	return getAttribute(name);
    }

    public Object getAttribute(String name) {
	if (! valid) {
	    String msg = sm.getString("applicationSession.session.ise");

	    throw new IllegalStateException(msg);
	}

	if (name == null) {
	    String msg = sm.getString("applicationSession.value.iae");

	    throw new IllegalArgumentException(msg);
	}

	return values.get(name);
    }

    /**
     * @deprecated
     */
    public String[] getValueNames() {
	Enumeration e = getAttributeNames();
	Vector names = new Vector();

	while (e.hasMoreElements()) {
	    names.addElement(e.nextElement());
	}

	String[] valueNames = new String[names.size()];

	names.copyInto(valueNames);

	return valueNames;
	
    }

    public Enumeration getAttributeNames() {
	if (! valid) {
	    String msg = sm.getString("applicationSession.session.ise");

	    throw new IllegalStateException(msg);
	}

	Hashtable valuesClone = (Hashtable)values.clone();

	return (Enumeration)valuesClone.keys();
    }

    /**
     * @deprecated
     */

    public void removeValue(String name) {
	removeAttribute(name);
    }

    public void removeAttribute(String name) {
	if (! valid) {
	    String msg = sm.getString("applicationSession.session.ise");

	    throw new IllegalStateException(msg);
	}

	if (name == null) {
	    String msg = sm.getString("applicationSession.value.iae");

	    throw new IllegalArgumentException(msg);
	}

	Object o = values.get(name);

	if (o instanceof HttpSessionBindingListener) {
	    HttpSessionBindingEvent e =
                new HttpSessionBindingEvent(this,name);

	    ((HttpSessionBindingListener)o).valueUnbound(e);
	}

	values.remove(name);
    }

    public void setMaxInactiveInterval(int interval) {
	if (! valid) {
	    String msg = sm.getString("applicationSession.session.ise");

	    throw new IllegalStateException(msg);
	}

	inactiveInterval = interval;
    }

    public int getMaxInactiveInterval() {
	if (! valid) {
	    String msg = sm.getString("applicationSession.session.ise");

	    throw new IllegalStateException(msg);
	}

	return inactiveInterval;
    }
}
//	realSession=null;

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


package org.apache.tomcat.facade;

import org.apache.tomcat.core.*;
import org.apache.tomcat.util.res.StringManager;
import java.io.*;
import java.net.*;
import java.util.*;
import javax.servlet.*;
import javax.servlet.http.*;

/**
 * Facade for http session. Used to prevent servlets to access
 * internal tomcat objects.
 *
 * This is a "special" facade - since session management is
 * (more or less) orthogonal to request processing, it is
 * indpendent of tomcat architecture. It will provide a
 * HttpSession implementation ( but it's not guaranteed
 * in any way it is "safe" ), and HttpSessionFacade will
 * act as a "guard" to make sure only servlet API public
 * methods are exposed.
 *
 * Another thing to note is that this object will be recycled
 * and will allways be set in a request. The "real" session
 * object will determine if the request is part of a session.
 *
 * @author James Duncan Davidson [duncan@eng.sun.com]
 * @author Jason Hunter [jch@eng.sun.com]
 * @author James Todd [gonzo@eng.sun.com]
 * @author costin@eng.sun.com
 */
final class HttpSessionFacade implements HttpSession {
    private static StringManager sm =
        StringManager.getManager("org.apache.tomcat.resources");
    ServerSession realSession;
    
    HttpSessionFacade() {
    }

    /** Package-level method - accessible only by core
     */
    void setRealSession(ServerSession s) {
 	realSession=s;
	realSession.setFacade( this );
     }

    /** Package-level method - accessible only by core
     */
    void recycle() {
	realSession=null;
    }

    // -------------------- public facade --------------------

    public String getId() {
	checkValid();
	return realSession.getId().toString();
    }

    /**
     * Return the time when this session was created, in milliseconds since
     * midnight, January 1, 1970 GMT.
     *
     * @exception IllegalStateException if this method is called on an
     *  invalidated session
     */
    public long getCreationTime() {
	checkValid();
	return realSession.getTimeStamp().getCreationTime();
    }
    
    /**
     * We return our own "disabled" SessionContext -
     * regardless of what the real session returns.
     *
     * @deprecated
     */
    public HttpSessionContext getSessionContext() {
	return new SessionContextImpl();
    }
    
    public long getLastAccessedTime() {
	checkValid();
	return realSession.getTimeStamp().getLastAccessedTime();
    }

    /**
     * Invalidates this session and unbinds any objects bound to it.
     *
     * @exception IllegalStateException if this method is called on
     *  an invalidated session
     */
    public void invalidate() {
	checkValid();
 	realSession.getTimeStamp().setValid( false );
    }

    /**
     * Return <code>true</code> if the client does not yet know about the
     * session, or if the client chooses not to join the session.  For
     * example, if the server used only cookie-based sessions, and the client
     * has disabled the use of cookies, then a session would be new on each
     * request.
     *
     * @exception IllegalStateException if this method is called on an
     *  invalidated session
     */
    public boolean isNew() {
	checkValid();
	return realSession.getTimeStamp().isNew();
    }
    
    /**
     * @deprecated
     */
    public void putValue(String name, Object value) {
	setAttribute(name, value);
    }

    public void setAttribute(String name, Object value) {
	checkValid();

	// 	ServerSessionManager ssm=(ServerSessionManager)
	// 	    realSession.getManager();
	// Original code - it's up to session manager to decide
	// what it can handle. 
	// 	if (ssm.isDistributable() &&
	// 	  !(value instanceof Serializable))
	// 	    throw new IllegalArgumentException
	// 		(sm.getString("standardSession.setAttribute.iae"));
	
	realSession.setAttribute( name, value );
	if (value instanceof HttpSessionBindingListener)
	    ((HttpSessionBindingListener) value).valueBound
		(new HttpSessionBindingEvent( this, name));

    }

    /**
     * @deprecated
     */
    public Object getValue(String name) {
	return getAttribute(name);
    }

    public Object getAttribute(String name) {
	checkValid();
	return realSession.getAttribute(name);
    }
    
    /**
     * @deprecated
     */
    public String[] getValueNames() {
	checkValid();
	
	Enumeration attrs = getAttributeNames();
	String names[] = new String[realSession.getAttributeCount()];
	for (int i = 0; i < names.length; i++)
	    names[i] = (String)attrs.nextElement();
	return names;
    }

    /**
     * Return an <code>Enumeration</code> of <code>String</code> objects
     * containing the names of the objects bound to this session.
     *
     * @exception IllegalStateException if this method is called on an
     *  invalidated session
     */
    public Enumeration getAttributeNames() {
	checkValid();
	return realSession.getAttributeNames();
    }

    /**
     * @deprecated
     */
    public void removeValue(String name) {
	removeAttribute(name);
    }

    /**
     * Remove the object bound with the specified name from this session.  If
     * the session does not have an object bound with this name, this method
     * does nothing.
     * <p>
     * After this method executes, and if the object implements
     * <code>HttpSessionBindingListener</code>, the container calls
     * <code>valueUnbound()</code> on the object.
     *
     * @param name Name of the object to remove from this session.
     *
     * @exception IllegalStateException if this method is called on an
     *  invalidated session
     */
    public void removeAttribute(String name) {
	checkValid();
	Object object=realSession.getAttribute( name );
	realSession.removeAttribute(name);
	if (object instanceof HttpSessionBindingListener) {
	    ((HttpSessionBindingListener) object).valueUnbound
		(new HttpSessionBindingEvent( this, name));
	}

    }

    public void setMaxInactiveInterval(int interval) {
	realSession.getTimeStamp().setMaxInactiveInterval( interval * 1000 );
    }

    public int getMaxInactiveInterval() {
	checkValid();
	// We use long because it's better to do /1000 here than
	// every time the internal code does expire
	return (int)realSession.getTimeStamp().getMaxInactiveInterval()/1000;
    }

    // duplicated code, private
    private void checkValid() {
	if (!realSession.getTimeStamp().isValid()) {
	    throw new IllegalStateException
		(sm.getString("standardSession.getAttributeNames.ise"));
	}
    }

}
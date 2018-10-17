Object newS = ObjectSerializer.doSerialization( newLoader, orig);

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
package org.apache.tomcat.modules.session;

import java.io.*;
import java.util.Enumeration;
import java.util.Hashtable;
import java.util.Vector;
import org.apache.tomcat.util.*;
import org.apache.tomcat.util.threads.*;
import org.apache.tomcat.core.*;
import org.apache.tomcat.session.*;


/**
 * This is the adapter between tomcat and a StandardManager.
 * A session manager should not depend on tomcat internals - so you can
 * use it in other engines and back. All you need to do is
 * create an adapter ( tomcat Interceptor).
 *
 * You can even have multiple session managers per context - the first that
 * recognize the "requestedSessionId" will create it's own HttpSession object.
 * By using standard tomcat interceptor mechanisms you can plug in one or
 * many session managers per context or context manager ( or even per
 * URL - but that's not standard API feature ).
 * 
 * It must be inserted after SessionInterceptor, which does common
 * session stuff ( cookie, rewrite, etc)
 *
 * @author costin@eng.sun.com
 * @author hans@gefionsoftware.com
 * @author pfrieden@dChain.com
 * @author Shai Fultheim [shai@brm.com]
 */
public final class SimpleSessionStore  extends BaseInterceptor {
    int manager_note;

    int checkInterval = 60;
    int maxActiveSessions = -1;
    String randomClass=null;
    
    public SimpleSessionStore() {
    }

    // -------------------- Configuration properties --------------------

    /**
     * Set the check interval (in seconds) for this Manager.
     *
     * @param checkInterval The new check interval
     */
    public void setCheckInterval( int secs ) {
	checkInterval=secs;
    }

    public void setMaxActiveSessions( int count ) {
	maxActiveSessions=count;
    }

    public final void setRandomClass(String randomClass) {
	this.randomClass=randomClass;
	System.setProperty(ContextManager.RANDOM_CLASS_PROPERTY, randomClass);
    }

    
    // -------------------- Tomcat request events --------------------
    public void engineInit( ContextManager cm ) throws TomcatException {
	// set-up a per/container note for StandardManager
	manager_note = cm.getNoteId( ContextManager.CONTAINER_NOTE,
				     "tomcat.standardManager");
    }

    /**
     *  StandardManager will set the HttpSession if one is found.
     */
    public int requestMap(Request request ) {
	String sessionId = null;
	Context ctx=request.getContext();
	if( ctx==null ) {
	    log( "Configuration error in StandardSessionInterceptor " +
		 " - no context " + request );
	    return 0;
	}

	// "access" it and set HttpSession if valid
	sessionId=request.getRequestedSessionId();

	if (sessionId != null && sessionId.length()!=0) {
	    // GS, We are in a problem here, we may actually get
	    // multiple Session cookies (one for the root
	    // context and one for the real context... or old session
	    // cookie. We must check for validity in the current context.
	    ServerSessionManager sM = getManager( ctx );    
	    ServerSession sess= request.getSession( false );

	    // if not set already, try to find it using the session id
	    if( sess==null )
		sess=sM.findSession( sessionId );

	    // 3.2 - Hans fix ( use the session id from URL ) - it's
	    // part of the current code

	    // 3.2 - PF ( pfrieden@dChain.com ): fix moved to SessionId.
	    // ( check if the ID is valid before setting it, do that
	    //  for cookies since we can have multiple cookies, some
	    //  from old sessions )

	    if(null != sess) {
		// touch it 
		sess.getTimeStamp().touch( System.currentTimeMillis() );

		//log("Session found " + sessionId );
		// set it only if nobody else did !
		if( null == request.getSession( false ) ) {
		    request.setSession( sess );
		    // XXX use MessageBytes!
		    request.setSessionId( sessionId );
		    //log("Session set " + sessionId );
		}
	    }
	    return 0;
	}
	return 0;
    }
    
    public void reload( Request req, Context ctx ) {
	ClassLoader newLoader = ctx.getClassLoader();
	ServerSessionManager sM = getManager( ctx );    

	// remove all non-serializable objects from session
	Enumeration sessionEnum=sM.getSessions().keys();
	while( sessionEnum.hasMoreElements() ) {
	    ServerSession session = (ServerSession)sessionEnum.nextElement();
	    Enumeration e = session.getAttributeNames();
	    while( e.hasMoreElements() )   {
		String key = (String) e.nextElement();
		Object value = session.getAttribute(key);
		// XXX XXX We don't have to change loader for objects loaded
		// by the parent loader ?
		if (! ( value instanceof Serializable)) {
		    session.removeAttribute( key );
		    // XXX notification!!
		}
	    }
	}

	// XXX We should change the loader for each object, and
	// avoid accessing object's internals
	// XXX PipeStream !?!
	Hashtable orig= sM.getSessions();
	Object newS = SessionSerializer.doSerialization( newLoader, orig);
	sM.setSessions( (Hashtable)newS );
	
	// Update the request session id
	String reqId=req.getRequestedSessionId();
	ServerSession sS=sM.findSession( reqId );
	if ( sS != null) {
	    req.setSession(sS);
	    req.setSessionId( reqId );
	}
    }
    
    public int newSessionRequest( Request request, Response response) {
	Context ctx=request.getContext();
	if( ctx==null ) return 0;
	
	ServerSessionManager sM = getManager( ctx );    

	if( request.getSession( false ) != null )
	    return 0; // somebody already set the session

	// Fix from Shai Fultheim: load balancing needs jvmRoute
	ServerSession newS=sM.getNewSession(request.getJvmRoute());
	request.setSession( newS );
	request.setSessionId( newS.getId().toString());
	return 0;
    }

    //--------------------  Tomcat context events --------------------
    
    /** Init session management stuff for this context. 
     */
    public void contextInit(Context ctx) throws TomcatException {
	// Defaults !!
	ServerSessionManager sm= getManager( ctx );
	
	if( sm == null ) {
	    sm=new ServerSessionManager();
	    ctx.getContainer().setNote( manager_note, sm );
	    sm.setMaxInactiveInterval( (long)ctx.getSessionTimeOut() *
				       60 * 1000 );
	}
	sm.setMaxActiveSessions( maxActiveSessions );

	Expirer expirer=new Expirer();
	expirer.setCheckInterval( checkInterval );
	expirer.setExpireCallback( new Expirer.ExpireCallback() {
		public void expired(TimeStamp o ) {
		    ServerSession sses=(ServerSession)o.getParent();
		    ServerSessionManager ssm=sses.getSessionManager();
		    ssm.removeSession( sses );
		}
	    });
	expirer.start();
	sm.setExpirer(expirer);
    }
    
    /** Notification of context shutdown.
     *  We should clean up any resources that are used by our
     *  session management code. 
     */
    public void contextShutdown( Context ctx )
	throws TomcatException
    {
	if( debug > 0 ) ctx.log("Removing sessions from " + ctx );
	ServerSessionManager sm=getManager(ctx);
	sm.getExpirer().stop();
	sm.removeAllSessions();
    }

    // -------------------- Internal methods --------------------
    private ServerSessionManager getManager( Context ctx ) {
	return (ServerSessionManager)ctx.getContainer().getNote(manager_note);
    }



}
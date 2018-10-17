protected Log loghelper = Log.getLog("tc_log", this);

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
import java.util.Random;
import org.apache.tomcat.util.*;
import org.apache.tomcat.util.compat.*;
import org.apache.tomcat.util.threads.*;
import org.apache.tomcat.core.*;
import java.util.*;
import org.apache.tomcat.util.collections.SimplePool;
import org.apache.tomcat.util.log.*;
import org.apache.tomcat.util.buf.*;
import java.security.*;


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
    String randomClassName=null;
    // creating a Random is very expensive, make sure we reuse
    // instances ( keyed by class name - different contexts can use different
    // random sources 
    static Hashtable randoms=new Hashtable();
    
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
	this.randomClassName=randomClass;
	if( null == randoms.get( randomClassName) ) {
	    randoms.put( randomClassName,
			 createRandomClass( randomClassName ));
	}
    }

    
    // -------------------- Tomcat request events --------------------
    public void engineInit( ContextManager cm ) throws TomcatException {
	// set-up a per/container note for StandardManager
	manager_note = cm.getNoteId( ContextManager.CONTAINER_NOTE,
				     "tomcat.standardManager");
    }
    
    public void reload( Request req, Context ctx ) throws TomcatException {
	ClassLoader newLoader = ctx.getClassLoader();
	SimpleSessionManager sM = getManager( ctx );    

	// remove all non-serializable objects from session
	Enumeration sessionEnum=sM.getSessions().keys();
	while( sessionEnum.hasMoreElements() ) {
	    ServerSession session = (ServerSession)sessionEnum.nextElement();

	    // Move it to SUSPEND state
	    BaseInterceptor reqI[]= req.getContainer().
		getInterceptors(Container.H_sessionState);
	    for( int i=0; i< reqI.length; i++ ) {
		// during suspend hook the servlet callbacks will be called
		// - typically from the ServletInterceptor
		reqI[i].sessionState( req,
				      session,  ServerSession.STATE_SUSPEND);
	    }
	    session.setState( ServerSession.STATE_SUSPEND );
	    
	    int oldLoaderNote=cm.getNoteId( ContextManager.CONTAINER_NOTE,
					    "oldLoader");
	    ClassLoader oldLoader=(ClassLoader)ctx.getContainer().
		getNote(oldLoaderNote);

	    Hashtable newSession=new Hashtable();
	    Enumeration e = session.getAttributeNames();
	    while( e.hasMoreElements() )   {
		String key = (String) e.nextElement();
		Object value = session.getAttribute(key);

		if( value.getClass().getClassLoader() != oldLoader ) {
		    // it's loaded by the parent loader, no need to reload
		    newSession.put( key, value );
		} else if ( value instanceof Serializable ) {
		    Object newValue =
			ObjectSerializer.doSerialization( newLoader,
							  value);
		    newSession.put( key, newValue );
		} 
	    }

	    // Move it to RESTORE state
	    reqI= req.getContainer().
		getInterceptors(Container.H_sessionState);
	    for( int i=0; i< reqI.length; i++ ) {
		// during suspend hook the servlet callbacks will be called
		// - typically from the ServletInterceptor
		reqI[i].sessionState( req,
				      session,  ServerSession.STATE_RESTORED);
	    }
	    session.setState( ServerSession.STATE_RESTORED );

	    /* now put back all attributs */
	    e=newSession.keys();
	    while(e.hasMoreElements() ) {
		String key = (String) e.nextElement();
		Object value=newSession.get(key );
		session.setAttribute( key, value );
	    }
	}

	
    }

    /** The session store hook
     */
    public ServerSession findSession( Request request,
				      String sessionId, boolean create)
    {
	Context ctx=request.getContext();
	if( ctx==null ) return null;
	SimpleSessionManager sM = getManager( ctx );    
	
	ServerSession sess=sM.findSession( sessionId );
	if( sess!= null ) return sess;

	if( ! create ) return null; // not found, don't create

	// create new session
	// Fix from Shai Fultheim: load balancing needs jvmRoute
	ServerSession newS=sM.getNewSession(request.getJvmRoute());
	if( newS==null ) return null;
	newS.setContext( ctx );
	
	return newS;
    }

    //--------------------  Tomcat context events --------------------


    /** Init session management stuff for this context. 
     */
    public void contextInit(Context ctx) throws TomcatException {
	// Defaults !!
	SimpleSessionManager sm= getManager( ctx );
	
	if( sm == null ) {
	    sm=new SimpleSessionManager();
	    ctx.getContainer().setNote( manager_note, sm );
	    if( randomClassName==null )
		setRandomClass("java.security.SecureRandom" );
	    sm.setRandomSource( (Random)randoms.get( randomClassName ));
	    sm.setMaxInactiveInterval( (long)ctx.getSessionTimeOut() *
				       60 * 1000 );
	}
	sm.setMaxActiveSessions( maxActiveSessions );

	Expirer expirer=new Expirer();
	expirer.setCheckInterval( checkInterval );
	expirer.setExpireCallback( new Expirer.ExpireCallback() {
		public void expired(TimeStamp o ) {
		    ServerSession sses=(ServerSession)o.getParent();
		    SimpleSessionManager ssm=(SimpleSessionManager)
			sses.getManager();
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
	SimpleSessionManager sm=getManager(ctx);
	sm.getExpirer().stop();
	sm.removeAllSessions();
    }

    // -------------------- Internal methods --------------------
    private SimpleSessionManager getManager( Context ctx ) {
	return (SimpleSessionManager)ctx.getContainer().getNote(manager_note);
    }

    private Random createRandomClass( String s ) {
	Random randomSource=null;
	String className = s;
	if (className != null) {
	    try {
		Class randomClass = Class.forName(className);
		randomSource = (java.util.Random)randomClass.newInstance();
	    } catch (Exception e) {
		e.printStackTrace();
	    }
	}
	if (randomSource == null)
	    randomSource = new java.security.SecureRandom();
	return randomSource;
    }
    
}

/**
 * The actual "simple" manager
 * 
 */
class SimpleSessionManager  
{
    protected Log loghelper = new Log("tc_log", this);
    
    /** The set of previously recycled Sessions for this Manager.
     */
    protected SimplePool recycled = new SimplePool();

    /**
     * The set of currently active Sessions for this Manager, keyed by
     * session identifier.
     */
    protected Hashtable sessions = new Hashtable();

    protected Expirer expirer;
    /**
     * The interval (in seconds) between checks for expired sessions.
     */
    private int checkInterval = 60;

    /**
     * The maximum number of active Sessions allowed, or -1 for no limit.
     */
    protected int maxActiveSessions = -1;

    long maxInactiveInterval;
    
    protected Reaper reaper;
    Random randomSource=null;
    
    public SimpleSessionManager() {
    }

    public void setExpirer( Expirer ex ) {
	expirer = ex;
    }

    public Expirer getExpirer() {
	return expirer;
    }

    public void setRandomSource( Random r ) {
	randomSource=r;
    }

    // ------------------------------------------------------------- Properties

    public int getMaxActiveSessions() {
	return maxActiveSessions;
    }

    public void setMaxActiveSessions(int max) {
	maxActiveSessions = max;
    }

    // --------------------------------------------------------- Public Methods

    public void setMaxInactiveInterval( long l ) {
	maxInactiveInterval=l;
    }
    
    /**
     * Return the default maximum inactive interval (in miliseconds)
     * for Sessions created by this Manager. We use miliseconds
     * because that's how the time is expressed, avoid /1000
     * in the common code
     */
    public long getMaxInactiveInterval() {
	return maxInactiveInterval;
    }


    public Hashtable getSessions() {
	return sessions;
    }
    
    public void setSessions(Hashtable s) {
	sessions=s;
    }

    public ServerSession findSession(String id) {
	if (id == null) return null;
	return (ServerSession)sessions.get(id);
    }

    /**
     * Remove this Session from the active Sessions for this Manager.
     *
     * @param session Session to be removed
     */
    public void removeSession(ServerSession session) {
	sessions.remove(session.getId().toString());
	recycled.put(session);
	// announce the state change
	BaseInterceptor reqI[]=session.getContext().getContainer().
	    getInterceptors(Container.H_sessionState);
	for( int i=0; i< reqI.length; i++ ) {
	    // during suspend hook the servlet callbacks will be called
	    // - typically from the ServletInterceptor
	    reqI[i].sessionState( null,
				  session,  ServerSession.STATE_EXPIRED);
	}
	session.setState( ServerSession.STATE_EXPIRED );
	
	session.removeAllAttributes();
	expirer.removeManagedObject( session.getTimeStamp());
	session.setValid(false);
	
    }

    public ServerSession getNewSession() {
	return getNewSession( null ) ;
    }

    static Jdk11Compat jdk11Compat=Jdk11Compat.getJdkCompat();
    
    public ServerSession getNewSession(String jsIdent) {
	if ((maxActiveSessions >= 0) &&
	    (sessions.size() >= maxActiveSessions)) {
	    loghelper.log( "Too many sessions " + maxActiveSessions );
	    return null;
	}

	// Recycle or create a Session instance
	ServerSession session = (ServerSession)recycled.get();
	if (session == null) {
	    session = new ServerSession();
	    session.setManager( this );
	}
	
	// XXX can return MessageBytes !!!

        /**
         * When using a SecurityManager and a JSP page or servlet triggers
         * creation of a new session id it must be performed with the 
         * Permissions of this class using doPriviledged because the parent
         * JSP or servlet may not have sufficient Permissions.
         */
	String newId;
        if( System.getSecurityManager() != null ) {
            class doInit extends Action { // implements PrivilegedAction {
		private Random randomSource;
                private String jsIdent;
                public doInit(Random rs, String ident) {
		    randomSource = rs;
                    jsIdent = ident;
                }           
                public Object run() {
                    return SessionIdGenerator.getIdentifier(randomSource,
							    jsIdent);
                }           
            }    
            doInit di = new doInit(randomSource,jsIdent);
	    try {
		newId= (String)jdk11Compat.doPrivileged(di);
	    } catch( Exception ex ) {
		newId=null;
	    }
	    //AccessController.doPrivileged(di);
	} else {
	    newId= SessionIdGenerator.getIdentifier(randomSource, jsIdent);
	}

	// What if the newId belongs to an existing session ?
	// This shouldn't happen ( maybe we can try again ? )
	ServerSession oldS=findSession( newId );
	if( oldS!=null) {
	    // that's what the original code did
	    removeSession( oldS );
	}

	// Initialize the properties of the new session and return it
	session.getId().setString( newId );

	TimeStamp ts=session.getTimeStamp();
	ts.setNew(true);
	ts.setValid(true);

	ts.setCreationTime(System.currentTimeMillis());
	ts.setMaxInactiveInterval(getMaxInactiveInterval());
	session.getTimeStamp().setParent( session );

	//	System.out.println("New session: " + newId );
	sessions.put( newId, session );
	expirer.addManagedObject( session.getTimeStamp());
	return (session);
    }

    public void removeAllSessions() {
	Enumeration ids = sessions.keys();
	while (ids.hasMoreElements()) {
	    String id = (String) ids.nextElement();
	    ServerSession session = (ServerSession) sessions.get(id);
	    if (!session.getTimeStamp().isValid())
		continue;
	    removeSession( session );
	}
    }

}
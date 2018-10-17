public void setContextManager( ContextManager cm ) {

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


package org.apache.tomcat.core;

import org.apache.tomcat.util.log.Log;
import org.apache.tomcat.util.hooks.Hooks;

/** Implement "Chain of Responsiblity" pattern ( == hooks ).
 *
 *  You can extend this class and implement a number of hooks. The
 *  interceptor is added to a Container ( that represents a group of
 *  URLs where the interceptor will operate ) and the methods that
 *  are re-defined in the subclass are detected ( using introspection )
 *  and used to select the chains where the intercepptor is interested
 *  to participate.
 *
 *  It is possible to define new chains by adding a new method to this
 *  class. The caller ( "chain user" ) will determine the behavior in
 *  case of error and "call all" or "call until [condition]" rules.
 *
 *  Interceptors are the main extension mechanism for tomcat. They have full
 *  access and control all aspects in tomcat operation.
 *
 *  <p><b>Sandboxing. </b> Tomcat may be run in a java2 sandboxed environment.
 *  All request processing callbacks can be initiated as a result of 
 *  user ( untrusted ) code ( for example - a servlet creating a new session ).
 *
 *  The module is responsible for using doPriviledged() blocks for all
 *  actions that require special priviledges. "Base" modules ( included
 *  in the distribution ) that perform essential functionality must also
 *  ensure JDK1.1 compatibility. The priviledged block must be as small
 *  as possible and do only a clearly defined action.
 *  
 */
public class BaseInterceptor
{
    public static final int DECLINED=-1;
    public static final int OK=0;
    
    protected ContextManager cm;
    protected Container ct;
    // null for "global" interceptors
    protected Context ctx; 
    protected int debug=0;

    //  loghelper will use name of actual impl subclass
    protected Log loghelper = Log.getLog("org/apache/tomcat/core", this);

    public BaseInterceptor() {
    }

    // -------------------- Request notifications --------------------

    /**
     *  Called immediately after the request has been received, before
     *  any mapping.
     *
     *  This allows modules to alter the request before it is mapped, and
     *  implement decoding/encoding, detect charsets, etc.
     *  The request URI and (some) headers will be available.
     * 
     *  Similar with Apache's post_read_request
     */
    public int postReadRequest(Request request ) {
	return 0;
    }

    
    /** Handle mappings inside a context.
     *  You are required to respect the mappings in web.xml.
     */
    public int requestMap(Request request ) {
	return 0;
    }

    /** Will detect the context path for a request.
     *  It need to set: context, contextPath, lookupPath
     *
     *  A possible use for this would be a "user-home" interceptor
     *  that will implement ~costin servlets ( add and map them at run time).
     */
    public int contextMap( Request rrequest ) {
	return 0;
    }

    /** 
     *  This callback is used to extract and verify the user identity
     *  and credentials.
     *
     *  It will set the RemoteUser field if it can authenticate.
     *  The auth event is generated by a user asking for the remote
     *  user field of by tomcat if a request requires authenticated
     *  id.
     */
    public int authenticate(Request request, Response response) {
	return DECLINED;
    }

    /**
     *  Will check if the current ( authenticated ) user is authorized
     *  to access a resource, by checking if it have one of the
     *  required roles.
     *
     *  This is used by tomcat to delegate the authorization to modules.
     *  The authorize is called by isUserInRole() and by ContextManager
     *  if the request have security constraints.
     *
     *  @returns DECLINED if the module can't make a decision
     *           401 If the user is not authorized ( doesn't have
     *               any of the required roles )
     *           200 If the user have the right roles. No further module
     *               will be called.
     */
    public int authorize(Request request, Response response,
			 String reqRoles[]) {
	return DECLINED;
    }

    /** Called before service method is invoked. 
     */
    public int preService(Request request, Response response) {
	return 0;
    }

    /** Called before the first body write, and before sending
     *  the headers. The interceptor have a chance to change the
     *  output headers.
     *
     *  Before body allows you do do various
     *	actions before the first byte of the response is sent. After all
     *  those callbacks are called tomcat may send the status and headers
    */
    public int beforeBody( Request rrequest, Response response ) {
	return 0;
    }

    /** The hook for session managers. It'll be called to
     *  find or create a ServerSession object associated with a request.
     *
     *  There are 2 components of tomcat's session management - finding 
     *  the session ID, typically done during mapping ( either in tomcat
     *  or by a load balancer or web server ) and the actual storage
     *  manager ( including expiration, persistence, events, etc ).
     *
     *  This hook allow to plug different session managers. The mapping
     *  hooks ( combined with native code in the server/load balancer )
     *  are used to determine the session id and do low-level operations.
     *
     *  The hook will be called from the mapping hook whenever a session
     *  is detected ( create==false ) - the manager can update the timers.
     *  It will also be called if the user requests a new session, and
     *  none is created.
     *
     *  XXX should we return a status code and let the manager call
     *  req.setSession() ? Returning ServerSession seems more flexible,
     *  ( but different from the rest of the hooks )
     * @param reqSessionId if null the manager will generate the id
     */
    public ServerSession findSession( Request req,
				      String reqSessionId, boolean create) {
	return null;
    }

    /** Hook for session state changes.
     *  Will be called every time a session change it's state.
     *  A session module will announce all changes - like STATE_NEW when
     *  the session is created, STATE_EXPIRED when the session is expired,
     *  STATE_INVALID when the session is invalidated.
     */
    public int sessionState( Request req, ServerSession sess, int newState) {
	return 0;
    }

    
    /** Called before the output buffer is commited.
     */
    public int beforeCommit( Request request, Response response) {
	return 0;
    }


    /** Called after the output stream is closed ( either by servlet
     *  or automatically at end of service ).
     *
     * It is called after the servlet finished
     * sending the response ( either closeing the stream or ending ). You
     * can deal with connection reuse or do other actions
    */
    public int afterBody( Request request, Response response) {
	return 0;
    }

    /** Called after service method ends. Log is a particular use.
     */
    public int postService(Request request, Response response) {
	return 0;
    }

    /** Experimental hook: called after the request is finished,
	before returning to the caller. This will be called only
	on the main request, and will give interceptors a chance
	to clean up - that would be difficult in postService,
	that is called after included servlets too.

	Don't use this hook until it's marked final, I added it
	to deal with recycle() in facades - if we find a better
	solution this can go. ( unless people find it
	useful
     */
    public int postRequest(Request request, Response response) {
	return 0;
    }

    /** Hook for lazy evaluation of request info.
	This provides and uniform mechanism to allow modules to evaluate
	certain expensive request attributes/parameters when they are
	needed ( if ever ), and allows specialized modules and
	better integration with the web server/server modules.

	This replaces a number of hard-coded constructs and should
	clean up the core for un-needed dependencies, as well as provide
	flexibility in key areas as encoding, etc.
    */
    public Object getInfo( Context ctx, Request request,
			   int id, String key ) {
	return null;
    }

    public int setInfo( Context ctx, Request request,
			int id, String key, Object obj ) {
	return DECLINED;
    }

    /** This callback is called whenever an exception happen.
     *  If t is null assume this is a "status" report ( 500, 404, etc).
     *
     *  During this hook it is possible to create a sub-request
     *  and call the handler, and it is possible that the sub-request
     *  will also generate an exception. The handler must insure
     *  no loops will happen - but it's free to choose whatever method
     *  it wants.
     *
     *  It's also the handler responsiblity to insure correct
     *  servlet API semantics - if the spec becomes incopmatible
     *  with previous versions ( or multiple interpretations are
     *  possible) that can be made a context-specific handler.
     *
     *  @returns 200 if the error was handled ( similar with Apache's
     *           OK )
     *           0   if this handler can't deal with the error ( to
     *           allow chaining )
     */
    public int handleError( Request request, Response response, Throwable t) {
	return 0;
    }
    
    //-------------------- Engine state hooks --------------------

    /** Hook called when a new interceptor is added. All existing
     *	modules will be notified of the new added module.
     *
     *  This hook will be called before the interceptor is initialized
     *  ( using engineInit hook )
     *
     *  An interceptor can add/remove other interceptors or applications,
     *  or alter the ordering of hooks, or change/set server properties.
     * 
     *  @param cm  the server
     *  @param ctx not null if this is a local interceptor
     *  @param i  the new added interceptor
     *  @exception TomcatException The module will not be added if any
     *  module throws an exception.
     */
    public void addInterceptor( ContextManager cm, Context ctx,
				BaseInterceptor i )
	throws TomcatException
    {
    }
    
    /** Hook called when interceptors are removed. All existing
     *	modules will be notified of the module removal.
     *
     *  This hook will be called before the interceptor is removed
     * 
     *  @param cm  the server
     *  @param ctx not null if this is a local interceptor
     *  @param i  the removed interceptor
     *  @exception TomcatException is logged, but will not have any effect
     */
    public void removeInterceptor( ContextManager cm, Context ctx,
				BaseInterceptor i )
	throws TomcatException
    {
    }
    
    /** Initialize the module.
     *
     *  @exception TomcatException The module will not be added if any
     *  exception is thrown by engineInit.
     */
    public void engineInit(ContextManager cm)
	throws TomcatException
    {
    }

    /**
     *  Shut down the module.
     *
     *  @exception If any exception is reported, the module will be removed.
     *   XXX (?)
     */
    public void engineShutdown(ContextManager cm)
	throws TomcatException
    {
    }

    /** Notify that the server is ready and able to process requests
     */
    public  void engineStart(ContextManager cm )
	throws TomcatException
    {
    }
    

    /** Notify that the server is disabled and shoulnd't process more
     * requests
     */
    public  void engineStop(ContextManager cm )
	throws TomcatException
    {
    }

    /** Notifies the module that the server changed it's state.
     *  XXX this seems more flexible than init/start/stop/shutdown.
     */
    public void engineState( ContextManager cm, int state )
    	throws TomcatException
    {
    }


    // -------------------- Context hooks --------------------
    
    /**
     *  Called when a context is added to a CM. The context is probably not
     *  initialized yet, only path, docRoot, host, and properties set before
     *  adding the context ( in server.xml for example ) are available.
     * 
     *  At this stage mappers can start creating structures for the
     *  context ( the actual loading of the context may be delayed in
     *  future versions of tomcat until the first access ).
     *
     *  DefaultCMSetter will also adjust the logger and paths
     *  based on context manager properties.
     *
     *  Any activity that depends on web.xml must be done at
     *  init time.
     */
    public void addContext( ContextManager cm, Context ctx )
	throws TomcatException
    {
    }

    /** Called when a context is removed from a CM. A context is removed
     *  either as a result of admin ( remove or update), to support "clean"
     *  servlet reloading or at shutdown.
     */
    public void removeContext( ContextManager cm, Context ctx )
	throws TomcatException
    {
    }

    /** Notify when a context is initialized.
     *  The first interceptor in the chain for contextInit must read web.xml
     *  and set the context. When this method is called you can expect the
     *  context to be filled in with all the informations from web.xml.
     * 
     *  @exception If the interceptor throws exception the context will 
     *             not be initialized ( state==NEW or ADDED or DISABLED ).
     */
    public void contextInit(Context ctx)
	throws TomcatException
    {
    }

    /** Called when a context is stoped, before removeContext.
     *  You must free all resources associated with this context.
     */
    public void contextShutdown(Context ctx)
	throws TomcatException
    {
    }

    /** Notify that the context state changed
     */
    public void contextState( Context ctx, int newState )
	throws TomcatException
    {
    }
    
    /** Reload notification - called whenever a reload is done.
	This can be used to serialize sessions, log the event,
	remove any resource that was class-loader dependent.

	Note. The current implementation uses a note "oldLoader"
	that will keep a reference to the previous class loader
	during this hook. It will be set by the module that creates
	the loaders, and should be destroyed when the hook is done.
	This can also be implemented using a get/setOldClassLoader
	in Context, but so far this is used in only 2 modules, adding
	new API is not needed.
     */
    public void reload( Request req, Context ctx)
	throws TomcatException
    {
    }

    // -------------------- Container ( or Location ) hooks ---------------
    
    /** Notify that certain properties are defined for a URL pattern.
     *  Properties can be a "handler" that will be called for URLs
     *  matching the pattern or "security constraints" ( or any other
     *  properties that can be associated with URL patterns )
     *
     *  Interceptors will maintain their own mapping tables if they are
     *  interested in a certain property. General-purpose mapping
     *  code is provided in utils.
     *
     *  The method will be called once for every properties associated
     *  with a URL - it's up to the interceptor to interpret the URL
     *  and deal with "merging".
     * 
     *  A Container that defines a servlet mapping ( handler ) will have
     *  the handlerName set to the name of the handler. The Handler
     *  ( getHandler) can be null for dynamically added servlets, and
     *  will be set by a facade interceptor.
     *
     *   XXX We use this hook to create ServletWrappers for dynamically
     *  added servlets in InvokerInterceptor ( JspInterceptor is JDK1.2
     *  specific ). It may be good to add a new hook specifically for that
     */
    public void addContainer(Container container)
	throws TomcatException
    {
    }

    /** A rule was removed, update the internal strucures. You can also
     *  clean up and reload everything using Context.getContainers()
     */

    public void removeContainer(Container container)
	throws TomcatException
    {
    }

    /** 
     */
    public void addSecurityConstraint( Context ctx, String path, Container ct )
	throws TomcatException
    {
    }

    /** Notification of a new content handler added to a context
     */
    public void addHandler( Handler h )
	throws TomcatException
    {
    }

    /** Notification of a content handler removal
     */
    public void removeHandler( Handler h )
	throws TomcatException
    {
    }

    // -------------------- Servlet-specific hooks --------------------
    
    /** Servlet Init  notification
     */
    public void preServletInit( Context ctx, Handler sw )
	throws TomcatException
    {
    }

    
    public void postServletInit( Context ctx, Handler sw )
	throws TomcatException
    {
    }

    /** Servlet Destroy  notification
     */
    public void preServletDestroy( Context ctx, Handler sw )
	throws TomcatException
    {
    }

    
    public void postServletDestroy( Context ctx, Handler sw )
	throws TomcatException
    {
    }

    // -------------------- Helpers --------------------
    // Methods used in internal housekeeping
    
    public final void setDebug( int d ) {
	debug=d;
    }

    public final void setContextManager( ContextManager cm ) {
	this.cm=cm;
	this.ct=cm.getContainer();
    }

    public final ContextManager getContextManager() {
	return cm;
    }

    /** Called for context-level interceptors
     */
    public void setContext( Context ctx ) {
	if( ctx == null ) return;
	this.ctx=ctx;
	this.cm=ctx.getContextManager();
	this.ct=ctx.getContainer();
    }

    public Context getContext() {
	return ctx;
    }

    public final void log( String s ) {
	loghelper.log(s);
    }

    public final void log( String s, Throwable t ) {
	loghelper.log(s, t);
    }
    
    public final void log( String s, int level ) {
	loghelper.log(s, level);
    }
    
    public final void log( String s, Throwable t, int level ) {
	loghelper.log(s, t, level);
    }

    public Log getLog() {
	return loghelper;
    }
    
    public final int getDebug() {
        return debug;
    }

    /** Special method for self-registered hooks, intended to support
     *  a mechanism similar with Apache2.0 and further extensibility
     *  without interface changes.
     *
     *  Most modules are added to the Hooks automatically. A module
     *  overriding this method has full control over this process.
     *  If OK is returned, no other processing is done ( i.e. no introspection,
     *  we assume the module set up the right hooks )
     */
    public int registerHooks(Hooks h, ContextManager cm, Context ctx) {
	return DECLINED;
    }

    // -------------------- Notes --------------------

    private Object notes[]=new Object[ContextManager.MAX_NOTES];
    
    public final void setNote( int pos, Object value ) {
	notes[pos]=value;
    }

    public final Object getNote( int pos ) {
	return notes[pos];
    }

    public Object getNote( String name ) throws TomcatException {
	int id=cm.getNoteId( ContextManager.MODULE_NOTE, name );
	return getNote( id );
    }

    public void setNote( String name, Object value ) throws TomcatException {
	int id=cm.getNoteId( ContextManager.MODULE_NOTE, name );
	setNote( id, value );
    }

}
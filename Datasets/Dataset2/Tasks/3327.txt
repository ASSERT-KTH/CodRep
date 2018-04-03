import org.apache.tomcat.util.log.Log;

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

import org.apache.tomcat.util.Counters;
import org.apache.tomcat.util.log.*;

/**
 * The class that will generate the actual response or response fragment.
 * Each Handler has a "name" that will determine the content that
 * it will handle.
 *
 * The choice to not use "mime/type" as Apache, NES, IIS
 * is based on the fact that most of the time servlets have "names", and
 * the mime handling is very different in servlet API.
 * It is possible to use mime types as a name, and special interceptors can
 * take advantage of that ( to better integrate with the server ), but
 * this is not a basic feature.
 *
 * Handlers will implement doService, doInit, doDestroy - all methods are
 * protected and can't be called from outside. This ensures the only entry
 * points are service(), init(), destroy() and the state and error handling
 * is consistent.
 *
 * Common properties:
 * <ul>
 *   <li>name
 *   <li>configuration parameters
 *   <li>
 * </ul>
 *
 * @author Costin Manolache
 */
public class Handler {
    // -------------------- State --------------------

    /** The handler is new, not part of any application.
     *  You must to add the handler to application before doing
     *  anything else.
     *  To ADDED by calling Context.addHandler().
     *  From ADDED by calling Context.removeHandler();
     */
    public static final int STATE_NEW=0;

    /** The handler is added to an application and can be initialized.
     *  To READY by calling init(), if success
     *  TO DISABLED by calling init if it fails ( exception )
     *  From READY by calling destroy()
     */
    public static final int STATE_ADDED=1;

    /** Handler is unable to perform - any attempt to use it should
     *  report an internal error. This is the result of an internal
     *  exception or an error in init()
     *  To ADDED by calling destroy()
     *  From ADDED by calling init() ( if failure )
     */
    public static final int STATE_DISABLED=4;

    // -------------------- Properties --------------------
    // the handler is part of a module
    protected BaseInterceptor module;
    
    protected ContextManager contextM;
    
    protected String name;
    protected int state=STATE_NEW;

    protected Exception errorException=null;
    
    // Debug
    protected int debug=0;
    protected Log logger=null;
    Handler next;
    Handler prev;


    private Counters cntr=new Counters(ContextManager.MAX_NOTES);
    private Object notes[]=new Object[ContextManager.MAX_NOTES];

    // -------------------- Constructor --------------------

    /** Creates a new handler.
     */
    public Handler() {
    }

    /** A handler is part of a module. The module can create a number
	of handlers. Since the module is configurable, it can 
	also configure the handlers - including debug, etc.

	The handler shares the same log file with the module ( it
	can log to different logs, but the default for debug information
	is shared with the other components of a module ).
     */
    public void setModule(BaseInterceptor module ) {
	this.module=module;
	contextM=module.getContextManager();
	debug=module.getDebug();
	logger=module.getLog();
    }

    public BaseInterceptor getModule() {
	return module;
    }
    
    // -------------------- configuration --------------------

    public int getState() {
	return state;
    }

    public void setState( int i ) {
	this.state=i;
    }
    
    public final String getName() {
	return name;
    }

    public final void setName(String handlerName) {
        this.name=handlerName;
    }

    // -------------------- Common servlet attributes
    /** Sets an exception that relates to the ability of the
	servlet to execute.  An exception may be set by an
	interceptor if there is an error during the creation
	of the servlet. 
     */
    public void setErrorException(Exception ex) {
	errorException = ex;
    }

    /** Gets the exception that relates to the servlet's
	ability to execute.
     */
    public Exception getErrorException() {
	return errorException;
    }

    // -------------------- Methods --------------------

    /** Call the service method, and notify all listeners
     *
     * @exception Exception if an error happens during handling of
     *   the request. Common errors are:
     *   <ul><li>IOException if an input/output error occurs and we are
     *   processing an included servlet (otherwise it is swallowed and
     *   handled by the top level error handler mechanism)
     *       <li>ServletException if a servlet throws an exception and
     *  we are processing an included servlet (otherwise it is swallowed
     *  and handled by the top level error handler mechanism)
     *  </ul>
     *  Tomcat should be able to handle and log any other exception ( including
     *  runtime exceptions )
     */
    public void service(Request req, Response res)
	throws Exception
    {
	BaseInterceptor reqI[]=
	    req.getContainer().getInterceptors(Container.H_preService);
	for( int i=0; i< reqI.length; i++ ) {
	    reqI[i].preService( req, res );
	}

	Exception serviceException=null;
	try {
	    doService( req, res );
	} catch( Exception ex ) {
	    // save error state on request and response
	    serviceException=ex;
	    // if new exception, update info
	    if ( ex != res.getErrorException() ) {
		//log("setErrorException " + ex ); 
		res.setErrorException(ex);
		res.setErrorURI(null);
	    }
	}

	// continue with the postService ( roll back transactions, etc )
	reqI=req.getContainer().getInterceptors(Container.H_postService);
	for( int i=0; i< reqI.length; i++ ) {
	    reqI[i].postService( req, res );
	}

	// if error, handle
	if( serviceException != null ) {
	    //log("handle " + serviceException );
	    //serviceException.printStackTrace();
	    handleServiceError( req, res, serviceException );
	    //log("XXX After handleServiceError");
	}
    }

    /** A handler may either directly generate the response or it can
     *	act as a part of a pipeline. Next/Prev allow modules to generically
     *  set the pipeline.
     *
     *  Most handlers will generate the content themself. Few handlers
     *  may prepare the request/response - one example is the Servlet
     *  handler that wraps them and calls a servlet. Modules may
     *  do choose to either hook into the server using the provided
     *  callbacks, or use a pipeline of handler ( valves ). 
     */	
    public void setNext( Handler next ) {
	this.next=next;
    }

    public Handler getNext() {
	return next;
    }

    public Handler getPrevious() {
	return prev;
    }

    public void setPrevious( Handler prev ) {
	this.prev=prev;
    }
    
    // -------------------- methods you can override --------------------
    
    protected void handleServiceError( Request req, Response res, Throwable t )
	throws Exception
    {
	//log("handleServiceError " + t);
	contextM.handleError( req, res, t );
    }
    
    /** Reload notification. This hook is called whenever the
     *  application ( this handler ) is reloaded
     */
    public void reload() {
    }
    
    // Old name, deprecated
    protected void doService(Request req, Response res)
	throws Exception
    {

    }

    /** This is the actual content generator. A handler must generate
     *  the response - either itself or by calling another class, after
     *  setting/changing request properties or altering/wrapping
     *  the request and response.
     *
     *  A Handler should use the "next" property if it is part
     *  of a pipeline ( "valve") 
     */
    protected void invoke(Request req, Response res)
	throws Exception
    {
	// backward compatibility
	doService(req, res);
    }

    // -------------------- Debug --------------------

    public String toString() {
	return name;
    }

    /** Debug level for this handler.
     */
    public final void setDebug( int d ) {
	debug=d;
    }

    protected final void log( String s ) {
	if ( logger==null ) 
	    contextM.log(s);
	else 
	    logger.log(s);
    }

    protected final void log( String s, Throwable t ) {
	if(logger==null )
	    contextM.log(s, t);
	else
	    logger.log(s, t);
    }

    // -------------------- Notes --------------------
    public final void setNote( int pos, Object value ) {
	notes[pos]=value;
    }

    public final Object getNote( int pos ) {
	return notes[pos];
    }

    /** Accounting information. Not implemented - it'll contain usefull
	information like LAST_ACCESSED, INVOCATION_COUNT, SERVICE_TIME,
	ERRROS, IN_INCLUDE, etc.
     */
    public final Counters getCounters() {
	return cntr;
    }


}
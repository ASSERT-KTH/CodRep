if( isReloadable ) {// && ! "invoker".equals( getServletName())) {

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

import org.apache.tomcat.facade.*;
import org.apache.tomcat.util.*;
import org.apache.tomcat.servlets.TomcatInternalServlet;
import java.io.*;
import java.net.*;
import java.util.*;
import javax.servlet.*;
import javax.servlet.http.*;

/**
 * Class used to represent a servlet inside a Context.
 * 
 * @author James Duncan Davidson [duncan@eng.sun.com]
 * @author Jason Hunter [jch@eng.sun.com]
 * @author James Todd [gonzo@eng.sun.com]
 * @author Harish Prabandham
 * @author costin@dnt.ro
 */
public class ServletWrapper extends Handler {

    // servletName is stored in config!
    protected String servletName;
    protected String servletClassName; // required
    protected Class servletClass;

    protected Servlet servlet;

    // facade
    protected ServletConfig configF;

    // Jsp pages
    private String path = null;

    // optional informations
    protected String description = null;

    // If init() fails, this will keep the reason.
    // init may be called when the servlet starts, but we need to
    // report the error later, to the client
    Exception unavailable=null;
    long unavailableTime=-1;
    
    // Usefull info for class reloading
    protected boolean isReloadable = false;
    // information + make sure destroy is called when no other servlet
    // is running ( this have to be revisited !) 
    protected long lastAccessed;
    protected int serviceCount = 0;
    
    int loadOnStartup=0;

    Hashtable securityRoleRefs=new Hashtable();

    public ServletWrapper() {
    }

    public void setContext( Context context) {
	super.setContext( context );
	isReloadable=context.getReloadable();
        configF = context.getFacadeManager().createServletConfig( this );
    }

    // -------------------- Servlet specific properties 
    public void setLoadOnStartUp( int level ) {
	loadOnStartup=level;
    }

    public void setLoadOnStartUp( String level ) {
	loadOnStartup=new Integer(level).intValue();
    }

    public int getLoadOnStartUp() {
	return loadOnStartup;
    }
    
    void setReloadable(boolean reloadable) {
	isReloadable = reloadable;
    }

    public String getServletName() {
	if(name!=null) return name;
	return path;
    }

    public void setServletName(String servletName) {
        this.servletName=servletName;
	name=servletName;
    }

    public String getServletDescription() {
        return this.description;
    }

    public void setDescription( String d ) {
	description=d;
    }
    
    public void setServletDescription(String description) {
        this.description = description;
    }

    public String getServletClass() {
        return this.servletClassName;
    }

    public void setServletClass(String servletClassName) {
	if( name==null ) name=servletClassName;
	this.servletClassName = servletClassName;
    }

    /** Security Role Ref represent a mapping between servlet role names and
     *  server roles
     */
    public void addSecurityMapping( String name, String role,
				    String description ) {
	securityRoleRefs.put( name, role );
    }

    public String getSecurityRole( String name ) {
	return (String)securityRoleRefs.get( name );
    }

    // -------------------- Jsp specific code
    // Will go in JspHandler
    
    public String getPath() {
        return this.path;
    }

    public void setPath(String path) {
        this.path = path;
    }

    // -------------------- 

    public Servlet getServlet() {
	if(servlet==null) {
	    try {
		loadServlet();
	    } 	catch( Exception ex ) {
		ex.printStackTrace();
	    }
	}
	return servlet;
    }

    protected void doDestroy() throws TomcatException {
	synchronized (this) {
	    // Fancy sync logic is to make sure that no threads are in the
	    // handlerequest when this is called and, furthermore, that
	    // no threads go through handle request after this method starts!
	    // Wait until there are no outstanding service calls,
	    // or until 30 seconds have passed (to avoid a hang)
		
	    //XXX I don't think it works ( costin )
	    
	    // XXX Move it to an interceptor!!!!
	    while (serviceCount > 0) {
		try {
		    wait(30000);
		    break;
		} catch (InterruptedException e) { }
	    }

	    try {
		if( servlet!=null) 
		    servlet.destroy();
	    } catch(Exception ex) {
		// Should never come here...
		context.log( "Error in destroy ", ex );
	    }
	}
    }

    /** Load and init a the servlet pointed by this wrapper
     */
    private void loadServlet()
	throws ClassNotFoundException, InstantiationException,
	IllegalAccessException
    {
	// XXX Move this to an interceptor, so it will be configurable.
	// ( and easier to read )
	if (servletClass == null) {
	    if (servletClassName == null) {
		throw new IllegalStateException("Can't happen - classname "
						+ "is null, who added this ?");
	    }
	    ServletLoader loader=context.getServletLoader();
	    servletClass=loader.loadClass(servletClassName);
	}
	
	servlet = (Servlet)servletClass.newInstance();

	// hack for internal servlets
	if( ! servletClassName.startsWith("org.apache.tomcat") ) return;
	if( servlet instanceof TomcatInternalServlet ) {
	    ((TomcatInternalServlet)servlet).setFacadeManager( context.
							 getFacadeManager());
	}
    }

    /** Override Handler's init - load the servlet before calling
	and interceptor
    */
    public void init()
    	throws Exception
    {
	// make sure the servlet in loaded before calling preInit
	// Jsp case - maybe another Jsp engine is used
	if( servlet==null && path != null ) {
	    handleJspInit();
	}
	// Will throw exception if it can't load, let upper
	// levels handle this
	//	try {
	if( servlet==null ) loadServlet();
	//	} catch( ClassNotFoundException ex ) {
	//	} catch( InstantiationException ex ) {
	//} catch( IllegalStateException ex ) {
	//}
	
	// Call pre, doInit and post
	super.init();
    }

    protected void doInit()
	throws Exception
    {
	// The servlet is loaded and not null - otherwise init()
	// throws exception
	try {
	    // if multiple threads will call the same servlet at once,
	    // we should have only one init 
	    synchronized( this ) {
		// we may have 2 threads entering doInit,
		// the first one may init the servlet
		if( initialized )
		    return;
		final Servlet sinstance = servlet;
		final ServletConfig servletConfig = configF;
		
		// init - only if unavailable was null or
		// unavailable period expired
		servlet.init(servletConfig);
		initialized=true;
	    }
	} catch( UnavailableException ex ) {
	    unavailable=ex;
	    unavailableTime=System.currentTimeMillis();
	    unavailableTime += ex.getUnavailableSeconds() * 1000;
	} catch( Exception ex ) {
	    unavailable=ex;
	}
    }

    /** Override service to hook reloading - it can be done in a clean
	interceptor. It also hooks jsp - we should have a separate
	JspHandler
    */
    public void service(Request req, Response res) 
    {
	try {
	    handleReload(req);
	} catch( TomcatException ex ) {
	    ex.printStackTrace();// what to do ?
	}

	// <servlet><jsp-file> case
	if( path!=null ) {
	    if( path.startsWith("/"))
		req.setAttribute( "javax.servlet.include.request_uri",
				  req.getContext().getPath()  + path );
	    else
		req.setAttribute( "javax.servlet.include.request_uri",
				  req.getContext().getPath()  + "/" + path );
	    req.setAttribute( "javax.servlet.include.servlet_path", path );
	}

	if( unavailable!=null  ) {
	    // Don't load if Unavailable timer is in place
	    if(  stillUnavailable() ) {
		handleUnavailable( req, res );
		initialized=false;
		return;
	    }
	    unavailable=null;// timer expired
	}

	// called only if unavailable==null or timer expired.
	// will do an init
	super.service( req, res );
    }

    protected void doService(Request req, Response res)
	throws Exception
    {
	// We are initialized and fine
	if (servlet instanceof SingleThreadModel) {
	    synchronized(servlet) {
		servlet.service(req.getFacade(), res.getFacade());
	    }
	} else {
	    servlet.service(req.getFacade(), res.getFacade());
	}
    }

    // -------------------- Reloading --------------------

    // XXX Move it to interceptor - so it can be customized
    // Reloading
    // XXX ugly - should find a better way to deal with invoker
    // The problem is that we are just clearing up invoker, not
    // the class loaded by invoker.
    void handleReload(Request req) throws TomcatException {
	// That will be reolved after we reset the context - and many
	// other conflicts.
	if( isReloadable && ! "invoker".equals( getServletName())) {
	    ServletLoader loader=context.getServletLoader();
	    if( loader!=null) {
		// XXX no need to check after we remove the old loader
		if( loader.shouldReload() ) {
		    // workaround for destroy 
		    try {
			destroy();
		    } catch(Exception ex ) {
			context.log( "Error in destroy ", ex );
		    }
		    initialized=false;
		    loader.reload();
		    
		    ContextManager cm=context.getContextManager();
		    cm.doReload( req, context );
		    
		    servlet=null;
		    servletClass=null;
		    /* Initial attempt to shut down the context and sessions.
		       
		       String path=context.getPath();
		       String docBase=context.getDocBase();
		       // XXX all other properties need to be saved
		       // or something else
		       ContextManager cm=context.getContextManager();
		       cm.removeContext(path);
		       Context ctx=new Context();
		       ctx.setPath( path );
		       ctx.setDocBase( docBase );
		       cm.addContext( ctx );
		       context=ctx;
		       // XXX shut down context, remove sessions, etc
		    */
		}
	    }
	}
    }


    // -------------------- Jsp hooks
        // <servlet><jsp-file> case - we know it's a jsp
    void handleJspInit() {
	// XXX Jsp Servlet is initialized, the servlet is not generated -
	// we can't hook in! It's jspServet that has to pass the config -
	// but it can't so easily, plus  it'll have to hook in.
	// I don't think that ever worked anyway - and I don't think
	// it can work without integrating Jsp handling into tomcat
	// ( using interceptor )
	ServletWrapper jspServletW = context.getServletByName("jsp");
	servletClassName = jspServletW.getServletClass();
    }
    

    // -------------------- Unavailable --------------------
    /** Check if we can try again an init
     */
    private boolean stillUnavailable() {
	// we have a timer - maybe we can try again - how much
	// do we have to wait - (in mSec)
	long moreWaitTime=unavailableTime - System.currentTimeMillis();
	if( unavailableTime > 0 && ( moreWaitTime < 0 )) {
	    // we can try again
	    unavailable=null;
	    unavailableTime=-1;
	    context.log(getServletName() + " unavailable time expired," +
			" try again ");
	    return false;
	} else {
	    return true;
	}
    }
    
    /** Send 503. Should be moved in ErrorHandling
     */
    private void handleUnavailable( Request req, Response res ) {
	if( unavailable instanceof UnavailableException ) {
	    int unavailableTime = ((UnavailableException)unavailable).
		getUnavailableSeconds();
	    if( unavailableTime > 0 ) {
		res.setHeader("Retry-After",
			      Integer.toString(unavailableTime));
	    }
	}

	String msg=unavailable.getMessage();
	long moreWaitTime=unavailableTime - System.currentTimeMillis();
	context.log( "Error in " + getServletName() +
		     "init(), error happened at " +
		     unavailableTime + " wait " + moreWaitTime +
		     " : " + msg, unavailable);
	req.setAttribute("javax.servlet.error.message", msg );
	res.setStatus(HttpServletResponse.SC_SERVICE_UNAVAILABLE); // 503
	contextM.handleStatus( req, res,
			       HttpServletResponse.SC_SERVICE_UNAVAILABLE );
	return;
    }


    // -------------------- Not found
    private void handleNotFound( Request req, Response res) {
	context.log( "Can't find servet " + getServletName() + " " +
		     getServletClass() );
	res.setStatus( 404 );
	contextM.handleStatus( req, res,  404 );
    }


}
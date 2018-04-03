import org.apache.tomcat.util.res.StringManager;

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
import org.apache.tomcat.util.StringManager;
import org.apache.tomcat.util.compat.*;
import org.apache.tomcat.util.http.*;
import java.io.*;
import java.util.*;
import java.security.*;
import javax.servlet.*;
import javax.servlet.http.*;

/* This code needs a re-write, it's very ugly.
   The hardest problem is the requirement to pass the "same" request, but with
   small modifications. One solution is to use a facade ( was used in tomcat
   origianlly ). The current solution is to save the modified attributes
   and restore after the method returns. This saves one object creation -
   since the subRequest object still has to be created.

   The details are facade-specific, shouldn't affect the core.
*/

/*
  We do a new sub-request for each include() or forward().
  Even if today we take all decisions based only on path, that may
  change ( i.e. a request can take different paths based on authentication,
  headers, etc - other Interceptors may affect it), that means we need to
  call CM.

  I think this is the correct action - instead of doing a lookup when
  we construct the dispatcher. ( costin )
 */

/**
 *
 *
 * @author James Duncan Davidson [duncan@eng.sun.com]
 * @author Jason Hunter [jch@eng.sun.com]
 * @author James Todd [gonzo@eng.sun.com]
 * @author Alex Cruikshank [alex@epitonic.com]
 * @author costin@dnt.ro
 */
final class RequestDispatcherImpl implements RequestDispatcher {
    static final boolean debug=false;
    // Use the strings from core
    private static StringManager sm = StringManager.
	getManager("org.apache.tomcat.resources");

    // Attributes that will be replaced during include
    private static final String A_REQUEST_URI=
	"javax.servlet.include.request_uri";
    private static final String A_CONTEXT_PATH=
    	"javax.servlet.include.context_path";
    private static final String A_SERVLET_PATH=
	"javax.servlet.include.servlet_path";
    private static final String A_PATH_INFO=
	"javax.servlet.include.path_info";
    private static final String A_QUERY_STRING=
	"javax.servlet.include.query_string";
    
    
    Context context;

    // path dispatchers
    String path;
    String queryString;

    // name dispatchers
    String name;

    /** Used for Context.getRD( path )
     */
    public RequestDispatcherImpl(Context context) {
        this.context = context;
    }

    public void setPath( String urlPath ) {
	// separate the query string
	int i = urlPath.indexOf("?");
	if( i<0 )
	    this.path=urlPath;
	else {
	    this.path=urlPath.substring( 0,i );
	    int len=urlPath.length();
	    if( i< len )
		this.queryString =urlPath.substring(i + 1);
        }
    }

    public void setName( String name ) {
	this.name=name;
    }

    // -------------------- Public methods --------------------

    // Wrappers for jdk1.2 priviledged actions
    Jdk11Compat jdk11Compat=Jdk11Compat.getJdkCompat();
    RDIAction forwardAction=new RDIAction( this,false);
    RDIAction includeAction=new RDIAction( this,true);
    
    public void forward(ServletRequest request, ServletResponse response)
	throws ServletException, IOException
    {
	if( System.getSecurityManager() != null ) {
	    try {
		forwardAction.prepare( request, response );
		jdk11Compat.doPrivileged( forwardAction );
	    } catch( Exception e) {
		wrapException( e, null );
	    }
	} else {
	    doForward(request,response);
	}
    }

    public void include(ServletRequest request, ServletResponse response)
	throws ServletException, IOException
    {
	if( System.getSecurityManager() != null ) {
	    try {
		includeAction.prepare( request, response );
		jdk11Compat.doPrivileged( includeAction );
	    } catch( Exception e) {
		wrapException( e, null );
	    }
	} else {
	    doInclude(request,response);
	}
    }

    // -------------------- Actual forward/include impl --------------------
    
    private void doForward(ServletRequest request, ServletResponse response)
	throws ServletException, IOException
    {
	/** We need to find the request/response. The servlet API
	 *  guarantees that we will receive the original request as parameter.
	 */
	Request realRequest = ((HttpServletRequestFacade)request).
	    getRealRequest();
        Response realResponse = realRequest.getResponse();

	// according to specs (as of 2.2: started is OK, just not committed)
	if (realResponse.isBufferCommitted()) 
	    throw new IllegalStateException(sm.getString("rdi.forward.ise"));

	// reset the output buffer but not the headers and cookies
	realResponse.resetBuffer();

	// the strange case in a separate method.
	if( name!=null) {
	    forwardNamed( request, response );
	    return;
	}
	
	// from strange spec reasons, forward and include are very different in
	// the way they process the request - if you don't understand the code
	// try to understand the spec.
	
	// in forward case, the Path parametrs of the request are what you 
	// expect, so we just do a new processRequest on the modified request

	// set the context - no need to fire context parsing again
	realRequest.setContext( context );

	realRequest.requestURI().setString( context.getPath() + path );

	// merge query string as specified in specs - before, it may affect
	// the way the request is handled by special interceptors
	if( queryString != null ) {
	    // Append queryString to the request parameters -
	    // the original request is changed.
	    realRequest.parameters().processParameters( queryString ); 
	    //	    addQueryString( realRequest, queryString );
	}
	
	// run the new request through the context manager
	// not that this is a very particular case of forwarding
	context.getContextManager().processRequest(realRequest);

	// unset "included" attribute if any - we may be in a servlet
	// included from another servlet,
	// in which case the attribute will create problems
	realRequest.removeAttribute( A_REQUEST_URI);
	realRequest.removeAttribute( A_SERVLET_PATH);


	// CM should have set the wrapper - call it
	Handler wr=realRequest.getHandler();
	if( wr!=null ) {
	    try {
		wr.service(realRequest, realResponse);
	    } catch( Exception ex ) {
		realResponse.setErrorException(ex);
	    }
	}

	// Clean up the request and response as needed
	// No action required

	if ( realResponse.isExceptionPresent() ) {
	    // if error URI not set, set our URI
	    if ( null == realResponse.getErrorURI() )
		realResponse.setErrorURI( context.getPath() + path );
	    Exception ex = realResponse.getErrorException();
	    wrapException( ex,
			   sm.getString("dispatcher.forwardException"));
	}
	
	// close the response - output after this point will be discarded.
	// XXX XXX Maybe this is Henri's bug !!!
	realResponse.finish();
    }

    // -------------------- Include --------------------

    private void doInclude(ServletRequest request, ServletResponse response)
	throws ServletException, IOException
    {
        Request realRequest = ((HttpServletRequestFacade)request).
	    getRealRequest();
	Response realResponse = realRequest.getResponse();
	

	if( debug ) {
	    System.out.println("RDI: doInclude: " + path + " " + name +
			       " " + queryString );
	}
	
	// the strange case in a separate method
	if( name!=null) {
	    includeNamed( request, response );
	    return;
	}

	// Implement the spec that "no changes in response, only write"
	// can also be done by setting the response to 0.9 mode
	//	IncludedResponse iResponse = new IncludedResponse(realResponse);
	boolean old_included=realResponse.isIncluded();
	if( ! old_included ) {
	    realResponse.setIncluded( true );
	}

	// We need to pass the original request, with all the paths -
	// and the new paths in special attributes.

	// We still need to find out where do we want to go ( today )
	// That means we create a subRequest with the new paths ( since
	// the mapping and aliasing is done on Requests), and run it
	// through prepare.

	// That also means that some special cases ( like the invoker !! )
	// will have to pay attention to the attributes, or we'll get a loop

	Request subRequest=context.getContextManager().
	    createRequest( context, path );
	subRequest.setParent( realRequest );
	subRequest.getTop(); // control inclusion depth

	// I hope no interceptor (or code) in processRequest use any
	// of the original request info ( like Auth headers )
	//
	// XXX We need to clone the request, so that processRequest can
	// make an informed mapping ( Auth, Authorization, etc)
	//
	// This will never work corectly unless we do a full clone - but
	// for simple cases ( no auth, etc) it does

	// note that we also need a dummy response - SessionInterceptors may
	// change something !
	subRequest.setResponse( realResponse );
	
	context.getContextManager().processRequest(subRequest);
	
	// Now subRequest containse the processed and aliased paths, plus
	// the wrapper that will handle the request.

	// We will use the stack a bit - save all path attributes, set the
	// new values, and after return from wrapper revert to the original
	Object old_request_uri=replaceAttribute(realRequest, A_REQUEST_URI,
						context.getPath() + path );
	Object old_context_path=replaceAttribute(realRequest, A_CONTEXT_PATH,
						 context.getPath());
	Object old_servlet_path=replaceAttribute(realRequest, A_SERVLET_PATH,
					 subRequest.servletPath().toString());
	Object old_path_info=replaceAttribute(realRequest, A_PATH_INFO,
					  subRequest.pathInfo().toString());
	Object old_query_string=replaceAttribute(realRequest, A_QUERY_STRING,
						 queryString);

	if( debug ) {
	    System.out.println("RDI: old " + old_request_uri + " " +
			       old_context_path + " " + old_servlet_path +
			       " " + old_path_info + " " + old_query_string);
	    System.out.println("RDI: new "+context.getPath() + " " + path + " "
			       + subRequest.servletPath().toString() + " " +
			       subRequest.pathInfo().toString() + " " +
			       queryString);
	}

	if( queryString != null ) {
	    // the original parameters will be preserved, and a new
	    // child Parameters will be used for the included request.
	    realRequest.parameters().push();
	    Parameters child=realRequest.parameters().getCurrentSet();

	    child.processParameters( queryString );
	    
	}

	Request old_child = realRequest.getChild();
	realRequest.setChild( subRequest );
	
 	// now it's really strange: we call the wrapper on the subrequest
	// for the realRequest ( since the real request will still have the
	// original handler/wrapper )

	Handler wr=subRequest.getHandler();
	if( wr!=null ) {
	    try {
		wr.service(realRequest, realResponse);
	    } catch( Exception ex ) {
		realResponse.setErrorException(ex);
	    }
	}

	
	// After request, we want to restore the include attributes - for
	// chained includes.

	realRequest.setChild( old_child );

	if( queryString != null ) {
	    // restore the parameters
	    realRequest.parameters().pop();
	}
	//realRequest.setParameters( old_parameters);

	replaceAttribute( realRequest, A_REQUEST_URI, old_request_uri);
	replaceAttribute( realRequest, A_CONTEXT_PATH,old_context_path); 
	replaceAttribute( realRequest, A_SERVLET_PATH, old_servlet_path);
	replaceAttribute( realRequest, A_PATH_INFO, old_path_info);
	replaceAttribute( realRequest, A_QUERY_STRING, old_query_string);
	
	// revert to the response behavior
	if( ! old_included ) {
	    realResponse.setIncluded( false );
	}

	// Rethrow original error if present
	if ( realResponse.isExceptionPresent() ) {
	    // if error URI not set, set our URI
	    if ( null == realResponse.getErrorURI() )
		realResponse.setErrorURI( context.getPath() + path );
	    Exception ex = realResponse.getErrorException();
	    wrapException( ex, sm.getString("dispatcher.includeException"));
	}
    }

    // -------------------- Special case of "named" dispatcher -------------

    /** Named dispatcher include
     *  Separate from normal include - which is still too messy
     */
    private void includeNamed(ServletRequest request, ServletResponse response)
	throws ServletException, IOException
    {
	// We got here if name!=null, so assert it
	Handler wr = context.getServletByName( name );
	// Use the original request - as in specification !
	Request realRequest=((HttpServletRequestFacade)request).getRealRequest();
	Response realResponse = realRequest.getResponse();

	// Set the "included" flag so that things like header setting in the
	// included servlet will be correctly ignored
	boolean old_included=realResponse.isIncluded();
	if( ! old_included ) realResponse.setIncluded( true );

	if( wr!=null) {
	    try {
		wr.service(realRequest, realResponse);
	    } catch( Exception ex ) {
		realResponse.setErrorException( ex );
	    }
	}

        // Clean up the request and response as needed
	if( ! old_included ) {
	    realResponse.setIncluded( false );
	}

	// Rethrow original error if present
	if ( realResponse.isExceptionPresent() ) {
	    // if error URI not set, set our URI
	    if ( null == realResponse.getErrorURI() )
		realResponse.setErrorURI( "named servlet: " + name );
	    wrapException( realResponse.getErrorException(),
			   sm.getString("dispatcher.includeException"));
	}
    }

    /** Named forward
     */
    private void forwardNamed(ServletRequest request, ServletResponse response)
	throws ServletException, IOException
    {
	// We got here if name!=null, so assert it
	Handler wr = context.getServletByName( name );

	// Use the original request - as in specification !
	Request realRequest=((HttpServletRequestFacade)request).
	    getRealRequest();
	Response realResponse = realRequest.getResponse();

	// Set the "included" flag so that things like header setting in the
	// included servlet will be correctly ignored
	boolean old_included=realResponse.isIncluded();
	if( ! old_included ) realResponse.setIncluded( true );

	if( wr!=null) {
	    try {
		wr.service(realRequest, realResponse);
	    } catch( Exception ex ) {
		wrapException( ex, null );
	    }
	}

	// Clean up the request and response as needed
	// No action required

	// Rethrow original error if present
	if ( realResponse.isExceptionPresent() ) {
	    // if error URI not set, set our URI
	    if ( null == realResponse.getErrorURI() )
		realResponse.setErrorURI( "named servlet: " + name );
	    wrapException( realResponse.getErrorException(),
			   sm.getString("dispatcher.forwardException"));
	}
    }    

    // -------------------- Special methods --------------------

    /** Restore attribute - if value is null, remove the attribute.
     *  ( or it is - null means no value in getAttribute, so setting to
     *    null should mean setting to no value. ?)
     */
    private Object replaceAttribute( Request realRequest, String name,
				     Object value)
    {
	Object oldAttribute=realRequest.getAttribute(name);
	if( value == null )
	    realRequest.removeAttribute( name );
	else
	    realRequest.setAttribute( name, value );
	return oldAttribute;
    }

    // Rethrow original error if present 
    private void wrapException(Exception ex, String msg)
	throws IOException, ServletException, RuntimeException
    {
	if ( ex instanceof IOException )
	    throw (IOException) ex;
	if ( ex instanceof RuntimeException )
	    throw (RuntimeException) ex;
	else if ( ex instanceof ServletException )
	    throw (ServletException) ex;
	else
	    if( msg==null )
		throw new ServletException(ex );
	    else
		throw new ServletException(msg, ex );
    }

    // -------------------- Used for doPriviledged in JDK1.2 ----------
    static class RDIAction extends Action {
	ServletRequest req;
	ServletResponse res;
	RequestDispatcherImpl rdi;
	boolean include;
	RDIAction(RequestDispatcherImpl rdi, boolean incl) {
	    this.rdi=rdi;
	    include=incl;
	}
	public void prepare( ServletRequest req, ServletResponse res ) {
	    this.req=req;
	    this.res=res;
	}
	public Object run() throws Exception {
	    if( include )
		rdi.doInclude( req, res );
	    else
		rdi.doForward( req, res );
	    return null;
	}
    }
}
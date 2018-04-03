(sm.getString("dispatcher.forwardException"), ex );

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
    // Use the strings from core
    private static StringManager sm = StringManager.
	getManager("org.apache.tomcat.resources");
    
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
    
    public void forward(ServletRequest request, ServletResponse response)
	throws ServletException, IOException
    {
	if( System.getSecurityManager() != null ) {
	    final ServletRequest req = request;
	    final ServletResponse res = response;
	    try {
		java.security.AccessController.doPrivileged(
		    new java.security.PrivilegedExceptionAction()
		    {
			public Object run() throws ServletException, IOException {
			    doForward(req,res);
			    return null;
			}
		    }               
		);
	    } catch( PrivilegedActionException pe) {
		Exception e = pe.getException();
		if( e instanceof ServletException )
		    throw (ServletException)e;
		throw (IOException)e;
	    }
	} else {
	    doForward(request,response);
	}
    }

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
	if( queryString != null )
	    addQueryString( realRequest, queryString );
	
	// run the new request through the context manager
	// not that this is a very particular case of forwarding
	context.getContextManager().processRequest(realRequest);

	// unset "included" attribute if any - we may be in a servlet
	// included from another servlet,
	// in which case the attribute will create problems
	realRequest.removeAttribute( "javax.servlet.include.request_uri");
	realRequest.removeAttribute( "javax.servlet.include.servlet_path");


	// CM should have set the wrapper - call it
	Handler wr=realRequest.getHandler();
	if( wr!=null ) 
	    invoke( wr, realRequest, realResponse);
	// Clean up the request and response as needed
	;       // No action required

	// Rethrow original error if present
	if ( realResponse.isExceptionPresent() ) {
	    // if error URI not set, set our URI
	    if ( null == realResponse.getErrorURI() )
		realResponse.setErrorURI( context.getPath() + path );
	    Exception ex = realResponse.getErrorException();
	    if ( ex instanceof IOException )
		throw (IOException) ex;
	    if ( ex instanceof RuntimeException )
		throw (RuntimeException) ex;
	    else if ( ex instanceof ServletException )
		throw (ServletException) ex;
	    else
		throw new ServletException
		    (sm.getString("dispatcher.forwardException", ex));
	}

	// close the response - output after this point will be discarded.
	realResponse.finish();
    }

    public void include(ServletRequest request, ServletResponse response)
	throws ServletException, IOException
    {
	if( System.getSecurityManager() != null ) {
	    final ServletRequest req = request;
	    final ServletResponse res = response;
	    try {
		java.security.AccessController.doPrivileged(
		    new java.security.PrivilegedExceptionAction()
		    {
			public Object run() throws ServletException, IOException {
			    doInclude(req,res);
			    return null;     
			}               
		    }    
		);   
	    } catch( PrivilegedActionException pe) {
		Exception e = pe.getException();       
		if( e instanceof ServletException )
		    throw (ServletException)e;
		throw (IOException)e;
	    }
	} else {
	    doInclude(request,response);
	}
    }

    private void doInclude(ServletRequest request, ServletResponse response)
	throws ServletException, IOException
    {
        Request realRequest = ((HttpServletRequestFacade)request).
	    getRealRequest();
	Response realResponse = realRequest.getResponse();

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

	// Here the spec is very special, pay attention

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
	Object old_request_uri=realRequest.
	    getAttribute("javax.servlet.include.request_uri");
	realRequest.setAttribute("javax.servlet.include.request_uri",
				 //				 path);
				 context.getPath() + path );

	Object old_context_path=realRequest.
	    getAttribute("javax.servlet.include.context_path");
	realRequest.setAttribute("javax.servlet.include.context_path",
				 context.getPath());
	// never change anyway - RD can't get out

	Object old_servlet_path=realRequest.
	    getAttribute("javax.servlet.include.servlet_path");
	realRequest.setAttribute("javax.servlet.include.servlet_path",
				 subRequest.servletPath().toString());
	
	Object old_path_info=realRequest.
	    getAttribute("javax.servlet.include.path_info");
	realRequest.setAttribute("javax.servlet.include.path_info",
				 subRequest.pathInfo().toString());

	Object old_query_string=realRequest.
	    getAttribute("javax.servlet.include.query_string");
	realRequest.setAttribute("javax.servlet.include.query_string",
				 queryString);
	
	if( false ) {
	    System.out.println("RD: " + old_request_uri + " " +
			       old_context_path + " " + old_servlet_path +
			       " " + old_path_info + " " + old_query_string);
	    System.out.println("NEW: " + context.getPath() + " " + path + " "
			       + subRequest.servletPath().toString() + " " +
			       subRequest.pathInfo().toString() + " " +
			       queryString);
	}
	
	// Not explicitely stated, but we need to save the old parameters
	// before adding the new ones
	realRequest.getParameterNames();
	// force reading of parameters from POST
	Hashtable old_parameters=(Hashtable)realRequest.getParameters().clone();

	// NOTE: it has a side effect of _reading_ the form data - which
	// is against the specs ( you can't read the post until asked for
	// parameters). I see no way of dealing with that -
	// if we don't do it and the included request need a parameter,
	// the form will be read and we'll have no way to know that.

	// IMHO the spec should do something about that - or smarter
	// people should implement the spec. ( costin )

	addQueryString( realRequest, queryString );

	Request old_child = realRequest.getChild();
	realRequest.setChild( subRequest );
	
 	// now it's really strange: we call the wrapper on the subrequest
	// for the realRequest ( since the real request will still have the
	// original handler/wrapper )
	Handler wr=subRequest.getHandler();
	if( wr!=null ) 
	    invoke( wr, realRequest, realResponse);
	
	// After request, we want to restore the include attributes - for
	// chained includes.
	realRequest.setChild( old_child );

	realRequest.setParameters( old_parameters);

	replaceAttribute( realRequest, "javax.servlet.include.request_uri",
				 old_request_uri);
	replaceAttribute( realRequest, "javax.servlet.include.context_path",
				 old_context_path); 
	replaceAttribute( realRequest, "javax.servlet.include.servlet_path",
				 old_servlet_path);
	replaceAttribute( realRequest, "javax.servlet.include.path_info",
				 old_path_info);
	replaceAttribute( realRequest, "javax.servlet.include.query_string",
				 old_query_string);
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
	    if ( ex instanceof IOException )
		throw (IOException) ex;
	    if ( ex instanceof RuntimeException )
		throw (RuntimeException) ex;	
	    else if ( ex instanceof ServletException )
		throw (ServletException) ex;
	    else
		throw new ServletException
		    (sm.getString("dispatcher.includeException"), ex);
	}
    }

	

    /** Named dispatcher include
     *  Separate from normal include - which is still too messy
     */
    public void includeNamed(ServletRequest request, ServletResponse response)
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

	if( wr!=null)
	    invoke( wr, realRequest, realResponse);

        // Clean up the request and response as needed
	if( ! old_included ) {
	    realResponse.setIncluded( false );
	}

	// Rethrow original error if present
	if ( realResponse.isExceptionPresent() ) {
	    // if error URI not set, set our URI
	    if ( null == realResponse.getErrorURI() )
		realResponse.setErrorURI( "named servlet: " + name );
	    Exception ex = realResponse.getErrorException();
	    if ( ex instanceof IOException )
		throw (IOException) ex;
	    else if ( ex instanceof ServletException )
		throw (ServletException) ex;
	    else
		throw new ServletException
		    (sm.getString("dispatcher.includeException", ex));
	}
    }

    /** Named forward
     */
    public void forwardNamed(ServletRequest request, ServletResponse response)
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

	if( wr!=null)
	    invoke( wr, realRequest, realResponse);

	// Clean up the request and response as needed
	;       // No action required

	// Rethrow original error if present
	if ( realResponse.isExceptionPresent() ) {
	    // if error URI not set, set our URI
	    if ( null == realResponse.getErrorURI() )
		realResponse.setErrorURI( "named servlet: " + name );
	    Exception ex = realResponse.getErrorException();
	    if ( ex instanceof IOException )
		throw (IOException) ex;
	    else if ( ex instanceof ServletException )
		throw (ServletException) ex;
	    else
		throw new ServletException
		    (sm.getString("dispatcher.forwardException", ex));
	}
    }    

    /**
     * Adds a query string to the existing set of parameters.
     * The additional parameters represented by the query string will be
     * merged with the existing parameters.
     * Used by the RequestDispatcherImpl to add query string parameters
     * to the request.
     *
     * @param inQueryString URLEncoded parameters to add
     */
    void addQueryString(Request req, String inQueryString) {
        // if query string is null, do nothing
        if ((inQueryString == null) || (inQueryString.trim().length() <= 0))
            return;

	Hashtable newParams = HttpUtils.parseQueryString(queryString);
	Hashtable parameters= req.getParameters();

	// add new to old ( it alters the original hashtable in request)
	Enumeration e=newParams.keys();
	while(e.hasMoreElements() ) {
	    String key=(String)e.nextElement();
	    Object oldValue = parameters.get(key);
	    Object newValue = newParams.get(key);
	    // The simple case -- no existing parameters with this name
	    if (oldValue == null) {
		parameters.put( key, newValue);
		continue;
	    }
	    // Construct arrays of the old and new values
	    String oldValues[] = null;
	    if (oldValue instanceof String[]) {
		oldValues = (String[]) oldValue;
	    } else if (oldValue instanceof String) {
		oldValues = new String[1];
		oldValues[0] = (String) oldValue;
	    } else {
		// Can not happen?
		oldValues = new String[1];
		oldValues[0] = oldValue.toString();
	    }
	    String newValues[] = null;
	    if (newValue instanceof String[]) {
		newValues = (String[]) newValue;
	    } else if (newValue instanceof String) {
		newValues = new String[1];
		newValues[0] = (String) newValue;
	    } else {
		// Can not happen?
		newValues = new String[1];
		newValues[0] = newValue.toString();
	    }
	    // Merge the two sets of values into a new array
	    String mergedValues[] =
		new String[newValues.length + oldValues.length];
	    for (int i = 0; i < newValues.length; i++)
		mergedValues[i] = newValues[i];	// New values first per spec
	    for (int i = newValues.length; i < mergedValues.length; i++)
		mergedValues[i] = oldValues[i - newValues.length];
	    // Save the merged values list in the original request
	    parameters.put(key, mergedValues);
	}
    }

    /** Restore attribute - if value is null, remove the attribute.
     *  X Maybe it should be the befavior of setAttribute() - it is not
     *  specified what to do with null.
     *  ( or it is - null means no value in getAttribute, so setting to
     *    null should mean setting to no value. ?)
     */
    private void replaceAttribute( Request realRequest, String name, Object value) {
	if( value == null )
	    realRequest.removeAttribute( name );
	else
	    realRequest.setAttribute( name, value );
    }

    private void invoke( Handler wr, Request req, Response resp )
	throws IOException, ServletException
    {
	try {
	    wr.service(req, resp);
	} catch( Exception ex ) {
	    if( ex instanceof ServletException )
		throw (ServletException)ex;
	    if( ex instanceof IOException )
		throw (IOException)ex;
	    throw new ServletException( ex );
	}
    }
}
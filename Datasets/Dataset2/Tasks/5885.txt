context.lookupServletByName(this.name);

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

import org.apache.tomcat.util.StringManager;
import java.io.*;
import java.util.*;
import javax.servlet.*;
import javax.servlet.http.*;

/**
 *
 *
 * @author James Duncan Davidson [duncan@eng.sun.com]
 * @author Jason Hunter [jch@eng.sun.com]
 * @author James Todd [gonzo@eng.sun.com]
 * @author Alex Cruikshank [alex@epitonic.com]
 */

public class RequestDispatcherImpl implements RequestDispatcher {

    private StringManager sm =
        StringManager.getManager(Constants.Package);
    private Context context;
    private Request lookupResult = null;
    private String name = null;
    private String urlPath;
    private String queryString;

    RequestDispatcherImpl(Context context) {
        this.context = context;
    }

    public void forward(ServletRequest request, ServletResponse response)
    throws ServletException, IOException {
	HttpServletRequestFacade reqFacade =
	    (HttpServletRequestFacade)request;
	HttpServletResponseFacade resFacade =
	    (HttpServletResponseFacade)response;
        Request realRequest = reqFacade.getRealRequest();
        Response realResponse = resFacade.getRealResponse();

	if (realResponse.isStarted()) {
            String msg = sm.getString("rdi.forward.ise");

	    throw new IllegalStateException(msg);
        }

	// Pre-pend the context name to give appearance of real request

	urlPath = context.getPath() + urlPath;

	// XXX Need to clean up - what's the diff between the lookupResult
	// ( internal-generated sub-request ) and ForwardedRequest  ?
	// I think ForwardedRequest can be removed, it's a particular case of
	// sub-request ( costin )
	ForwardedRequest fRequest =
	    new ForwardedRequest(realRequest, urlPath);

        // add new query string parameters to request
        // if names are duplicates, new values will be prepended to arrays
        reqFacade.getRealRequest().addQueryString(queryString);

        fRequest.setServletPath(this.lookupResult.getServletPath());
	fRequest.setPathInfo(this.lookupResult.getPathInfo());

	this.lookupResult.getWrapper().handleRequest(fRequest, resFacade);
    }

    public void include(ServletRequest request, ServletResponse response)
    throws ServletException, IOException {
	HttpServletRequest req = (HttpServletRequest)request;

	// XXX instead of setting the new parameters and back to original,
	// it should just use a sub-request ( by cloning the original ) 
	// That will simplify everything and make the code clear ( costin )
	
	// 
        // XXX
        // while this appears to work i believe the code
        // could be streamlined/normalized a bit.

	// if we are in a chained include, then we'll store the attributes
	// from the last round so that we've got them for the next round

	String request_uri =
            (String)req.getAttribute(Constants.Attribute.RequestURI);
	String servlet_path =
            (String)req.getAttribute(Constants.Attribute.ServletPath);
	String path_info =
            (String)req.getAttribute(Constants.Attribute.PathInfo);
	String query_string =
	    (String)req.getAttribute(Constants.Attribute.QueryString);

	HttpServletRequestFacade reqFacade =
	    (HttpServletRequestFacade)request;
	HttpServletResponseFacade resFacade =
	    (HttpServletResponseFacade)response;
        Request realRequest = reqFacade.getRealRequest();
	Response realResponse = resFacade.getRealResponse();
        String originalQueryString = realRequest.getQueryString();
        Hashtable originalParameters = realRequest.getParametersCopy();


	// XXX
	// not sure why we're pre-pending context.getPath() here
	//req.setAttribute(Constants.Attribute.RequestURI,
        //    context.getPath() + urlPath);

        // XXX
        // added the "check for null" to get the named dispatcher
        // stuff working ... this might break something else

        if (urlPath != null) {
	    req.setAttribute(Constants.Attribute.RequestURI,
                urlPath);
        }

	if (lookupResult.getServletPath() != null) {
	    req.setAttribute(Constants.Attribute.ServletPath,
                lookupResult.getServletPath());
	}

	if (lookupResult.getPathInfo() != null) {
	    req.setAttribute(Constants.Attribute.PathInfo,
                lookupResult.getPathInfo());
	}

        // add new query string parameters to request
        // if names are duplicates, new values will be prepended to arrays
        reqFacade.getRealRequest().addQueryString( this.queryString );

        if (reqFacade.getRealRequest().getQueryString() != null) {
	    req.setAttribute(Constants.Attribute.QueryString,
                reqFacade.getRealRequest().getQueryString());
        }

	IncludedResponse iResponse = new IncludedResponse(realResponse);

	lookupResult.getWrapper().handleRequest(reqFacade, iResponse);

        // revert the parameters and query string to its original value
        reqFacade.getRealRequest().setParameters(originalParameters);
        reqFacade.getRealRequest().replaceQueryString(originalQueryString);

	if (request_uri != null) {
	    req.setAttribute(Constants.Attribute.RequestURI, request_uri);
	} else {
	    reqFacade.removeAttribute(Constants.Attribute.RequestURI);
	}

	if (servlet_path != null) {
	    req.setAttribute(Constants.Attribute.ServletPath,
                servlet_path);
	} else {
	    reqFacade.removeAttribute(Constants.Attribute.ServletPath);
	}

	if (path_info != null) {
	    req.setAttribute(Constants.Attribute.PathInfo, path_info);
	} else {
	    reqFacade.removeAttribute(Constants.Attribute.PathInfo);
	}

	if (query_string != null) {
	    req.setAttribute(Constants.Attribute.QueryString,
                query_string);
	} else {
	    reqFacade.removeAttribute(Constants.Attribute.QueryString);
	}
    }

    void setName(String name) {
        this.name = name;
	this.lookupResult =
	    context.getContainer().lookupServletByName(this.name);
    }

    void setPath(String urlPath) {
	int i = urlPath.indexOf("?");

	if (i > -1) {
	    try {
		this.queryString =
                    urlPath.substring(i + 1, urlPath.length());
	    } catch (Exception e) {
	    }

	    urlPath = urlPath.substring(0, i);
	}

	this.urlPath = urlPath;

	this.lookupResult = new Request();
	lookupResult.setLookupPath( this.urlPath );
	lookupResult.setContext( context );
	context.getContextManager().internalRequestParsing(lookupResult);
    }

    boolean isValid() {
        return (this.lookupResult != null);
    }
}
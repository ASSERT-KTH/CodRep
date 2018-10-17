public static final String TOMCAT_VERSION = "3.1 Beta";

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

/**
 *
 * @author James Todd [gonzo@eng.sun.com]
 */

public class Constants {
    public static final String TOMCAT_NAME = "Tomcat Web Server";
    public static final String TOMCAT_VERSION = "3.1M2";

    public static final String JSP_NAME = "JSP";
    public static final String JSP_VERSION = "1.1";
	
    public static final String SERVLET_NAME = "Servlet";
    public static final int SERVLET_MAJOR = 2;
    public static final int SERVLET_MINOR = 2;

    public static final String INVOKER_SERVLET_NAME = "invoker";
    public static final String DEFAULT_SERVLET_NAME = "default";

    public static final String ATTRIB_WORKDIR1 = "sun.servlet.workdir";
    public static final String ATTRIB_WORKDIR = "javax.servlet.context.tempdir";

    public static final String SESSION_COOKIE_NAME = "JSESSIONID";
    public static final String SESSION_PARAMETER_NAME = "jsessionid";
    
    public static final String Package = "org.apache.tomcat.core";
    public static final int RequestURIMatchRecursion = 5;
    public static final String WORK_DIR = "work";

    public static final String LOCALE_DEFAULT="en";
    
    public static final String ATTRIBUTE_RequestURI =
	"javax.servlet.include.request_uri";
    public static final String ATTRIBUTE_ServletPath =
	"javax.servlet.include.servlet_path";
    public static final String ATTRIBUTE_PathInfo =
	"javax.servlet.include.path_info";
    public static final String ATTRIBUTE_QueryString =
	"javax.servlet.include.query_string";
    public static final String ATTRIBUTE_Dispatch =
	"javax.servlet.dispatch.request_uri";
    public static final String ATTRIBUTE_ERROR_EXCEPTION_TYPE =
	"javax.servlet.error.exception_type";
    public static final String ATTRIBUTE_ERROR_MESSAGE =
	"javax.servlet.error.message";
    public static final String ATTRIBUTE_RESOLVED_SERVLET =
	"org.apache.tomcat.servlet.resolved";
    
    public static final String WEB_XML_PublicId =
	"-//Sun Microsystems, Inc.//DTD Web Application 2.2//EN";
    public static final String WEB_XML_Resource =
	"/org/apache/tomcat/deployment/web.dtd";

    public static final String HTML = "text/html";

    public static final String DEFAULT_CONTENT_TYPE = "text/plain";
    public static final String DEFAULT_CHAR_ENCODING = "8859_1";


    // deprecated
    public static final String[] MASKED_DIR = {
	"META-INF","WEB-INF"
    };

}
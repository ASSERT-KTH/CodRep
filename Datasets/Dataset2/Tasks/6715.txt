public static final String Version = "1.0R1";

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

    public static final String Package = "org.apache.tomcat.core";
    public static final int RequestURIMatchRecursion = 5;
    public static final String WorkDir = "work";

    public static class Context {
        public static final String WebInfDir = "WEB-INF";
        public static final String WARInfDir = "META-INF";
        public static final String ConfigFile = WebInfDir + "/web.xml";
        public static final String ServletDir = WebInfDir + "/classes";
        public static final String LibDir = WebInfDir + "/lib";
        public static final String WARExpandDir = "docBase";

        public static final String[] MASKED_DIR = {
            WebInfDir,
            WARInfDir
        };

        public static String[] CLASS_PATHS = {
            ServletDir
        };

        public static String[] LIB_PATHS = {
            LibDir
        };

        public static final String EngineHeader =
            Tomcat.Name + "/" + Tomcat.Version + " (" + JSP.Name + " " +
	    JSP.Version + "; " + Servlet.Name + " " + Servlet.Version;

        public static class Servlet {
            public static final String Name = "Servlet";
	    public static final String Version = "2.2";
            public static final int MajorVersion = 2;
            public static final int MinorVersion = 2;
	}

        public static class JSP {
	    public static final String Name = "JSP";
	    public static final String Version = "1.1";
	}

        public static class Tomcat {
            /**
             * Name of the Engine. If you change this string, ALSO
             * CHANGE the string used in: 
             *
             * org.apache.jasper.runtime.ServletEngine.getServletEngine()
             *                                             - akv
             *
             */
	    public static final String Name = "Tomcat Web Server";
	    public static final String Version = "2.2";
	}

        public static class Attribute {
	    public static class WorkDir {
	        public static final String Name = "sun.servlet.workdir";
	    }
	}

        public static class Default {
	    public static final String Name = "default";
	    public static final String Path = "";
	}
    }

    public static class Property {
        public static final String Name = "core.properties";
        public static final String EngineHeader = "engine.header";
        public static final String MimeType = "mimeType";
    }

    public static class Cookie {
        public static final String SESSION_COOKIE_NAME = "JSESSIONID";
    }

    public static class Servlet {
        public static class Default {
	    public static final String Name = "default";
	    public static final String Class =
	        "org.apache.tomcat.core.DefaultServlet";
	    public static final String Map = "";
	}

        public static class Invoker {
	    public static final String Name = "invoker";
	    public static final String Class =
	        "org.apache.tomcat.core.InvokerServlet";
	    public static final String Map = "/servlet";
	}

        public static class NoInvoker {
	    public static final String Name = Invoker.Name;
	    public static final String Class =
	        "org.apache.tomcat.core.NoInvokerServlet";
	    public static final String Map = Invoker.Map;
	}
    }

    public static class JSP {
        public static final String NAME = "jsp";
	public static final String CLASSNAME = "org.apache.jasper.runtime.JspServlet";
     
        public static class Directive {
            public static class Compile {
                public static final String Name = "jsp_precompile";
                public static final String Value = "true";
            }
        }
    }

    public static class Attribute {
        public static final String WorkDirectory =
            "javax.servlet.context.tempdir";
        public static final String RequestURI =
            "javax.servlet.include.request_uri";
        public static final String ServletPath =
            "javax.servlet.include.servlet_path";
        public static final String PathInfo =
            "javax.servlet.include.path_info";
        public static final String QueryString =
            "javax.servlet.include.query_string";
        public static final String Dispatch =
            "javax.servlet.dispatch.request_uri";
        public static final String ERROR_EXCEPTION_TYPE =
            "javax.servlet.error.exception_type";
        public static final String ERROR_MESSAGE =
            "javax.servlet.error.message";
        public static final String RESOLVED_SERVLET =
            "org.apache.tomcat.servlet.resolved";
    }

    public static class Locale {
        public static final String Default = "en";
    }

    public static class ContentType {
        public static final String Default = "text/plain";
        public static final String HTML = "text/html";
        public static final String Plain = Default;
    }

    public static class CharacterEncoding {
        public static final String Default = "8859_1";
    }

    public static class Header {
        public static final String AcceptLanguage = "Accept-Language";
    }
 
    public static class Request {
        public static final String HTTP = "http";
        public static final String HTTPS = "https";
        public static final String FILE = "file";
        public static final String WAR = "war";
        public static final String JAR = "jar";
    }
}
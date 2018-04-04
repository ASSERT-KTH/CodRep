Log.FATAL);

/*
 *
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
 */ 





package org.apache.jasper;

import javax.servlet.ServletContext;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;

import org.apache.jasper.compiler.JspReader;
import org.apache.jasper.compiler.ServletWriter;
//import org.apache.jasper.runtime.JspLoader;
import org.apache.jasper.servlet.JasperLoader;
import org.apache.jasper.compiler.TagLibraries;

import org.apache.jasper.compiler.Compiler;
import org.apache.jasper.compiler.JspCompiler;
import org.apache.jasper.compiler.SunJavaCompiler;
import org.apache.jasper.compiler.JavaCompiler;

import org.apache.tomcat.util.log.*;
/**
 * A place holder for various things that are used through out the JSP
 * engine. This is a per-request/per-context data structure. Some of
 * the instance variables are set at different points.
 *
 * JspLoader creates this object and passes this off to the "compiler"
 * subsystem, which then initializes the rest of the variables. 
 *
 * @author Anil K. Vijendran
 * @author Harish Prabandham
 */
public class JspEngineContext implements JspCompilationContext {
    JspReader reader;
    ServletWriter writer;
    ServletContext context;
    JasperLoader loader;
    String classpath; // for compiling JSPs.
    boolean isErrPage;
    String jspFile;
    String servletClassName;
    String servletPackageName;
    String servletJavaFileName;
    String contentType;
    Options options;
    HttpServletRequest req;
    HttpServletResponse res;
    

    public JspEngineContext(JasperLoader loader, String classpath, 
                            ServletContext context, String jspFile, 
                            boolean isErrPage, Options options, 
                            HttpServletRequest req, HttpServletResponse res) 
    {
        this.loader = loader;
        this.classpath = classpath;
        this.context = context;
        this.jspFile = jspFile;
        this.isErrPage = isErrPage;
        this.options = options;
        this.req = req;
        this.res = res;
    }

    /**
     * Get the http request we are servicing now...
     */
    public HttpServletRequest getRequest() {
        return req;
    }
    

    /**
     * Get the http response we are using now...
     */
    public HttpServletResponse getResponse() {
        return res;
    }

    /**
     * The classpath that is passed off to the Java compiler. 
     */
    public String getClassPath() {
        return loader.getClassPath() + classpath;
    }
    
    /**
     * Get the input reader for the JSP text. 
     */
    public JspReader getReader() { 
        return reader;
    }
    
    /**
     * Where is the servlet being generated?
     */
    public ServletWriter getWriter() {
        return writer;
    }
    
    /**
     * Get the ServletContext for the JSP we're processing now. 
     */
    public ServletContext getServletContext() {
        return context;
    }
    
    /**
     * What class loader to use for loading classes while compiling
     * this JSP? I don't think this is used right now -- akv. 
     */
    public ClassLoader getClassLoader() {
        return loader;
    }

    public void addJar( String jar ) throws IOException  {
	loader.addJar( jar );
    }

    /**
     * Are we processing something that has been declared as an
     * errorpage? 
     */
    public boolean isErrorPage() {
        return isErrPage;
    }
    
    /**
     * What is the scratch directory we are generating code into?
     * FIXME: In some places this is called scratchDir and in some
     * other places it is called outputDir.
     */
    public String getOutputDir() {
        return options.getScratchDir().toString();
    }
    
    /**
     * Path of the JSP URI. Note that this is not a file name. This is
     * the context rooted URI of the JSP file. 
     */
    public String getJspFile() {
        return jspFile;
    }
    
    /**
     * Just the class name (does not include package name) of the
     * generated class. 
     */
    public String getServletClassName() {
        return servletClassName;
    }
    
    /**
     * The package name into which the servlet class is generated. 
     */
    public String getServletPackageName() {
        return servletPackageName;
    }

    /**
     * Utility method to get the full class name from the package and
     * class name. 
     */
    public final String getFullClassName() {
        if (servletPackageName == null)
            return servletClassName;
        return servletPackageName + "." + servletClassName;
    }

    /**
     * Full path name of the Java file into which the servlet is being
     * generated. 
     */
    public String getServletJavaFileName() {
        return servletJavaFileName;
    }

    /**
     * Are we keeping generated code around?
     */
    public boolean keepGenerated() {
        return options.getKeepGenerated();
    }

    /**
     * What's the content type of this JSP? Content type includes
     * content type and encoding. 
     */
    public String getContentType() {
        return contentType;
    }

    /**
     * Get hold of the Options object for this context. 
     */
    public Options getOptions() {
        return options;
    }

    public void setContentType(String contentType) {
        this.contentType = contentType;
    }

    public void setReader(JspReader reader) {
        this.reader = reader;
    }
    
    public void setWriter(ServletWriter writer) {
        this.writer = writer;
    }
    
    public void setServletClassName(String servletClassName) {
        this.servletClassName = servletClassName;
    }
    
    public void setServletPackageName(String servletPackageName) {
        this.servletPackageName = servletPackageName;
    }
    
    public void setServletJavaFileName(String servletJavaFileName) {
        this.servletJavaFileName = servletJavaFileName;
    }
    
    public void setErrorPage(boolean isErrPage) {
        this.isErrPage = isErrPage;
    }

    /**
     * Create a "Compiler" object based on some init param data. If	
     * jspCompilerPlugin is not specified or is not available, the 
     * SunJavaCompiler is used.
     */
    public Compiler createCompiler() throws JasperException {
	String compilerPath = options.getJspCompilerPath();
	Class jspCompilerPlugin = options.getJspCompilerPlugin();
        JavaCompiler javac;

	if (jspCompilerPlugin != null) {
            try {
                javac = (JavaCompiler) jspCompilerPlugin.newInstance();
            } catch (Exception ex) {
		Constants.message("jsp.warning.compiler.class.cantcreate",
				  new Object[] { jspCompilerPlugin, ex }, 
				  Logger.FATAL);
                javac = new SunJavaCompiler();
	    }
	} else {
            javac = new SunJavaCompiler();
	}

        if (compilerPath != null)
            javac.setCompilerPath(compilerPath);

        Compiler jspCompiler = new JspCompiler(this);
	jspCompiler.setJavaCompiler(javac);
         
        return jspCompiler;
    }
    
    /** 
     * Get the full value of a URI relative to this compilations context
     */
    public String resolveRelativeUri(String uri)
    {
        if (uri.charAt(0) == '/')
        {
            return uri;
        }
        else
        {
            String actURI =  req.getServletPath();
            String baseURI = actURI.substring(0, actURI.lastIndexOf('/'));
            return baseURI + '/' + uri;
        }
    }    

    /**
     * Gets a resource as a stream, relative to the meanings of this
     * context's implementation.
     *@returns a null if the resource cannot be found or represented 
     *         as an InputStream.
     */
    public java.io.InputStream getResourceAsStream(String res)
    {
        return context.getResourceAsStream(res);
    }

    /** 
     * Gets the actual path of a URI relative to the context of
     * the compilation.
     */
    public String getRealPath(String path)
    {
        if (context != null)
        {
            return context.getRealPath(path);
        }
        else
        {
            return path;
        }
    }

   
}
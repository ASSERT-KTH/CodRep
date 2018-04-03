return 500;

/*
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
package org.apache.tomcat.facade;

import javax.servlet.*;
import javax.servlet.http.*;

import javax.servlet.jsp.HttpJspPage;
import javax.servlet.jsp.JspFactory;

import java.util.*;
import java.io.*;
import java.net.*;

import org.apache.tomcat.util.log.*;
import org.apache.tomcat.util.*;
import org.apache.tomcat.util.depend.*;

import org.apache.jasper.*;
import org.apache.jasper.Constants;
import org.apache.jasper.runtime.*;
import org.apache.jasper.compiler.*;
import org.apache.jasper.compiler.Compiler;
import org.apache.tomcat.core.*;
import org.apache.tomcat.facade.*;

/**
 * Plug in the JSP engine (a.k.a Jasper)!
 * Tomcat uses a "built-in" mapping for jsps ( *.jsp -> jsp ). "jsp"
 * can be either a real servlet (JspServlet) that compiles the jsp
 * and include the resource, or we can "intercept" and do the
 * compilation and mapping in requestMap stage.
 *
 * JspInterceptor will be invoked once per jsp, and will add an exact
 * mapping - all further invocation are identical with servlet invocations
 * with direct maps, with no extra overhead.
 *
 * Future - better abstraction for jsp->java converter ( jasper ), better
 * abstraction for java->class, plugin other jsp implementations,
 * better scalability.
 *
 * @author Anil K. Vijendran
 * @author Harish Prabandham
 * @author Costin Manolache
 */
public class JspInterceptor extends BaseInterceptor {
    static final String JIKES="org.apache.jasper.compiler.JikesJavaCompiler";
    static final String JSP_SERVLET="org.apache.jasper.servlet.JspServlet";
    
    Properties args=new Properties(); // args for jasper
    boolean useJspServlet=false; 
    String jspServletCN=JSP_SERVLET;
    
    // -------------------- Jasper options --------------------
    // Options that affect jasper functionality. Will be set on
    // JspServlet ( if useJspServlet="true" ) or TomcatOptions.
    // IMPORTANT: periodically test for new jasper options
    
    /**
     * Are we keeping generated code around?
     */
    public void setKeepGenerated( String s ) {
	args.put( "keepgenerated", s );
    }

    /**
     * Are we supporting large files?
     */
    public void setLargeFile( String s ) {
	args.put( "largefile", s );
    }

    /**
     * Are we supporting HTML mapped servlets?
     */
    public void setMappedFile( String s ) {
	args.put( "mappedfile", s );
    }

    /**
     * Should errors be sent to client or thrown into stderr?
     */
    public void setSendErrToClient( String s ) {
	args.put( "sendErrToClient", s );
    }

    /**
     * Class ID for use in the plugin tag when the browser is IE. 
     */
    public void setIEClassId( String s ) {
	args.put( "ieClassId", s );
    }

    /**
     * What classpath should I use while compiling the servlets
     * generated from JSP files?
     */
    public void setClassPath( String s ) {
	args.put( "classpath", s );
    }

    /**
     * What is my scratch dir?
     */
    public void setScratchdir( String s ) {
	args.put( "scratchdir", s );
    }

    /**
     * Path of the compiler to use for compiling JSP pages.
     */
    public void setJspCompilerPath( String s ) {
	args.put( "jspCompilerPath", s );
    }

    /**
     * What compiler plugin should I use to compile the servlets
     * generated from JSP files?
     * @deprecated Use setJavaCompiler instead
     */
    public void setJspCompilerPlugin( String s ) {
	args.put( "jspCompilerPlugin", s );
    }

    /** Include debug information in generated classes
     */
    public void setClassDebugInfo( String s ) {
	args.put("classDebugInfo", s );
    }
    
    public void setProperty( String n, String v ) {
	args.put( n, v );
    }
    // -------------------- JspInterceptor properties --------------------

    /** Use the old JspServlet to execute Jsps, instead of the
	new code. Note that init() never worked (AFAIK) and it'll
	be slower - but given the stability of JspServlet it may
	be a safe option. This will significantly slow down jsps.
	Default is false.
    */
    public void setUseJspServlet( boolean b ) {
	useJspServlet=b;
    }

    /** Specify the implementation class of the jsp servlet.
     */
    public void setJspServlet( String  s ) {
	jspServletCN=s;
    }

    /**
     * What compiler should I use to compile the servlets
     * generated from JSP files? Default is "javac" ( you can use
     * "jikes" as a shortcut ).
     */
    public void setJavaCompiler( String type ) {
	if( "jikes".equals( type ) )
	    type=JIKES;

	args.put( "jspCompilerPlugin", type );
    }

    // -------------------- Hooks --------------------

    /**
     * Jasper-specific initializations, add work dir to classpath,
     */
    public void addContext(ContextManager cm, Context ctx)
	throws TomcatException 
    {
	JspFactory.setDefaultFactory(new JspFactoryImpl());

	// jspServlet uses it's own loader. We need to add workdir
	// to the context classpath to use URLLoader and normal
	// operation
	// XXX alternative: use WEB-INF/classes for generated files 
	if( ! useJspServlet ) {
	    try {
		// Note: URLClassLoader in JDK1.2.2 doesn't work with file URLs
		// that contain '\' characters.  Insure only '/' is used.
		// jspServlet uses it's own mechanism
		URL url=new URL( "file", null,
		 ctx.getWorkDir().getAbsolutePath().replace('\\','/') + "/");
		ctx.addClassPath( url );
		if( debug > 9 ) log( "Added to classpath: " + url );
	    } catch( MalformedURLException ex ) {
	    }
	}
    }

    /** Do the needed initialization if jspServlet is used.
     *  It must be called after Web.xml is read ( WebXmlReader ).
     */
    public void contextInit(Context ctx)
	throws TomcatException
    {
	if( useJspServlet ) {
	    // prepare jsp servlet. 
	    Handler jasper=ctx.getServletByName( "jsp" );
	    if ( debug>10) log( "Got jasper servlet " + jasper );

	    ServletHandler jspServlet=(ServletHandler)jasper;
	    if( jspServlet.getServletClassName() == null ) {
		log( "Jsp already defined in web.xml " +
		     jspServlet.getServletClassName() );
		return;
	    }
	    if( debug>-1)
		log( "jspServlet=" +  jspServlet.getServletClassName());
	    Enumeration enum=args.keys();
	    while( enum.hasMoreElements() ) {
		String s=(String)enum.nextElement();
		String v=(String)args.get(s);
		if( debug>0 ) log( "Setting " + s + "=" + v );
		jspServlet.getServletInfo().addInitParam(s, v );
	    }
	    
	    if( debug > 0 ) {
		//enable jasperServlet logging
		log( "Seetting debug on jsp servlet");
		org.apache.jasper.Constants.jasperLog=
		    org.apache.tomcat.util.log.Logger.getDefaultLogger();
		org.apache.jasper.Constants.jasperLog.
		    setVerbosityLevel("debug");
	    }

	    jspServlet.setServletClassName(jspServletCN);
	}
    }

    /** Set the HttpJspBase classloader before init,
     *  as required by Jasper
     */
    public void preServletInit( Context ctx, Handler sw )
	throws TomcatException
    {
	if( ! (sw instanceof ServletHandler) )
	    return;
	try {
	    // requires that everything is compiled
	    Servlet theServlet = ((ServletHandler)sw).getServlet();
	    if (theServlet instanceof HttpJspBase)  {
		if( debug > 9 )
		    log( "PreServletInit: HttpJspBase.setParentClassLoader" +
			 sw );
		HttpJspBase h = (HttpJspBase) theServlet;
		h.setClassLoader(ctx.getClassLoader());
	    }
	} catch(Exception ex ) {
	    throw new TomcatException( ex );
	}
    }

    //-------------------- Main hook - compile the jsp file if needed
    
    /** Detect if the request is for a JSP page and if it is find
	the associated servlet name and compile if needed.

	That insures that init() will take place on the equivalent
	servlet - and behave exactly like a servlet.

	A request is for a JSP if:
	- the handler is a ServletHandler ( i.e. defined in web.xml
	or dynamically loaded servlet ) and it has a "path" instead of
	class name
	- the handler has a special name "jsp". That means a *.jsp -> jsp
	needs to be defined. This is a tomcat-specific mechanism ( not
	part of the standard ) and allow users to associate other extensions
	with JSP by using the "fictious" jsp handler.

	An (cleaner?) alternative for mapping other extensions would be
	to set them on JspInterceptor.
    */
    public int requestMap( Request req ) {
	if( useJspServlet ) {
	    // no further processing - jspServlet will take care
	    // of the processing as before ( all processing
	    // will happen in the handle() pipeline.
	    return 0;
	}

	Handler wrapper=req.getHandler();

	if( wrapper==null )
	    return 0;

	// It's not a jsp if it's not "*.jsp" mapped or a servlet
	if( (! "jsp".equals( wrapper.getName())) &&
	    (! (wrapper instanceof ServletHandler)) ) {
	    return 0;
	}

	ServletHandler handler=null;
	String jspFile=null;

	// There are 2 cases: extension mapped and exact map with
	// a <servlet> with file-name declaration

	// note that this code is called only the first time
	// the jsp page is called - all other calls will treat the jsp
	// as a regular servlet, nothing is special except the initial
	// processing.

	// XXX deal with jsp_compile
	
	if( "jsp".equals( wrapper.getName())) {
	    // if it's an extension mapped file, construct and map a handler
	    jspFile=req.servletPath().toString();
	    
	    // extension mapped jsp - define a new handler,
	    // add the exact mapping to avoid future overhead
	    handler= mapJspPage( req.getContext(), jspFile );
	    req.setHandler( handler );
	} else if( wrapper instanceof ServletHandler) {
	    // if it's a simple servlet, we don't care about it
	    handler=(ServletHandler)wrapper;
	    jspFile=handler.getServletInfo().getJspFile();
	    if( jspFile==null )
		return 0; // not a jsp
	}

	// Each .jsp file is compiled to a servlet, and will
	// have a dependency to check if it's expired
	Dependency dep= handler.getServletInfo().getDependency();
	if( dep!=null && ! dep.isExpired() ) {
	    // if the jspfile is older than the class - we're ok
	    // this happens if the .jsp file was compiled in a previous
	    // run of tomcat.
	    return 0;
	}

	// we need to compile... ( or find previous .class )
	JasperLiaison liasion=new JasperLiaison(getLog(), debug);
	liasion.processJspFile(req, jspFile, handler, args);
	return 0;
    }

    // -------------------- Utils --------------------
    
    private static final String SERVLET_NAME_PREFIX="TOMCAT/JSP";
    
    /** Add an exact map that will avoid *.jsp mapping and intermediate
     *  steps. It's equivalent with declaring
     *  <servlet-name>tomcat.jsp.[uri]</>
     *  <servlet-mapping><servlet-name>tomcat.jsp.[uri]</>
     *                   <url-pattern>[uri]</></>
     */
    private ServletHandler mapJspPage( Context ctx, String uri)
    {
	String servletName= SERVLET_NAME_PREFIX + uri;

	if( debug>0)
	    log( "mapJspPage " + ctx + " " + " " + servletName + " " +  uri  );

	Handler h=ctx.getServletByName( servletName );
	if( h!= null ) {
	    log( "Name already exists " + servletName +
		 " while mapping " + uri);
	    return null; // exception ?
	}
	
	ServletHandler wrapper=new ServletHandler();
	wrapper.setModule( this );
	wrapper.setContext(ctx);
	wrapper.setName(servletName);
	wrapper.getServletInfo().setJspFile( uri );
	
	// add the mapping - it's a "invoker" map ( i.e. it
	// can be removed to keep memory under control.
	// The memory usage is smaller than JspSerlvet anyway, but
	// can be further improved.
	try {
	    ctx.addServlet( wrapper );
	    ctx.addServletMapping( uri ,
				   servletName );
	    if( debug > 0 )
		log( "Added mapping " + uri + " path=" + servletName );
	} catch( TomcatException ex ) {
	    log("mapJspPage: ctx=" + ctx +
		", servletName=" + servletName, ex);
	    return null;
	}
	return wrapper;
    }

}

// -------------------- The main Jasper Liaison --------------------

final class JasperLiaison {
    Log log;
    final int debug;
    
    JasperLiaison( Log log, int debug ) {
	this.log=log;
	this.debug=debug;
    }
    
    /** Generate mangled names, check for previous versions,
     *  generate the .java file, compile it - all the expensive
     *  operations. This happens only once ( or when the jsp file
     *  changes ). 
     */
    int processJspFile(Request req, String jspFile,
		       ServletHandler handler, Properties args)
    {
	// ---------- Expensive part - compile and load
	
	// If dep==null, the handler was never used - we need
	// to either compile it or find the previous compiled version
	// If dep.isExpired() we need to recompile.

	if( debug > 10 ) log.log( "Before compile sync  " + jspFile );
	synchronized( handler ) {
	    
	    // double check - maybe another thread did that for us
	    Dependency dep= handler.getServletInfo().getDependency();
	    if( dep!=null && ! dep.isExpired() ) {
		// if the jspfile is older than the class - we're ok
		return 0;
	    }

	    Context ctx=req.getContext();
	    
	    // Mangle the names - expensive operation, but nothing
	    // compared with a compilation :-)
	    JasperMangler mangler=
		new JasperMangler(ctx.getWorkDir().getAbsolutePath(),
			       ctx.getAbsolutePath(),
			       jspFile );

	    // register the handler as dependend of the jspfile 
	    if( dep==null ) {
		dep=setDependency( ctx, mangler, handler );
		// update the servlet class name
		handler.setServletClassName( mangler.getServletClassName() );

		// check again - maybe we just found a compiled class from
		// a previous run
		if( ! dep.isExpired() )
		    return 0;
	    }

	    //	    if( debug > 3) 
	    ctx.log( "Compiling: " + jspFile + " to " +
		     mangler.getServletClassName());
	    
	    //XXX old servlet -  destroy(); 
	    
	    // jump version number - the file needs to be recompiled
	    // reset the handler error, un-initialize the servlet
	    handler.setErrorException( null );
	    handler.setState( Handler.STATE_ADDED );
	    
	    // Move to the next class name
	    mangler.nextVersion();

	    // record time of attempted translate-and-compile
	    // if the compilation fails, we'll not try again
	    // until the jsp file changes
	    dep.setLastModified( System.currentTimeMillis() );

	    // Update the class name in wrapper
	    if( debug> 1 )
		log.log( "Update class Name " + mangler.getServletClassName());
	    handler.setServletClassName( mangler.getServletClassName() );

	    
	    try {
		Options options=new JasperOptionsImpl(args); 
		JspCompilationContext ctxt=createCompilationContext(req,
								    options,
								    mangler);
		JavaCompiler javaC=createJavaCompiler( options );

		jsp2java( mangler, ctxt );
		javac( javaC, ctxt, mangler );
	    
		if(debug>0)log.log( "Generated " +
				    mangler.getClassFileName() );
	    } catch( Exception ex ) {
		if( ctx!=null )
		    ctx.log("compile error: req="+req, ex);
		else
		    log.log("compile error: req="+req, ex);
		handler.setErrorException(ex);
		handler.setState(Handler.STATE_DISABLED);
		// until the jsp cahnges, when it'll be enabled again
		return 0;
	    }

	    dep.setExpired( false );
	    
	}

	return 0;
    }

    /** Convert the .jsp file to a java file, then compile it to class
     */
    void jsp2java(JasperMangler mangler,  JspCompilationContext ctxt)
	throws Exception
    {
	if( debug > 0 ) log.log( "Generating " + mangler.getJavaFileName());
	// make sure we have the directories
	String javaFileName=mangler.getJavaFileName();
	
	File javaFile=new File(javaFileName);
	
	// make sure the directory is created
	new File( javaFile.getParent()).mkdirs();
	
	Compiler compiler=new Compiler(ctxt);
	compiler.setMangler( mangler );
	// we will compile ourself
	compiler.setJavaCompiler( null );
	
	
	synchronized ( mangler ) {
	    compiler.compile();
	}
	if( debug > 0 ) {
	    File f = new File( mangler.getJavaFileName());
	    log.log( "Created file : " + f +  " " + f.lastModified());
	    
	}
    }
    
    String javaEncoding = "UTF8";           // perhaps debatable?
    static String sep = System.getProperty("path.separator");

    /** Compile a java to class. This should be moved to util, togheter
	with JavaCompiler - it's a general purpose code, no need to
	keep it part of jasper
    */
    void javac(JavaCompiler javac, JspCompilationContext ctxt,
	       Mangler mangler)
	throws JasperException
    {

        javac.setEncoding(javaEncoding);
	String cp=System.getProperty("java.class.path")+ sep + 
	    ctxt.getClassPath() + sep + ctxt.getOutputDir();
        javac.setClasspath( cp );
	if( debug>5) log.log( "ClassPath " + cp);
	
	ByteArrayOutputStream out = new ByteArrayOutputStream (256);
	javac.setOutputDir(ctxt.getOutputDir());
        javac.setMsgOutput(out);

	String javaFileName = mangler.getJavaFileName();
	if( debug>0 ) log.log( "Compiling java file " + javaFileName);
	/**
         * Execute the compiler
         */
        boolean status = javac.compile(javaFileName);

        if (!ctxt.keepGenerated()) {
            File javaFile = new File(javaFileName);
            javaFile.delete();
        }
    
        if (status == false) {
            String msg = out.toString ();
            throw new JasperException("Unable to compile "
                                      + msg);
        }
	if( debug > 0 ) log.log("Compiled ok");
    }

    /** tool for customizing javac.
     */
    public JavaCompiler createJavaCompiler(Options options)
	throws JasperException
    {
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

	javac.setClassDebugInfo(options.getClassDebugInfo());

	return javac;
    }

    private String computeClassPath(Context ctx) {
	URL classP[]=ctx.getClassPath();
	String separator = System.getProperty("path.separator", ":");
        String cpath = "";
        for(int i=0; i< classP.length; i++ ) {
            URL cp = classP[i];
            File f = new File( cp.getFile());
            if (cpath.length()>0) cpath += separator;
            cpath += f;
        }
	return cpath;
    }

    private JspCompilationContext createCompilationContext( Request req,
							    Options opt,
							    Mangler mangler)
    {
	JasperEngineContext ctxt = new JasperEngineContext();
	ctxt.setServletClassName( mangler.getClassName());
	ctxt.setJspFile( req.servletPath().toString());
	ctxt.setClassPath( computeClassPath( req.getContext()) );
	ctxt.setServletContext( req.getContext().getFacade());
	ctxt.setOptions( opt );
	ctxt.setClassLoader( req.getContext().getClassLoader());
	ctxt.setOutputDir(req.getContext().getWorkDir().getAbsolutePath());
	return ctxt;
    }
    
    // Add an "expire check" to the generated servlet.
    private Dependency setDependency( Context ctx, JasperMangler mangler,
				      ServletHandler handler )
    {
	ServletInfo info=handler.getServletInfo();
	// create a lastModified checker.
	if( debug>0) log.log("Registering dependency for " + handler );
	Dependency dep=new Dependency();
	dep.setOrigin( new File(mangler.getJspFilePath()) );
	dep.setTarget( handler );
	dep.setLocal( true );
	File f=new File( mangler.getClassFileName() );
	if( mangler.getVersion() > 0 ) {
	    // it has a previous version
	    dep.setLastModified(f.lastModified());
	    // update the "expired" variable
	    dep.checkExpiry();
	} else {
	    dep.setLastModified( -1 );
	    dep.setExpired( true );
	}
	if( debug>0 )
	    log.log( "file = " + mangler.getClassFileName() + " " +
		     f.lastModified() );
	if( debug>0 )
	    log.log("origin = " + dep.getOrigin() + " " +
		    dep.getOrigin().lastModified());
	ctx.getDependManager().addDependency( dep );
	info.setDependency( dep );
	return dep;
    }
	

}
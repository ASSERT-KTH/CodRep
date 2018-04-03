wrapper.setServletClassName( classN );

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
package org.apache.tomcat.modules.facade22;

import javax.servlet.*;
import javax.servlet.http.*;

import javax.servlet.jsp.HttpJspPage;
import javax.servlet.jsp.JspFactory;

import java.util.*;
import java.io.*;
import java.net.*;

import org.apache.tomcat.util.log.*;
import org.apache.tomcat.util.*;

import org.apache.jasper.*;
import org.apache.jasper.Constants;
import org.apache.jasper.runtime.*;
import org.apache.jasper.compiler.*;
import org.apache.jasper.compiler.Compiler;
import org.apache.tomcat.core.*;
import org.apache.tomcat.facade.ServletWrapper;

/**
 * Plug in the JSP engine (a.k.a Jasper)! 
 *
 * @author Anil K. Vijendran
 * @author Harish Prabandham
 * @author Costin Manolache
 */
public class JspInterceptor extends BaseInterceptor {
    int jspInfoNOTE;
    TomcatOptions options=new TomcatOptions();

    static final String JIKES="org.apache.jasper.compiler.JikesJavaCompiler";
    
    public void setJavaCompiler( String type ) {
	// shortcut
	if( "jikes".equals( type ) )
	    type=JIKES;
	
	try {
	    options.jspCompilerPlugin=Class.forName(type);
	} catch(Exception ex ) {
	    ex.printStackTrace();
	}
    }

    public void engineInit(ContextManager cm )
	throws TomcatException
    {
	super.engineInit(cm);
	jspInfoNOTE=cm.getNoteId( ContextManager.HANDLER_NOTE,
				  "tomcat.jspInfoNote");
    }

    
    public void addContext(ContextManager cm, Context ctx)
	throws TomcatException 
    {
	JspFactory.setDefaultFactory(new JspFactoryImpl());
	try {
	    URL url=new URL( "file", null,
			     ctx.getWorkDir().getAbsolutePath() + "/");
	    ctx.addClassPath( url );
	    if( debug > 0 ) log( "Added to classpath: " + url );
	} catch( MalformedURLException ex ) {
	}
    }

    public void preServletInit( Context ctx, Handler sw )
	throws TomcatException
    {
	Servlet theServlet = ((ServletWrapper)sw).getServlet();
	if (theServlet instanceof HttpJspBase)  {
	    if( debug > 0 )
		log( "PreServletInit: HttpJspBase.setParentClassLoader" + sw );
	    HttpJspBase h = (HttpJspBase) theServlet;
	    h.setClassLoader(ctx.getClassLoader());
	}
    }

    public int requestMap( Request req ) {
	Handler wrapper=(Handler)req.getHandler();

	//	log( "Try: " + req );
	
	if( wrapper!=null && ! "jsp".equals( wrapper.getName())
	    && wrapper.getPath() == null)
	    return 0;

	// XXX jsp handler is still needed
	if( wrapper==null )
	    return 0;
	
	Context ctx= req.getContext();

	// If this Wrapper was already used, we have all the info
	JspInfo jspInfo=(JspInfo)wrapper.getNote( jspInfoNOTE );
	if( jspInfo == null ) {
	    if( debug > 0 ) log("New jsp page - no jspInfo ");
	    jspInfo=new JspInfo(req);
	    mapJspPage( req, jspInfo, jspInfo.uri, jspInfo.fullClassN);
	}

	if( debug > 3) {
	    log( "Check if source is up-to-date " +
		 jspInfo.jspSource + " " + 
		 jspInfo.jspSource.lastModified() + " "
		 + jspInfo.compileTime );
	}

	if( jspInfo.jspSource.lastModified() 
	    > jspInfo.compileTime ) {
	    //XXX 	    destroy();
	    
	    // jump version number - the file needs to
	    // be recompiled, and we don't want a reload
	    if( debug > 0 ) log( "Before sync block  " + jspInfo );
	    synchronized( jspInfo ) {
		//		if( debug>0 )
		if( jspInfo.jspSource.lastModified() 
		    > jspInfo.compileTime ) {
		    if( debug > 0 ) log( "Compiling " + jspInfo );
		
		    jspInfo.nextVersion();
		    compile( req, jspInfo );
		    mapJspPage( req , jspInfo, jspInfo.uri,
				jspInfo.fullClassN);
		}
	    } 
	}

	return 0;
    }

    /** Add an exact map that will avoid *.jsp mapping and intermediate
     *  steps
     */
    void mapJspPage( Request req, JspInfo jspInfo,
		     String servletName, String classN )
    {
	Context ctx=req.getContext();
	ServletWrapper wrapper=null;
	String servletPath=servletName;
	// add the mapping - it's a "invoker" map ( i.e. it
	// can be removed to keep memory under control.
	// The memory usage is smaller than JspSerlvet anyway, but
	// can be further improved.
	try {
	    wrapper=(ServletWrapper)ctx.getServletByName( servletName );
	    // We may want to replace the class and reset it if changed
	    
	    if( wrapper==null ) {
		wrapper=new ServletWrapper();
		wrapper.setContext(ctx);
		wrapper.setServletName(servletName);
		wrapper.setPath( servletPath );
		wrapper.setOrigin( Handler.ORIGIN_INVOKER );
		ctx.addServlet( wrapper );
		
		ctx.addServletMapping( servletPath ,
				       servletPath );
		if( debug > 0 )
		    log( "Added mapping " + servletPath +
			 " path=" + servletPath );
	    }
	    wrapper.setServletClass( classN );
	    wrapper.setNote( jspInfoNOTE, jspInfo );
	    // set initial exception on the servlet if one is present
	    if ( jspInfo.isExceptionPresent() ) {
		wrapper.setErrorException(jspInfo.getCompileException());
		wrapper.setExceptionPermanent(true);
	    }
	} catch( TomcatException ex ) {
	    log("mapJspPage: request=" + req + ", jspInfo=" + jspInfo + ", servletName=" + servletName + ", classN=" + classN, ex);
	    return ;
	}
	req.setHandler( wrapper );
	if( debug>0) log("Wrapper " + wrapper);
    }

    /** Convert the .jsp file to a java file, then compile it to class
     */
    void compile(Request req, JspInfo jspInfo ) {
	if( debug > 0 ) log( "Compiling " + jspInfo.realClassPath);
	try {
	    // make sure we have the directories
        File dir;
        if (jspInfo.pkgDir!=null)
    	    dir=new File( jspInfo.outputDir + "/" + jspInfo.pkgDir);
        else
    	    dir=new File( jspInfo.outputDir);
	    dir.mkdirs();
	    JspMangler mangler= new JspMangler(jspInfo);
	    JspEngineContext1 ctxt = new JspEngineContext1(req, mangler);
	    ctxt.setOptions( options );
	    
	    Compiler compiler=new Compiler(ctxt);
	    compiler.setMangler( mangler );
		
	    // we will compile ourself
	    compiler.setJavaCompiler( null );

	    // record time of attempted translate-and-compile
	    jspInfo.touch();

	    synchronized ( this ) {
		compiler.compile();
	    }
	    
	    javac( createJavaCompiler( options ), ctxt, mangler );
	    
	    if(debug>0)log( "Compiled to " + jspInfo.realClassPath );
	} catch( Exception ex ) {
	    log("compile: req="+req+", jspInfo=" + jspInfo, ex);
	    jspInfo.setCompileException(ex);
	}
    }
    
    String javaEncoding = "UTF8";           // perhaps debatable?
    static String sep = System.getProperty("path.separator");

    static String getClassPath( Context ctx ) {
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
    
    /** Compile a java to class. This should be moved to util, togheter
	with JavaCompiler - it's a general purpose code, no need to
	keep it part of jasper
    */
    public void javac(JavaCompiler javac, JspEngineContext1 ctxt,
		      Mangler mangler)
	throws JasperException
    {

        javac.setEncoding(javaEncoding);
	String cp=System.getProperty("java.class.path")+ sep + 
	    ctxt.getClassPath() + sep + ctxt.getOutputDir();
        javac.setClasspath( cp );
	if( debug>0) log( "ClassPath " + cp);
	
	ByteArrayOutputStream out = new ByteArrayOutputStream (256);
	javac.setOutputDir(ctxt.getOutputDir());
        javac.setMsgOutput(out);

	String javaFileName = mangler.getJavaFileName();
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
    }

    /** tool for customizing javac
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

	return javac;
    }

    // XXX need to implement precompile
    private void precompile() {
	//         String qString = request.getQueryString();
	//          if (qString != null &&
	// 		 (qString.startsWith(Constants.PRECOMPILE) ||
	// 		  qString.indexOf("&" + Constants.PRECOMPILE)
	// 		  != -1))
	//             precompile = true;
    }

}

/** Given a URL, generate pkg, class name, etc.
    This is an internal ( private ) object, we'll add get/set
    later ( after we pass the experimental stage) 
 */
class JspInfo {
    Request request;
    
    String uri; // path

    int version; // version
    int debug=0;
    String pkg;
    String pkgDir;
    String baseClassN;
    String fullClassN; // package.classN
    String classN; // no package
    String ext;

    String outputDir;
    String javaFilePath; // full path to the generated java file
    String realClassPath; // full path to the compiled java class
    String mapPath; // In even of server reload, keep last version

    File jspSource; // used to avoid File allocation for lastModified
    long compileTime;// tstamp of last compile attemp

    Exception compileException; // translation/compile exception 

    JspInfo( Request req ) {
	init( req );
    }

    public String toString() {
	return uri +" " + version;
    }

    /** Update compile time
     */
    public void touch() {
	compileTime=System.currentTimeMillis();
    }

    /** A change was detected, move to a new class name
     */
    public void nextVersion() {
	version++;
	updateVersionedPaths();
    }

    /** Update all paths that contain version number
     */
    void updateVersionedPaths() {
    if( pkgDir!=null ) {
        classN = baseClassN + "_" + version;
        realClassPath = outputDir + "/" + pkgDir + "/" + classN + ".class";
        javaFilePath = outputDir + "/" + pkgDir + "/" + classN + ".java";
        fullClassN = pkg  + "." + classN;
    } else {
        classN = baseClassN + "_" + version;
        realClassPath = outputDir + "/" +  classN + ".class";
        javaFilePath = outputDir + "/" + classN + ".java";
        fullClassN = classN;
    }

// 	log("ClassN=" + classN +
// 			   " realClassPath=" + realClassPath +
// 			   " javaFilePath=" + javaFilePath +
// 			   " fullClassN =" + fullClassN);
	writeVersion();
	// save to mapFile
    }

    private static String [] keywords = {
        "abstract", "boolean", "break", "byte",
        "case", "catch", "char", "class",
        "const", "continue", "default", "do",
        "double", "else", "extends", "final",
        "finally", "float", "for", "goto",
        "if", "implements", "import",
        "instanceof", "int", "interface",
        "long", "native", "new", "package",
        "private", "protected", "public",
        "return", "short", "static", "super",
        "switch", "synchronized", "this",
        "throw", "throws", "transient",
        "try", "void", "volatile", "while"
    };

    /** Mangle Package names to avoid reserver words **/
    private String manglePackage(String s){
	    for (int i = 0; i < keywords.length; i++) {
            char fs = File.separatorChar;
            int index = s.indexOf(keywords[i]);
            if(index == -1 ) continue;
            while (index != -1) {
                String tmpathName = s.substring (0,index) + "__";
                s = tmpathName + s.substring (index);
                index = s.indexOf(keywords[i],index+3);
            }
        }
        return(s);
    }

    /** Compute various names used
     */
    void init(Request req ) {
	this.request = req;
	compileException = null;
	// 	String includeUri
	// 	    = (String) req.getAttribute(Constants.INC_SERVLET_PATH);
	uri=req.getServletPath();
	Context ctx=req.getContext();
	outputDir = ctx.getWorkDir().getAbsolutePath();
	String jspFilePath=FileUtil.safePath( ctx.getAbsolutePath(),
					      uri); 
	jspSource = new File(jspFilePath);
	
	// extension
	int lastComp=uri.lastIndexOf(  "/" );
	String endUnproc=null;
	if( lastComp > 0 ) {
	    // has package
	    pkgDir=uri.substring( 1, lastComp );
	    endUnproc=uri.substring( lastComp+1 );
	} else {
	    endUnproc=uri.substring( 1 );
	}

	if( pkgDir!=null ) {
        pkgDir=manglePackage(pkgDir);
	    pkgDir=pkgDir.replace('.', '_');
	    pkg=pkgDir.replace('/', '.');
	    //	    pkgDir=pkgDir.replace('/', File.separator );

	}

	int extIdx=endUnproc.lastIndexOf( "." );

	if( extIdx>=0 ) {
	    baseClassN=endUnproc.substring( 0, extIdx );
	    ext=endUnproc.substring( extIdx );
	} else {
	    baseClassN=endUnproc;
	}
	// XXX insert "mangle" to make names safer
    if (pkgDir!=null)
    	mapPath = outputDir + "/" + pkgDir + "/" + baseClassN + ".ver";
    else
    	mapPath = outputDir + "/" + baseClassN + ".ver";

	File mapFile=new File(mapPath);
	if( mapFile.exists() ) {
	    // read version from file
	    readVersion();
	    updateVersionedPaths();
	    updateCompileTime();
	} else {
	    version=0;
	    updateVersionedPaths();
	    compileTime=0;
	}

	if( debug>0  )
	    log("uri=" + uri +
		//" outputDir=" + outputDir +
		//" jspSource=" + jspSource +
		" pkgDir=" + pkgDir +
		" baseClassN=" + baseClassN +
		" ext=" + ext +
		" mapPath=" + mapPath +
		" version=" + version);


    }

    /** After startup we try to find if the file was precompiled
	before
    */
    void readVersion() {
	File mapFile=new File(mapPath);
	version=0;
	compileTime=0;
	try {
	    FileInputStream fis=new FileInputStream( mapFile );
	    version=(int)fis.read();
// 	    log("Version=" + version );
	    fis.close();
	} catch( Exception ex ) {
	    log("readVersion() mapPath=" + mapPath, ex);
	}
    }

    /** After we compile a page, we save the version in a
	file with known name, so we can restore the state when we
	restart. Note that this should move to a general-purpose
	persist repository ( on my plans for next version of tomcat )
    */
    void writeVersion() {
	File mapFile=new File(mapPath);
	try {
	    File dir=new File(mapFile.getParent());
	    dir.mkdirs();
	    FileOutputStream fis=new FileOutputStream( mapFile );
	    fis.write(version);
// 	    log("WVersion=" + version );
	    fis.close();
	} catch( Exception ex ) {
	    log("writeVersion() mapPath=" + mapPath, ex);
	}
    }

    /** After a startup we read the compile time from the class
	file lastModified. No further access to that file is done.
	If class file doesn't exist, use java file lastModified if
	it exists.  We don't need to re-translate if the java file
	has not expired.
    */
    void updateCompileTime() {
	File f=new File( realClassPath );
	compileTime=0;
	if ( ! f.exists() ) return;
	compileTime=f.lastModified();
    }

    void setCompileException(Exception ex) {
	compileException = ex;
    }

    Exception getCompileException() {
	return compileException;
    }

    boolean isExceptionPresent() {
	return ( compileException != null );
    }

    void log(String s) {
	if (request != null && request.getContext() != null) {
	    request.getContext().log(s);
	}
	else {
	    System.err.println(s);
	}
    }

    void log(String s, Exception e) {
	if (request != null && request.getContext() != null) {
	    request.getContext().log(s, e);
	}
	else {
	    System.err.println(s);
	    e.printStackTrace();
	}
    }
}

// XXX add code to set the options
class TomcatOptions implements Options {
    public boolean keepGenerated = true;
    public boolean largeFile = false;
    public boolean mappedFile = false;
    public boolean sendErrorToClient = false;
    public String ieClassId = "clsid:8AD9C840-044E-11D1-B3E9-00805F499D93";
    public Class jspCompilerPlugin = null;
    public String jspCompilerPath = null;
    public int debug=0;
    
    public File scratchDir;
    private Object protectionDomain;
    public String classpath = null;

    public boolean getKeepGenerated() {
        return keepGenerated;
    }

    public boolean getLargeFile() {
        return largeFile;
    }

    public boolean getMappedFile() {
        return mappedFile;
    }
    
    public boolean getSendErrorToClient() {
        return sendErrorToClient;
    }
 
    public String getIeClassId() {
        return ieClassId;
    }

    public void setScratchDir( File f ) {
	scratchDir=f;
    }
    
    public File getScratchDir() {
	if( debug>0 ) log("Options: getScratchDir " + scratchDir);
        return scratchDir;
    }

    public final Object getProtectionDomain() {
	if( debug>0 ) log("Options: GetPD" );
	return protectionDomain;
    }

    public String getClassPath() {
	if( debug>0 ) log("Options: GetCP " + classpath  );
        return classpath;
    }

    public Class getJspCompilerPlugin() {
        return jspCompilerPlugin;
    }

    public String getJspCompilerPath() {
        return jspCompilerPath;
    }

    void log(String s) {
	System.err.println(s);
    }
    
}


class JspEngineContext1 implements JspCompilationContext {
    JspReader reader;
    ServletWriter writer;
    ServletContext context;
    JspLoader loader;
    String classpath; // for compiling JSPs.
    boolean isErrPage;
    String jspFile;
    String servletClassName;
    String servletPackageName;
    String servletJavaFileName;
    String contentType;
    Options options;
    public int debug=0;
    
    Request req;
    Mangler m;
    
    public JspEngineContext1(Request req, Mangler m)
    {
	this.req=req;
	this.m=m;
    }

    public HttpServletRequest getRequest() {
	if( debug>0 ) log("JspEngineContext1: getRequest " + req );
        return (HttpServletRequest)req.getFacade();
    }
    

    /**
     * Get the http response we are using now...
     */
    public HttpServletResponse getResponse() {
	if( debug>0 ) log("JspEngineContext1: getResponse " );
        return (HttpServletResponse)req.getResponse().getFacade();
    }

    /**
     * The classpath that is passed off to the Java compiler. 
     */
    public String getClassPath() {
	if( debug>0 ) log("JspEngineContext1: getClassPath " +
	    JspInterceptor.getClassPath(req.getContext()));
	return JspInterceptor.getClassPath(req.getContext());
    }
    
    /**
     * Get the input reader for the JSP text. 
     */
    public JspReader getReader() {
	if( debug>0 ) log("JspEngineContext1: getReader " + reader );
        return reader;
    }
    
    /**
     * Where is the servlet being generated?
     */
    public ServletWriter getWriter() {
	if( debug>0 ) log("JspEngineContext1: getWriter " + writer );
        return writer;
    }
    
    /**
     * Get the ServletContext for the JSP we're processing now. 
     */
    public ServletContext getServletContext() {
	if( debug>0 ) log("JspEngineContext1: getCtx " +
			   req.getContext().getFacade());
        return (ServletContext)req.getContext().getFacade();
    }
    
    /**
     * What class loader to use for loading classes while compiling
     * this JSP? I don't think this is used right now -- akv. 
     */
    public ClassLoader getClassLoader() {
	if( debug>0 ) log("JspEngineContext1: getLoader " + loader );
        return req.getContext().getClassLoader();
    }

    public void addJar( String jar ) throws IOException {
	if( debug>0 ) log("Add jar " + jar);
	//loader.addJar( jar );
    }

    /**
     * Are we processing something that has been declared as an
     * errorpage? 
     */
    public boolean isErrorPage() {
	if( debug>0 ) log("JspEngineContext1: isErrorPage " + isErrPage );
        return isErrPage;
    }
    
    /**
     * What is the scratch directory we are generating code into?
     * FIXME: In some places this is called scratchDir and in some
     * other places it is called outputDir.
     */
    public String getOutputDir() {
	if( debug>0 ) log("JspEngineContext1: getOutputDir " +
			   req.getContext().getWorkDir().getAbsolutePath());
        return req.getContext().getWorkDir().getAbsolutePath();
    }
    
    /**
     * Path of the JSP URI. Note that this is not a file name. This is
     * the context rooted URI of the JSP file. 
     */
    public String getJspFile() {
	String sP=req.getServletPath();
	Context ctx=req.getContext();
	if( debug>0 ) log("JspEngineContext1: getJspFile " +
			   sP);//   ctx.getRealPath( sP ) );
	//        return ctx.getRealPath( sP );
	return sP;
    }
    
    /**
     * Just the class name (does not include package name) of the
     * generated class. 
     */
    public String getServletClassName() {
	if( debug>0 ) log("JspEngineContext1: getServletClassName " +
			   m.getClassName());
        return m.getClassName();
    }
    
    /**
     * The package name into which the servlet class is generated. 
     */
    public String getServletPackageName() {
	if( debug>0 ) log("JspEngineContext1: getServletPackageName " +
			   servletPackageName );
        return servletPackageName;
    }

    /**
     * Utility method to get the full class name from the package and
     * class name. 
     */
    public final String getFullClassName() {
	if( debug>0 ) log("JspEngineContext1: getServletPackageName " +
			   servletPackageName + "." + servletClassName);
        if (servletPackageName == null)
            return servletClassName;
        return servletPackageName + "." + servletClassName;
    }

    /**
     * Full path name of the Java file into which the servlet is being
     * generated. 
     */
    public String getServletJavaFileName() {
	if( debug>0 ) log("JspEngineContext1: getServletPackageName " +
			   servletPackageName + "." + servletClassName);
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

    public void setOptions(Options options) {
	this.options=options;
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

    public Compiler createCompiler() throws JasperException {
	if( debug>0 ) log("JspEngineContext1: createCompiler ");
	return null;
    }
    
    public String resolveRelativeUri(String uri)
    {
	if( debug>0 ) log("JspEngineContext1: resolveRelativeUri " + uri);
	return null;
    };    

    public java.io.InputStream getResourceAsStream(String res)
    {
	if( debug>0 ) log("JspEngineContext1: getRAS " + res);
        ServletContext sctx=(ServletContext)req.getContext().getFacade();
	return sctx.getResourceAsStream(res);
    };

    /** 
     * Gets the actual path of a URI relative to the context of
     * the compilation.
     */
    public String getRealPath(String path)
    {
	if( debug>0 ) log("GetRP " + path);
	Context ctx=req.getContext();
	return FileUtil.safePath( ctx.getAbsolutePath(),
				  path);
    };

    void log(String s, Exception e) {
	if (this.req != null && this.req.getContext() != null) {
	    this.req.getContext().log(s, e);
	}
	else {
	    System.err.println(s);
	    e.printStackTrace();
	}
    }

    void log(String s) {
	if (req != null && req.getContext() != null) {
	    req.getContext().log(s);
	}
	else {
	    System.err.println(s);
	}
    }

}


class JspMangler implements Mangler{
    JspInfo jspInfo;

    public JspMangler(JspInfo info)  {
	this.jspInfo=info;
    }

    public final String getClassName() {
        return jspInfo.classN;
    }

    public final String getJavaFileName() {
	return jspInfo.javaFilePath;
    }

    public final String getPackageName() {
	return jspInfo.pkg;
	// It's not used, and shouldn't be used by compiler.
	// ( well, it's used to rename the file after compile
	// in JspServlet scheme - that must be out of compiler )
    }

    // Full path to the class file - without version.
    public final String getClassFileName() {
	return null; // see getPackageName comment
    }
}

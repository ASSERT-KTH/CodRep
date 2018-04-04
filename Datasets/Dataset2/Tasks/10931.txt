String hValue = req.getHeader(hName);

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
package org.apache.tomcat.modules.generators;

import org.apache.tomcat.core.*;
import org.apache.tomcat.util.res.StringManager;
import org.apache.tomcat.util.io.FileUtil;
import org.apache.tomcat.util.http.*;
import org.apache.tomcat.util.buf.*;
import java.io.*;
import java.net.*;
import java.text.*;
import java.util.*;
import java.security.*;

/**
 * Handler for static files.
 *
 * @author costin@dnt.ro
 */
public class StaticInterceptor extends BaseInterceptor {
    int realFileNote=-1;
    boolean useAcceptLanguage=true;
    String charset=null;
    private boolean extraSafety=false;
    private boolean useInternal=false;
    private boolean strict23Welcome=false;

    public StaticInterceptor() {
    }

    /**
     * Should directory listings be generated when there is
     * no welcome file present?
     */
    private boolean listings = true;

    public boolean getListings() {
	return listings;
    }

    public void setListings(boolean listings) {
	this.listings = listings;
    }

    /** Do we do an internal redirect?
     *  @param internal <code>true</code>  do an internal redirect.
                        <code>false</code> do a 301 redirect.
    */
    public void setUseInternal(boolean internal) {
	useInternal = internal;
    }

    /** Support the 2.3 behavior of allowing mapped servlets as welcome files.
     * @param support <code>true</code> Allow mapped servlets.
     *                <code>false</code> Allow only files.
     */
    public void setStrict23Welcome(boolean support) {
	strict23Welcome = support;
    }

    public void setUseAcceptLanguage(boolean use) {
        useAcceptLanguage=use;
    }

    public void setUseCharset(String charset) {
        this.charset=charset;
    }
    /** Request extra safety checks.
     *  Defaults to <code>false</code> since it also prevents
     *  certain include/forwards from working.
     */
    public void setExtraSafety(boolean safe) {
	extraSafety = safe;
    }
    public void engineInit(ContextManager cm) throws TomcatException {
	//	if( debug>0 ) log("Engine init " );
	
	try {
	    realFileNote = cm.getNoteId( ContextManager.REQUEST_NOTE,
				       "static.realFile");
	} catch( TomcatException ex ) {
	    log("getting note for " + cm, ex);
	    throw new RuntimeException( "Invalid state ");
	}
    }
    
    public void contextInit( Context ctx)
	throws TomcatException
    {
	//if( debug>0 ) log("Ctx init " + ctx );
	FileHandler fileHandler=new FileHandler();
	DirHandler dirHandler=new DirHandler();
	fileHandler.setModule( this );
	fileHandler.setContext( ctx );
	fileHandler.setNoteId( realFileNote );
	fileHandler.setExtraSafety(extraSafety);
	ctx.addServlet( fileHandler );

	dirHandler.setNoteId( realFileNote );
	dirHandler.setContext( ctx );
	dirHandler.setModule( this );
        dirHandler.setUseAcceptLanguage(useAcceptLanguage);
        dirHandler.setCharset(charset);
	if (listings)
	    ctx.addServlet( dirHandler );
    }

    public int requestMap(Request req) {
	//	if( debug>0 ) log("Req map " + req);
	if( req.getHandler() != null )
	    return 0;

	Context ctx=req.getContext();

	// will call getRealPath(), all path normalization
	// and a number of checks
	String pathInfo=req.servletPath().toString();
	if( pathInfo==null ) pathInfo="";

	if( debug > 0 ) log("Method: " + req.method());
	if(req.method().equalsIgnoreCase("OPTIONS") ||
           req.method().equalsIgnoreCase("TRACE")) {
	    req.setHandler(  ctx.getServletByName( "tomcat.fileHandler"));
	    return 0;
	}
	    
	String absPath=FileUtil.safePath( ctx.getAbsolutePath(),
					  pathInfo);

	if( debug > 0 ) log( "RequestMap " + req + " " + absPath + " " +
			     ctx.getAbsolutePath() );
	if( absPath == null ) return 0;
	String requestURI=req.requestURI().toString();

	if( debug > 0 )
	    log( "Requested: "  + absPath );

	File file=new File( absPath );

	if( file.isFile() ) {
	    if( debug > 0 ) log( "Setting handler to file " + absPath);
	    req.setNote( realFileNote, absPath );
	    req.setHandler(  ctx.getServletByName( "tomcat.fileHandler"));
	    return 0;
	}

	if( ! file.isDirectory() ) {
	    // we support only files and dirs
	    if( debug > 0) log( "No file and no directory");
	    return 0; // no handler is set - will end up as 404
	}


	// consistent with Apache
	if( ! requestURI.endsWith("/") && !req.getResponse().isIncluded()) {
	    String redirectURI= requestURI + "/";
	    redirectURI=fixURLRewriting( req, redirectURI );
	    String query = req.query().toString();
	    if( query != null && !query.equals("") )
		redirectURI += "?" + query;
	    req.setAttribute("javax.servlet.error.message",
			     redirectURI);
	    if( debug > 0) log( "Redirect " + redirectURI );
	    req.setHandler( ctx.getServletByName( "tomcat.redirectHandler"));
	    return 0;
	}
	// Directory, check if we have a welcome file
	
	String welcomeFile = null;
	if( strict23Welcome ) {
	    welcomeFile = getStrictWelcomeFile(ctx, file, pathInfo);
	} else {
	    welcomeFile = getWelcomeFile(ctx, file);
	}
	if( debug > 0 )
	    log( "DefaultServlet: welcome file: "  + welcomeFile);
	
	// Doesn't matter if we are or not in include
	if( welcomeFile == null  ) {
	    // normal dir, no welcome.
	    req.setHandler( ctx.getServletByName( "tomcat.dirHandler"));
	    if( debug > 0) log( "Dir handler");
	    return 0;
	}
	int status = 0;
	if(useInternal) {
	    status = doInternalRedirect(req,welcomeFile);
	} else {
	    status = doExternalRedirect(req,welcomeFile);
	}
	return status;
    }

    /** Re-map the request as an internal redirect.
     *  We have gray areas in the 2.2 spec, so we are going to follow
     *  the 2.3 spec for guidance.
     */
    private int doInternalRedirect(Request req, String welcomeFile) {
        BaseInterceptor ri[];
	String requestURI=req.requestURI().toString();
	String redirectURI=concatPath(requestURI,welcomeFile);
	Context ctx = req.getContext();
	req.requestURI().setString(redirectURI);
	req.unparsedURI().recycle();
	req.servletPath().recycle();
	req.pathInfo().recycle();

	/* We are using the real request here, so we don't want to have
	   to repeat all of the pre-processing for cm.processRequest.
	   This means that postReadRequest hooks aren't re-called for 
	   the new URI, but that shouldn't matter. And calling
	   them again is more likely to do harm than good IMHO. However,
	   we need to contextMap again to catch extention-mapped servlets.
	*/
	int status = 0;
	if(ctx == null) {
	    ri=cm.getContainer().getInterceptors(Container.H_contextMap);
	} else {
	    ri = ctx.getContainer().getInterceptors(Container.H_contextMap);
	}
	
	for( int i=0; i< ri.length; i++ ) {
	    status=ri[i].contextMap( req );
	    if( status!=0 ) return status;
	}
	ri=req.getContext().getContainer().
	    getInterceptors(Container.H_requestMap);
	for( int i=0; i< ri.length; i++ ) {
	    if( debug > 1 )
		log( "RequestMap " + ri[i] );
	    status=ri[i].requestMap( req );
	    if( status!=0 ) return status;
	    if(ri[i] == this) 
		break; // ContextManager will finish the list.
	}
	return 0; 
    }
    /** Send redirect to the welcome file.
     * This is consistent with other web servers and avoids
     * gray areas in the spec - if the welcome file is a jsp,
     * what will be the requestPath - if it's the dir, then
     * jasper will not work. The original code created a
     * RequestDispatcher and the JSP will see an included
     * request, but that's not a specified behavior
     */
    private int doExternalRedirect(Request req, String welcomeFile) {
    	String redirectURI=null;
	String requestURI=req.requestURI().toString();
	redirectURI=concatPath( requestURI, welcomeFile);
	redirectURI=fixURLRewriting( req, redirectURI );
	String query = req.query().toString();
	if ( query != null && ! query.equals("") )
	    redirectURI += "?" + query;
	Context lCtx = req.getContext();

	req.setAttribute("javax.servlet.error.message",
			 redirectURI);
	if( debug > 0) log( "Redirect " + redirectURI );
	// allow processing to go on - another mapper may change the
	// outcome, we are just the default ( preventive for bad ordering,
	// in correct config Static is the last one anyway ).
	req.setHandler( lCtx.getServletByName( "tomcat.redirectHandler"));
	return 0;
    }

    // Fix for URL rewriting 
    private String fixURLRewriting(Request req, String redirectURI ) {
	ServerSession session=req.getSession( false );
	if( session != null &&
	    Request.SESSIONID_FROM_URL.equals(req.getSessionIdSource()))  {
	    String id=";jsessionid="+req.getSessionId() ;
	    redirectURI += id ;
	}
	return redirectURI;
    }

    
    private static String concatPath( String s1, String s2 ) {
	if( s1.endsWith( "/" ) ) {
	    if( s2.startsWith( "/" ))
		return s1 + s2.substring(1);
	    else
		return s1 + s2;
	} else {
	    if( s2.startsWith("/"))
		return s1 + s2;
	    else
		return s1 + "/" + s2;
	}
    }

    private String getStrictWelcomeFile(Context context, File dir, String pathInfo) {
        String wf[]= context.getWelcomeFiles();
        BaseInterceptor ri[] = context.getContainer().
	                          getInterceptors(Container.H_contextMap);
	for(int i=0; i < wf.length; i++) {
	    if(getOneWelcomeFile(dir, wf[i])) {
		return wf[i];
	    }
	    String wfURI = concatPath(pathInfo, wf[i]);
	    Request req = cm.createRequest(context, wfURI);
	    int status = 0;
	
	    for( int j=0; j< ri.length; j++ ) {
		status=ri[j].contextMap( req );
		if( status!=0 ) break;
	    }
	    if(status == 0 && req.servletPath() != null && 
	       ! req.servletPath().equals("") && 
	       req.getContainer().getMapType() != Container.EXTENSION_MAP) {
		return req.servletPath().toString().substring(pathInfo.length());
	    }
	}
	    
	return null;
    }
    private String getWelcomeFile(Context context, File dir) {
        String wf[]= context.getWelcomeFiles();

	for( int i=0; i<wf.length; i++ ) {
	    if (getOneWelcomeFile(dir, wf[i])) {
		return wf[i];
	    }
	}
	return null;
    }
    private boolean getOneWelcomeFile(File dir, String wf) {
	File f = new File(dir, wf);
	return f.exists();
    }
}

// -------------------- Handlers --------------------

/** Serve the content of a file ( and nothing more !).
 *
 */
final class FileHandler extends Handler  {
    int realFileNote;
    Context context;
    private boolean extraSafety=false;

    FileHandler() {
	//	setOrigin( Handler.ORIGIN_INTERNAL );
	name="tomcat.fileHandler";
    }

    public void setContext(Context ctx) {
	this.context=ctx;
    }

    public void setExtraSafety(boolean safe) {
	extraSafety = safe;
    }
    public void setNoteId( int n ) {
	realFileNote=n;
    }

    public void doService(Request req, Response res)
	throws Exception
    {
	if(req.method().equalsIgnoreCase("OPTIONS")) {
	    doOptions(req, res);
	    return;
	} else if(req.method().equalsIgnoreCase("TRACE")) {
	    doTrace(req, res);
	    return;
	}
	// if we are in include, with req==original request
	// - just use the current sub-request
	Request subReq=req;
	if(req.getChild()!=null)
	    subReq=req.getChild();
	Context ctx=subReq.getContext();
	// Use "javax.servlet.include.servlet_path" for path if defined.
	// ErrorHandler places the path here when invoking an error page.
	String pathInfo = (String)subReq.getAttribute("javax.servlet.include.servlet_path");
	if(pathInfo == null) {
	    // If the attribute isn't there, then we aren't included.
	    // In that case, we must use the real request.
	    //*** DEBUG *** subReq = req;
	    pathInfo=subReq.servletPath().toString();
	}
	String absPath = (String)subReq.getNote( realFileNote );
	if( absPath==null )
	    absPath=FileUtil.safePath( context.getAbsolutePath(),
				       pathInfo);

	if( debug>0) log( "Requested file = " + absPath);
	String base = ctx.getAbsolutePath();
	absPath = extraCheck( base, absPath );
	if( absPath==null ) {
	    context.getContextManager().handleStatus( req, res, 404);
	    return;
	}

	File file = new File( absPath );
	// If we are included, the If-Modified-Since isn't for us.
	if( ! res.isIncluded() ) {
	    long date = req.getDateHeader("If-Modified-Since");
	    if ((file.lastModified() <= (date + 1000)) ) {
		// The entity has not been modified since the date
		// specified by the client. This is not an error case.
		context.getContextManager().handleStatus( req, res, 304);
		return;
	    }

	}
	if( debug>0) log( "After paranoic checks = " + absPath);

        String mimeType=ctx.getMimeMap().getContentTypeFor(absPath);

	if (mimeType == null) {
	    mimeType = "text/plain";
	}
	if( debug>0) log( "Serving  " + absPath);
	
	res.setContentType(mimeType);
	res.setContentLength((int)file.length());

	setDateHeader(res, "Last-Modified", file.lastModified());

	FileInputStream in=null;
	try {
	    in = new FileInputStream(file);

	    OutputBuffer out=res.getBuffer();
	    byte[] buf = new byte[1024];
	    int read = 0;
	    
	    while ((read = in.read(buf)) != -1) {
		out.write(buf, 0, read);
	    }
	} catch (FileNotFoundException e) {
	    // Figure out what we're serving
	    context.getContextManager().handleStatus( req, res, 404);
	} finally {
	    if (in != null) {
		in.close();
	    }
	}
    }

    // This should be deprecated as dangerous.
    static void setDateHeader( Response res, String name, long value ) {
	if( ! res.isIncluded() ) {
	    MimeHeaders headers=res.getMimeHeaders();
	    headers.setValue( name ).setTime( value );
	}
    }
    void doOptions(Request req, Response res)
	    throws IOException {
	res.addHeader("Allow","HEAD, GET, POST, OPTIONS, TRACE");
    }
    void doTrace(Request req, Response res)
	throws IOException {
	String CRLF = "\r\n";
	res.setContentType("message/http");
	StringBuffer resp = new StringBuffer();
	Enumeration headers = req.getHeaderNames();
	while( headers.hasMoreElements() ) {
	    String hName = (String)headers.nextElement();
	    String hValue = req.getMimeHeaders().getHeader(name);
	    resp.append(CRLF).append(hName).append(": ").append(hValue);
	}
	resp.append(CRLF);
	res.setContentLength(resp.length());
	Writer out = res.getBuffer();
	out.write(resp.toString());
    }

    /** All path checks that were part of DefaultServlet
     */
    String extraCheck( String base, String absPath ) {
	// Extra safe 
	if (absPath.endsWith("/") ||
	    absPath.endsWith("\\") ||
	    absPath.endsWith(".")) {
	    log("Ends with \\/. " + absPath);
	    return null;
	}
	if(extraSafety) {
	    if (absPath.length() > base.length())
		{
		    String relPath=absPath.substring( base.length() + 1);
		    if( debug>0) log( "RelPath = " + relPath );

		    String relPathU=relPath.toUpperCase();
		    if ( relPathU.startsWith("WEB-INF") ||
			 relPathU.startsWith("META-INF") ||
			 (relPathU.indexOf("/WEB-INF/") >= 0) ||
			 (relPathU.indexOf("/META-INF/") >= 0) ) {
			return null;
		    }
		}
	}
	return absPath;
    }


}

// -------------------- Directory --------------------

/** HTML-display for directories ( and nothing more !).
 *  This is the handler for static resources of type "dir".
 */
final class DirHandler extends Handler  {
    private static final String datePattern = "EEE, dd MMM yyyyy HH:mm z";
    int realFileNote;
    int sbNote=0;
    Context context;
    Locale defLocale=null;
    String defCharset=null;
    StringManager defSM=null;

    DirHandler() {
	//	setOrigin( Handler.ORIGIN_INTERNAL );
	name="tomcat.dirHandler";
    }

    public void setNoteId( int n ) {
	realFileNote=n;
    }

    public void setContext(Context ctx) {
	this.context=ctx;
    }

    public void setUseAcceptLanguage(boolean use) {
        if( use ) {
            defLocale=null;
            defSM=null;
        } else {
            defLocale=Locale.getDefault();
            defSM=StringManager.
                    getManager("org.apache.tomcat.resources",defLocale);
        }
    }

    public void setCharset(String charset) {
        defCharset=charset;
    }
    
    public void doService(Request req, Response res)
	throws Exception
    {
        Locale locale;
        StringManager sm;
        String charset=null;

        // if default locale not specified, use Accept-Language header
        if( defLocale == null) {
            // this is how get locale is implemented. Ugly, but it's in
            // the next round of optimizations
            String acceptL=req.getMimeHeaders().getHeader( "Accept-Language");
            locale=AcceptLanguage.getLocale(acceptL);
            sm=StringManager.
                getManager("org.apache.tomcat.resources",locale);
        } else {
            locale=defLocale;
            sm=defSM;
        }

        if( defCharset != null ) {
            if( "locale".equals(defCharset))
                charset=LocaleToCharsetMap.getCharset(locale);
            else
                charset=defCharset;
        }

	DateFormat dateFormat =
	    new SimpleDateFormat(datePattern,locale );

	boolean inInclude=req.getChild()!=null;
	Request subReq=req;
	if( inInclude ) subReq = req.getChild();
	Context ctx=req.getContext();
	String pathInfo=subReq.servletPath().toString();
	if( pathInfo == null ) pathInfo="";
	String absPath=FileUtil.safePath( context.getAbsolutePath(),
					  pathInfo);
	File file = new File( absPath );
	String requestURI=subReq.requestURI().toString();
	String base = ctx.getAbsolutePath();
	if (absPath.length() > base.length())
	{
		String relPath=absPath.substring( base.length() + 1);
		String relPathU=relPath.toUpperCase();
		if ( relPathU.startsWith("WEB-INF") ||
		     relPathU.startsWith("META-INF")) {
		    context.getContextManager().handleStatus( req, res, 404);
		    return;
		}
	}

	OutputBuffer buf=res.getBuffer();
	if( sbNote==0 ) {
	    //sbNote=req.getContextManager().
	    //    getNoteId(ContextManager.REQUEST_NOTE,
	    // 		     "RedirectHandler.buff");
	    sbNote=req.getContextManager().
		getNoteId(ContextManager.REQUEST_NOTE,"uft8encoder");
	}

	// we can recycle it because
	// we don't call toString();
	// 	StringBuffer buf=(StringBuffer)req.getNote( sbNote );
	// 	if( buf==null ) {
	// 	    buf = new StringBuffer();
	// 	    req.setNote( sbNote, buf );
	// 	}

	UEncoder utfEncoder=(UEncoder)req.getNote( sbNote );
	if( utfEncoder==null ) {
	    utfEncoder=new UEncoder();
	    utfEncoder.addSafeCharacter( '/' );
	}

	if (! inInclude) {
           if (charset == null || charset.equalsIgnoreCase("ISO-8859-1"))
               res.setContentType("text/html");
           else {
               res.setContentType("text/html; charset=" + charset);
               res.setUsingWriter(true);
           }
	    buf.write("<html>\r\n");
	    buf.write("<head>\r\n");
	    buf.write("<title>");
	    buf.write(sm.getString("defaultservlet.directorylistingfor"));
	    buf.write(requestURI);
	    buf.write("</title>\r\n</head><body bgcolor=white>\r\n");
	}

	buf.write("<table width=90% cellspacing=0 ");
	buf.write("cellpadding=5 align=center>");
	buf.write("<tr><td colspan=3><font size=+2><strong>");
	buf.write(sm.getString("defaultservlet.directorylistingfor"));
	buf.write(requestURI);
	buf.write("</strong></td></tr>\r\n");

	if (! pathInfo.equals("/")) {
	    buf.write("<tr><td colspan=3 bgcolor=#ffffff>");
	    //buf.write("<a href=\"../\">Up one directory");
	    
	    String toPath = requestURI;

	    if (toPath.endsWith("/")) {
		toPath = toPath.substring(0, toPath.length() - 1);
	    }
	    
	    toPath = toPath.substring(0, toPath.lastIndexOf("/"));
	    
	    //if (toPath.length() == 0) {
	    //toPath = "/";
	    //}
	    // Add trailing "/"
	    toPath += "/";
	    
	    buf.write("<a href=\"");
	    utfEncoder.urlEncode( buf, toPath);
	    buf.write( "\"><tt>" );
	    buf.write( sm.getString("defaultservlet.upto"));
	    buf.write( toPath);
	    buf.write("</tt></a></td></tr>\r\n");
	}

	// Pre-calculate the request URI for efficiency

	// Make another URI that definitely ends with a /
	String slashedRequestURI = null;

	if (requestURI.endsWith("/")) {
	    slashedRequestURI = requestURI;
	} else {
	    slashedRequestURI = requestURI + "/";
	}

	String[] fileNames = file.list();
	boolean dirsHead=true;
	boolean shaderow = false;

	for (int i = 0; i < fileNames.length; i++) {
	    String fileName = fileNames[i];

            // Don't display special dirs at top level
	    if( (pathInfo.length() == 0 || "/".equals(pathInfo)) &&
     		"WEB-INF".equalsIgnoreCase(fileName) ||
 	    	"META-INF".equalsIgnoreCase(fileName) )
    		continue;

	    File f = new File(file, fileName);

	    if (f.isDirectory()) {
		if( dirsHead ) {
		    dirsHead=false;
		    buf.write("<tr><td colspan=3 bgcolor=#cccccc>");
		    buf.write("<font size=+2><strong>");
		    buf.write( sm.getString("defaultservlet.subdirectories"));
		    buf.write( "</strong>\r\n");
		    buf.write("</font></td></tr>\r\n");
		}

                String fileN = f.getName();

                buf.write("<tr");

                if (shaderow) buf.write(" bgcolor=#eeeeee");
		shaderow=!shaderow;
		
                buf.write("><td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;");
                buf.write("<tt><a href=\"");
		utfEncoder.urlEncode( buf, slashedRequestURI);
		utfEncoder.urlEncode( buf, fileN);
		buf.write("/\">");
		buf.write(fileN);
		buf.write("/</a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;");
		buf.write("</tt>\r\n");
                buf.write("</td><td><tt>&nbsp;&nbsp;</tt></td>");
                buf.write("<td align=right><tt>");
		buf.write(dateFormat.format(new Date(f.lastModified())));
                buf.write("</tt></td></tr>\r\n");
	    }
	}

	shaderow = false;
	buf.write("<tr><td colspan=3 bgcolor=#ffffff>&nbsp;</td></tr>");
	boolean fileHead=true;
	
	for (int i = 0; i < fileNames.length; i++) {
	    File f = new File(file, fileNames[i]);

	    if (f.isFile()) {
		String fileN = f.getName();
		
		if( fileHead ) {
		    fileHead=false;
		    buf.write("<tr><td colspan=4 bgcolor=#cccccc>");
		    buf.write("<font size=+2><strong>");
		    buf.write(sm.getString("defaultservlet.files"));
		    buf.write("</strong></font></td></tr>");
		}

		buf.write("<tr");

		if (shaderow) buf.write(" bgcolor=#eeeeee");
		shaderow = ! shaderow;
		
		buf.write("><td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\r\n");

		buf.write("<tt><a href=\"");
		utfEncoder.urlEncode( buf, slashedRequestURI);
		utfEncoder.urlEncode( buf, fileN);
		buf.write("\">");
		buf.write( fileN );
		buf.write( "</a>");
		buf.write("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</tt>");
		buf.write("</td>\r\n");

		buf.write("<td align=right><tt>");
		displaySize( buf, (int)f.length());
		buf.write("</tt></td>");

		buf.write("<td align=right><tt>");
		buf.write(dateFormat.format(new Date(f.lastModified())));
		buf.write("</tt></td></tr>\r\n");
	    }
	    
	    buf.write("\r\n");
	}
	
	buf.write("<tr><td colspan=3 bgcolor=#ffffff>&nbsp;</td></tr>");
	buf.write("<tr><td colspan=3 bgcolor=#cccccc>");
	buf.write("<font size=-1>");
	buf.write(ContextManager.TOMCAT_NAME);
	buf.write(" v");
	buf.write(ContextManager.TOMCAT_VERSION);
	buf.write("</font></td></tr></table>");
	
	if (! inInclude)  buf.write("</body></html>\r\n");

    // 	res.getBuffer().write(buf);
    // 	buf.setLength(0);
    }

    void displaySize( OutputBuffer buf, int filesize )
	throws IOException
    {
	int leftside = filesize / 1024;
	int rightside = (filesize % 1024) / 103;  // makes 1 digit
	// To avoid 0.0 for non-zero file, we bump to 0.1
	if (leftside == 0 && rightside == 0 && filesize != 0) 
	    rightside = 1;
	buf.write(String.valueOf(leftside));
	buf.write(".");
	buf.write(String.valueOf(rightside));
	buf.write(" KB");
    }
}
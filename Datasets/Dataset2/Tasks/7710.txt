int debug=0;

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
package org.apache.tomcat.servlets;

import org.apache.tomcat.core.*;
import org.apache.tomcat.core.Constants;
import org.apache.tomcat.util.*;
import java.io.*;
import java.net.*;
import java.text.*;
import java.util.*;
import javax.servlet.*;
import javax.servlet.http.*;

/**
 * 
 * @author James Duncan Davidson [duncan@eng.sun.com]
 * @author Jason Hunter [jch@eng.sun.com]
 * @author James Todd [gonzo@eng.sun.com]
 */
public class DefaultServlet extends HttpServlet {
    private static final String datePattern = "EEE, dd MMM yyyyy HH:mm z";
    private static final DateFormat dateFormat = new SimpleDateFormat(datePattern);

    ServletContext contextF;
    private Context context;
    String docBase;
    int debug=1;
    
    public void init() throws ServletException {
	contextF = getServletContext();
	context = ((ServletContextFacade)getServletContext()).getRealContext();

	// doesn't change - set it in init!
	docBase = context.getDocBase();
        if (! docBase.endsWith("/")) {
            docBase += "/";
        }

	// debug 
	String dbg=getServletConfig().getInitParameter("debug");
	if( dbg!=null) debug=1;
    }

    public String getServletInfo() {
        return "DefaultServlet";
    }

    public void doGet(HttpServletRequest request,
		      HttpServletResponse response)
	throws ServletException, IOException
    {
	String pathInfo = (String)request.getAttribute(
            "javax.servlet.include.path_info");
	String requestURI = (String)request.getAttribute(
            "javax.servlet.include.request_uri");

	if (pathInfo == null) {
	    pathInfo = request.getPathInfo();
	}

	if (requestURI == null) {
	    requestURI = request.getRequestURI();
	}

	// Clean up pathInfo 
	File file = new File(docBase + pathInfo);
	String absPath = file.getAbsolutePath();
	
	if( debug > 0 ) contextF.log( "DefaultServlet: "  + absPath);

        // take care of File.getAbsolutePath() troubles on
        // jdk1.1.x/win
        String patchedPath = FileUtil.patch(absPath);
	if( debug > 0 && ! absPath.equals(patchedPath)  )
	    contextF.log( "DefaultServlet: patched path" + patchedPath );
	absPath=patchedPath;

        if (isFileMasked(docBase, absPath)) {
	    response.sendError(response.SC_NOT_FOUND);
	    return;
        }

        if (file.isDirectory()) {
	    // check for welcome file
	    String welcomeFile = getWelcomeFile(file);
	    if( debug > 0 ) contextF.log( "DefaultServlet: welcome file: "  + welcomeFile);
	    
	    if (welcomeFile != null) {
	        if (requestURI.endsWith("/")) {
		    String path = requestURI;
		    String contextPath = context.getPath();

		    if (contextPath.length() == 0) {
		        contextPath = "/";
		    }

		    int index = requestURI.indexOf(contextPath);

		    if (index > -1 ) {
		        path = requestURI.substring(
			    index + contextPath.length());
		    }

		    if (! path.startsWith("/")) {
		        path = "/" + path;
		    }

		    if( debug > 0 ) contextF.log( "DefaultServlet: forward: "  + path + " " + welcomeFile);
		    ServletContext context =
		        getServletContext().getContext(contextPath);
		    RequestDispatcher rd = context.getRequestDispatcher(
			path + welcomeFile);

		    rd.forward(request, response);
		} else {
		    boolean inInclude = false;
		    Object o = request.getAttribute(
                        Constants.Attribute.Dispatch);

		    if (o != null) {
		        inInclude = true;
		    }

		    // do a redirect so that all relative
		    // urls work correctly

		    if( debug > 0 ) contextF.log( "DefaultServlet: redirect: "  + requestURI);
		    if (! inInclude) {
			response.sendRedirect(requestURI + "/");
		    }
		}
	    } else {
	        // XXX
	        // ok, see if it's okay to do this
	        serveDir(file, request, response);
	    }
	} else {
	    // serve that file
	    // check that .jsp/ doesn't slip through on Windows!
	    if( debug > 0 ) contextF.log( "DefaultServlet: serving file: "  + file);
	    if (! absPath.endsWith("/") &&
	        ! absPath.endsWith("\\")) {
	        serveFile(file, request, response);
	    } else {
	        response.sendError(response.SC_NOT_FOUND,
                    "File Not Found<br>" + requestURI);
	    }
	}
    }

    private String getWelcomeFile(File file) {
        String welcomeFile = null;
        Enumeration enum = context.getWelcomeFiles();

	while (enum.hasMoreElements()) {
	    String fileName = (String)enum.nextElement();

            if (fileName != null &&
                fileName.trim().length() > 0) {
	        File f = new File(file, fileName);

	        if (f.exists()) {
	            welcomeFile = fileName;

		    break;
                }
	    }
	}

	return welcomeFile;
    }

    private void serveFile(File file, HttpServletRequest request,
        HttpServletResponse response)
    throws IOException {

	String absPath = file.getAbsolutePath();
	String canPath = file.getCanonicalPath();

        // take care of File.getAbsolutePath() troubles on
        // jdk1.1.x/win

        absPath = FileUtil.patch(absPath);

        // This absPath/canPath comparison plugs security holes...
	// On Windows, makes "x.jsp.", "x.Jsp", and "x.jsp%20" 
        // return 404 instead of the JSP source
	// On all platforms, makes sure we don't let ../'s through
        // Unfortunately, on Unix, it prevents symlinks from working
	// So, a check for File.separatorChar='\\' ..... It hopefully
	// happens on flavors of Windows.
	if (File.separatorChar  == '\\') { 
		// On Windows check ignore case....
		if(!absPath.equalsIgnoreCase(canPath)) {
	    	response.sendError(response.SC_NOT_FOUND);
	    	return;
		}
	} else {
		// The following code on Non Windows disallows ../ 
		// in the path but also disallows symlinks.... 
		// 
		// if(!absPath.equals(canPath)) {
	    	// response.sendError(response.SC_NOT_FOUND);
	    	// return;
		// }
		// instead lets look for ".." in the absolute path
		// and disallow only that. 
		// Why should we loose out on symbolic links?
		//

		if(absPath.indexOf("..") != -1) {
			// We have .. in the path...
	    	response.sendError(response.SC_NOT_FOUND);
	    	return;
		}
	}

	String mimeType = contextF.getMimeType( file.getName() );

	if (mimeType == null) {
	    mimeType = "text/plain";
	}

	response.setContentType(mimeType);
	response.setContentLength((int)file.length());
	response.setDateHeader("Last-Modified", file.lastModified());

	FileInputStream in = new FileInputStream(file);

	try {
	    serveStream(in, request, response);
	} catch (FileNotFoundException e) {
	    // Figure out what we're serving

	    String requestURI = (String)request.getAttribute(
		Constants.Attribute.RequestURI);

   	    if (requestURI == null) {
	    	requestURI = request.getRequestURI();
	    }

	    response.sendError(response.SC_NOT_FOUND,
                "File Not Found<br>" + requestURI);
	} catch (SocketException e) {
	    return;  // munch
	} finally {
	    if (in != null) {
		in.close();
	    }
	}
    }

    private void serveStream(InputStream in, HttpServletRequest request,
        HttpServletResponse response)
    throws IOException {
	// XXX		
	// ok, here we are trying to figure out if the response has
	// already been started with a stream or a writer. We really
	// need to move these flags into the Request and Response objects
	// in web.core, but I don't want to suffer that big a hit right
	// before code freeze.
	// So, we take the preferred track (stream) first, and fall
	// back to writer.

	try {
	    ServletOutputStream out = response.getOutputStream();
	    serveStreamAsStream(in, out);
	} catch (IllegalStateException ise) {
	    PrintWriter out = response.getWriter();
	    serveStreamAsWriter(in, out);
	}
    }

    private void serveStreamAsStream(InputStream in, OutputStream out)
    throws IOException {
	byte[] buf = new byte[1024];
	int read = 0;

	while ((read = in.read(buf)) != -1) {
	    out.write(buf, 0, read);
	}
    }

    private void serveStreamAsWriter(InputStream in, PrintWriter out)
    throws IOException {
	InputStreamReader r = new InputStreamReader(in);
	char[] buf = new char[1024];
	int read = 0;

	while ((read = r.read(buf)) != -1) {
	    out.write(buf, 0, read);
	}
    }
    
    private boolean isFileMasked(String docBase, String requestedFile) {
        for (int i = 0; i < Constants.Context.MASKED_DIR.length; i++) {
            String maskFile = Constants.Context.MASKED_DIR[i];

            // case insensitive check
            if (requestedFile.toLowerCase().startsWith(
                    FileUtil.patch(docBase + maskFile).toLowerCase())) {
	        return true;
	    }
        }
        return false;
    }

    private boolean isDirMasked(String basedir, String subdir) {
        // In the future we could make sure to only mask the special
        // directories if they're rooted in the basedir.  That would
        // allow a WEB-INF dir to be served if it's not *the* WEB-INF for
        // example.
        // But to do that would cause a security breach when one context
        // contained another context, since the subcontext would have its
        // hidden dirs displayed.  So for now all masked dirs are masked.
        //
        for (int i = 0; i < Constants.Context.MASKED_DIR.length; i++) {
            if (subdir.equalsIgnoreCase(Constants.Context.MASKED_DIR[i])) {
                return true;
            }
        }
        return false;
    }

    private void serveDir(File file, HttpServletRequest request,
        HttpServletResponse response)
    throws IOException {
	// XXX
	// genericize this! put it into another class! especially
	// important as we should be able to dive into archives
	// and get this same kind of information in the furture.
	
	boolean shaderow = false;

	// Make sure that we don't let ../'s through

	String absPath = file.getAbsolutePath();
	String canPath = file.getCanonicalPath();

        // take care of File.getAbsolutePath() troubles on
        // jdk1.1.x/win

        absPath = FileUtil.patch(absPath);

	if (File.separatorChar  == '\\') { 
		// On Windows check ignore case....
		if(!absPath.equalsIgnoreCase(canPath)) {
		    response.sendError(response.SC_NOT_FOUND);
		    return;
		}
	} else {
		// The following code on Non Windows disallows ../ 
		// in the path but also disallows symlinks.... 
		// 
		// if(!absPath.equals(canPath)) {
	    	// response.sendError(response.SC_NOT_FOUND);
	    	// return;
		// }
		// instead lets look for ".." in the absolute path
		// and disallow only that. 
		// Why should we loose out on symbolic links?
		//

		if(absPath.indexOf("..") != -1) {
		    // We have .. in the path...
		    response.sendError(response.SC_NOT_FOUND);
		    return;
		}
	}

	Vector dirs = new Vector();
	Vector files = new Vector();
	String[] fileNames = file.list();
        String docBase = "";

        if (context.getDocumentBase().getProtocol().equalsIgnoreCase("war") &&
	    context.isWARExpanded()) {
	    String s = context.getWARDir().getAbsolutePath();

	    docBase = FileUtil.patch(s);
	} else {
	    docBase = context.getDocumentBase().getFile();
	}

        if (! docBase.endsWith("/")) {
            docBase += "/";
        }

	for (int i = 0; i < fileNames.length; i++) {
	    String fileName = fileNames[i];

	    File f = new File(file, fileName);

            // Make sure dir isn't masked
            if (f.isDirectory() && isDirMasked(docBase, fileName)) {
                continue;
            }

	    if (f.isDirectory()) {
                dirs.addElement(f);
	    } else {
		files.addElement(f);
	    }
	}
	
	// Pre-calculate the request URI for efficiency

	String requestURI = request.getRequestURI();

	// Make another URI that definitely ends with a /

	String slashedRequestURI = null;

	if (requestURI.endsWith("/")) {
	    slashedRequestURI = requestURI;
	} else {
	    slashedRequestURI = requestURI + "/";
	}

	// see if we are in an include

	boolean inInclude = false;
        Object o = request.getAttribute(Constants.Attribute.Dispatch);

	if (o != null) {
	    inInclude = true;
	}

	StringBuffer buf = new StringBuffer();

	if (! inInclude) {
	    response.setContentType("text/html");
	    buf.append("<html>\r\n");
	    buf.append("<head>\r\n");

	    // XXX
	    // i18n

	    buf.append("<title>Directory Listing for: " + requestURI);
	    buf.append("</title>\r\n</head><body bgcolor=white>\r\n");
	}

	buf.append("<table width=90% cellspacing=0 ");
	buf.append("cellpadding=5 align=center>");
	buf.append("<tr><td colspan=3><font size=+2><strong>");
	buf.append("Directory Listing for: " + requestURI);
	buf.append("</strong></td></tr>\r\n");

	if (! requestURI.equals("/")) {
	    buf.append("<tr><td colspan=3 bgcolor=#ffffff>");
	    //buf.append("<a href=\"../\">Up one directory");

	    String toPath = requestURI;

	    if (toPath.endsWith("/")) {
		toPath = toPath.substring(0, toPath.length() - 1);
	    }

	    toPath = toPath.substring(0, toPath.lastIndexOf("/"));

	    if (toPath.length() == 0) {
		toPath = "/";
	    }

	    buf.append("<a href=\"" + toPath + "\"><tt>Up to: " + toPath);
	    buf.append("</tt></a></td></tr>\r\n");
	}
	
	if (dirs.size() > 0) {
	    buf.append("<tr><td colspan=3 bgcolor=#cccccc>");
	    buf.append("<font size=+2><strong>Subdirectories:</strong>\r\n");
	    buf.append("</font></td></tr>\r\n");

	    Enumeration e = dirs.elements();

            while (e.hasMoreElements()) {
                File f = (File)e.nextElement();
                String fileName = f.getName();

                buf.append("<tr");

                if (shaderow) {
                    buf.append(" bgcolor=#eeeeee");
                    shaderow = false;
                } else {
                    shaderow = true;
                }

                buf.append("><td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;");
                buf.append("<tt><a href=\"" + slashedRequestURI +
                    fileName + "\">" + fileName +
                    "/</a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" +
                    "</tt>\r\n");
                buf.append("</td><td><tt>&nbsp;&nbsp;</tt></td>");
                buf.append("<td align=right><tt>");
                buf.append(dateFormat.format(new Date(f.lastModified())));
                buf.append("</tt></td></tr>\r\n");
            }

	    buf.append("\r\n");
	}

	shaderow = false;
	buf.append("<tr><td colspan=3 bgcolor=#ffffff>&nbsp;</td></tr>");

	if (files.size() > 0) {
	    buf.append("<tr><td colspan=4 bgcolor=#cccccc>");
	    buf.append("<font size=+2><strong>Files:</strong>");
	    buf.append("</font></td></tr>");

	    Enumeration e = files.elements();

	    while (e.hasMoreElements()) {
		buf.append("<tr");

		if (shaderow) {
		    buf.append(" bgcolor=#eeeeee");
		    shaderow = false;
		} else {
		    shaderow = true;
		}

		buf.append("><td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\r\n");

		File f = (File)e.nextElement();
		String fileName = f.getName();

		buf.append("<tt><a href=\"" + slashedRequestURI +
                    fileName + "\">" + fileName + "</a>");
		buf.append("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<tt>");
		buf.append("</td></td>\r\n<td align=right><tt>");

		int filesize = (int)f.length();
		int leftside = filesize / 1024;
		int rightside = (filesize % 1024) / 103;  // makes 1 digit

		// To avoid 0.0 for non-zero file, we bump to 0.1

		if (leftside == 0 && rightside == 0 && filesize != 0) {
		    rightside = 1;
		}

		buf.append(leftside + "." + rightside + " KB");
		buf.append("</tt></td>");
		buf.append("<td align=right><tt>");
		buf.append(dateFormat.format(new Date(f.lastModified())));
		buf.append("</tt></td></tr>\r\n");
	    }

	    buf.append("\r\n");
	}

	buf.append("<tr><td colspan=3 bgcolor=#ffffff>&nbsp;</td></tr>");
	buf.append("<tr><td colspan=3 bgcolor=#cccccc>");
	buf.append("<font size=-1>");
	buf.append(Constants.TOMCAT_NAME);
	buf.append(" v");
	buf.append(Constants.TOMCAT_VERSION);
	buf.append("</font></td></tr></table>");

	if (! inInclude) {
	    buf.append("</body></html>\r\n");
	}

	String output = buf.toString();

	byte[] bytes = output.getBytes();

	ByteArrayInputStream in = new ByteArrayInputStream(bytes);

	serveStream(in, request, response);
    }
}
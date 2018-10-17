if( request.remoteHost().toString() != null )


package org.apache.tomcat.modules.loggers;


import java.io.*;
import java.text.*;
import java.util.*;

import org.apache.tomcat.core.BaseInterceptor;
import org.apache.tomcat.core.ContextManager;
import org.apache.tomcat.core.Request;
import org.apache.tomcat.core.Response;
import org.apache.tomcat.core.TomcatException;


/** <p>This is a TomCat RequestInterceptor that creates log files
 * in the style of the Apache servers "AccessLog". It used by
 * embedding a line like the following into <code>server.xml</code>:</p>
 * <pre>
 *   &lt;RequestInterceptor
 *     className="org.apache.tomcat.logging.AccessLogInterceptor"
 *     logFile="logs/AccessLog" format="combined"/&gt;
 * </pre>
 * <p>Possible attributes of the above XML element are:
 * <table>
 *   <tr>
 *     <th valign="top">logFile</th>
 *     <td>Name of the logfile being generated. Defaults to "logs/AccessLog".
 *       Tomcat.home is prepended, if the file name is relative.</td>
 *   </tr>
 *   <tr>
 *     <th valign="top">flush</th>
 *     <td>An optional boolean attribute, that enables (value = "true")
 *       or disables (value="false", default) flushing the log file
 *       after every request. For performance reasons, you should
 *       not enable flushing unless you are debugging this class.
 *     </td>
 *   </tr>
 *   <tr>
 *     <th valign="top">format</th>
 *     <td>
 *       A string describing the logfile format. Possible values are
 *       "combined" (Apache httpd combined format, default), "common"
 *       (Apache httpd common format) or a format string like
 *       <pre>
 *         '%h %l %u %t "%r" %>s %b "%{Referer}" "%{User-Agent}"'
 *         '%h %l %u %t "%r" %>s %b'
 *       </pre>
 *       (The above examples are used when "combined" or "common"
 *       format is requested.) Possible patterns are:
 *       <table>
 *         <tr><th valign="top">%%</th>
 *           <td>The percent character itself</td>
 *         </tr>
 *         <tr>
 *           <th valign="top">%{var}</th>
 *           <td>The value of <code>request.getHeader("var")</code> or
 *             empty string for null.<td>
 *         </tr>
 *         <tr>
 *           <th valign="top">%b</th>
 *           <td>The value of <code>response.getContentLength()</code>.</td>
 *         </tr>
 *         <tr>
 *           <th valign="top">%h</th>
 *           <td>The value of <code>request.getRemoteHost()</code>.</td>
 *         </tr>
 *         <tr>
 *           <th valign="top">%l</th>
 *           <td>Should be the remote users name, as indicated by an
 *             identd lookup. Currently it is always "-".</td>
 *         </tr>
 *         <tr>
 *           <th valign="top">%r</th>
 *           <td>First line of the request submitted by the client, for
 *             example
 *             <pre>
 *               GET /index.html?frame=main HTTP/1.0
 *             </pre>
 *             The first line is rebuilt from the values of
 *             <code>request.getMethod()</code>,
 *             <code>request.getRequestURI()</code>,
 *             <code>request.getQueryString()</code> and
 *             <code>request.getProtocol()</code>. It should probably
 *             better be recorded while reading the headers.
 *           </td>
 *         </tr>
 *         <tr>
 *           <th valign="top">%s</th>
 *           <td>The value of <code>response.getStatus()</code>.</td>
 *         </tr>
 *         <tr>
 *           <th valign="top">%>s</th>
 *           <td>The value of <code>response.getStatus()</code>.
 *             Should differ between different internal requests, as
 *             Apache httpd does, but this is currently not supported.</td>
 *         </tr>
 *         <tr>
 *           <th valign="top">%t</th>
 *           <td>The current time and date in the format
 *             <pre>
 *               [20/Apr/2001:19:45:23 0200]
 *             </pre>
 *           </td>
 *         </tr>
 *         <tr>
 *           <th valign="top">%u</th>
 *           <td>The value of <code>request.getRemoteUser()</code> or
 *             "-" for null.</td>.
 *         </tr>
 *         <tr>
 *       </table>
 *     </td>
 *   </tr> 
 * </table>
 * </p>
 *
 * @author  Jochen Wiedmann, jochen.wiedmann@softwareag.com
 */
public class AccessLogInterceptor extends BaseInterceptor {
    private static final String LOGFORMAT_COMBINED = "%h %l %u %t \"%r\" %>s %b \"%{Referer}\" \"%{User-Agent}\"";
    private static final String LOGFORMAT_COMMON = "%h %l %u %t \"%r\" %>s %b";
    private static FileWriter fw = null;
    private static String fileName = "logs/AccessLog";
    private static boolean useFlush = false;
    private static String logformat = LOGFORMAT_COMBINED;
    private static DateFormat df = new SimpleDateFormat("dd/MMM/yyyy:HH:mm:ss");
    
    /** Creates a new AccessLogInterceptor */
    public AccessLogInterceptor() {}
    
    /** <p>Sets the logfile name.</p>
     */
    public static void setLogFile(String logFile) {
	synchronized (AccessLogInterceptor.class) {
	    fileName = logFile;
	}
    }
    
    /** <p>Enables (true) or disables (false, default) flushing
     * the log file after any request.</p>
     */
    public static void setFlush(boolean flush) {
	synchronized (AccessLogInterceptor.class) {
	    useFlush = flush;
	}
    }
    
    /** <p>Sets the logfile format.</p>
     */
    public static void setFormat(String format) {
	synchronized (AccessLogInterceptor.class) {
	    if (format.equalsIgnoreCase("combined")) {
		logformat = LOGFORMAT_COMBINED;
	    } else if (format.equalsIgnoreCase("common")) {
		logformat = LOGFORMAT_COMMON;
	    } else {
		logformat = format;
	    }
	}
    }
    
    /** <p>This method <strong>must</strong> be called while
     * synchronizing on <code>AccessLogIntercepror.class</code>!</p>
     */
    private FileWriter getFileWriter() {
	if (fw != null) {
	    return fw;
	}
	if (fileName != null) {
	    try {
		File f = new File(fileName);
		if (!f.isAbsolute()) {
		    f=new File( cm.getHome());
		    f=new File( f, fileName );
		    //f = cm.getAbsolute(f);
		}
		fw = new FileWriter(f.getAbsolutePath(), true);
	    } catch (IOException e) {
		e.printStackTrace(System.err);
	    }
	}
	return fw;
    }
    
    /** <p>This method is actually creating an entry in the log file.</p>
     */
    public int beforeCommit(Request request, Response response) {
	synchronized (AccessLogInterceptor.class) {
	    FileWriter fw = getFileWriter();
	    if (fw != null) {
		try {
		    for (int i = 0;  i < logformat.length();  i++) {
			char c = logformat.charAt(i);
			if (c == '%'  &&  ++i < logformat.length()) {
			    c = logformat.charAt(i);
			    switch (c) {
			    case 'h':
				if( reqest.remoteHost().toString() != null )
				    fw.write(request.remoteHost().toString());
				else
				    fw.write( "DEFAULT" );
				break;
			    case 'l':
				fw.write('-');
				break; // identd not supported
			    case 'u':
				String user = request.getRemoteUser();
				fw.write(user == null ? "-" : user);
				break;
			    case 't':
				Calendar cal =
				    Calendar.getInstance();
				fw.write('[');
				fw.write(df.format(cal.getTime()));
				fw.write(' ');
				long millis =
				    cal.get(Calendar.ZONE_OFFSET) +
				    cal.get(Calendar.DST_OFFSET);
				String msecstr =
				    Long.toString((millis+60*500)/(60*1000));
				for (int j = msecstr.length();  j < 4;  j++) {
				    fw.write('0');
				}
				fw.write(msecstr);
				fw.write(']');
				break;
			    case 'r':
				fw.write(request.method().toString());
				fw.write(' ');
				fw.write(request.requestURI().toString());
				String q = request.queryString().toString();
				if (q != null) {
				    fw.write('?');
				    fw.write(q);
				}
				fw.write(' ');
				fw.write(request.protocol().toString().trim());
				break;
			    case 'b':
				fw.write(response.getMimeHeaders().
					 getHeader("Content-Length"));
				break;
			    case 's':
				fw.write(Integer.
					 toString(response.getStatus()));
				break;
			    case '>':
				if (++i < logformat.length()) {
				    c = logformat.charAt(i);
				    if (c == 's') {
					fw.write(Integer.toString(response.getStatus()));
				    } else {
					fw.write('>');
					fw.write(c);
				    }
				} else {
				    fw.write(c);
				}
				break;
			    case '{':
				int offset = logformat.indexOf('}', i);
				if (offset == -1) {
				    fw.write(c);
				} else {
				    String var =
					logformat.substring(i+1, offset);
				    String val = request.getHeader(var);
				    if (val != null) {
					fw.write(val);
				    }
				    i = offset;
				}
				break;
			    default:  fw.write(c); break;
			    } 
			} else {
			    fw.write(c);
			}
		    }
		    fw.write('\n');
		    if (useFlush) {
			fw.flush();
		    }
		} catch (IOException e) {
		}
	    }
	}
	return 0;
    }

    public void engineShutdown(ContextManager cm) throws TomcatException {
	// From: Mike Schrag <mschrag@cavtel.net> 
	try {
	    getFileWriter().flush();
	    getFileWriter().close();
	} catch (IOException e) {
	    e.printStackTrace();
	}
    }
}
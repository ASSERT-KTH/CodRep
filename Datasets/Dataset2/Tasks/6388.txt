public static final char[] NEWLINE=separator.toCharArray();

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
 */ 
package org.apache.tomcat.util.log;

import java.io.Writer;
import java.io.PrintWriter;
import java.io.OutputStreamWriter;
import java.io.FileWriter;
import java.io.File;
import java.io.IOException;
import java.io.StringWriter;
import java.lang.reflect.*;

import java.util.*;
import java.text.DateFormat;
import java.text.SimpleDateFormat;

// import javax.servlet.ServletException;	// for throwableToString()
// import org.apache.tomcat.core.TomcatException;	// for throwableToString()
import org.apache.tomcat.util.FastDateFormat;

/**
 * Interface for a logging object. A logging object provides mechanism
 * for logging errors and messages that are of interest to someone who
 * is trying to monitor the system.
 * 
 * @author Anil Vijendran (akv@eng.sun.com)
 * @author Alex Chaffee (alex@jguru.com)
 * @since  Tomcat 3.1
 */
public abstract class Logger {
    // ----- static content -----
    
    /**
     * Verbosity level codes.
     */
    public static final int FATAL = Integer.MIN_VALUE;
    public static final int ERROR = 1;
    public static final int WARNING = 2;
    public static final int INFORMATION = 3;
    public static final int DEBUG = 4;

    // -------------------- Internal fields --------------------

    protected static Writer defaultSink = new OutputStreamWriter(System.err);

    // registered loggers 
    protected static Hashtable loggers = new Hashtable(5);
    // default logger
    public static Logger defaultLogger = new DefaultLogger();
    static {
	defaultLogger.setVerbosityLevel(DEBUG);
    }
      
    // Usefull for subclasses
    private static final String separator = System.getProperty("line.separator", "\n");
    public static final char[] NEWLINE=separator.toCharArray();;


    /**
     * Prints the log message on a specified logger. 
     *
     * @param	name		the name of the logger. 
     * @param	message		the message to log. 
     * @param	verbosityLevel	what type of message is this? 
     *				(WARNING/DEBUG/INFO etc)
     */
    /*
      public static void log(String logName, String message, 
			   int verbosityLevel) 
    {
	Logger logger = getLogger(logName);
	if (logger != null)
	    logger.log(message, verbosityLevel);
    }
    */
    
    /**
     * Prints the log message on a specified logger at the "default"
     * log leve: INFORMATION
     *
     * @param	name		the name of the logger. 
     * @param	message		the message to log. 
     */
    /*
      public static void log(String logName, String message)
    {
	Logger logger = getLogger(logName);
	if (logger != null)
	    logger.log(message);
    }
    */
    
    /**
     * Set the default output stream that is used by all logging
     * channels. 
     * 
     * @param	w		the default output stream. 
     */
    public static void setDefaultSink(Writer w) {
	defaultSink = w;
    }

    public static Logger getLogger(String name) {
	return (Logger) loggers.get(name);
    }

    /**
     * Get the logger that prints to the default sink
     * (usu. System.err)
     **/
    public static Logger getDefaultLogger() {
	return defaultLogger;
    }

    public static Enumeration getLoggerNames() {
	return loggers.keys();
    }

    public static void putLogger(Logger logger) {	
	loggers.put(logger.getName(), logger);	
    }

    public static void removeLogger(Logger logger) {
	loggers.remove(logger.getName());
    }

    /**
     * Converts a Throwable to a printable stack trace, including the
     * nested root cause for a ServletException or TomcatException if
     * applicable
     * TODO: JDBCException too
     * 
     * @param t any Throwable, or ServletException, or null
     **/
    public static String throwableToString( Throwable t ) {
	// we could use a StringManager here to get the
	// localized translation of "Root cause:" , but
	// since it's going into a log, no user will see
	// it, and it's desirable that the log file is
	// predictable, so just use English
	return throwableToString( t, "Root cause:" );
    }

    public static final int MAX_THROWABLE_DEPTH=3;
    
    /**
     * Converts a Throwable to a printable stack trace, including the
     * nested root cause for a ServletException or TomcatException or
     * SQLException if applicable
     * 
     * @param t any Throwable, or ServletException, or null
     * @param rootcause localized string equivalent of "Root Cause"
     **/
    public static String throwableToString( Throwable t, String rootcause ) {
	if (rootcause == null)
	    rootcause = "Root Cause:";
	StringWriter sw = new StringWriter();
	PrintWriter w = new PrintWriter(sw);
	printThrowable(w, t, rootcause, MAX_THROWABLE_DEPTH);
	w.flush();
	return sw.toString();
    }

    private static Object emptyObjectArray[]=new Object[0];

    private static void printThrowable(PrintWriter w, Throwable t, String rootcause, int depth ) {
	if (t != null) {
	    // XXX XXX XXX Something seems wrong - DOS, permissions. Need to
	    // check.
	    t.printStackTrace(w);

	    // Find chained exception using few general patterns
	    
	    Class tC=t.getClass();
	    Method mA[]= tC.getMethods();
	    Method nextThrowableMethod=null;
	    for( int i=0; i< mA.length ; i++  ) {
		if( "getRootCause".equals( mA[i].getName() )
		    || "getNextException".equals( mA[i].getName() )
		    || "getException".equals( mA[i].getName() )) {
		    // check param types
		    Class params[]=mA[i].getParameterTypes();
		    if( params==null || params.length==0 ) {
			nextThrowableMethod=mA[i];
			break;
		    }
		}
	    }

	    if( nextThrowableMethod != null ) {
		try {
		    Throwable nextT=(Throwable)nextThrowableMethod.invoke( t , emptyObjectArray );
		    if( nextT != null ) {
			w.println(rootcause);
			if( depth > 0 ) {
			    printThrowable(w, nextT, rootcause, depth-1);
			}
		    }
		} catch( Exception ex ) {
		    // ignore
		}
	    }
	}
    }
    
    /**
     * General purpose nasty hack to determine if an exception can be
     * safely ignored -- specifically, if it's an IOException or
     * SocketException that is thrown in the normal course of a socket
     * closing halfway through a connection, or if it's a weird
     * unknown type of exception.  This is an intractable problem, and
     * this is a bad solution, but at least it's centralized.
     **/
    public static boolean canIgnore(Throwable t) {
	String msg = t.getMessage();
	if (t instanceof java.io.InterruptedIOException) {
	    return true;
	}
	else if (t instanceof java.io.IOException) {
	    // Streams throw Broken Pipe exceptions if their
	    // underlying sockets close
	    if( "Broken pipe".equals(msg))
		return true;
	}
	else if (t instanceof java.net.SocketException) {
	    // TCP stacks can throw SocketExceptions when the client
	    // disconnects.  We don't want this to shut down the
	    // endpoint, so ignore it. Is there a more robust
	    // solution?  Should we compare the message string to
	    // "Connection reset by peer"?
	    return true;
	}
	return false;
    }


    // ----- instance (non-static) content -----
    
    protected boolean custom = true;
    protected Writer sink = defaultSink;
    String path;
    protected String name;
    
    private int level = WARNING;

    /**
     * Should we timestamp this log at all?
     **/
    protected boolean timestamp = true;

    /**
     * true = The timestamp format is raw msec-since-epoch <br>
     * false = The timestamp format is a custom string to pass to SimpleDateFormat
     **/
    protected boolean timestampRaw = false;

    /**
     * The timestamp format string, default is "yyyy-MM-dd hh:mm:ss"
     **/
    protected String timestampFormat = "yyyy-MM-dd hh:mm:ss";

    protected DateFormat timestampFormatter
	= new FastDateFormat(new SimpleDateFormat(timestampFormat));
    
    /**
     * Is this Log usable?
     */
    public boolean isOpen() {
	return this.sink != null;
    }

    /**
     * Prints the log message at the "default" log level: INFORMATION
     * 
     * @param	message		the message to log.
     */
    public final void log(String message) {
	log(message, Logger.INFORMATION);
    }
        
    /**
     * Prints the log message.
     * 
     * @param	message		the message to log.
     * @param	verbosityLevel	what type of message is this?
     * 				(WARNING/DEBUG/INFO etc)
     */
    public final void log(String message, int verbosityLevel) {
	log(message, null, level);
    }

    /**
     * Prints log message and stack trace, with verbosityLevel ERROR.
     * This makes the assumption that throwables are exceptions which
     * are errors by nature; if you disagree, you can always call
     * log(msg, t, Logger.INFORMATION) or whatever.
     *
     * @param	message		the message to log. 
     * @param t the exception that was thrown.  */
    public final void log(String message, Throwable t)
    {
	log(message, t, ERROR);
    }
    
    /**
     * Prints log message and stack trace.
     *
     * @param	message		the message to log. 
     * @param	t		the exception that was thrown.
     * @param	verbosityLevel	what type of message is this?
     * 				(WARNING/DEBUG/INFO etc)
     */
    public final void log(String message, Throwable t, 
			  int verbosityLevel) 
    {
	if (matchVerbosityLevel(verbosityLevel)) {
	    if (t == null) {
		realLog(message);
	    }
	    else {
		realLog(message, t);
	    }
	}
    }

    public boolean matchVerbosityLevel(int verbosityLevel) {
	return verbosityLevel <= getVerbosityLevel();
    }
    
    /**
     * Subclasses implement these methods which are called by the
     * log(..) methods internally.
     *
     * @param	message		the message to log.
     */
    protected abstract void realLog(String message);

    /** 
     * Subclasses implement these methods which are called by the
     * log(..) methods internally. 
     *
     * @param	message		the message to log. 
     * @param	t		the exception that was thrown.
     */
    protected abstract void realLog(String message, Throwable t);
    
    /**
     * Flush the log. 
     */
    public abstract void flush();


    /**
     * Close the log. 
     */
    public synchronized void close() {
	this.sink = null;
	loggers.remove(getName());
    }
    
    /**
     * Get name of this log channel. 
     */
    public String getName() {
	return this.name;
    }

    /**
     * Set name of this log channel.
     *
     * @param	name		Name of this logger. 
     */
    public void setName(String name) {
	this.name = name;

	// Once the name of this logger is set, we add it to the list
	// of loggers... 
	putLogger(this);
    }

    /**
     * Set the path name for the log output file.
     * 
     * @param	path		The path to the log file. 
     */
    public void setPath(String path) {
        if (File.separatorChar == '/')
            this.path = path.replace('\\', '/');
        else if (File.separatorChar == '\\')
            this.path = path.replace('/', '\\');
    }

    public String getPath() {
	return path;
    }

    public String toString() {
	return "Logger(" + getName() + ", " + getPath() + ")";
    }

    /** Open the log - will create the log file and all the parent directories.
     *  You must open the logger before use, or it will write to System.err
     */
    public void open() {
	if (path == null) 
            return;
	// use default sink == System.err
	try {
	    File file = new File(path);
	    
	    if (!file.exists())
		new File(file.getParent()).mkdirs();
	    
	    this.sink = new FileWriter(path);
	} catch (IOException ex) {
	    System.err.print("Unable to open log file: "+path+"! ");
	    System.err.println(" Using stderr as the default.");
	    this.sink = defaultSink;
	}
    }

    

    /**
     * Set the verbosity level for this logger. This controls how the
     * logs will be filtered. 
     *
     * @param	level		one of the verbosity level strings. 
     */
    public void setVerbosityLevel(String level) {
	if ("warning".equalsIgnoreCase(level))
	    this.level = WARNING;
	else if ("fatal".equalsIgnoreCase(level))
	    this.level = FATAL;
	else if ("error".equalsIgnoreCase(level))
	    this.level = ERROR;
	else if ("information".equalsIgnoreCase(level))
	    this.level = INFORMATION;
	else if ("debug".equalsIgnoreCase(level))
	    this.level = DEBUG;
    }

    /**
     * Set the verbosity level for this logger. This controls how the
     * logs will be filtered. 
     *
     * @param	level		one of the verbosity level codes. 
     */
    public void setVerbosityLevel(int level) {
	this.level = level;
    }
    
    /**
     * Get the current verbosity level. 
     */
    public int getVerbosityLevel() {
	return this.level;
    }

    /**
     * Do we need to time stamp this or not?
     *
     * @param	value		"yes/no" or "true/false"
     */
    public void setTimestamp(String value) {
	if ("true".equalsIgnoreCase(value) || "yes".equalsIgnoreCase(value))
	    timestamp = true;
	else if ("false".equalsIgnoreCase(value) || "no".equalsIgnoreCase(value))
	    timestamp = false;
    }

    public  boolean isTimestamp() {
	return timestamp;
    }

    /**
     * If we are timestamping at all, what format do we use to print
     * the timestamp? See java.text.SimpleDateFormat.
     *
     * Default = "yyyy-MM-dd hh:mm:ss". Special case: "msec" => raw
     * number of msec since epoch, very efficient but not
     * user-friendly
     **/
    public void setTimestampFormat(String value)
    {
	if (value.equalsIgnoreCase("msec"))
	    timestampRaw = true;
	else {
	    timestampRaw = false;
	    timestampFormat = value;
	    timestampFormatter =
		new FastDateFormat(new SimpleDateFormat(timestampFormat));
	}
    }
    
    public String getTimestampFormat()
    {
	if (timestampRaw)
	    return "msec";
	else
	    return timestampFormat;
    }
    
//     public void setCustomOutput( String value ) {
// 	if ("true".equalsIgnoreCase(value) || "yes".equalsIgnoreCase(value))
// 	    custom = true;
// 	else if ("false".equalsIgnoreCase(value) || "no".equalsIgnoreCase(value))
// 	    custom = false;
//     }

    protected String formatTimestamp(long msec) {
	StringBuffer buf = new StringBuffer();
	formatTimestamp(msec, buf);
	return buf.toString();
    }

    // dummy variable to make SimpleDateFormat work right
    private static java.text.FieldPosition position = new java.text.FieldPosition(DateFormat.YEAR_FIELD);
    
    protected void formatTimestamp(long msec, StringBuffer buf) {
	if (timestamp == false)
	    return;
	else if (timestampRaw) {
	    buf.append(Long.toString(msec));
	    return;
	}
	else {
	    Date d = new Date(msec);
	    timestampFormatter.format(d, buf, position);
	    return;
	}
    }
    
    // ----- Logger.Helper static inner class -----
    
}
String verbosityLevel="INFORMATION";

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

package org.apache.tomcat.modules.config;

import org.apache.tomcat.core.*;
import org.apache.tomcat.util.log.*;
import org.apache.tomcat.util.qlog.*;
import org.apache.tomcat.util.io.FileUtil;
import java.io.*;
import java.net.*;
import java.util.*;

/*
  Logging in Tomcat is quite flexible; we can either have a log
  file per module (example: ContextManager) or we can have one
  for Servlets and one for Jasper, or we can just have one
  tomcat.log for both Servlet and Jasper.  Right now there are
  three standard log streams, "tc_log", "servlet_log", and
  "JASPER_LOG".  
  
  Path: 
  
  The file to which to output this log, relative to
  TOMCAT_HOME.  If you omit a "path" value, then stderr or
  stdout will be used.
  
  Verbosity: 
  
  Threshold for which types of messages are displayed in the
  log.  Levels are inclusive; that is, "WARNING" level displays
  any log message marked as warning, error, or fatal.  Default
  level is WARNING.  Note: servlet_log must be level
  INFORMATION in order to see normal servlet log messages.
  
  verbosityLevel values can be: 
  FATAL
  ERROR
  WARNING 
  INFORMATION
  DEBUG

  Timestamps:
  
  By default, logs print a timestamp in the form "yyyy-MM-dd
  hh:mm:ss" in front of each message.  To disable timestamps
  completely, set 'timestamp="no"'. To use the raw
  msec-since-epoch, which is more efficient, set
  'timestampFormat="msec"'.  If you want a custom format, you
  can use 'timestampFormat="hh:mm:ss"' following the syntax of
  java.text.SimpleDateFormat (see Javadoc API).  For a
  production environment, we recommend turning timestamps off,
  or setting the format to "msec".
  
  Custom Output:
  
  "Custom" means "normal looking".  "Non-custom" means
  "surrounded with funny xml tags".  In preparation for
  possibly disposing of "custom" altogether, now the default is
  'custom="yes"' (i.e. no tags)
  
  Per-component Debugging:
  
  Some components accept a "debug" attribute.  This further
  enhances log output.  If you set the "debug" level for a
  component, it may output extra debugging information.
*/


/**
 *  Define a logger with the specified name, using the logger
 *  implementation in org.apache.tomcat.util.log.QueueLogger
 *
 *  Tomcat uses the util.log.Log class - if you want to use
 *  a different logger ( like log4j or jsrXXX ) you need to create a
 *  new interceptor that will use your favorite logger and
 *  create a small adapter ( class extending Log and directing
 *  the output to your favorite logger.
 *
 *  The only contract used in tomcat for logging is the util.Log.
 * 
 */
public class LogSetter extends  BaseInterceptor {
    String name;
    String path;
    String verbosityLevel;
    boolean servletLogger=false;
    boolean timestamps=true;
    String tsFormat=null;
    
    public LogSetter() {
    }

    /** Set the name of the logger.
     *  Predefined names are: tc_log, servlet_log, JASPER_LOG.
     */
    public void setName( String s ) {
	name=s;
    }

    public void setPath( String s ) {
	path=s;
    }

    public void setVerbosityLevel( String s ) {
	verbosityLevel=s;
    }

    /** This logger will be used for servlet's log.
     *  ( if not set, the logger will output tomcat messages )
     */
    public void setServletLogger( boolean b ) {
	servletLogger=b;
    }

    /** Display the time of the event ( log ).
     */
    public void setTimestamps( boolean b ) {
	timestamps=b;
    }

    /** Set the format of the timestamp.
	"msec" will display the raw time ( fastest ),
	otherwise a SimpleDateFormat.
    */
    public void setTimestampFormat( String s ) {
	tsFormat=s;
    }
    
    /**
     *  The log will be added and opened as soon as the module is
     *  added to the server
     */
    public void addInterceptor(ContextManager cm, Context ctx,
			       BaseInterceptor module)
	throws TomcatException
    {
	if( module!=this ) return;

	LogManager logManager=(LogManager)cm.getNote("tc.LogManager");
	
	// Log will redirect all Log.getLog to us
	if( logManager==null ) {
	    logManager=new TomcatLogManager();
	    cm.setNote("tc.LogManager", logManager);
	    Log.setLogManager( logManager );
	}

	LogDaemon logDaemon=(LogDaemon)cm.getNote("tc.LogDaemon");
	if( logDaemon==null ) {
	    logDaemon=new LogDaemon();
	    cm.setNote( "tc.LogDaemon", logDaemon );
	    logDaemon.start();
	}
	
	if( name==null ) {
	    if( servletLogger )
		name="org/apache/tomcat/facade";
	    else
		name="org/apache/tomcat/core";
	}

	if( path!=null && ! FileUtil.isAbsolute( path ) ) {
	    File wd= new File(cm.getHome(), path);
	    path= wd.getAbsolutePath();
	}
	
	// workarounds for legacy log names
	if( "tc_log".equals( name ) )
	    name="org/apache/tomcat/core";
	if( servletLogger || "servlet_log".equals( name ) )
	    name="org/apache/tomcat/facade";

	if( ctx != null ) {
	    // this logger is local to a context
	    name=name +  "/"  + ctx.getId();
	}

	createLogger(logManager, logDaemon );
	
    }

    public void engineInit( ContextManager cm )
	throws TomcatException
    {
	// make sure it's started
	LogDaemon logDaemon=(LogDaemon)cm.getNote("tc.LogDaemon");
	logDaemon.start();
    }

    public void engineShutdown(ContextManager cm)
	throws TomcatException
    {
	if( getContext() != null )
	    return;
	
	cm.getLog().flush();
	// engineShutdown shouldn't be called on local modules anyway !

	LogDaemon logDaemon=(LogDaemon)cm.getNote("tc.LogDaemon");
	if( logDaemon!=null ) {
	    try{ 
		logDaemon.stop();
	    } catch( Exception ex ) {
		ex.printStackTrace();
	    }
	    //	    cm.setNote( "tc.LogDaemon", null );
	}

    }



    
    /** Set default ServletLog for Context if necessary
     */

    public void addContext( ContextManager cm, Context ctx )
	throws TomcatException
    {
	if( "org/apache/tomcat/facade".equals( name ) &&
		    ctx.getServletLog() == null ) {
	    ctx.setServletLog( Log.getLog( name, ctx.getId() ) );
	}
    }

    /** Adapter and registry for QueueLoggers
     */
    static class TomcatLogManager extends LogManager {


    }

    
    private void createLogger(LogManager logManager, LogDaemon logDaemon) {
	
	if( debug>0) 
	    log( "Constructing logger " + name + " " + path + " " + ctx );
	
	QueueLogger ql=new QueueLogger();
	ql.setLogDaemon( logDaemon );
	if( ! timestamps )
	    ql.setTimestamp( "false" );
	if( tsFormat!=null )
	    ql.setTimestampFormat( tsFormat );
	
	if( path!=null )
	    ql.setPath(path);
	if( verbosityLevel!= null )
	    ql.setVerbosityLevel(verbosityLevel);

	ql.open();

	logManager.addChannel( name, ql );

	if( "org/apache/tomcat/core".equals( name ) ) {
	    // this will be the Log interface to the log we just created
	    // ( the way logs and channels are created is a bit
	    // complicated - work for later )
	    cm.setLog( Log.getLog( name, "ContextManager"));
	}

	if( ctx!=null ) {
	    if( servletLogger ) {
		ctx.setServletLog( Log.getLog( name, ctx.getId() ) );
	    } else {
		ctx.setLog( Log.getLog( name, ctx.getId() ) );
	    }
	}  
    }
}
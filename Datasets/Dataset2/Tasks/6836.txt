else if (File.separatorChar == '\\')

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
package org.apache.tomcat.logging;

import java.io.Writer;
import java.io.PrintWriter;
import java.io.FileWriter;
import java.io.File;
import java.io.IOException;

import java.util.*;

/**
 * Interface for a logging object. A logging object provides mechanism
 * for logging errors and messages that are of interest to someone who
 * is trying to monitor the system.
 * 
 * @author Anil Vijendran (akv@eng.sun.com)
 * @since  Tomcat 3.1
 */
public abstract class Logger {

    /**
     * Is this Log usable?
     */
    public boolean isOpen() {
	return this.sink != null;
    }

    /**
     * Prints the log message on a specified logger. 
     *
     * @param	name		the name of the logger. 
     * @param	message		the message to log. 
     * @param	verbosityLevel	what type of message is this? 
     *				(WARNING/DEBUG/INFO etc)
     */
    public static void log(String logName, String message, 
			   int verbosityLevel) 
    {
	Logger logger = getLogger(logName);
	if (logger != null)
	    logger.log(message, verbosityLevel);
    }

    /**
     * Prints the log message on a specified logger at the "default"
     * log leve: INFORMATION
     *
     * @param	name		the name of the logger. 
     * @param	message		the message to log. 
     */
    public static void log(String logName, String message)
    {
	Logger logger = getLogger(logName);
	if (logger != null)
	    logger.log(message);
    }
    
     
    /**
     * Prints the log message.
     * 
     * @param	message		the message to log.
     * @param	verbosityLevel	what type of message is this?
     * 				(WARNING/DEBUG/INFO etc)
     */
    public final void log(String message, int verbosityLevel) {
	if (matchVerbosityLevel(verbosityLevel))
	    realLog(message);
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
	if (matchVerbosityLevel(verbosityLevel))
	    realLog(message, t);
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
        else if (File.separatorChar = '\\')
            this.path = path.replace('/', '\\');
    }

    public String getPath() {
	return path;
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
     * Verbosity level codes.
     */
    public static final int FATAL = Integer.MIN_VALUE;
    public static final int ERROR = 1;
    public static final int WARNING = 2;
    public static final int INFORMATION = 3;
    public static final int DEBUG = 4;
    

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
	    timeStamp = true;
	else if ("false".equalsIgnoreCase(value) || "no".equalsIgnoreCase(value))
	    timeStamp = false;
    }

    public  boolean isTimestamp() {
	return timeStamp;
    }
    
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

    public static Enumeration getLoggerNames() {
	return loggers.keys();
    }

    public static void putLogger(Logger logger) {
	loggers.put(logger.getName(), logger);
    }

    public static void removeLogger(Logger logger) {
	loggers.remove(logger.getName());
    }

    public void setCustomOutput( String value ) {
	if ("true".equalsIgnoreCase(value) || "yes".equalsIgnoreCase(value))
	    custom = true;
	else if ("false".equalsIgnoreCase(value) || "no".equalsIgnoreCase(value))
	    custom = false;
    }

    protected boolean custom;
    protected Writer sink = defaultSink;
    String path;
    protected String name;
    
    protected static Writer defaultSink = new PrintWriter(System.err);
    protected static Hashtable loggers = new Hashtable(5);

    private int level = WARNING;
    protected boolean timeStamp = true;
}
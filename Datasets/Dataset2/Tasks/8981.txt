import org.apache.tomcat.util.collections.Queue;

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
import java.io.StringWriter;
import java.io.PrintWriter;

import java.util.Date;

import org.apache.tomcat.util.Queue;

/**
 * A real implementation of the Logger abstraction.
 * It uses a log queue, so that the caller will not
 * have to wait.
 *
 * @author Anil V (akv@eng.sun.com)
 * @since  Tomcat 3.1
 */
public class QueueLogger extends Logger {
    /**
     * Just one daemon and one queue for all Logger instances.. 
     */
    static LogDaemon logDaemon = null;
    static Queue     logQueue  = null;

    public QueueLogger() {
	if (logDaemon == null || logQueue == null) {
	    logQueue = new Queue();
	    logDaemon = new LogDaemon(logQueue);
	    logDaemon.start();
	}
    }
    
    /**
     * Adds a log message to the queue and returns immediately. The
     * logger daemon thread will pick it up later and actually print
     * it out.
     * 
     * @param	message		the message to log.
     */
    final protected void realLog(String message) {
	realLog( message, null );
    }
    
    /**
     * Adds a log message and stack trace to the queue and returns
     * immediately. The logger daemon thread will pick it up later and
     * actually print it out. 
     *
     * @param	message		the message to log. 
     * @param	t		the exception that was thrown.
     */
    final protected void realLog(String message, Throwable t) {
	if( timestamp )
	    logQueue.put(new LogEntry(this,
				      System.currentTimeMillis(),
				      message, t));
	else
	    logQueue.put(new LogEntry(this,
				      message, t));
    }
    
    /**
     * Flush the log. In a separate thread, no wait for the caller.
     */
    public void flush() {
	logDaemon.flush();
    }

    public String toString() {
	return "QueueLogger(" + getName() + ", " + getPath() + ")";
    }
}
/**
 * The daemon thread that looks in a queue and if it is not empty
 * writes out everything in the queue to the sink.
 */
final class LogDaemon extends Thread {
    private Queue logQueue;
    
    LogDaemon(Queue logQueue) {
	this.logQueue = logQueue;
	setDaemon(true);
    }
	
    private static final char[] NEWLINE=Logger.NEWLINE;
    
    // There is only one thread, so we can reuse this
    char outBuffer[]=new char[512]; // resize
    
    // NEVER call toString() on StringBuffer!!!!!
    StringBuffer outSB = new StringBuffer();
    
    
    private void emptyQueue() {
	do {
	    LogEntry logEntry =
		(LogEntry) logQueue.pull();
	    QueueLogger tl=logEntry.l;
		Writer writer=tl.sink;
		if (writer != null) {
		    try {
			outSB.setLength(0);
			
			logEntry.print( outSB );
			outSB.append( NEWLINE );
			
			int len=outSB.length();
			if( len > outBuffer.length ) {
			    outBuffer=new char[len];
			}
			outSB.getChars(0, len, outBuffer, 0);

			writer.write( outBuffer, 0, len );	    
			writer.flush();
		    } catch (Exception ex) { // IOException
			ex.printStackTrace(); // nowhere else to write it
		    }
		}
	} while (!LogDaemon.this.logQueue.isEmpty());
    }

    public void run() {
	while (true) {
	    emptyQueue();
	}
    }
    
    /** Flush the queue - in a separate thread, so that
	caller doesn't have to wait
    */
    public void flush() {
	Thread workerThread = new Thread(flusher);
	workerThread.start();
    }
    
    Runnable flusher = new Runnable() {
	    public void run() {
		emptyQueue();
	    }
	};
}

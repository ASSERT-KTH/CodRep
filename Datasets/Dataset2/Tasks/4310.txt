BaseInterceptor ci[]=cm.getContainer().getInterceptors();

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
package org.apache.tomcat.task;

import org.apache.tomcat.core.*;
import org.apache.tomcat.util.*;
import org.apache.tomcat.helper.*;
import org.apache.tomcat.util.xml.*;
import org.apache.tomcat.util.log.*;
import java.io.*;
import java.net.*;
import java.util.*;

// Used to stop tomcat
import org.apache.tomcat.service.PoolTcpConnector;
import org.apache.tomcat.service.connector.Ajp12ConnectionHandler;
import org.apache.tomcat.modules.server.Ajp12Interceptor;

/**
 * This task will stop tomcat
 *
 * @author Costin Manolache
 */
public class StopTomcat { 
    static final String DEFAULT_CONFIG="conf/server.xml";
    private static StringManager sm =
	StringManager.getManager("org.apache.tomcat.resources");

    String configFile;
    String tomcatHome;
    Log loghelper = new Log("tc_log", "StopTomcat");
    
    public StopTomcat() 
    {
    }

    // -------------------- Parameters --------------------

    public void setConfig( String s ) {
	configFile=s;
    }

    /** -f option
     */
    public void setF( String s ) {
	configFile=s;
    }

    public void setH( String s ) {
	tomcatHome=s;
	System.getProperties().put("tomcat.home", s);
    }

    public void setHome( String s ) {
	tomcatHome=s;
	System.getProperties().put("tomcat.home", s);
    }

    // -------------------- Ant execute --------------------
    public void execute() throws Exception {
	System.out.println(sm.getString("tomcat.stop"));
	try {
	    stopTomcat(); // stop serving
	}
	catch (TomcatException te) {
	    if (te.getRootCause() instanceof java.net.ConnectException)
		System.out.println(sm.getString("tomcat.connectexception"));
	    else
		throw te;
	}
	return;
    }

    // -------------------- Implementation --------------------
    
    /** Stop tomcat using the configured cm
     *  The manager is set up using the same configuration file, so
     *  it will have the same port as the original instance ( no need
     *  for a "log" file).
     *  It uses the Ajp12 connector, which has a built-in "stop" method,
     *  that will change when we add real callbacks ( it's equivalent
     *  with the previous RMI method from almost all points of view )
     */
    void stopTomcat() throws TomcatException {
	XmlMapper xh=new XmlMapper();
	xh.setDebug( 0 );
	ContextManager cm=new ContextManager();
	
	ServerXmlHelper sxml=new ServerXmlHelper();

	sxml.setConnectorHelper( xh );
	// load server.xml
	File f = null;
	if (configFile != null)
	    f=new File(configFile);

	String tchome=sxml.getTomcatInstall();
	f=new File(tchome, DEFAULT_CONFIG);
	cm.setInstallDir( tchome);

	try {
	    xh.readXml(f,cm);
	} catch( Exception ex ) {
	    throw new TomcatException("Fatal exception reading " + f, ex);
	}
	
	execute( cm );     
    }
    
    
    /** This particular implementation will search for an AJP12
	connector ( that have a special stop command ).
    */
    public void execute(ContextManager cm)
	throws TomcatException 
    {
	// Find Ajp12 connector
	int portInt=8007;
	InetAddress address=null;
	BaseInterceptor ci[]=cm.getInterceptors();
	for( int i=0; i<ci.length; i++ ) {
	    Object con=ci[i];
	    if( con instanceof  Ajp12ConnectionHandler ) {
		PoolTcpConnector tcpCon=(PoolTcpConnector) con;
		portInt=tcpCon.getPort();
		address=tcpCon.getAddress();
	    }
	    if( con instanceof  Ajp12Interceptor ) {
		Ajp12Interceptor tcpCon=(Ajp12Interceptor) con;
		portInt=tcpCon.getPort();
		address=tcpCon.getAddress();
	    }
	}

	// use Ajp12 to stop the server...
	try {
	    if (address == null)
		address = InetAddress.getLocalHost();
	    Socket socket = new Socket(address, portInt);
	    OutputStream os=socket.getOutputStream();
	    byte stopMessage[]=new byte[2];
	    stopMessage[0]=(byte)254;
	    stopMessage[1]=(byte)15;
	    os.write( stopMessage );
	    socket.close();
	} catch(Exception ex ) {
	    throw new TomcatException("Error stopping Tomcat with Ajp12 on " + address + ":" + portInt, ex);
	}
    }
    
}
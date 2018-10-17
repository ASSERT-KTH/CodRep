newId= (String)jdk11Compat.doPrivileged(di, jdk11Compat.getAccessControlContext());

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
package org.apache.tomcat.modules.session;

import java.io.*;
import java.util.Random;
import org.apache.tomcat.util.*;
import org.apache.tomcat.util.compat.*;
import org.apache.tomcat.util.threads.*;
import org.apache.tomcat.core.*;
import java.util.*;
import org.apache.tomcat.util.collections.SimplePool;
import org.apache.tomcat.util.log.*;
import org.apache.tomcat.util.buf.*;
import java.security.*;


/**
 * Generate session IDs. Will use a random generator and the
 * load balancing route.
 *
 * This class generates a unique 10+ character id. This is good
 * for authenticating users or tracking users around.
 * <p>
 * This code was borrowed from Apache JServ.JServServletManager.java.
 * It is what Apache JServ uses to generate session ids for users.
 * Unfortunately, it was not included in Apache JServ as a class
 * so I had to create one here in order to use it.
 *
 * @author costin@eng.sun.com
 * @author hans@gefionsoftware.com
 * @author pfrieden@dChain.com
 * @author Shai Fultheim [shai@brm.com]
 * @author James Duncan Davidson [duncan@eng.sun.com]
 * @author Jason Hunter [jhunter@acm.org]
 * @author Jon S. Stevens <a href="mailto:jon@latchkey.com">jon@latchkey.com</a>
 */
public final class SessionIdGenerator  extends BaseInterceptor {

    String randomClassName=null;
    Random randomSource=null;

    DataInputStream randomIS=null;
    String devRandomSource="/dev/urandom";
    
    static Jdk11Compat jdk11Compat=Jdk11Compat.getJdkCompat();
    
    public SessionIdGenerator() {
    }

    // -------------------- Configuration properties --------------------

    public final void setRandomClass(String randomClass) {
	this.randomClassName=randomClass;
    }

    /** Use /dev/random-type special device. This is new code, but may reduce the
     *  big delay in generating the random.
     *
     *  You must specify a path to a random generator file. Use /dev/urandom
     *  for linux ( or similar ) systems. Use /dev/random for maximum security
     *  ( it may block if not enough "random" exist ). You can also use
     *  a pipe that generates random.
     *
     *  The code will check if the file exists, and default to java Random
     *  if not found. There is a significant performance difference, very
     *  visible on the first call to getSession ( like in the first JSP )
     *  - so use it if available.
     */
    public void setRandomFile( String s ) {
	// as a hack, you can use a static file - and genarate the same
	// session ids ( good for strange debugging )
	try {
	    devRandomSource=s;
	    File f=new File( devRandomSource );
	    if( ! f.exists() ) return;
	    randomIS= new DataInputStream( new FileInputStream(f));
	    randomIS.readLong();
	    log( "Opening " + devRandomSource );
	} catch( IOException ex ) {
	    randomIS=null;
	}
    }
    
    
    // -------------------- Tomcat request events --------------------

    public int sessionState( Request req, ServerSession sess, int state ) {
	if( state==ServerSession.STATE_NEW ) {
	    String jsIdent=req.getJvmRoute();
	    String newId=createNewId( jsIdent );
	    sess.getId().setString( newId );
	}
	return state;
    }

    //--------------------  Tomcat context events --------------------


    /** Init session management stuff for this context. 
     */
    public void engineInit(ContextManager cm) throws TomcatException {
    }
    

    // -------------------- Internal methods --------------------

    String createNewId(String jsIdent) {
        /**
         * When using a SecurityManager and a JSP page or servlet triggers
         * creation of a new session id it must be performed with the 
         * Permissions of this class using doPriviledged because the parent
         * JSP or servlet may not have sufficient Permissions.
         */
	String newId;

        if( System.getSecurityManager() == null ) {
	    newId= getIdentifier(jsIdent);
	    return newId;
	}
	// We're in a sandbox...
	PriviledgedIdGenerator di = new PriviledgedIdGenerator(this, jsIdent);
	try {
	    newId= (String)jdk11Compat.doPrivileged(di);
	} catch( Exception ex ) {
	    newId=null;
	}
	return newId;
    }

    // Sandbox support
    static class PriviledgedIdGenerator extends Action {
	SessionIdGenerator sg;
	String jsIdent;
	public PriviledgedIdGenerator(SessionIdGenerator sg, String jsIdent ) {
	    this.sg=sg;
	    this.jsIdent=jsIdent;
	}           
	public Object run() {
	    return sg.getIdentifier(jsIdent);
	}           
    }    

    /** Create the random generator using the configured class name, and
     * defaulting to java.security.SecureRandom
     */
    private void createRandomClass() {
	if( randomClassName==null ) {
	    // backward compatibility 
	    randomClassName=(String)cm.getProperty("randomClass" );
	    // set a reasonable default 
	    if( randomClassName==null ) {
		randomClassName="java.security.SecureRandom";
	    }
	}
	try {
	    Class randomClass = Class.forName(randomClassName);
	    randomSource = (java.util.Random)randomClass.newInstance();
	} catch (Exception e) {
	    log("SessionIdGenerator.createRandomClass", e);
	}
	if (randomSource == null)
	    randomSource = new java.security.SecureRandom();
	log( "Created random class " + randomSource.getClass().getName());
    }

    /*
     * Create a suitable string for session identification
     * Use synchronized count and time to ensure uniqueness.
     * Use random string to ensure timestamp cannot be guessed
     * by programmed attack.
     *
     * format of id is <6 chars random><3 chars time><1+ char count>
     */
    static private int session_count = 0;
    static private long lastTimeVal = 0;

    // MAX_RADIX is 36
    /*
     * we want to have a random string with a length of
     * 6 characters. Since we encode it BASE 36, we've to
     * modulo it with the following value:
     */
    public final static long maxRandomLen = 2176782336L; // 36 ** 6

    /*
     * The session identifier must be unique within the typical lifespan
     * of a Session, the value can roll over after that. 3 characters:
     * (this means a roll over after over an day which is much larger
     *  than a typical lifespan)
     */
    public final static long maxSessionLifespanTics = 46656; // 36 ** 3

    /*
     *  millisecons between different tics. So this means that the
     *  3-character time string has a new value every 2 seconds:
     */
    public final static long ticDifference = 2000;

    // ** NOTE that this must work together with get_jserv_session_balance()
    // ** in jserv_balance.c
    public synchronized String getIdentifier(String jsIdent)
    {
        StringBuffer sessionId = new StringBuffer();
	
        // random value ..
        long n = 0;
	if( randomIS!=null ) {
	    try {
		n=randomIS.readLong();
		//System.out.println("Getting /dev/random " + n );
	    } catch( IOException ex ) {
		ex.printStackTrace();
		randomIS=null;
		// We could also re-open it ( if it's a file of random values )
	    }
	}
	if( randomIS==null ) {
	    if (randomSource==null )
		createRandomClass();
	    n=randomSource.nextLong();
	} 

        if (n < 0) n = -n;
        n %= maxRandomLen;
        // add maxLen to pad the leading characters with '0'; remove
	// first digit with substring.
        n += maxRandomLen;
        sessionId.append (Long.toString(n, Character.MAX_RADIX)
                  .substring(1));

        long timeVal = (System.currentTimeMillis() / ticDifference);
        // cut..
        timeVal %= maxSessionLifespanTics;
        // padding, see above
        timeVal += maxSessionLifespanTics;

        sessionId.append (Long.toString (timeVal, Character.MAX_RADIX)
                  .substring(1));

        /*
         * make the string unique: append the session count since last
         * time flip.
         */
        // count sessions only within tics. So the 'real' session count
        // isn't exposed to the public ..
        if (lastTimeVal != timeVal) {
          lastTimeVal = timeVal;
          session_count = 0;
        }
        sessionId.append (Long.toString (++session_count,
                     Character.MAX_RADIX));

        if (jsIdent != null && jsIdent.length() > 0) {
            return sessionId.toString()+"."+jsIdent;
        }
        return sessionId.toString();
    }

}
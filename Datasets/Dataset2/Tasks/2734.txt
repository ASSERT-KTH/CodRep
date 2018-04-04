private static final int debug=0;

/*
 * Copyright (c) 1997-1999 The Java Apache Project.  All rights reserved.
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
 * 3. All advertising materials mentioning features or use of this
 *    software must display the following acknowledgment:
 *    "This product includes software developed by the Java Apache 
 *    Project for use in the Apache JServ servlet engine project
 *    <http://java.apache.org/>."
 *
 * 4. The names "Apache JServ", "Apache JServ Servlet Engine" and 
 *    "Java Apache Project" must not be used to endorse or promote products 
 *    derived from this software without prior written permission.
 *
 * 5. Products derived from this software may not be called "Apache JServ"
 *    nor may "Apache" nor "Apache JServ" appear in their names without 
 *    prior written permission of the Java Apache Project.
 *
 * 6. Redistributions of any form whatsoever must retain the following
 *    acknowledgment:
 *    "This product includes software developed by the Java Apache 
 *    Project for use in the Apache JServ servlet engine project
 *    <http://java.apache.org/>."
 *    
 * THIS SOFTWARE IS PROVIDED BY THE JAVA APACHE PROJECT "AS IS" AND ANY
 * EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE JAVA APACHE PROJECT OR
 * ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
 * NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
 * STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
 * OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * This software consists of voluntary contributions made by many
 * individuals on behalf of the Java Apache Group. For more information
 * on the Java Apache Project and the Apache JServ Servlet Engine project,
 * please see <http://java.apache.org/>.
 *
 */

package org.apache.tomcat.depend;

import java.io.*;
import java.lang.*;
import java.net.*;
import java.text.*;
import java.util.*;
import java.util.zip.*;
import java.security.*;

/** How it works:
    - A DependManager gets loaded with a number of Dependency
    - each Dependency includes a File and a timestamp.
    - If any of the Files is changed after timestamp this DependManager
    will set "expired" to true
    - One check at a time, but without sync
    - if a check was done recently ( delay property ) - assume nothing changed

    It is also possible to do the checks in background, but for big
    servers ( with many contexts) it have scalability problems.
 */
public class DependManager {
    int delay=4000;
    Dependency deps[]=new Dependency[32];
    int depsCount=0;
    long lastCheck=0;
    boolean checking=false;
    long checkTime=0;
    int checkCount=0;

    boolean expired=false;
    
    public DependManager() {
    }

    public void setDelay( int d ) {
	delay=d;
    }

    // statistics
    public long getCheckTime() {
	return checkTime;
    }

    public long getCheckCount() {
	return checkCount;
    }
    
    // Not synchronized - we do that inside
    public boolean shouldReload() {
	// somebody else is checking, so we don't know yet.
	// assume we're fine - reduce the need for sync
	if( checking ) return expired;

	synchronized(this) {
	    try {
		// someone else got here and did it before me
		if( checking ) return expired;
			
		// did a check in the last N seconds
		long startCheck=System.currentTimeMillis();
		if( startCheck - lastCheck < delay )
		    return expired;
		
		checking=true;

		// it's ok if a new dep is added - this is not
		//exact science ( and no dep can be removed)
		for( int i=0; i<depsCount; i++ ) {
		    Dependency d=deps[i];
		    long lm=d.getLastModified();
		    File f=d.getOrigin();
		    if( lm < f.lastModified() ) {
			// something got modified
			expired=true;
		    }
		}
		checkTime += lastCheck-startCheck;
		checkCount++;
		lastCheck=startCheck;
	    } finally {
		checking=false;
	    }
	    return expired;
	}
    }

    public synchronized void addDependency( Dependency dep ) {
	if( depsCount >= deps.length ) {
	    Dependency deps1[]=new Dependency[ deps.length *2 ];
	    System.arraycopy( deps, 0, deps1, 0 , depsCount );
	    deps=deps1;
	}
	deps[depsCount++]= dep ;
	if( debug>2) log( "Added " + dep.getOrigin() + " " + dep.getTarget());
    }
    
    // -------------------- Private 

    private static final int debug=10;
    
    void log( String s ) {
	System.out.println("DependManager: " + s );
    }
}
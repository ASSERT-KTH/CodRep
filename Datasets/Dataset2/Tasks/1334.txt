org.objectweb.carol.util.configuration.CarolConfiguration.init();

/*
 * @(#) BasicServer.java	1.0 02/07/15
 *
 * Copyright (C) 2002 - INRIA (www.inria.fr)
 *
 * CAROL: Common Architecture for RMI ObjectWeb Layer
 *
 * This library is developed inside the ObjectWeb Consortium,
 * http://www.objectweb.org
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or any later version.
 * 
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 * 
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307
 * USA
 * 
 *
 */
package org.objectweb.carol.jtests.conform.basic.server;

//tmp import 
import java.util.*;

// java import
import java.util.Properties;
import java.rmi.Remote;

// javax import
import javax.rmi.PortableRemoteObject;
import javax.naming.InitialContext;
import javax.naming.Context;


/*
 * Class <code>BasicServer</code> is a  Server for Junit tests
 * Test The InitialContext and the PortableRemoteObject situation with remote object  
 */
public class BasicServer {

    /**
     * Name of the basic remote object (in all name services)
     */
    private static String  basicObjectName = "basicname";

    /**
     * Name of the basic multi remote object (in all name services)
     */  
    private static String  basicMultiObjectName =  "basicmultiname";    

    /**
     * Name of the basic object ref
     */  
    private static String  basicObjectRefName =  "basicrefname"; 

    /**
     * Initial Contexts
     */
    private static Context ic = null;

    /**
     * TheBasicObject
     */
    private static BasicObjectItf ba = null;

    /**
     * TheBasicMultiObject
     */
    private static BasicMultiObjectItf bma = null;

    /**
     * TheBasicObjectRef
     */
    private static BasicObjectRef bref = null;  
  
    /**
     * Main method 
     * This method bind all the name in the registry 
     */
    public static void main(String [] args) {	
	start();
    }

    public static void start() {
	try {
	    
	    org.objectweb.carol.util.configuration.CarolConfiguration.initCarol();

	    // create, export and bind TheBasicObject an the BasicMultiObject (wich call the BasicObject)
	    ba = new BasicObject();
	    bma = new BasicMultiObject();
	    bref = new BasicObjectRef("string");
	    
	    // get the IntialContext
	    ic = new InitialContext();

	    // multi rebind
	    ic.rebind(basicObjectName, ba);   	    
	    ic.rebind(basicMultiObjectName, bma);
	    ic.rebind(basicObjectRefName, bref);
	     
	} catch (Exception e) {
	    e.printStackTrace();
	    System.err.println("Server can't start :" + e);
	}
    }

    public static void stop() {
	try {
	    // get the IntialContext
	    ic = new InitialContext();
	    
	    // multi rebind
	    ic.unbind(basicObjectName);   	    
	    ic.unbind(basicMultiObjectName);
	    ic.unbind(basicObjectRefName);	
	} catch (Exception e) {
	    e.printStackTrace();
	    System.err.println("Server can't start :" + e);
	}

	// for the moment
	System.exit(0);
    }
}
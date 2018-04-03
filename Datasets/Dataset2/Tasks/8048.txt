TraceCarol.error("ProtocolCurrent() Exception", e);

/*
 * @(#) JUnicastServerRef.java	1.0 02/07/15
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
package org.objectweb.carol.util.multi;

//javax import
import javax.naming.Context;
import javax.naming.InitialContext;
import javax.rmi.CORBA.PortableRemoteObjectDelegate;

import java.util.Properties;
import java.util.Hashtable;
import java.util.Enumeration;

//carol import
import org.objectweb.carol.util.configuration.RMIConfiguration;
import org.objectweb.carol.util.configuration.CarolConfiguration; 
import org.objectweb.carol.util.configuration.TraceCarol; 

/**
 * Class <code>ProtocolCurrent</code>For handling the association Rmi/ Thread
 * 
 * @author  Guillaume Riviere (Guillaume.Riviere@inrialpes.fr)
 * @version 1.0, 15/07/2002
 *
 */

public class ProtocolCurrent {

    /**
     * Protocols Portale Remote Object Delegate 
     */
    private static Hashtable prodHashtable = null;    

    /**
     * Context Array for each protocol
     */
    private static Hashtable icHashtable = null;

    /**
     * Protocol Number for default
     */
    private static String defaultRMI;

    /**
     * Thread Local for protocol context propagation
     */
    private static InheritableThreadLocal threadCtx;
     
    /**
     * private constructor for singleton
     */
    private static ProtocolCurrent current = new ProtocolCurrent () ;

    /**
     * private constructor for unicicity
     */
    private ProtocolCurrent() {

	try {

	    threadCtx = new InheritableThreadLocal(); 
	    prodHashtable = new Hashtable();
	    icHashtable = new Hashtable();
	    //get rmi configuration  hashtable 	    
	    Hashtable allRMIConfiguration = CarolConfiguration.getAllRMIConfiguration();	    
	    int nbProtocol = allRMIConfiguration.size();
	    for (Enumeration e = allRMIConfiguration.elements() ; e.hasMoreElements() ;) {
		RMIConfiguration currentConf = (RMIConfiguration)e.nextElement();
		String rmiName = currentConf.getName();
		// get the PRO 
		prodHashtable.put(rmiName, (PortableRemoteObjectDelegate)Class.forName(currentConf.getPro()).newInstance());
		icHashtable.put(rmiName,  new InitialContext(currentConf.getJndiProperties()));
	    }
	    defaultRMI = CarolConfiguration.getDefaultProtocol().getName();
	    // set the default protocol
	    threadCtx.set(defaultRMI) ;
	    
	    // trace Protocol current
	    if (TraceCarol.isDebugCarol()) {
		TraceCarol.debugCarol("ProtocolCurrent.ProtocolCurrent()");
		TraceCarol.debugCarol("Number of rmi:" + icHashtable.size());
		TraceCarol.debugCarol("Default:"+ defaultRMI);
	    }
	    
	} catch (Exception e) {
	    e.printStackTrace();
	}
    }
    
    /**
     * Method getCurrent
     *
     * @return ProtocolCurrent return the current 
     *
     */
    public static ProtocolCurrent getCurrent() {
	return current ;
    }


    /**
     * This method if for setting one rmi context
     * 
     * @param s the rmi name
     */
    public void setRMI (String s) {
	threadCtx.set(s) ;
    }

    /**
     * set the default protocol
     */
    public void setDefault () {
	threadCtx.set(defaultRMI) ;
    }

   /**
    * Get the Portable Remote Object Hashtable
    * @return  Hashtable the hashtable of PROD
    */
    public  Hashtable getPortableRemoteObjectHashtable() {
	return prodHashtable;
    }

   /**
    * Get the Context Hashtable
    * @return Hashtable the hashtable of Context 
    */
    public Hashtable getContextHashtable() {
	return icHashtable;
    }    

    /**
     * Get current protocol PROD
     * @return PortableRemoteObjectDelegate the portable remote object
     */
    public PortableRemoteObjectDelegate getCurrentPortableRemoteObject() {
	if (threadCtx.get() == null) {
	    return (PortableRemoteObjectDelegate)prodHashtable.get(defaultRMI); 
	} else {
	    return (PortableRemoteObjectDelegate)prodHashtable.get((String)threadCtx.get());
	}
    }

    /**
     * Get current protocol Initial Context
     * @return InitialContext the initial Context
     */
    public Context getCurrentInitialContext() {
	if (threadCtx.get() == null) {
	    return (Context)icHashtable.get(defaultRMI); 
	} else {
	    return (Context)icHashtable.get((String)threadCtx.get());
	}
    }

    /**
     * Get current protocol RMI name
     * @return String the RMI name
     */
    public String getCurrentRMIName() {
	if (threadCtx.get() == null) {
	    return defaultRMI; 
	} else {
	    return (String)threadCtx.get();
	}
    }

    /**
     * To string method 
     */
    public String toString() {
	return "\nnumber of rmi:" + icHashtable.size() 
	    + "\ndefault:"+ defaultRMI;
    }
}  
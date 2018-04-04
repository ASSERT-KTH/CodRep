Method exportO = unicastClass.getMethod("toStub",  new Class [] { Remote.class });

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
package org.objectweb.carol.rmi.multi;

//java import
import java.lang.reflect.Method;
import java.rmi.Remote;
import java.rmi.RemoteException;
import java.rmi.NoSuchObjectException;

//javax import
import javax.rmi.CORBA.PortableRemoteObjectDelegate;


/**
 * class <code>JeremiePRODelegate</code> for the mapping between Jeremie UnicastRemoteObject and PortableRemoteObject
 * 
 * @author  Guillaume Riviere (Guillaume.Riviere@inrialpes.fr)
 * @version 1.0, 15/07/2002  
 */
public class JeremiePRODelegate implements PortableRemoteObjectDelegate {

    /**
     * UnicastRemoteObjectClass
     */
    private static String className = "org.objectweb.jeremie.libs.binding.moa.UnicastRemoteObject";

    /**
     * Instance object for this UnicastRemoteObject
     */
    private static Class unicastClass = null;

    /**
     * Empty constructor for instanciate this class
     */
    public JeremiePRODelegate() throws Exception {
	// class for name
	unicastClass = Class.forName(className);
	
    }


    /**
     * Export a Remote Object 
     * @param Remote object to export
     * @exception RemoteException exporting remote object problem 
     */
    public void exportObject(Remote obj) throws RemoteException {
	try {
	    Method exportO = unicastClass.getMethod("exportObject",  new Class [] { Remote.class });
	    exportO.invoke(unicastClass, (new Object[] { obj } ));
	} catch (Exception e) {
	    throw new RemoteException(e.toString());
	}
    }

    
    /**
     * Method for unexport object
     * @param Remote obj object to unexport 
     * @exception NoSuchObjectException if the object is not currently exported
     */
    public void unexportObject(Remote obj) throws NoSuchObjectException {
	try {
	    Method unexportO = unicastClass.getMethod("unexportObject",  new Class [] { Remote.class, Boolean.class });
	    unexportO.invoke(unicastClass, (new Object[] { obj, new Boolean(true) } ));
	} catch (Exception e) {
	    throw new NoSuchObjectException (e.toString());
	}
    }

    /**
     * Connection method
     * @param target a remote object;
     * @param source another remote object; 
     * @exception RemoteException if the connection fail
     */ 
    public void connect(Remote target,Remote source) throws RemoteException {
	// do nothing
    }

	
    /**
     * Narrow method
     * @param Remote obj the object to narrow 
     * @param Class newClass the expected type of the result  
     * @return an object of type newClass
     * @exception ClassCastException if the obj class is not compatible with a newClass cast 
     */
    public Object narrow(Object obj, Class newClass ) throws ClassCastException {
	if (newClass.isAssignableFrom(obj.getClass())) {
	    return obj;
	} else {
	    throw new ClassCastException("Can't cast "+obj.getClass().getName()+" in "+newClass.getName());
	}
    }

    /**
     * To stub method
     * @return the stub object    
     * @param Remote object to unexport    
     * @exception NoSuchObjectException if the object is not currently exported
     */
    public Remote toStub(Remote obj) throws NoSuchObjectException {
	try {
	    Method exportO = unicastClass.getMethod("exportObject",  new Class [] { Remote.class });
	    return (Remote)exportO.invoke(unicastClass, (new Object[] { obj } ));
	} catch (Exception e) {
	    throw new NoSuchObjectException(e.toString());
	}
    }

}
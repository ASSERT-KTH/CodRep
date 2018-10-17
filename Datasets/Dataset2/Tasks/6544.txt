JeremieRegistry.this.stop();

/*
 * @(#) JeremieRegistry.java	1.0 02/07/15
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
 */
package org.objectweb.carol.jndi.ns;

import java.rmi.registry.Registry;
import java.rmi.RemoteException;
import org.objectweb.jeremie.libs.services.registry.LocateRegistry;
import org.objectweb.jeremie.libs.binding.moa.UnicastRemoteObject;
import org.objectweb.carol.util.configuration.TraceCarol;

/*
 * Class <code>JeremieRegistry</code>
 *
 * @author  Guillaume Riviere (Guillaume.Riviere@inrialpes.fr)
 * @version 1.0, 15/01/2003
 */
public class JeremieRegistry implements NameService {
    /**
     * port number ( 12340 for default)
     */
    public int port=12340;

    /**
     * registry 
     */
    public Registry registry = null; 

    /**
     * start Method, Start a new NameService or do nothing if the name service is all ready start
     * @param int port is port number
     * @throws NameServiceException if a problem occure 
     */
    public void start() throws NameServiceException {	
	if (TraceCarol.isDebugJndiCarol()) {
            TraceCarol.debugJndiCarol("JeremieRegistry.start() on port:" + port);
        }
	try {
	    if (!isStarted()) {
		if (port >= 0) {
		    registry = LocateRegistry.createRegistry(port);
		    // add a shudown hook for this process
		    Runtime.getRuntime().addShutdownHook(new Thread() {
			    public void run() {
				try {
				    stop();
				} catch (Exception e) {
				    TraceCarol.error("JeremieRegistry ShutdownHook problem" ,e);
				}
			    }
			});
		} else {		  		
		    if (TraceCarol.isDebugJndiCarol()) {
			TraceCarol.debugJndiCarol("Can't start JeremieRegistry, port="+port+" is < 0");
		    }
		}
				    
	    } else {		
		if (TraceCarol.isDebugJndiCarol()) {
		    TraceCarol.debugJndiCarol("JeremieRegistry is already start on port:" + port);
		}
	    }
	} catch (Exception e) {
	    throw new NameServiceException("can not start jeremie registry: " +e);
	}
    }

    /**
     * stop Method, Stop a NameService or do nothing if the name service is all ready stop
     * @throws NameServiceException if a problem occure 
     */
    public void stop() throws NameServiceException {
	if (TraceCarol.isDebugJndiCarol()) {
            TraceCarol.debugJndiCarol("JeremieRegistry.stop()");
        }
	try {
	    if (registry!=null) UnicastRemoteObject.unexportObject(registry, true);
	    registry = null;
	} catch (Exception e) {
	    throw new NameServiceException("can not stop jeremie registry: " +e);
	}
    }

    /**
     * isStarted Method, check if a name service is started
     * @return boolean true if the name service is started
     */
    public boolean isStarted() {
	if (registry != null) return true;
	try {
	    LocateRegistry.getRegistry(port).list();   
	} catch (RemoteException re) {
	    return false;
	}
	return true;
    }

    /**
     * set port method, set the port for the name service
     * @param int port number
     */
    public void setPort(int p) {
	if (TraceCarol.isDebugJndiCarol()) {
            TraceCarol.debugJndiCarol("JeremieRegistry.setPort("+p+")");
        }
	if (p!= 0) {
	    port = p;
	}
    }
}
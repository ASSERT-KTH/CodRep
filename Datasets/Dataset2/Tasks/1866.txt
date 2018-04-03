import org.objectweb.jeremie.services.handler.api.Service;

/*
 * @(#) JeremieCarolHandler.java	1.0 02/07/15
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
package org.objectweb.carol.rmi.jonathan.jeremie;

import org.objectweb.carol.util.configuration.CarolCurrentConfiguration;
import org.objectweb.jeremie.apis.services.handler.Service;
import org.objectweb.jonathan.apis.kernel.Context;
import org.objectweb.jonathan.apis.kernel.JonathanException;
import org.omg.IOP.ServiceContext;


/**
 * Class <code>CarolHandler</code> is the CAROL Handler for 
 * Jonathan server interception
 * 
 * @author  Guillaume Riviere (Guillaume.Riviere@inrialpes.fr) 
 * @version 1.0, 15/07/2002
 */
public class JeremieCarolHandler implements Service {

    private String name = null;

   /** 
    * Builds a new Jonathan jeremie carol service handler instance.
    * @exception JonathanException if something goes wrong.
    */
   public JeremieCarolHandler() throws JonathanException {
       // do nothing
       this.name="jeremie";
   }
   
    /** 
     * Returns a request context.
     * @return always null
     */
    public ServiceContext getRequestContext(int id, boolean r, byte[] key, Context k) {
	    return null;
    }
	 
    
    /** 
     * Returns a reply context.
     * @return always null
     */
    public ServiceContext getReplyContext(int id, Context k) {
	    return null;
    }
    
    /** 
     * This method is called by the services handler to let the operations 
     * related to the target service be performed on request arrival.
     * @param context   the service context of the request;
     */
    public void handleRequestContext(ServiceContext context, int id, boolean r, byte[] key, Context k) {
	CarolCurrentConfiguration.getCurrent().setRMI(name);
	
    }
    
    /** 
     * This method is called by the services handler to let the operations 
     * related to the target service be performed on reply arrival.
     * @param context     the service context of the reply;
     */
    public void handleReplyContext(ServiceContext context, int id, Context k) {
	// do nothing on reply
    }   
}
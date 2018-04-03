return  IIOPReferenceContextWrapper.getSingleInstance(super.getInitialContext(env));

/*
 * @(#)IIOPReferenceContextWrapper.java	1.0 02/07/15
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
package org.objectweb.carol.jndi.iiop;

// java import
import java.util.Hashtable;

import javax.naming.Context;
import javax.naming.NamingException;

import com.sun.jndi.cosnaming.CNCtxFactory;
/*
 * Class <code>OpenOrbRemoteReferenceContextWrapperFactory</code> is the CAROL JNDI Context factory.
 *  This context factory build the iiop context for reference wrapping to/from an openorb remote object
 * 
 * @author  Guillaume Riviere (Guillaume.Riviere@inrialpes.fr)
 * @see javax.naming.spi.InitialContextFactory
 * @version 1.0, 15/07/2002
 */
public class OpenOrbReferenceContextWrapperFactory extends CNCtxFactory {

    /**
     * Get/Build the IIOP Wrapper InitialContext
     *
     * @param env the inital IIOP environement
     * @return a <code>Context</code> coresponding to the inital IIOP environement with 
     *         IIOP Serializable ressource wrapping
     *
     * @throws NamingException if a naming exception is encountered
     */   
    public Context getInitialContext(Hashtable env) throws NamingException {
	env.put("java.naming.factory.initial","org.openorb.rmi.jndi.CtxFactory");
	return new IIOPReferenceContextWrapper(super.getInitialContext(env));
    }


}
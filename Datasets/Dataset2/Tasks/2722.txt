super("ProcessException" + ex);

/*
 * @(#) ProcessException.java	1.0 02/07/15
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
package org.objectweb.carol.util.bootstrap;

import java.io.Serializable;

/**
 * Class <code>ProcessException</code> is a Process exception
 * 
 * @author  Guillaume Riviere (Guillaume.Riviere@inrialpes.fr)
 * @version 1.0, 15/07/2002
 *
 */

public class ProcessException extends Exception implements Serializable {

    String mess = null;

    /**
     * empty constructor
    */
    public ProcessException() {
	super("ProcessException");
    }
    /**
     * string constructor
    */
    public ProcessException(String s) {
	super("ProcessException" + s);
	mess = s;
    }   
    
    /**
     * throwable constructor
    */
    public ProcessException(Throwable ex) {
	super("ProcessException", ex);
    }
    
    /**
     * to string method
     */
    public String toString() {

	return "ProcessException: an exception occurs in the remote Process:\n" + "  " + getMessage() + "\n   " + mess;

    }
        
}
import org.eclipse.ecf.internal.provider.Trace;

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.provider.generic;

import org.eclipse.ecf.core.ContainerTypeDescription;
import org.eclipse.ecf.core.ContainerCreateException;
import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.identity.IDCreateException;
import org.eclipse.ecf.core.provider.IContainerInstantiator;
import org.eclipse.ecf.provider.Trace;

public class ContainerInstantiator implements
        IContainerInstantiator {
    public static final String TCPCLIENT_NAME = "ecf.generic.client";
    public static final String TCPSERVER_NAME = "ecf.generic.server";

    public static final Trace debug = Trace.create("containerfactory");
    public ContainerInstantiator() {
        super();
    }
    protected void debug(String msg) {
        if (Trace.ON && debug != null) {
            debug.msg(msg);
        }
    }
    protected void dumpStack(String msg, Throwable t) {
        if (Trace.ON && debug != null) {
            debug.dumpStack(t,msg);
        }
    }
    protected ID getIDFromArg(Class type, Object arg)
            throws IDCreateException {
        if (arg instanceof ID) return (ID) arg;
        if (arg instanceof String) {
            String val = (String) arg;
            if (val == null || val.equals("")) {
                return IDFactory.getDefault().createGUID();
            } else return IDFactory.getDefault().createStringID((String) arg);
        } else if (arg instanceof Integer) {
            return IDFactory.getDefault().createGUID(((Integer) arg).intValue());
        } else
            return IDFactory.getDefault().createGUID();
    }

    protected Integer getIntegerFromArg(Class type, Object arg)
            throws NumberFormatException {
        if (arg instanceof Integer)
            return (Integer) arg;
        else if (arg != null) {
            return new Integer((String) arg);
        } else return new Integer(-1);
    }

    public IContainer createInstance(
            ContainerTypeDescription description, Class[] argTypes,
            Object[] args) throws ContainerCreateException {
        boolean isClient = true;
        if (description.getName().equals(TCPSERVER_NAME)) {
            debug("creating server");
            isClient = false;
        } else {
            debug("creating client");
        }
        ID newID = null;
        try {
            String [] argDefaults = description.getArgDefaults();
            newID = (argDefaults==null||argDefaults.length==0)?null:getIDFromArg(String.class,
                    description.getArgDefaults()[0]);
            Integer ka = (argDefaults==null||argDefaults.length < 2)?null:getIntegerFromArg(String.class, description
                    .getArgDefaults()[1]);
            if (args != null) {
                if (args.length > 0) {
                    newID = getIDFromArg(argTypes[0], args[0]);
                    if (args.length > 1) {
                        ka = getIntegerFromArg(argTypes[1],args[1]);
                    }
                }
            }
            debug("id="+newID+";keepAlive="+ka);
            // new ID must not be null
            if (newID == null)
                throw new ContainerCreateException(
                        "id must be provided");
            if (isClient) {
                return new TCPClientSOContainer(new SOContainerConfig(newID),
                        ka.intValue());
            } else {
                return new TCPServerSOContainer(new SOContainerConfig(newID),
                        ka.intValue());
            }
        } catch (ClassCastException e) {
            dumpStack("ClassCastException",e);
            throw new ContainerCreateException(
                    "Parameter type problem creating container", e);
        } catch (Exception e) {
            dumpStack("Exception",e);
            throw new ContainerCreateException(
                    "Exception creating generic container with id "+newID, e);
        }
    }
}
 No newline at end of file
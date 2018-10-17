private static PortableRemoteObjectDelegate rmi = new JrmpPRODelegate(true);

/*
 * Copyright (C) 2002-2004, Simon Nieuviarts
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
 */
package org.objectweb.carol.cmi;

import java.lang.reflect.Constructor;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.rmi.NoSuchObjectException;
import java.rmi.Remote;
import java.rmi.RemoteException;
import java.rmi.server.ObjID;
import java.rmi.server.RemoteRef;
import java.rmi.server.RemoteStub;

import javax.rmi.CORBA.PortableRemoteObjectDelegate;

import org.objectweb.carol.rmi.multi.JrmpPRODelegate;

class SunLowerOrb {
    private static Class liveref;
    private static Constructor liveref_cons;
    private static Class usref;
    private static Constructor usref_cons;
    private static Method usref_export;
    private static Class tcpep;
    private static Constructor tcpep_cons;
    private static Constructor liveref_cons2;
    private static Class uref;
    private static Constructor uref_cons;
    private static boolean init = false;

    static {
        try {
            liveref = Class.forName("sun.rmi.transport.LiveRef");
            Class[] p0 = { ObjID.class, int.class };
            liveref_cons = liveref.getConstructor(p0);
            usref = Class.forName("sun.rmi.server.UnicastServerRef");
            Class[] p1 = { liveref };
            usref_cons = usref.getConstructor(p1);
            Class[] p2 = { Remote.class, Object.class, boolean.class };
            usref_export = usref.getMethod("exportObject", p2);
            tcpep = Class.forName("sun.rmi.transport.tcp.TCPEndpoint");
            Class[] p3 = { String.class, int.class };
            tcpep_cons = tcpep.getConstructor(p3);
            Class ep = Class.forName("sun.rmi.transport.Endpoint");
            Class[] p4 = { ObjID.class, ep, boolean.class };
            liveref_cons2 = liveref.getConstructor(p4);
            uref = Class.forName("sun.rmi.server.UnicastRef");
            Class[] p5 = { liveref };
            uref_cons = uref.getConstructor(p5);
            init = true;
        } catch (ClassNotFoundException e) {
            // Init failed
        } catch (SecurityException e) {
            // Init failed
        } catch (NoSuchMethodException e) {
            // Init failed
        }
    }
    
    public static boolean isValid() {
        return init;
    }

    public static Remote export(Remote obj, int port, ObjID id) throws IllegalArgumentException, InstantiationException, IllegalAccessException, InvocationTargetException {
        Object[] p0 = { id, new Integer(port) };
        Object lr = liveref_cons.newInstance(p0);
        Object[] p1 = { lr };
        Object usr = usref_cons.newInstance(p1);
        Object[] p2 = { obj, null, new Boolean(true) }; 
        Object ret = usref_export.invoke(usr, p2);
        return (Remote)ret;
    }

    public static RemoteRef getRemoteRef(String host, int port, ObjID id) throws IllegalArgumentException, InstantiationException, IllegalAccessException, InvocationTargetException {
        Object[] p0 = { host, new Integer(port) };
        Object ep = tcpep_cons.newInstance(p0);
        Object[] p1 = { id, ep, new Boolean(false) };
        Object ref = liveref_cons2.newInstance(p1);
        Object[] p2 = { ref };
        Object rr = uref_cons.newInstance(p2);
        return (RemoteRef)rr;
    }
}


class GcjLowerOrb {
    private static boolean init = false;

    static {
        try {
            //init = true;
        } catch (SecurityException e) {
            // Init failed
        }
    }
    
    public static boolean isValid() {
        return init;
    }

    public static Remote export(Remote obj, int port, ObjID id) throws IllegalArgumentException, InstantiationException, IllegalAccessException, InvocationTargetException {
        return null;
    }

    public static RemoteRef getRemoteRef(String host, int port, ObjID id) throws IllegalArgumentException, InstantiationException, IllegalAccessException, InvocationTargetException {
        return null;
    }
}


public class LowerOrb {
    private static String prefix = "rmi:";
    public static final int DEFAULT_CREG_PORT = 1099;
    public static final int REG_ID = 0xC2C91901;
    private static ObjID id = new ObjID(REG_ID);
    private static PortableRemoteObjectDelegate rmi = new JrmpPRODelegate();

    public static Remote toStub(Remote obj) throws NoSuchObjectException {
        return rmi.toStub(obj);
    }

    public static void exportObject(Remote obj) throws RemoteException {
        rmi.exportObject(obj);
    }

    public static void unexportObject(Remote obj) throws NoSuchObjectException {
        rmi.unexportObject(obj);
    }

    public static PortableRemoteObjectDelegate getPRODelegate() {
        return rmi;
    }

    public static Remote exportRegistry(Remote obj, int port)
        throws RemoteException {
        /*
        LiveRef lref = new LiveRef(id, port);
        UnicastServerRef uref = new UnicastServerRef(lref);
        return uref.exportObject(obj, null, true);
        */
        try {
            if (SunLowerOrb.isValid()) {
                return SunLowerOrb.export(obj, port, id);
            } else if (GcjLowerOrb.isValid()) {
                return GcjLowerOrb.export(obj, port, id);
            } else {
                throw new RemoteException("Don't know how to export registry : ORB specific");
            }
        } catch (InvocationTargetException e) {
            Throwable t = e.getTargetException();
            if (t instanceof RemoteException) {
                throw (RemoteException)t;
            } else {
                throw new RemoteException("Unexpected exception", t);
            }
        } catch (RemoteException e) {
            throw e;
        } catch (Exception e) {
            throw new RemoteException("Unexpected exception", e);
        }
    }

    private static Class[] stubConsParamTypes = { RemoteRef.class };

    public static Remote getRegistryStub(
        String className,
        String host,
        int port)
        throws RemoteException {
        if (port <= 0)
            throw new RemoteException("Invalid port no " + port);
        RemoteRef rr;
        try {
            /*
            Endpoint ep = new TCPEndpoint(host, port);
            LiveRef ref = new LiveRef(id, ep, false);
            RemoteRef rr = new UnicastRef(ref);
            */
            if (SunLowerOrb.isValid()) {
                rr = SunLowerOrb.getRemoteRef(host, port, id);
            } else if (GcjLowerOrb.isValid()) {
                rr = GcjLowerOrb.getRemoteRef(host, port, id);
            } else {
                throw new RemoteException("Don't know how to build a stub : ORB specific");
            }
            Class stubcl = Class.forName(className + "_Stub");
            Object[] p0 = { rr };
            Constructor cons = stubcl.getConstructor(stubConsParamTypes);
            return (RemoteStub) cons.newInstance(p0);
        } catch (InvocationTargetException e) {
            Throwable t = e.getTargetException();
            if (t instanceof RemoteException) {
                throw (RemoteException)t;
            } else {
                throw new RemoteException("Unexpected exception", t);
            }
        } catch (RemoteException e) {
            throw e;
        } catch (Exception e) {
            throw new RemoteException("Unexpected exception", e);
        }
    }
}
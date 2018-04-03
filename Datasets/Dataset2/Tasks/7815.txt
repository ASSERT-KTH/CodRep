ClusterRegistryImpl_Cluster cstub = new ClusterRegistryImpl_Cluster(r);

/*
 * Copyright (C) 2002-2003, Simon Nieuviarts
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

import java.net.MalformedURLException;
import java.rmi.AlreadyBoundException;
import java.rmi.NotBoundException;
import java.rmi.Remote;
import java.rmi.RemoteException;

public final class Naming {
    private Naming() {
    }

    public static ClusterRegistry getRegistry(String host, int port)
        throws RemoteException {
        ClusterRegistry r =
            (ClusterRegistry) LowerOrb.getRegistryStub(
                "org.objectweb.carol.cmi.ClusterRegistryImpl", host, port);
        return r;
    }

    public static ClusterRegistry getRegistry(NamingContextHostPort[] hp)
        throws RemoteException {
        int n = hp.length;
        if (n == 0) return null;
        ClusterRegistry r = getRegistry(hp[0].host, hp[0].port);
        if (n == 1) return r;
        ClusterRegistryImplCStub cstub = new ClusterRegistryImplCStub(r);
        for (int i = 1; i < n; i++) {
            cstub.setStub(getRegistry(hp[i].host, hp[i].port));
        }
        return cstub;
    }

    public static ClusterRegistry getLocalRegistry(NamingContextHostPort[] hp)
        throws MalformedURLException, RemoteException {
        ClusterRegistry creg = getRegistry(hp);
        if (creg instanceof ClusterStub)
            throw new MalformedURLException("Can not bind or unbind in multiple machines");
        return creg;
    }

    public static Object lookup(String name)
        throws MalformedURLException, NotBoundException, RemoteException {
        NamingContext nc = new NamingContext(name);
        ClusterRegistry reg = getRegistry(nc.hp);
        if (nc.name.length() == 0)
            return reg;
        return reg.lookup(nc.name);
    }

    public static void bind(String name, Remote obj)
        throws MalformedURLException, AlreadyBoundException, RemoteException {
        NamingContext nc = new NamingContext(name);
        ClusterRegistry reg = getLocalRegistry(nc.hp);
        if (obj == null)
            throw new NullPointerException("cannot bind null object");
        reg.bind(nc.name, obj);
    }

    public static void rebind(String name, Remote obj)
        throws MalformedURLException, RemoteException {
        NamingContext nc = new NamingContext(name);
        ClusterRegistry reg = getLocalRegistry(nc.hp);
        if (obj == null)
            throw new NullPointerException("cannot bind null object");
        reg.rebind(nc.name, obj);
    }

    public static void unbind(String name)
        throws MalformedURLException, NotBoundException, RemoteException {
        NamingContext nc = new NamingContext(name);
        ClusterRegistry reg = getLocalRegistry(nc.hp);
        reg.unbind(nc.name);
    }

    public static String[] list(String name)
        throws MalformedURLException, RemoteException {
        NamingContext nc = new NamingContext(name);
        ClusterRegistry reg = getRegistry(nc.hp);

        String prefix = nc.scheme.equals("") ? "" : nc.scheme + ":";
        prefix += "//";
        int i = 0;
        while (i < nc.hp.length) {
            prefix += nc.hp[i].host;
            if (nc.hp[i].port != LowerOrb.DEFAULT_CREG_PORT)
                prefix += ":" + nc.hp[i].port;
            i++;
            if (i < nc.hp.length)
                prefix += ",";
        }
        prefix += "/";

        String lst[] = reg.list();
        for (i = 0; i < lst.length; i++)
            lst[i] = prefix + lst[i];
        return lst;
    }
}
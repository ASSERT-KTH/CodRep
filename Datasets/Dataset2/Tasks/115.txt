provider = (String) myEnv.get(Context.PROVIDER_URL);

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
/*
 * @(#)FlatCtx.java	1.4 99/10/15
 *
 * Copyright 1997, 1998, 1999 Sun Microsystems, Inc. All Rights
 * Reserved.
 *
 * Sun grants you ("Licensee") a non-exclusive, royalty free,
 * license to use, modify and redistribute this software in source and
 * binary code form, provided that i) this copyright notice and license
 * appear on all copies of the software; and ii) Licensee does not
 * utilize the software in a manner which is disparaging to Sun.
 *
 * This software is provided "AS IS," without a warranty of any
 * kind. ALL EXPRESS OR IMPLIED CONDITIONS, REPRESENTATIONS AND
 * WARRANTIES, INCLUDING ANY IMPLIED WARRANTY OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE OR NON-INFRINGEMENT, ARE
 * HEREBY EXCLUDED.  SUN AND ITS LICENSORS SHALL NOT BE LIABLE
 * FOR ANY DAMAGES SUFFERED BY LICENSEE AS A RESULT OF USING,
 * MODIFYING OR DISTRIBUTING THE SOFTWARE OR ITS DERIVATIVES. IN
 * NO EVENT WILL SUN OR ITS LICENSORS BE LIABLE FOR ANY LOST
 * REVENUE, PROFIT OR DATA, OR FOR DIRECT, INDIRECT, SPECIAL,
 * CONSEQUENTIAL, INCIDENTAL OR PUNITIVE DAMAGES, HOWEVER
 * CAUSED AND REGARDLESS OF THE THEORY OF LIABILITY, ARISING OUT
 * OF THE USE OF OR INABILITY TO USE SOFTWARE, EVEN IF SUN HAS
 * BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.
 *
 * This software is not designed or intended for use in on-line
 * control of aircraft, air traffic, aircraft navigation or aircraft
 * communications; or in the design, construction, operation or
 * maintenance of any nuclear facility. Licensee represents and warrants
 * that it will not use or redistribute the Software for such purposes.
 */
package org.objectweb.carol.cmi.jndi;

import java.rmi.AccessException;
import java.rmi.RemoteException;
import java.util.Hashtable;

import javax.naming.CompositeName;
import javax.naming.Context;
import javax.naming.InvalidNameException;
import javax.naming.Name;
import javax.naming.NameAlreadyBoundException;
import javax.naming.NameClassPair;
import javax.naming.NameNotFoundException;
import javax.naming.NameParser;
import javax.naming.NamingEnumeration;
import javax.naming.NamingException;
import javax.naming.OperationNotSupportedException;
import javax.naming.Reference;
import javax.naming.Referenceable;
import javax.naming.spi.NamingManager;

import org.objectweb.carol.cmi.ClusterRegistry;
import org.objectweb.carol.util.configuration.TraceCarol;

/**
 * A sample service provider that implements a flat namespace in memory.
 */

class FlatCtx implements Context {
    private Hashtable myEnv = null;
    private String provider = null;
    private static NameParser myParser = new FlatNameParser();
    private ClusterRegistry reg;

    FlatCtx(Hashtable environment) throws NamingException {
        if (environment != null) {
            myEnv = (Hashtable) (environment.clone());
            provider = (String) myEnv.get("java.naming.provider.url");
        }
        if (provider == null) {
            provider = "cmi:";
        }
        org.objectweb.carol.cmi.NamingContext nc;
        try {
            nc = new org.objectweb.carol.cmi.NamingContext(provider);
        } catch (java.net.MalformedURLException e) {
            throw new NamingException(e.toString());
        }
        try {
            reg = org.objectweb.carol.cmi.Naming.getRegistry(nc.hp);
        } catch (java.rmi.RemoteException e) {
            throw new NamingException(e.toString());
        }
    }

    public Object lookup(String name) throws NamingException {
        if (TraceCarol.isDebugJndiCarol())
            TraceCarol.debugJndiCarol("lookup(" + name + ")");
        if (name.equals("")) {
            // Asking to look up this context itself.  Create and return
            // a new instance with its own independent environment.
            return (new FlatCtx(myEnv));
        }
        try {
            Object obj = reg.lookup(name);
            if (obj instanceof RemoteReference) {
                return NamingManager.getObjectInstance(
                    ((RemoteReference) obj).getReference(),
                    null,
                    this,
                    this.myEnv);
            }
            if (TraceCarol.isDebugJndiCarol())
                TraceCarol.debugJndiCarol("lookup(" + name + ") returned");
            return obj;
        } catch (java.rmi.NotBoundException e) {
            throw new NameNotFoundException(e.toString());
        } catch (Exception e) {
            throw new NamingException(e.toString());
        }
    }

    public Object lookup(Name name) throws NamingException {
        // Flat namespace; no federation; just call string version
        return lookup(name.toString());
    }

    public void bind(String name, Object obj) throws NamingException {
        if (TraceCarol.isDebugJndiCarol())
            TraceCarol.debugJndiCarol("bind(" + name + ")");
        if (name.equals("")) {
            throw new InvalidNameException("Cannot bind empty name");
        }
        Object o = NamingManager.getStateToBind(obj, null, this, myEnv);
        try {
            if (o instanceof java.rmi.Remote) {
                reg.bind(name, (java.rmi.Remote) o);
            } else if (o instanceof Reference) {
                reg.bind(name, new ReferenceImpl((Reference) o));
            } else if (o instanceof Referenceable) {
                reg.bind(
                    name,
                    new ReferenceImpl(((Referenceable) o).getReference()));
            } else
                throw new NamingException(
                    "object to bind must be Remote : "
                        + obj.getClass().getName());
        } catch (java.rmi.RemoteException e) {
            throw new NamingException(e.toString());
        } catch (java.rmi.AlreadyBoundException e) {
            throw new NameAlreadyBoundException(e.toString());
        }
    }

    public void bind(Name name, Object obj) throws NamingException {
        // Flat namespace; no federation; just call string version
        bind(name.toString(), obj);
    }

    public void rebind(String name, Object obj) throws NamingException {
        if (TraceCarol.isDebugJndiCarol())
            TraceCarol.debugJndiCarol("rebind(" + name + ")");
        if (name.equals("")) {
            throw new InvalidNameException("Cannot bind empty name");
        }
        Object o = NamingManager.getStateToBind(obj, null, this, myEnv);
        try {
            if (o instanceof java.rmi.Remote) {
                reg.rebind(name, (java.rmi.Remote) o);
            } else if (o instanceof Reference) {
                reg.rebind(name, new ReferenceImpl((Reference) o));
            } else if (o instanceof Referenceable) {
                reg.rebind(
                    name,
                    new ReferenceImpl(((Referenceable) o).getReference()));
            } else
                throw new NamingException(
                    "object to bind must be Remote : "
                        + obj.getClass().getName());
        } catch (java.rmi.RemoteException e) {
            throw new NamingException(e.toString());
        }
    }

    public void rebind(Name name, Object obj) throws NamingException {
        // Flat namespace; no federation; just call string version
        rebind(name.toString(), obj);
    }

    public void unbind(String name) throws NamingException {
        if (TraceCarol.isDebugJndiCarol())
            TraceCarol.debugJndiCarol("unbind(" + name + ")");
        if (name.equals("")) {
            throw new InvalidNameException("Cannot unbind empty name");
        }
        try {
            reg.unbind(name);
        } catch (java.rmi.RemoteException e) {
            throw new NamingException(e.toString());
        } catch (java.rmi.NotBoundException e) {
            throw new NameNotFoundException(e.toString());
        }
    }

    public void unbind(Name name) throws NamingException {
        // Flat namespace; no federation; just call string version
        unbind(name.toString());
    }

    public void rename(String oldname, String newname) throws NamingException {
        throw new NamingException("not supported");
    }

    public void rename(Name oldname, Name newname) throws NamingException {
        // Flat namespace; no federation; just call string version
        rename(oldname.toString(), newname.toString());
    }

    public NamingEnumeration list(String name) throws NamingException {
        try {
            return new CmiNames(reg.list());
        } catch (AccessException e) {
            throw new NamingException(e.toString());
        } catch (RemoteException e) {
            throw new NamingException(e.toString());
        }
    }

    public NamingEnumeration list(Name name) throws NamingException {
        // Flat namespace; no federation; just call string version
        return list(name.toString());
    }

    public NamingEnumeration listBindings(String name) throws NamingException {
        throw new NamingException("not supported");
    }

    public NamingEnumeration listBindings(Name name) throws NamingException {
        // Flat namespace; no federation; just call string version
        return listBindings(name.toString());
    }

    public void destroySubcontext(String name) throws NamingException {
        throw new OperationNotSupportedException("FlatCtx does not support subcontexts");
    }

    public void destroySubcontext(Name name) throws NamingException {
        // Flat namespace; no federation; just call string version
        destroySubcontext(name.toString());
    }

    public Context createSubcontext(String name) throws NamingException {
        throw new OperationNotSupportedException("FlatCtx does not support subcontexts");
    }

    public Context createSubcontext(Name name) throws NamingException {
        // Flat namespace; no federation; just call string version
        return createSubcontext(name.toString());
    }

    public Object lookupLink(String name) throws NamingException {
        // This flat context does not treat links specially
        return lookup(name);
    }

    public Object lookupLink(Name name) throws NamingException {
        // Flat namespace; no federation; just call string version
        return lookupLink(name.toString());
    }

    public NameParser getNameParser(String name) throws NamingException {
        return myParser;
    }

    public NameParser getNameParser(Name name) throws NamingException {
        // Flat namespace; no federation; just call string version
        return getNameParser(name.toString());
    }

    public String composeName(String name, String prefix)
        throws NamingException {
        Name result =
            composeName(new CompositeName(name), new CompositeName(prefix));
        return result.toString();
    }

    public Name composeName(Name name, Name prefix) throws NamingException {
        Name result = (Name) (prefix.clone());
        result.addAll(name);
        return result;
    }

    public Object addToEnvironment(String propName, Object propVal)
        throws NamingException {
        if (myEnv == null) {
            myEnv = new Hashtable(5, 0.75f);
        }
        return myEnv.put(propName, propVal);
    }

    public Object removeFromEnvironment(String propName)
        throws NamingException {
        if (myEnv == null)
            return null;

        return myEnv.remove(propName);
    }

    public Hashtable getEnvironment() throws NamingException {
        if (myEnv == null) {
            // Must return non-null
            return new Hashtable(3, 0.75f);
        } else {
            return (Hashtable) myEnv.clone();
        }
    }

    public String getNameInNamespace() throws NamingException {
        return "";
    }

    public void close() throws NamingException {
        myEnv = null;
        reg = null;
    }

    // Class for enumerating name/class pairs
    class CmiNames implements NamingEnumeration {
        String[] names;
        int index = 0;

        CmiNames (String[] names) {
            this.names = names;
        }

        public boolean hasMoreElements() {
            return index < names.length;
        }

        public boolean hasMore() throws NamingException {
            return hasMoreElements();
        }

        public Object nextElement() {
            String name = names[index++];
            String className = "java.lang.Object";
            return new NameClassPair(name, className);
        }

        public Object next() throws NamingException {
            return nextElement();
        }

        public void close() throws NamingException {
        names=null;
        }
    }
}
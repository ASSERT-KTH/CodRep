"org.objectweb.jeremie.services.registry.jndi.JRMIInitialContextFactory");

/*
 * Created on Nov 26, 2003
 *
 * To change the template for this generated file go to
 * Window - Preferences - Java - Code Generation - Code and Comments
 */
package org.objectweb.carol.jndi.spi;
import java.io.Serializable;
import java.rmi.Remote;
import java.util.Hashtable;
import java.util.HashMap;
import javax.naming.CompositeName;
import javax.naming.Context;
import javax.naming.InitialContext;
import javax.naming.Name;
import javax.naming.NameParser;
import javax.naming.NamingEnumeration;
import javax.naming.NamingException;
import javax.naming.Reference;
import javax.naming.Referenceable;

import org.objectweb.carol.jndi.wrapping.JNDIRemoteResource;
import org.objectweb.carol.jndi.wrapping.JNDIResourceWrapper;
import org.objectweb.carol.util.configuration.CarolCurrentConfiguration;

/**
 * @author riviereg
 *
 * To change the template for this generated type comment go to
 * Window - Preferences - Java - Code Generation - Code and Comments
 */
public class JEREMIEContext implements Context {
	/**
	 * the JEREMIE JNDI context
	 * @see #JEREMIEContext
	 */
	private static Context jeremieContext = null;

	/**
	 * the mapping between URL and wrapped context
	 * @see #JEREMIEContext
	 */
    private static HashMap hashMap = new HashMap();

	/**
	 * the Exported Wrapper Hashtable
	 *
	 */
	private static Hashtable wrapperHash = new Hashtable();

	/**
	 * Constructs an JEREMIE Wrapper context 
	 * @param jeremieContext the inital JEREMIE context
	 *
	 * @throws NamingException if a naming exception is encountered
	 */
	private JEREMIEContext(Context jeremieCtx) throws NamingException {
		jeremieContext = jeremieCtx;
	
	}

	/**
	* 
	* @param o
	* @param name
	* @return
	* @throws NamingException
	*/
	public static Context getSingleInstance(Hashtable env)
		throws NamingException {
        String key = null;
        if (env != null) {
            key = (String) env.get(Context.PROVIDER_URL);
        }
        Context ctx = (Context) hashMap.get(key);
        if (ctx == null) {
			env.put(
				"java.naming.factory.initial",
                "org.objectweb.jeremie.libs.services.registry.jndi.JRMIInitialContextFactory");
			ctx = new JEREMIEContext(new InitialContext(env));
            hashMap.put(key, ctx);
		}
		return ctx;
	}

	/**
	 * Unwrap a Remote Object: 
	 * If this object is a serializable wrapper return the serializable 
	 *
	 * @param o the object to resolve
	 * @return the serializable object
	 */
	private Object unwrapObject(Object o, Name name) throws NamingException {
		try {
			//TODO: May we can do a narrow ? 
			if (o instanceof JNDIRemoteResource) {
				return ((JNDIRemoteResource) o).getResource();
			} else {
				return o;
			}
		} catch (Exception e) {
			e.printStackTrace();
			throw new NamingException("" + e);
		}
	}

	/**
	 * Encode an Object :
	 * If the object is a reference wrap it into a JNDIResourceWrapper Object
	 * here the good way is to contact the carol configuration to get the jeremie
	 * protable remote object
	 *
	 * @param o the object to encode
	 * @return  a <code>Remote JNDIRemoteReference Object</code> if o is a ressource
	 *          o if else
	 */
	private Object wrapObject(Object o, Object name, boolean replace)
		throws NamingException {
		try {
			if ((!(o instanceof Remote))
				&& (!(o instanceof Referenceable))
				&& (!(o instanceof Reference))
				&& (o instanceof Serializable)) {
				JNDIResourceWrapper irw =
					new JNDIResourceWrapper((Serializable) o);
				CarolCurrentConfiguration
					.getCurrent()
					.getCurrentPortableRemoteObject()
					.exportObject(
					irw);
				Remote oldObj =
					(Remote) wrapperHash.put(name, irw);
				if (oldObj != null) {
					if (replace) {
						CarolCurrentConfiguration
							.getCurrent()
							.getCurrentPortableRemoteObject()
							.unexportObject(
							oldObj);
					} else {
						CarolCurrentConfiguration
							.getCurrent()
							.getCurrentPortableRemoteObject()
							.unexportObject(
							irw);
						wrapperHash.put(name, oldObj);
						throw new NamingException("Object already bind");
					}
				}
				return irw;
			} else {
				return o;
			}
		} catch (Exception e) {
			throw new NamingException("" + e);
		}
	}

	// Context methods
	// The Javadoc is deferred to the Context interface.

	public Object lookup(Name name) throws NamingException {
		return unwrapObject(jeremieContext.lookup(name), name);
	}

	public Object lookup(String name) throws NamingException {
		return lookup(new CompositeName(name));
	}

	public void bind(Name name, Object obj) throws NamingException {
		jeremieContext.bind(name, wrapObject(obj, name, false));
	}

	public void bind(String name, Object obj) throws NamingException {
		bind(new CompositeName(name), obj);
	}

	public void rebind(Name name, Object obj) throws NamingException {
		jeremieContext.rebind(name, wrapObject(obj, name, true));
	}

	public void rebind(String name, Object obj) throws NamingException {
		rebind(new CompositeName(name), obj);
	}

	public void unbind(Name name) throws NamingException {
		try {
			jeremieContext.unbind(name);
			if (wrapperHash.containsKey(name)) {
				CarolCurrentConfiguration
					.getCurrent()
					.getCurrentPortableRemoteObject()
					.unexportObject(
					(Remote) wrapperHash.remove(name));
			}
		} catch (Exception e) {
			throw new NamingException("" + e);
		}
	}

	public void unbind(String name) throws NamingException {
		unbind(new CompositeName(name));
	}

	public void rename(Name oldName, Name newName) throws NamingException {
		if (wrapperHash.containsKey(oldName)) {
			wrapperHash.put(newName, wrapperHash.remove(oldName));
		}
		jeremieContext.rename(oldName, newName);
	}

	public void rename(String name, String newName) throws NamingException {
		rename(new CompositeName(name), new CompositeName(newName));
	}

	public NamingEnumeration list(Name name) throws NamingException {
		return jeremieContext.list(name);
	}

	public NamingEnumeration list(String name) throws NamingException {
		return list(new CompositeName(name));
	}

	public NamingEnumeration listBindings(Name name) throws NamingException {
		return jeremieContext.listBindings(name);
	}

	public NamingEnumeration listBindings(String name) throws NamingException {
		return listBindings(new CompositeName(name));
	}

	public void destroySubcontext(Name name) throws NamingException {
		jeremieContext.destroySubcontext(name);
	}

	public void destroySubcontext(String name) throws NamingException {
		destroySubcontext(new CompositeName(name));
	}

	public Context createSubcontext(Name name) throws NamingException {
		return jeremieContext.createSubcontext(name);
	}

	public Context createSubcontext(String name) throws NamingException {
		return createSubcontext(new CompositeName(name));
	}

	public Object lookupLink(Name name) throws NamingException {
		return jeremieContext.lookupLink(name);
	}

	public Object lookupLink(String name) throws NamingException {
		return lookupLink(new CompositeName(name));
	}

	public NameParser getNameParser(Name name) throws NamingException {
		return jeremieContext.getNameParser(name);
	}

	public NameParser getNameParser(String name) throws NamingException {
		return getNameParser(new CompositeName(name));
	}

	public String composeName(String name, String prefix)
		throws NamingException {
		return name;
	}

	public Name composeName(Name name, Name prefix) throws NamingException {
		return (Name) name.clone();
	}

	public Object addToEnvironment(String propName, Object propVal)
		throws NamingException {
		return jeremieContext.addToEnvironment(propName, propVal);
	}

	public Object removeFromEnvironment(String propName)
		throws NamingException {
		return jeremieContext.removeFromEnvironment(propName);
	}

	public Hashtable getEnvironment() throws NamingException {
		return jeremieContext.getEnvironment();
	}

	public void close() throws NamingException {
		// do nothing for the moment
	}

	public String getNameInNamespace() throws NamingException {
		return jeremieContext.getNameInNamespace();
	}

}
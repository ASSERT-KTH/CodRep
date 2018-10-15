private transient ClassLoader classLoader = null;

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/

package org.eclipse.ecf.core.identity;

import java.io.Serializable;
import java.net.URI;
import java.net.URISyntaxException;

import org.eclipse.ecf.core.identity.provider.IDInstantiator;

/**
 * Namespace class. This class defines the properties associated with an
 * identity Namespace. Namespaces are defined by a unique 'name' (e.g. 'email',
 * 'icq', 'aolim'), and an 'instantiatorClass'. The instantiator class defines a
 * class that implements the org.eclipse.ecf.identity.provider.IDInstantiator
 * interface and is responsible for creating instances of the given namespace.
 * The instances created by the instantiatorClass <b>must </b> implement the
 * org.eclipse.ecf.identity.ID interface, but otherwise can provide any other
 * identity functionality desired.
 * 
 */
public class Namespace implements Serializable {

    private String name;
    private String instantiatorClass;
    private String description;

    private int hashCode = 0;
    private ClassLoader classLoader = null;

    private transient IDInstantiator instantiator = null;

    public Namespace(ClassLoader cl, String name, String instantiatorClass,
            String desc) {
        this.classLoader = cl;
        this.name = name;
        this.instantiatorClass = instantiatorClass;
        this.description = desc;
        this.hashCode = name.hashCode();
    }
    public Namespace(String name, IDInstantiator inst, String desc) {
        this.instantiator = inst;
        this.instantiatorClass = this.instantiator.getClass().getName();
        this.classLoader = this.instantiator.getClass().getClassLoader();
        this.name = name;
        this.description = desc;
        this.hashCode = name.hashCode();
    }
    /**
     * Override of Object.equals. This equals method returns true if the
     * provided Object is also a Namespace instance, and the names of the two
     * instances match.
     * 
     * @param other
     *            the Object to test for equality
     */
    public boolean equals(Object other) {
        if (!(other instanceof Namespace))
            return false;
        return ((Namespace) other).name.equals(name);
    }

    public String getDescription() {
        return description;
    }

    /**
     * Get an ISharedObjectContainerInstantiator using the classloader used to
     * load the Namespace class
     * 
     * @return ISharedObjectContainerInstantiator associated with this Namespace
     *         instance
     * @exception Exception
     *                thrown if instantiator class cannot be loaded, or if it
     *                cannot be cast to ISharedObjectContainerInstantiator
     *                interface
     */
    protected IDInstantiator getInstantiator() throws ClassNotFoundException,
            InstantiationException, IllegalAccessException {
        synchronized (this) {
            if (instantiator == null)
                initializeInstantiator(classLoader);
            return instantiator;
        }
    }

    protected boolean testIDEquals(BaseID first, BaseID second) {
        // First check that namespaces are the same and non-null
        Namespace sn = second.getNamespace();
        if (sn == null || !this.equals(sn))
            return false;
        return first.namespaceEquals(second);
    }
    protected String getNameForID(BaseID id) {
        return id.namespaceGetName();
    }
    protected URI getURIForID(BaseID id) throws URISyntaxException {
        return id.namespaceToURI();
    }
    protected int getCompareToForObject(BaseID first, BaseID second) {
        return first.namespaceCompareTo(second);
    }
    protected int getHashCodeForID(BaseID id) {
        return id.namespaceHashCode();
    }

    /**
     * @return String name of Namespace instance
     * 
     */
    public String getName() {
        return name;
    }

    protected String getPermissionName() {
        return toString();
    }

    public int hashCode() {
        return hashCode;
    }
    protected void initializeInstantiator(ClassLoader cl)
            throws ClassNotFoundException, InstantiationException,
            IllegalAccessException {
        if (cl == null)
            classLoader = this.getClass().getClassLoader();
        // Load instantiator class
        Class clazz = Class.forName(instantiatorClass, true, classLoader);
        // Make new instance
        instantiator = (IDInstantiator) clazz.newInstance();
    }

    public String toString() {
        StringBuffer b = new StringBuffer("Namespace[");
        b.append(name).append(";");
        b.append(instantiatorClass).append(";");
        b.append(description).append("]");
        return b.toString();
    }
}
 No newline at end of file
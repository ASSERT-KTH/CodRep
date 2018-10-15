namespace = IDFactory.getDefault().getNamespaceByName(StringID.class.getName());

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/

package org.eclipse.ecf.core.identity;

import java.net.URI;
import java.net.URISyntaxException;

import org.eclipse.ecf.core.identity.provider.IDInstantiator;

/**
 * A string-based identity
 * 
 * @author Scott B. Lewis, slewis@composent.com
 */
public class StringID extends BaseID {

	private static final long serialVersionUID = 3256437019155446068L;
	public static class Creator implements IDInstantiator {
        public ID makeInstance(Namespace ns, Class[] argTypes, Object[] args)
                throws IDInstantiationException {
            return new StringID(ns, (String) args[0]);
        }
    }
    public static final String STRINGID_INSTANTIATOR_CLASS = StringID.Creator.class
            .getName();

    public static final String STRINGID_NAME = StringID.class.getName();

    protected String value;

    /**
     * Protected constructor for factory-based construction
     * 
     * @param n
     *            the Namespace this identity will belong to
     * @param s
     *            the String defining this StringID
     */
    protected StringID(Namespace n, String s) {
        super(n);
        value = s;
        setEmptyNamespace();
    }
    public int compareTo(Object o) {
        setEmptyNamespace();
        return super.compareTo(o);
    }
    public boolean equals(Object o) {
        setEmptyNamespace();
        return super.equals(o);
    }
    public String getName() {
        setEmptyNamespace();
        return super.getName();
    }
    public int hashCode() {
        setEmptyNamespace();
        return super.hashCode();
    }
    public Namespace getNamespace() {
        setEmptyNamespace();
        return namespace;
    }
    public String toString() {
        setEmptyNamespace();
        int strlen = value.length();
        StringBuffer sb = new StringBuffer(strlen + 10);
        sb.insert(0, "StringID[").insert(9, value).insert(strlen + 9, ']');
        return sb.toString();
    }
    public URI toURI() throws URISyntaxException {
        setEmptyNamespace();
        return super.toURI();
    }
    protected int namespaceCompareTo(BaseID obj) {
        return getName().compareTo(obj.getName());
    }
    protected boolean namespaceEquals(BaseID obj) {
        if (!(obj instanceof StringID))
            return false;
        StringID o = (StringID) obj;
        return value.equals(o.getName());
    }
    protected String namespaceGetName() {
        return value;
    }
    protected int namespaceHashCode() {
        return value.hashCode() ^ getClass().hashCode();
    }
    protected URI namespaceToURI() throws URISyntaxException {
        return new URI(getName());
    }
    protected synchronized void setEmptyNamespace() {
        if (namespace == null) {
            namespace = IDFactory.getNamespaceByName(StringID.class.getName());
        }
    }
}
 No newline at end of file
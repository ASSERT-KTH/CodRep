public void setProperties(Map props) {

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/

package org.eclipse.ecf.core;

import java.io.Serializable;
import java.util.Hashtable;
import java.util.Map;

import org.eclipse.ecf.core.identity.ID;

/**
 * Description of an ISharedObject instance.
 * 
 * @see org.eclipse.ecf.core.ISharedObjectManager#createSharedObject(SharedObjectDescription, ISharedObjectContainerTransaction)
 */
public class SharedObjectDescription implements Serializable {

	private static final long serialVersionUID = 3257848783613146929L;

	protected static long staticID = 0;

    protected transient ClassLoader classLoader;
    protected ID id;
    protected ID homeID;
    protected String className;
    protected Map properties;
    protected long identifier;

    public static long getNextUniqueIdentifier() {
        return staticID++;
    }
    public SharedObjectDescription(ClassLoader loader, ID objectID, ID homeID,
            String className, Map dict, long ident) {
        this.classLoader = loader;
        this.id = objectID;
        this.homeID = homeID;
        this.className = className;
        if (dict != null) this.properties = dict;
        else this.properties = new Hashtable();
        this.identifier = ident;
    }

    public SharedObjectDescription(ClassLoader loader, ID id, String className, Map dict, long ident) {
        this(loader, id, null, className, dict, ident);
    }
    public SharedObjectDescription(ID id, Class clazz, Map dict, long ident) {
        this(clazz.getClassLoader(),id,clazz.getName(),dict,ident);
    }
    public SharedObjectDescription(ClassLoader loader, ID id, String className, Map dict) {
        this(loader, id, null, className, dict, getNextUniqueIdentifier());
    }
    public SharedObjectDescription(ClassLoader loader, ID id, String className) {
        this(loader, id, null, className, null, getNextUniqueIdentifier());
    }
    public SharedObjectDescription(ID id, String className, Map dict, long ident) {
        this(null, id, null, className, dict, ident);
    }
    public SharedObjectDescription(ID id, String className, Map dict) {
        this(null, id, null, className, dict, getNextUniqueIdentifier());
    }
    public SharedObjectDescription(ID id, Class clazz, Map dict) {
        this(id,clazz,dict,getNextUniqueIdentifier());
    }
    public SharedObjectDescription(ID id, String className, long ident) {
        this(null, id, null, className, null, ident);
    }
    public SharedObjectDescription(ID id, Class clazz, long ident) {
        this(id,clazz,null,ident);
    }
    public SharedObjectDescription(ID id, String className) {
        this(id, className, getNextUniqueIdentifier());
    }
    public SharedObjectDescription(ID id, Class clazz) {
        this(id,clazz,null);
    }
    public ID getID() {
        return id;
    }
    public void setID(ID theID) {
        this.id = theID;
    }
    public ID getHomeID() {
        return homeID;
    }
    public void setHomeID(ID theID) {
        this.homeID = theID;
    }
    public String getClassname() {
        return className;
    }
    public void setClassname(String theName) {
        this.className = theName;
    }
    public Map getProperties() {
        return properties;
    }
    public void getProperties(Map props) {
        this.properties = props;
    }
    public ClassLoader getClassLoader() {
        return classLoader;
    }
    public long getIdentifier() {
        return identifier;
    }
    public void setIdentifier(long identifier) {
        this.identifier = identifier;
    }
    
    public String toString() {
        StringBuffer sb = new StringBuffer("SharedObjectDescription[");
        sb.append("classLoader:").append(classLoader).append(";");
        sb.append("id:").append(id).append(";");
        sb.append("homeID:").append(homeID).append(";");
        sb.append("class:").append(className).append(";");
        sb.append("props:").append(properties).append(";");
        sb.append("ident:").append(identifier).append("]");
        return sb.toString();
    }
}
 No newline at end of file
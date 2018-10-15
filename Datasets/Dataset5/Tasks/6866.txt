public interface ISharedObjectContainerConfig extends IIdentifiable {

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/

package org.eclipse.ecf.core;

import java.util.Map;

/**
 * Configuration information associated with ISharedObjectContainer.
 *
 * @see ISharedObjectContainer#getConfig()
 */
public interface ISharedObjectContainerConfig extends IIDentifiable {

    /**
     * The properties associated with the owner ISharedObjectContainer
     * 
     * @return Map the properties associated with owner
     *         ISharedObjectContainer
     */
    public Map getProperties();
    /**
     * Returns an object which is an instance of the given class associated with
     * this object.
     * 
     * @param clazz
     *            the adapter class to lookup
     * @return Object a object castable to the given class, or null if this
     *         object does not have an adapter for the given class
     */
    public Object getAdapter(Class clazz);
}
 No newline at end of file
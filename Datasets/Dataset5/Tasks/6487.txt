package org.eclipse.ecf.provider.util;

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.core.util;

/**
 * Map a given name onto a classloader. The container that provides an
 * IClassLoaderMapper to the constructor of an IdentifiableObjectInputStream can
 * use the name provided to lookup a shared object of same name and map that
 * name to a classloader instance
 * 
 */
public interface IClassLoaderMapper {
	public ClassLoader mapNameToClassLoader(String name);
}
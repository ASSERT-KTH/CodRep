import org.eclipse.ecf.core.sharedobject.ISharedObjectContainer;

/*******************************************************************************
 * Copyright (c) 2004 Peter Nehrer and Composent, Inc.
 * All rights reserved. This program and the accompanying materials 
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors:
 *     Peter Nehrer - initial API and implementation
 *******************************************************************************/
package org.eclipse.ecf.sdo;

import org.eclipse.ecf.core.ISharedObjectContainer;
import org.eclipse.ecf.core.util.ECFException;

/**
 * @author pnehrer
 */
public interface IDataGraphSharingManager {

	IDataGraphSharing getInstance(ISharedObjectContainer container)
			throws ECFException;
}
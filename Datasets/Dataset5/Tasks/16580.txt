public ISynchAsynchConnection createInstance(

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.core.comm.provider;

import org.eclipse.ecf.core.comm.ConnectionDescription;
import org.eclipse.ecf.core.comm.ConnectionInstantiationException;
import org.eclipse.ecf.core.comm.ISynchAsynchConnection;
import org.eclipse.ecf.core.comm.ISynchAsynchConnectionEventHandler;

public interface ISynchAsynchConnectionInstantiator {
	public ISynchAsynchConnection makeInstance(
			ConnectionDescription description,
			ISynchAsynchConnectionEventHandler handler, Class[] clazzes,
			Object[] args) throws ConnectionInstantiationException;
}
 No newline at end of file
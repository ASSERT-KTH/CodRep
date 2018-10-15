package org.eclipse.ecf.provider.comm;

/****************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Composent, Inc. - initial API and implementation
 *****************************************************************************/
package org.eclipse.ecf.core.comm;

/**
 * Event handler callback interface for connections that have both asynchronous
 * and synchronous capabilities
 * 
 * @author slewis
 * 
 */
public interface ISynchAsynchEventHandler extends ISynchEventHandler,
		IAsynchEventHandler {
}
 No newline at end of file
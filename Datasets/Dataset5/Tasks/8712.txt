package org.eclipse.ecf.internal.example.collab.ui;

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

package org.eclipse.ecf.example.collab.ui;

import java.io.File;

import org.eclipse.ecf.core.identity.ID;

public interface FileReceiverUI {

	public void receiveStart(ID from, File aFile, long length, float rate);
	public void receiveData(ID from, File aFile, int dataLength);
	public void receiveDone(ID from, File aFile, Exception e);

}
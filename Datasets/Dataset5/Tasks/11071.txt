StringBuffer buf = new StringBuffer("PingResponseMessage[]"); //$NON-NLS-1$

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

package org.eclipse.ecf.provider.comm.tcp;

import java.io.Serializable;

public class PingResponseMessage implements Serializable {
	private static final long serialVersionUID = 3257569516165740857L;

	protected PingResponseMessage() {
    }

    public String toString() {
        StringBuffer buf = new StringBuffer("PingResponseMessage");
        return buf.toString();
    }
}
 No newline at end of file
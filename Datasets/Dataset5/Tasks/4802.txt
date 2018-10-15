package org.eclipse.ecf.internal.provider.xmpp.deprecated;

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
package org.eclipse.ecf.provider.xmpp.container;

import java.io.Serializable;

public class SharedObjectMsg implements Serializable {
    
    private static final long serialVersionUID = 3257002168199360564L;
    String msg;
    String param;
    
    public SharedObjectMsg(String msg, String param) {
        this.msg = msg;
        this.param = param;
    }
    public String getMsg() {
        return msg;
    }
    public String getParam() {
        return param;
    }
}
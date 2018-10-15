System.out.println("hello from="+from);

/*******************************************************************************
* Copyright (c) 2009 EclipseSource and others. All rights reserved. This
* program and the accompanying materials are made available under the terms of
* the Eclipse Public License v1.0 which accompanies this distribution, and is
* available at http://www.eclipse.org/legal/epl-v10.html
*
* Contributors:
*   EclipseSource - initial API and implementation
******************************************************************************/
package org.eclipse.ecf.examples.remoteservices.hello.impl;

import org.eclipse.ecf.examples.remoteservices.hello.IHello;

public class Hello implements IHello {

	public void hello(String from) {
		System.out.println(this.getClass().getName()+".hello from="+from);
	}

}
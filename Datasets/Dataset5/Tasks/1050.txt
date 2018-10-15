package org.eclipse.xtend.typesystem.emf.ui.internal;

/*******************************************************************************
 * Copyright (c) 2008 itemis AG (http://www.itemis.eu) and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 *******************************************************************************/
package org.eclipse.xtend.typesystem.emf.internal;

import org.eclipse.ui.IStartup;
import org.eclipse.xtend.typesystem.emf.check.CheckRegistry;

/**
 * @author Dennis Hübner - Initial contribution and API
 * 
 */
public class EarlyStarter implements IStartup {

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ui.IStartup#earlyStartup()
	 */
	public void earlyStartup() {
		CheckRegistry.getInstance();
	}

}
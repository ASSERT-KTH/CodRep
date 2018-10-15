package org.eclipse.ecf.internal.provisional.docshare.cola;

/****************************************************************************
 * Copyright (c) 2008 Mustafa K. Isik and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Mustafa K. Isik - initial API and implementation
 *****************************************************************************/

package org.eclipse.ecf.docshare.cola;

import org.eclipse.ecf.core.util.Trace;
import org.eclipse.ecf.internal.docshare.Activator;
import org.eclipse.ecf.internal.docshare.DocshareDebugOptions;

public class ColaReplacement implements TransformationStrategy {

	private static final long serialVersionUID = -7295023855308474804L;
	private static ColaReplacement INSTANCE;

	private ColaReplacement() {
		// default constructor is private to enforce singleton property via
		// static factory method
	}

	public static TransformationStrategy getInstance() {
		if (INSTANCE == null) {
			INSTANCE = new ColaReplacement();
		}
		return INSTANCE;
	}

	public ColaUpdateMessage getOperationalTransform(ColaUpdateMessage remoteMsg, ColaUpdateMessage appliedLocalMsg, boolean localMsgHighPrio) {
		Trace.entering(Activator.PLUGIN_ID, DocshareDebugOptions.METHODS_ENTERING, this.getClass(), "getOperationalTransform", new Object[] {remoteMsg, appliedLocalMsg, new Boolean(localMsgHighPrio)}); //$NON-NLS-1$

		// TODO Auto-generated method stub

		Trace.exiting(Activator.PLUGIN_ID, DocshareDebugOptions.METHODS_EXITING, this.getClass(), "getOperationalTransform", null); //$NON-NLS-1$

		return null;
	}

}
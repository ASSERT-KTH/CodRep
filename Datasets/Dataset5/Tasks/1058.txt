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

import java.io.Serializable;

public interface TransformationStrategy extends Serializable {

	ColaUpdateMessage getOperationalTransform(ColaUpdateMessage remoteIncomingMsg,
			ColaUpdateMessage localAppliedMsg, boolean localMsgHighPrio);
}
package org.eclipse.ecf.internal.ui.deprecated.views;

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
package org.eclipse.ecf.ui.views;

import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.ui.SharedImages;
import org.eclipse.swt.graphics.Image;

public class RosterAccount extends RosterGroup {

	public RosterAccount(String name, ID id) {
		super(name, id);
	}

	public String getLabel() {
		return getName();
	}

	public Image getImage() {
		return SharedImages.getImage(SharedImages.IMG_USER_AVAILABLE);
	}

}
 No newline at end of file
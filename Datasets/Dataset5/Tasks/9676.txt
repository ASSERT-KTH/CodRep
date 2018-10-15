import org.eclipse.wst.xml.vex.core.internal.provisional.dom.I.VEXElement;

/*******************************************************************************
 * Copyright (c) 2004, 2008 John Krasnay and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors:
 *     John Krasnay - initial API and implementation
 *******************************************************************************/
package org.eclipse.wst.xml.vex.core.internal.layout;

import org.eclipse.wst.xml.vex.core.internal.dom.Element;
import org.eclipse.wst.xml.vex.core.internal.provisional.dom.VEXElement;

public interface ElementOrRangeCallback {
	public void onElement(Element child, String displayStyle);

	public void onRange(VEXElement parent, int startOffset, int endOffset);
}
 No newline at end of file
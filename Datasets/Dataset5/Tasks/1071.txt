package org.eclipse.wst.xquery.core.text;

/*******************************************************************************
 * Copyright (c) 2008, 2009 28msec Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     Gabriel Petrovay (28msec) - initial API and implementation
 *******************************************************************************/
package org.eclipse.wst.xquery.internal.core.text;

import org.eclipse.jface.text.rules.IWordDetector;

public class XQDTWordDetector implements IWordDetector {

    /**
     * @see IWordDetector#isWordStart
     */
    public boolean isWordStart(char c) {
        return Character.isJavaIdentifierStart(c);
    }

    /**
     * @see IWordDetector#isWordPart
     */
    public boolean isWordPart(char c) {
        return ((Character.isJavaIdentifierPart(c) || c == '-' || c == '.') && c != '$');
    }
}
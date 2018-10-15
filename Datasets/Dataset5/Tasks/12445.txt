import org.eclipse.wst.xquery.set.core.ISETPreferenceConstants;

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
package org.eclipse.wst.xquery.set.internal.ui;

import java.util.ArrayList;
import java.util.List;

import org.eclipse.dltk.core.IMethod;
import org.eclipse.dltk.core.IModelElement;
import org.eclipse.dltk.core.IModelElementVisitor;
import org.eclipse.wst.xquery.set.internal.core.preferences.ISETPreferenceConstants;

public class HandlerCollector implements IModelElementVisitor {

    private List<IMethod> fHandlers = new ArrayList<IMethod>();

    public boolean visit(IModelElement element) {
        if (element.getElementType() == IModelElement.PROJECT_FRAGMENT
                && !element.getElementName().equals(ISETPreferenceConstants.DIR_NAME_HANDLER)) {
            return false;
        }
        if (element.getElementType() == IModelElement.METHOD) {
            fHandlers.add((IMethod)element);
            return false;
        }
        return true;
    }

    public IMethod[] getHandlers() {
        return fHandlers.toArray(new IMethod[fHandlers.size()]);
    }
}
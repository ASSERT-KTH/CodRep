package org.eclipse.wst.xquery.debug.ui.interpreters;

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
package org.eclipse.wst.xquery.internal.debug.ui.interpreters;

import org.eclipse.dltk.internal.debug.ui.interpreters.EnvironmentVariablesLabelProvider;
import org.eclipse.jface.dialogs.IDialogSettings;
import org.eclipse.jface.viewers.IBaseLabelProvider;

public class LocalInterpreterEnvironmentVariablesBlock extends AbstractInterpreterEnvironmentVariablesBlock {

    public LocalInterpreterEnvironmentVariablesBlock(GenericAddInterpreterDialog dialog) {
        super(dialog);
    }

    protected IBaseLabelProvider getLabelProvider() {
        return new EnvironmentVariablesLabelProvider();
    }

    protected IDialogSettings getDialogSettions() {
        return null;
    }

}
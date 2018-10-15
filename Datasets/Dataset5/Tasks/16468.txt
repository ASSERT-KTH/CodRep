IInterpreterRunner runner = super.getInterpreterRunner(mode);

/*******************************************************************************
 * Copyright (c) 2009 Mark Logic Corporation and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     Sam Neth (Mark Logic) - initial API and implementation
 *******************************************************************************/
package org.eclipse.wst.xquery.internal.launching.marklogic;

import org.eclipse.debug.core.ILaunchManager;
import org.eclipse.dltk.launching.IInterpreterInstallType;
import org.eclipse.dltk.launching.IInterpreterRunner;
import org.eclipse.wst.xquery.core.semantic.ISemanticValidator;
import org.eclipse.wst.xquery.launching.ISemanticValidatingInterpreterInstall;
import org.eclipse.wst.xquery.launching.XQDTInterpreterInstall;

public class MarkLogicInstall extends XQDTInterpreterInstall implements ISemanticValidatingInterpreterInstall {

    public MarkLogicInstall(IInterpreterInstallType type, String id) {
        super(type, id);
    }

    @Override
    public IInterpreterRunner getInterpreterRunner(String mode) {
        final IInterpreterRunner runner = super.getInterpreterRunner(mode);

        if (runner != null) {
            return runner;
        }

        if (mode.equals(ILaunchManager.RUN_MODE)) {
            return new MarkLogicRunner(this);
        }

        return null;
    }

    public ISemanticValidator getSemanticValidator() {
        return new MarkLogicSemanticValidator(this);
    }

}
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

import org.eclipse.core.runtime.IStatus;
import org.eclipse.dltk.core.environment.IEnvironment;
import org.eclipse.dltk.internal.debug.ui.interpreters.IAddInterpreterDialogRequestor;
import org.eclipse.dltk.launching.IInterpreterInstall;
import org.eclipse.dltk.ui.util.IStatusChangeListener;
import org.eclipse.jface.dialogs.IDialogConstants;
import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Shell;

public abstract class AbstractAddInterpreterDialogBlock implements IInterpreterNameProvider {

    protected IAddInterpreterDialogRequestor fRequestor;

    protected IInterpreterInstall fEditedInterpreter;

    protected GenericAddInterpreterDialog fAddInterpreterDialog;

    private Composite fContainer;

    public final void createControls(Composite comp) {
        fContainer = new Composite(comp, SWT.NONE);
        GridLayout layout = new GridLayout(3, false);
        layout.marginWidth = 0;
        layout.marginHeight = 0;
        layout.verticalSpacing = fAddInterpreterDialog.convertVerticalDLUsToPixels(IDialogConstants.VERTICAL_SPACING);
        layout.horizontalSpacing = fAddInterpreterDialog
                .convertHorizontalDLUsToPixels(IDialogConstants.HORIZONTAL_SPACING);
        fContainer.setLayout(layout);
        GridData gd = new GridData(GridData.FILL_BOTH);
        gd.horizontalSpan = 3;
        fContainer.setLayoutData(gd);

        addControlsTo(fContainer);
    }

    public void dispose() {
        if (fContainer != null) {
            fContainer.dispose();
        }
    }

    abstract protected void addControlsTo(Composite comp);

    public void initialize(GenericAddInterpreterDialog dialog, IAddInterpreterDialogRequestor requestor,
            IInterpreterInstall editedInterpreter) {
        fAddInterpreterDialog = dialog;
        fRequestor = requestor;
        fEditedInterpreter = editedInterpreter;
    }

    protected IEnvironment getEnvironemnt() {
        return fAddInterpreterDialog.getEnvironment();
    }

    protected Shell getShell() {
        return fAddInterpreterDialog.getShell();
    }

    protected IStatusChangeListener getStatusListener() {
        return fAddInterpreterDialog;
    }

    abstract public void initializeFields(IInterpreterInstall install);

    abstract protected IStatus validateInterpreterLocation();

    abstract protected IStatus validateInterpreterName();

    abstract public void setFieldValuesToInterpreter(IInterpreterInstall install);

    abstract protected String getInterpreterName();

    abstract protected String getInterpreterLocation();

    public void setFocus() {
    }

    public void createFieldListeners() {
    }

    protected int convertWidthInCharsToPixels(int chars) {
        return fAddInterpreterDialog.convertWidthInCharsToPixels(chars);
    }

}
 No newline at end of file
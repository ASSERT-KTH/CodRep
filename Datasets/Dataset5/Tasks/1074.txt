import org.eclipse.wst.xquery.debug.ui.interpreters.AbstractAddInterpreterDialogBlock;

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
package org.eclipse.wst.xquery.internal.debug.ui.marklogic.interpreters;

import java.net.URI;
import java.net.URISyntaxException;

import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Path;
import org.eclipse.core.runtime.Status;
import org.eclipse.dltk.compiler.util.Util;
import org.eclipse.dltk.core.environment.IEnvironment;
import org.eclipse.dltk.internal.debug.ui.interpreters.InterpretersMessages;
import org.eclipse.dltk.internal.launching.LazyFileHandle;
import org.eclipse.dltk.internal.ui.wizards.dialogfields.DialogField;
import org.eclipse.dltk.internal.ui.wizards.dialogfields.IDialogFieldListener;
import org.eclipse.dltk.internal.ui.wizards.dialogfields.StringDialogField;
import org.eclipse.dltk.launching.IInterpreterInstall;
import org.eclipse.dltk.ui.dialogs.StatusInfo;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.wst.xquery.internal.debug.ui.interpreters.AbstractAddInterpreterDialogBlock;

@SuppressWarnings("restriction")
public class MarkLogicAddInterpreterDialogBlock extends AbstractAddInterpreterDialogBlock {

    protected StringDialogField fInterpreterNameField;
    protected StringDialogField fInterpreterLocationField;

    protected StringDialogField fInterpreterUserField;
    protected StringDialogField fInterpreterPasswordField;

    private IStatus[] fStati;

    private final static char PASS_CHAR = (char)9679;
    private final static String SEPARATOR = "|";

    public MarkLogicAddInterpreterDialogBlock() {
        fStati = new IStatus[5];
        for (int i = 0; i < fStati.length; i++) {
            fStati[i] = new StatusInfo();
        }
    }

    protected void addControlsTo(Composite comp) {
        int numColumns = 3;

        fInterpreterNameField = new StringDialogField();
        fInterpreterNameField.setLabelText(InterpretersMessages.addInterpreterDialog_InterpreterEnvironmentName);
        fInterpreterNameField.doFillIntoGrid(comp, numColumns);

        fInterpreterLocationField = new StringDialogField();
        fInterpreterLocationField.setLabelText("XCC UR&L:");
        fInterpreterLocationField.doFillIntoGrid(comp, numColumns);
        ((GridData)fInterpreterLocationField.getTextControl(null).getLayoutData()).widthHint = convertWidthInCharsToPixels(70);

        fInterpreterUserField = new StringDialogField();
        fInterpreterUserField.setLabelText("MarkLogic &User:");
        fInterpreterUserField.doFillIntoGrid(comp, numColumns);

        fInterpreterPasswordField = new StringDialogField();
        fInterpreterPasswordField.setLabelText("Password:");
        fInterpreterPasswordField.doFillIntoGrid(comp, numColumns);
        fInterpreterPasswordField.getTextControl(null).setEchoChar(PASS_CHAR);
    }

    public String getInterpreterLocation() {
        return fInterpreterLocationField.getText();
    }

    public String getInterpreterName() {
        return fInterpreterNameField.getText();
    }

    public void initializeFields(IInterpreterInstall install) {
        if (install == null) {
            fInterpreterNameField.setText(Util.EMPTY_STRING);
            fInterpreterLocationField.setText(Util.EMPTY_STRING);
        } else {
            String[] parts = install.getInterpreterArgs().trim().split("\\" + SEPARATOR);
            fInterpreterNameField.setText(install.getName());
            // fInterpreterLocationField.setText(install.getInstallLocation().getCanonicalPath());
            fInterpreterLocationField.setText(parts[0]);
            fInterpreterUserField.setText(parts[1]);
            fInterpreterPasswordField.setText(parts[2]);
        }
        setInterpreterNameStatus(validateInterpreterName());
        setInterpreterLocationStatus(validateInterpreterLocation());
        updateStatus();
    }

    public void setFieldValuesToInterpreter(IInterpreterInstall install) {
        install.setName(getInterpreterName());

        // try {
        // install.setInstallLocation(new RemoteFileHandle(getEnvironemnt(), new
        // URI(getInterpreterLocation())));
        // } catch (URISyntaxException e) {
        // return;
        // }
        // install.setInterpreterArgs(fInterpreterUserField.getText() + SEPARATOR +
        // fInterpreterPasswordField.getText());

        IEnvironment selectedEnv = fAddInterpreterDialog.getEnvironment();
        install.setInstallLocation(new LazyFileHandle(selectedEnv.getId(), new Path("/")));
        install.setInterpreterArgs(fInterpreterLocationField.getText() + SEPARATOR + fInterpreterUserField.getText()
                + SEPARATOR + fInterpreterPasswordField.getText());

    }

    protected IStatus validateInterpreterLocation() {
        String locationName = getInterpreterLocation();
        IStatus s = null;
        if (locationName.length() == 0) {
            s = new StatusInfo(IStatus.INFO, InterpretersMessages.addInterpreterDialog_enterLocation);
        } else {
            try {
                URI uri = new URI(locationName);
                // if (!RemoteEnvironmentProvider.supportsScheme(uri.getScheme())) {
                // s = new StatusInfo(IStatus.ERROR,
                // "The XCC URL must have one of the file schemes: http, https");
                // } else
                if (uri.getHost() == null || uri.getHost().length() == 0) {
                    s = new StatusInfo(IStatus.ERROR, "The XCC URL host cannot be empty.");
                } else {
                    s = Status.OK_STATUS;
                }
            } catch (URISyntaxException use) {
                s = new StatusInfo(IStatus.ERROR, "Invalid XCC URL (" + use.getMessage() + ")");
            }
        }

        return s;
    }

    public String generateInterpreterName(String location) {
        return null;
    }

    @Override
    public void createFieldListeners() {
        fInterpreterNameField.setDialogFieldListener(new IDialogFieldListener() {

            public void dialogFieldChanged(DialogField field) {
                setInterpreterNameStatus(validateInterpreterName());
                updateStatus();
            }
        });

        fInterpreterLocationField.setDialogFieldListener(new IDialogFieldListener() {

            public void dialogFieldChanged(DialogField field) {
                setInterpreterLocationStatus(validateInterpreterLocation());
                updateStatus();
            }
        });
    }

    protected IStatus validateInterpreterName() {
        StatusInfo status = new StatusInfo();
        String name = fInterpreterNameField.getText();
        if (name == null || name.trim().length() == 0) {
            status.setInfo(InterpretersMessages.addInterpreterDialog_enterName);
        } else if (fRequestor.isDuplicateName(name)
                && (fEditedInterpreter == null || !name.equals(fEditedInterpreter.getName()))) {
            status.setError(InterpretersMessages.addInterpreterDialog_duplicateName);
        }
        return status;
    }

    private void setInterpreterNameStatus(IStatus status) {
        fStati[0] = status;
    }

    private void setInterpreterLocationStatus(IStatus status) {
        fStati[1] = status;
    }

    public void updateStatus() {
        IStatus max = null;
        for (int i = 0; i < fStati.length; i++) {
            IStatus curr = fStati[i];
            if (curr.matches(IStatus.ERROR)) {
                getStatusListener().statusChanged(curr);
                return;
            }
            if (max == null || curr.getSeverity() > max.getSeverity()) {
                max = curr;
            }
        }
        getStatusListener().statusChanged(max);
    }

}
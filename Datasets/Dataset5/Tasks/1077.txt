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
import org.eclipse.core.runtime.Path;
import org.eclipse.debug.ui.StringVariableSelectionDialog;
import org.eclipse.dltk.compiler.util.Util;
import org.eclipse.dltk.core.environment.IEnvironment;
import org.eclipse.dltk.core.environment.IFileHandle;
import org.eclipse.dltk.internal.debug.ui.interpreters.InterpretersMessages;
import org.eclipse.dltk.internal.launching.LazyFileHandle;
import org.eclipse.dltk.internal.ui.wizards.dialogfields.DialogField;
import org.eclipse.dltk.internal.ui.wizards.dialogfields.IDialogFieldListener;
import org.eclipse.dltk.internal.ui.wizards.dialogfields.IStringButtonAdapter;
import org.eclipse.dltk.internal.ui.wizards.dialogfields.StringButtonDialogField;
import org.eclipse.dltk.internal.ui.wizards.dialogfields.StringDialogField;
import org.eclipse.dltk.launching.IInterpreterInstall;
import org.eclipse.dltk.launching.IInterpreterInstallType;
import org.eclipse.dltk.ui.dialogs.StatusInfo;
import org.eclipse.dltk.ui.environment.IEnvironmentUI;
import org.eclipse.dltk.utils.PlatformFileUtils;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.BusyIndicator;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Label;

@SuppressWarnings("restriction")
public class AddLocalInterpreterDialogBlock extends AbstractAddInterpreterDialogBlock implements
        IInterpreterNameProvider {

    protected StringDialogField fInterpreterNameField;
    protected StringButtonDialogField fInterpreterLocationField;
    protected StringDialogField fInterpreterArgsField;

    protected AbstractInterpreterEnvironmentVariablesBlock fEnvironmentVariablesBlock;

    private IStatus[] fStati;

    public AddLocalInterpreterDialogBlock() {
        fStati = new IStatus[5];
        for (int i = 0; i < fStati.length; i++) {
            fStati[i] = new StatusInfo();
        }
    }

    protected void addControlsTo(Composite parent) {
        int numColumns = 3;

        fInterpreterNameField = new StringDialogField();
        fInterpreterNameField.setLabelText(InterpretersMessages.addInterpreterDialog_InterpreterEnvironmentName);
        fInterpreterNameField.doFillIntoGrid(parent, numColumns);

        fInterpreterLocationField = new StringButtonDialogField(new IStringButtonAdapter() {
            public void changeControlPressed(DialogField field) {
                browseForInstallation();
            }
        });
        fInterpreterLocationField.setLabelText(InterpretersMessages.addInterpreterDialog_InterpreterExecutableName);
        fInterpreterLocationField.setButtonLabel(InterpretersMessages.addInterpreterDialog_browse1);
        fInterpreterLocationField.doFillIntoGrid(parent, numColumns);
        ((GridData)fInterpreterLocationField.getTextControl(null).getLayoutData()).widthHint = convertWidthInCharsToPixels(50);

        fInterpreterArgsField = new StringDialogField();
        fInterpreterArgsField.setLabelText(InterpretersMessages.AddInterpreterDialog_iArgs);
        fInterpreterArgsField.doFillIntoGrid(parent, numColumns - 1);
        Button button = new Button(parent, SWT.PUSH);
        button.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
        button.setText("Variables...");
        button.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent e) {
                StringVariableSelectionDialog dialog = new StringVariableSelectionDialog(getShell());
                dialog.open();
                String variable = dialog.getVariableExpression();
                if (variable != null) {
                    fInterpreterArgsField.getTextControl(null).insert(variable);
                }
            }
        });

        fEnvironmentVariablesBlock = createEnvironmentVariablesBlock();
        if (fEnvironmentVariablesBlock != null) {
            Label l = new Label(parent, SWT.NONE);
            l.setText(InterpretersMessages.AddScriptInterpreterDialog_interpreterEnvironmentVariables);
            GridData gd = new GridData(GridData.FILL_HORIZONTAL);
            gd.horizontalSpan = numColumns;
            l.setLayoutData(gd);

            Control block = fEnvironmentVariablesBlock.createControl(parent);
            gd = new GridData(GridData.FILL_BOTH);
            gd.horizontalSpan = numColumns;
            block.setLayoutData(gd);
        }
    }

    protected AbstractInterpreterEnvironmentVariablesBlock createEnvironmentVariablesBlock() {
        return null;
    }

    public void setFieldValuesToInterpreter(IInterpreterInstall install) {
        IEnvironment selectedEnv = fAddInterpreterDialog.getEnvironment();
        install.setInstallLocation(new LazyFileHandle(selectedEnv.getId(), new Path(getInterpreterLocation())));
        install.setName(getInterpreterName());
        install.setInterpreterArgs(getInterpreterArguments());
        if (fEnvironmentVariablesBlock != null) {
            fEnvironmentVariablesBlock.performApply(install);
        }
    }

    protected IStatus validateInterpreterLocation() {
        IEnvironment selectedEnv = fAddInterpreterDialog.getEnvironment();
        String locationName = getInterpreterLocation();
        IStatus s = null;
        final IFileHandle file;
        if (locationName.length() == 0) {
            file = null;
            s = new StatusInfo(IStatus.INFO, InterpretersMessages.addInterpreterDialog_enterLocation);
        } else {
            file = PlatformFileUtils.findAbsoluteOrEclipseRelativeFile(selectedEnv, new Path(locationName));
            if (!file.exists()) {
                s = new StatusInfo(IStatus.ERROR, InterpretersMessages.addInterpreterDialog_locationNotExists);
            } else {
                final IStatus[] temp = new IStatus[1];
                BusyIndicator.showWhile(getShell().getDisplay(), new Runnable() {

                    public void run() {
                        temp[0] = fAddInterpreterDialog.getInterpreterType().validateInstallLocation(file);
                    }
                });
                s = temp[0];
            }
        }
        if (s.isOK()) {
            String name = getInterpreterName();
            if ((name == null || name.length() == 0) && file != null) {
                // auto-generate interpreter name
                String pName = generateInterpreterName(file.toOSString());
                if (pName != null) {
                    fInterpreterNameField.setText(pName);
                }
            }
        }
        return s;
    }

    protected String getInterpreterLocation() {
        return fInterpreterLocationField.getText().trim();
    }

    protected String getInterpreterName() {
        return fInterpreterNameField.getText().trim();
    }

    protected String getInterpreterArguments() {
        return fInterpreterArgsField.getText().trim();
    }

    protected void browseForInstallation() {
        IEnvironment environment = getEnvironemnt();
        IEnvironmentUI environmentUI = (IEnvironmentUI)environment.getAdapter(IEnvironmentUI.class);
        if (environmentUI != null) {
            String newPath = environmentUI.selectFile(getShell(), IEnvironmentUI.EXECUTABLE);
            if (newPath != null) {
                fInterpreterLocationField.setText(newPath);
            }
        }
    }

    public void initializeFields(IInterpreterInstall install) {
        if (install == null) {
            fInterpreterNameField.setText(Util.EMPTY_STRING);
            fInterpreterLocationField.setText(Util.EMPTY_STRING);
            fInterpreterArgsField.setText(Util.EMPTY_STRING);
        } else {
            fInterpreterNameField.setText(install.getName());
            fInterpreterLocationField.setText(install.getRawInstallLocation().toOSString());
            String interpreterArgs = install.getInterpreterArgs();
            if (interpreterArgs != null) {
                fInterpreterArgsField.setText(interpreterArgs);
            }
            if (fEnvironmentVariablesBlock != null) {
                fEnvironmentVariablesBlock.initializeFrom(install, install.getInterpreterInstallType());
            }
        }
        setInterpreterNameStatus(validateInterpreterName());
        setInterpreterLocationStatus(validateInterpreterLocation());
        updateStatus();
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

    private void setInterpreterNameStatus(IStatus status) {
        fStati[0] = status;
    }

    private void setInterpreterLocationStatus(IStatus status) {
        fStati[1] = status;
    }

    protected IStatus validateInterpreterName() {
        StatusInfo status = new StatusInfo();
        String name = getInterpreterName();
        if (name == null || name.length() == 0) {
            status.setInfo(InterpretersMessages.addInterpreterDialog_enterName);
        } else if (fRequestor.isDuplicateName(name)
                && (fEditedInterpreter == null || !name.equals(fEditedInterpreter.getName()))) {
            status.setError(InterpretersMessages.addInterpreterDialog_duplicateName);
        }
        return status;
    }

    @Override
    public void setFocus() {
        fInterpreterNameField.setFocus();
    }

    public String generateInterpreterName(String location) {
        return null;
    }

    protected boolean validateGeneratedName(String name) {
        IInterpreterInstallType[] types = fAddInterpreterDialog.getInterpreterTypes();
        for (int i = 0; i < types.length; i++) {
            IInterpreterInstallType type = types[i];
            IInterpreterInstall inst = type.findInterpreterInstallByName(name);
            if (inst != null) {
                // it is allowed to find interpreter being edited.
                return inst == fEditedInterpreter;
            }
        }
        return true;
    }

}
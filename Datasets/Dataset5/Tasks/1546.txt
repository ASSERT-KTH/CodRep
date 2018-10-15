import org.eclipse.wst.xquery.set.core.SETProjectConfig;

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

import java.net.URI;
import java.net.URISyntaxException;

import org.eclipse.core.resources.IContainer;
import org.eclipse.core.resources.IFile;
import org.eclipse.core.resources.IProject;
import org.eclipse.core.resources.IResource;
import org.eclipse.core.runtime.IPath;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Path;
import org.eclipse.core.runtime.Status;
import org.eclipse.dltk.core.DLTKCore;
import org.eclipse.dltk.core.IMethod;
import org.eclipse.dltk.core.ModelException;
import org.eclipse.dltk.ui.DLTKUILanguageManager;
import org.eclipse.jface.dialogs.IDialogConstants;
import org.eclipse.jface.dialogs.TitleAreaDialog;
import org.eclipse.jface.viewers.ILabelProvider;
import org.eclipse.jface.window.Window;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.ModifyEvent;
import org.eclipse.swt.events.ModifyListener;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.dialogs.ElementListSelectionDialog;
import org.eclipse.ui.dialogs.ElementTreeSelectionDialog;
import org.eclipse.ui.dialogs.ISelectionStatusValidator;
import org.eclipse.ui.model.WorkbenchContentProvider;
import org.eclipse.ui.model.WorkbenchLabelProvider;
import org.eclipse.wst.xquery.set.core.SETNature;
import org.eclipse.wst.xquery.set.internal.core.SETProjectConfig;
import org.eclipse.wst.xquery.set.internal.core.preferences.ISETPreferenceConstants;
import org.eclipse.wst.xquery.set.ui.SETUIPlugin;

public class SETEditProjectConfigDialog extends TitleAreaDialog {

    class WidgetListener implements ModifyListener {

        public void modifyText(ModifyEvent e) {
            if (e.widget == fUriText) {
                try {
                    new URI(fUriText.getText());

                    setErrorMessage(null);
                    if (fOKButton != null) {
                        fOKButton.setEnabled(true);
                    }

                } catch (URISyntaxException use) {
                    setErrorMessage("Invalid URI. " + use.getMessage());
                    if (fOKButton != null) {
                        fOKButton.setEnabled(false);
                    }
                }
            } else if (e.widget == fStartPageText) {
                // DLTK
                // XQueryModule module =
                // (XQueryModule)SourceParserUtil.getModuleDeclaration(fSourceModule);
                // MethodDeclaration[] decls = module.getFunctions();
                //
                //				
                // MethodDeclaration collectFunctionDeclarations();
                // ISourceModule sm = null;
                // sm.
            }
        }
    }

    private SETProjectConfig fConfig;
    private IProject fProject;

    private Text fUriText;
    private Text fVersionText;
    private Text fStartPageText;

    private Button fOKButton;

    private WidgetListener fListener = new WidgetListener();

    public SETEditProjectConfigDialog(Shell shell, IProject project, SETProjectConfig config) {
        super(shell);
        fConfig = config;
        fProject = project;
    }

    @Override
    protected Control createDialogArea(Composite parent) {
        Composite composite = new Composite(parent, SWT.NONE);
        composite.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
        composite.setLayout(new GridLayout(3, false));

        setTitle("Project Configuration");
        setMessage("Edit the project configuration");

        Label label = new Label(composite, SWT.NONE);
        label.setText("Logical URI:");

        fUriText = new Text(composite, SWT.SINGLE | SWT.BORDER);
        GridData gd = new GridData(SWT.FILL, SWT.CENTER, true, false);
        gd.horizontalSpan = 2;
        fUriText.setLayoutData(gd);
        fUriText.addModifyListener(fListener);

        label = new Label(composite, SWT.NONE);
        label.setText("Version:");

        fVersionText = new Text(composite, SWT.SINGLE | SWT.BORDER);
        gd = new GridData(SWT.FILL, SWT.CENTER, true, false);
        gd.horizontalSpan = 2;
        fVersionText.setLayoutData(gd);
        fVersionText.addModifyListener(fListener);

        label = new Label(composite, SWT.NONE);
        label.setText("Start Page:");

        fStartPageText = new Text(composite, SWT.SINGLE | SWT.BORDER);
        gd = new GridData(SWT.FILL, SWT.CENTER, true, false);
        gd.horizontalSpan = 2;
        fStartPageText.setLayoutData(gd);
        fStartPageText.addModifyListener(fListener);

        Composite buttonComp = new Composite(composite, SWT.NONE);
        gd = new GridData();
        gd.horizontalAlignment = GridData.END;
        gd.horizontalSpan = 2;
        buttonComp.setLayoutData(gd);
        GridLayout layout = new GridLayout(2, false);
        layout.marginWidth = 0;
        layout.marginHeight = 0;
        buttonComp.setLayout(layout);

        Button button = org.eclipse.dltk.ui.util.SWTFactory.createPushButton(buttonComp, "Handler function...", null);
        button.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent e) {
                String startPage = getHandlerFunctionStartPage(fProject, getShell());
                fStartPageText.setText(startPage);
            }
        });

        button = org.eclipse.dltk.ui.util.SWTFactory.createPushButton(buttonComp, "Public resource...", null);
        button.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent e) {
                String startPage = getPublicResourceStartPage(fProject, getShell());
                fStartPageText.setText(startPage);
            }
        });

        initializeData();

        return composite;
    }

    public static String getHandlerFunctionStartPage(IProject project, Shell shell) {
        HandlerCollector collector = new HandlerCollector();
        try {
            DLTKCore.create(project).accept(collector);

            ElementListSelectionDialog dialog = new ElementListSelectionDialog(shell, new WorkbenchLabelProvider());
            dialog.setElements(collector.getHandlers());
            dialog.setTitle("Start Page");
            dialog.setMessage("Select the project start page handler");

            if (dialog.open() == IDialogConstants.OK_ID) {
                IMethod handler = (IMethod)dialog.getFirstResult();
                String functionName = handler.getElementName();
                functionName = functionName.substring(functionName.indexOf(':') + 1);

                IResource resource = handler.getResource();
                String handlerModuleName = new Path(resource.getName()).removeFileExtension().toString();

                return "/" + handlerModuleName + "/" + functionName;
            }

        } catch (ModelException e1) {
            e1.printStackTrace();
        }

        return "";
    }

    public static String getPublicResourceStartPage(IProject project, Shell shell) {
        final ILabelProvider labelProvider = DLTKUILanguageManager.createLabelProvider(SETNature.NATURE_ID);
        ElementTreeSelectionDialog dialog = new ElementTreeSelectionDialog(shell, labelProvider,
                new WorkbenchContentProvider());

        dialog.setValidator(new ISelectionStatusValidator() {
            public IStatus validate(Object[] selection) {
                if (selection.length != 1) {
                    return new Status(IStatus.ERROR, SETUIPlugin.PLUGIN_ID, "You must select one file");
                } else {
                    if (!(selection[0] instanceof IFile)) {
                        return new Status(IStatus.ERROR, SETUIPlugin.PLUGIN_ID, "");
                    }
                }
                return new Status(IStatus.OK, SETUIPlugin.PLUGIN_ID, "");
            }
        });
        dialog.setTitle("Select Resource");
        dialog.setMessage("Select the resource to be set as the start page:");
        dialog.setDoubleClickSelects(true);
        IContainer publicDir = project.getFolder(ISETPreferenceConstants.DIR_NAME_PUBLIC);
        dialog.setInput(publicDir);

        if (dialog.open() == Window.OK) {
            IPath path = ((IFile)dialog.getFirstResult()).getFullPath().removeFirstSegments(2);
            return "/" + path.toPortableString();
        }
        return "";
    }

    @Override
    protected Button createButton(Composite parent, int id, String label, boolean defaultButton) {
        if (id == IDialogConstants.OK_ID) {
            fOKButton = super.createButton(parent, id, label, defaultButton);
            ;
        }
        return fOKButton;
    }

    private void initializeData() {
        if (fConfig != null) {
            fUriText.setText(fConfig.getLogicalUri().toString());
            fVersionText.setText(fConfig.getVersion());

            String startPage = fConfig.getStartPage();
            if (startPage != null) {
                fStartPageText.setText(fConfig.getStartPage());
            }
        }
    }

    @Override
    protected void okPressed() {
        try {
            String startPage = fStartPageText.getText().trim();
            startPage = (fStartPageText.getText().trim().length() == 0 ? null : startPage);

            String version = fVersionText.getText().trim();
            version = (version.length() == 0 ? "1.0" : version);

            fConfig = new SETProjectConfig(new URI(fUriText.getText()), startPage, version);
        } catch (URISyntaxException e) {
        }

        super.okPressed();
    }

    public SETProjectConfig getProjectConfig() {
        return fConfig;
    }

}
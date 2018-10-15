"An error occurred while setting the project buildpath: " + me.getMessage()));

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
package org.eclipse.wst.xquery.set.internal.ui.wizards;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.lang.reflect.InvocationTargetException;
import java.net.URI;

import org.eclipse.core.internal.content.ContentTypeManager;
import org.eclipse.core.resources.IContainer;
import org.eclipse.core.resources.IFile;
import org.eclipse.core.resources.IFolder;
import org.eclipse.core.resources.IProject;
import org.eclipse.core.resources.IResource;
import org.eclipse.core.resources.IWorkspaceRoot;
import org.eclipse.core.resources.ResourcesPlugin;
import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.IPath;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.NullProgressMonitor;
import org.eclipse.core.runtime.OperationCanceledException;
import org.eclipse.core.runtime.Path;
import org.eclipse.core.runtime.Status;
import org.eclipse.core.runtime.SubProgressMonitor;
import org.eclipse.core.runtime.content.IContentTypeSettings;
import org.eclipse.dltk.ast.declarations.ModuleDeclaration;
import org.eclipse.dltk.core.DLTKCore;
import org.eclipse.dltk.core.DLTKLanguageManager;
import org.eclipse.dltk.core.IBuildpathEntry;
import org.eclipse.dltk.core.IModelElement;
import org.eclipse.dltk.core.IScriptModel;
import org.eclipse.dltk.core.IScriptProject;
import org.eclipse.dltk.core.ModelException;
import org.eclipse.dltk.core.ScriptModelHelper;
import org.eclipse.dltk.internal.launching.DLTKLaunchingPlugin;
import org.eclipse.dltk.internal.ui.wizards.buildpath.FolderSelectionDialog;
import org.eclipse.dltk.internal.ui.wizards.dialogfields.ComboDialogField;
import org.eclipse.dltk.internal.ui.wizards.dialogfields.DialogField;
import org.eclipse.dltk.internal.ui.wizards.dialogfields.IDialogFieldListener;
import org.eclipse.dltk.internal.ui.wizards.dialogfields.IStringButtonAdapter;
import org.eclipse.dltk.internal.ui.wizards.dialogfields.SelectionButtonDialogField;
import org.eclipse.dltk.internal.ui.wizards.dialogfields.StringButtonDialogField;
import org.eclipse.dltk.internal.ui.wizards.dialogfields.StringDialogField;
import org.eclipse.dltk.ui.DLTKUILanguageManager;
import org.eclipse.jface.dialogs.ErrorDialog;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.jface.viewers.ILabelProvider;
import org.eclipse.jface.viewers.IStructuredSelection;
import org.eclipse.jface.viewers.Viewer;
import org.eclipse.jface.viewers.ViewerFilter;
import org.eclipse.jface.window.Window;
import org.eclipse.jface.wizard.WizardPage;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.MouseAdapter;
import org.eclipse.swt.events.MouseEvent;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.FileDialog;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.IWorkbenchWindow;
import org.eclipse.ui.PartInitException;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.actions.WorkspaceModifyOperation;
import org.eclipse.ui.dialogs.ElementListSelectionDialog;
import org.eclipse.ui.dialogs.ISelectionStatusValidator;
import org.eclipse.ui.ide.IDE;
import org.eclipse.ui.model.WorkbenchContentProvider;
import org.eclipse.ui.wizards.newresource.BasicNewResourceWizard;
import org.eclipse.wst.xquery.core.model.ast.XQueryLibraryModule;
import org.eclipse.wst.xquery.internal.core.XQDTContentType;
import org.eclipse.wst.xquery.internal.core.parser.XQDTSourceParser;
import org.eclipse.wst.xquery.set.core.ISETPreferenceConstants;
import org.eclipse.wst.xquery.set.core.SETNature;
import org.eclipse.wst.xquery.set.core.SETProjectConfig;
import org.eclipse.wst.xquery.set.core.SETProjectConfigUtil;
import org.eclipse.wst.xquery.set.ui.SETUIPlugin;

@SuppressWarnings("restriction")
public class SETImportModuleWizardPage extends WizardPage implements IDialogFieldListener {

    private static final String TEMP_DIR = ".config/temp/";

    protected StringButtonDialogField fModuleFileField;
    protected StringButtonDialogField fProjectField;
    protected StringDialogField fModuleNameField;
    protected ComboDialogField fModuleExtensionField;
    protected SelectionButtonDialogField fHandlerModuleSelectionField;
    protected SelectionButtonDialogField fLibraryModuleSelectionField;
    protected SelectionButtonDialogField fExternalModuleSelectionField;

    protected StringButtonDialogField fLibraryModulePathField;
    protected StringButtonDialogField fExternalModulePathField;

    protected Group fModuleTypeGroup;
    protected Composite fLibraryModuleComposite;
    protected Composite fExternalModuleComposite;

    private String[] fExtensions;
    private boolean fIsGroupEnabled;

    private IStructuredSelection fSelection;

    protected SETImportModuleWizardPage(String pageName, IStructuredSelection selection) {
        super(pageName);
        setTitle(pageName);
        setDescription("Import a XQuery module from the local file system into a Sausalito project");

        fExtensions = ContentTypeManager.getInstance().getContentType(XQDTContentType.XQUERY_CONTENT_TYPE)
                .getFileSpecs(IContentTypeSettings.FILE_EXTENSION_SPEC);
        for (int i = 0; i < fExtensions.length; i++) {
            fExtensions[i] = "." + fExtensions[i];
        }

        fSelection = selection;
    }

    public void createControl(Composite parent) {
        initializeDialogUnits(parent);

        int numCols = 4;

        Composite composite = new Composite(parent, SWT.NONE);
        composite.setLayoutData(new GridData(GridData.GRAB_HORIZONTAL | GridData.FILL_HORIZONTAL));
        composite.setLayout(new GridLayout(numCols, false));

        fModuleFileField = new StringButtonDialogField(new IStringButtonAdapter() {
            public void changeControlPressed(DialogField field) {
                handleModuleFileButtonSelected();
            }
        });
        fModuleFileField.setLabelText("Select module file:");
        fModuleFileField.setButtonLabel("Browse...");
        fModuleFileField.doFillIntoGrid(composite, numCols);
        GridData gd = new GridData(GridData.FILL_HORIZONTAL);
        gd.horizontalSpan = 2;
        fModuleFileField.getTextControl(null).setLayoutData(gd);

        fProjectField = new StringButtonDialogField(new IStringButtonAdapter() {
            public void changeControlPressed(DialogField field) {
                handleProjectButtonSelected();
            }
        });
        fProjectField.setLabelText("Select project:");
        fProjectField.setButtonLabel("Select...");
        fProjectField.doFillIntoGrid(composite, numCols);
        Text text = fProjectField.getTextControl(null);
        gd = new GridData(GridData.FILL_HORIZONTAL | SWT.READ_ONLY);
        gd.horizontalSpan = 2;
        text.setLayoutData(gd);
        text.setEditable(false);

        fModuleNameField = new StringDialogField();
        fModuleNameField.setLabelText("Module name:");
        fModuleNameField.doFillIntoGrid(composite, 2);
        fModuleNameField.getTextControl(null).setLayoutData(new GridData(GridData.FILL_HORIZONTAL));

        fModuleExtensionField = new ComboDialogField(SWT.READ_ONLY);
        fModuleExtensionField.setLabelText("File extension:");
        fModuleExtensionField.doFillIntoGrid(composite, 2);
        fModuleExtensionField.setItems(fExtensions);
        fModuleExtensionField.getComboControl(null).select(0);

        createVerticalSpacer(composite, numCols);

        fModuleTypeGroup = new Group(composite, SWT.NONE);
        fModuleTypeGroup.setLayout(new GridLayout(numCols, false));
        gd = new GridData(GridData.FILL_HORIZONTAL);
        gd.horizontalSpan = numCols;
        fModuleTypeGroup.setLayoutData(gd);
        fModuleTypeGroup.setText("Module type");

        createVerticalSpacer(fModuleTypeGroup, numCols);

        fHandlerModuleSelectionField = new SelectionButtonDialogField(SWT.RADIO);
        fHandlerModuleSelectionField.setLabelText("&Handler module");
        fHandlerModuleSelectionField.doFillIntoGrid(fModuleTypeGroup, numCols);
        fHandlerModuleSelectionField.setSelection(true);

        GridLayout layout = new GridLayout(numCols, false);
        layout.marginHeight = 0;
        layout.marginWidth = 0;
        gd = new GridData(GridData.FILL_HORIZONTAL);
        gd.horizontalSpan = numCols;
        gd.horizontalIndent = 15;

        createVerticalSpacer(fModuleTypeGroup, numCols);

        fLibraryModuleSelectionField = new SelectionButtonDialogField(SWT.RADIO);
        fLibraryModuleSelectionField.setLabelText("&Library module");
        fLibraryModuleSelectionField.doFillIntoGrid(fModuleTypeGroup, numCols);

        fLibraryModuleComposite = new Composite(fModuleTypeGroup, SWT.NONE);
        fLibraryModuleComposite.setLayout(layout);
        fLibraryModuleComposite.setLayoutData(gd);
        fLibraryModuleComposite.addMouseListener(new MouseAdapter() {
            @Override
            public void mouseDown(MouseEvent e) {
                fModuleExtensionField.setEnabled(true);
                fHandlerModuleSelectionField.setSelection(false);
                fLibraryModuleSelectionField.setSelection(true);
                fExternalModuleSelectionField.setSelection(false);
                fLibraryModulePathField.getTextControl(null).setFocus();
            }
        });

        fLibraryModulePathField = new StringButtonDialogField(new IStringButtonAdapter() {
            public void changeControlPressed(DialogField field) {
                handleLibraryModulePathButtonSelected();
            }
        });
        fLibraryModulePathField.setLabelText("Select module location:");
        fLibraryModulePathField.setButtonLabel("Select...");
        fLibraryModulePathField.doFillIntoGrid(fLibraryModuleComposite, numCols);
        fLibraryModulePathField.getTextControl(null).setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
        fLibraryModulePathField.setEnabled(false);
        fLibraryModulePathField.setText(ISETPreferenceConstants.DIR_NAME_LIBRARY);

        createVerticalSpacer(fModuleTypeGroup, numCols);

        fExternalModuleSelectionField = new SelectionButtonDialogField(SWT.RADIO);
        fExternalModuleSelectionField.setLabelText("&External module");
        fExternalModuleSelectionField.doFillIntoGrid(fModuleTypeGroup, numCols);

        fExternalModuleComposite = new Composite(fModuleTypeGroup, SWT.NONE);
        fExternalModuleComposite.setLayout(layout);
        fExternalModuleComposite.setLayoutData(gd);
        fExternalModuleComposite.addMouseListener(new MouseAdapter() {
            @Override
            public void mouseDown(MouseEvent e) {
                fModuleExtensionField.setEnabled(true);
                fHandlerModuleSelectionField.setSelection(false);
                fLibraryModuleSelectionField.setSelection(false);
                fExternalModuleSelectionField.setSelection(true);
                fExternalModulePathField.getTextControl(null).setFocus();
            }
        });

        fExternalModulePathField = new StringButtonDialogField(new IStringButtonAdapter() {
            public void changeControlPressed(DialogField field) {
                handleExternalModulePathButtonSelected();
            }
        });
        fExternalModulePathField.setLabelText("Select module location:");
        fExternalModulePathField.setButtonLabel("Select...");
        fExternalModulePathField.doFillIntoGrid(fExternalModuleComposite, numCols);
        fExternalModulePathField.getTextControl(null).setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
        fExternalModulePathField.setEnabled(false);
        fExternalModulePathField.setText(ISETPreferenceConstants.DIR_NAME_EXTERNAL);

        createVerticalSpacer(fModuleTypeGroup, numCols);

        processSelection();

        addFieldListeners();

        setPageComplete(isValid());
        setGroupEnabled(fIsGroupEnabled);

        setControl(composite);
    }

    private void processSelection() {
        if (fSelection != null && !fSelection.isEmpty()) {
            IProject project = null;
            IPath selectedPath = null;

            Object[] elements = fSelection.toArray();
            for (Object element : elements) {
                if (element instanceof IResource) {
                    IResource resource = (IResource)element;
                    if (!(resource instanceof IContainer)) {
                        resource = resource.getParent();
                    }
                    project = resource.getProject();
                    selectedPath = resource.getFullPath();
                } else if (element instanceof IModelElement) {
                    IModelElement modelElem = (IModelElement)element;
                    IResource resource = modelElem.getResource();
                    if (!(resource instanceof IContainer)) {
                        resource = resource.getParent();
                    }
                    project = resource.getProject();
                    selectedPath = resource.getFullPath();
                }
                try {
                    if (project != null && project.isAccessible() && project.hasNature(SETNature.NATURE_ID)) {
                        break;
                    }
                } catch (CoreException ce) {
                    // do nothing ...
                }
                project = null;
                selectedPath = null;
            }

            if (project == null) {
                return;
            }
            // set the project name
            fProjectField.setText(project.getName());

            // set the module type selection
            IPath projectPath = project.getFullPath();
            fHandlerModuleSelectionField.setSelection(false);
            fLibraryModuleSelectionField.setSelection(false);
            fExternalModuleSelectionField.setSelection(false);
            if (projectPath.append(ISETPreferenceConstants.DIR_NAME_LIBRARY).isPrefixOf(selectedPath)) {
                fLibraryModuleSelectionField.setSelection(true);
                fLibraryModulePathField.setText(selectedPath.removeFirstSegments(1).toOSString());
            } else if (projectPath.append(ISETPreferenceConstants.DIR_NAME_EXTERNAL).isPrefixOf(selectedPath)) {
                fExternalModuleSelectionField.setSelection(true);
                fExternalModulePathField.setText(selectedPath.removeFirstSegments(1).toOSString());
            } else {
                fHandlerModuleSelectionField.setSelection(true);
                fModuleExtensionField.setEnabled(false);
            }
        }
    }

    protected void createVerticalSpacer(Composite parent, int numCols) {
        GridData gd = new GridData(SWT.NONE);
        gd.horizontalSpan = numCols;
        gd.heightHint = 0;
        Label l = new Label(parent, SWT.LEFT);
        l.setLayoutData(gd);
    }

    private void addFieldListeners() {
        fHandlerModuleSelectionField.setDialogFieldListener(this);
        fLibraryModuleSelectionField.setDialogFieldListener(this);
        fExternalModuleSelectionField.setDialogFieldListener(this);

        fModuleFileField.setDialogFieldListener(this);
        fProjectField.setDialogFieldListener(this);
        fModuleNameField.setDialogFieldListener(this);
        fModuleExtensionField.setDialogFieldListener(this);

        fLibraryModulePathField.setDialogFieldListener(this);
        fExternalModulePathField.setDialogFieldListener(this);
    }

    public void dialogFieldChanged(DialogField field) {
        if (field == fHandlerModuleSelectionField) {
            fModuleExtensionField.setEnabled(!fHandlerModuleSelectionField.isSelected());
        } else if (field == fLibraryModuleSelectionField) {
            boolean selection = fExternalModuleSelectionField.isSelected();
            fExternalModulePathField.setEnabled(selection);
            if (selection) {
                checkDirectory(ISETPreferenceConstants.DIR_NAME_EXTERNAL);
            }
        } else if (field == fExternalModuleSelectionField) {
            boolean selection = fExternalModuleSelectionField.isSelected();
            fExternalModulePathField.setEnabled(selection);
            if (selection) {
                checkDirectory(ISETPreferenceConstants.DIR_NAME_EXTERNAL);
            }
        }

        setPageComplete(isValid());
        setGroupEnabled(fIsGroupEnabled);
    }

    private void setGroupEnabled(boolean valid) {
        for (Control control : fModuleTypeGroup.getChildren()) {
            control.setEnabled(valid);
        }
        if (valid) {
            if (fLibraryModuleSelectionField.isSelected()) {
                fLibraryModulePathField.setEnabled(true);
            } else if (fExternalModuleSelectionField.isSelected()) {
                fExternalModulePathField.setEnabled(true);
            }
        }
    }

    private boolean isValid() {
        fIsGroupEnabled = false;

        String modulePath = fModuleFileField.getText().trim();
        if (modulePath.length() == 0) {
            setErrorMessage(null);
            return false;
        }
        File file = new File(modulePath);
        if (!file.exists() || !file.isFile()) {
            setErrorMessage("The provided module file is not accessible");
            return false;
        }

        IScriptProject project = getProject();
        if (project == null) {
            setErrorMessage("Select a target sausalito project");
            return false;
        }
        if (!project.getProject().isAccessible()) {
            setErrorMessage("The selected project is not accessible");
            return false;
        }

        String moduleName = fModuleNameField.getText().trim();
        if (moduleName.length() == 0) {
            setErrorMessage("Provide a name for the imported module");
            return false;
        }
        if (!moduleName.matches("(\\w|\\-)*")) {
            setErrorMessage("\"" + moduleName + "\" is not a valid module namea");
            return false;
        }

        fIsGroupEnabled = true;

        if (fLibraryModuleSelectionField.isSelected()) {
            String pathText = fLibraryModulePathField.getText().trim();
            if (pathText.length() == 0) {
                setErrorMessage("Select a location for the imported library module");
                return false;
            } else {
                IPath path = getLibraryModulePath();
                if (path == null || path.segmentCount() == 0) {
                    setErrorMessage("Select an existing destination in the \""
                            + ISETPreferenceConstants.DIR_NAME_LIBRARY + "\" project directory");
                    return false;
                }
                if (!path.segment(0).equals(ISETPreferenceConstants.DIR_NAME_LIBRARY)) {
                    setErrorMessage("Library modules must be located in the \""
                            + ISETPreferenceConstants.DIR_NAME_LIBRARY + "\" project directory");
                    return false;
                }
            }
        } else if (fExternalModuleSelectionField.isSelected()) {
            String pathText = fExternalModulePathField.getText().trim();
            if (pathText.length() == 0) {
                setErrorMessage("Select a location for the imported external module");
                return false;
            } else {
                IPath path = getExternalModulePath();
                if (path == null || path.segmentCount() == 0) {
                    setErrorMessage("Select an existing destination in the \""
                            + ISETPreferenceConstants.DIR_NAME_EXTERNAL + "\" project directory");
                    return false;
                }
                if (!path.segment(0).equals(ISETPreferenceConstants.DIR_NAME_EXTERNAL)) {
                    setErrorMessage("External modules must be located in the \""
                            + ISETPreferenceConstants.DIR_NAME_EXTERNAL + "\" project directory");
                    return false;
                }
            }
        }

        IPath path = getModuleDestinationFilePath();
        if (path != null) {
            if (project.getProject().exists(path)) {
                setErrorMessage("A module already exists at location: " + path.toOSString());
                return false;
            }
        }

        setErrorMessage(null);
        return true;
    }

    private IPath getLibraryModulePath() {
        String pathText = fLibraryModulePathField.getText().trim();

        if (pathText.length() == 0) {
            return null;
        }

        IScriptProject project = getProject();
        if (project == null) {
            return null;
        }

        IPath path = new Path(pathText);
        if (!project.getProject().exists(path)) {
            return null;
        }

        return path;
    }

    private IPath getExternalModulePath() {
        String pathText = fExternalModulePathField.getText().trim();

        if (pathText.length() == 0) {
            return null;
        }

        IScriptProject project = getProject();
        if (project == null) {
            return null;
        }

        IPath path = new Path(pathText);
        if (!project.getProject().exists(path)) {
            return null;
        }

        return path;
    }

    private IPath getModuleDestinationFilePath() {
        IPath path = null;
        if (fHandlerModuleSelectionField.isSelected()) {
            path = new Path(ISETPreferenceConstants.DIR_NAME_HANDLER);
        } else if (fLibraryModuleSelectionField.isSelected()) {
            path = getLibraryModulePath();
        } else if (fExternalModuleSelectionField.isSelected()) {
            path = getExternalModulePath();
        }
        if (path != null) {
            return path.append(getModuleFileName() + getModuleFileExtension());
        }
        return null;
    }

    private IPath getImportPath() {
        return new Path(fModuleFileField.getText().trim());
    }

    private String getModuleFileExtension() {
        return fModuleExtensionField.getText();
    }

    private String getModuleFileName() {
        return fModuleNameField.getText().trim();
    }

    private static class ImportModuleRecord {

        private static final int TYPE_HANDLER = 1;
        private static final int TYPE_LIBRARY = 2;
        private static final int TYPE_EXTERNAL = 3;

        protected int type;
        protected IProject project;
        protected IPath importPath;
        protected IPath destinationPath;

        public ImportModuleRecord(IProject project, IPath source, IPath destination) {
            this.project = project;
            importPath = source;
            destinationPath = destination;
            String dir = destination.segment(0);
            if (dir.equals(ISETPreferenceConstants.DIR_NAME_HANDLER)) {
                type = TYPE_HANDLER;
            } else if (dir.equals(ISETPreferenceConstants.DIR_NAME_LIBRARY)) {
                type = TYPE_LIBRARY;
            } else if (dir.equals(ISETPreferenceConstants.DIR_NAME_EXTERNAL)) {
                type = TYPE_EXTERNAL;
            }
        }
    }

    public boolean finishPage() {
        final ImportModuleRecord moduleRecord = new ImportModuleRecord(getProject().getProject(), getImportPath(),
                getModuleDestinationFilePath());

        WorkspaceModifyOperation op = new WorkspaceModifyOperation() {
            protected void execute(IProgressMonitor monitor) throws CoreException, InvocationTargetException,
                    InterruptedException {
                try {
                    monitor.beginTask("", 4000);
                    if (!importModule(moduleRecord, monitor)) {
                        rollbackImportModule(moduleRecord);
                    }
                } catch (OperationCanceledException oce) {
                    monitor.setTaskName("Canceling module import...");
                    rollbackImportModule(moduleRecord);
                } catch (CoreException ce) {
                    rollbackImportModule(moduleRecord);
                    throw ce;
                } finally {
                    monitor.done();
                }

            }
        };

        try {
            getContainer().run(true, true, op);
        } catch (InterruptedException ie) {
            return false;
        } catch (InvocationTargetException ite) {
            // one of the steps resulted in a core exception
            Throwable t = ite.getTargetException();
            reportError(t);
            return false;
        }

        try {
            openEditor(f);
        } catch (CoreException e) {
            reportError(e);
        }

        return true;
    }

    private boolean importModule(ImportModuleRecord moduleRecord, IProgressMonitor monitor)
            throws InvocationTargetException, InterruptedException, CoreException {

        // the monitor.beginTask() was already called by the invoking function 
        checkMonitor(monitor);

        addFolderToBuildpath(moduleRecord.destinationPath.segment(0), new SubProgressMonitor(monitor, 1000));

        IFile moduleFile = null;
        if (moduleRecord.type == ImportModuleRecord.TYPE_HANDLER
                || moduleRecord.type == ImportModuleRecord.TYPE_LIBRARY) {
            moduleFile = importHandlerOrLibraryModule(moduleRecord, monitor);
        } else if (moduleRecord.type == ImportModuleRecord.TYPE_EXTERNAL) {
            moduleFile = importExternalModule(moduleRecord, monitor);
        }

        if (moduleFile == null) {
            return false;
        }

        f = moduleFile;
        return true;
    }

    private IFile f;

    private IFile importHandlerOrLibraryModule(ImportModuleRecord moduleRecord, IProgressMonitor monitor)
            throws CoreException {

        // copy the module inside the project to a temporary path
        // such that we can parse it 
        monitor.setTaskName("Copying module...");

        IProject project = moduleRecord.project;
        IFile to = project.getFile(moduleRecord.destinationPath);
        File from = moduleRecord.importPath.toFile();
        IPath tempPath = new Path(TEMP_DIR).append(moduleRecord.destinationPath.lastSegment());
        createFoldersInPath(project, tempPath.removeLastSegments(1), new SubProgressMonitor(monitor, 500));
        copyFile(from, project.getFile(tempPath), new SubProgressMonitor(monitor, 500));

        checkMonitor(monitor);

        // parse the file in the temporary location
        monitor.setTaskName("Parsing module...");

        XQueryLibraryModule libMod = parseModule(moduleRecord, tempPath, monitor);

        int off = libMod.getNamespaceUri().matchStart();
        int len = libMod.getNamespaceUri().matchLength();

        SETProjectConfig config = SETProjectConfigUtil.readProjectConfig(moduleRecord.project);
        if (config == null) {
            throw new CoreException(new Status(IStatus.ERROR, SETUIPlugin.PLUGIN_ID,
                    "Could not read the project configuration file"));
        }

        URI projectUri = config.getLogicalUri();

        String toResolve = null;
        if (moduleRecord.type == ImportModuleRecord.TYPE_HANDLER) {
            toResolve = moduleRecord.destinationPath.removeFirstSegments(1).removeFileExtension().toPortableString();
        } else {
            toResolve = moduleRecord.destinationPath.removeFileExtension().toPortableString();
        }
        URI resolvedUri = projectUri.resolve(toResolve);
        String ns = resolvedUri.toString();

        try {
            copyConfigureFile(project.getFile(tempPath), to, off, len, ns, new SubProgressMonitor(monitor, 500));
        } catch (IOException ioe) {
            throw new CoreException(new Status(IStatus.ERROR, SETUIPlugin.PLUGIN_ID, ioe.getMessage()));
        }

        checkMonitor(monitor);

        deleteTempDir(project, new SubProgressMonitor(monitor, 500));

        return to;
    }

    private void deleteTempDir(IProject project, IProgressMonitor monitor) throws CoreException {
        monitor = (monitor == null ? new NullProgressMonitor() : monitor);

        IFolder folder = project.getFolder(TEMP_DIR);
        if (folder.exists()) {
            folder.delete(true, new SubProgressMonitor(monitor, 10));
        }
    }

    private void createFoldersInPath(IProject project, IPath path, IProgressMonitor monitor) throws CoreException {
        IPath current = new Path("");
        for (String segment : path.segments()) {
            current = current.append(segment);
            IFolder folder = project.getFolder(current);
            if (!folder.exists()) {
                folder.create(true, true, new SubProgressMonitor(monitor, 10));
            }
        }
    }

    private IFile importExternalModule(ImportModuleRecord moduleRecord, IProgressMonitor monitor) throws CoreException {
        monitor.setTaskName("Importing external module...");

        IProject project = moduleRecord.project;
        IFile to = project.getFile(moduleRecord.destinationPath);
        File from = moduleRecord.importPath.toFile();

        copyFile(from, to, new SubProgressMonitor(monitor, 3000));

        return to;
    }

    private void copyFile(File fromFile, IFile toFile, IProgressMonitor monitor) throws CoreException {
        try {
            FileInputStream fis = new FileInputStream(fromFile);
            toFile.create(fis, true, monitor);
        } catch (FileNotFoundException fnfe) {
            throw new CoreException(new Status(IStatus.ERROR, SETUIPlugin.PLUGIN_ID, fnfe.getMessage()));
        }
    }

    private void copyConfigureFile(IFile fromFile, IFile toFile, int offset, int length, String namespace,
            IProgressMonitor monitor) throws CoreException, IOException {
        InputStreamReader sr = null;
        OutputStreamWriter sw = null;
        try {
            sr = new InputStreamReader(fromFile.getContents());
            File out = toFile.getRawLocation().toFile();
            //boolean done = out.createNewFile();
            sw = new OutputStreamWriter(new FileOutputStream(out));

            char[] pre = new char[offset + 1];
            sr.read(pre);
            sw.write(pre);
            sr.skip(length - 1);
            sw.write(namespace);
            int c;
            while ((c = sr.read()) != -1) {
                sw.write(c);
            }
        } catch (Throwable t) {
        } finally {
            if (sr != null) {
                sr.close();
            }
            if (sw != null) {
                sw.close();
            }
//            toFile.getParent().refreshLocal(IResource.DEPTH_INFINITE, monitor);
        }
    }

    private void rollbackImportModule(ImportModuleRecord moduleRecord) throws CoreException {
        IProject project = moduleRecord.project;
        IPath modulePath = moduleRecord.destinationPath;
        if (project.exists(modulePath)) {
            project.getFile(modulePath).delete(true, null);
        }
        deleteTempDir(project, null);
    }

    private void checkMonitor(IProgressMonitor monitor) {
        if (monitor.isCanceled()) {
            throw new OperationCanceledException();
        }
    }

    private void reportError(Throwable t) {
        String message = "Import problems";
        IStatus status;
        if (t instanceof CoreException) {
            status = ((CoreException)t).getStatus();
        } else {
            status = new Status(IStatus.ERROR, SETUIPlugin.PLUGIN_ID, 1, message, t);
        }
        ErrorDialog.openError(getShell(), message, null, status);
    }

    protected void handleProjectButtonSelected() {
        IScriptProject project = chooseProject();
        if (project != null) {
            fProjectField.setText(project.getElementName());
        }
    }

    protected void handleModuleFileButtonSelected() {
        File file = browseForModuleFile();
        if (file != null) {
            fModuleFileField.setText(file.getPath());
            IPath path = new Path(file.getPath());

            String moduleName = path.lastSegment();
            String ext = path.getFileExtension();
            if (ext != null && ext.length() > 0) {
                moduleName = moduleName.substring(0, moduleName.lastIndexOf(ext) - 1);
            }
            fModuleNameField.setText(moduleName);
        }

        ;
    }

    protected void handleLibraryModulePathButtonSelected() {
        if (!checkDirectory(ISETPreferenceConstants.DIR_NAME_LIBRARY)) {
            return;
        }
        IPath dir = chooseLibraryModulePath();
        if (dir != null) {
            fLibraryModulePathField.setText(dir.removeFirstSegments(1).toOSString());
        }
    }

    private boolean checkDirectory(String name) {
        IScriptProject project = getProject();
        if (project == null) {
            setErrorMessage("Select a valid Sausalito project");
            return false;
        }

        // create the source directory if necessary
        IResource res = project.getProject().findMember(name);
        if (res == null) {
            boolean create = MessageDialog.openConfirm(getShell(), "Create directory", "The \"" + name
                    + "\" project directory is missing for the selected project.\nDo you want to create it now?");
            if (create) {
                IFolder folder = project.getProject().getFolder(name);
                try {
                    folder.create(true, true, null);
                } catch (CoreException ce) {
                    setErrorMessage("An error ocured while creating the \"" + name + "\" directory: " + ce.getMessage());
                    return false;
                }
            } else {
                return false;
            }
        } else if (!(res instanceof IFolder)) {
            setErrorMessage("The \"" + name + "\" directory cannot be created");
            return false;
        }

        isValid();
        return true;
    }

    protected void handleExternalModulePathButtonSelected() {
        if (!checkDirectory(ISETPreferenceConstants.DIR_NAME_EXTERNAL)) {
            return;
        }

        IPath dir = chooseExternalModulePath();
        if (dir != null) {
            fExternalModulePathField.setText(dir.removeFirstSegments(1).toOSString());
        }
    }

    private IScriptProject chooseProject() {
        final ILabelProvider labelProvider = DLTKUILanguageManager.createLabelProvider(SETNature.NATURE_ID);
        final ElementListSelectionDialog dialog = new ElementListSelectionDialog(getShell(), labelProvider);
        dialog.setTitle("Project selection");
        dialog.setMessage("Select the import destination project");

        try {
            final IScriptProject[] projects = ScriptModelHelper.getOpenedScriptProjects(DLTKCore
                    .create(getWorkspaceRoot()), SETNature.NATURE_ID);
            dialog.setElements(projects);
        } catch (ModelException e) {
            DLTKLaunchingPlugin.log(e);
        }

        final IScriptProject project = getProject();
        if (project != null) {
            dialog.setInitialSelections(new Object[] { project });
        }

        if (dialog.open() == Window.OK) {
            return (IScriptProject)dialog.getFirstResult();
        }

        return null;
    }

    private IPath chooseLibraryModulePath() {
        final ILabelProvider labelProvider = DLTKUILanguageManager.createLabelProvider(SETNature.NATURE_ID);
        FolderSelectionDialog dialog = new FolderSelectionDialog(getShell(), labelProvider,
                new WorkbenchContentProvider());

        IContainer libDir = getProject().getProject().getFolder(ISETPreferenceConstants.DIR_NAME_LIBRARY);
        IContainer container = libDir;
        IPath path = getLibraryModulePath();
        if (path != null) {
            container = getProject().getProject().getFolder(path);
        }

        dialog.addFilter(new ViewerFilter() {
            private IPath prefix = getProject().getPath().append(ISETPreferenceConstants.DIR_NAME_LIBRARY);

            public boolean select(Viewer viewer, Object parentElement, Object element) {
                if (element instanceof IFolder) {
                    IFolder folder = (IFolder)element;
                    return prefix.isPrefixOf(folder.getFullPath());
                }
                return false;
            }
        });
        dialog.setValidator(new ISelectionStatusValidator() {
            public IStatus validate(Object[] selection) {
                if (selection.length == 0) {
                    return new Status(IStatus.ERROR, SETUIPlugin.PLUGIN_ID, "You must select one destination directory");
                }
                return new Status(IStatus.OK, SETUIPlugin.PLUGIN_ID, "");
            }
        });
        dialog.setTitle("Library Module Directory");
        dialog.setMessage("Select the target directory for the library module:");
        dialog.setDoubleClickSelects(true);
        dialog.setInput(getProject().getProject());
        if (container.exists()) {
            dialog.setInitialSelection(container);
        } else {
            dialog.setInitialSelection(libDir);
        }

        if (dialog.open() == Window.OK) {
            return ((IFolder)dialog.getFirstResult()).getFullPath();
        }

        return null;
    }

    private IPath chooseExternalModulePath() {
        final ILabelProvider labelProvider = DLTKUILanguageManager.createLabelProvider(SETNature.NATURE_ID);
        FolderSelectionDialog dialog = new FolderSelectionDialog(getShell(), labelProvider,
                new WorkbenchContentProvider());

        IContainer extDir = getProject().getProject().getFolder(ISETPreferenceConstants.DIR_NAME_EXTERNAL);
        IContainer container = extDir;
        IPath path = getExternalModulePath();
        if (path != null) {
            container = getProject().getProject().getFolder(path);
        }

        dialog.addFilter(new ViewerFilter() {
            private IPath prefix = getProject().getPath().append(ISETPreferenceConstants.DIR_NAME_EXTERNAL);

            public boolean select(Viewer viewer, Object parentElement, Object element) {
                if (element instanceof IFolder) {
                    IFolder folder = (IFolder)element;
                    return prefix.isPrefixOf(folder.getFullPath());
                }
                return false;
            }
        });
        dialog.setValidator(new ISelectionStatusValidator() {
            public IStatus validate(Object[] selection) {
                if (selection.length == 0) {
                    return new Status(IStatus.ERROR, SETUIPlugin.PLUGIN_ID, "You must select one destination directory");
                }
                return new Status(IStatus.OK, SETUIPlugin.PLUGIN_ID, "");
            }
        });
        dialog.setTitle("External Module Directory");
        dialog.setMessage("Select the target directory for the external module:");
        dialog.setDoubleClickSelects(true);
        dialog.setInput(getProject().getProject());
        if (container.exists()) {
            dialog.setInitialSelection(container);
        } else {
            dialog.setInitialSelection(extDir);
        }

        if (dialog.open() == Window.OK) {
            return ((IFolder)dialog.getFirstResult()).getFullPath();
        }

        return null;
    }

    protected IScriptProject getProject() {
        String projectName = fProjectField.getText().trim();
        if (projectName.length() < 1) {
            return null;
        }

        return getScriptModel().getScriptProject(projectName);
    }

    protected File browseForModuleFile() {
        FileDialog fileDialog = new FileDialog(getShell());
        String filePath = fileDialog.open();
        if (filePath != null) {
            filePath = filePath.trim();
            if (filePath.length() > 0) {
                return new File(filePath);
            }
        }

        return null;
    }

    private IWorkspaceRoot getWorkspaceRoot() {
        return ResourcesPlugin.getWorkspace().getRoot();
    }

    protected IScriptModel getScriptModel() {
        return DLTKCore.create(getWorkspaceRoot());
    }

    private void openEditor(final IFile toFile) throws CoreException {
        IWorkbenchWindow[] windows = PlatformUI.getWorkbench().getWorkbenchWindows();
        if (windows.length == 1) {
            toFile.refreshLocal(0, null);
            BasicNewResourceWizard.selectAndReveal(toFile, windows[0]);

            final IWorkbenchPage page = windows[0].getActivePage();
            windows[0].getShell().getDisplay().asyncExec(new Runnable() {
                public void run() {
                    try {
                        IDE.openEditor(page, toFile);
                    } catch (PartInitException e) {
                        e.printStackTrace();
                    }
                }
            });
        }
    }

    private void addFolderToBuildpath(String name, IProgressMonitor monitor) throws CoreException {
        IScriptProject project = getProject();

        monitor.beginTask("Configuring project buildpath", 1000);

        checkMonitor(monitor);

        // check if the directory is in the source path
        try {
            monitor.setTaskName("Adding \"" + name + "\" directory to the project buildpath");

            IPath srcEntry = project.getPath().append(name);

            IBuildpathEntry[] originalPath = project.getRawBuildpath();
            for (IBuildpathEntry entry : originalPath) {
                if (entry.getPath().equals(srcEntry)) {
                    monitor.worked(1000);
                    return;
                }
            }
            IBuildpathEntry[] newPath = new IBuildpathEntry[originalPath.length + 1];
            System.arraycopy(originalPath, 0, newPath, 0, originalPath.length);
            IBuildpathEntry newEntry = DLTKCore.newSourceEntry(srcEntry);
            newPath[originalPath.length] = newEntry;
            project.setRawBuildpath(newPath, new SubProgressMonitor(monitor, 1000));

            checkMonitor(monitor);

        } catch (ModelException me) {
            throw new CoreException(new Status(IStatus.ERROR, SETUIPlugin.PLUGIN_ID,
                    "An error occured while setting the project buildpath: " + me.getMessage()));
        } finally {
            monitor.done();
        }
    }

    private XQueryLibraryModule parseModule(ImportModuleRecord moduleRecord, IPath tempPath, IProgressMonitor monitor)
            throws CoreException {

        XQDTSourceParser parser = (XQDTSourceParser)DLTKLanguageManager.getSourceParser(SETNature.NATURE_ID);
        char[] fileName = getProject().getPath().append(tempPath).toString().toCharArray();
        File module = moduleRecord.importPath.toFile();
        long length = module.length();
        if (length > Integer.MAX_VALUE) {
            throw new CoreException(new Status(IStatus.ERROR, SETUIPlugin.PLUGIN_ID,
                    "Cannot import XQuery files larger than 2MB"));
        }

        char[] source = new char[(int)length];

        InputStreamReader reader = null;
        try {
            reader = new InputStreamReader(new FileInputStream(module));
            reader.read(source);
            if (reader != null) {
                reader.close();
            }
        } catch (IOException e) {
            throw new CoreException(new Status(IStatus.ERROR, SETUIPlugin.PLUGIN_ID, e.getMessage()));
        }

        ModuleDeclaration modDecl = parser.parse(fileName, source, null);

        monitor.worked(1000);

        checkMonitor(monitor);

        // read the project configuration and retrieve the logical URI
        monitor.setTaskName("Configuring module...");

        if (modDecl == null || !(modDecl instanceof XQueryLibraryModule)) {
            throw new CoreException(new Status(IStatus.ERROR, SETUIPlugin.PLUGIN_ID,
                    "The imported file does not contain a valid XQuery Module"));
        }

        return (XQueryLibraryModule)modDecl;
    }
}
 No newline at end of file
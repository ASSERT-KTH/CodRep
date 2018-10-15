JAXWSUIMessages.ANNOTATIONS_VIEW_NO_SUITABLE_LIBRARY_FOUND, "JAX-WS")); //$NON-NLS-1$

/*******************************************************************************
 * Copyright (c) 2009 Shane Clarke.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Shane Clarke - initial API and implementation
 *******************************************************************************/
package org.eclipse.jst.ws.internal.jaxws.ui.widgets;

import java.util.HashMap;
import java.util.Map;

import org.eclipse.core.resources.IProject;
import org.eclipse.jdt.core.IClasspathEntry;
import org.eclipse.jdt.launching.JavaRuntime;
import org.eclipse.jst.ws.internal.jaxws.ui.JAXWSUIMessages;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Link;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.dialogs.PreferencesUtil;
import org.eclipse.ui.part.FileEditorInput;

public class ClasspathComposite extends Composite {
    
    private String JRE_PREF_PAGE_ID = "org.eclipse.jdt.debug.ui.preferences.VMPreferencePage"; //$NON-NLS-1$
    private String PROP_ID = "org.eclipse.jdt.ui.propertyPages.BuildPathsPropertyPage"; //$NON-NLS-1$
    private Object DATA_REVEAL_ENTRY = "select_classpath_entry"; //$NON-NLS-1$

    private Label informationLabel;
    
    public ClasspathComposite(Composite parent, int style) {
        super(parent, style);
        addControls();
    }
    
    public void addControls() {
        GridLayout gridLayout = new GridLayout();
        this.setLayout(gridLayout);
        GridData gridData = new GridData(SWT.FILL, SWT.FILL, true, true);
        this.setLayoutData(gridData);
        this.setBackground(getParent().getDisplay().getSystemColor(SWT.COLOR_WHITE));
        informationLabel = new Label(this, SWT.NONE);
        informationLabel.setBackground(getParent().getDisplay().getSystemColor(SWT.COLOR_WHITE));
        informationLabel.setText(JAXWSUIMessages.bind(
                JAXWSUIMessages.ANNOTATIONS_VIEW_NO_SUITABLE_LIBRARY_FOUND, "JAX-WS"));
        Link link = new Link(this, SWT.NONE);
        link.setBackground(getParent().getDisplay().getSystemColor(SWT.COLOR_WHITE));
        link.setText(JAXWSUIMessages.CONFIGURE_JAVA_1_6_LIBRARY);
        link.addSelectionListener(new SelectionAdapter() {
            public void widgetSelected(SelectionEvent selectionEvent) {
                if (selectionEvent.text.equals("1")) { //$NON-NLS-1$
                    PreferencesUtil.createPreferenceDialogOn(getShell(), JRE_PREF_PAGE_ID,
                            new String[] { JRE_PREF_PAGE_ID }, null).open();
                } else {
                    Map<Object, IClasspathEntry> data = new HashMap<Object, IClasspathEntry>();
                    data.put(DATA_REVEAL_ENTRY, JavaRuntime.getDefaultJREContainerEntry());
                    PreferencesUtil.createPropertyDialogOn(getShell(), getProject(), PROP_ID,
                            new String[] { PROP_ID }, data).open();
                }
            }
        });
        //TODO update the labels to provide information for supported annotation libraries that are missing
        //on the selected projects classpath.
        //Label otherLibrariesLabel  = new Label(this, SWT.SHADOW_IN);
        //otherLibrariesLabel.setBackground(getParent().getDisplay().getSystemColor(SWT.COLOR_WHITE));
        //otherLibrariesLabel.setText("Annotation Libraries currently supported: " + AnnotationsManager.getAnnotationCategories());
        //otherLibrariesLabel.setText(JAXWSUIMessages.ANNOTATIONS_VIEW_OTHER_ANNOTATION_LIBRARIES_USE);

    }

    private IProject getProject() {
        return ((FileEditorInput) PlatformUI.getWorkbench().getActiveWorkbenchWindow().getActivePage()
                .getActiveEditor().getEditorInput()).getFile().getProject();
    }
    
    
    public void updateLibraryLabel(String libraryName) {
        informationLabel.setText(JAXWSUIMessages.bind(
                JAXWSUIMessages.ANNOTATIONS_VIEW_NO_SUITABLE_LIBRARY_FOUND, libraryName));
    }
    
 }
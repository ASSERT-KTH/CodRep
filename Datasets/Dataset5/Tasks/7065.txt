.getMethodParameter(null, method, offset);

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
package org.eclipse.jst.ws.internal.jaxws.ui.views;

import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.List;

import org.eclipse.core.resources.IFile;
import org.eclipse.core.runtime.NullProgressMonitor;
import org.eclipse.jdt.core.ICompilationUnit;
import org.eclipse.jdt.core.IField;
import org.eclipse.jdt.core.IJavaElement;
import org.eclipse.jdt.core.IJavaProject;
import org.eclipse.jdt.core.IMethod;
import org.eclipse.jdt.core.IPackageDeclaration;
import org.eclipse.jdt.core.IType;
import org.eclipse.jdt.core.JavaModelException;
import org.eclipse.jdt.core.dom.SingleVariableDeclaration;
import org.eclipse.jdt.ui.JavaUI;
import org.eclipse.jface.action.IMenuManager;
import org.eclipse.jface.text.ITextSelection;
import org.eclipse.jface.text.TextSelection;
import org.eclipse.jface.viewers.ISelection;
import org.eclipse.jface.viewers.TreeViewer;
import org.eclipse.jface.viewers.TreeViewerColumn;
import org.eclipse.jface.viewers.Viewer;
import org.eclipse.jface.viewers.ViewerComparator;
import org.eclipse.jface.viewers.ViewerFilter;
import org.eclipse.jst.ws.annotations.core.AnnotationDefinition;
import org.eclipse.jst.ws.annotations.core.AnnotationsManager;
import org.eclipse.jst.ws.annotations.core.utils.AnnotationUtils;
import org.eclipse.jst.ws.internal.jaxws.ui.JAXWSUIMessages;
import org.eclipse.jst.ws.internal.jaxws.ui.JAXWSUIPlugin;
import org.eclipse.jst.ws.internal.jaxws.ui.actions.AnnotationsViewFilterAction;
import org.eclipse.jst.ws.internal.jaxws.ui.widgets.ClasspathComposite;
import org.eclipse.jst.ws.jaxws.core.utils.JDTUtils;
import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Tree;
import org.eclipse.swt.widgets.TreeColumn;
import org.eclipse.ui.IActionBars;
import org.eclipse.ui.IEditorDescriptor;
import org.eclipse.ui.IEditorInput;
import org.eclipse.ui.IEditorPart;
import org.eclipse.ui.IFileEditorInput;
import org.eclipse.ui.IMemento;
import org.eclipse.ui.INullSelectionListener;
import org.eclipse.ui.IPartListener2;
import org.eclipse.ui.IViewSite;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.IWorkbenchPart;
import org.eclipse.ui.IWorkbenchPartReference;
import org.eclipse.ui.IWorkbenchWindow;
import org.eclipse.ui.PartInitException;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.ide.IDE;
import org.eclipse.ui.part.PageBook;
import org.eclipse.ui.part.ViewPart;
import org.eclipse.ui.texteditor.ITextEditor;

/**
 * 
 * @author sclarke
 *
 */
public class AnnotationsView extends ViewPart implements INullSelectionListener, IPartListener2 {
    private PageBook pageBook;
    private Tree annotationTree;

    private Composite notAvaiableComposite;
    private ClasspathComposite setupClasspathComposite;
    
	private TreeViewer annotationTreeViewer;
	
	private IMemento memento;
	
	private AnnotationsViewFilterAction annotationsViewFilterAction;

	public AnnotationsView() {
	}

    public void createPartControl(Composite parent) {
        pageBook = new PageBook(parent, SWT.NONE);
        
        annotationTree = new Tree(pageBook, SWT.SINGLE | SWT.FULL_SELECTION | SWT.BORDER | SWT.V_SCROLL
                | SWT.H_SCROLL);
        annotationTreeViewer = new TreeViewer(annotationTree);
		
		annotationTreeViewer.setContentProvider(new AnnotationsViewContentProvider());
		annotationTreeViewer.getTree().setHeaderVisible(true);
		annotationTreeViewer.getTree().setLinesVisible(true);
		
		TreeViewerColumn annotationsViewerColumn = new TreeViewerColumn(annotationTreeViewer, SWT.NONE);
		annotationsViewerColumn.setLabelProvider(new AnnotationsColumnLabelProvider());
		TreeColumn annotationsColumn = annotationsViewerColumn.getColumn();
		annotationsColumn.setWidth(400);
        annotationsColumn.setMoveable(false);
        annotationsColumn.setText(JAXWSUIMessages.ANNOTATIONS_VIEW_ANNOTATIONS_COLUMN_NAME);
        
        TreeViewerColumn valuesViewerColumn = new TreeViewerColumn(annotationTreeViewer, SWT.NONE);
        valuesViewerColumn.setLabelProvider(new AnnotationsValuesColumnLabelProvider(annotationTreeViewer));
        valuesViewerColumn.setEditingSupport(new AnnotationsValuesEditingSupport(this, annotationTreeViewer));
        TreeColumn valuesColumn = valuesViewerColumn.getColumn(); 
		valuesColumn.setWidth(400);
		valuesColumn.setMoveable(false);
		valuesColumn.setAlignment(SWT.LEFT);
		valuesColumn.setText(JAXWSUIMessages.ANNOTATIONS_VIEW_ANNOTATIONS_VALUES_COLUMN_NAME);
		
		//Selection Service
		startListeningForSelectionChanges();
		//Part Service
		getViewSite().getWorkbenchWindow().getPartService().addPartListener(this);
		
		contributeToActionBars();
		
		notAvaiableComposite = new Composite(pageBook, SWT.NONE);
		GridLayout gridLayout = new GridLayout();
		notAvaiableComposite.setLayout(gridLayout);
		GridData gridData = new GridData(SWT.FILL, SWT.FILL, true, true);
		notAvaiableComposite.setLayoutData(gridData);
		notAvaiableComposite.setBackground(parent.getDisplay().getSystemColor(SWT.COLOR_WHITE));
		Label label = new Label(notAvaiableComposite, SWT.NONE);
		label.setBackground(parent.getDisplay().getSystemColor(SWT.COLOR_WHITE));
		label.setText(JAXWSUIMessages.ANNOTATIONS_VIEW_ANNOTATIONS_NOT_AVAILABLE_ON_SELECTION);
		
		annotationTreeViewer.setComparator(new ViewerComparator() {
            @Override
            public int compare(Viewer viewer, Object obj1, Object obj2) {
                if (obj1 instanceof Class) {
                  return AnnotationsManager.getAnnotationDefinitionForClass(obj1).getAnnotationClassName().
                      compareTo(AnnotationsManager.getAnnotationDefinitionForClass(obj2).
                              getAnnotationClassName());
                }
                if (obj1 instanceof Method) {
                    return ((Method)obj1).getName().compareTo(((Method)obj2).getName());
                }
                return super.compare(viewer, obj1, obj2);
            }
		});
		
		//TODO Add a Faceted Project composite
		setupClasspathComposite = new ClasspathComposite(pageBook, SWT.NONE);

		pageBook.showPage(notAvaiableComposite);
	}
    
    private void startListeningForSelectionChanges() {
        getViewSite().getWorkbenchWindow().getSelectionService().addPostSelectionListener(this);
    }
    
    private void stopListeningForSelectionChanges() {
        getViewSite().getWorkbenchWindow().getSelectionService().removePostSelectionListener(this);
    }
    
    public void selectionChanged(IWorkbenchPart part, ISelection selection) {
        IWorkbenchPage workbenchPage = getViewSite().getWorkbenchWindow().getActivePage();
        IWorkbenchPartReference workbenchPartReference = workbenchPage.getActivePartReference();
       
        if ( workbenchPartReference.getId().equals(getViewSite().getId()) 
                || !workbenchPartReference.getId().equals(JavaUI.ID_CU_EDITOR)) {
            return;
        }

        IEditorPart editorPart = workbenchPage.getActiveEditor();

        IFileEditorInput fileEditorInput = (IFileEditorInput) editorPart.getEditorInput();

        if (selection instanceof TextSelection) {
            ITextSelection txtSelection = (TextSelection) selection;
            ICompilationUnit compilationUnit = JDTUtils.getCompilationUnitFromFile(fileEditorInput.getFile());
            if (compilationUnit != null) {
                updateView(compilationUnit, txtSelection);
            }
        }
    }

	public void updateView(IJavaElement javaElement, ITextSelection textSelection) {
        IJavaProject javaProject = javaElement.getJavaProject();

        if (!checkClasspath(javaProject)) {
            annotationTreeViewer.setInput(null);
            pageBook.showPage(setupClasspathComposite);
            return;
        }

        pageBook.showPage(annotationTree);

	    int offset = textSelection.getOffset();
        try {
            ICompilationUnit compilationUnit = null;
            if (javaElement instanceof ICompilationUnit) {
                compilationUnit = (ICompilationUnit)javaElement;
                javaElement = compilationUnit.getElementAt(offset);
            }
        
            if (javaElement == null) {
                return;
            }
            
            if (javaElement.getElementType() == IJavaElement.PACKAGE_DECLARATION) {
                if (javaElement.getResource().getName().equals("package-info.java")) { //$NON-NLS-1$
                    annotationTreeViewer.setInput((IPackageDeclaration) javaElement);
                } else {
                    annotationTreeViewer.setInput(null);
                }
            }
            
            if (javaElement.getElementType() == IJavaElement.IMPORT_DECLARATION) {
                annotationTreeViewer.setInput(null);
            }
            
            if (javaElement.getElementType() == IJavaElement.TYPE) {
                annotationTreeViewer.setInput((IType) javaElement);
            }
    
            if (javaElement.getElementType() == IJavaElement.FIELD) {
                annotationTreeViewer.setInput((IField) javaElement);
            }

            if (javaElement.getElementType() == IJavaElement.METHOD) {
                IMethod method = (IMethod) javaElement;
                SingleVariableDeclaration parameter = AnnotationUtils
                        .getMethodParameter(method, offset);
                if (parameter != null) {
                    annotationTreeViewer.setInput(parameter);
                } else {
                    annotationTreeViewer.setInput(method);
                }
            }
            annotationTreeViewer.refresh();
        } catch (JavaModelException jme) {
            JAXWSUIPlugin.log(jme.getStatus());
        }
	}
    
    private boolean checkClasspath(IJavaProject javaProject) {
        List<String> categories = new ArrayList<String>();
        categories.addAll(AnnotationsManager.getAnnotationCategories());
        ViewerFilter[] viewerFilters = annotationTreeViewer.getFilters();
        for (ViewerFilter viewerFilter : viewerFilters) {
           if (viewerFilter instanceof AnnotationsViewCategoryFilter) {
               categories.removeAll(((AnnotationsViewCategoryFilter)viewerFilter).getCategories());
           }
        }

        boolean jwsReady = true;
        try {
            for (String category : categories) {
                List<AnnotationDefinition> annotationDefinitions = AnnotationsManager
                        .getAnnotationsByCategory(category);
                String className = annotationDefinitions.get(0).getAnnotationClassName();
                if (javaProject.findType(className) == null) {
                    jwsReady = false;
                    setupClasspathComposite.updateLibraryLabel(category);
                    break;
                } else {
                    continue;
                }
            }
        } catch (JavaModelException jme) {
            JAXWSUIPlugin.log(jme.getStatus());
        }
        return jwsReady;
    }

    public void partActivated(IWorkbenchPartReference partRef) {
        IWorkbenchPart workbenchPart = partRef.getPart(false);
        if (partRef.getId().equals(JavaUI.ID_CU_EDITOR)) {
            javaEditorActivated((IEditorPart) workbenchPart);
        } else if (partRef.getId().equals(getViewSite().getId())) {
            //annotationsViewActivated();
        } else {
            clearAnnotationsView();
        }
    }

    public void partDeactivated(IWorkbenchPartReference partRef) {
    }

    public void partVisible(IWorkbenchPartReference partRef) {
        if (partRef.getId().equals(getViewSite().getId())) {
            startListeningForSelectionChanges();
        }
    }

    public void partHidden(IWorkbenchPartReference partRef) {
        if (partRef.getId().equals(getViewSite().getId())) {
            stopListeningForSelectionChanges();
        }
    }

    public void partOpened(IWorkbenchPartReference partRef) {
    }

    public void partClosed(IWorkbenchPartReference partRef) {
        if (partRef.getId().equals(JavaUI.ID_CU_EDITOR)) {
            if (getViewSite() != null) {
                IWorkbenchWindow workbenchWindow = getViewSite().getWorkbenchWindow();
                if (workbenchWindow != null) {
                    IWorkbenchPage workbenchPage = workbenchWindow.getActivePage();
                    if (workbenchPage != null) {
                        IEditorPart editorPart = workbenchPage.getActiveEditor();
                        try {
                            if (editorPart == null
                                    || !(editorPart.getEditorInput() instanceof IFileEditorInput)
                                    || !IDE.getEditorDescriptor(
                                            ((IFileEditorInput) editorPart.getEditorInput()).getFile()).getId()
                                            .equals(JavaUI.ID_CU_EDITOR)) {
                                clearAnnotationsView();
                            }
                        } catch (PartInitException pie) {
                            JAXWSUIPlugin.log(pie.getStatus());
                        }                 
                    }
                }
            }
        }
    }

    public void partBroughtToTop(IWorkbenchPartReference partRef) {
    }

    public void partInputChanged(IWorkbenchPartReference partRef) {
    }
	
	private void clearAnnotationsView() {
        annotationTreeViewer.setInput(null);
        annotationTreeViewer.refresh();
        pageBook.showPage(notAvaiableComposite);                
	}
	
	private void javaEditorActivated(IEditorPart editorPart) {
        ITextEditor textEditor = (ITextEditor) editorPart;
        ISelection selection = textEditor.getSelectionProvider().getSelection();
        IJavaElement javaElement = (IJavaElement) editorPart.getEditorInput().getAdapter(IJavaElement.class);
        if (javaElement != null) {
            pageBook.showPage(annotationTree);
            updateView(javaElement, (ITextSelection) selection);
            selectionChanged(editorPart, selection);
        }
    }

    private void annotationsViewActivated() {
        try {
            IEditorPart editorPart = getViewSite().getPage().getActiveEditor();
            if (editorPart != null) {
                IEditorInput editorInput = editorPart.getEditorInput();
                if (editorInput instanceof IFileEditorInput) {
                    IFile file = ((IFileEditorInput) editorInput).getFile();
                    IEditorDescriptor editorDescriptor = IDE.getEditorDescriptor(file);
                    if (editorDescriptor.getId().equals(JavaUI.ID_CU_EDITOR)) {
                        javaEditorActivated(editorPart);
                    }
                }
            }
        } catch (PartInitException pie) {
            JAXWSUIPlugin.log(pie.getStatus());
        }
    }
	
    @Override
    public void dispose() {
        super.dispose();
        stopListeningForSelectionChanges();
        getViewSite().getWorkbenchWindow().getPartService().removePartListener(this);
    }
    
    @Override
    public void init(IViewSite site, IMemento memento) throws PartInitException {
        super.init(site, memento);
        this.memento = memento;
    }

    @Override
    public void saveState(IMemento memento) {
        super.saveState(memento);
        annotationsViewFilterAction.saveState(memento);
    }

	private void contributeToActionBars() {
		IActionBars bars = getViewSite().getActionBars();
		fillLocalPullDown(bars.getMenuManager());
	}

	private void fillLocalPullDown(IMenuManager manager) {
	    annotationsViewFilterAction = new AnnotationsViewFilterAction(this, annotationTreeViewer,
	            JAXWSUIMessages.ANNOTATIONS_VIEW_FILTER_ACTION_NAME);
	    if (memento != null) {
	        annotationsViewFilterAction.init(memento);
	    }
	    manager.add(annotationsViewFilterAction);
	}

	/**
	 * Passing the focus request to the viewer's control.
	 */
	public void setFocus() {
		annotationTreeViewer.getControl().setFocus();
	}
	
    public void refresh() {
        Display display = annotationTreeViewer.getControl().getDisplay();
        if (!display.isDisposed()) {
            display.asyncExec(new Runnable() {
                public void run() {
                    IWorkbenchWindow workbenchWindow = PlatformUI.getWorkbench().getActiveWorkbenchWindow();
                    IWorkbenchPage workbenchPage = workbenchWindow.getActivePage();
                    IEditorPart editorPart = workbenchPage.getActiveEditor();
                    try {
                        if (editorPart != null
                                && editorPart.getEditorInput() instanceof IFileEditorInput
                                && IDE.getEditorDescriptor(
                                        ((IFileEditorInput) editorPart.getEditorInput()).getFile()).getId()
                                        .equals(JavaUI.ID_CU_EDITOR)) {
                            ITextEditor txtEditor = (ITextEditor) workbenchPage.getActiveEditor();
                            IFileEditorInput fileEditorInput = (IFileEditorInput) txtEditor.getEditorInput();

                            ICompilationUnit compilationUnit = JDTUtils
                                    .getCompilationUnitFromFile(fileEditorInput.getFile());
                            if (compilationUnit != null) {
                                if (!compilationUnit.isConsistent()) {
                                    compilationUnit.makeConsistent(new NullProgressMonitor());
                                }
                                updateView(compilationUnit, (ITextSelection) txtEditor.getSelectionProvider()
                                        .getSelection());
                            }
                        }
                    } catch (JavaModelException jme) {
                        JAXWSUIPlugin.log(jme.getStatus());
                    } catch (PartInitException pie) {
                        JAXWSUIPlugin.log(pie.getStatus());
                    }
                }
            });
        }
    }
}
 No newline at end of file
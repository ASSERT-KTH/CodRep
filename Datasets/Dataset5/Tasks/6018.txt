import org.eclipse.jst.ws.annotations.core.AnnotationsManager;

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
package org.eclipse.jst.ws.internal.jaxws.ui.actions;

import java.util.Arrays;
import java.util.List;

import org.eclipse.jface.action.Action;
import org.eclipse.jface.viewers.IStructuredContentProvider;
import org.eclipse.jface.viewers.LabelProvider;
import org.eclipse.jface.viewers.StructuredViewer;
import org.eclipse.jface.viewers.Viewer;
import org.eclipse.jface.window.Window;
import org.eclipse.jst.ws.internal.jaxws.core.annotations.AnnotationsManager;
import org.eclipse.jst.ws.internal.jaxws.ui.JAXWSUIMessages;
import org.eclipse.jst.ws.internal.jaxws.ui.JAXWSUIPlugin;
import org.eclipse.jst.ws.internal.jaxws.ui.views.AnnotationsView;
import org.eclipse.jst.ws.internal.jaxws.ui.views.AnnotationsViewCategoryFilter;
import org.eclipse.swt.graphics.Image;
import org.eclipse.ui.IMemento;
import org.eclipse.ui.dialogs.ListSelectionDialog;

/**
 * @author sclarke
 *
 */
public class AnnotationsViewFilterAction extends Action {
    private StructuredViewer viewer;
    private AnnotationsViewCategoryFilter categoryFilter;
    
    public AnnotationsViewFilterAction(AnnotationsView annotationsView, StructuredViewer viewer, String text) {
        super(text);
        this.viewer = viewer;
        this.setImageDescriptor(JAXWSUIPlugin.getImageDescriptor("icons/elcl16/filter_ps.gif")); //$NON-NLS-1$
        categoryFilter = new AnnotationsViewCategoryFilter(annotationsView, viewer);
    }

    @Override
    public void run() {
        ListSelectionDialog listSelectionDialog = new ListSelectionDialog(viewer.getControl().getShell(),
                AnnotationsManager.getAnnotationCategories(), new AnnotationsCategoryDialogContentProvider(),
                new AnnotationsCategoryDialogLabelProvider(), 
                JAXWSUIMessages.ANNOTATIONS_VIEW_FILTER_ACTION_SELECT_CATEGORIES_MESSAGE);
        
        listSelectionDialog.setInitialElementSelections(categoryFilter.getCategories());
        
        int returnValue = listSelectionDialog.open();
        if (returnValue == Window.OK) {
            Object[] result = listSelectionDialog.getResult();
            categoryFilter.filterAnnotations(Arrays.asList(result));
        }
    }
    
    public void init(IMemento memento) {
        categoryFilter.init(memento);
    }
    
    public void saveState(IMemento memento) {
        categoryFilter.saveState(memento);
    }
    
    private static class AnnotationsCategoryDialogContentProvider implements IStructuredContentProvider {

        public Object[] getElements(Object inputElement) {
            if (inputElement instanceof List) {
                return ((List<String>)inputElement).toArray();
            }
            return new Object[] {};
        }

        public void dispose() {
        }

        public void inputChanged(Viewer viewer, Object oldInput, Object newInput) {
        }
        
    }
    
    private static class AnnotationsCategoryDialogLabelProvider extends LabelProvider {
        public String getText(Object element) {
            return element.toString();
        }

        public Image getImage(Object element) {
            return null;
        }
    }
}
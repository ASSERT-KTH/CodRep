return AnnotationsManager.getAnnotations(inputElement).toArray();

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

import org.eclipse.jface.viewers.ITreeContentProvider;
import org.eclipse.jface.viewers.Viewer;
import org.eclipse.jst.ws.annotations.core.AnnotationsManager;

public class AnnotationsViewContentProvider implements ITreeContentProvider {

	public Object[] getChildren(Object parentElement) {
	    if (parentElement instanceof Class) {
	        return ((Class<?>)parentElement).getDeclaredMethods();
	    }
		return new Object[] {};
	}

	public Object getParent(Object element) {
		return null;
	}

	public boolean hasChildren(Object element) {
	    if (element instanceof Class) {
	        return ((Class<?>)element).getDeclaredMethods().length > 0;
	    }
		return false;
	}

	public Object[] getElements(Object inputElement) {
	    if (inputElement != null) {
	        return AnnotationsManager.getAnnotations(inputElement);
	    }
	    return new Object[] {};
	}
	
	public void dispose() {

	}

	public void inputChanged(Viewer viewer, Object oldInput, Object newInput) {
	}

}
return ((IResultList) element).getResults().size() + Messages.UserSearchLabelProvider_ContactsFound;

/*******************************************************************************
 * Copyright (c) 2008 Marcelo Mayworm. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: 	Marcelo Mayworm - initial API and implementation
 *
 ******************************************************************************/
package org.eclipse.ecf.presence.ui;

import org.eclipse.ecf.internal.presence.ui.Messages;
import org.eclipse.ecf.presence.search.IResult;
import org.eclipse.ecf.presence.search.IResultList;
import org.eclipse.ecf.ui.SharedImages;
import org.eclipse.jface.viewers.LabelProvider;
import org.eclipse.swt.graphics.Image;

/**
 * Label provider for multiple users viewer. This label provider implements an
 * LabelProvider suitable for use by viewers that accepts LabelProvider as
 * input. This class may be subclassed in order to customize the
 * behavior/display of other label providers.
 * @since 2.0
 * 
 */
public class UserSearchLabelProvider extends LabelProvider {

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.jface.viewers.LabelProvider#getImage(java.lang.Object)
	 */
	public Image getImage(Object element) {
		if (element instanceof IResultList)
			return SharedImages.getImage(SharedImages.IMG_GROUP);
		if (element instanceof IResult)
			return SharedImages.getImage(SharedImages.IMG_USER_AVAILABLE);

		return null;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.jface.viewers.LabelProvider#getText(java.lang.Object)
	 */
	public String getText(Object element) {
		if (element instanceof IResult) {
			return ((IResult) element).getUser().getName();
		} else if (element instanceof IResultList) {
			return ((IResultList) element).geResults().size() + Messages.UserSearchLabelProvider_ContactsFound;
		}
		return element.toString();
	}

}
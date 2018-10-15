package org.eclipse.ecf.internal.ui;

package org.eclipse.ecf.ui;

import org.eclipse.jface.preference.PreferencePage;
import org.eclipse.jface.resource.ImageDescriptor;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.ui.IWorkbench;
import org.eclipse.ui.IWorkbenchPreferencePage;

public class CategoryPreferencePage extends PreferencePage implements
		IWorkbenchPreferencePage {

	public CategoryPreferencePage() {
	}

	public CategoryPreferencePage(String title) {
		super(title);
	}

	public CategoryPreferencePage(String title, ImageDescriptor image) {
		super(title, image);
	}

	protected Control createContents(Composite parent) {
		return null;
		
	}

	public void init(IWorkbench workbench) {
	}

}
public IXtendXpandResource findXtendXpandResource(String extxptNamespace, String extension);

/*******************************************************************************
 * Copyright (c) 2005, 2007 committers of openArchitectureWare and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     committers of openArchitectureWare - initial API and implementation
 *******************************************************************************/

package org.eclipse.xtend.shared.ui.core;

import org.eclipse.core.resources.IResource;
import org.eclipse.core.resources.IStorage;
import org.eclipse.core.runtime.IPath;
import org.eclipse.core.runtime.IProgressMonitor;

public interface IModelManager {

    public abstract IXtendXpandResource findExtXptResource(IStorage storage);

    public abstract IXtendXpandProject findProject(IPath path);

    public abstract IXtendXpandProject findProject(IResource resource);

    public abstract void analyze(IProgressMonitor monitor);

	public IXtendXpandResource findOawResource(String oawNamespace, String extension);

}
 No newline at end of file
package org.eclipse.wst.xquery.core.codeassist;

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
package org.eclipse.wst.xquery.internal.core.codeassist;

import org.eclipse.dltk.core.IScriptProject;

public interface IImplicitImportActivator {

    public abstract boolean activateForProject(IScriptProject project);

}
 No newline at end of file
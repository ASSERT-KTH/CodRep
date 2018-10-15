//			XtendXpandMarkerManager.deleteMarkers((IFile) source);

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
package org.eclipse.xtend.shared.ui;

import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.Reader;

import org.eclipse.core.resources.IFile;
import org.eclipse.core.resources.IMarker;
import org.eclipse.core.resources.IStorage;
import org.eclipse.core.runtime.CoreException;
import org.eclipse.internal.xtend.xtend.parser.ErrorHandler;
import org.eclipse.internal.xtend.xtend.parser.XtendError;
import org.eclipse.xtend.expression.Resource;
import org.eclipse.xtend.shared.ui.core.IXtendXpandResource;
import org.eclipse.xtend.shared.ui.core.builder.XtendXpandMarkerManager;

/**
 * Base implementation of the {@link ResourceContributor} interface with common
 * used methods.
 * 
 * @author kthoms
 * @since 4.1.2
 */
public abstract class ResourceContributorBase implements ResourceContributor {

	protected ErrorHandler getErrorHandler(final IStorage source) {
		if (source instanceof IFile) {
			XtendXpandMarkerManager.deleteMarkers((IFile) source);
		}
		return new ErrorHandler() {

			public void handleError(XtendError e) {
				// BNI bug#312571
				// 1. start position can be 0 (missing semicolon at the end of a file)
				// 2. why should only one error be handled (!hasErrors)
				if (e.getStart() >= 0) {
					if (source instanceof IFile) {
						IFile f = (IFile) source;
						XtendXpandMarkerManager.addErrorMarker(f, e.getMessage(), IMarker.SEVERITY_ERROR, e.getStart(),
								e.getEnd());
					}
				}
			}
		};
	}

	protected abstract void logInfo(String message);

	protected abstract void logError(String message, Throwable t);

	/**
	 * @see ResourceContributor#parse(IStorage, IXtendXpandResource)
	 */
	public final IXtendXpandResource create(final IStorage file, String fqn) {
		Resource res = parse(file, fqn);

		if (res != null) {
			return createExtXptResource(res, file);
		}
		return null;
	}

	protected Reader createReader(IStorage resource) {
		InputStream in;
		try {
			in = resource.getContents();
			return new InputStreamReader(in);
		} catch (final CoreException e1) {
			logInfo(e1.getMessage());
			return null;
		}
	}

	/**
	 * Parse the resource file.
	 * 
	 * @param source
	 * @return The succesfully
	 */
	protected abstract Resource parse(IStorage source, String fqn);

	protected abstract IXtendXpandResource createExtXptResource(Resource resource,
			IStorage source);

}
if (!cxfLibraryVersion.equals(getCxfRuntimeVersion())) {

/*******************************************************************************
 * Copyright (c) 2008 IONA Technologies PLC
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 * IONA Technologies PLC - initial API and implementation
 *******************************************************************************/
package org.eclipse.jst.ws.internal.cxf.core;

import java.io.File;
import java.text.MessageFormat;
import java.util.ArrayList;
import java.util.List;

import org.eclipse.core.runtime.IPath;
import org.eclipse.core.runtime.Path;
import org.eclipse.jdt.core.IClasspathContainer;
import org.eclipse.jdt.core.IClasspathEntry;
import org.eclipse.jdt.core.IJavaProject;
import org.eclipse.jdt.core.JavaCore;

/**
 * 
 * @author sclarke
 *
 */
public class CXFClasspathContainer implements IClasspathContainer {

	private IPath path;
	private List<IClasspathEntry> classpathEntries;
	private String cxfLibraryEdition;
	private String cxfLibraryVersion;
	private String cxfLibraryLocation;
	
	public CXFClasspathContainer(IPath path, IJavaProject javaProject) {
		this.path = path;
		classpathEntries =  new ArrayList<IClasspathEntry>();
		cxfLibraryLocation = getCxfRuntimeLocation();
		cxfLibraryVersion = getCxfRuntimeVersion();
		cxfLibraryEdition = getCxfRuntimeEdition();
	}
	
	public IClasspathEntry[] getClasspathEntries() {
        if (cxfLibraryVersion != getCxfRuntimeVersion()) {
            classpathEntries = new ArrayList<IClasspathEntry>();
            cxfLibraryLocation = getCxfRuntimeLocation();
            cxfLibraryVersion = getCxfRuntimeVersion();
            cxfLibraryEdition = getCxfRuntimeEdition();
        }

	    if (classpathEntries.size() == 0) {
	        File cxfLibDirectory = getCXFLibraryDirectory();
	        if (cxfLibDirectory.exists() && cxfLibDirectory.isDirectory()) {
	            String[] files = cxfLibDirectory.list();
	            for (int i = 0; i < files.length; i++) {
	                File file = new File(cxfLibDirectory.getPath() + File.separator + files[i]);
	                String fileName = file.getName();
	                if (fileName.indexOf(".") != -1
	                        && fileName.substring(fileName.lastIndexOf("."), fileName.length()).equals(
	                                ".jar")) {
	                	classpathEntries.add(JavaCore.newLibraryEntry(new Path(file.getAbsolutePath()), null, 
	                	        new Path("/")));
	                }
	            }
	        }
		}
		return classpathEntries.toArray(new IClasspathEntry[classpathEntries.size()]);
	}
	
	public boolean isValid() {
	    if (getCxfRuntimeLocation().length() > 0) {
            File cxfLibDirectory = getCXFLibraryDirectory();
            return cxfLibDirectory.exists() && cxfLibDirectory.isDirectory();
	    }
	    return false;
	}
	
	public String getDescription() {
		return  MessageFormat.format(CXFCoreMessages.CXF_CONTAINER_LIBRARY, cxfLibraryEdition, 
		        cxfLibraryVersion);
	}

	public int getKind() {
		return K_APPLICATION;
	}

	public IPath getPath() {
		return path;
	}
	
	private String getCxfRuntimeLocation() {
	    return CXFCorePlugin.getDefault().getJava2WSContext().getCxfRuntimeLocation();
    }

    private String getCxfRuntimeVersion() {
        return CXFCorePlugin.getDefault().getJava2WSContext().getCxfRuntimeVersion();
    }

    private String getCxfRuntimeEdition() {
        return CXFCorePlugin.getDefault().getJava2WSContext().getCxfRuntimeEdition();
    }

	private File getCXFLibraryDirectory() {
        IPath cxfLibPath = new Path(cxfLibraryLocation);
        if (!cxfLibPath.hasTrailingSeparator()) {
            cxfLibPath = cxfLibPath.addTrailingSeparator();
        }
        cxfLibPath = cxfLibPath.append("lib"); //$NON-NLS-1$

        File cxfLibDirectory = new File(cxfLibPath.toOSString());
        return cxfLibDirectory;
    }
}
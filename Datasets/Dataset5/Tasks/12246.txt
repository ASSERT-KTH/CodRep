DebugOptions.PACKAGE_VERSION_COMPARATOR, this.getClass(),

/*******************************************************************************
 * Copyright (c) 2010-2011 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *   Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.osgi.services.remoteserviceadmin;

import org.eclipse.ecf.internal.osgi.services.remoteserviceadmin.DebugOptions;
import org.eclipse.ecf.internal.osgi.services.remoteserviceadmin.LogUtility;
import org.osgi.framework.Version;

public class PackageVersionComparator implements IPackageVersionComparator {

	public void comparePackageVersions(String packageName,
			Version remoteVersion, Version localVersion)
			throws RuntimeException {
		LogUtility.trace("comparePackageVersions",
				DebugOptions.PACKAGEVERSIONCOMPARATOR, this.getClass(),
				"packageName=" + packageName + ",remoteVersion="
						+ remoteVersion + ",localVersion=" + localVersion);
		// By default we do strict comparison of remote with local...they must
		// be exactly the same, or we thrown a runtim exception
		int compareResult = localVersion.compareTo(remoteVersion);
		// Now check compare result, and throw exception to fail compare
		if (compareResult != 0)
			throw new RuntimeException(
					"Package version compare failed with compareResult="
							+ compareResult + " for package=" + packageName
							+ " localVersion=" + localVersion
							+ " remoteVersion=" + remoteVersion);
	}

}
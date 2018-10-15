package org.eclipse.wst.xquery.core.utils;

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
package org.eclipse.wst.xquery.internal.core.utils;

import java.util.Arrays;

import org.eclipse.core.runtime.IPath;
import org.eclipse.core.runtime.Path;

public class PathUtil {

    public static IPath makePathRelativeTo(IPath path, IPath base) {
        String device = path.getDevice();
        String[] segments = path.segments();

        //can't make relative if devices are not equal
        if (device != base.getDevice() && (device == null || !device.equalsIgnoreCase(base.getDevice()))) {
            return path;
        }
        int commonLength = path.matchingFirstSegments(base);
        final int differenceLength = base.segmentCount() - commonLength;
        final int newSegmentLength = differenceLength + path.segmentCount() - commonLength;
        if (newSegmentLength == 0) {
            return Path.EMPTY;
        }
        String[] newSegments = new String[newSegmentLength];
        //add parent references for each segment different from the base
        Arrays.fill(newSegments, 0, differenceLength, ".."); //$NON-NLS-1$
        //append the segments of this path not in common with the base
        System.arraycopy(segments, commonLength, newSegments, differenceLength, newSegmentLength - differenceLength);
        IPath resPath = new Path(null, "");
        for (String string : newSegments) {
            resPath = resPath.append(string);
        }
        if (path.hasTrailingSeparator()) {
            resPath.addTrailingSeparator();
        }
        return resPath;
    }
}
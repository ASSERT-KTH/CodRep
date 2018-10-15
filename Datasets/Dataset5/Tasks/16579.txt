ID id = IDFactory.getDefault().createStringID(DataGraphSharing.DATA_GRAPH_SHARING_ID);

/*******************************************************************************
 * Copyright (c) 2004 Peter Nehrer and Composent, Inc.
 * All rights reserved. This program and the accompanying materials 
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors:
 *     Peter Nehrer - initial API and implementation
 *******************************************************************************/
package org.eclipse.ecf.internal.sdo;

import org.eclipse.ecf.core.ISharedObjectContainer;
import org.eclipse.ecf.core.ISharedObjectManager;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.util.ECFException;
import org.eclipse.ecf.sdo.IDataGraphSharing;
import org.eclipse.ecf.sdo.IDataGraphSharingManager;

/**
 * @author pnehrer
 */
public class DataGraphSharingManager implements IDataGraphSharingManager {

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.sdo.IDataGraphSharingManager#getInstance(org.eclipse.ecf.core.ISharedObjectContainer)
     */
    public synchronized IDataGraphSharing getInstance(
            ISharedObjectContainer container) throws ECFException {
        ISharedObjectManager mgr = container.getSharedObjectManager();
        ID id = IDFactory.getDefault().makeStringID(DataGraphSharing.DATA_GRAPH_SHARING_ID);
        DataGraphSharing result = (DataGraphSharing) mgr.getSharedObject(id);
        if (result == null) {
            result = new DataGraphSharing();
            mgr.addSharedObject(id, result, null);
        }

        return result;
    }
}
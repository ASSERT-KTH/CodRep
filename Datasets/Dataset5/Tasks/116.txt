import org.eclipse.jst.ws.jaxws.core.utils.WSDLUtils;

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
package org.eclipse.jst.ws.internal.cxf.ui.viewers;

import java.util.Map;

import org.eclipse.jface.viewers.ColumnLabelProvider;
import org.eclipse.jst.ws.internal.cxf.core.model.WSDL2JavaDataModel;
import org.eclipse.jst.ws.internal.cxf.core.utils.WSDLUtils;

/**
 * @author sclarke
 */
public class PackageNameColumnLabelProvider extends ColumnLabelProvider {
    private Map<String, String> includedNamespaces;

    public PackageNameColumnLabelProvider(WSDL2JavaDataModel model) {
        includedNamespaces = model.getIncludedNamespaces();
    }

    @Override
    public String getText(Object element) {
        if (includedNamespaces.containsKey(element.toString())) {
            return includedNamespaces.get(element.toString());
        }
        return WSDLUtils.getPackageNameFromNamespace(element.toString());
    }

}
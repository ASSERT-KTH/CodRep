if (annotationKey.equals(CXFModelUtils.WEB_PARAM)) {

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
package org.eclipse.jst.ws.internal.cxf.creation.ui.viewers;

import java.util.List;
import java.util.Map;

import org.eclipse.jdt.core.IMethod;
import org.eclipse.jdt.core.IType;
import org.eclipse.jdt.core.dom.SingleVariableDeclaration;
import org.eclipse.jdt.internal.core.SourceMethod;
import org.eclipse.jface.viewers.ColumnLabelProvider;
import org.eclipse.jst.ws.internal.cxf.core.model.Java2WSDataModel;
import org.eclipse.jst.ws.internal.cxf.core.utils.CXFModelUtils;
import org.eclipse.jst.ws.annotations.core.utils.AnnotationUtils;
import org.eclipse.jst.ws.internal.cxf.creation.ui.CXFCreationUIPlugin;
import org.eclipse.swt.graphics.Image;

/**
 * @author sclarke
 */
@SuppressWarnings("restriction")
public class AnnotationColumnLabelProvider extends ColumnLabelProvider {
    private Image addAnnotationImage;
    private Image removeAnnotationImage;
    private Image disabled;

    private Map<IMethod, Map<String, Boolean>> methodMap;
    private String annotationKey;
    private IType type;

    public AnnotationColumnLabelProvider(Java2WSDataModel model, String annotationKey, IType type) {
        this.methodMap = model.getMethodMap();
        this.annotationKey = annotationKey;
        this.type = type;
        addAnnotationImage = CXFCreationUIPlugin.imageDescriptorFromPlugin(CXFCreationUIPlugin.PLUGIN_ID,
                "icons/obj16/true.gif").createImage(); //$NON-NLS-1$
        removeAnnotationImage = CXFCreationUIPlugin.imageDescriptorFromPlugin(CXFCreationUIPlugin.PLUGIN_ID,
                "icons/obj16/false.gif").createImage(); //$NON-NLS-1$
        disabled = CXFCreationUIPlugin.imageDescriptorFromPlugin(CXFCreationUIPlugin.PLUGIN_ID,
                "icons/obj16/disabled.gif").createImage(); //$NON-NLS-1$
    }

    public String getText(Object element) {
        return ""; //$NON-NLS-1$
    }

    @Override
    public Image getImage(Object element) {
        if (element instanceof SourceMethod) {
            if (methodMap == null || annotationKey == null || type == null) {
                return null;
            }

            IMethod method = (SourceMethod) element;

            if (annotationKey == CXFModelUtils.WEB_PARAM) {
                List<SingleVariableDeclaration> parameters = AnnotationUtils.getMethodParameters(type,
                        method);

                if (parameters.size() == 0) {
                    return disabled;
                }
                for (SingleVariableDeclaration parameter : parameters) {
                    if (AnnotationUtils.isAnnotationPresent(parameter, annotationKey)) {
                        return disabled;
                    }
                }
            }
            
            if (AnnotationUtils.isAnnotationPresent(method, annotationKey)) {
                return disabled;
            }
            
            if (methodMap.get(method) != null) {
                Boolean addAnnotation =  methodMap.get(method).get(annotationKey);
                if (addAnnotation) {
                    return addAnnotationImage;
                } else {
                    return removeAnnotationImage;
                }                
            }
        }
        return null;
    }

    @Override
    public void dispose() {
        super.dispose();
        addAnnotationImage.dispose();
        removeAnnotationImage.dispose();
        disabled.dispose();
    }

}
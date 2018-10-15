package org.eclipse.jst.ws.internal.jaxws.ui.annotations.initialization;

/*******************************************************************************
 * Copyright (c) 2009 Shane Clarke.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Shane Clarke - initial API and implementation
 *******************************************************************************/
package org.eclipse.jst.ws.internal.jaxws.core.annotations.initialization;

import static org.eclipse.jst.ws.internal.jaxws.core.utils.JAXWSUtils.PARAMETER_STYLE;
import static org.eclipse.jst.ws.internal.jaxws.core.utils.JAXWSUtils.STYLE;
import static org.eclipse.jst.ws.internal.jaxws.core.utils.JAXWSUtils.USE;

import java.lang.annotation.Annotation;
import java.util.ArrayList;
import java.util.List;

import javax.jws.soap.SOAPBinding;
import javax.jws.soap.SOAPBinding.ParameterStyle;
import javax.jws.soap.SOAPBinding.Style;
import javax.jws.soap.SOAPBinding.Use;

import org.eclipse.jdt.core.IJavaElement;
import org.eclipse.jdt.core.dom.AST;
import org.eclipse.jdt.core.dom.MemberValuePair;
import org.eclipse.jst.ws.annotations.core.AnnotationsCore;
import org.eclipse.jst.ws.annotations.core.initialization.AnnotationAttributeInitializer;

public class SOAPBindingAttributeInitializer extends AnnotationAttributeInitializer {

    @Override
    public List<MemberValuePair> getMemberValuePairs(IJavaElement javaElement, AST ast,
            Class<? extends Annotation> annotationClass) {
        List<MemberValuePair> memberValuePairs = new ArrayList<MemberValuePair>();

        MemberValuePair styleValuePair = AnnotationsCore.createEnumMemberValuePair(ast,
                SOAPBinding.class.getCanonicalName(), STYLE, Style.DOCUMENT);

        MemberValuePair useValuePair = AnnotationsCore.createEnumMemberValuePair(ast,
                SOAPBinding.class.getCanonicalName(), USE, Use.LITERAL);

        MemberValuePair parameterStyleValuePair = AnnotationsCore.createEnumMemberValuePair(ast,
                SOAPBinding.class.getCanonicalName(), PARAMETER_STYLE, ParameterStyle.WRAPPED);
        
        memberValuePairs.add(styleValuePair);
        memberValuePairs.add(useValuePair);
        memberValuePairs.add(parameterStyleValuePair);
        return memberValuePairs;
    }
}
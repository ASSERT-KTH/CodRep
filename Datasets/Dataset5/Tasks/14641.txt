textFileChange.addEdit(AnnotationUtils.createAddImportTextEdit(myPackage, XmlSchema.class.getCanonicalName()));

/*******************************************************************************
 * Copyright (c) 2009 Progress Software
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Shane Clarke - initial API and implementation
 *******************************************************************************/
package org.eclipse.jst.ws.jaxb.core.tests;

import java.util.ArrayList;
import java.util.List;

import javax.xml.bind.annotation.XmlSchema;

import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.NullProgressMonitor;
import org.eclipse.jdt.core.IPackageDeclaration;
import org.eclipse.jdt.core.dom.Annotation;
import org.eclipse.jdt.core.dom.MemberValuePair;
import org.eclipse.jst.ws.annotations.core.AnnotationsCore;
import org.eclipse.jst.ws.annotations.core.utils.AnnotationUtils;

public class AddAnnotationToPackageTest extends AbstractAnnotationTest {

    @Override
    public String getPackageName() {
        return "com.example";
    }

    @Override
    public String getClassName() {
        return "package-info.java";
    }

    @Override
    public String getClassContents() {
        return "package com.example;\n";
    }

    @Override
    public Annotation getAnnotation() {
        List<MemberValuePair> memberValuePairs = new ArrayList<MemberValuePair>();

        MemberValuePair locationVP = AnnotationsCore.createStringMemberValuePair(ast,
                "location", "uri:someSchema");

        MemberValuePair namespaceVP = AnnotationsCore.createStringMemberValuePair(ast,
                "namespace", "uri:testNS");
        
        memberValuePairs.add(locationVP);
        memberValuePairs.add(namespaceVP);
        
        return AnnotationsCore.createNormalAnnotation(ast, XmlSchema.class.getSimpleName(), memberValuePairs);
    }

    public void testAddAnnotationToPackage() {
        try {
            assertNotNull(annotation);
            assertEquals(XmlSchema.class.getSimpleName(), AnnotationUtils.getAnnotationName(annotation));
            IPackageDeclaration myPackage = source.getPackageDeclaration(getPackageName());
            assertNotNull(myPackage);
            
            textFileChange.addEdit(AnnotationUtils.createAddAnnotationTextEdit(myPackage, annotation));
            textFileChange.addEdit(AnnotationUtils.createAddImportTextEdit(myPackage, XmlSchema.class));
            
            assertTrue(executeChange(new NullProgressMonitor(), textFileChange));

            assertTrue(AnnotationUtils.isAnnotationPresent(myPackage, AnnotationUtils.getAnnotationName(annotation)));
            assertTrue(source.getImport(XmlSchema.class.getCanonicalName()).exists());
        } catch (CoreException ce) {
            fail(ce.getLocalizedMessage());
        }
    }
    
}
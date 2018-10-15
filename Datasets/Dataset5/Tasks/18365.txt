static String getAttributeValue(IConfigurationElement configurationElement, String attributeName) {

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
package org.eclipse.jst.ws.annotations.core;

import java.lang.annotation.Annotation;
import java.lang.annotation.ElementType;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

import org.eclipse.core.runtime.IConfigurationElement;
import org.eclipse.core.runtime.IExtensionPoint;
import org.eclipse.core.runtime.Platform;
import org.eclipse.jdt.core.IAnnotation;
import org.eclipse.jdt.core.IField;
import org.eclipse.jdt.core.IJavaElement;
import org.eclipse.jdt.core.ILocalVariable;
import org.eclipse.jdt.core.IMethod;
import org.eclipse.jdt.core.IPackageDeclaration;
import org.eclipse.jdt.core.IType;
import org.eclipse.jdt.core.JavaModelException;
import org.eclipse.jdt.core.dom.Name;
import org.eclipse.jdt.core.dom.SimpleName;
import org.eclipse.jst.ws.annotations.core.initialization.IAnnotationAttributeInitializer;

/**
 * Manages the annotation categories, definitions, processors and initializers contributed through the
 * <code>org.eclipse.jst.ws.annotations.core.annotationDefinition</code>,
 * <code>org.eclipse.jst.ws.annotations.core.annotationCategory</code>,
 * <code>org.eclipse.jst.ws.annotations.core.annotationInitializer</code> and
 * <code>org.eclipse.jst.ws.annotations.core.annotationProcessor</code> extension points.
 * <p>
 * <strong>Provisional API:</strong> This class/interface is part of an interim API that is still under
 * development and expected to change significantly before reaching stability. It is being made available at
 * this early stage to solicit feedback from pioneering adopters on the understanding that any code that uses
 * this API will almost certainly be broken (repeatedly) as the API evolves.
 * </p>
 */
public final class AnnotationsManager {
    private static final String ANNOTATION_DEFINITION = "annotationDefinition"; //$NON-NLS-1$
    private static final String ANNOTATION_CATEGORY = "annotationCategory"; //$NON-NLS-1$
    private static final String ANNOTATION_INITIALIZER = "annotationInitializer"; //$NON-NLS-1$
    private static final String ANNOTATION_PROCESSOR = "annotationProcessor"; //$NON-NLS-1$
    private static final String ANNOTATION = "annotation"; //$NON-NLS-1$

    private static List<AnnotationDefinition> annotationCache = null;
    private static Map<String, String> annotationCategoryCache = null;
    private static Map<String, IConfigurationElement> annotationInitializerCache = null;
    private static Map<String, List<IConfigurationElement>> annotationProcessorCache = null;
    private static Map<String, List<AnnotationDefinition>> annotationsByCategoryMap = null;
    private static Map<String, AnnotationDefinition> annotationClassNameToDefinitionMap;
    private static Map<String, AnnotationDefinition> annotationSimpleNameToDefinitionMap;
    private static Map<String, AnnotationDefinition> annotationQualifiedNameToDefinitionMap;

    private static final String ATT_ID = "id"; //$NON-NLS-1$
    private static final String ATT_NAME = "name"; //$NON-NLS-1$
    private static final String ATT_CATEGORY = "category"; //$NON-NLS-1$

    //	private static final String ELEM_TARGET_FILTER = "targetFilter"; //$NON-NLS-1$
    //	private static final String ATT_TARGET = "target"; //$NON-NLS-1$

    private AnnotationsManager() {
    }

    /**
     * Returns a list of {@link AnnotationDefinition} constructed from contributions to the
     * <code>org.eclipse.jst.ws.annotations.core.annotationDefinition</code> extension point.
     *
     * @return a list of annotation definitions.
     */
    public static synchronized List<AnnotationDefinition> getAnnotations() {
        if (annotationCache == null) {
            annotationCache = new ArrayList<AnnotationDefinition>();

            IExtensionPoint extensionPoint = Platform.getExtensionRegistry().getExtensionPoint(
                    AnnotationsCorePlugin.PLUGIN_ID, ANNOTATION_DEFINITION);
            if (extensionPoint != null) {
                IConfigurationElement[] elements = extensionPoint.getConfigurationElements();
                for (int i = 0; i < elements.length; i++) {
                    IConfigurationElement element = elements[i];
                    if (element.getName().equals(ANNOTATION)) {
                        AnnotationDefinition annotationDefinition = new AnnotationDefinition(element,
                                getAnnotationCategory(getAttributeValue(element, ATT_CATEGORY)));
                        annotationCache.add(annotationDefinition);
                    }
                }
            }
        }
        return annotationCache;
    }

    /**
     * Returns a list of all the contributed {@link java.lang.annotation.Annotation} that target the given java element type.
     *
     * @param element one of
     * <li>org.eclipse.jdt.core.IPackageDeclaration</li>
     * <li>org.eclipse.jdt.core.IType</li>
     * <li>org.eclipse.jdt.core.IField</li>
     * <li>org.eclipse.jdt.core.IMethod</li>
     * <li>org.eclipse.jdt.core.ILocalVariable</li>
     *
     * @return a list of annotations.
     */
    public static List<Class<? extends Annotation>> getAnnotations(IJavaElement javaElement) {
        List<Class<? extends Annotation>> annotations = new ArrayList<Class<? extends Annotation>>();

        try {
            List<AnnotationDefinition> annotationDefinitions = getAllAnnotationsForElement(javaElement);

            filterAnnotationsList(javaElement, annotationDefinitions);

            for (AnnotationDefinition annotationDefinition : annotationDefinitions) {
                annotations.add(annotationDefinition.getAnnotationClass());
            }
        } catch (JavaModelException jme) {
            AnnotationsCorePlugin.log(jme.getStatus());
        }
        return annotations;
    }

    private static synchronized Map<String, AnnotationDefinition> getAnnotationToClassNameDefinitionMap() {

        if (annotationClassNameToDefinitionMap == null) {
            List<AnnotationDefinition> annotationDefinitions = getAnnotations();

            annotationClassNameToDefinitionMap = new HashMap<String, AnnotationDefinition>();

            for (AnnotationDefinition annotationDefinition : annotationDefinitions) {
                annotationClassNameToDefinitionMap.put(annotationDefinition.getAnnotationClass()
                        .getCanonicalName(), annotationDefinition);
            }
        }
        return annotationClassNameToDefinitionMap;
    }

    private static synchronized Map<String, AnnotationDefinition> getSimpleNameToDefinitionMap() {
        if (annotationSimpleNameToDefinitionMap == null) {
            List<AnnotationDefinition> annotationDefinitions = getAnnotations();

            annotationSimpleNameToDefinitionMap = new HashMap<String, AnnotationDefinition>();

            for (AnnotationDefinition annotationDefinition : annotationDefinitions) {
                annotationSimpleNameToDefinitionMap.put(annotationDefinition.getName(), annotationDefinition);
            }
        }
        return annotationSimpleNameToDefinitionMap;
    }

    private static synchronized Map<String, AnnotationDefinition> getQualifiedNameToDefinitionMap() {
        if (annotationQualifiedNameToDefinitionMap == null) {
            List<AnnotationDefinition> annotationDefinitions = getAnnotations();

            annotationQualifiedNameToDefinitionMap = new HashMap<String, AnnotationDefinition>();

            for (AnnotationDefinition annotationDefinition : annotationDefinitions) {
                annotationQualifiedNameToDefinitionMap.put(annotationDefinition.getAnnotationClassName(),
                        annotationDefinition);
            }
        }
        return annotationQualifiedNameToDefinitionMap;
    }

    /**
     * Returns the {@link AnnotationDefinition} for the given {@link java.lang.annotation.Annotation} class
     * or null if no annotation definition can be found.
     * @param annotationClass the <code>java.lang.annotation.Annotation</code> class.
     * @return the annotation definition for the <code>java.lang.annotation.Annotation</code> class.
     */
    public static AnnotationDefinition getAnnotationDefinitionForClass(Class<? extends Annotation> annotationClass) {
        return getAnnotationToClassNameDefinitionMap().get(annotationClass.getCanonicalName());
    }

    /**
     * Returns the {@link AnnotationDefinition} for the given fully qualified {@link java.lang.annotation.Annotation} class
     * name or null if no annotation definition can be found.
     * @param canonicalName the fully qualified name of the <code>java.lang.annotation.Annotation</code> class.
     * @return the annotation definition for the fully qualified <code>java.lang.annotation.Annotation</code> class name.
     */
    public static AnnotationDefinition getAnnotationDefinitionForClass(String canonicalName) {
        return getAnnotationToClassNameDefinitionMap().get(canonicalName);
    }

    /**
     * Returns the {@link IAnnotationAttributeInitializer} for the given {@link org.eclipse.jdt.core.dom.Name}
     * or null if none can be found.
     * @param name a {@link SimpleName} or {@link QualifiedName} for the annotation to search for.
     * @return an <code>IAnnotationAttributeInitializer</code> for the given name.
     */
    public static IAnnotationAttributeInitializer getAnnotationAttributeInitializerForName(Name name) {
        if (name != null) {
            if (name.isSimpleName() && getSimpleNameToDefinitionMap().containsKey(((SimpleName) name).getIdentifier())) {
                return getSimpleNameToDefinitionMap().get(((SimpleName) name).getIdentifier()).getAnnotationAttributeInitializer();
            } else if (name.isQualifiedName() && getQualifiedNameToDefinitionMap().containsKey(name.getFullyQualifiedName())) {
                return getQualifiedNameToDefinitionMap().get(name.getFullyQualifiedName()).getAnnotationAttributeInitializer();
            }
        }
        return null;
    }

    /**
     * Returns a list of all the {@link AnnotationDefinition} with the given annotation category name.
     * @param categoryName the annotation category name.
     * @return a list of annotation definitions.
     */
    public static synchronized List<AnnotationDefinition> getAnnotationsByCategory(String categoryName) {
        if (annotationsByCategoryMap == null) {
            annotationsByCategoryMap = new HashMap<String, List<AnnotationDefinition>>();
            for (AnnotationDefinition annotationDefinition : getAnnotations()) {

                List<AnnotationDefinition> annotationDefinitionList = annotationsByCategoryMap.get(
                        annotationDefinition.getCategory());

                if (annotationDefinitionList == null) {
                    annotationDefinitionList = new ArrayList<AnnotationDefinition>();
                    annotationDefinitionList.add(annotationDefinition);
                    annotationsByCategoryMap.put(annotationDefinition.getCategory(),
                            annotationDefinitionList);
                    continue;
                }
                annotationDefinitionList.add(annotationDefinition);
            }
        }
        return annotationsByCategoryMap.get(categoryName);
    }

    /**
     * Returns a list of the annotation categories.
     * @return a list of annotation categories.
     */
    public static List<String> getAnnotationCategories() {
        return Arrays.asList(getAnnotationCategoryCache().values().toArray(
                new String[getAnnotationCategoryCache().size()]));
    }

    private static String getAnnotationCategory(String categoryId) {
        return getAnnotationCategoryCache().get(categoryId);
    }

    private static synchronized Map<String, String> getAnnotationCategoryCache() {
        if (annotationCategoryCache != null) {
            return annotationCategoryCache;
        }

        annotationCategoryCache = new HashMap<String, String>();

        IExtensionPoint extensionPoint = Platform.getExtensionRegistry().getExtensionPoint(
                AnnotationsCorePlugin.PLUGIN_ID, ANNOTATION_CATEGORY);
        if (extensionPoint != null) {
            IConfigurationElement[] elements = extensionPoint.getConfigurationElements();
            for (int i = 0; i < elements.length; i++) {
                IConfigurationElement element = elements[i];
                annotationCategoryCache.put(getAttributeValue(element, ATT_ID),
                        getAttributeValue(element, ATT_NAME));
            }
        }
        return annotationCategoryCache;
    }

    protected static synchronized Map<String, IConfigurationElement> getAnnotationInitializerCache() {
        if (annotationInitializerCache != null) {
            return annotationInitializerCache;
        }

        annotationInitializerCache = new HashMap<String, IConfigurationElement>();

        IExtensionPoint extensionPoint = Platform.getExtensionRegistry().getExtensionPoint(
                AnnotationsCorePlugin.PLUGIN_ID, ANNOTATION_INITIALIZER);
        if (extensionPoint != null) {
            IConfigurationElement[] elements = extensionPoint.getConfigurationElements();
            for (int i = 0; i < elements.length; i++) {
                IConfigurationElement element = elements[i];
                annotationInitializerCache.put(getAttributeValue(element, ANNOTATION),
                        element);
            }
        }
        return annotationInitializerCache;
    }

    public static synchronized Map<String, List<IConfigurationElement>> getAnnotationProcessorsCache() {
        if (annotationProcessorCache == null) {
            annotationProcessorCache = new HashMap<String, List<IConfigurationElement>>();

            IExtensionPoint extensionPoint = Platform.getExtensionRegistry().getExtensionPoint(
                    AnnotationsCorePlugin.PLUGIN_ID, ANNOTATION_PROCESSOR);
            if (extensionPoint != null) {
                IConfigurationElement[] elements = extensionPoint.getConfigurationElements();
                for (int i = 0; i < elements.length; i++) {
                    IConfigurationElement element = elements[i];
                    if (element.getName().equalsIgnoreCase("processor")) {
                        String annotationKey = getAttributeValue(element, ANNOTATION);
                        List<IConfigurationElement> configurationElements = annotationProcessorCache.get(
                                annotationKey);
                        if (configurationElements == null) {
                            configurationElements = new ArrayList<IConfigurationElement>();
                            configurationElements.add(element);
                            annotationProcessorCache.put(annotationKey, configurationElements);
                            continue;
                        }
                        configurationElements.add(element);
                    }
                }
            }
        }
        return annotationProcessorCache;
    }

    public static String getAttributeValue(IConfigurationElement configurationElement, String attributeName) {
        String attribute = configurationElement.getAttribute(attributeName);
        if (attribute != null) {
            return attribute;
        }
        return ""; //$NON-NLS-1$
    }

    private static List<AnnotationDefinition> getAllAnnotationsForElement(IJavaElement javaElement)
    throws JavaModelException {

        if (javaElement instanceof IPackageDeclaration) {
            return getAnnotationsForElementType(ElementType.PACKAGE);
        }

        if (javaElement instanceof IType) {
            IType type = (IType) javaElement;
            if (type.isAnnotation()) {
                return getAnnotationsForElementType(ElementType.ANNOTATION_TYPE);
            }
            return getAnnotationsForElementType(ElementType.TYPE);
        }

        if (javaElement instanceof IField) {
            return getAnnotationsForElementType(ElementType.FIELD);
        }

        if (javaElement instanceof IMethod) {
            return getAnnotationsForElementType(ElementType.METHOD);
        }

        if (javaElement instanceof ILocalVariable) {
            return getAnnotationsForElementType(ElementType.PARAMETER);
        }

        if (javaElement instanceof IAnnotation) {
            return getAnnotationsForElementType(ElementType.ANNOTATION_TYPE);
        }

        return Collections.emptyList();
    }

    private static List<AnnotationDefinition> getAnnotationsForElementType(ElementType elementType) {
        List<AnnotationDefinition> annotationDefinitions = new ArrayList<AnnotationDefinition>();

        if (annotationCache == null) {
            getAnnotations();
        }

        for (AnnotationDefinition annotationDefinition : annotationCache) {
            if (annotationDefinition.getTargets().contains(elementType) &&
                    !isDeprecated(annotationDefinition)) {
                annotationDefinitions.add(annotationDefinition);
            }
        }
        return annotationDefinitions;
    }

    private static void filterAnnotationsList(IJavaElement javaElement,
            List<AnnotationDefinition> annotationDefinitions) throws JavaModelException {
        Iterator<AnnotationDefinition> annotationIter = annotationDefinitions.iterator();
        while (annotationIter.hasNext()) {
            AnnotationDefinition annotationDefinition = annotationIter.next();

            if (javaElement instanceof IType) {
                IType type = (IType) javaElement;
                if (isClassRestricted(type, annotationDefinition)
                        || isInterfaceRestricted(type, annotationDefinition)
                        || isEnumRestricted(type, annotationDefinition)) {
                    annotationIter.remove();
                }
            }
            if (javaElement instanceof IMethod) {
                IMethod method = (IMethod) javaElement;
                if (method.isMainMethod()) {
                    annotationIter.remove();
                }
                if (method.isConstructor()
                        && !annotationDefinition.getTargets().contains(ElementType.CONSTRUCTOR)) {
                    annotationIter.remove();
                }

                if (isClassRestricted(method, annotationDefinition)
                        || isInterfaceRestricted(method, annotationDefinition)
                        || isEnumRestricted(method, annotationDefinition)) {
                    annotationIter.remove();
                }
            }

            if (javaElement instanceof IField) {
                if(isClassRestricted(javaElement, annotationDefinition)
                        || isInterfaceRestricted(javaElement, annotationDefinition)
                        ||isEnumRestricted(javaElement, annotationDefinition)) {
                    annotationIter.remove();
                }
            }
        }
    }

    private static boolean isClassRestricted(IJavaElement javaElement,
            AnnotationDefinition annotationDefinition) throws JavaModelException {
        if (javaElement.getElementType() == IJavaElement.TYPE) {
            return !((IType)javaElement).isClass() && annotationDefinition.isClassOnly();
        }
        if (javaElement.getElementType() == IJavaElement.METHOD) {
            IType type = (IType)javaElement.getParent();
            return !type.isClass() && annotationDefinition.isClassOnly();
        }
        if (javaElement.getElementType() == IJavaElement.FIELD) {
            IType type = (IType)javaElement.getParent();
            return !type.isClass() && annotationDefinition.isClassOnly();
        }
        return false;
    }

    private static boolean isInterfaceRestricted(IJavaElement javaElement,
            AnnotationDefinition annotationDefinition) throws JavaModelException {
        if (javaElement.getElementType() == IJavaElement.TYPE) {
            return !((IType)javaElement).isInterface() && annotationDefinition.isInterfaceOnly();
        }
        if (javaElement.getElementType() == IJavaElement.METHOD) {
            IType type = (IType)javaElement.getParent();
            return !type.isInterface()  && annotationDefinition.isInterfaceOnly();
        }
        if (javaElement.getElementType() == IJavaElement.FIELD) {
            IType type = (IType)javaElement.getParent();
            return !type.isInterface() && annotationDefinition.isInterfaceOnly();
        }
        return false;
    }

    private static boolean isEnumRestricted(IJavaElement javaElement,
            AnnotationDefinition annotationDefinition) throws JavaModelException {
        if (javaElement.getElementType() == IJavaElement.TYPE) {
            return !((IType)javaElement).isEnum() && annotationDefinition.isEnumOnly();
        }
        if (javaElement.getElementType() == IJavaElement.METHOD) {
            IType type = (IType)javaElement.getParent();
            return !type.isEnum() && annotationDefinition.isEnumOnly();
        }
        if (javaElement.getElementType() == IJavaElement.FIELD) {
            IType type = (IType)javaElement.getParent();
            return !type.isEnum() && annotationDefinition.isEnumOnly();
        }
        return false;
    }

    //TODO Move the Deprecated option to preferences
    private static boolean isDeprecated(AnnotationDefinition annotationDefinition) {
        Class<?> annotationClass = annotationDefinition.getAnnotationClass();
        return annotationClass.getAnnotation(java.lang.Deprecated.class) != null;
    }
}
private AnnotationProcessor getAnnotationProcessor(IConfigurationElement configurationElement,

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
package org.eclipse.jst.ws.internal.annotations.core.processor;

import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.IConfigurationElement;
import org.eclipse.jst.ws.annotations.core.AnnotationsCorePlugin;
import org.eclipse.jst.ws.annotations.core.AnnotationsManager;
import org.eclipse.jst.ws.annotations.core.processor.AbstractAnnotationProcessor;

import com.sun.mirror.apt.AnnotationProcessor;
import com.sun.mirror.apt.AnnotationProcessorEnvironment;
import com.sun.mirror.apt.AnnotationProcessorFactory;
import com.sun.mirror.apt.AnnotationProcessors;
import com.sun.mirror.declaration.AnnotationTypeDeclaration;

public class AnnotationsCoreProcessorFactory implements AnnotationProcessorFactory {

    public AnnotationProcessor getProcessorFor(Set<AnnotationTypeDeclaration> annotationSet,
            AnnotationProcessorEnvironment processorEnvironment) {

    	if (annotationSet.size() == 0) {
    		return AnnotationProcessors.NO_OP;
    	}
        List<AnnotationProcessor> annotationProcessors = new ArrayList<AnnotationProcessor>();

        Map<String, List<IConfigurationElement>> annotationProcessorCache =
            AnnotationsManager.getAnnotationProcessorsCache();

        for (AnnotationTypeDeclaration annotationTypeDeclaration : annotationSet) {
            List<IConfigurationElement> processorElements = annotationProcessorCache.get(
                    annotationTypeDeclaration.getQualifiedName());

            for (IConfigurationElement configurationElement : processorElements) {
                if (configurationElement != null) {
                    AnnotationProcessor processor = getAnnotationProcessor(configurationElement,
                            processorEnvironment);
                    if (processor != null) {
                        annotationProcessors.add(processor);
                    }
                }
            }
        }

        return AnnotationProcessors.getCompositeAnnotationProcessor(annotationProcessors);
    }

    public AnnotationProcessor getAnnotationProcessor(IConfigurationElement configurationElement,
            AnnotationProcessorEnvironment processorEnvironment) {
          try {
              AbstractAnnotationProcessor annotationProcessor =
                  (AbstractAnnotationProcessor)configurationElement.createExecutableExtension("class");
              annotationProcessor.setAnnotationProcessorEnvironment(processorEnvironment);
              return annotationProcessor;
          } catch (CoreException ce) {
              AnnotationsCorePlugin.log(ce.getStatus());
          }
          return null;
      }

    public Collection<String> supportedAnnotationTypes() {
        return AnnotationsManager.getAnnotationProcessorsCache().keySet();
    }

    public Collection<String> supportedOptions() {
        return Collections.emptyList();
    }

}
package org.eclipse.xpand3.analyzation;

/**
 * <copyright> 
 *
 * Copyright (c) 2002-2007 itemis AG and others.
 * All rights reserved.   This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: 
 *   itemis AG - Initial API and implementation
 *
 * </copyright>
 *
 */
package org.eclipse.xand3.analyzation;


/**
 * @author Sven Efftinge
 *
 */
public interface LanguageSpecificDeclarationContributorFactory {
	/**
     * gives the middle end a way to declare if it can and wants to handle a given
     *  source file / resource. If and only if it returns true, it will be asked for
     *  the functions and advice provided in this resource.
     */
    boolean canHandle (String resourceName);
    
    /**
     * 
     * @param resourceName
     * @return
     */
    DeclarationsContributor createDeclarationContributor(String resourceName);
}	
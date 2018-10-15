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

import java.util.HashSet;
import java.util.Set;



/**
 * @author Sven Efftinge
 *
 */
public class TypeSystemFactory {
	
	private final static Set<LanguageSpecificDeclarationContributorFactory> factories = new HashSet<LanguageSpecificDeclarationContributorFactory>();
	
	public static void registerLanguageSpecificFactory(LanguageSpecificDeclarationContributorFactory factory) {
		factories.add(factory);
	}
	
	public static DeclarationsContributor createDeclarationContributor(String namespace) {
		for (LanguageSpecificDeclarationContributorFactory factory : factories) {
			if (factory.canHandle(namespace)) {
				return factory.createDeclarationContributor(namespace);
			}
		}
		return null;
	}
	
	
}
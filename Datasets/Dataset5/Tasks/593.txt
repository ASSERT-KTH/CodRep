import org.eclipse.xtend.typesystem.emf.XtendTypesytemEmfPlugin;

/*******************************************************************************
 * <copyright>
 * Copyright (c) 2008 itemis AG and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 * committers of openArchitectureWare - initial API and implementation
 * </copyright>
 *******************************************************************************/

package org.eclipse.xtend.typesystem.emf.check;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.eclipse.core.runtime.IConfigurationElement;
import org.eclipse.core.runtime.IExtensionPoint;
import org.eclipse.core.runtime.IExtensionRegistry;
import org.eclipse.core.runtime.Platform;
import org.eclipse.emf.ecore.EPackage;
import org.eclipse.emf.ecore.EValidator;
import org.eclipse.xtend.typesystem.internal.emf.XtendTypesytemEmfPlugin;

/**
 * Reads checks extensions, instantiates validators and registers them.
 * 
 * @author Jan Köhnlein
 */
public class CheckRegistry {

	private final Log log = LogFactory.getLog(getClass());

	private static final String EXTENSION_POINT_ID = XtendTypesytemEmfPlugin.PLUGIN_ID + ".checks";
	private static final String NS_URI_ATTR_ID = "nsURI";
	private static final String CHECK_FILE_ATTR_ID = "checkFile";
	private static final String CHECK_FILE_PATH_ATTR_ID = "path";
	private static final String OVERRIDE_ATTR_ID = "override";
	private static final String REFERENCED_META_MODEL = "referencedMetaModel";

	private static CheckRegistry INSTANCE;

	private CheckRegistry() {
		registerExtensions();
	}

	public static CheckRegistry getInstance() {
		if (INSTANCE == null) {
			INSTANCE = new CheckRegistry();
		}
		return INSTANCE;
	}

	private void registerExtensions() {
		try {
			IExtensionRegistry extensionRegistry = Platform.getExtensionRegistry();
			IExtensionPoint extensionPoint = extensionRegistry.getExtensionPoint(EXTENSION_POINT_ID);
			IConfigurationElement[] metaModels = extensionPoint.getConfigurationElements();
			for (IConfigurationElement metaModel : metaModels) {
				try {
					String nsURI = metaModel.getAttribute(NS_URI_ATTR_ID);
					EPackage ePackage = findEPackage(nsURI);
					String override = metaModel.getAttribute(OVERRIDE_ATTR_ID);
					CheckEValidatorAdapter oawValidator;
					if ("true".equals(override)) {
						oawValidator = new CheckEValidatorAdapter(ePackage);
					}
					else {
						EValidator validator = EValidator.Registry.INSTANCE.getEValidator(ePackage);
						if (validator instanceof CheckEValidatorAdapter)
							oawValidator = (CheckEValidatorAdapter) validator;
						else
							oawValidator = new CheckEValidatorAdapter(ePackage, validator);
					}
					IConfigurationElement[] checkFiles = metaModel.getChildren(CHECK_FILE_ATTR_ID);
					for (IConfigurationElement checkFile : checkFiles) {
						try {
							String checkFileName = checkFile.getAttribute(CHECK_FILE_PATH_ATTR_ID);
							CheckFileWithContext registeredCheckFile = new CheckFileWithContext(checkFileName);
							for (IConfigurationElement referencedMetaModel : checkFile
									.getChildren(REFERENCED_META_MODEL)) {
								String refNsURI = referencedMetaModel.getAttribute(NS_URI_ATTR_ID);
								registeredCheckFile.addImportedEPackageNsUri(refNsURI);
							}
							oawValidator.addCheckFile(registeredCheckFile);
						}
						catch (Exception exc) {
							log.error(exc);
						}
					}
					EValidator.Registry.INSTANCE.put(ePackage, oawValidator);
				}
				catch (Exception exc) {
					log.error(exc);
				}
			}
		}
		catch (Exception exc) {
			log.error(exc);
		}
	}

	private EPackage findEPackage(String nsURI) {
		Object registeredEPackageDescriptor = EPackage.Registry.INSTANCE.get(nsURI);
		if (registeredEPackageDescriptor instanceof EPackage) {
			return (EPackage) registeredEPackageDescriptor;
		}
		else if (registeredEPackageDescriptor instanceof EPackage.Descriptor) {
			return ((EPackage.Descriptor) registeredEPackageDescriptor).getEPackage();
		}
		throw new IllegalArgumentException("Wrong type in Ecore.Registry");
	}
}
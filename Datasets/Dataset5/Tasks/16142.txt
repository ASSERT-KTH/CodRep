log.error("Use the XmlBeautifier from XSD Feature: org.eclipse.xtend.typesystem.xsd.XMLBeautifier instead.");

/*******************************************************************************
 * Copyright (c) 2005, 2009 committers of openArchitectureWare and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     committers of openArchitectureWare - initial API and implementation
 *******************************************************************************/

package org.eclipse.xpand2.output;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;

/**
 * *
 * 
 * @author Sven Efftinge (http://www.efftinge.de)
 * @author Bernd Kolb
 * @deprecated Use the XmlBeautifier from XSD Feature instead. 
 * @see org.eclipse.xtend.typesystem.xsd.XmlBeautifier
 */
@Deprecated
public class XmlBeautifier implements PostProcessor {

	private final Log log = LogFactory.getLog(getClass());

	public void beforeWriteAndClose(final FileHandle info) {
		log.error("Use the XmlBeautifier from XSD Feature: org.eclipse.xtend.typesystem.xsd.XmlBeautifier instead.");
	}

	public void afterClose(final FileHandle impl) {
	}

}
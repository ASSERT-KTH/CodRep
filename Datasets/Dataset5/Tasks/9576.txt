throw new IOException("Error creating endpoint description: " //$NON-NLS-1$

/*******************************************************************************
 * Copyright (c) 2010-2011 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *   Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.osgi.services.remoteserviceadmin;

import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import org.eclipse.ecf.internal.osgi.services.remoteserviceadmin.DebugOptions;
import org.eclipse.ecf.internal.osgi.services.remoteserviceadmin.EndpointDescriptionParser;
import org.eclipse.ecf.internal.osgi.services.remoteserviceadmin.LogUtility;

/**
 * Default implementation of {@link IEndpointDescriptionReader}.
 * 
 */
public class EndpointDescriptionReader implements IEndpointDescriptionReader {

	public org.osgi.service.remoteserviceadmin.EndpointDescription[] readEndpointDescriptions(
			InputStream input) throws IOException {
		// First create parser
		EndpointDescriptionParser parser = new EndpointDescriptionParser();
		// Parse input stream
		parser.parse(input);
		// Get possible endpoint descriptions
		List<EndpointDescriptionParser.EndpointDescription> parsedDescriptions = parser
				.getEndpointDescriptions();
		List<org.osgi.service.remoteserviceadmin.EndpointDescription> results = new ArrayList<org.osgi.service.remoteserviceadmin.EndpointDescription>();
		// For each one parsed, get properties and
		for (EndpointDescriptionParser.EndpointDescription ed : parsedDescriptions) {
			Map parsedProperties = ed.getProperties();
			try {
				results.add(new EndpointDescription(parsedProperties));
			} catch (Exception e) {
				LogUtility.logError(
						"readEndpointDescriptions", //$NON-NLS-1$
						DebugOptions.ENDPOINT_DESCRIPTION_READER,
						this.getClass(),
						"Exception parsing endpoint description properties", e); //$NON-NLS-1$
				throw new IOException("Error creating endpoint description: "
						+ e.getMessage());
			}
		}
		return results.toArray(new EndpointDescription[results.size()]);
	}

}
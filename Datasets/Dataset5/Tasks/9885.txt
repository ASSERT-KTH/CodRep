}

/*******************************************************************************
 * Copyright (c) 2005, 2007 committers of openArchitectureWare and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     committers of openArchitectureWare - initial API and implementation
 *******************************************************************************/
package org.eclipse.xtend.typesystem.uml2.profile;

import java.io.File;
import java.io.IOException;
import java.util.List;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.eclipse.emf.common.util.URI;
import org.eclipse.emf.ecore.resource.Resource;
import org.eclipse.emf.ecore.resource.impl.ResourceSetImpl;
import org.eclipse.emf.ecore.xml.type.AnyType;
import org.eclipse.emf.mwe.core.ConfigurationException;
import org.eclipse.emf.mwe.core.issues.Issues;
import org.eclipse.emf.mwe.core.issues.IssuesImpl;
import org.eclipse.uml2.uml.Element;
import org.eclipse.uml2.uml.Model;
import org.eclipse.uml2.uml.NamedElement;
import org.eclipse.uml2.uml.Profile;
import org.eclipse.uml2.uml.Stereotype;
import org.eclipse.uml2.uml.UMLPackage;
import org.eclipse.xtend.typesystem.uml2.Setup;

/**
 * Extensions for support of UML2 Profiles.
 * 
 * @author Karsten Thoms
 * @since 4.2
 */
public class ProfilingExtensions {
	private static final Log LOG = LogFactory.getLog(ProfilingExtensions.class);
	
	/**
	 * We utilize the XmiReader to load profiles. To use the XmiReader class within this class
	 * we need to override a method. 
	 */
	@SuppressWarnings("deprecation")
	private static class XmiReader extends org.eclipse.xtend.typesystem.emf.XmiReader {
		
		public XmiReader() {
			super();
			setMetaModelPackage(UMLPackage.class.getName());
		}

		public Element load (String file) {
			setModelFile(file);
			Issues issues = new IssuesImpl();
	        final File f = loadFile(issues);
	        if (issues.hasErrors()) {
	        	throw new RuntimeException(issues.toString());
	        }
	        final URI fileURI = URI.createFileURI(f.getAbsolutePath());

	        final Resource r = new ResourceSetImpl().createResource(fileURI);
	        try {
	            r.load(null);
	        } catch (final IOException e) {
	            throw new ConfigurationException(e);
	        }
	        if (AnyType.class.isAssignableFrom(r.getContents().get(0).getClass())) {
	        	throw new ConfigurationException("Profile not loaded correctly. Root element is of type AnyType - could not be instantiated as Profile.");
	        }
	        return (Element) r.getContents().get(0);
		}
	};
	
	/**
	 * Applies a profile to a Model.
	 * @param model The Model instance.
	 * @param uri Resource Path to the .profile.uml/.profile.uml2 file.  
	 * @return The loaded Profile
	 */
	public static Profile applyProfile (Model model, String uri) {
		new Setup().setStandardUML2Setup(true);//setup pathmap
		if (!uri.endsWith(".profile.uml2") && !uri.endsWith(".profile.uml")) {
			uri += ".profile.uml";
		}
		Profile profile = (Profile) new XmiReader().load(uri);
		if (profile==null) {
			throw new NullPointerException("Profile '"+uri+"' not loaded.");
		}
		model.applyProfile(profile);
		return profile;
	}
	
	/**
	 * Applies a stereotype by name to an Element. 
	 * @param elem The element the stereotype should be applied on
	 * @param stereotypeName The qualified stereotype name. <code>[ProfileName]::[StereotypeName]
	 */
	public static void applyStereotype(Element elem, String stereotypeName) {
		Stereotype st = elem.getApplicableStereotype(stereotypeName);
		if (st!=null && !elem.isStereotypeApplied(st)) {
			elem.applyStereotype(st);
		}
		if (LOG.isDebugEnabled() && (elem.getAppliedStereotype(stereotypeName)!=null))
			LOG.debug("Stereotype '"+stereotypeName+"' applied for '"+elem);
	}
	
	/**
	 * Sets a <i>single-valued</i> tagged value for an element. Auto-applies the stereotype if not already done.
	 * @param elem The element a tagged value should be set for.
	 * @param stereotypeName The qualified stereotype name. <code>[ProfileName]::[StereotypeName]
	 * @param taggedValueName Name of the tagged value.
	 * @param value The value to set.
	 */
	public static void setTaggedValue (Element elem, String stereotypeName, String taggedValueName, Object value) {
		Stereotype st = elem.getApplicableStereotype(stereotypeName);
		if (st!=null) {
			if (!elem.isStereotypeApplied(st)) elem.applyStereotype(st);
			try {
				if (value==null) {
					LOG.warn(taggedValueName+": Tried to set null value for element "+(elem instanceof NamedElement ? ((NamedElement)elem).getName() : elem));
				} else {
					elem.setValue(st, taggedValueName, value);
				}
			} catch (IllegalArgumentException e) {
				LOG.error(taggedValueName+": "+e.getMessage());
			}
		}
	}
	
	/**
	 * Sets a <i>multi-valued</i> tagged value for an element. Auto-applies the stereotype if not already done.
	 * @param elem The element a tagged value should be set for.
	 * @param stereotypeName The qualified stereotype name. <code>[ProfileName]::[StereotypeName]
	 * @param taggedValueName Name of the tagged value.
	 * @param value The value to set.
	 */
	@SuppressWarnings("unchecked")
	public static void addTaggedValue (Element elem, String stereotypeName, String taggedValueName, Object value) {
		Stereotype st = elem.getApplicableStereotype(stereotypeName);
		if (st!=null) {
			if (!elem.isStereotypeApplied(st)) elem.applyStereotype(st);
			try {
				if (value==null) {
					LOG.warn(taggedValueName+": Tried to set null value for element "+(elem instanceof NamedElement ? ((NamedElement)elem).getName() : elem));
				} else {
					List<Object> list = (List<Object>) elem.getValue(st, taggedValueName);
					list.add(value);
				}
			} catch (IllegalArgumentException e) {
				LOG.error(taggedValueName+": "+e.getMessage());
			}
		}
	}

}
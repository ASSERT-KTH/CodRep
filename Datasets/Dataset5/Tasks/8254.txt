if (r instanceof OawXSDResource) {

/*******************************************************************************
 * Copyright (c) 2005 - 2009 itemis AG (http://www.itemis.eu) and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 *******************************************************************************/

package org.eclipse.xtend.typesystem.xsd.builder;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.apache.commons.logging.Log;
import org.eclipse.emf.common.util.URI;
import org.eclipse.emf.ecore.EPackage;
import org.eclipse.emf.ecore.resource.Resource;
import org.eclipse.emf.ecore.resource.impl.ResourceSetImpl;
import org.eclipse.emf.ecore.util.BasicExtendedMetaData;
import org.eclipse.emf.ecore.util.ExtendedMetaData;
import org.eclipse.emf.ecore.xmi.XMLResource;
import org.eclipse.emf.ecore.xmi.impl.EcoreResourceFactoryImpl;
import org.eclipse.emf.mwe.core.monitor.ProgressMonitor;
import org.eclipse.xsd.XSDSchema;
import org.eclipse.xsd.util.XSDResourceImpl;
import org.eclipse.xtend.typesystem.xsd.builder.OawXSDResource.OawXSDResourceFactory;
import org.eclipse.xtend.typesystem.xsd.util.Msg;
import org.eclipse.xtend.typesystem.xsd.util.XSDLog;

/**
 * @author Moritz Eysholdt - Initial contribution and API
 */
public class OawXSDResourceSet extends ResourceSetImpl implements XSDManager {

	private static int counter = 0;

	protected ExtendedMetaData extendedMetadata;

	private int id = counter++;

	protected Log log = XSDLog.getLog(getClass());

	public OawXSDResourceSet() {
		super();

		// log.info("created new " + getClass().getSimpleName() + " -> " + id);

		extendedMetadata = new BasicExtendedMetaData(getPackageRegistry());

		getAdapterFactories().add(new XSDResolverFactory());

		getLoadOptions().put(XSDResourceImpl.XSD_TRACK_LOCATION, Boolean.TRUE);
		getLoadOptions().put(XMLResource.OPTION_EXTENDED_META_DATA,
				extendedMetadata);
		Map<String, Object> extMap = getResourceFactoryRegistry()
				.getExtensionToFactoryMap();
		extMap.put("wsdl", new OawXSDResourceFactory());
		extMap.put("xsd", new OawXSDResourceFactory());
		extMap.put("ecore", new EcoreResourceFactoryImpl());
	}

	public void clear() {
		for (Resource r : getResources())
			if (r.isLoaded())
				r.unload();
		getResources().clear();
	}

	public OawXSDResource createXsdResource(URI uri) {
		return (OawXSDResource) super.createResource(uri);
	}

	public int getID() {
		return id;
	}

	public List<EPackage> getPackages() {
		ArrayList<EPackage> l = new ArrayList<EPackage>();
		for (Resource r : getResources())
			if (r instanceof Resource) {
				OawXSDResource x = (OawXSDResource) r;
				if (x.isEcorePackageGenerated())
					l.add(x.getEPackage());
			}
		return l;
	}

	public Set<EPackage> getPackages(Collection<URI> uris) {
		HashSet<EPackage> s = new HashSet<EPackage>();
		HashSet<OawXSDResource> o = new HashSet<OawXSDResource>();
		for (URI u : uris) {
			Resource r = getResource(u, false);
			if (r instanceof OawXSDResource)
				((OawXSDResource) r).collectPackages(s, o);
		}
		return s;
	}

	public List<XSDSchema> getSchemas() {
		ArrayList<XSDSchema> a = new ArrayList<XSDSchema>();
		for (Resource r : getResources())
			if (r instanceof OawXSDResource) {
				OawXSDResource xr = (OawXSDResource) r;
				if (xr.getSchema() != null)
					a.add(xr.getSchema());
			}
		return a;
	}

	public OawXSDResource getXsdResource(URI uri, boolean loadOnDemand) {
		return (OawXSDResource) super.getResource(uri, loadOnDemand);
	}

	public boolean hasErrors() {
		for (Resource r : getResources())
			if (!r.getErrors().isEmpty())
				return true;
		return false;
	}

	public boolean isEmpty() {
		return getPackages().isEmpty();
	}

	public void loadAndGenerate(URI uri) {
		OawXSDResource res = getXsdResource(uri, true);
		res.generateECore();
	}

	public void markDirty(URI uri) {
		Resource r = getResource(uri, false);
		if (r == null)
			r = createResource(uri);
		OawXSDResource xr = (OawXSDResource) r;
		log.info(Msg.create("Marking dirty: ").uri(uri));
		xr.markFileDirty();
		xr.setGeneratePackage(true);
	}

	public void registerPackage(EPackage pkg) {
		getPackageRegistry().put(pkg.getNsURI(), pkg);
	}

	public void reloadDirty(ProgressMonitor pm) {
		log.info("Reloading all dirty");
		reloadSchemasWithDirtyFiles(pm);
		reloadEPackagesWithDirtySchemas(pm);
	}

	private void reloadEPackagesWithDirtySchemas(ProgressMonitor pm) {
		ArrayList<OawXSDResource> l = new ArrayList<OawXSDResource>();
		for (Resource r : getResources())
			if (r instanceof OawXSDResource) {
				OawXSDResource xr = (OawXSDResource) r;
				if (xr.isSchemaDirty())
					l.add(xr);
			}

		for (OawXSDResource r : l)
			if (r.isEcorePackageGenerated() && !pm.isCanceled())
				r.unloadPackage();

		for (OawXSDResource r : l)
			if (r.isGeneratePackage() && r.isSchemaDirty() && !pm.isCanceled()) {
				pm.subTask("generating EPackage for "
						+ r.getURI().lastSegment());
				r.generateECore();
				pm.worked(2);
			}
		pm.done();
	}

	private void reloadSchemasWithDirtyFiles(ProgressMonitor pm) {
		ArrayList<OawXSDResource> l = new ArrayList<OawXSDResource>();
		for (Resource r : getResources())
			if (r instanceof OawXSDResource) {
				OawXSDResource xr = (OawXSDResource) r;
				if (xr.isFileDirty() || !xr.isLoaded())
					l.add(xr);
			}
		pm.beginTask("XSD Adapter", (l.size() * 3) + 1);

		pm.subTask("unloading changed resources");
		for (OawXSDResource r : l)
			if (r.isLoaded() && !pm.isCanceled())
				r.unload();
		pm.worked(1);

		for (OawXSDResource r : l)
			try {
				if (!r.isLoaded() && !pm.isCanceled()) {
					log.info(Msg.create("Reloading ").uri(r.getURI()));
					pm.subTask("loading " + r.getURI().lastSegment());
					r.load(new HashMap<Object, Object>());
					pm.worked(1);
				}
			} catch (IOException e) {
				log.error(e);
			}
	}

	public void remove(URI uri) {
		OawXSDResource r = getXsdResource(uri, false);
		if (r == null)
			return;
		r.markFileDirty();
		log.info(Msg.create("Removing ").uri(uri).txt(" from ").scls(this));
		r.unload();
		getResources().remove(r);
	}

	@Override
	public String toString() {
		ArrayList<String> i = new ArrayList<String>();
		for (EPackage pkg : getPackages()) {
			if (pkg != null)
				i.add(pkg.getName());
			else
				i.add("(null!)");
		}
		return getClass().getSimpleName() + id + i.toString();
	}

	public void unregisterPackage(EPackage pkg) {
		getPackageRegistry().remove(pkg.getNsURI());
	}

}
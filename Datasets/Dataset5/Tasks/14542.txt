return this.getProject().getLocation().toFile().toURI().toURL();

/*******************************************************************************
 * Copyright (c) 2004, 2008 John Krasnay and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors:
 *     John Krasnay - initial API and implementation
 *     Igor Jacy Lino Campista - Java 5 warnings fixed (bug 311325)
 *******************************************************************************/
package org.eclipse.wst.xml.vex.ui.internal.config;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.net.MalformedURLException;
import java.net.URL;
import java.text.MessageFormat;
import java.util.ArrayList;
import java.util.List;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.FactoryConfigurationError;
import javax.xml.parsers.ParserConfigurationException;

import org.eclipse.core.resources.IFile;
import org.eclipse.core.resources.IProject;
import org.eclipse.core.resources.IncrementalProjectBuilder;
import org.eclipse.core.resources.ResourcesPlugin;
import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.wst.xml.vex.core.internal.dom.DocumentWriter;
import org.eclipse.wst.xml.vex.ui.internal.VexPlugin;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xml.sax.SAXException;

/**
 * Represents a Vex plugin project.
 */
public class PluginProject extends ConfigSource {

	public static final String PLUGIN_XML = "vex-plugin.xml"; //$NON-NLS-1$
	public static final String PROJECT_CONFIG_SER = ".vexConfig.ser"; //$NON-NLS-1$

	/**
	 * Class constructor.
	 * 
	 * @param config
	 *            VexConfiguration associated with this project.
	 */
	protected PluginProject(IProject project) {
		this.projectPath = project.getFullPath().toString();
	}

	/**
	 * Remove the .vexConfig.ser state in which the project state is stored.
	 */
	public void cleanState() throws CoreException {
		IFile configSer = this.getProject().getFile(PROJECT_CONFIG_SER);
		configSer.delete(true, null);
	}

	/**
	 * Factory method that returns the plugin project for the given IProject. If
	 * the given project does not have the Vex plugin project nature, null is
	 * returned. PluginProject instances are cached so they can be efficiently
	 * returned.
	 * 
	 * @param project
	 *            IProject for which to return the PluginProject.
	 * @return
	 * @throws CoreException
	 */
	public static PluginProject get(IProject project) {
		for (ConfigSource source : ConfigRegistry.getInstance().getAllConfigSources()) {
			if (source instanceof PluginProject) {
				PluginProject pluginProject=(PluginProject)source;
				if (project.equals(pluginProject.getProject())) {
					return pluginProject;
				}
			}	
		}
		return null;
	}

	public URL getBaseUrl() {
		try {
			return this.getProject().getLocation().toFile().toURL();
		} catch (MalformedURLException e) {
			throw new RuntimeException(Messages
					.getString("PluginProject.malformedUrl"), e); //$NON-NLS-1$
		}
	}

	/**
	 * Returns the IProject associated with this plugin project.
	 */
	public IProject getProject() {
		return ResourcesPlugin.getWorkspace().getRoot().getProject(
				this.projectPath);
	}

	/**
	 * Loads the project from it's serialized state file and registers it with
	 * the ConfigRegistry. If the serialized state cannot be loaded, a new
	 * PluginProject is created and the builder is launched.
	 */
	public static PluginProject load(IProject project) {

		try {
			if (!project.isOpen() || !project.hasNature(PluginProjectNature.ID)) {
				String message = MessageFormat.format(Messages
						.getString("PluginProject.notPluginProject"), //$NON-NLS-1$
						new Object[] { project.getName() });
				throw new IllegalArgumentException(message);
			}
		} catch (CoreException e) {
			String message = MessageFormat.format(Messages
					.getString("PluginProject.notPluginProject"), //$NON-NLS-1$
					new Object[] { project.getName() });
			throw new IllegalArgumentException(message);
		}

		IFile serFile = project.getFile(PROJECT_CONFIG_SER);

		PluginProject pluginProject = null;
		if (serFile.exists()) {
			try {
				ObjectInputStream ois = new ObjectInputStream(serFile
						.getContents());
				pluginProject = (PluginProject) ois.readObject();
			} catch (Exception ex) {
				String message = MessageFormat.format(Messages
						.getString("PluginProject.loadingError"), //$NON-NLS-1$
						new Object[] { serFile });
				VexPlugin.getInstance().log(IStatus.WARNING, message, ex);
			}
		}

		boolean rebuild = false;

		if (pluginProject == null) {
			rebuild = true;
			pluginProject = new PluginProject(project);
		}

		ConfigRegistry registry = ConfigRegistry.getInstance();
		registry.addConfigSource(pluginProject);
		registry.fireConfigChanged(new ConfigEvent(PluginProject.class));

		if (rebuild) {
			try {
				project.build(IncrementalProjectBuilder.FULL_BUILD, null);

			} catch (Exception ex) {
				String message = MessageFormat.format(Messages
						.getString("PluginProject.buildError"), //$NON-NLS-1$
						new Object[] { project.getName() });
				VexPlugin.getInstance().log(IStatus.ERROR, message, ex);
			}
		}

		return pluginProject;
	}

	/**
	 * Re-parses the vex-plugin.xml file.
	 */
	public void parseConfigXml() throws SAXException, IOException {

		DocumentBuilder builder;
		try {
			builder = DocumentBuilderFactory.newInstance().newDocumentBuilder();
		} catch (ParserConfigurationException e) {
			throw new RuntimeException(e);
		} catch (FactoryConfigurationError e) {
			throw new RuntimeException(e);
		}

		this.removeAllItems();

		URL url = new URL(this.getBaseUrl(), PluginProject.PLUGIN_XML);
		Document doc = builder.parse(url.toString());

		Element root = doc.getDocumentElement();

		this.setUniqueIdentifer(root.getAttribute("id")); //$NON-NLS-1$

		NodeList nodeList = doc.getElementsByTagName("extension"); //$NON-NLS-1$

		for (int i = 0; i < nodeList.getLength(); i++) {
			Element element = (Element) nodeList.item(i);
			String extPoint = element.getAttribute("point"); //$NON-NLS-1$
			String id = element.getAttribute("id"); //$NON-NLS-1$
			String name = element.getAttribute("name"); //$NON-NLS-1$

			List<Node> configElementList = new ArrayList<Node>();
			NodeList childList = element.getChildNodes();
			for (int j = 0; j < childList.getLength(); j++) {
				Node child = childList.item(j);
				if (child instanceof Element) {
					configElementList.add(child);
				}
			}

			IConfigElement[] configElements = new IConfigElement[configElementList
					.size()];
			for (int j = 0; j < configElementList.size(); j++) {
				configElements[j] = new DomConfigurationElement(
						(Element) configElementList.get(j));
			}

			this.addItem(extPoint, id, name, configElements);
		}

	}

	/**
	 * Saves the state of this project into .vexConfig.ser.
	 */
	public void saveState() throws CoreException, IOException {
		ByteArrayOutputStream baos = new ByteArrayOutputStream();
		ObjectOutputStream oos = new ObjectOutputStream(baos);
		oos.writeObject(this);
		ByteArrayInputStream bais = new ByteArrayInputStream(baos.toByteArray());
		IFile configSer = this.getProject().getFile(PROJECT_CONFIG_SER);
		if (configSer.exists()) {
			configSer.setContents(bais, true, false, null);
		} else {
			configSer.create(bais, true, null);
			configSer.setDerived(true);
		}

	}

	/**
	 * Writes this configuraton to the file vex-config.xml in the project.
	 */
	public void writeConfigXml() throws CoreException, IOException {
		ByteArrayOutputStream baos = new ByteArrayOutputStream();
		PrintWriter out = new PrintWriter(new OutputStreamWriter(baos, "utf-8")); //$NON-NLS-1$

		ConfigurationElement root = new ConfigurationElement("plugin"); //$NON-NLS-1$
		for (ConfigItem item : this.getAllItems()) {
			ConfigurationElement extElement = new ConfigurationElement(
			"extension"); //$NON-NLS-1$
			extElement.setAttribute("id", item.getSimpleId()); //$NON-NLS-1$
			extElement.setAttribute("name", item.getName()); //$NON-NLS-1$
			extElement.setAttribute("point", item.getExtensionPointId()); //$NON-NLS-1$
			IConfigItemFactory factory = ConfigRegistry.getInstance()
				.getConfigItemFactory(item.getExtensionPointId());
			extElement.setChildren(factory.createConfigurationElements(item));
			root.addChild(extElement);	
		}
		writeElement(root, out, 0);

		out.close();

		InputStream inputStream = new ByteArrayInputStream(baos.toByteArray());

		IFile file = this.getProject().getFile(PLUGIN_XML);
		if (file.exists()) {
			file.setContents(inputStream, true, false, null);
		} else {
			file.create(inputStream, true, null);
		}
	}

	// =========================================================== PRIVATE

	private String projectPath;
	/** Filename used when serializing in a Vex plugin project */
	public static final String SER_FILE = ".vexConfig.ser"; //$NON-NLS-1$

	private static void writeElement(IConfigElement element, PrintWriter out,
			int level) {
		StringBuffer elementIndent = new StringBuffer();
		for (int i = 0; i < level; i++) {
			elementIndent.append("  "); //$NON-NLS-1$
		}
		StringBuffer elementPrefix = new StringBuffer();
		elementPrefix.append("<"); //$NON-NLS-1$
		elementPrefix.append(element.getName());

		StringBuffer attributeIndent = new StringBuffer(elementIndent
				.toString());
		for (int i = 0; i < elementPrefix.length() + 1; i++) {
			attributeIndent.append(" "); //$NON-NLS-1$
		}

		out.print(elementIndent.toString());
		out.print(elementPrefix.toString());
		String[] attributeNames = element.getAttributeNames();
		for (int i = 0; i < attributeNames.length; i++) {
			String attributeName = attributeNames[i];
			if (i > 0) {
				out.println();
				out.print(attributeIndent);
			} else {
				out.print(" "); //$NON-NLS-1$
			}

			out.print(attributeName);
			out.print("=\""); //$NON-NLS-1$
			out.print(DocumentWriter
					.escape(element.getAttribute(attributeName)));
			out.print("\""); //$NON-NLS-1$
		}
		out.println(">"); //$NON-NLS-1$

		IConfigElement[] children = element.getChildren();
		for (int i = 0; i < children.length; i++) {
			writeElement(children[i], out, level + 1);
		}

		out.print(elementIndent);
		out.print("</"); //$NON-NLS-1$
		out.print(element.getName());
		out.println(">"); //$NON-NLS-1$
	}

}
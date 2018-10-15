executionContext.setVetoableCallBack(callback);

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

package org.eclipse.xpand2;

import java.io.BufferedOutputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.io.StringReader;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import org.eclipse.emf.mwe.core.ConfigurationException;
import org.eclipse.emf.mwe.core.WorkflowContext;
import org.eclipse.emf.mwe.core.issues.Issues;
import org.eclipse.emf.mwe.core.monitor.ProgressMonitor;
import org.eclipse.internal.xpand2.ast.Definition;
import org.eclipse.internal.xpand2.ast.ExpandStatement;
import org.eclipse.internal.xpand2.ast.Template;
import org.eclipse.internal.xpand2.codeassist.XpandTokens;
import org.eclipse.internal.xpand2.parser.XpandParseFacade;
import org.eclipse.internal.xpand2.pr.ProtectedRegionResolverImpl;
import org.eclipse.internal.xtend.util.ProfileCollector;
import org.eclipse.internal.xtend.xtend.parser.ParseException;
import org.eclipse.xpand2.output.Outlet;
import org.eclipse.xpand2.output.Output;
import org.eclipse.xpand2.output.OutputImpl;
import org.eclipse.xpand2.output.PostProcessor;
import org.eclipse.xtend.expression.AbstractExpressionsUsingWorkflowComponent;
import org.eclipse.xtend.expression.Variable;
import org.eclipse.xtend.typesystem.MetaModel;

public class Generator extends AbstractExpressionsUsingWorkflowComponent {

	private static final String COMPONENT_NAME = "Xpand Generator";

	private String genPath = null;

	private String srcPath = null;

	private String prSrcPaths = null;

	private String prExcludes = null;

	private boolean prDefaultExcludes = true;

	private String expand = null;

	private String fileEncoding = System.getProperty("file.encoding");

	private List<?> beautifier = new ArrayList<Object>();

	private final List<String> advices = new ArrayList<String>();

	private final List<String> extensionAdvices = new ArrayList<String>();

	private boolean automaticHyphens = false;

	private String collectProfileSummary = null;

	private String verboseProfileFilename = null;

	private Output output = null;

	/**
	 * Sets the collection profile summary.
	 * 
	 * @param summary
	 *            the summary
	 */
	public void setCollectProfileSummary(final String summary) {
		collectProfileSummary = summary;
	}

	/**
	 * Sets the filename for verbose profile.
	 * 
	 * @param fileName
	 *            filename for verbose profile
	 */
	public void setVerboseProfileFilename(final String fileName) {
		verboseProfileFilename = fileName;
	}

	/**
	 * Enables or disables the automatic hyphenation. If automatic hyphenation
	 * is enabled, redundant blank lines are avoided automatically.
	 * 
	 * @param automaticHyphens
	 *            If <code>true</code>, automatic hyphenation is enabled,
	 *            otherwise disabled.
	 */
	public void setAutomaticHyphens(final boolean automaticHyphens) {
		this.automaticHyphens = automaticHyphens;
	}

	/**
	 * @see org.eclipse.emf.mwe.core.lib.AbstractWorkflowComponent#getLogMessage()
	 */
	@Override
	public String getLogMessage() {
		final Set<String> outletDescriptions = new HashSet<String>();
		for (final Outlet outlet : outlets) {
			outletDescriptions.add(outlet.toString());
		}
		final String outletDesc = outletDescriptions.size() == 1 ? outletDescriptions.iterator().next()
				: outletDescriptions.toString();
		return "generating '" + expand + "' => " + outletDesc;
	}

	/**
	 * Adds an advice.
	 * 
	 * @param advice
	 *            the advice
	 */
	@Override
	public void addAdvice(final String advice) {
		if (!advices.contains(advice)) {
			advices.add(advice);
		}
	}

	/**
	 * Adds an extension advice.
	 * 
	 * @param extensionAdvice
	 *            the extension advice
	 */
	@Override
	public void addExtensionAdvice(final String extensionAdvice) {
		if (!extensionAdvices.contains(extensionAdvice)) {
			extensionAdvices.add(extensionAdvice);
		}
	}

	/**
	 * Returns the list of beatifiers that will be applied to the generated
	 * output.
	 * 
	 * @return list of beautifiers
	 */
	public List<?> getBeautifier() {
		return beautifier;
	}

	/**
	 * Sets the list of beatifiers that will be applied to the generated output.
	 * 
	 * @param beautifiers
	 *            list of beautifiera
	 */
	public void setBeautifier(final List<?> beautifiers) {
		beautifier = beautifiers;
	}

	/**
	 * Sets the character encoding used for the output file.
	 * 
	 * @param fileEncoding
	 *            name of character encoding
	 */
	public void setFileEncoding(final String fileEncoding) {
		this.fileEncoding = fileEncoding;
	}

	/**
	 * Returns the name of character encoding used for the output file.
	 * 
	 * @return name of character encoding
	 */
	public String getFileEncoding() {
		return fileEncoding;
	}

	/**
	 * 
	 * @deprecated use outlets instead
	 */
	@Deprecated
	public void setGenPath(final String genPath) {
		this.genPath = fixPath(genPath);
	}

	/**
	 * Sets the statement that is to expand by the generator.
	 * 
	 * @param invoke
	 *            statement to expand
	 */
	public void setExpand(final String invoke) {
		expand = invoke;
	}

	/**
	 * Enables oder disables the default excludes for protected regions.
	 * 
	 * @param prDefaultExcludes
	 *            If <code>true</code>, the default excludes are enabled,
	 *            otherwise disabled.
	 */
	public void setPrDefaultExcludes(final boolean prDefaultExcludes) {
		this.prDefaultExcludes = prDefaultExcludes;
	}

	/**
	 * Sets the additional excludes for protected regions.
	 * 
	 * @param prExcludes
	 *            the excludes
	 */
	public void setPrExcludes(final String prExcludes) {
		this.prExcludes = prExcludes;
	}

	/**
	 * Sets the source paths for protected regions.
	 * 
	 * @param prSrcPathes
	 *            the source paths
	 */
	public void setPrSrcPaths(final String prSrcPathes) {
		this.prSrcPaths = prSrcPathes;
	}

	/**
	 * @see org.eclipse.emf.mwe.core.lib.AbstractWorkflowComponent#getComponentName()
	 */
	@Override
	public String getComponentName() {
		return COMPONENT_NAME;
	}

	/**
	 * 
	 * @deprecated use outlets instead
	 */
	@Deprecated
	public void setSrcPath(final String srcPath) {
		this.srcPath = fixPath(srcPath);
	}

	private String fixPath(final String p) {
		if (p.endsWith("\\"))
			return p.replace('\\', '/');
		if (p.endsWith("/"))
			return p;
		return p + "/";
	}

	@Override
	protected void invokeInternal2(final WorkflowContext ctx, final ProgressMonitor monitor, final Issues issues) {
		OutputStream verboseProfileOutputStream = null;

		if (verboseProfileFilename != null) {
			try {
				verboseProfileOutputStream = new BufferedOutputStream(new FileOutputStream(verboseProfileFilename));
				ProfileCollector.getInstance().setDetailedLoggingWriter(verboseProfileOutputStream);
			}
			catch (final IOException exc) {
				log.warn("Could not open profiling log file", exc);
			}
		}

		final Output out = getOutput();
		final List<Outlet> outlets = getInitializedOutlets();
		for (final Outlet outlet : outlets) {
			out.addOutlet(outlet);
		}

		ProtectedRegionResolverImpl prs = null;
		if (prSrcPaths != null) {
			prs = new ProtectedRegionResolverImpl();
			prs.setDefaultExcludes(prDefaultExcludes);
			prs.setIgnoreList(prExcludes);
			prs.setSrcPathes(prSrcPaths);
			prs.setFileEncoding(fileEncoding);
		}

		XpandExecutionContextImpl executionContext = new XpandExecutionContextImpl(out, prs, getGlobalVars(ctx),
				exceptionHandler, getNullEvaluationHandler());
		if (monitor != null) {
			executionContext.setMonitor(monitor);
		}
		executionContext.setResourceManager(getResourceManager());
		if (callback != null) {
			executionContext.setCallBack(callback);
		}

		if (fileEncoding != null) {
			executionContext.setFileEncoding(fileEncoding);
		}

		for (final MetaModel mm : metaModels) {
			executionContext.registerMetaModel(mm);
		}

		final ExpandStatement es = getStatement();
		if (es == null)
			throw new ConfigurationException("property 'expand' has wrong syntax!");

		final String[] names = ctx.getSlotNames();
		for (final String name : names) {
			executionContext = (XpandExecutionContextImpl) executionContext.cloneWithVariable(new Variable(name, ctx
					.get(name)));
		}

		for (final String advice : advices) {
			final String[] allAdvices = advice.split(",");
			for (final String string : allAdvices) {
				executionContext.registerAdvices(string.trim());
			}
		}

		for (final String advice : extensionAdvices) {
			final String[] allAdvices = advice.split(",");
			for (final String string : allAdvices) {
				executionContext.registerExtensionAdvices(string.trim());
			}
		}

		es.evaluate(executionContext);

		for (final Outlet element : outlets) {
			final String name = (element.getName() == null ? "[default]" : element.getName()) + "(" + element.getPath()
					+ ")";
			if (element.getFilesWrittenAndClosed() > 0) {
				log.info("Written " + element.getFilesWrittenAndClosed() + " files to outlet " + name);
			}
			if (element.getFilesCreated() > element.getFilesWrittenAndClosed()) {
				log.info("Skipped writing of " + (element.getFilesCreated() - element.getFilesWrittenAndClosed())
						+ " files to outlet " + name);
			}
		}

		ProfileCollector.getInstance().finish();
		if ("true".equalsIgnoreCase(this.collectProfileSummary)) {
			log.info("profiling info: \n" + ProfileCollector.getInstance().toString());
		}

		if (verboseProfileOutputStream != null) {
			try {
				verboseProfileOutputStream.close();
			}
			catch (final IOException exc) {
				log.warn("problem closing profile log file", exc);
			}
		}
	}

	private final List<Outlet> outlets = new ArrayList<Outlet>();

	/**
	 * Adds an outlet.
	 * 
	 * @param outlet
	 *            the outlet
	 */
	public void addOutlet(final Outlet outlet) {
		outlets.add(outlet);
	}

	/**
	 * Sets the output.
	 * 
	 * @param output
	 *            the output
	 */
	public void setOutput(final Output output) {
		this.output = output;
	}

	private Output getOutput() {
		if (output == null) {
			// lazy initialization
			final OutputImpl out = new OutputImpl();
			out.setAutomaticHyphens(automaticHyphens);
			this.output = out;
		}
		return output;
	}

	private List<Outlet> initializedOutlets = null;

	private List<Outlet> getInitializedOutlets() {
		if (initializedOutlets == null) {
			final List<Outlet> result = new ArrayList<Outlet>(outlets);
			if (result.isEmpty()) {
				if (genPath != null) { // backward compatibility
					Outlet o = new Outlet();
					o.setAppend(false);
					o.setFileEncoding(fileEncoding);
					o.setOverwrite(true);
					o.setPath(genPath);
					result.add(o);

					o = new Outlet();
					o.setAppend(true);
					o.setFileEncoding(fileEncoding);
					o.setName("APPEND");
					o.setOverwrite(true);
					o.setPath(genPath);
					result.add(o);
				}
				if (srcPath != null) {
					final Outlet o = new Outlet();
					o.setAppend(false);
					o.setFileEncoding(fileEncoding);
					o.setName("ONCE");
					o.setOverwrite(false);
					o.setPath(srcPath);

					result.add(o);
				}
			}
			for (final Outlet o : result) {
				if (o.postprocessors.isEmpty()) {
					for (final Object name : beautifier) {
						final PostProcessor element = (PostProcessor) name;
						o.addPostprocessor(element);
					}
				}
				// Initialize file encoding for outlets. If it is not set then
				// take the Generator
				// default encoding. If this not set also then take System
				// default.
				if (o.getFileEncoding() == null) {
					o.setFileEncoding(fileEncoding);
				}
			}
			initializedOutlets = result;
		}
		return initializedOutlets;
	}

	/**
	 * Retrieves the configured and initialized outlets of the generator.
	 * 
	 * @since 4.2
	 */
	public final List<Outlet> getOutlets() {
		return Collections.unmodifiableList(getInitializedOutlets());
	}

	private ExpandStatement getStatement() {
		final Template tpl = XpandParseFacade.file(new StringReader(XpandTokens.LT + "DEFINE test FOR test"
				+ XpandTokens.RT + XpandTokens.LT + "EXPAND " + expand + XpandTokens.RT + XpandTokens.LT + "ENDDEFINE"
				+ XpandTokens.RT), null);
		ExpandStatement es = null;
		try {
			es = (ExpandStatement) ((Definition) tpl.getDefinitions()[0]).getBody()[1];
		}
		catch (final Exception e) {
			log.error(e);
		}
		return es;
	}

	@Override
	protected void checkConfigurationInternal(final Issues issues) {
		super.checkConfigurationInternal(issues);
		if (genPath == null && getInitializedOutlets().isEmpty()) {
			issues.addError(this, "You need to configure at least one outlet!");
		}
		if ((genPath != null || srcPath != null) && !outlets.isEmpty()) {
			issues.addWarning(this, "'genPath' and 'srcPath' properties are ignored since you have specified outlets!");
		}
		int defaultOutlets = 0;
		for (final Outlet o : getInitializedOutlets()) {
			if (o.getName() == null) {
				defaultOutlets++;
			}
		}
		if (defaultOutlets > 1) {
			issues.addError(this,
					"Only one outlet can be the default outlet. Please specifiy a name for the other outlets!");
		}
		else if (defaultOutlets == 0) {
			issues.addWarning(this, "No default outlet configured!");
		}
		if (expand == null) {
			issues.addError(this, "property 'expand' not configured!");
		}
		else {
			try {
				final ExpandStatement es = getStatement();
				if (es == null) {
					issues.addError(this, "property 'expand' has wrong syntax!");
				}
			}
			catch (final ParseException e) {
				issues.addError(this, "property 'expand' has wrong syntax : " + e.getMessage());
			}
		}
	}

}
e.printStackTrace();

/**
 * <copyright> 
 *
 * Copyright (c) 2008 itemis AG and others.
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
package org.eclipse.emf.editor.extxpt;

import java.util.ArrayList;
import java.util.List;

import org.eclipse.core.resources.IProject;
import org.eclipse.emf.common.util.TreeIterator;
import org.eclipse.emf.ecore.EObject;
import org.eclipse.emf.ecore.EStructuralFeature;
import org.eclipse.emf.ecore.util.EcoreUtil;
import org.eclipse.emf.editor.EEPlugin;
import org.eclipse.emf.mwe.core.issues.Issues;
import org.eclipse.emf.mwe.core.issues.IssuesImpl;
import org.eclipse.internal.xtend.expression.parser.SyntaxConstants;
import org.eclipse.internal.xtend.xtend.ast.ExtensionFile;
import org.eclipse.xtend.XtendFacade;
import org.eclipse.xtend.check.CheckUtils;
import org.eclipse.xtend.expression.EvaluationException;
import org.eclipse.xtend.expression.ExecutionContext;
import org.eclipse.xtend.shared.ui.Activator;
import org.eclipse.xtend.shared.ui.core.IXtendXpandProject;
import org.eclipse.xtend.shared.ui.core.IXtendXpandResource;

/**
 * @author Dennis Hübner - Initial contribution and API
 * 
 */
public class ExtXptFacade {

	private IProject project;
	private final ExecutionContext context;
	public static final String CHECK_EXT = "Checks";
	public static final String STYLE_EXT = "ItemLabelProvider";
	public static final String PROPOSAL_EXT = "Proposals";

	public ExtXptFacade(IProject project, ExecutionContext context) {
		this.project = project;
		this.context = context;
	}

	public Object style(String extension, EObject object) {
		String extendFile = path(object) + ExtXptFacade.STYLE_EXT;
		Object retVal = evaluate(extendFile, extension, object);
		return retVal;
	}

	/**
	 * @param extensionFile
	 * @param extensionName
	 * @param params
	 * @return
	 */
	private Object evaluate(String extensionFile, String extensionName, Object... params) {
		Object retVal = null;
		try {
			XtendFacade facade = XtendFacade.create(context, extensionFile);
			retVal = facade.call(extensionName, params);
		}
		catch (IllegalArgumentException e) {
			// no extension specified
		}
		catch (EvaluationException e) {
			EEPlugin.logError("Exception during extension evaluation", e);
		}
		catch (RuntimeException e) {
			// TODO check file exists
			// extension file not found
		}
		catch (Throwable e) {
			EEPlugin.logError("Exception during extension evaluation", new RuntimeException(e));
		}
		return retVal;
	}

	// TODO split method
	public List<?> proposals(EStructuralFeature feature, EObject ctx, List<?> fromList) {
		String extFile = path(ctx) + ExtXptFacade.PROPOSAL_EXT;
		List<?> retVal = new ArrayList<Object>();
		Object eval;
		if (fromList != null) {
			retVal = fromList;
			eval = evaluate(extFile, feature.getName(), ctx, fromList);
		}
		else {
			eval = evaluate(extFile, feature.getName(), ctx);
		}
		if (eval != null) {
			if (eval instanceof List<?>) {
				retVal = (List<?>) eval;
			}
			else {
				EEPlugin.logError("Returned type must be a List! File:" + extFile + ", Extension:" + feature.getName());
			}
		}
		return retVal;
	}

	public Issues check(EObject rootObject) {
		String checkFile = path(rootObject) + ExtXptFacade.CHECK_EXT;
		List<EObject> all = new ArrayList<EObject>();
		all.add(rootObject);
		EObject rootContainer = EcoreUtil.getRootContainer(rootObject);
		TreeIterator<EObject> iter = rootContainer.eAllContents();
		while (iter.hasNext())
			all.add(iter.next());
		Issues issuesImpl = new IssuesImpl();
		IXtendXpandProject extxptProject = Activator.getExtXptModelManager().findProject(project);
		if (extxptProject != null) {
			IXtendXpandResource extxptResource = extxptProject.findExtXptResource(checkFile, CheckUtils.FILE_EXTENSION);
			if (extxptResource != null) {
				ExtensionFile file = (ExtensionFile) extxptResource.getExtXptResource();
				try {
					file.check(context, all, issuesImpl, false);
				}
				catch (IllegalArgumentException e) {
					// no extension specified
				}
				catch (Exception e) {
					EEPlugin.logError("Exception during check evaluation", e);
				}
			}
		}
		else {
			EEPlugin.logWarning("Enable Xtend/Xpand-Nature for '" + project.getName() + "' to check models.");
		}
		return issuesImpl;
	}

	private String path(EObject object) {
		return object.eClass().getEPackage().getName() + SyntaxConstants.NS_DELIM;
	}

	public IProject getProject() {
		return project;
	}
}
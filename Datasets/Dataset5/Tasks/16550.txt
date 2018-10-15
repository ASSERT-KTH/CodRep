is = ResourceLoaderFactory.createResourceLoader().getResourceAsStream (_extensionFile.replace (SyntaxConstants.NS_DELIM, "/") + "." +XtendFile.FILE_EXTENSION);

/*
Copyright (c) 2008 Arno Haase, André Arnold.
All rights reserved. This program and the accompanying materials
are made available under the terms of the Eclipse Public License v1.0
which accompanies this distribution, and is available at
http://www.eclipse.org/legal/epl-v10.html

Contributors:
    Arno Haase - initial API and implementation
    André Arnold
 */
package org.eclipse.xtend.middleend.xtend;

import java.io.InputStream;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;

import org.eclipse.emf.mwe.core.WorkflowContext;
import org.eclipse.emf.mwe.core.issues.Issues;
import org.eclipse.emf.mwe.core.monitor.ProgressMonitor;
import org.eclipse.emf.mwe.core.resources.ResourceLoaderFactory;
import org.eclipse.internal.xtend.expression.parser.SyntaxConstants;
import org.eclipse.internal.xtend.xtend.XtendFile;
import org.eclipse.xtend.expression.AbstractExpressionsUsingWorkflowComponent;
import org.eclipse.xtend.middleend.LanguageContributor;
import org.eclipse.xtend.middleend.xtend.plugin.OldXtendRegistryFactory;


/**
 * 
 * @author Arno Haase (http://www.haase-consulting.com)
 * @author André Arnold
 */
public class XtendComponent extends AbstractExpressionsUsingWorkflowComponent {

    /** Stores the value of the 'invoke' property. Needed for error analysis. */ 
    private String _invokeExpression;
    String _extensionFile = null;
    private String _expression = null;
    private String _outputSlot = WorkflowContext.DEFAULT_SLOT;
    
    private String _fileEncoding = null;
    
    public XtendComponent () {
    	if (LanguageContributor.INSTANCE.getLanguageContributionByName(OldXtendRegistryFactory.LANGUAGE_NAME) == null)
    		LanguageContributor.INSTANCE.addLanguageContribution (OldXtendRegistryFactory.class);
	}

    public void setFileEncoding (String fileEncoding) {
        _fileEncoding = fileEncoding;
    }
    
    @Override
    public String getLogMessage() {
    	return "executing '" + _invokeExpression + "'";
    }
    
    public void setInvoke (String invoke) {
    	_invokeExpression = invoke;
        final int i = invoke.lastIndexOf (SyntaxConstants.NS_DELIM);
        if (i != -1) {
            _extensionFile = invoke.substring(0, i);
            _expression = invoke.substring (i + SyntaxConstants.NS_DELIM.length());
        } 
        else 
            _expression = invoke;
    }

    public void setOutputSlot (String outputSlot) {
        _outputSlot = outputSlot;
    }
    
    @Override
    public void invokeInternal2(final WorkflowContext ctx, final ProgressMonitor monitor, final Issues issues) {
        if (! extensionFileExists ()) {
            issues.addError ("Cannot find extension file: " + _extensionFile);
            return;
        }
        
        final Map<String, Object> localVars = new HashMap<String, Object> ();
        for (String slotName: ctx.getSlotNames())
            localVars.put (slotName, ctx.get (slotName));
        
        final Map<String, Object> globalVars = new HashMap<String, Object> ();
        Set<String> varNames = getGlobalVars(ctx).keySet();
        for (String varName: varNames)
            globalVars.put (varName, getGlobalVars(ctx).get(varName).getValue());
        
        final Object result = XtendBackendFacade.evaluateExpression (_expression, _extensionFile, _fileEncoding, metaModels, localVars, globalVars, _advice);
        ctx.set (_outputSlot, result);
    }

    private boolean extensionFileExists() {
        InputStream is = null;
        try {
            is = ResourceLoaderFactory.createResourceLoader().getResourceAsStream (_extensionFile.replace (SyntaxConstants.NS_DELIM, "/") + XtendFile.FILE_EXTENSION);
        }
        catch (Exception exc) {
            // do nothing - an exception just means that the extension file does not exist 
        }
        if (is != null) {
            try {
                is.close ();
            }
            catch (Exception e) {}
        }
        return is != null;
    }

    @Override
    public void checkConfigurationInternal (Issues issues) {
        super.checkConfigurationInternal (issues);
        
        // Try to create detailed error message (see Bug#172567)
        String compPrefix = getId()!=null ? getId()+": " : "";
        
        if (_invokeExpression == null || _invokeExpression.trim().length()==0) {
            issues.addError(compPrefix + "Property 'invoke' not specified.");
            return;
        }
        if (_extensionFile == null) {
            issues.addError (compPrefix + "Error parsing property 'invoke': Could not extract name of the extension file.");
            return;
        }
        if (! extensionFileExists () || _expression == null) {
            issues.addError (compPrefix + "Property 'invoke' not specified properly. Extension file '" + _extensionFile + "' not found.");
            return;
        }
        if (_expression == null) {
            issues.addError (compPrefix + "Error parsing property 'invoke': Could not extract the expression to invoke in extension file '" + _extensionFile + "'.");
            return;
        }
    }
}
package org.eclipse.xtend.middleend.old;

/*
Copyright (c) 2008 Arno Haase.
All rights reserved. This program and the accompanying materials
are made available under the terms of the Eclipse Public License v1.0
which accompanies this distribution, and is available at
http://www.eclipse.org/legal/epl-v10.html

Contributors:
    Arno Haase - initial API and implementation
 */
package org.eclipse.xtend.middleend.old.xtend;

import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.eclipse.emf.mwe.core.WorkflowContext;
import org.eclipse.emf.mwe.core.WorkflowInterruptedException;
import org.eclipse.emf.mwe.core.issues.Issues;
import org.eclipse.emf.mwe.core.monitor.ProgressMonitor;
import org.eclipse.xtend.expression.AbstractExpressionsUsingWorkflowComponent;


//TODO test this

/**
 * 
 * @author Arno Haase (http://www.haase-consulting.com)
 */
public class CheckComponent extends AbstractExpressionsUsingWorkflowComponent {

    private String _expression = null;
    private List<String> _checkFiles = new ArrayList<String>();
    private boolean _abortOnError = true;
    private boolean _warnIfNothingChecked = false;
    private String _emfAllChildrenSlot;
    private String _fileEncoding = null;

    public void setAbortOnError (boolean abortOnError) {
        _abortOnError = abortOnError;
    }

    public void addCheckFile (String checkFile) {
        _checkFiles.add(checkFile);
    }

    public void setExpression (String expression) {
        _expression = expression;
    }

    public void setWarnIfNothingChecked (boolean b) {
        _warnIfNothingChecked = b;
    }

    public void setEmfAllChildrenSlot (String childExpression) {
        _emfAllChildrenSlot = childExpression;
    }

    public void setFileEncoding (String fileEncoding) {
        _fileEncoding = fileEncoding;
    }

    @Override
    public String getLogMessage() {
    	final StringBuilder result = new StringBuilder ();
    	if ( _emfAllChildrenSlot != null ) 
    		result.append ("slot " + _emfAllChildrenSlot + " ");
    	else 
    		result.append ("expression " + _expression + " ");
    	
    	result.append ("check file(s): ");
    	for (String f: _checkFiles) 
    		result.append (f + " ");
		
    	return result.toString();
    }    

    
    @Override
    protected void invokeInternal2 (WorkflowContext wfCtx, ProgressMonitor monitor, Issues issues) {
        final Collection<?> allObjects = getExpressionResult (wfCtx, _expression);

        for (String checkFile : _checkFiles) 
            CheckBackendFacade.checkAll (checkFile, _fileEncoding, metaModels, issues, allObjects);

        if (_abortOnError && issues.hasErrors())
            throw new WorkflowInterruptedException ("Errors during validation.");
    }


    @Override
    public void checkConfiguration (Issues issues) {
        super.checkConfiguration (issues);
        
        if (_expression == null && _emfAllChildrenSlot != null) 
            _expression = _emfAllChildrenSlot + ".eAllContents.union ( {" + _emfAllChildrenSlot + "} )";
        else if (_expression != null && _emfAllChildrenSlot == null) {
            // ok - do nothing, expression already has a reasonable value
        } 
        else 
            issues.addError(this, "You have to set one of the properties 'expression' and 'emfAllChildrenSlot'!");

        if (_checkFiles.isEmpty()) 
            issues.addError (this, "Property 'checkFile' not set!");
    }

    private Collection<?> getExpressionResult (WorkflowContext wfCtx, String expression2) {
        final Map<String, Object> localVars = new HashMap<String, Object>();
        final String[] names = wfCtx.getSlotNames ();
        for (int i = 0; i < names.length; i++) 
            localVars.put (names[i], wfCtx.get (names[i]));
        
        final Object result = XtendBackendFacade.evaluateExpression (expression2, metaModels, localVars);
        
        if (result instanceof Collection)
            return (Collection<?>) result;

        if (result == null)
            return Collections.EMPTY_SET;

        return Collections.singleton (result);
    }
}
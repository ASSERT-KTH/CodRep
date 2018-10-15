final StringBuilder sb = new StringBuilder ("dereferenced null " + ((pos != null) ? ("(" + pos + ")") : ""));

/*
Copyright (c) 2008 Arno Haase.
All rights reserved. This program and the accompanying materials
are made available under the terms of the Eclipse Public License v1.0
which accompanies this distribution, and is available at
http://www.eclipse.org/legal/epl-v10.html

Contributors:
    Arno Haase - initial API and implementation
 */
package org.eclipse.xtend.backend.internal;

import java.util.ArrayList;
import java.util.List;

import org.apache.commons.logging.LogFactory;
import org.eclipse.xtend.backend.common.BackendTypesystem;
import org.eclipse.xtend.backend.common.Constants;
import org.eclipse.xtend.backend.common.ContributionStateContext;
import org.eclipse.xtend.backend.common.CreationCache;
import org.eclipse.xtend.backend.common.ExecutionContext;
import org.eclipse.xtend.backend.common.FunctionDefContext;
import org.eclipse.xtend.backend.common.FunctionInvoker;
import org.eclipse.xtend.backend.common.GlobalParamContext;
import org.eclipse.xtend.backend.common.LocalVarContext;
import org.eclipse.xtend.backend.common.SourcePos;
import org.eclipse.xtend.backend.common.StacktraceEntry;


/**
 * 
 * @author Arno Haase (http://www.haase-consulting.com)
 */
public final class ExecutionContextImpl implements ExecutionContext {
	private final CreationCache _creationCache = new CreationCacheImpl ();
	private FunctionDefContext _functionDefContext;
	private LocalVarContext _localVarContext = new LocalVarContext ();
	private final FunctionInvoker _functionInvoker = new FunctionInvokerImpl ();
	private final BackendTypesystem _typeSystem;
	private final GlobalParamContext _globalParamContext = new GlobalParamContextImpl ();
	private final boolean _logStacktrace;
	private final List<StacktraceEntry> _stacktrace = new ArrayList<StacktraceEntry> ();
	
	private final ContributionStateContext _contributionStateContext = new ContributionStateContext ();
	
	public ExecutionContextImpl (FunctionDefContext initialFunctionDefContext, BackendTypesystem typesystem, boolean logStacktrace) {
		_functionDefContext = initialFunctionDefContext;
		_typeSystem = typesystem;
		_logStacktrace = logStacktrace;
	}

	public CreationCache getCreationCache() {
		return _creationCache;
	}

	public FunctionDefContext getFunctionDefContext() {
		return _functionDefContext;
	}

	public void setFunctionDefContext(FunctionDefContext ctx) {
		_functionDefContext = ctx;
	}

	public LocalVarContext getLocalVarContext() {
		return _localVarContext;
	}

	public void setLocalVarContext(LocalVarContext ctx) {
		_localVarContext = ctx;
	}

	public FunctionInvoker getFunctionInvoker() {
		return _functionInvoker;
	}

	public BackendTypesystem getTypesystem() {
		return _typeSystem;
	}

	public GlobalParamContext getGlobalParamContext() {
		return _globalParamContext;
	}

	public void logNullDeRef (SourcePos pos) {
	    final StringBuilder sb = new StringBuilder ("dereferenced null (" + pos + ")");
	    for (int i=_stacktrace.size() - 1; i>= 0; i--)
	        sb.append ("\n  " + _stacktrace.get (i));
	    
	    LogFactory.getLog (Constants.LOG_NULL_DEREF).warn (sb);
	}
	
	public ContributionStateContext getContributionStateContext () {
	    return _contributionStateContext;
	}

    public List<StacktraceEntry> getStacktrace () {
        return _stacktrace;
    }

    public boolean isLogStacktrace () {
        return _logStacktrace;
    }
}
ctx.getResourceManager().setFileEncoding (fileEncoding);

/*
Copyright (c) 2008, 2009 Arno Haase, André Arnold.
All rights reserved. This program and the accompanying materials
are made available under the terms of the Eclipse Public License v1.0
which accompanies this distribution, and is available at
http://www.eclipse.org/legal/epl-v10.html

Contributors:
    Arno Haase - initial API and implementation
    André Arnold
 */
package org.eclipse.xtend.middleend.xtend;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.HashMap;
import java.util.Map;

import org.eclipse.emf.mwe.core.issues.Issues;
import org.eclipse.xtend.backend.BackendFacade;
import org.eclipse.xtend.backend.common.ExecutionContext;
import org.eclipse.xtend.backend.common.FunctionDefContext;
import org.eclipse.xtend.backend.common.QualifiedName;
import org.eclipse.xtend.expression.ExecutionContextImpl;
import org.eclipse.xtend.middleend.LanguageContributor;
import org.eclipse.xtend.middleend.MiddleEnd;
import org.eclipse.xtend.middleend.MiddleEndFactory;
import org.eclipse.xtend.middleend.xtend.internal.OldHelper;
import org.eclipse.xtend.middleend.xtend.internal.xtend.CheckConverter;
import org.eclipse.xtend.middleend.xtend.plugin.OldCheckRegistryFactory;
import org.eclipse.xtend.middleend.xtend.plugin.OldXtendRegistryFactory;
import org.eclipse.xtend.typesystem.MetaModel;


/**
 * 
 * @author Arno Haase (http://www.haase-consulting.com)
 * @author André Arnold
 */
public class CheckBackendFacade {

    private final String _checkFile;
    private final MiddleEnd _middleEnd;
    private final Collection<MetaModel> _mms;

    public static void checkAll (String xtendFileName, Collection<MetaModel> mms, Issues issues, Collection<?> allObjects) {
        checkAll (xtendFileName, null, mms, issues, allObjects);
    }
    
    public static void checkAll (String checkFileName, String fileEncoding, Collection<MetaModel> mms, Issues issues, Collection<?> allObjects) {
        CheckBackendFacade.invokeCheckFunction (checkFileName, fileEncoding, mms, CheckConverter.ALL_CHECKS_FUNCTION_NAME, issues, allObjects);
    }

    /**
     * This function invokes a single Xtend function, returning the result. The fileEncoding may be null, in which case the platform's default file
     *  encoding is used.
     */
    public static Object invokeCheckFunction (String checkFileName, String fileEncoding, Collection<MetaModel> mms, QualifiedName functionName, Object... parameters) {
        return createForFile (checkFileName, fileEncoding, mms).invokeCheckFunction (functionName, parameters);
    }
    
    public Object invokeCheckFunction (QualifiedName functionName, Object... parameters) {
        final FunctionDefContext fdc = _middleEnd.getFunctions (_checkFile);
        final ExecutionContext ctx = BackendFacade.createExecutionContext (fdc, _middleEnd.getTypesystem(), true); //TO--DO configure isLogStacktrace
        return fdc.invoke (ctx, functionName, Arrays.asList (parameters));
    }
    
    
    public static CheckBackendFacade createForFile (String checkFileName, String fileEncoding, Collection<MetaModel> mms) {
        return new CheckBackendFacade (checkFileName, fileEncoding, mms);
    }

    private Map<Class<?>, Object> getSpecificParameters (String fileEncoding, Collection<MetaModel> mms) {
        fileEncoding = OldHelper.normalizedFileEncoding (fileEncoding);

        final ExecutionContextImpl ctx = new ExecutionContextImpl ();
        ctx.setFileEncoding (fileEncoding);
        for (MetaModel mm: mms)
            ctx.registerMetaModel (mm);
        
        final Map<Class<?>, Object> result = new HashMap<Class<?>, Object> ();
        result.put (OldXtendRegistryFactory.class, ctx);
        result.put (OldCheckRegistryFactory.class, ctx);
        return result;
    }
    
    private CheckBackendFacade (String checkFileName, String fileEncoding, Collection<MetaModel> mms) {
        if (mms == null)
            mms = new ArrayList<MetaModel> ();
        
        _checkFile = OldHelper.normalizeCheckResourceName (checkFileName);
        _mms = mms;
    	if (LanguageContributor.INSTANCE.getLanguageContributionByName (OldXtendRegistryFactory.LANGUAGE_NAME) == null) {
    		LanguageContributor.INSTANCE.addLanguageContribution (OldXtendRegistryFactory.class);
    	}
    	if (LanguageContributor.INSTANCE.getLanguageContributionByName (OldCheckRegistryFactory.LANGUAGE_NAME) == null) {
    		LanguageContributor.INSTANCE.addLanguageContribution (OldCheckRegistryFactory.class);
    	}
        if (MiddleEndFactory.canCreateFromExtentions()) {
            _middleEnd = MiddleEndFactory.createFromExtensions (OldHelper.guessTypesystem (mms), getSpecificParameters (fileEncoding, mms));
        } else {
        	_middleEnd = MiddleEndFactory.create (OldHelper.guessTypesystem (mms), LanguageContributor.INSTANCE.getFreshMiddleEnds (getSpecificParameters (fileEncoding, mms)));
        }
    }

    public FunctionDefContext getFunctionDefContext () {
        return _middleEnd.getFunctions (_checkFile);
    }

}

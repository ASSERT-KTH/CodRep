import org.eclipse.xtend.middleend.old.internal.xtendlib.XtendLibContributor;

/*
Copyright (c) 2008 Arno Haase.
All rights reserved. This program and the accompanying materials
are made available under the terms of the Eclipse Public License v1.0
which accompanies this distribution, and is available at
http://www.eclipse.org/legal/epl-v10.html

Contributors:
    Arno Haase - initial API and implementation
 */
package org.eclipse.xtend.middleend.old;

import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.eclipse.internal.xpand2.ast.Template;
import org.eclipse.internal.xpand2.model.XpandDefinition;
import org.eclipse.xpand2.XpandExecutionContext;
import org.eclipse.xpand2.XpandUtil;
import org.eclipse.xtend.backend.common.BackendTypesystem;
import org.eclipse.xtend.backend.common.NamedFunction;
import org.eclipse.xtend.backend.functions.FunctionDefContextFactory;
import org.eclipse.xtend.backend.functions.FunctionDefContextInternal;
import org.eclipse.xtend.backend.util.Cache;
import org.eclipse.xtend.backend.xtendlib.XtendLibContributor;


/**
 * This class manages the interdependent graph of parsed and converted Xpand files, allowing access to them by "compilation unit".
 * 
 * @author Arno Haase (http://www.haase-consulting.com)
 */
final class OldXpandRegistry {
    private final XpandExecutionContext _ctx;
    private final BackendTypesystem _ts;
    private final OldXtendRegistry _extensions;

    private final Cache<String, FunctionDefContextInternal> _functionDefContexts = new Cache<String, FunctionDefContextInternal> () {
        @Override
        protected FunctionDefContextInternal create (String compilationUnit) {
            return new FunctionDefContextFactory (_ts).create();
        }
    };
    
    /**
     * all functions actually defined in a given compilation unit
     */
    private final Map<String, List<NamedFunction>> _functionsByResource = new HashMap <String, List<NamedFunction>>();
    

    public OldXpandRegistry (XpandExecutionContext ctx, BackendTypesystem ts, OldXtendRegistry extensions) {
        _ctx = ctx;
        _ts = ts;
        _extensions = extensions;
    }
    
    
    private FunctionDefContextInternal getFunctionDefContext (String xtendName) {
        return _functionDefContexts.get (OldXtendHelper.normalizeXtendResourceName (xtendName));
    }
    
    
    /**
     * parses and converts an Xpand file and all other files it depends on. 
     */
    public void registerXpandFile (String xpandFile) {
        xpandFile = OldXtendHelper.normalizeXpandResourceName (xpandFile);
        
        if (_functionsByResource.containsKey (xpandFile))
            return;
        
        final String xpandResourceName = OldXtendHelper.xpandFileAsOldResourceName(xpandFile);
        final Template file = (Template) _ctx.getResourceManager().loadResource (xpandResourceName, XpandUtil.TEMPLATE_EXTENSION);
        if (file == null)
            throw new IllegalArgumentException ("could not find Xpand file '" + xpandResourceName + "'");
        
        final XpandExecutionContext ctx = (XpandExecutionContext) _ctx.cloneWithResource (file);
        
        final TypeToBackendType typeConverter = new TypeToBackendType (_ts, ctx);
        final OldDefinitionConverter definitionFactory = new OldDefinitionConverter (ctx, typeConverter);
        
        final List<NamedFunction> defined = new ArrayList<NamedFunction>();
        final FunctionDefContextInternal fdc = getFunctionDefContext (xpandFile);
        
        // register the XtendLib. Do this first so the extension can override functions
        fdc.register (new XtendLibContributor (_ts).getContributedFunctions());
        
        //TODO imported namespaces
        
        final Set<XpandDefinitionName> referenced = new HashSet<XpandDefinitionName> ();
        
        for (XpandDefinition ext: file.getDefinitions ())
            defined.add (definitionFactory.create (ext, fdc, referenced));
        
        
        _functionsByResource.put (xpandFile, defined);
        
        // make sure all imported resources are registered as well
        for (String imported: file.getImportedExtensions()) {
            _extensions.registerExtension (imported);
            for (NamedFunction f: _extensions.getContributedFunctions(imported))
                fdc.register (f);
        }

        // read all referenced template files...
        final Set<String> xpandFileNames = new HashSet<String> ();
        for (XpandDefinitionName n: referenced)
            xpandFileNames.add (n.getCanonicalTemplateFileName());
        
        for (String xpandFileName: xpandFileNames)
            registerXpandFile (xpandFileName);
        
        // ... and register all template definitions from these files. It is necessary to have them all registered to enable 
        //  polymorphism - static type analysis does not find all potential matches.
        for (String xpandFileName: xpandFileNames)
            for (NamedFunction f: _functionsByResource.get (xpandFileName))
                fdc.register(f);
    }


    public Collection<NamedFunction> getContributedFunctions (String xpandFile) {
        return _functionsByResource.get (xpandFile);
    }
}







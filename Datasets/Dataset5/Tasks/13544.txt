private static final Log log = LogFactory.getLog(XpandExecutionContextImpl.class);

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

import java.io.Reader;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.eclipse.emf.mwe.core.monitor.ProgressMonitor;
import org.eclipse.internal.xpand2.NoSuchTemplateException;
import org.eclipse.internal.xpand2.XpandUtil;
import org.eclipse.internal.xpand2.model.AdvicedDefinition;
import org.eclipse.internal.xpand2.model.XpandAdvice;
import org.eclipse.internal.xpand2.model.XpandDefinition;
import org.eclipse.internal.xpand2.model.XpandResource;
import org.eclipse.internal.xpand2.parser.XpandParseFacade;
import org.eclipse.internal.xpand2.pr.ProtectedRegionResolver;
import org.eclipse.internal.xpand2.type.XpandTypesMetaModel;
import org.eclipse.internal.xtend.expression.parser.SyntaxConstants;
import org.eclipse.internal.xtend.type.baseimpl.PolymorphicResolver;
import org.eclipse.internal.xtend.util.Cache;
import org.eclipse.internal.xtend.util.Pair;
import org.eclipse.internal.xtend.util.Triplet;
import org.eclipse.internal.xtend.xtend.ast.Around;
import org.eclipse.internal.xtend.xtend.ast.Extension;
import org.eclipse.xpand2.output.Output;
import org.eclipse.xtend.expression.ExceptionHandler;
import org.eclipse.xtend.expression.ExecutionContextImpl;
import org.eclipse.xtend.expression.NullEvaluationHandler;
import org.eclipse.xtend.expression.Resource;
import org.eclipse.xtend.expression.ResourceManager;
import org.eclipse.xtend.expression.ResourceParser;
import org.eclipse.xtend.expression.TypeSystemImpl;
import org.eclipse.xtend.expression.Variable;
import org.eclipse.xtend.expression.VetoableCallback;
import org.eclipse.xtend.typesystem.Callable;
import org.eclipse.xtend.typesystem.Operation;
import org.eclipse.xtend.typesystem.Type;

/**
 * *
 * 
 * @author Sven Efftinge (http://www.efftinge.de) *
 */
public class XpandExecutionContextImpl extends ExecutionContextImpl implements XpandExecutionContext {

    private final Log log = LogFactory.getLog(getClass());

    protected final Output output;
    
    protected final ProtectedRegionResolver protectedRegionResolver;
    
    private List<XpandAdvice> registeredAdvices = new ArrayList<XpandAdvice>();
    
    public XpandExecutionContextImpl(Output output, ProtectedRegionResolver prs) {
        this (output, prs, null, null, null);
    }
    public XpandExecutionContextImpl(Output output, ProtectedRegionResolver prs, String fileEncoding) {
        this (output, prs, null, null, null);
        resourceManager.setFileEncoding(fileEncoding);
    }
    
    public XpandExecutionContextImpl(Output output, ProtectedRegionResolver prs, Map<String, Variable> globalVars, ExceptionHandler exceptionHandler, NullEvaluationHandler nullEvaluationHandler) {
        this(new TypeSystemImpl(), output, prs, globalVars, exceptionHandler, nullEvaluationHandler);
    }

    public XpandExecutionContextImpl(
    		ResourceManager resourceManager,
    		Output output,
    		ProtectedRegionResolver prs,
    		Map<String, Variable> globalVars,
    		ProgressMonitor monitor,
    		ExceptionHandler exceptionHandler,
    		NullEvaluationHandler nullEvaluationHandler,
    		VetoableCallback callback) {
        this(
        	resourceManager,
        	/*Resource*/ null,
        	new TypeSystemImpl(),
        	/*Map<String, Variable> vars*/ null,
        	globalVars,
        	output,
        	prs,
        	monitor,
        	exceptionHandler,
        	/*List<Around>*/ null,
        	nullEvaluationHandler,
        	/*Map<Resource, Set<Extension>> allExtensionsPerResource*/ null,
        	callback,
        	/*Cache<Triplet<Resource,String,List<Type>>,Extension> extensionsForNameAndTypesCache*/ null,
        	/*Map<Pair<String, List<Type>>, Type> extensionsReturnTypeCache*/ null
        	);
    }

    protected XpandExecutionContextImpl(
		    final TypeSystemImpl ts,
		    Output output,
		    ProtectedRegionResolver prs,
		    Map<String, Variable> globalVars,
		    ExceptionHandler exceptionHandler,
		    NullEvaluationHandler nullEvaluationHandler) {
    	super(ts, globalVars);
        registerMetaModel(new XpandTypesMetaModel(this));
        registerParser(resourceManager);
        this.output = output;
        this.protectedRegionResolver = prs;
        this.exceptionHandler = exceptionHandler;
        this.nullEvaluationHandler = nullEvaluationHandler;
    }

    protected XpandExecutionContextImpl (
    		ResourceManager resourceManager, 
    		Resource currentResource, 
    		TypeSystemImpl typeSystem, 
    		Map<String, Variable> vars, 
            Map<String, Variable> globalVars, 
            Output output, 
            ProtectedRegionResolver protectedRegionResolver, 
            ProgressMonitor monitor, 
            ExceptionHandler exceptionHandler,
            List<Around> advices,
            NullEvaluationHandler nullEvaluationHandler,
            Map<Resource, Set<Extension>> allExtensionsPerResource,
            VetoableCallback callback, 
            Cache<Triplet<Resource,String,List<Type>>,Extension> extensionsForNameAndTypesCache,
            Map<Pair<String, List<Type>>, Type> extensionsReturnTypeCache) {
        super (
        	resourceManager, 
        	currentResource, 
        	typeSystem, 
        	vars, 
        	globalVars,
        	monitor,
        	exceptionHandler,
        	advices,
        	nullEvaluationHandler,
        	allExtensionsPerResource,
        	callback,
        	extensionsForNameAndTypesCache,
        	extensionsReturnTypeCache);
        registerMetaModel(new XpandTypesMetaModel(this));
        registerParser(resourceManager);
        this.output = output;
        this.protectedRegionResolver = protectedRegionResolver;
        this.exceptionHandler = exceptionHandler;
    }

    private void registerParser(ResourceManager resourceManager) {
		resourceManager.registerParser(XpandUtil.TEMPLATE_EXTENSION, new ResourceParser() {

			public Resource parse(Reader in, String fileName) {
				return XpandParseFacade.file(in, fileName);
			}});
	}

    @Override
    public ExecutionContextImpl cloneContext() {
        final XpandExecutionContextImpl result = new XpandExecutionContextImpl (resourceManager, currentResource(), typeSystem, getVisibleVariables(), getGlobalVariables(), output, 
                protectedRegionResolver, getMonitor(), exceptionHandler,registeredExtensionAdvices, nullEvaluationHandler,allExtensionsPerResource, callback,this.extensionsForNameAndTypesCache, this.extensionsReturnTypeCache);
        result.registeredAdvices.addAll(registeredAdvices); //todo: [aha] before I refactored, there was an assignment in this place. Is this modification correct?
        return result;
    }
    
    public List<XpandDefinition> getAllDefinitions() {
        XpandResource tpl = null;
            tpl = (XpandResource) currentResource();
        if (tpl == null)
            return null;
        
        XpandDefinition[] localDefinitions = tpl.getDefinitions();
        
        List<XpandDefinition> advicedDefinitions = new ArrayList<XpandDefinition>(localDefinitions.length);
        
        for (int i = 0; i < localDefinitions.length; i++) {
			XpandDefinition xpandDefinition = localDefinitions[i];
			for (int x = registeredAdvices.size() - 1; x >= 0; x--) {
				final XpandAdvice adv = registeredAdvices.get(x);
				if (adv.matches(xpandDefinition, this)) {
					xpandDefinition = new AdvicedDefinition(adv, xpandDefinition);
				}
			}
			advicedDefinitions.add(xpandDefinition);
		}
        
        return advicedDefinitions;
    	
    }

    public XpandDefinition findDefinition(final String name, final Type target, final Type[] paramTypes) {
        XpandResource tpl = null;
        if (name.indexOf(SyntaxConstants.NS_DELIM) != -1) { // local call
            tpl = findTemplate(XpandUtil.withoutLastSegment(name));
        } else {
            tpl = (XpandResource) currentResource();
        }
        if (tpl == null)
            return null;
        final XpandExecutionContext ctx = (XpandExecutionContext) cloneWithResource(tpl);
        XpandDefinition def = findDefinition(tpl.getDefinitions(), name, target, paramTypes, ctx);
        if (def != null) {
	        for (int x = registeredAdvices.size() - 1; x >= 0; x--) {
	            final XpandAdvice adv = registeredAdvices.get(x);
	            if (adv.matches(def, this)) {
	                def = new AdvicedDefinition(adv, def);
	            }
	        }
        }
        return def;
    }

    public void registerAdvices(final String fullyQualifiedName) {
        final XpandResource tpl = findTemplate(fullyQualifiedName);
        if (tpl == null)
            throw new NoSuchTemplateException(fullyQualifiedName);
        final XpandAdvice[] as = tpl.getAdvices();
        for (int i = 0; i < as.length; i++) {
            final XpandAdvice advice = as[i];
            if (registeredAdvices.contains(advice)) {
                log.warn("advice " + advice.toString() + " allready registered!");
            } else {
                registeredAdvices.add(advice);
            }
        }
    }

    public ProtectedRegionResolver getProtectedRegionResolver() {
        return protectedRegionResolver;
    }

    public Output getOutput() {
        return output;
    }

    public XpandResource findTemplate(final String templateName) {
        return findTemplate(templateName, getImportedNamespaces());
    }
        
    public XpandResource findTemplate(final String templateName, String[] importedNs) {
        final List<?> possibleNames = typeSystem.getPossibleNames(templateName, importedNs);
        for (final Iterator<?> iter = possibleNames.iterator(); iter.hasNext();) {
            final String element = (String) iter.next();
            final XpandResource tpl = (XpandResource) resourceManager.loadResource(element,
                    XpandUtil.TEMPLATE_EXTENSION);
            if (tpl != null)
                return tpl;
        }
        return null;
    }

    /**
     * resolves the correct definition (using parametric polymorphism)
     * 
     * @param definitions
     * @param target
     * @param paramTypes
     * @return
     */
    private XpandDefinition findDefinition(final XpandDefinition[] definitions, final String name, final Type target,
            Type[] paramTypes, final XpandExecutionContext ctx) {
        if (paramTypes == null) {
            paramTypes = new Type[0];
        }
        final Set<Callable> features = new HashSet<Callable>();
        for (int i = 0; i < definitions.length; i++) {
            final XpandDefinition def = definitions[i];
            if (def.getParams().length == paramTypes.length) {
                final List<Type> defsParamTypes = new ArrayList<Type>();
                Type t = null;
                boolean complete = true;
                for (int j = 0; j < paramTypes.length && complete; j++) {
                    t = ctx.getTypeForName(def.getParams()[j].getType().getValue());
                    if (t == null) {
                        complete = false;
                    }
                    defsParamTypes.add(t);
                }
                t = ctx.getTypeForName(def.getTargetType());
                if (t == null) {
                    complete = false;
                }
                if (complete) {
                    features.add(new DefinitionOperationAdapter(def, def.getName(), t, defsParamTypes));
                }
            }
        }
        final DefinitionOperationAdapter defAdapter = (DefinitionOperationAdapter) PolymorphicResolver.getOperation(
                features, XpandUtil.getLastSegment(name), target, Arrays.asList(paramTypes));
        if (defAdapter != null)
            return defAdapter.def;
        return null;
    }

    public class DefinitionOperationAdapter implements Operation {

		private String name;

        private Type owner;

        private List<Type> paramTypes;

        public XpandDefinition def;

        public DefinitionOperationAdapter(final XpandDefinition def, final String name, final Type owner,
                final List<Type> paramTypes) {
            this.name = name;
            this.owner = owner;
            this.paramTypes = paramTypes;
            this.def = def;
        }

        public String getName() {
            return name;
        }

        public Type getReturnType() {
            throw new UnsupportedOperationException();
        }

        public Type getOwner() {
            return owner;
        }

        public List<Type> getParameterTypes() {
            return paramTypes;
        }

        public Object evaluate(final Object target, final Object[] params) {
            throw new UnsupportedOperationException();
        }

        public String getDocumentation() {
            return "Xpand definition " + getName() + " adapted in an Operation";
        }

        public Type getReturnType(final Type targetType, final Type[] paramTpes) {
            return getReturnType();
        }

    }

    /**
     * @deprecated Context must be immutable, use the existing constructors
     */
    @Deprecated
	public void setResourceManager(ResourceManager resourceManager) {
        throw new UnsupportedOperationException("Context must be immutable, use the existing constructors");
	}
}
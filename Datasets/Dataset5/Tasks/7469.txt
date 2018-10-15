log.warn("advice " + around.toString() + " already registered!");

/*******************************************************************************
 * Copyright (c) 2005, 2007 committers of openArchitectureWare and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     committers of openArchitectureWare - initial API and implementation
 *******************************************************************************/

package org.eclipse.xtend.expression;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.eclipse.emf.mwe.core.monitor.ProgressMonitor;
import org.eclipse.internal.xtend.expression.ast.DeclaredParameter;
import org.eclipse.internal.xtend.expression.ast.Identifier;
import org.eclipse.internal.xtend.expression.ast.SyntaxElement;
import org.eclipse.internal.xtend.type.baseimpl.PolymorphicResolver;
import org.eclipse.internal.xtend.type.baseimpl.TypesComparator;
import org.eclipse.internal.xtend.xtend.XtendFile;
import org.eclipse.internal.xtend.xtend.ast.Around;
import org.eclipse.internal.xtend.xtend.ast.Extension;
import org.eclipse.internal.xtend.xtend.ast.ExtensionFile;
import org.eclipse.internal.xtend.xtend.types.AdviceContext;
import org.eclipse.xtend.typesystem.MetaModel;
import org.eclipse.xtend.typesystem.Operation;
import org.eclipse.xtend.typesystem.Property;
import org.eclipse.xtend.typesystem.Type;

/**
 * @author Sven Efftinge (http://www.efftinge.de)
 * @author Arno Haase
 * @author Peter Friese
 */
public class ExecutionContextImpl implements ExecutionContext {
	private final static Log log = LogFactory.getLog(ExecutionContextImpl.class);

	protected final ResourceManager resourceManager;

	private final Map<String, Variable> variables = new HashMap<String, Variable>();

	private final Map<String, Variable> globalVars = new HashMap<String, Variable>();

	private ProgressMonitor monitor;

	/**
	 * this field is conceptually final, i.e. it is set only at object
	 * construction time. To simplify implementation, it is however technically
	 * not final. This is done so that the cloneWith/WithoutResource methods can
	 * delegate to cloneContext and afterwards modify the instance. That
	 * provides cloneContext as a single method for subclasses to override.
	 */
	private Resource currentResource;

	protected final TypeSystemImpl typeSystem;

	protected ExceptionHandler exceptionHandler;

	protected NullEvaluationHandler nullEvaluationHandler = null;

	public ExecutionContextImpl() {
		this((Map<String, Variable>) null);
	}

	public ExecutionContextImpl(TypeSystemImpl ts) {
		this(ts, null);
	}

	public ExecutionContextImpl(Map<String, Variable> globalVars) {
		this(new ResourceManagerDefaultImpl(), null, new TypeSystemImpl(), new HashMap<String, Variable>(), globalVars, null,
				null, null, null, null);
	}

	public ExecutionContextImpl(TypeSystemImpl ts, Map<String, Variable> globalVars) {
		this(new ResourceManagerDefaultImpl(), null, ts, new HashMap<String, Variable>(), globalVars, null, null, null, null,
				null);
	}

	public ExecutionContextImpl(ResourceManager resourceManager, TypeSystemImpl typeSystem, Map<String, Variable> globalVars) {
		this(resourceManager, null, typeSystem, new HashMap<String, Variable>(), globalVars, null, null, null, null, null);
	}

	public ExecutionContextImpl(ResourceManager resourceManager, Resource resource, TypeSystemImpl typeSystem,
			Map<String, Variable> variables, Map<String, Variable> globalVars, ProgressMonitor monitor,
			ExceptionHandler exceptionHandler, List<Around> advices, NullEvaluationHandler neh2,
			Map<Resource, Set<Extension>> extensionPerResourceMap) {
		if (extensionPerResourceMap != null) {
			this.allExtensionsPerResource = extensionPerResourceMap;
		} else {
			this.allExtensionsPerResource = new HashMap<Resource, Set<Extension>>();
		}
		this.resourceManager = resourceManager;
		this.currentResource = resource;
		this.typeSystem = typeSystem;
		this.variables.putAll(variables);
		if (globalVars != null) {
			this.globalVars.putAll(globalVars);
		}
		this.monitor = monitor;
		this.exceptionHandler = exceptionHandler;
		if (advices != null) {
			registeredExtensionAdvices = advices;
		}

		this.nullEvaluationHandler = neh2;
	}

	public void registerMetaModel(final MetaModel mm) {
		typeSystem.registerMetaModel(mm);
	}

	public Operation findOperation(final String name, final Object target, final Object[] params) {
		return typeSystem.findOperation(name, target, params);
	}

	public Property findProperty(final String name, final Object target) {
		return typeSystem.findProperty(name, target);
	}

	public Type[] findTypesForPrefix(final String prefix) {
		return typeSystem.findTypesForPrefix(prefix, getImportedNamespaces());
	}

	public Type[] getAllTypes() {
		return typeSystem.getAllTypes();
	}

	public Set<String> getNamespaces() {
		return typeSystem.getNamespaces();
	}

	public Type getBooleanType() {
		return typeSystem.getBooleanType();
	}

	public Type getCollectionType(final Type innerType) {
		return typeSystem.getCollectionType(innerType);
	}

	public Type getFeatureType() {
		return typeSystem.getFeatureType();
	}

	public Type getIntegerType() {
		return typeSystem.getIntegerType();
	}

	public Type getListType(final Type innerType) {
		return typeSystem.getListType(innerType);
	}

	public Type getObjectType() {
		return typeSystem.getObjectType();
	}

	public Type getOperationType() {
		return typeSystem.getOperationType();
	}

	public Type getPropertyType() {
		return typeSystem.getPropertyType();
	}

	public Type getRealType() {
		return typeSystem.getRealType();
	}

	public Type getSetType(final Type innerType) {
		return typeSystem.getSetType(innerType);
	}

	public Type getStaticPropertyType() {
		return typeSystem.getStaticPropertyType();
	}

	public Type getStringType() {
		return typeSystem.getStringType();
	}

	public Type getType(final Object obj) {
		return typeSystem.getType(obj);
	}

	public Type getTypeForName(final String name) {
		return typeSystem.getTypeForName(name, getImportedNamespaces());
	}

	protected String[] getImportedNamespaces() {
		return currentResource != null ? currentResource.getImportedNamespaces() : new String[0];
	}

	public Type getTypeType() {
		return typeSystem.getTypeType();
	}

	public Type getVoidType() {
		return typeSystem.getVoidType();
	}

	public ExecutionContextImpl cloneContext() {
		return new ExecutionContextImpl(resourceManager, currentResource, typeSystem, variables, globalVars, monitor,
				exceptionHandler, registeredExtensionAdvices, nullEvaluationHandler, allExtensionsPerResource);
	}

	public void setFileEncoding(final String encoding) {
		if (resourceManager != null) {
			resourceManager.setFileEncoding(encoding);
		}
	}

	public Variable getVariable(final String name) {
		return variables.get(name);
	}

	public Map<String, Variable> getVisibleVariables() {
		return Collections.unmodifiableMap(variables);
	}

	public Map<String, Variable> getGlobalVariables() {
		return Collections.unmodifiableMap(globalVars);
	}

	public ExecutionContext cloneWithVariable(final Variable v) {
		final ExecutionContextImpl result = cloneContext();
		result.variables.put(v.getName(), v);
		return result;
	}

	public ExecutionContext cloneWithoutVariables() {
		final ExecutionContextImpl result = cloneContext();
		result.variables.clear();
		return result;
	}

	public ExecutionContext cloneWithResource(final Resource ns) {
		final ExecutionContextImpl ctx = cloneContext();
		ctx.currentResource = ns;
		return ctx;
	}

	public ExecutionContext cloneWithoutResource() {
		final ExecutionContextImpl ctx = cloneContext();
		ctx.currentResource = null;
		return ctx;
	}

	public ExecutionContext cloneWithoutMonitor() {
		final ExecutionContextImpl ctx = cloneContext();
		ctx.setMonitor(null);
		return ctx;
	}

	public Resource currentResource() {
		return currentResource;
	}

	protected Map<Resource, Set<Extension>> allExtensionsPerResource = null;

	public Set<? extends Extension> getAllExtensions() {
		Set<Extension> allExtensions = allExtensionsPerResource.get(currentResource());
		if (allExtensions == null) {
			allExtensions = new HashSet<Extension>();
			final Resource res = currentResource();
			if (res != null) {
				if (res instanceof XtendFile) {
					final List<Extension> extensionList = ((XtendFile) res).getExtensions();
					for (Extension element : extensionList) {
						element.init(this);
						allExtensions.add(advise(element));
					}
				}
				final String[] extensions = res.getImportedExtensions();
				for (final String extension : extensions) {
					final Object o = resourceManager.loadResource(extension, XtendFile.FILE_EXTENSION);
					final XtendFile extFile = (XtendFile) o;
					if (extFile == null) {
						throw new RuntimeException("Unable to load extension file : " + extension);
					}
					final ExecutionContext ctx = cloneWithResource(extFile);
					final List<Extension> extensionList = extFile.getPublicExtensions(resourceManager, ctx);
					for (final Extension element : extensionList) {
						element.init(ctx);
						allExtensions.add(advise(element));
					}
				}
			}
			allExtensionsPerResource.put(currentResource(), allExtensions);
		}
		return allExtensions;
	}

	public Extension getExtensionForTypes(final String functionName, final Type[] parameterTypes) {
		return PolymorphicResolver.getExtension(getAllExtensions(), functionName, Arrays.asList(parameterTypes));
	}

	public Extension getExtension(final String functionName, final Object[] actualParameters) {
		final Type[] types = new Type[actualParameters.length];
		for (int i = 0; i < types.length; i++) {
			types[i] = getType(actualParameters[i]);
		}
		return getExtensionForTypes(functionName, types);
	}

	public void setMonitor(ProgressMonitor monitor) {
		this.monitor = monitor;
	}

	public ProgressMonitor getMonitor() {
		return monitor;
	}

	public void preTask(Object element) {
		if (monitor == null) {
			return;
		}
		monitor.preTask(element, this);
	}

	public void postTask(Object element) {
		if (monitor == null) {
			return;
		}
		monitor.postTask(element, this);
	}

	public void handleRuntimeException(RuntimeException ex, SyntaxElement element, Map<String, Object> additionalContextInfo) {
		if (this.exceptionHandler == null) {
			throw ex;
		}
		exceptionHandler.handleRuntimeException(ex, element, this, additionalContextInfo);
	}

	public ResourceManager getResourceManager() {
		return this.resourceManager;
	}

	protected List<Around> registeredExtensionAdvices = new ArrayList<Around>();

	public void registerExtensionAdvices(final String fullyQualifiedName) {
		final XtendFile ext = (XtendFile) resourceManager.loadResource(fullyQualifiedName, XtendFile.FILE_EXTENSION);
		if (ext == null) {
			throw new IllegalArgumentException("Couldn't find extension file '" + fullyQualifiedName + "'");
		}
		final List<Around> as = ext.getArounds();
		for (Around around : as) {
			if (registeredExtensionAdvices.contains(around)) {
				log.warn("advice " + around.toString() + " allready registered!");
			} else {
				registeredExtensionAdvices.add(around);
			}
		}
	}

	public List<Around> getExtensionAdvices() {
		return registeredExtensionAdvices;
	}

	private final TypesComparator typesComparator = new TypesComparator();

	private Extension advise(Extension element) {
		if (!getExtensionAdvices().isEmpty()) {
			for (Around a : getExtensionAdvices()) {
				if (a.nameMatches(element.getQualifiedName())) {
					List<Type> paramTypes = a.getParamTypes(this);
					List<Type> extPTypes = element.getParameterTypes();
					int diff = extPTypes.size() - paramTypes.size();
					if (diff >= 0) {
						if (diff > 0 && a.isWildparams()) { // fill wildcard
							// params with
							// Object types
							for (int i = 0; i < diff; i++) {
								paramTypes.add(getObjectType());
							}
						}
						if (typesComparator.compare(paramTypes, extPTypes) >= 0) {
							element = new ExtensionAdvisor(a, element);
						}
					}
				}
			}
		}
		return element;
	}

	class ExtensionAdvisor implements Extension {

		private final Extension delegate;

		private final Around advice;

		public ExtensionAdvisor(Around advice, Extension delegate) {
			this.delegate = delegate;
			this.advice = advice;
		}

		public Object evaluate(Object[] parameters, ExecutionContext ctx) {

			ctx = ctx.cloneWithVariable(new Variable(Around.CONTEXT_PARAM_NAME, new AdviceContext(delegate, ctx, parameters)));
			for (int i = 0; i < advice.getParams().size(); i++) {
				ctx = ctx.cloneWithVariable(new Variable(advice.getParams().get(i).getName().getValue(), parameters[i]));
			}
			ctx = ctx.cloneWithResource(advice.getParent());
			return advice.getExpression().evaluate(ctx);
		}

		public void analyze(ExecutionContext ctx, Set<AnalysationIssue> issues) {
			delegate.analyze(ctx, issues);
		}

		public int getEnd() {
			return delegate.getEnd();
		}

		public ExtensionFile getExtensionFile() {
			return delegate.getExtensionFile();
		}

		public String getFileName() {
			return delegate.getFileName();
		}

		public List<DeclaredParameter> getFormalParameters() {
			return delegate.getFormalParameters();
		}

		public int getLine() {
			return delegate.getLine();
		}

		public String getName() {
			return delegate.getName();
		}

		public List<String> getParameterNames() {
			return delegate.getParameterNames();
		}

		public List<Type> getParameterTypes() {
			return delegate.getParameterTypes();
		}

		public Type getReturnType(Type[] parameters, ExecutionContext ctx, Set<AnalysationIssue> issues) {
			return delegate.getReturnType(parameters, ctx, issues);
		}

		public Type getReturnType() {
			return delegate.getReturnType();
		}

		public Identifier getReturnTypeIdentifier() {
			return delegate.getReturnTypeIdentifier();
		}

		public int getStart() {
			return delegate.getStart();
		}

		public String getNameString(ExecutionContext context) {
			return delegate.getNameString(context);
		}

		public void init(ExecutionContext ctx) {
			delegate.init(ctx);
		}

		public boolean isCached() {
			return delegate.isCached();
		}

		public boolean isPrivate() {
			return delegate.isPrivate();
		}

		public void setExtensionFile(ExtensionFile file) {
			delegate.setExtensionFile(file);
		}

		public String toOutlineString() {
			return delegate.toOutlineString();
		}

		@Override
		public String toString() {
			return delegate.toString();
		}

		public String getQualifiedName() {
			return delegate.getQualifiedName();
		}

	}

	public Object handleNullEvaluation(SyntaxElement element) {
		if (nullEvaluationHandler != null) {
			return nullEvaluationHandler.handleNullEvaluation(element, this);
		}
		return null;
	}

	public void release() {
		typeSystem.release();
	}

}
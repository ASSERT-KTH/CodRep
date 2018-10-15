baseType = element.getEClassifier();

/*******************************************************************************
 * Copyright (c) 2005, 2009 committers of openArchitectureWare and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     committers of openArchitectureWare - initial API and implementation
 *     QNX Software Systems - No lookup of EDataTypeTypes in getType(Object)
 *******************************************************************************/

package org.eclipse.xtend.typesystem.emf;

import java.util.Collection;
import java.util.HashSet;
import java.util.Iterator;
import java.util.Set;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.eclipse.emf.common.util.EList;
import org.eclipse.emf.common.util.Enumerator;
import org.eclipse.emf.ecore.EClass;
import org.eclipse.emf.ecore.EClassifier;
import org.eclipse.emf.ecore.EDataType;
import org.eclipse.emf.ecore.EEnum;
import org.eclipse.emf.ecore.EEnumLiteral;
import org.eclipse.emf.ecore.EGenericType;
import org.eclipse.emf.ecore.ENamedElement;
import org.eclipse.emf.ecore.EObject;
import org.eclipse.emf.ecore.EPackage;
import org.eclipse.emf.ecore.ETypedElement;
import org.eclipse.emf.ecore.EcorePackage;
import org.eclipse.emf.ecore.resource.ResourceSet;
import org.eclipse.emf.ecore.util.EcoreUtil;
import org.eclipse.emf.mwe.utils.SingleGlobalResourceSet;
import org.eclipse.internal.xtend.expression.parser.SyntaxConstants;
import org.eclipse.internal.xtend.type.baseimpl.BuiltinMetaModel;
import org.eclipse.internal.xtend.util.Cache;
import org.eclipse.xtend.expression.TypeSystem;
import org.eclipse.xtend.type.impl.java.JavaBeansMetaModel;
import org.eclipse.xtend.type.impl.java.JavaTypeImpl;
import org.eclipse.xtend.typesystem.MetaModel;
import org.eclipse.xtend.typesystem.Type;

public class EmfRegistryMetaModel implements MetaModel {

	private final Log log = LogFactory.getLog(getClass());

	TypeSystem typeSystem;

	private EObjectType eobjectType = null;
	
	// Used to resolve Java based datatypes.
	private JavaBeansMetaModel internalJbmm = new JavaBeansMetaModel();
	
	public EObjectType getEobjectType() {
		return eobjectType;
	}

	private final Cache<EObject, Type> cache = new Cache<EObject, Type>() {

		@Override
		protected Type createNew(EObject param) {
			if (param == null) {
				return null;
			}
			if (param instanceof EGenericType) {
				EGenericType genericType = (EGenericType) param;
				if (typeSystem != null) {
					Type innerType = getTypeForEClassifier(genericType.getETypeArguments().get(0));
					return new EmfListType(innerType, typeSystem, BuiltinMetaModel.LIST);
				}
				else {
					param = genericType.getEClassifier();
				}
			}

			if (!(param instanceof EClassifier))
				return null;

			EClassifier ele = (EClassifier) param;

			if (ele.getName() == null) {
				return null;
			}

			if (ele instanceof EClass) {
				return new EClassType(EmfRegistryMetaModel.this, getFullyQualifiedName(ele), (EClass) ele);
			}
			else if (ele instanceof EEnum) {
				return new EEnumType(EmfRegistryMetaModel.this, getFullyQualifiedName(ele), (EEnum) ele);
			}
			else if (ele instanceof EDataType) {
				if (typeSystem != null) {
					if (stringTypes.contains(ele)) {
						return typeSystem.getStringType();
					}
					else if (booleanTypes.contains(ele)) {
						return typeSystem.getBooleanType();
					}
					else if (intTypes.contains(ele)) {
						return typeSystem.getIntegerType();
					}
					else if (realTypes.contains(ele)) {
						return typeSystem.getRealType();
					}
					else if (objectTypes.contains(ele)) {
						return typeSystem.getObjectType();
					}
					else if (listTypes.contains(ele)) {
						return new EmfListType(typeSystem.getObjectType(), typeSystem, BuiltinMetaModel.LIST);
					}
				}
				EDataType dataType = (EDataType) ele;
				if (dataType.getInstanceClassName()!=null) {
					// fall back to qualified Java name for EDatatypes
					Type t = internalJbmm.getTypeForName(dataType.getInstanceClassName().replace(".", "::"));
					if (t == null) {
						// for primitives
						t = typeSystem.getTypeForName(dataType.getInstanceClassName().replace(".", "::"));
					}
					return t;
				} else {
					return typeSystem.getObjectType();
				}
			}
			return null;
		}

	};

	private final HashSet<EClassifier> stringTypes;

	private final HashSet<EClassifier> intTypes;

	private final HashSet<EClassifier> realTypes;

	private final HashSet<EClassifier> booleanTypes;

	private final HashSet<EClassifier> objectTypes;

	private final HashSet<EClassifier> listTypes;

	public void setUseSingleGlobalResourceSet(boolean b) {
		if (b) {
			addResourceSet(SingleGlobalResourceSet.get());
		}
	}

	public void setTypeSystem(final TypeSystem typeSystem) {
		this.typeSystem = typeSystem;
		this.internalJbmm.setTypeSystem(typeSystem);
		if (eobjectType == null) {
			eobjectType = new EObjectType(getTypeSystem());
		}
	}

	public EmfRegistryMetaModel() {
		stringTypes = new HashSet<EClassifier>();
		stringTypes.add(EcorePackage.eINSTANCE.getEString());
		stringTypes.add(EcorePackage.eINSTANCE.getEChar());
		stringTypes.add(EcorePackage.eINSTANCE.getECharacterObject());

		booleanTypes = new HashSet<EClassifier>();
		booleanTypes.add(EcorePackage.eINSTANCE.getEBoolean());
		booleanTypes.add(EcorePackage.eINSTANCE.getEBooleanObject());

		intTypes = new HashSet<EClassifier>();
		intTypes.add(EcorePackage.eINSTANCE.getEInt());
		intTypes.add(EcorePackage.eINSTANCE.getEIntegerObject());
		intTypes.add(EcorePackage.eINSTANCE.getELong());
		intTypes.add(EcorePackage.eINSTANCE.getELongObject());
		intTypes.add(EcorePackage.eINSTANCE.getEShort());
		intTypes.add(EcorePackage.eINSTANCE.getEShortObject());
		intTypes.add(EcorePackage.eINSTANCE.getEByte());
		intTypes.add(EcorePackage.eINSTANCE.getEByteObject());
		intTypes.add(EcorePackage.eINSTANCE.getEBigInteger());

		realTypes = new HashSet<EClassifier>();
		realTypes.add(EcorePackage.eINSTANCE.getEFloat());
		realTypes.add(EcorePackage.eINSTANCE.getEFloatObject());
		realTypes.add(EcorePackage.eINSTANCE.getEDouble());
		realTypes.add(EcorePackage.eINSTANCE.getEDoubleObject());
		realTypes.add(EcorePackage.eINSTANCE.getEBigDecimal());

		objectTypes = new HashSet<EClassifier>();
		objectTypes.add(EcorePackage.eINSTANCE.getEJavaObject());

		listTypes = new HashSet<EClassifier>();
		listTypes.add(EcorePackage.eINSTANCE.getEEList());
	}

	private final Cache<String, Type> typeForNameCache = new Cache<String, Type>() {
		@Override
		protected Type createNew(String typeName) {

			if (typeName.equals(eobjectType.getName())) {
				return eobjectType;
			}
			Set<ENamedElement> ele = getNamedElementRec(allPackages(), typeName);
			if (ele.size() > 1) {
				boolean classifiers = true;
				for (ENamedElement element : ele) {
					classifiers = classifiers && element instanceof EClassifier;
				}
				if (classifiers) {
					log.warn("Multiple types (" + ele.size() + ") with name " + typeName + " found!");
				}
			}
			if (ele.isEmpty()) {
				return null;
			}
			ENamedElement type = ele.iterator().next();
			if (type instanceof EClassifier) {
				return cache.get(type);
			}
			return null;
		}

	};

	private EPackage[] _allPackages;

	/**
	 * returns the managed packages. Uses the global EPackage Registry.
	 * 
	 * @return
	 */
	protected EPackage[] allPackages() {
		if (_allPackages != null) {
			return _allPackages;
		}

		Set<EPackage> packages = new HashSet<EPackage>();
		for (String name : new HashSet<String>(EPackage.Registry.INSTANCE.keySet())) {
			try {
				packages.add(EPackage.Registry.INSTANCE.getEPackage(name));
			}
			catch (Exception e) {
				log.error(e, e);
			}
		}
		for (ResourceSet rs : resourceSets) {
			for (String name : rs.getPackageRegistry().keySet()) {
				try {
					packages.add(rs.getPackageRegistry().getEPackage(name));
				}
				catch (Exception e) {
					log.error(e, e);
				}
			}
		}
		_allPackages = packages.toArray(new EPackage[packages.size()]);
		return _allPackages;
	}

	private final Set<ResourceSet> resourceSets = new HashSet<ResourceSet>();

	public void addResourceSet(ResourceSet rs) {
		this.resourceSets.add(rs);
	}

	public Type getTypeForName(final String typeName) {
		return typeForNameCache.get(typeName);
	}

	private Set<ENamedElement> getNamedElementRec(final ENamedElement[] elements, final String name) {
		Set<ENamedElement> result = new HashSet<ENamedElement>();
		final String[] frags = name.split(SyntaxConstants.NS_DELIM);
		final String firstFrag = frags[0];
		for (final ENamedElement ele : elements) {
			final String eleName = getElementName(ele);
			if (eleName != null && eleName.equals(firstFrag)) {
				if (frags.length > 1) {
					final Collection<ENamedElement> children = EcoreUtil.getObjectsByType(ele.eContents(),
							EcorePackage.eINSTANCE.getENamedElement());

					result.addAll(getNamedElementRec(children.toArray(new ENamedElement[children.size()]), name
							.substring(name.indexOf(SyntaxConstants.NS_DELIM) + SyntaxConstants.NS_DELIM.length())));
				}
				else {
					result.add(ele);
				}
			}
		}
		return result;
	}

	public Type getType(final Object obj) {
		if (obj instanceof EObject) {
			if (obj instanceof EEnumLiteral && ((EEnumLiteral) obj).getName() != null
					&& ((EEnumLiteral) obj).getEEnum() != null) {
				final EEnumLiteral el = (EEnumLiteral) obj;
				return getTypeForEClassifier(el.getEEnum());
			}
			final EClass clazz = ((EObject) obj).eClass();
			return getTypeForEClassifier(clazz);
		}

		final Set<Type> types = getKnownTypes();
		if (obj instanceof Enumerator) {
			for (Type t : types) {
				// check for EEnumType because the EDataTypeType for
				// ecore::EEnumerator matches all enumerator instances
				if (t instanceof EEnumType) {
					if (t.isInstance(obj)) {
						return t;
					}
				}
			}
		}

		return null;
	}

	private Set<Type> knownTypes = null;

	public Set<Type> getKnownTypes() {
		if (knownTypes == null) {
			final Set<Type> result = new HashSet<Type>();
			result.add(eobjectType);
			for (EPackage pack : allPackages()) {
				for (final Iterator<EObject> iter = pack.eAllContents(); iter.hasNext();) {
					final Object obj = iter.next();
					if (obj instanceof EClassifier) {
						try {
							Type t = getTypeForEClassifier((EClassifier) obj);
							if (t != null && !(t instanceof JavaTypeImpl))
								result.add(t);
						}
						catch (RuntimeException e) {
							// TODO Auto-generated catch block
							e.printStackTrace();
						}
					}
				}
			}
			knownTypes = result;
			return result;
		}
		return knownTypes;
	}

	public Type getTypeForEClassifier(final EClassifier element) {
		if (element == null) {
			return getTypeSystem().getVoidType();
		}
		return cache.get(element);
	}

	public Type getTypeForEClassifier(final EGenericType element) {
		EClassifier baseType = null;
		if (element.getEClassifier() != null) {
			baseType = element.getEClassifier();;
		} else {
			baseType = element.getERawType();
		}
		
		if ((baseType == null) || !listTypes.contains(baseType))
			return getTypeForEClassifier(baseType);

		if (element.getETypeArguments().size() != 1)
			throw new RuntimeException("Unexpected number of type arguments");

		return cache.get(element);
	}

	public Type getTypeForETypedElement(final ETypedElement typedElement) {
		if (typedElement.getEType() == null) {
			return getTypeSystem().getVoidType();
		}
		Type t = null;
		if (typedElement.getEType() instanceof EDataType) {
			if (typedElement.getEGenericType() != null) {
				t = getTypeForEClassifier(typedElement.getEGenericType());
			} else {
				t = getTypeForEClassifier(typedElement.getEType());
			}
		}
		else {
			if (typedElement.getEGenericType() != null) {
				t = getTypeForEClassifier(typedElement.getEGenericType());
			} else {
				t = getTypeSystem().getTypeForName(getFullyQualifiedName(typedElement.getEType()));
			}
		}
		if (typedElement.isMany())
			return new EmfListType(t, typeSystem, BuiltinMetaModel.LIST);
		else
			return t;
	}

	public TypeSystem getTypeSystem() {
		return typeSystem;
	}

	public String getFullyQualifiedName(final ENamedElement ele) {
		return getFqnRec(ele.eContainer(), getElementName(ele));
	}

	protected String getFqnRec(final EObject ele, final String suffix) {
		if (ele == null || !(ele instanceof ENamedElement)) {
			return suffix;
		}
		else {
			return getFqnRec(ele.eContainer(), getElementName((ENamedElement) ele) + SyntaxConstants.NS_DELIM + suffix);
		}
	}

	private void traversePackage(final String parentNamespace, final Set<String> namespaces, final EPackage thePackage) {
		StringBuilder sb = new StringBuilder();
		if (parentNamespace != null) {
			sb.append(parentNamespace);
			sb.append("::");
		}

		sb.append(getElementName(thePackage));

		String namespace = sb.toString();
		namespaces.add(namespace);

		EList<EPackage> subpackages = thePackage.getESubpackages();
		for (EPackage subPackage : subpackages) {
			traversePackage(namespace, namespaces, subPackage);
		}
	}

	public Set<String> getNamespaces() {
		Set<String> result = new HashSet<String>();
		EPackage[] allPackages = allPackages();
		for (EPackage thePackage : allPackages) {
			traversePackage(null, result, thePackage);
		}
		return result;
	}

	protected String getElementName(ENamedElement ele) {
		return ele == null ? null : ele.getName();
	}
}
 No newline at end of file
final BackendType backendType = (attrib.isMultivalued()) ? CollectionType.INSTANCE : umlTs.getTypeForStereotypeProperty (umlType);

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
package org.eclipse.xtend.backend.types.uml2.internal;

import java.util.ArrayList;
import java.util.Collection;
import java.util.HashSet;
import java.util.List;

import org.apache.commons.logging.LogFactory;
import org.eclipse.emf.common.util.EList;
import org.eclipse.emf.common.util.URI;
import org.eclipse.emf.ecore.EClass;
import org.eclipse.emf.ecore.EObject;
import org.eclipse.emf.ecore.EStructuralFeature;
import org.eclipse.emf.ecore.InternalEObject;
import org.eclipse.emf.ecore.util.EcoreUtil;
import org.eclipse.uml2.uml.Classifier;
import org.eclipse.uml2.uml.Element;
import org.eclipse.uml2.uml.Generalization;
import org.eclipse.uml2.uml.Property;
import org.eclipse.uml2.uml.Stereotype;
import org.eclipse.uml2.uml.Type;
import org.eclipse.xtend.backend.common.BackendType;
import org.eclipse.xtend.backend.common.BackendTypesystem;
import org.eclipse.xtend.backend.common.ExecutionContext;
import org.eclipse.xtend.backend.types.AbstractProperty;
import org.eclipse.xtend.backend.types.AbstractType;
import org.eclipse.xtend.backend.types.builtin.CollectionType;
import org.eclipse.xtend.backend.types.uml2.UmlTypesystem;


/**
 * 
 * @author Arno Haase (http://www.haase-consulting.com)
 * @author André Arnold
 */
public final class StereotypeType extends AbstractType {
    private final Stereotype _stereoType;
    
    public StereotypeType (String name, Stereotype stereoType, UmlTypesystem umlTs) {
        super (name, name, superTypes (umlTs, stereoType).toArray (new BackendType[0])); //TODO uniqueRepresentation
        _stereoType = stereoType;
        
        for (StereotypeProperty stp: getProperties (this, stereoType, umlTs))
            register (stp, stp.getType (umlTs));
    }

    
    private Collection<StereotypeProperty> getProperties (BackendType owningType, Stereotype stereoType, UmlTypesystem umlTs) {
        final Collection<StereotypeProperty> result = new HashSet<StereotypeProperty> ();
        
        for (Property attrib: stereoType.getAttributes()) {
            if (attrib.getName() == null)
                continue;

            UmlTypesystem.fixName (attrib);
            
            final Type umlType = getTypeResolveProxy (attrib);
            if (umlType.getQualifiedName() == null) {
                LogFactory.getLog (owningType.getClass ()).error ("qualified name is null for element " + attrib.getQualifiedName());
                continue;
            }
            
            final BackendType backendType = (attrib.isMultivalued()) ? CollectionType.INSTANCE : umlTs.findType (umlType);
            result.add (new StereotypeProperty (attrib.getName (), backendType));
        }
        
        return result;
    }

    
    private static Collection<BackendType> superTypes (UmlTypesystem umlTs, Stereotype stereoType) {
        final List<Classifier> all = new ArrayList<Classifier> (stereoType.getExtendedMetaclasses());
        all.addAll (stereoType.getSuperClasses());

        final List<BackendType> result = new ArrayList<BackendType>();
        
        for (Classifier classifier : all) 
            result.add (umlTs.getTypeForEClassifier (classifier.eClass()));

        return result;
    }
    
    
    private Type getTypeResolveProxy (Property p) {
        Type result = p.getType();
        
        if (result.eIsProxy()) {
            final InternalEObject proxy = (InternalEObject) result;
            final URI uri = proxy.eProxyURI();

            result = (Type) EcoreUtil.resolve (proxy, p);

            if (result.eIsProxy()) 
                throw new IllegalStateException ("Couldn't resolve proxy under " + uri);
        }
        
        return result;
    }

    
    @Override
    public int hashCode () {
        final int prime = 31;
        int result = 1;
        result = prime * result + ((_stereoType == null) ? 0 : _stereoType.hashCode());
        return result;
    }

    @Override
    public boolean equals (Object obj) {
        if (this == obj)
            return true;
        if (obj == null)
            return false;
        if (getClass() != obj.getClass())
            return false;
        final StereotypeType other = (StereotypeType) obj;
        if (_stereoType == null) {
            if (other._stereoType != null)
                return false;
        } else if (!_stereoType.equals(other._stereoType))
            return false;
        return true;
    }
    
    
    private final class StereotypeProperty extends AbstractProperty {
        private final BackendType _type;
        
        public StereotypeProperty (String name, BackendType type) {
            super (StereotypeType.this, Object.class, name, true, false);
            _type = type;
        }
        
        @Override
        public Object getRaw (ExecutionContext ctx, Object target) {
            if (target instanceof Element) {
                final Element ele = (Element) target;
                
                for (Stereotype st : ele.getAppliedStereotypes()) {
                    if (isStereoTypeAssignable (st, _stereoType)) {
                        final Object value = ele.getValue (st, getName());

                        // custom datatypes
                        // see Bug#185033
                        if (value instanceof EList) {
                            final EList<?> eList = (EList<?>) value;
                            final Collection<Object> values = new ArrayList<Object>();
                            for (Object dynObject: eList) {
                                final Object dynValue = getDynamicValue(dynObject);
                                if (dynValue != null)
                                    values.add(dynValue);
                            }
                            if (!values.isEmpty ())
                                return values;
                        }
                        else if (value instanceof EObject) {
                            final Object dynValue = getDynamicValue(value);
                            if (dynValue != null)
                                return dynValue;
                        }

                        return value;
                    }
                }
            }
            throw new IllegalArgumentException("uml2 Element expected but was " + target.getClass().getName());
        }
        
        public BackendType getType (BackendTypesystem ts) {
            return _type;
        }
        
        private Object getDynamicValue(final Object value) {
            if (value instanceof EObject) {
                final EObject dynObject = (EObject) value;
                final EClass dynClass = dynObject.eClass();
                final EStructuralFeature baseClassFeature = dynClass.getEStructuralFeature("base_Class");
                
                if(baseClassFeature != null){
                    return dynObject.eGet(baseClassFeature,true);
                }
            }
            return null;
        }
        
        private boolean isStereoTypeAssignable(Stereotype st1, Stereotype st2) {
            if (st1.getQualifiedName().equals(st2.getQualifiedName())) {
                return true;
            }
            List<Generalization> gs = st1.getGeneralizations();
            for (Generalization g : gs) {
                if (g.getGeneral() instanceof Stereotype && isStereoTypeAssignable((Stereotype) g.getGeneral(), st2))
                    return true;
            }
            return false;
        }
    }

}
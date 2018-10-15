return (cache.get(assignable)).contains(toAssigTo);

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

package org.eclipse.xtend.shared.ui.core.metamodel.jdt.oaw;

import org.eclipse.core.runtime.NullProgressMonitor;
import org.eclipse.internal.xtend.util.Cache;
import org.eclipse.internal.xtend.util.StringHelper;
import org.eclipse.jdt.core.Flags;
import org.eclipse.jdt.core.IField;
import org.eclipse.jdt.core.IMethod;
import org.eclipse.jdt.core.IType;
import org.eclipse.jdt.core.ITypeHierarchy;
import org.eclipse.jdt.core.JavaModelException;
import org.eclipse.jdt.core.Signature;
import org.eclipse.xtend.shared.ui.core.metamodel.jdt.JdtTypeStrategy;
import org.eclipse.xtend.shared.ui.internal.XtendLog;

public class JdtOawClassicTypeStrategy implements JdtTypeStrategy {

    public JdtOawClassicTypeStrategy() {
        super();
    }

    public IType[] getSuperTypes(final IType type) throws JavaModelException {
        final ITypeHierarchy hier = type.newSupertypeHierarchy(new NullProgressMonitor());
        final IType[] ifs = hier.getSuperInterfaces(type);
        final IType st = hier.getSuperclass(type);
        if (st == null)
            return ifs;
        final IType[] result = new IType[ifs.length + 1];
        System.arraycopy(ifs, 0, result, 0, ifs.length);
        result[ifs.length] = st;
        return result;
    }

    private final Cache<IType,ITypeHierarchy> cache = new Cache<IType,ITypeHierarchy>() {

        @Override
        protected ITypeHierarchy createNew(IType type) {
            try {
                return type.newSupertypeHierarchy(new NullProgressMonitor());
            } catch (JavaModelException e) {
                XtendLog.logError(e);
                return null;
            }
        }
    };

    public boolean isAssignable(final IType toAssigTo, final IType assignable) {
        return ((ITypeHierarchy) cache.get(assignable)).contains(toAssigTo);
    }

    public boolean isGetter(final IMethod method) {
        int flags;
        try {
            flags = method.getFlags();
        } catch (final JavaModelException e) {
            return false;
        }
        try {
            if (!Flags.isStatic(flags) && method.getParameterTypes().length == 0
                    && !Signature.SIG_VOID.equals(method.getReturnType()))
                return true;
        } catch (final JavaModelException e) {
            XtendLog.logError(e);
        }
        return false;
    }

    public String getterToProperty(final String elementName) {
        return elementName;
    }

    public boolean isOperation(final IMethod method) {
        if (!isGetter(method)) {
            try {
                final int flags = method.getFlags();
                if (!Flags.isStatic(flags)) {
                    if (!method.getElementName().startsWith("set"))
                        return true;
                }
            } catch (final JavaModelException e) {
                return false;
            }
        }
        return false;
    }

    public String propertyName(final IMethod method) {
        return getterToProperty(method.getElementName());
    }

    public String getPropertiesInnerType(final IMethod method) {
        final IType type = method.getDeclaringType();
        IMethod[] methods = null;
        final String adderMethod = "add" + StringHelper.firstUpper(method.getElementName());
        try {
            methods = type.getMethods();
            for (int i = 0; i < methods.length; i++) {
                final IMethod m = methods[i];
                if (m.getParameterTypes().length == 1 && m.getElementName().equals(adderMethod))
                    return m.getParameterTypes()[0];
            }
        } catch (final JavaModelException e) {
            XtendLog.logError(e);
        }
        return null;
    }
    
    public boolean isConstant(IField field) {
		try {
			if (field.isEnumConstant() || field.getDeclaringType().isInterface() || (Flags.isPublic(field.getFlags()) && Flags.isFinal(field.getFlags()) && Flags.isStatic(field.getFlags()))) {
				return true;
			}
		} catch (JavaModelException e) {
			return false;
		}
		return false;
	}

	public String propertyName(IField field) {
		return field.getElementName();
	}
    

}
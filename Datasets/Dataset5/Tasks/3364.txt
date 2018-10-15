package org.eclipse.wst.xquery.debug.core;

/*******************************************************************************
 * Copyright (c) 2008, 2009 28msec Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     Gabriel Petrovay (28msec) - initial API and implementation
 *******************************************************************************/
package org.eclipse.wst.xquery.debug.internal.core;

import java.util.Arrays;

import org.eclipse.dltk.debug.core.model.AtomicScriptType;
import org.eclipse.dltk.debug.core.model.ComplexScriptType;
import org.eclipse.dltk.debug.core.model.IScriptType;
import org.eclipse.dltk.debug.core.model.IScriptTypeFactory;

public class XQDTTypeFactory implements IScriptTypeFactory {

    private static final String[] simpleTypes = { "ENTITIES", "ENTITY", "ID", "IDREF", "IDREFS", "NCName", "NMTOKEN",
            "NMTOKENS", "NOTATION", "Name", "QName", "anyAtomicType", "anySimpleType", "anyType", "anyURI",
            "base64Binary", "boolean", "byte", "date", "dateTime", "dayTimeDuration", "decimal", "double", "duration",
            "float", "gDay", "gMonth", "gMonthDay", "gYear", "gYearMonth", "hexBinary", "int", "integer", "language",
            "long", "negativeInteger", "nonNegativeInteger", "nonPositiveInteger", "normalizedString",
            "positiveInteger", "short", "string", "time", "token", "unsignedByte", "unsignedInt", "unsignedShort",
            "unsugnedLong", "untyped", "untypedAtomic", "yearMonthDuration" };

    public IScriptType buildType(String type) {
//        if (type.endsWith("*") || type.endsWith("+")) {
//            return new ArrayScriptType();
//        }
        int index = Arrays.binarySearch(simpleTypes, type);
        if (index >= 0) {
            return new AtomicScriptType(type);
        }
        return new ComplexScriptType(type);
    }

}
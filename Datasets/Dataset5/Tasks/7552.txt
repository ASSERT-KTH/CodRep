super(NAMESPACE, makeAttributeQName(prefix), namespaceURI, null, true, location);

/*
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 * 
 *      http://www.apache.org/licenses/LICENSE-2.0
 * 
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package org.apache.xerces.stax.events;

import javax.xml.namespace.QName;
import javax.xml.stream.Location;
import javax.xml.stream.events.Namespace;

import org.apache.xerces.xni.NamespaceContext;

/**
 * 
 * @author Lucian Holland
 *
 * @version $Id$
 */
public class NamespaceImpl extends AttributeImpl implements Namespace {

    private final String fPrefix;
    private final String fNamespaceURI;

    /**
     * @param location
     * @param schemaType
     */
    public NamespaceImpl(final String prefix, final String namespaceURI, final Location location) {
        super(NAMESPACE, makeAttributeQName(prefix), namespaceURI, null, true, location, null);
        fPrefix = (prefix == null ? "" : prefix);
        fNamespaceURI = namespaceURI;
    }

    /**
     * @param prefix The prefix for this namespace.
     * @return A QName for the attribute that declares this namespace.
     */
    private static QName makeAttributeQName(String prefix) {
        if (prefix == null) {
            return new QName("", "xmlns", "");
        }
        return new QName(NamespaceContext.XMLNS_URI, prefix, "xmlns");
    }

    /**
     * @see javax.xml.stream.events.Namespace#getPrefix()
     */
    public String getPrefix() {
        return fPrefix;
    }

    /**
     * @see javax.xml.stream.events.Namespace#getNamespaceURI()
     */
    public String getNamespaceURI() {
        return fNamespaceURI;
    }

    /**
     * @see javax.xml.stream.events.Namespace#isDefaultNamespaceDeclaration()
     */
    public boolean isDefaultNamespaceDeclaration() {
        return fPrefix == "";
    }
}
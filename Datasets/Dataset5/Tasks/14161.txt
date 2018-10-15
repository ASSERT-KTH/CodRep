public final class EntityDeclarationImpl extends XMLEventImpl implements

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

import javax.xml.stream.Location;
import javax.xml.stream.events.EntityDeclaration;

/**
 * 
 * @author Lucian Holland
 *
 * @version $Id$
 */
public class EntityDeclarationImpl extends XMLEventImpl implements
        EntityDeclaration {

    private final String fPublicId;
    private final String fSystemId;
    private final String fName;
    private final String fNotationName;

    /**
     * @param eventType
     * @param location
     * @param schemaType
     */
    public EntityDeclarationImpl(final String publicId, final String systemId, final String name, final String notationName, final Location location) {
        super(ENTITY_DECLARATION, location);
        fPublicId = publicId;
        fSystemId = systemId;
        fName = name;
        fNotationName = notationName;
    }

    /**
     * @see javax.xml.stream.events.EntityDeclaration#getPublicId()
     */
    public String getPublicId() {
        return fPublicId;
    }

    /**
     * @see javax.xml.stream.events.EntityDeclaration#getSystemId()
     */
    public String getSystemId() {
        return fSystemId;
    }

    /**
     * @see javax.xml.stream.events.EntityDeclaration#getName()
     */
    public String getName() {
        return fName;
    }

    /**
     * @see javax.xml.stream.events.EntityDeclaration#getNotationName()
     */
    public String getNotationName() {
        return fNotationName;
    }

    /**
     * @see javax.xml.stream.events.EntityDeclaration#getReplacementText()
     */
    public String getReplacementText() {
        // TODO Auto-generated method stub
        return null;
    }

    /**
     * @see javax.xml.stream.events.EntityDeclaration#getBaseURI()
     */
    public String getBaseURI() {
        // TODO Auto-generated method stub
        return null;
    }

}
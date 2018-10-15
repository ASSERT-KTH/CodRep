super(ENTITY_REFERENCE, location);

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
import javax.xml.stream.events.EntityReference;

/**
 * 
 * @author Lucian Holland
 *
 * @version $Id$
 */
public class EntityReferenceImpl extends XMLEventImpl implements
        EntityReference {

    /**
     * The entity declaration for this entity reference.
     */
    private final EntityDeclaration fDecl;

    /**
     * Constructor.
     * @param location
     */
    public EntityReferenceImpl(final EntityDeclaration decl, final Location location) {
        super(ENTITY_REFERENCE, location, null);
        fDecl = decl;;
    }

    /**
     * @see javax.xml.stream.events.EntityReference#getDeclaration()
     */
    public EntityDeclaration getDeclaration() {
        return fDecl;
    }

    /**
     * @see javax.xml.stream.events.EntityReference#getName()
     */
    public String getName() {
        //TODO: Is this actually correct? Not sure how an entity ref can have a different
        //name to the entity decl, but needs checking just in case.
        return fDecl.getName();
    }

}
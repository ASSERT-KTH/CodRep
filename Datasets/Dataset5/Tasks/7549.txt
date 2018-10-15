super(XMLStreamConstants.END_ELEMENT, location);

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

import java.util.Iterator;

import javax.xml.namespace.QName;
import javax.xml.stream.Location;
import javax.xml.stream.XMLStreamConstants;
import javax.xml.stream.events.EndElement;

/**
 * 
 * @author Lucian Holland
 *
 * @version $Id$
 */
public class EndElementImpl extends XMLEventImpl implements EndElement {

    /**
     * The qualified name of the element that is being closed.
     */
    private final QName fName;

    /**
     * @param location The location object for this event.
     */
    public EndElementImpl(final QName name, final Location location) {
        super(XMLStreamConstants.END_ELEMENT, location, null);
        fName = name;
    }

    /**
     * @see javax.xml.stream.events.EndElement#getName()
     */
    public QName getName() {
        return fName;
    }

    /**
     * @see javax.xml.stream.events.EndElement#getNamespaces()
     */
    public Iterator getNamespaces() {
        // TODO Auto-generated method stub
        return null;
    }
    
}
super(START_DOCUMENT, location);

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
import javax.xml.stream.events.StartDocument;

/**
 * 
 * @author Lucian Holland
 *
 * @version $Id$
 */
public class StartDocumentImpl extends XMLEventImpl implements StartDocument {

    private final String fCharEncoding;
    private final boolean fEncodingSet;
    private final String fVersion;
    private final boolean fIsStandalone;
    private final boolean fStandaloneSet;

    /**
     * @param location
     */
    public StartDocumentImpl(final String charEncoding, final boolean encodingSet, final boolean isStandalone, final boolean standaloneSet, final String version, final Location location) {
        super(START_DOCUMENT, location, null);
        fCharEncoding = charEncoding;
        fEncodingSet = encodingSet;
        fIsStandalone = isStandalone;
        fStandaloneSet = standaloneSet;
        fVersion = version;
    }

    /**
     * @see javax.xml.stream.events.StartDocument#getSystemId()
     */
    public String getSystemId() {
        return getLocation().getSystemId();
    }

    /**
     * @see javax.xml.stream.events.StartDocument#getCharacterEncodingScheme()
     */
    public String getCharacterEncodingScheme() {
        return fCharEncoding;
    }

    /**
     * @see javax.xml.stream.events.StartDocument#encodingSet()
     */
    public boolean encodingSet() {
        return fEncodingSet;
    }

    /**
     * @see javax.xml.stream.events.StartDocument#isStandalone()
     */
    public boolean isStandalone() {
        return fIsStandalone;
    }

    /**
     * @see javax.xml.stream.events.StartDocument#standaloneSet()
     */
    public boolean standaloneSet() {
        return fStandaloneSet;
    }

    /**
     * @see javax.xml.stream.events.StartDocument#getVersion()
     */
    public String getVersion() {
        return fVersion;
    }
 
}
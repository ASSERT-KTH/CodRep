public final class CharactersImpl extends XMLEventImpl implements Characters {

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
import javax.xml.stream.events.Characters;

/**
 * 
 * @author Lucian Holland
 *
 * @version $Id$
 */
public class CharactersImpl extends XMLEventImpl implements Characters {

    private final String fData;
    private final boolean fIsWS;
    private final boolean fIsCData;
    private final boolean fIsIgnorableWS;

    /**
     * Standard constructor.
     * @param eventType
     * @param location
     * @param schemaType
     */
    public CharactersImpl(final String data, final boolean isWS, final boolean isCData, final boolean isIgnorableWS, final Location location) {
        super(CHARACTERS, location);
        fData = data;
        fIsWS = isWS;
        fIsCData = isCData;
        fIsIgnorableWS = isIgnorableWS;
    }

    /**
     * @see javax.xml.stream.events.Characters#getData()
     */
    public String getData() {
        return fData;
    }

    /**
     * @see javax.xml.stream.events.Characters#isWhiteSpace()
     */
    public boolean isWhiteSpace() {
        return fIsWS;
    }

    /**
     * @see javax.xml.stream.events.Characters#isCData()
     */
    public boolean isCData() {
        return fIsCData;
    }

    /**
     * @see javax.xml.stream.events.Characters#isIgnorableWhiteSpace()
     */
    public boolean isIgnorableWhiteSpace() {
        return fIsIgnorableWS;
    }

    
}
super(PROCESSING_INSTRUCTION, location);

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
import javax.xml.stream.XMLStreamException;
import javax.xml.stream.XMLStreamWriter;
import javax.xml.stream.events.ProcessingInstruction;

/**
 * 
 * @author Lucian Holland
 *
 * @version $Id$
 */
public class ProcessingInstructionImpl extends XMLEventImpl implements
        ProcessingInstruction {

    private final String fTarget;
    private final String fData;

    /**
     * @param location
     */
    public ProcessingInstructionImpl(final String target, final String data, final Location location) {
        super(PROCESSING_INSTRUCTION, location, null);
        fTarget = target;
        fData = data;
    }

    /**
     * @see javax.xml.stream.events.ProcessingInstruction#getTarget()
     */
    public String getTarget() {
        return fTarget;
    }

    /**
     * @see javax.xml.stream.events.ProcessingInstruction#getData()
     */
    public String getData() {
        return fData;
    }

    /**
     * @see org.apache.xerces.stax.events.XMLEventImpl#writeToStreamWriter(javax.xml.stream.XMLStreamWriter)
     */
    public void writeToStreamWriter(XMLStreamWriter writer) throws XMLStreamException {
        
    }

}
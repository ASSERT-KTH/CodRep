public final class XMLEventFactoryImpl extends XMLEventFactory {

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

package org.apache.xerces.stax;

import java.util.Iterator;

import javax.xml.namespace.NamespaceContext;
import javax.xml.namespace.QName;
import javax.xml.stream.Location;
import javax.xml.stream.XMLEventFactory;
import javax.xml.stream.events.Attribute;
import javax.xml.stream.events.Characters;
import javax.xml.stream.events.Comment;
import javax.xml.stream.events.DTD;
import javax.xml.stream.events.EndDocument;
import javax.xml.stream.events.EndElement;
import javax.xml.stream.events.EntityDeclaration;
import javax.xml.stream.events.EntityReference;
import javax.xml.stream.events.Namespace;
import javax.xml.stream.events.ProcessingInstruction;
import javax.xml.stream.events.StartDocument;
import javax.xml.stream.events.StartElement;

/**
 * <p>Implementation of XMLEventFactory.</p>
 * 
 * @version $Id$
 */
public class XMLEventFactoryImpl extends XMLEventFactory {

    public XMLEventFactoryImpl() {}
    
    public void setLocation(Location location) {}
    
    public Attribute createAttribute(String prefix, String namespaceURI,
            String localName, String value) {
        return null;
    }

    public Attribute createAttribute(String localName, String value) {
        return null;
    }

    public Attribute createAttribute(QName name, String value) {
        return null;
    }
    
    public Namespace createNamespace(String namespaceURI) {
        return null;
    }

    public Namespace createNamespace(String prefix, String namespaceUri) {
        return null;
    }
    
    public StartElement createStartElement(QName name, Iterator attributes,
            Iterator namespaces) {
        return null;
    }
    
    public StartElement createStartElement(String prefix, String namespaceUri,
            String localName) {
        return null;
    }
  
    public StartElement createStartElement(String prefix, String namespaceUri,
            String localName, Iterator attributes, Iterator namespaces) {
        return null;
    }
    
    public StartElement createStartElement(String prefix, String namespaceUri,
            String localName, Iterator attributes, Iterator namespaces,
            NamespaceContext context) {
        return null;
    }

    public EndElement createEndElement(QName name, Iterator namespaces) {
        return null;
    }

    public EndElement createEndElement(String prefix, String namespaceUri,
            String localName) {
        return null;
    }
    
    public EndElement createEndElement(String prefix, String namespaceUri,
            String localName, Iterator namespaces) {
        return null;
    }
    
    public Characters createCharacters(String content) {
        return null;
    }

    public Characters createCData(String content) {
        return null;
    }

    public Characters createSpace(String content) {
        return null;
    }

    public Characters createIgnorableSpace(String content) {
        return null;
    }
    
    public StartDocument createStartDocument() {
        return null;
    }
    
    public StartDocument createStartDocument(String encoding, String version,
            boolean standalone) {
        return null;
    }
    
    public StartDocument createStartDocument(String encoding, String version) {
        return null;
    }

    public StartDocument createStartDocument(String encoding) {
        return null;
    }
    
    public EndDocument createEndDocument() {
        return null;
    }
    
    public EntityReference createEntityReference(String name,
            EntityDeclaration declaration) {
        return null;
    }
    
    public Comment createComment(String text) {
        return null;
    }
    
    public ProcessingInstruction createProcessingInstruction(String target,
            String data) {
        return null;
    }
    
    public DTD createDTD(String dtd) {
        return null;
    }
}
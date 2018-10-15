private final PSVIProvider provider;

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

package simpletype;

import java.io.File;

import javax.xml.XMLConstants;
import javax.xml.parsers.SAXParser;
import javax.xml.parsers.SAXParserFactory;
import javax.xml.validation.SchemaFactory;

import org.apache.xerces.xs.ElementPSVI;
import org.apache.xerces.xs.PSVIProvider;
import org.apache.xerces.xs.XSConstants;
import org.apache.xerces.xs.datatypes.ByteList;
import org.apache.xerces.xs.datatypes.ObjectList;
import org.apache.xerces.xs.datatypes.XSDateTime;
import org.apache.xerces.xs.datatypes.XSDecimal;
import org.apache.xerces.xs.datatypes.XSDouble;
import org.apache.xerces.xs.datatypes.XSFloat;
import org.apache.xerces.xs.datatypes.XSQName;
import org.xml.sax.SAXException;
import org.xml.sax.helpers.DefaultHandler;

/**
 * <p>Demonstrates how to use the datatype interfaces in 
 * <code>org.apache.xerces.xs.datatypes</code>.</p>
 * 
 * @author Ankit Pasricha, IBM
 * 
 * @version $Id$
 */
public class DatatypeInterfaceUsage extends DefaultHandler {

    private PSVIProvider provider;
    
    public DatatypeInterfaceUsage(PSVIProvider p) {
        provider = p;
    }
    
    /**
     * @param args
     */
    public static void main(String[] args) throws Exception {
        
        if(args.length == 2) {
            // Use SAX parser and store the PSVIProvider to access PSVI info.
            SAXParserFactory fact = SAXParserFactory.newInstance();
            fact.setSchema(SchemaFactory.newInstance(XMLConstants.W3C_XML_SCHEMA_NS_URI).newSchema(new File(args[0])));
            SAXParser parser = fact.newSAXParser();
            PSVIProvider p = (PSVIProvider)parser.getXMLReader();
            
            parser.parse(args[1], new DatatypeInterfaceUsage(p));
        }
        else
            printUsage();
    }
    
    static void printUsage() {
        System.err.println("USAGE: java java.DatatypeInterfaceUsage <xsd file name (one only)> <xml file name(one only)>");
    }

    public void endElement(String uri, String localName, String qName) throws SAXException {
        ElementPSVI psvi = provider.getElementPSVI();
        if(psvi != null) {
            //If there was an element content
            Object value = psvi.getActualNormalizedValue();
            short type = psvi.getActualNormalizedValueType();
            if(value != null) {
                switch(type) {
                case XSConstants.INTEGER_DT:
                case XSConstants.DECIMAL_DT:
                case XSConstants.INT_DT:
                case XSConstants.LONG_DT:
                case XSConstants.SHORT_DT:
                case XSConstants.BYTE_DT:
                case XSConstants.UNSIGNEDBYTE_DT:
                case XSConstants.UNSIGNEDINT_DT:
                case XSConstants.UNSIGNEDLONG_DT:
                case XSConstants.UNSIGNEDSHORT_DT:
                    XSDecimal decimal = (XSDecimal)value;
                    System.out.println(decimal.getInt());
                    break;
                    
                case XSConstants.DATE_DT:
                case XSConstants.DATETIME_DT:
                case XSConstants.GDAY_DT:
                case XSConstants.GMONTH_DT:
                case XSConstants.GMONTHDAY_DT:
                case XSConstants.GYEAR_DT:
                case XSConstants.GYEARMONTH_DT:
                case XSConstants.DURATION_DT:
                case XSConstants.TIME_DT:
                    XSDateTime dt = (XSDateTime)value;
                    System.out.println(dt.getDays());
                    break;
                    
                case XSConstants.FLOAT_DT:
                    XSFloat f = (XSFloat)value;
                    System.out.println(f.getValue());
                    break;
                    
                case XSConstants.DOUBLE_DT:
                    XSDouble d = (XSDouble)value;
                    System.out.println(d.getValue());
                    break;
                    
                case XSConstants.HEXBINARY_DT:
                case XSConstants.BASE64BINARY_DT:
                    ByteList list = (ByteList)value;
                    System.out.println(list.getLength());
                    break;
                    
                case XSConstants.LIST_DT:
                case XSConstants.LISTOFUNION_DT:
                    ObjectList l = (ObjectList)value;
                    System.out.println(l.getLength());
                    break;
                    
                case XSConstants.QNAME_DT:
                    XSQName qname = (XSQName)value;
                    System.out.println(qname.getXNIQName());
                    break;
                
                default:
                    System.out.println("error!!!");
                }
            }
        }
        super.endElement(uri, localName, qName);
    }

}
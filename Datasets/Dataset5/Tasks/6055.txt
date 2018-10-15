document.setXmlEncoding("utf-8");

/*
 * The Apache Software License, Version 1.1
 * 
 * Copyright (c) 1999-2002 The Apache Software Foundation.  All rights 
 * reserved.
 * 
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 * 
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer. 
 * 
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in
 *    the documentation and/or other materials provided with the
 *    distribution.
 * 
 * 3. The end-user documentation included with the redistribution,
 *    if any, must include the following acknowledgment:  
 *       "This product includes software developed by the
 *        Apache Software Foundation (http://www.apache.org/)."
 *    Alternately, this acknowledgment may appear in the software itself,
 *    if and wherever such third-party acknowledgments normally appear.
 * 
 * 4. The names "Xerces" and "Apache Software Foundation" must
 *    not be used to endorse or promote products derived from this
 *    software without prior written permission. For written 
 *    permission, please contact apache\@apache.org.
 * 
 * 5. Products derived from this software may not be called "Apache",
 *    nor may "Apache" appear in their name, without prior written
 *    permission of the Apache Software Foundation.
 * 
 * THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESSED OR IMPLIED
 * WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
 * OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED.  IN NO EVENT SHALL THE APACHE SOFTWARE FOUNDATION OR
 * ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
 * USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
 * OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
 * OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
 * SUCH DAMAGE.
 * ====================================================================
 * 
 * This software consists of voluntary contributions made by many
 * individuals on behalf of the Apache Software Foundation, and was
 * originally based on software copyright (c) 2002, International
 * Business Machines, Inc., http://www.ibm.com .  For more information
 * on the Apache Software Foundation, please see
 * <http://www.apache.org/>.
 */

package dom.serialize;

import java.io.IOException;
import java.io.StringWriter;
import java.io.Writer;

import org.apache.xerces.dom.DocumentImpl;
import org.w3c.dom.ls.DOMWriter;
import org.w3c.dom.ls.DOMImplementationLS;
import org.apache.xerces.dom.DOMImplementationImpl;
import org.apache.xml.serialize.OutputFormat;
import org.apache.xml.serialize.Serializer;
import org.apache.xml.serialize.SerializerFactory;
import org.w3c.dom.Document;
import org.w3c.dom.Element;

/**
 * Tests that original behavior of XMLSerializer is not broken.
 * The namespace fixup is only performed with DOMWriter.
 * 
 * @author Elena Litani, IBM
 */
public class TestXmlns {

      public static void main(String[] args) {

            // Create a document.
            DocumentImpl document = new DocumentImpl();
            document.setEncoding("utf-8");
            // Create an element with a default namespace declaration.
            Element outerNode = document.createElement("outer");
            outerNode.setAttribute("xmlns", "myuri:");
            document.appendChild(outerNode);

            // Create an inner element with no further namespace declaration.
            Element innerNode = document.createElement("inner");
            outerNode.appendChild(innerNode);

            // DOM is complete, now serialize it.
            Writer writer = new StringWriter();
            OutputFormat format = new OutputFormat();
            format.setEncoding("utf-8");
            Serializer serializer = SerializerFactory.getSerializerFactory("xml").makeSerializer(writer, format);
            try {
                  serializer.asDOMSerializer().serialize(document);
            } catch (IOException exception) {
                  exception.printStackTrace();
                  System.exit(1);
            }

            // Show the results on the console.
            System.out.println("\n---XMLSerializer output---");
            System.out.println(writer.toString());


            // create DOM Serializer

            System.out.println("\n---DOMWriter output---");
            DOMWriter domWriter = ((DOMImplementationLS)DOMImplementationImpl.getDOMImplementation()).createDOMWriter();
            
            try {
                domWriter.writeNode(System.out, document);
            } catch (Exception e){
                e.printStackTrace();
            }

            
      }
}
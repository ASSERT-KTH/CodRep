import org.w3c.dom.traversal.*;

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 1999 The Apache Software Foundation.  All rights 
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
 *    permission, please contact apache@apache.org.
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
 * individuals on behalf of the Apache Software Foundation and was
 * originally based on software copyright (c) 1999, International
 * Business Machines, Inc., http://www.apache.org.  For more
 * information on the Apache Software Foundation, please see
 * <http://www.apache.org/>.
 */
package dom.traversal;


import org.apache.xerces.domx.traversal.*;
import org.w3c.dom.Node;
import org.w3c.dom.Element;

 /** An example filter which enables the client to set a <b>name</b> value 
  *  accept those node names which <b>match</b> (or explicitly <b>not match</b>) 
  *  the set name value.
  */
 public class NameNodeFilter implements NodeFilter {
    
    String fName;
    boolean fMatch = true;
            
        /** The name to compare with the node name. If null, all node names  
         *  are successfully matched. 
         */
        public void setName(String name) {
            this.fName = name;
        }
        
        /** Return the name to compare with node name. If null, all node names  
         *  are successfully matched. */
        public String getName() {
            return this.fName;
        }
        
        /** 
         *  Controls whether the node name is accepted when it <b>does</b> match 
         *  the setName value, or when it <b>does not</b> match the setName value. 
         *  If the setName value is null this match value does not matter, and
         *  all names will match.
         *  If match is true, the node name is accepted when it matches. 
         *  If match is false, the node name is accepted when does not match. 
         */
        public void setMatch(boolean match) {
            this.fMatch = match;
        }
        
        /** Return match value. */
        public boolean getMatch() {
            return this.fMatch;
        }
        
        /** acceptNode determines if this filter accepts a node name or not. */ 
        public short acceptNode(Node n) {

            if (fName == null || fMatch && n.getNodeName().equals(fName) 
            ||  !fMatch && !n.getNodeName().equals(fName))
                return FILTER_ACCEPT;
            else 
                return FILTER_REJECT;
        }
    }
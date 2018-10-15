private static final long serialVersionUID = -2052250142899797905L;

/*
 * Copyright 1999,2000,2004,2005 The Apache Software Foundation.
 * 
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * 
 *      http://www.apache.org/licenses/LICENSE-2.0
 * 
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.apache.wml.dom;

import org.apache.wml.*;

/**
 * @xerces.internal
 * @version $Id$
 * @author <a href="mailto:david@topware.com.tw">David Li</a>
 */
public class WMLGoElementImpl extends WMLElementImpl implements WMLGoElement {

    private static final long serialVersionUID = 3256718485575841072L;

    public WMLGoElementImpl (WMLDocumentImpl owner, String tagName) {
        super( owner, tagName);
    }
    
    public void setSendreferer(String newValue) {
        setAttribute("sendreferer", newValue);
    }
    
    public String getSendreferer() {
        return getAttribute("sendreferer");
    }
    
    public void setAcceptCharset(String newValue) {
        setAttribute("accept-charset", newValue);
    }
    
    public String getAcceptCharset() {
        return getAttribute("accept-charset");
    }
    
    public void setHref(String newValue) {
        setAttribute("href", newValue);
    }
    
    public String getHref() {
        return getAttribute("href");
    }
    
    public void setClassName(String newValue) {
        setAttribute("class", newValue);
    }
    
    public String getClassName() {
        return getAttribute("class");
    }
    
    public void setId(String newValue) {
        setAttribute("id", newValue);
    }
    
    public String getId() {
        return getAttribute("id");
    }
    
    public void setMethod(String newValue) {
        setAttribute("method", newValue);
    }
    
    public String getMethod() {
        return getAttribute("method");
    }
    
}
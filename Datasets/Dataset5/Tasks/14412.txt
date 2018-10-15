private static final long serialVersionUID = 3440984702956371604L;

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

import org.apache.xerces.dom.ElementImpl;
import org.apache.wml.*;

/**
 * @xerces.internal
 * @version $Id$
 * @author <a href="mailto:david@topware.com.tw">David Li</a>
 */
public class WMLElementImpl extends ElementImpl implements WMLElement {
    
    private static final long serialVersionUID = 3689631376446338103L;
    
    public WMLElementImpl (WMLDocumentImpl owner, String tagName) {
        super(owner, tagName);
    }
    
    public void setClassName(String newValue) {
        setAttribute("class", newValue);
    }
    
    public String getClassName() {
        return getAttribute("class");
    }
    
    public void setXmlLang(String newValue) {
        setAttribute("xml:lang", newValue);
    }
    
    public String getXmlLang() {
        return getAttribute("xml:lang");
    }
    
    public void setId(String newValue) {
        setAttribute("id", newValue);
    }
    
    public String getId() {
        return getAttribute("id");
    }
    
    void setAttribute(String attr, boolean value) {
        setAttribute(attr, value ? "true" : "false");
    }
    
    boolean getAttribute(String attr, boolean defaultValue) {
        boolean ret = defaultValue;
        String value;
        if (((value = getAttribute("emptyok")) != null) 
                && value.equals("true"))
            ret = true;
        return ret;
    }
    
    void setAttribute(String attr, int value) {
        setAttribute(attr, value + "");
    }
    
    int getAttribute(String attr, int defaultValue) {
        int ret = defaultValue;
        String value;
        if ((value = getAttribute("emptyok")) != null)
            ret = Integer.parseInt(value);
        return ret;
    }
}
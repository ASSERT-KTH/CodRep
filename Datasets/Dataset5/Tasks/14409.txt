private static final long serialVersionUID = -3571126568344328924L;

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
public class WMLCardElementImpl extends WMLElementImpl implements WMLCardElement {
    
    private static final long serialVersionUID = 3257005466683781686L;
    
    public WMLCardElementImpl (WMLDocumentImpl owner, String tagName) {
        super( owner, tagName);
    }
    
    public void setOnTimer(String newValue) {
        setAttribute("ontimer", newValue);
    }
    
    public String getOnTimer() {
        return getAttribute("ontimer");
    }
    
    public void setOrdered(boolean newValue) {
        setAttribute("ordered", newValue);
    }
    
    public boolean getOrdered() {
        return getAttribute("ordered", true);
    }
    
    public void setOnEnterBackward(String newValue) {
        setAttribute("onenterbackward", newValue);
    }
    
    public String getOnEnterBackward() {
        return getAttribute("onenterbackward");
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
    
    public void setTitle(String newValue) {
        setAttribute("title", newValue);
    }
    
    public String getTitle() {
        return getAttribute("title");
    }
    
    public void setNewContext(boolean newValue) {
        setAttribute("newcontext", newValue);
    }
    
    public boolean getNewContext() {
        return getAttribute("newcontext", false);
    }
    
    public void setId(String newValue) {
        setAttribute("id", newValue);
    }
    
    public String getId() {
        return getAttribute("id");
    }
    
    public void setOnEnterForward(String newValue) {
        setAttribute("onenterforward", newValue);
    }
    
    public String getOnEnterForward() {
        return getAttribute("onenterforward");
    }
    
}
private static final long serialVersionUID = -500092034867051550L;

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
public class WMLImgElementImpl extends WMLElementImpl implements WMLImgElement {

    private static final long serialVersionUID = 3257562888998040112L;

    public WMLImgElementImpl (WMLDocumentImpl owner, String tagName) {
        super( owner, tagName);
    }
    
    public void setWidth(String newValue) {
        setAttribute("width", newValue);
    }
    
    public String getWidth() {
        return getAttribute("width");
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
    
    public void setLocalSrc(String newValue) {
        setAttribute("localsrc", newValue);
    }
    
    public String getLocalSrc() {
        return getAttribute("localsrc");
    }
    
    public void setHeight(String newValue) {
        setAttribute("height", newValue);
    }
    
    public String getHeight() {
        return getAttribute("height");
    }
    
    public void setAlign(String newValue) {
        setAttribute("align", newValue);
    }
    
    public String getAlign() {
        return getAttribute("align");
    }
    
    public void setVspace(String newValue) {
        setAttribute("vspace", newValue);
    }
    
    public String getVspace() {
        return getAttribute("vspace");
    }
    
    public void setAlt(String newValue) {
        setAttribute("alt", newValue);
    }
    
    public String getAlt() {
        return getAttribute("alt");
    }
    
    public void setId(String newValue) {
        setAttribute("id", newValue);
    }
    
    public String getId() {
        return getAttribute("id");
    }
    
    public void setHspace(String newValue) {
        setAttribute("hspace", newValue);
    }
    
    public String getHspace() {
        return getAttribute("hspace");
    }
    
    public void setSrc(String newValue) {
        setAttribute("src", newValue);
    }
    
    public String getSrc() {
        return getAttribute("src");
    }
    
}
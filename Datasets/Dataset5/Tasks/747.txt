return _prefix + ":"+name; //$NON-NLS-1$

package org.eclipse.jst.jsf.facelet.core.internal.cm;

import java.util.Iterator;

import org.eclipse.wst.xml.core.internal.contentmodel.CMContent;
import org.eclipse.wst.xml.core.internal.contentmodel.CMDataType;
import org.eclipse.wst.xml.core.internal.contentmodel.CMElementDeclaration;
import org.eclipse.wst.xml.core.internal.contentmodel.CMNamedNodeMap;
import org.eclipse.wst.xml.core.internal.contentmodel.CMNode;

class DocumentElementCMAdapter implements CMNamedNodeMap,
        CMElementDeclaration
{
    private final  String               _prefix;
    private final  ElementCMAdapter     _adapter;
    
    public DocumentElementCMAdapter(final ElementCMAdapter adapter, final String prefix)
    {
        _prefix = prefix;
        _adapter = adapter;
    }
    
    public int getLength()
    {
        return _adapter.getLength();
    }

    public CMNode getNamedItem(String name)
    {
        return _adapter.getNamedItem(name);
    }

    public CMNode item(int index)
    {
        return _adapter.item(index);
    }

    @SuppressWarnings("unchecked")
    public Iterator iterator()
    {
        return _adapter.iterator();
    }

    public CMNamedNodeMap getAttributes()
    {
        return _adapter.getAttributes();
    }

    public CMContent getContent()
    {
        return _adapter.getContent();
    }

    public int getContentType()
    {
       return _adapter.getContentType();
    }

    public CMDataType getDataType()
    {
        return _adapter.getDataType();
    }

    public String getElementName()
    {
        return getPrefixedName(_adapter.getElementName());
    }

    public CMNamedNodeMap getLocalElements()
    {
        return _adapter.getLocalElements();
    }

    public int getMaxOccur()
    {
        return _adapter.getMaxOccur();
    }

    public int getMinOccur()
    {
        return _adapter.getMinOccur();
    }

    public String getNodeName()
    {
        return getPrefixedName(_adapter.getNodeName());
    }

    private String getPrefixedName(final String name)
    {
        return _prefix + ":"+name;
    }
    
    public int getNodeType()
    {
        return _adapter.getNodeType();
    }

    public Object getProperty(String propertyName)
    {
        return _adapter.getProperty(propertyName);
    }

    public boolean supports(String propertyName)
    {
        return _adapter.supports(propertyName);
    }

}
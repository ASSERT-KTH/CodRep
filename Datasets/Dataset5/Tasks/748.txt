throw new UnsupportedOperationException(""); //$NON-NLS-1$

package org.eclipse.jst.jsf.facelet.core.internal.cm;

import java.util.Iterator;

import org.eclipse.wst.xml.core.internal.contentmodel.CMDocument;
import org.eclipse.wst.xml.core.internal.contentmodel.CMNamedNodeMap;
import org.eclipse.wst.xml.core.internal.contentmodel.CMNamespace;
import org.eclipse.wst.xml.core.internal.contentmodel.CMNode;

/**
 * A namespace a specific to a document, where it's tag name prefix is known.
 *
 */
class DocumentNamespaceCMAdapter implements CMNamedNodeMap, CMDocument
{
    private final String                    _prefix;
    private final NamespaceCMAdapter        _adapter;
    
    public DocumentNamespaceCMAdapter(final NamespaceCMAdapter adapter, final String prefix)
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
        CMNode  node = _adapter.getNamedItem(name);
        
        if (node != null)
        {
            node =  new DocumentElementCMAdapter((ElementCMAdapter) node,_prefix);
        }
        return node;
    }

    public CMNode item(int index)
    {
        CMNode  item = _adapter.item(index);
        
        if (item != null)
        {
            item = new DocumentElementCMAdapter((ElementCMAdapter) item,_prefix);
        }
        return item;
    }

    public Iterator<?> iterator()
    {
        return new WrappingIterator(_adapter.iterator());
    }

    private class WrappingIterator implements Iterator<CMNode>
    {
        private Iterator<?>   _it;
        
        public WrappingIterator(final Iterator<?> it)
        {
            _it = it;
        }
        public boolean hasNext()
        {
            return _it.hasNext();
        }

        public CMNode next()
        {
            CMNode node = (CMNode) _it.next();
            node = getNamedItem(node.getNodeName());
            return node;
        }

        public void remove()
        {
            throw new UnsupportedOperationException("");
        }
    }

    public CMNamedNodeMap getElements()
    {
        return this;
    }

    public CMNamedNodeMap getEntities()
    {
        //not changing entities
        return _adapter.getEntities();
    }

    public CMNamespace getNamespace()
    {
        return new CMNamespaceImpl(_adapter.getNamespace(), _prefix);
    }

    public String getNodeName()
    {
        // not changing node name
        return _adapter.getNodeName();
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

    private static class CMNamespaceImpl implements CMNamespace
    {
        private final CMNamespace   _proxy;
        private final String        _prefix;
        
        CMNamespaceImpl(CMNamespace proxy, final String prefix)
        {
            _proxy = proxy;
            _prefix = prefix;
        }

        public String getPrefix()
        {
            return _prefix;
        }

        public String getURI()
        {
            return _proxy.getURI();
        }

        public String getNodeName()
        {
            return _proxy.getNodeName();
        }

        public int getNodeType()
        {
            return _proxy.getNodeType();
        }

        public Object getProperty(String propertyName)
        {
            return _proxy.getProperty(propertyName);
        }

        public boolean supports(String propertyName)
        {
            return _proxy.supports(propertyName);
        }
    }
}
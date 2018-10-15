public abstract Map<String, ITagElement>  getTags();

package org.eclipse.jst.jsf.facelet.core.internal.tagmodel;

import java.util.Collection;
import java.util.Map;

import org.eclipse.jst.jsf.common.runtime.internal.view.model.common.ITagElement;




/**
 * A description about a facelet tag library descriptor (facelet-taglib_1_0.dtd)
 * 
 * @author cbateman
 *
 */
public abstract class FaceletTaglib extends org.eclipse.jst.jsf.common.runtime.internal.view.model.common.Namespace
{
    /**
     * The namespace that this tag library is associated with
     */
    private final String  _namespace;

    protected FaceletTaglib(final String namespace)
    {
        _namespace = namespace;
    }


    @Override
    public abstract String getDisplayName();

    @Override
    public String getNSUri() {
        return _namespace;
    }

    @Override
    public abstract Collection<? extends ITagElement> getViewElements();


    @Override
    public String toString()
    {
        return "Namespace: " + _namespace + "\n" + getLibraryTypeDescription()
                + "\n";
    }

    /**
     * @return the library type description
     */
    public abstract String getLibraryTypeDescription();

    /**
     * @return a map of tags indexed by name.  Map should be regarded
     * as unmodifiable and may throw exceptions on modification
     */
    public abstract Map<String, FaceletTag>  getTags();


    public abstract ITagElement getViewElement(String name);


    @Override
    public abstract boolean hasViewElements();

    @Override
    public abstract boolean isInitialized();
}
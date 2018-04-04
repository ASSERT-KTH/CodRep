Map attachments = invocation.aspectAttachments;

/***************************************
 *                                     *
 *  JBoss: The OpenSource J2EE WebOS   *
 *                                     *
 *  Distributable under LGPL license.  *
 *  See terms of license at gnu.org.   *
 *                                     *
 ***************************************/
package org.jboss.aspect.interceptors;

import java.io.Serializable;
import java.lang.reflect.Method;
import java.util.Map;

import org.dom4j.Element;
import org.dom4j.Namespace;
import org.dom4j.QName;
import org.jboss.aspect.AspectInitizationException;
import org.jboss.aspect.spi.AspectInterceptor;
import org.jboss.aspect.spi.AspectInvocation;
import org.jboss.util.Classes;

/**
 * The AdaptorInterceptor allows you proivde add an adaptor
 * via the Adaptor interface.  
 * 
 * The problem with the Delegating interceptor is that as you add more
 * interfaces to an object you run a higher chance of having method name 
 * clashes.
 * 
 * 
 * This interceptor uses the following configuration attributes:
 * <ul>
 * <li>adaptor  - The interface that the implementation object is exposing 
 *                via the Adaptable interface.  This is a required attribute. 
 * <li>implementation  - class name of the object that will be used to delegate
 *                method calls to.  This is a required attribute.
 * <li>singleton - if set to "true", then the method calls of multiple
 *                aspect object will be directed to a single instance of
 *                the delegate.  This makes the adaptor a singleton. 
 * </ul>
 * 
 * @author <a href="mailto:hchirino@jboss.org">Hiram Chirino</a>
 * 
 */
public class AdaptorInterceptor implements AspectInterceptor, Serializable
{

    public static final Namespace NAMESPACE = Namespace.get(AdaptorInterceptor.class.getName());
    public static final QName ATTR_ADAPTOR = new QName("adaptor", NAMESPACE);
    public static final QName ATTR_IMPLEMENTATION = new QName("implementation", NAMESPACE);
    public static final QName ATTR_SIGLETON = new QName("singleton", NAMESPACE);

    public Object singeltonObject;
    public Class implementingClass;
    public Class adaptorClass;

    static final Method GET_ADAPTER_METHOD;
    static {
        Method m = null;
        try
        {
            m = Adaptor.class.getMethod("getAdapter", new Class[] { Class.class });
        }
        catch (NoSuchMethodException e)
        {
        }
        GET_ADAPTER_METHOD = m;
    }

    /**
     * @see org.jboss.aspect.spi.AspectInterceptor#invoke(AspectInvocation)
     */
    public Object invoke(AspectInvocation invocation) throws Throwable
    {

        if (!adaptorClass.equals(invocation.args[0]))
        {
            if (invocation.isNextIntrestedInMethodCall())
                return invocation.invokeNext();
            return null;
        }

        Object o = null;
        if (singeltonObject != null)
        {
            o = singeltonObject;
        }
        else
        {
            Map attachments = invocation.attachments;
            o = attachments.get(this);
            if (o == null)
            {
                o = implementingClass.newInstance();
                attachments.put(this, o);
            }
        }
        return o;
    }

    /**
     * Builds a Config object for the interceptor.
     * 
     * @see org.jboss.aspect.spi.AspectInterceptor#init(Element)
     */
    public void init(Element xml) throws AspectInitizationException
    {
        try
        {
            String adaptorName = xml.attribute(ATTR_ADAPTOR).getValue();
            String className = xml.attribute(ATTR_IMPLEMENTATION).getValue();

            adaptorClass = Classes.loadClass(adaptorName);
            implementingClass = Classes.loadClass(className);

            String singlton = xml.attribute(ATTR_SIGLETON) == null ? null : xml.attribute(ATTR_SIGLETON).getValue();
            if ("true".equals(singlton))
                singeltonObject = implementingClass.newInstance();

        }
        catch (Exception e)
        {
            throw new AspectInitizationException("Aspect Interceptor missconfigured: ", e);
        }
    }

    /**
     * @see org.jboss.aspect.spi.AspectInterceptor#getInterfaces()
     */
    public Class[] getInterfaces()
    {
        return new Class[] { Adaptor.class };
    }

    public boolean isIntrestedInMethodCall(Method method)
    {
        return GET_ADAPTER_METHOD.equals(method);
    }
}
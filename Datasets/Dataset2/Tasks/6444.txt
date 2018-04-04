import org.jboss.mx.util.MBeanServerLocator;

/***************************************
 *                                     *
 *  JBoss: The OpenSource J2EE WebOS   *
 *                                     *
 *  Distributable under LGPL license.  *
 *  See terms of license at gnu.org.   *
 *                                     *
 ***************************************/
package org.jboss.aspect.interceptors;

import java.lang.reflect.Method;
import java.security.Principal;
import java.util.ArrayList;
import java.util.Iterator;

import javax.management.MBeanServer;
import javax.management.ObjectName;
import javax.transaction.Transaction;

import org.dom4j.Element;
import org.dom4j.Namespace;
import org.dom4j.QName;
import org.jboss.aspect.AspectInitizationException;
import org.jboss.aspect.spi.AspectInterceptor;
import org.jboss.aspect.spi.AspectInvocation;
import org.jboss.invocation.Invocation;
import org.jboss.util.Classes;
import org.jboss.util.jmx.MBeanServerLocator;

/**
 * The JMXInvokerInterceptor allows pass down method invocations
 * through the JBossMX interceptor stack.
 * 
 * This interceptor uses the following configuration attributes:
 * <ul>
 * <li>mbean  -  The JMX MBean that will will be sending the method invocations to. 
 * </ul>
 * 
 * @author <a href="mailto:hchirino@jboss.org">Hiram Chirino</a>
 * 
 */
public class JMXInvokerInterceptor implements AspectInterceptor
{
    public static final Namespace NAMESPACE = Namespace.get(JMXInvokerInterceptor.class.getName());
    public static final QName ATTR_MBEAN = new QName("mbean", NAMESPACE);
    public static final QName ELEM_EXPOSE_INTERFACE = new QName("expose-interface", NAMESPACE);
    public static final QName ATTR_CLASS = new QName("class", NAMESPACE);

    public static final Object TRANSACTION_KEY = "tx";
    public static final Object PRINCIPLE_KEY = "principle";
    public static final Object CREDENTIAL_KEY = "principle";

    MBeanServer server;
    ObjectName mbean;
    Class exposedInterfaces[];

    public JMXInvokerInterceptor()
    {
    }

    public JMXInvokerInterceptor(MBeanServer server, ObjectName mbean)
    {
        this.server = server;
        this.mbean = mbean;
    }

    /**
     * @see org.jboss.aspect.spi.AspectInterceptor#invoke(AspectInvocation)
     */
    public Object invoke(AspectInvocation invocation) throws Throwable
    {
        if (server == null)
            server = MBeanServerLocator.locate();

        // I think that we will eventuraly get the following values out
        // of ThreadLocals instead of the DP attachments.
        Transaction tx = (Transaction) invocation.aspectAttachments.get(TRANSACTION_KEY);
        Principal principle = (Principal) invocation.aspectAttachments.get(PRINCIPLE_KEY);
        Object credentials = (Object) invocation.aspectAttachments.get(CREDENTIAL_KEY);

        // Convert the AspectInvocation into a JBoss Invocation
        Invocation jmxInvocation =
            new Invocation(invocation.targetObject, invocation.method, invocation.args, tx, principle, credentials);

        return server.invoke(mbean, "", new Object[] { jmxInvocation }, Invocation.INVOKE_SIGNATURE);
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
            ClassLoader cl = Classes.getContextClassLoader();
            String mbean = xml.attribute(ATTR_MBEAN).getValue();
            this.mbean = new ObjectName(mbean);

            ArrayList al = new ArrayList();
            Iterator i = xml.elementIterator(ELEM_EXPOSE_INTERFACE);
            while (i.hasNext())
            {
                Element iXML = (Element) i.next();
                String s = iXML.attribute(ATTR_CLASS).getValue();
                al.add(cl.loadClass(s));
            }
            exposedInterfaces = new Class[al.size()];
            al.toArray(exposedInterfaces);

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
        return exposedInterfaces;
    }

    /**
     * @see org.jboss.aspect.spi.AspectInterceptor#isIntrestedInMethodCall(Method)
     */
    public boolean isIntrestedInMethodCall(Method method)
    {
        return true;
    }

}
@version $Revision: 1.2 $

/*
* JBoss, the OpenSource EJB server
*
* Distributable under LGPL license.
* See terms of license at gnu.org.
*/
package org.jboss.ejb;

import java.util.ArrayList;
import java.util.Iterator;

import org.w3c.dom.Element;

import org.jboss.logging.Logger;
import org.jboss.metadata.MetaData;

/** A utility class that manages the handling of the container-interceptors
child element of the container-configuration.

@author Scott_Stark@displayscape.com
@version $Revision: 1.1 $
*/
public class ContainerInterceptors
{
    public static final int BMT = 1;
    public static final int CMT = 2;
    public static final int ANY = 3;
    static final String BMT_VALUE = "Bean";
    static final String CMT_VALUE = "Container";
    static final String ANY_VALUE = "Both";

    /** Given a container-interceptors element of a container-configuration,
    add the indicated interceptors to the container depending on the container
    transcation type and metricsEnabled flag.

    @param container, the container instance to setup.
    @param transType, one of the BMT, CMT or ANY constants.
    @param metricsEnabled, the ContainerFactoryMBean.metricsEnabled flag
    @param element, the container-interceptors element from the container-configuration.
    */
    public static void addInterceptors(Container container, int transType, boolean metricsEnabled, Element element)
    {
        // Get the interceptor stack(either jboss.xml or standardjboss.xml)
        Iterator interceptorElements = MetaData.getChildrenByTagName(element, "interceptor");
        String transaction = stringTransactionValue(transType);
        ClassLoader loader = container.getClassLoader();
        // First build the container interceptor stack from interceptorElements
        ArrayList istack = new ArrayList();
        while( interceptorElements != null && interceptorElements.hasNext() )
        {
            Element ielement = (Element) interceptorElements.next();
            String transAttr = ielement.getAttribute("transaction");
            if( transAttr.length() == 0 || transAttr.equalsIgnoreCase(transaction) )
            {   // The transaction type matches the container bean trans type, check the metricsEnabled
                String metricsAttr = ielement.getAttribute("metricsEnabled");
                boolean metricsInterceptor = metricsAttr.equalsIgnoreCase("true");
                if( metricsEnabled == false && metricsInterceptor == true )
                    continue;

                String className = null;
                try
                {
                    className = MetaData.getElementContent(ielement);
                    Class clazz = loader.loadClass(className);
                    Interceptor interceptor = (Interceptor) clazz.newInstance();
                    istack.add(interceptor);
                }
                catch(Exception e)
                {
                     Logger.warning("Could not load the "+className+" interceptor for this container");
                     Logger.exception(e);
                }
            }
        }

        if( istack.size() == 0 )
            Logger.warning("There are no interceptors configured. Check the standardjboss.xml file");

        // Now add the interceptors to the container
        for(int i = 0; i < istack.size(); i ++)
        {
            Interceptor interceptor = (Interceptor) istack.get(i);
            container.addInterceptor(interceptor);
        }
        // Finally we add the last interceptor from the container
        container.addInterceptor(container.createContainerInterceptor());
    }

    static String stringTransactionValue(int transType)
    {
        String transaction = ANY_VALUE;
        switch( transType )
        {
            case BMT:
                transaction = BMT_VALUE;
            break;
            case CMT:
                transaction = CMT_VALUE;
            break;
        }
        return transaction;
    }
}
ObjectName OBJECT_NAME = ObjectNameFactory.create("jboss:type=example,name=schedulable");

/*
 * JBoss, the OpenSource J2EE webOS
 *
 * Distributable under LGPL license.
 * See terms of license at gnu.org.
 */
package org.jboss.util;

import java.util.Date;

import javax.management.Notification;
import javax.management.ObjectName;

import org.jboss.system.ServiceMBean;

/**
 *
 * @author <a href="mailto:andreas.schaefer@madplanet.com">Andreas Schaefer</a>
 **/
public interface SchedulableExampleMBean
   extends ServiceMBean
{
   // -------------------------------------------------------------------------
   // Constants
   // -------------------------------------------------------------------------  
   
   public static final String OBJECT_NAME = "jboss:type=example,name=schedulable";
   
   // -------------------------------------------------------------------------
   // Methods
   // -------------------------------------------------------------------------
   
   public void hit( Notification lNotification, Date lDate, long lRepetitions, ObjectName lName, String lTest );
   
}
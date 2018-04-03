@version $Revision: 1.3 $

/*
* JBoss, the OpenSource J2EE webOS
*
* Distributable under LGPL license.
* See terms of license at gnu.org.
*/
package org.jboss.logging.log4j;

import org.apache.log4j.Priority;

/** Adds a trace priority that is below the standard log4j DEBUG priority.
 This is a custom priority that is 100 below the Priority.DEBUG_INT and
 represents a lower priority useful for logging events that should only
 be displayed when deep debugging is required.
 
 @see org.apache.log4j.Category
 @see org.apache.log4j.Priority
 
 @author Scott.Stark@jboss.org
 @version $Revision: 1.2 $
 */
public class TracePriority extends Priority
{
  // Constants -----------------------------------------------------
   /** The integer representation of the priority, (Priority.DEBUG_INT - 100) */
   public static final int TRACE_INT = Priority.DEBUG_INT - 100;
   /** The TRACE priority object singleton */
   public static final TracePriority TRACE = new TracePriority(TRACE_INT, "TRACE");
  
  // Attributes ----------------------------------------------------

  // Static --------------------------------------------------------
   /** Convert an integer passed as argument to a priority. If the conversion
    fails, then this method returns the specified default.
    @return the Priority object for name if one exists, defaultPriority otherwize.
    */
   public static Priority toPriority(String name, Priority defaultPriority)
   {
      if( name == null )
         return TRACE;
      
      Priority p = TRACE;
      if( name.charAt(0) != 'T' )
         p = Priority.toPriority(name, defaultPriority);
      return p;
   }
   /** Convert an integer passed as argument to a priority. If the conversion
    fails, then this method returns the specified default.
    @return the Priority object for i if one exists, defaultPriority otherwize.
    */
   public static Priority toPriority(int i, Priority defaultPriority)
   {
      Priority p;
      if( i == TRACE_INT )
         p = TRACE;
      else
         p = Priority.toPriority(i);
      return p;
   }

  // Constructors --------------------------------------------------
   protected TracePriority(int level, String strLevel)
   {
      super(level, strLevel, 7);
   }
   
}
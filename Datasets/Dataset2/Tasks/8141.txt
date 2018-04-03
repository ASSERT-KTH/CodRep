@version $Revision: 1.4 $

/*
* JBoss, the OpenSource J2EE webOS
*
* Distributable under LGPL license.
* See terms of license at gnu.org.
*/
package org.jboss.logging.log4j;

import org.apache.log4j.Category;
import org.apache.log4j.spi.CategoryFactory;

/** A custom log4j category that adds support for trace() level logging.
@see #trace(String)
@see #trace(String, Throwable)
@see TracePriority

@author Scott.Stark@jboss.org
@version $Revision: 1.3 $
*/
public class JBossCategory extends Category
{
   // Constants -----------------------------------------------------

   // Attributes ----------------------------------------------------
   private static CategoryFactory factory = new JBossCategoryFactory();

   // Static --------------------------------------------------------
   /** This method overrides {@link Category#getInstance} by supplying
   its own factory type as a parameter.
   */
   public static Category getInstance(String name)
   {
      return Category.getInstance(name, factory); 
   }
   /** This method overrides {@link Category#getInstance} by supplying
   its own factory type as a parameter.
   */
   public static Category getInstance(Class clazz)
   {
      return Category.getInstance(clazz.getName(), factory); 
   }

  // Constructors --------------------------------------------------
   /** Creates new JBossCategory with the given category name.
    @param name, the category name.
   */
   public JBossCategory(String name)
   {
      super(name);
   }

   /** Check to see if the TRACE priority is enabled for this category.
   @return true if a {@link #trace(String)} method invocation would pass
   the msg to the configured appenders, false otherwise.
   */
   public boolean isTraceEnabled()
   {
      if( hierarchy.isDisabled(TracePriority.TRACE_INT) )
         return false;
      return TracePriority.TRACE.isGreaterOrEqual(this.getChainedPriority());
   }

   /** Issue a log msg with a priority of TRACE.
   Invokes super.log(TracePriority.TRACE, message);
   */
   public void trace(Object message)
   {
      super.log(TracePriority.TRACE, message);
   }
   /** Issue a log msg and throwable with a priority of TRACE.
   Invokes super.log(TracePriority.TRACE, message, t);
   */
   public void trace(Object message, Throwable t)
   {
      super.log(TracePriority.TRACE, message, t);
   }

   // Inner classes -------------------------------------------------
   /** The CategoryFactory implementation for the custom JBossCategory.
   */
   public static class JBossCategoryFactory implements CategoryFactory
   {
      public Category makeNewCategoryInstance(String name)
      {
         return new JBossCategory(name);
      }
   }
}
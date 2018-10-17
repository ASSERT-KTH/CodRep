import org.jboss.persistence.schema.AbstractType;

/***************************************
 *                                     *
 *  JBoss: The OpenSource J2EE WebOS   *
 *                                     *
 *  Distributable under LGPL license.  *
 *  See terms of license at gnu.org.   *
 *                                     *
 ***************************************/

package org.jboss.cmp.ejb;

import org.jboss.cmp.schema.AbstractType;

public class JavaType implements AbstractType
{
   private String name;
   private int family;

   public JavaType(Class clazz, int family)
   {
      this.name = clazz.getName();
      this.family = family;
   }

   public String getName()
   {
      return name;
   }

   public int getFamily()
   {
      return family;
   }
}
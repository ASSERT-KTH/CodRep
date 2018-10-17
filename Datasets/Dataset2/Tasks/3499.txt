package org.jboss.cmp.ejb.ejbql;

/***************************************
 *                                     *
 *  JBoss: The OpenSource J2EE WebOS   *
 *                                     *
 *  Distributable under LGPL license.  *
 *  See terms of license at gnu.org.   *
 *                                     *
 ***************************************/

package org.jboss.cmp.ejbql;

public class ASTIdentifier extends SimpleNode
{
   private String name;

   public ASTIdentifier(int i)
   {
      super(i);
   }

   public String getName()
   {
      return name;
   }

   public void setName(String name)
   {
      this.name = name;
   }

   public String toString()
   {
      return name;
   }

   public Object jjtAccept(ParserVisitor visitor, Object data) throws CompileException
   {
      return visitor.visit(this, data);
   }
}
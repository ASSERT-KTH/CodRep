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

public class ASTInputParameter extends SimpleNode
{
   public int id;

   public ASTInputParameter(int i)
   {
      super(i);
   }

   public String toString()
   {
      return super.toString() + " id=" + id;
   }

   public Object jjtAccept(ParserVisitor visitor, Object data) throws CompileException
   {
      return visitor.visit(this, data);
   }
}
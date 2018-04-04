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

public class ASTSelect extends SimpleNode
{
   public boolean distinct = false;

   public ASTSelect(int i)
   {
      super(i);
   }

   public Object jjtAccept(ParserVisitor visitor, Object data) throws CompileException
   {
      return visitor.visit(this, data);
   }
}
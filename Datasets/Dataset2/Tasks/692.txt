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

public class ASTEJBQL extends SimpleNode
{
   public ASTEJBQL(int i)
   {
      super(i);
   }

   public Object jjtAccept(ParserVisitor visitor, Object data) throws CompileException
   {
      return visitor.visit(this, data);
   }
}
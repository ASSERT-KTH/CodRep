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

public class ASTPath extends SimpleNode
{
   public ASTPath(int i)
   {
      super(i);
   }

   public Object jjtAccept(ParserVisitor visitor, Object data) throws CompileException
   {
      return visitor.visit(this, data);
   }

   public String toString()
   {
      return toString(jjtGetNumChildren());
   }

   public String toString(int depth)
   {
      StringBuffer buf = new StringBuffer();
      buf.append(jjtGetChild(0).toString());
      for (int i = 1; i < depth; i++)
      {
         buf.append('.');
         buf.append(jjtGetChild(i).toString());
      }
      return buf.toString();
   }
}
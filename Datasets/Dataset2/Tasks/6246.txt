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

public class ASTCondition extends SimpleNode
{
   public boolean not;
   public Token token;

   public ASTCondition(int i)
   {
      super(i);
   }

   public String toString()
   {
      return "Condition: " + (not ? "not " : "") + token;
   }

   public Object jjtAccept(ParserVisitor visitor, Object data) throws CompileException
   {
      return visitor.visit(this, data);
   }
}
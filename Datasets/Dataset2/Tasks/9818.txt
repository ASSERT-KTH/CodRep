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

public abstract class SimpleNode implements VisitableNode
{
   protected VisitableNode parent;
   protected VisitableNode[] children;
   protected int id;

   public SimpleNode(int i)
   {
   }

   public void jjtOpen()
   {
   }

   public void jjtClose()
   {
   }

   public void jjtSetParent(Node n)
   {
      parent = (VisitableNode) n;
   }

   public Node jjtGetParent()
   {
      return parent;
   }

   public void jjtAddChild(Node n, int i)
   {
      if (children == null)
      {
         children = new VisitableNode[i + 1];
      }
      else if (i >= children.length)
      {
         VisitableNode c[] = new VisitableNode[i + 1];
         System.arraycopy(children, 0, c, 0, children.length);
         children = c;
      }
      children[i] = (VisitableNode) n;
   }

   public Node jjtGetChild(int i)
   {
      return children[i];
   }

   public int jjtGetNumChildren()
   {
      return (children == null) ? 0 : children.length;
   }

   /** Accept the visitor. **/
   public Object jjtAccept(ParserVisitor visitor, Object data) throws CompileException
   {
      return visitor.visit(this, data);
   }

   /** Accept the visitor. **/
   public Object childrenAccept(ParserVisitor visitor, Object data) throws CompileException
   {
      if (children != null)
      {
         for (int i = 0; i < children.length; ++i)
         {
            children[i].jjtAccept(visitor, data);
         }
      }
      return data;
   }
}

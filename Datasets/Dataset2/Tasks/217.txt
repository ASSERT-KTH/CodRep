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

public interface VisitableNode extends Node
{
   public Object jjtAccept(ParserVisitor visitor, Object data) throws CompileException;

   public Object childrenAccept(ParserVisitor visitor, Object data) throws CompileException;
}
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

public interface ParserVisitor
{
   public Object visit(SimpleNode node, Object data) throws CompileException;

   public Object visit(ASTEJBQL node, Object data) throws CompileException;

   public Object visit(ASTSelect node, Object data) throws CompileException;

   public Object visit(ASTFrom node, Object data) throws CompileException;

   public Object visit(ASTIdDeclaration node, Object data) throws CompileException;

   public Object visit(ASTWhere node, Object data) throws CompileException;

   public Object visit(ASTOr node, Object data) throws CompileException;

   public Object visit(ASTAnd node, Object data) throws CompileException;

   public Object visit(ASTNot node, Object data) throws CompileException;

   public Object visit(ASTCondition node, Object data) throws CompileException;

   public Object visit(ASTPath node, Object data) throws CompileException;

   public Object visit(ASTIdentifier node, Object data) throws CompileException;

   public Object visit(ASTInputParameter node, Object data) throws CompileException;

   public Object visit(ASTLiteral node, Object data) throws CompileException;
}
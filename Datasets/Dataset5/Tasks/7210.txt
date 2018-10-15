if (ele instanceof BooleanOperation) {

/*******************************************************************************
 * Copyright (c) 2005, 2007 committers of openArchitectureWare and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     committers of openArchitectureWare - initial API and implementation
 *******************************************************************************/
package org.eclipse.internal.xtend.expression.ast;

public abstract class AbstractExpressionVisitor extends AbstractVisitor {

	@Override
	public final Object visit(final ISyntaxElement ele) {
		Object result = null;
		if (result == null && ele instanceof BooleanOperation) {
			result = visitBooleanOperation((BooleanOperation) ele);
		}
		if (result == null && ele instanceof Cast) {
			result = visitCast((Cast) ele);
		}
		if (result == null && ele instanceof ConstructorCallExpression) {
			result = visitConstructorCallExpression((ConstructorCallExpression) ele);
		}
		if (result == null && ele instanceof GlobalVarExpression) {
			result = visitGlobalVarExpression((GlobalVarExpression) ele);
		}
		if (result == null && ele instanceof ChainExpression) {
			result = visitChainExpression((ChainExpression) ele);
		}
		if (result == null && ele instanceof CollectionExpression) {
			result = visitCollectionExpression((CollectionExpression) ele);
		}
		if (result == null && ele instanceof OperationCall) {
			result = visitOperationCall((OperationCall) ele);
		}
		if (result == null && ele instanceof TypeSelectExpression) {
			result = visitTypeSelectExpression((TypeSelectExpression) ele);
		}
		if (result == null && ele instanceof FeatureCall) {
			result = visitFeatureCall((FeatureCall) ele);
		}
		if (result == null && ele instanceof IfExpression) {
			result = visitIfExpression((IfExpression) ele);
		}
		if (result == null && ele instanceof LetExpression) {
			result = visitLetExpression((LetExpression) ele);
		}
		if (result == null && ele instanceof SwitchExpression) {
			result = visitSwitchExpression((SwitchExpression) ele);
		}
		if (result == null && ele instanceof ListLiteral) {
			result = visitListLiteral((ListLiteral) ele);
		}
		if (result == null && ele instanceof BooleanLiteral) {
			result = visitBooleanLiteral((BooleanLiteral) ele);
		}
		if (result == null && ele instanceof IntegerLiteral) {
			result = visitIntegerLiteral((IntegerLiteral) ele);
		}
		if (result == null && ele instanceof NullLiteral) {
			result = visitNullLiteral((NullLiteral) ele);
		}
		if (result == null && ele instanceof RealLiteral) {
			result = visitRealLiteral((RealLiteral) ele);
		}
		if (result == null && ele instanceof StringLiteral) {
			result = visitStringLiteral((StringLiteral) ele);
		}
		return result;
	}

	protected Object visitBooleanOperation(BooleanOperation node) {
		if (node.getLeft() != null) {
			node.getLeft().accept(this);
		}
		if (node.getRight() != null) {
			node.getRight().accept(this);
		}
		return node;
	}

	protected Object visitCast(Cast node) {
		if (node.getTarget() != null) {
			node.getTarget().accept(this);
		}
		return node;
	}

	protected Object visitConstructorCallExpression(ConstructorCallExpression node) {
		return node;
	}

	protected Object visitGlobalVarExpression(GlobalVarExpression node) {
		return node;
	}

	protected Object visitChainExpression(ChainExpression ce) {
		if (ce.getFirst() != null) {
			ce.getFirst().accept(this);
		}
		if (ce.getNext() != null) {
			ce.getNext().accept(this);
		}
		return ce;
	}

	protected Object visitFeatureCall(FeatureCall fc) {
		if (fc.getTarget() != null) {
			fc.getTarget().accept(this);
		}
		return fc;
	}

	protected Object visitCollectionExpression(CollectionExpression node) {
		if (node.getClosure() != null) {
			node.getClosure().accept(this);
		}
		if (node.getTarget() != null) {
			node.getTarget().accept(this);
		}
		return node;
	}

	protected Object visitOperationCall(OperationCall oc) {
		if (oc.getTarget() != null) {
			oc.getTarget().accept(this);
		}
		if (oc.getParamsAsList() != null) {
			for (Expression expr : oc.getParamsAsList()) {
				expr.accept(this);
			}
		}
		return oc;
	}

	protected Object visitTypeSelectExpression(TypeSelectExpression node) {
		if (node.getTarget() != null) {
			node.getTarget().accept(this);
		}
		return node;
	}

	protected Object visitIfExpression(IfExpression node) {
		if (node.getCondition() != null) {
			node.getCondition().accept(this);
		}
		if (node.getThenPart() != null) {
			node.getThenPart().accept(this);
		}
		if (node.getElsePart() != null) {
			node.getElsePart().accept(this);
		}
		return node;
	}

	protected Object visitLetExpression(LetExpression node) {
		if (node.getTargetExpression() != null) {
			node.getTargetExpression().accept(this);
		}
		if (node.getVarExpression() != null) {
			node.getVarExpression().accept(this);
		}
		return node;
	}

	protected Object visitSwitchExpression(SwitchExpression node) {
		for (Case caze : node.getCases()) {
			if (caze.getCondition() != null) {
				caze.getCondition().accept(this);
			}
			if (caze.getThenPart() != null) {
				caze.getThenPart().accept(this);
			}
		}
		if (node.getSwitchExpr() != null) {
			node.getSwitchExpr().accept(this);
		}
		if (node.getDefaultExpr() != null) {
			node.getDefaultExpr().accept(this);
		}
		return node;
	}

	protected Object visitListLiteral(ListLiteral node) {
		return node;
	}

	protected Object visitBooleanLiteral(BooleanLiteral node) {
		return node;
	}

	protected Object visitIntegerLiteral(IntegerLiteral node) {
		return node;
	}

	protected Object visitNullLiteral(NullLiteral node) {
		return node;
	}

	protected Object visitRealLiteral(RealLiteral node) {
		return node;
	}

	protected Object visitStringLiteral(StringLiteral node) {
		return node;
	}
}
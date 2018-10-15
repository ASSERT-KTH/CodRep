package org.eclipse.wst.xml.vex.ui.internal.action;

/*******************************************************************************
 * Copyright (c) 2004, 2008 John Krasnay and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors:
 *     John Krasnay - initial API and implementation
 *******************************************************************************/
package org.eclipse.wst.xml.vex.core.internal.action;

/**
 * Callback interface called from LayoutUtils.iterateTableCells.
 */
public interface TableCellCallback {

	/**
	 * Called before the first cell in a row is visited.
	 * 
	 * @param row
	 *            Element or IntRange representing the row.
	 * @param rowIndex
	 *            Zero-based index of the row.
	 */
	public void startRow(Object row, int rowIndex);

	/**
	 * Called when a cell is visited.
	 * 
	 * @param row
	 *            Element or IntRange representing the row.
	 * @param cell
	 *            Element or IntRange representing the cell.
	 * @param rowIndex
	 *            Zero-based index of the current row.
	 * @param cellIndex
	 *            Zero-based index of the current cell.
	 */
	public void onCell(Object row, Object cell, int rowIndex, int cellIndex);

	/**
	 * Called after the last cell in a row is visited.
	 * 
	 * @param row
	 *            Element or IntRange representing the row.
	 * @param rowIndex
	 *            Zero-based index of the row.
	 */
	public void endRow(Object row, int rowIndex);

}
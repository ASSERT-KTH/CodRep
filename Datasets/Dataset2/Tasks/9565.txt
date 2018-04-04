.getSelection("mail.table");

//The contents of this file are subject to the Mozilla Public License Version 1.1
//(the "License"); you may not use this file except in compliance with the 
//License. You may obtain a copy of the License at http://www.mozilla.org/MPL/
//
//Software distributed under the License is distributed on an "AS IS" basis,
//WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License 
//for the specific language governing rights and
//limitations under the License.
//
//The Original Code is "The Columba Project"
//
//The Initial Developers of the Original Code are Frederik Dietz and Timo Stich.
//Portions created by Frederik Dietz and Timo Stich are Copyright (C) 2003. 
//
//All Rights Reserved.
package org.columba.mail.gui.tree;

import java.awt.AlphaComposite;
import java.awt.Color;
import java.awt.Cursor;
import java.awt.GradientPaint;
import java.awt.Graphics2D;
import java.awt.Insets;
import java.awt.Point;
import java.awt.Rectangle;
import java.awt.SystemColor;
import java.awt.datatransfer.DataFlavor;
import java.awt.datatransfer.StringSelection;
import java.awt.datatransfer.Transferable;
import java.awt.datatransfer.UnsupportedFlavorException;
import java.awt.dnd.Autoscroll;
import java.awt.dnd.DnDConstants;
import java.awt.dnd.DragGestureEvent;
import java.awt.dnd.DragGestureListener;
import java.awt.dnd.DragSource;
import java.awt.dnd.DragSourceDragEvent;
import java.awt.dnd.DragSourceDropEvent;
import java.awt.dnd.DragSourceEvent;
import java.awt.dnd.DragSourceListener;
import java.awt.dnd.DropTarget;
import java.awt.dnd.DropTargetDragEvent;
import java.awt.dnd.DropTargetDropEvent;
import java.awt.dnd.DropTargetEvent;
import java.awt.dnd.DropTargetListener;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.InputEvent;
import java.awt.geom.AffineTransform;
import java.awt.geom.Rectangle2D;
import java.awt.image.BufferedImage;
import java.io.IOException;

import javax.swing.Icon;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JTree;
import javax.swing.Timer;
import javax.swing.tree.TreePath;

import org.columba.core.logging.ColumbaLogger;
import org.columba.core.main.MainInterface;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.config.FolderItem;
import org.columba.mail.folder.Folder;
import org.columba.mail.folder.command.CopyMessageCommand;
import org.columba.mail.folder.command.MoveMessageCommand;
import org.columba.mail.gui.tree.util.CArrowImage;
import org.columba.mail.gui.tree.util.CTransferableTreePath;

public class FolderTreeDnd
	implements DragGestureListener, DragSourceListener, Autoscroll {

	private TreeController treeController;

	private JTree tree;

	private Folder sourceFolder;

	private DragSource dragSource;

	private TreePath _pathSource; // The path being dragged
	private BufferedImage _imgGhost; // The 'drag image'
	private Point _ptOffset = new Point();
	// Where, in the drag image, the mouse was clicked

	public FolderTreeDnd(TreeController c) {
		this.treeController = c;
		this.tree = treeController.getView();

		/*
		new DropTarget(treeViewer.getFolderTree().getTree(), // component
		DnDConstants.ACTION_COPY_OR_MOVE, // actions
		this); // DropTargetListener
		*/

		dragSource = DragSource.getDefaultDragSource();

		dragSource.createDefaultDragGestureRecognizer(tree,
		// component where drag originates
		DnDConstants.ACTION_MOVE, // actions
		this); // drag gesture listener

		// Also, make this JTree a drag target
		DropTarget dropTarget = new DropTarget(tree, new CDropTargetListener());
		dropTarget.setDefaultActions(DnDConstants.ACTION_MOVE);
	}

	/****************************************** drop ***********************************/

	/*
	public void drop(DropTargetDropEvent event)
	{
	
		final DropTargetDropEvent e = event;
	
		try
		{
			DataFlavor stringFlavor = DataFlavor.stringFlavor;
			Transferable tr = e.getTransferable();
			if (e.isDataFlavorSupported(stringFlavor))
			{
	
				String filename = (String) tr.getTransferData(stringFlavor);
				e.acceptDrop(DnDConstants.ACTION_COPY_OR_MOVE);
	
				System.out.println("string: " + filename);
	
				Point p = e.getLocation();
	
				final TreePath path =
					treeViewer.getFolderTree().getTree().getPathForLocation(p.x, p.y);
	
	
				// we have to use this dropComplete here:
				if (path == null)
				{
					e.dropComplete(false);
					return;
				}
	
				else
				{
	
					if (filename.equals("folder"))
					{
						// folder dnd operation
	
						Folder selectedFolder = treeViewer.getSelected();
						//System.out.println( "folder name: "+ selectedFolder.getName() );
	
						if (selectedFolder.equals(sourceFolder))
						{
							//System.out.println( "source equals destination folder -> ABORTING" );
							e.rejectDrop();
							return;
						}
	
						if (sourceFolder.isParent(selectedFolder))
						{
							//System.out.println( "source is parent folder -> ABORTING" );
							e.rejectDrop();
							return;
						}
	
						selectedFolder.append(sourceFolder);
						TreeNodeEvent updateEvent =
							new TreeNodeEvent(selectedFolder.getParent(), TreeNodeEvent.STRUCTURE_CHANGED);
						MainInterface.crossbar.fireTreeNodeChanged(updateEvent);
						e.dropComplete(true);
					}
					else
					{
						// message dnd operation
	
						Folder selectedFolder = null;
						Folder srcFolder = null;
	
						treeViewer.getFolderTree().getTree().setSelectionPath(path);
	
						selectedFolder = treeViewer.getSelected();
	
						if (selectedFolder != null)
						{
	
							sourceFolder = MainInterface.headerTableViewer.getFolder();
	
							if (selectedFolder == null)
							{
								e.rejectDrop();
								return;
							}
	
							if ((selectedFolder != sourceFolder)
								&& (selectedFolder.getFolderItem().isAddAllowed()))
							{
	
								Object[] uids = MainInterface.headerTableViewer.getUids();
	
								if (e.getDropAction() == 1)
								{
									System.out.println("copy action");
	
									treeViewer.setSelected(sourceFolder);
	
									FolderOperation op =
										new FolderOperation(Operation.COPY, 0, uids, sourceFolder, selectedFolder);
									MainInterface.crossbar.operate(op);
	
									e.dropComplete(true);
	
								}
								else if (e.getDropAction() == 2)
								{
									System.out.println("move action");
	
									treeViewer.setSelected(sourceFolder);
	
									FolderOperation op =
										new FolderOperation(Operation.MOVE, 0, uids, sourceFolder, selectedFolder);
									MainInterface.crossbar.operate(op);
	
									e.dropComplete(true);
	
								}
								else
								{
									System.out.println("drop action not supported");
									e.rejectDrop();
								}
	
							}
							else
							{
								JOptionPane.showMessageDialog(MainInterface.mainFrame, "Invalid Folder!");
								e.rejectDrop();
							}
	
						}
						else
						{
							e.rejectDrop();
						}
	
					}
	
				}
	
			}
			else
			{
				e.rejectDrop();
			}
		}
		catch (IOException ioe)
		{
			ioe.printStackTrace();
			e.rejectDrop();
		}
		catch (UnsupportedFlavorException ufe)
		{
			ufe.printStackTrace();
			e.rejectDrop();
		}
	
	}
	
	public void dragEnter(DropTargetDragEvent e)
	{
	
	}
	
	public void dragExit(DropTargetEvent e)
	{
		System.out.println("dragExit lllllll");
	}
	
	public void dragOver(DropTargetDragEvent e)
	{
	
		Point p = e.getLocation();
	
		TreePath path =
			treeViewer.getFolderTree().getTree().getPathForLocation(p.x, p.y);
	
		if (path == null)
		{
			System.out.println("no treepath");
	
			//e.rejectDrag();
		}
		else
		{
			treeViewer.getFolderTree().getTree().setSelectionPath(path);
	
	
		}
	
		if (e.getDropAction() == 1)
		{
			//copy
			System.out.println("copy");
	
		}
		else if (e.getDropAction() == 2)
		{
			//movee
	
			System.out.println("move");
		}
		else
		{
	
		}
	}
	
	public void dropActionChanged(DropTargetDragEvent e)
	{
	}
	*/

	/********************************** drag ********************************************/

	public void dragGestureRecognized(DragGestureEvent e) {

		InputEvent event = e.getTriggerEvent();
		int mod = event.getModifiers();

		if ((mod & InputEvent.BUTTON2_MASK) == InputEvent.BUTTON2_MASK) {
			System.out.println("drag n drop action initiated");

			sourceFolder = (Folder) treeController.getSelected();
			FolderItem item = sourceFolder.getFolderItem();
			String access = item.get("property", "accessrights");

			/*
			if ((access.equals("user"))
				&& (!type.equals("imap"))
				&& (!type.equals("imaproot")))
			{
				e.startDrag(DragSource.DefaultMoveDrop,
				//ImageLoader.getImageIcon("","folder1").getImage(),
				//new Point(10,10), // cursor
				new StringSelection("folder"), // transferable
				this); // drag source listener
			}
			*/
			e.startDrag(DragSource.DefaultMoveDrop,
			//ImageLoader.getImageIcon("","folder1").getImage(),
			//new Point(10,10), // cursor
			new StringSelection("folder"), // transferable
			this); // drag source listener

		}

		Point ptDragOrigin = e.getDragOrigin();
		TreePath path = tree.getPathForLocation(ptDragOrigin.x, ptDragOrigin.y);
		if (path == null)
			return;
		if (isRootPath(path))
			return; // Ignore user trying to drag the root node

		Folder folder = (Folder) path.getLastPathComponent();
		FolderItem item = folder.getFolderItem();
		String access = item.get("property", "accessrights");

		if (access.equals("system"))
			return;
		/*
		String type = item.getType();
		
		if (access.equals("system"))
			return;
		if (type.equals("imaproot"))
			return;
		*/

		// Work out the offset of the drag point from the TreePath bounding rectangle origin
		Rectangle raPath = tree.getPathBounds(path);
		_ptOffset.setLocation(
			ptDragOrigin.x - raPath.x,
			ptDragOrigin.y - raPath.y);

		// Get the cell renderer (which is a JLabel) for the path being dragged
		JLabel lbl =
			(JLabel) tree.getCellRenderer().getTreeCellRendererComponent(tree,
			// tree
		path.getLastPathComponent(), // value
		false, // isSelected	(dont want a colored background)
		tree.isExpanded(path), // isExpanded
		tree.getModel().isLeaf(path.getLastPathComponent()), // isLeaf
		0, // row			(not important for rendering)
		false // hasFocus		(dont want a focus rectangle)
	);
		lbl.setSize((int) raPath.getWidth(), (int) raPath.getHeight());
		// <-- The layout manager would normally do this

		// Get a buffered image of the selection for dragging a ghost image
		_imgGhost =
			new BufferedImage(
				(int) raPath.getWidth(),
				(int) raPath.getHeight(),
				BufferedImage.TYPE_INT_ARGB_PRE);
		Graphics2D g2 = _imgGhost.createGraphics();

		// Ask the cell renderer to paint itself into the BufferedImage
		g2.setComposite(AlphaComposite.getInstance(AlphaComposite.SRC, 0.5f));
		// Make the image ghostlike
		lbl.paint(g2);

		// Now paint a gradient UNDER the ghosted JLabel text (but not under the icon if any)
		// Note: this will need tweaking if your icon is not positioned to the left of the text
		Icon icon = lbl.getIcon();
		int nStartOfText =
			(icon == null) ? 0 : icon.getIconWidth() + lbl.getIconTextGap();
		g2.setComposite(
			AlphaComposite.getInstance(AlphaComposite.DST_OVER, 0.5f));
		// Make the gradient ghostlike
		g2.setPaint(
			new GradientPaint(
				nStartOfText,
				0,
				SystemColor.controlShadow,
				tree.getWidth(),
				0,
				new Color(255, 255, 255, 0)));
		g2.fillRect(nStartOfText, 0, tree.getWidth(), _imgGhost.getHeight());

		g2.dispose();

		tree.setSelectionPath(path); // Select this path in the tree

		System.out.println("DRAGGING: " + path.getLastPathComponent());

		// Wrap the path being transferred into a Transferable object
		Transferable transferable = new CTransferableTreePath(path);

		// Remember the path being dragged (because if it is being moved, we will have to delete it later)
		_pathSource = path;

		// We pass our drag image just in case it IS supported by the platform
		//e.startDrag(DragSource.DefaultMoveDrop, _imgGhost, new Point(5,5), transferable, this);
		e.startDrag(
			new Cursor(Cursor.DEFAULT_CURSOR),
			_imgGhost,
			new Point(5, 5),
			transferable,
			this);
		//tree.setCursor( new Cursor(Cursor.DEFAULT_CURSOR) );
	}

	public void dragDropEnd(DragSourceDropEvent e) {
		//System.out.println("dragdropend");
		if (e.getDropSuccess()) {
			int nAction = e.getDropAction();
			if (nAction == DnDConstants.ACTION_MOVE) {
				// The dragged item (_pathSource) has been inserted at the target selected by the user.
				// Now it is time to delete it from its original location.
				//System.out.println("REMOVING: " + _pathSource.getLastPathComponent());

				tree.repaint();
				// .
				// .. ask your TreeModel to delete the node
				// .

				_pathSource = null;
			}
		}
	}

	public void dragExit(DragSourceEvent e) {
		//System.out.println("dragexit");
		//tree.setCursor( new Cursor(Cursor.DEFAULT_CURSOR) );
	}

	public void dragEnter(DragSourceDragEvent e) {
		//System.out.println("start enter");
		//tree.setCursor( new Cursor(Cursor.DEFAULT_CURSOR) );
	}

	public void dragOver(DragSourceDragEvent e) {
		//System.out.println("dragover");
		//tree.setCursor( new Cursor(Cursor.DEFAULT_CURSOR) );
	}
	public void dropActionChanged(DragSourceDragEvent e) {
		//System.out.println("dragactioncahnged");
		//tree.setCursor( new Cursor(Cursor.DEFAULT_CURSOR) );
	}

	class CDropTargetListener implements DropTargetListener {
		// Fields...
		private TreePath _pathLast = null;
		private Rectangle2D _raCueLine = new Rectangle2D.Float();
		private Rectangle2D _raGhost = new Rectangle2D.Float();
		private Color _colorCueLine;
		private Point _ptLast = new Point();
		private Timer _timerHover;
		private int _nLeftRight = 0; // Cumulative left/right mouse movement
		private BufferedImage _imgRight =
			new CArrowImage(15, 15, CArrowImage.ARROW_RIGHT);
		private BufferedImage _imgLeft =
			new CArrowImage(15, 15, CArrowImage.ARROW_LEFT);
		private int _nShift = 0;

		// Constructor...
		public CDropTargetListener() {
			_colorCueLine =
				new Color(
					SystemColor.controlShadow.getRed(),
					SystemColor.controlShadow.getGreen(),
					SystemColor.controlShadow.getBlue(),
					64);

			// Set up a hover timer, so that a node will be automatically expanded or collapsed
			// if the user lingers on it for more than a short time
			_timerHover = new Timer(1000, new ActionListener() {
				public void actionPerformed(ActionEvent e) {
					_nLeftRight = 0; // Reset left/right movement trend

					if (isRootPath(_pathLast))
						return;
					// Do nothing if we are hovering over the root node

					if (tree.isExpanded(_pathLast))
						tree.collapsePath(_pathLast);
					else
						tree.expandPath(_pathLast);
				}
			});
			_timerHover.setRepeats(false); // Set timer to one-shot mode
		}

		// DropTargetListener interface
		public void dragEnter(DropTargetDragEvent e) {
			if (!isDragAcceptable(e))
				e.rejectDrag();
			else
				e.acceptDrag(e.getDropAction());
		}

		public void dragExit(DropTargetEvent e) {
			if (!DragSource.isDragImageSupported()) {
				tree.repaint(_raGhost.getBounds());
			}
		}

		/**
		* This is where the ghost image is drawn
		*/
		public void dragOver(DropTargetDragEvent e) {

			DataFlavor[] flavors = e.getCurrentDataFlavors();
			for (int i = 0; i < flavors.length; i++) {
				DataFlavor flavor = flavors[i];
				if (flavor.equals(DataFlavor.stringFlavor)) {
					//System.out.println("message dnd");
					return;
				}
			}

			// Even if the mouse is not moving, this method is still invoked 10 times per second
			Point pt = e.getLocation();
			if (pt.equals(_ptLast))
				return;

			// Try to determine whether the user is flicking the cursor right or left
			int nDeltaLeftRight = pt.x - _ptLast.x;
			if ((_nLeftRight > 0 && nDeltaLeftRight < 0)
				|| (_nLeftRight < 0 && nDeltaLeftRight > 0))
				_nLeftRight = 0;
			_nLeftRight += nDeltaLeftRight;

			_ptLast = pt;

			Graphics2D g2 = (Graphics2D) tree.getGraphics();

			// If a drag image is not supported by the platform, then draw my own drag image
			if (!DragSource.isDragImageSupported()) {
				tree.paintImmediately(_raGhost.getBounds());
				// Rub out the last ghost image and cue line
				// And remember where we are about to draw the new ghost image
				_raGhost.setRect(
					pt.x - _ptOffset.x,
					pt.y - _ptOffset.y,
					_imgGhost.getWidth(),
					_imgGhost.getHeight());
				g2.drawImage(
					_imgGhost,
					AffineTransform.getTranslateInstance(
						_raGhost.getX(),
						_raGhost.getY()),
					null);
			} else // Just rub out the last cue line
				tree.paintImmediately(_raCueLine.getBounds());

			TreePath path = tree.getClosestPathForLocation(pt.x, pt.y);
			if (!(path == _pathLast)) {
				_nLeftRight = 0;
				// We've moved up or down, so reset left/right movement trend
				_pathLast = path;
				_timerHover.restart();
			}

			Point pt2 = e.getLocation();
			TreePath pathTarget = tree.getClosestPathForLocation(pt2.x, pt2.y);
			/*
			int row2 = tree.getClosestRowForLocation(pt2.x,pt2.y);
			Rectangle r2 = tree.getRowBounds(row2);
			*/

			Folder folder = (Folder) pathTarget.getLastPathComponent();

			// In any case draw (over the ghost image if necessary) a cue line indicating where a drop will occur
			Rectangle raPath = tree.getPathBounds(path);

			Rectangle raPath2 = (Rectangle) raPath.clone();
			//raPath2.y = raPath2.y + 1;
			raPath2.height = raPath2.height;
			if (raPath2.contains(pt2.x, pt2.y)) {
				System.out.println("direct collision");
			} else {
				/*
				if (folder.isLeaf())
				{
				}
				else
				{
				*/
				_raCueLine.setRect(
					0,
					raPath.y + (int) raPath.getHeight(),
					tree.getWidth(),
					2);

				g2.setColor(_colorCueLine);
				g2.fill(_raCueLine);
				//}
			}

			// Now superimpose the left/right movement indicator if necessary
			if (_nLeftRight > 20) {
				g2.drawImage(
					_imgRight,
					AffineTransform.getTranslateInstance(
						pt.x - _ptOffset.x,
						pt.y - _ptOffset.y),
					null);
				_nShift = +1;
			} else if (_nLeftRight < -20) {
				g2.drawImage(
					_imgLeft,
					AffineTransform.getTranslateInstance(
						pt.x - _ptOffset.x,
						pt.y - _ptOffset.y),
					null);
				_nShift = -1;
			} else
				_nShift = 0;

			// And include the cue line in the area to be rubbed out next time
			_raGhost = _raGhost.createUnion(_raCueLine);

			/*
						// Do this if you want to prohibit dropping onto the drag source
						if (path.equals(_pathSource))
							e.rejectDrag();
						else
							e.acceptDrag(e.getDropAction());
			*/
		}

		public void dropActionChanged(DropTargetDragEvent e) {
			if (!isDragAcceptable(e))
				e.rejectDrag();
			else
				e.acceptDrag(e.getDropAction());
		}

		public void drop(DropTargetDropEvent e) {
			_timerHover.stop();
			// Prevent hover timer from doing an unwanted expandPath or collapsePath

			if (!isDropAcceptable(e)) {
				e.rejectDrop();
				return;
			}

			e.acceptDrop(e.getDropAction());

			Transferable transferable = e.getTransferable();

			DataFlavor[] flavors = transferable.getTransferDataFlavors();
			for (int i = 0; i < flavors.length; i++) {
				DataFlavor flavor = flavors[i];
				if (flavor.equals(DataFlavor.stringFlavor)) {

					System.out.println("message dnd");
					Point pt = e.getLocation();
					TreePath pathTarget =
						tree.getClosestPathForLocation(pt.x, pt.y);
					Folder target = (Folder) pathTarget.getLastPathComponent();

					FolderCommandReference[] selection =
						(FolderCommandReference[]) treeController
							.getMailFrameController()
							.getSelectionManager()
							.getSelection("mail.headertable");

					/*
					Folder sourceFolder =
						(Folder) treeController
							.getMailFrameController()
							.tableController
							.getTableSelectionManager()
							.getFolder();
					
					**/
					if ((target != selection[0].getFolder())) {

						/*
						Object[] uids =
							treeController
								.getMailFrameController()
								.tableController
								.getTableSelectionManager()
								.getUids();
						*/
						FolderCommandReference[] result =
							new FolderCommandReference[2];

						result[0] = selection[0];
						result[1] = new FolderCommandReference(target);

						if (e.getDropAction() == 1) {
							ColumbaLogger.log.debug("copy action");

							//treeViewer.setSelected(sourceFolder);

							CopyMessageCommand c =
								new CopyMessageCommand(result);

							MainInterface.processor.addOp(c);

							// FIXME
							/*
							FolderOperation op =
								new FolderOperation(Operation.COPY, 0, uids, sourceFolder, target);
							MainInterface.crossbar.operate(op);
							*/

							e.dropComplete(true);

						} else if (e.getDropAction() == 2) {
							System.out.println("move action");

							MoveMessageCommand c =
								new MoveMessageCommand(result);

							MainInterface.processor.addOp(c);
							//treeViewer.setSelected(sourceFolder);

							// FIXME
							/*
							FolderOperation op =
								new FolderOperation(Operation.MOVE, 0, uids, sourceFolder, target);
							MainInterface.crossbar.operate(op);
							*/

							e.dropComplete(true);

						} else {
							ColumbaLogger.log.debug("drop action not supported");
							break;
						}

					} else {
						JOptionPane.showMessageDialog(null, "Invalid Folder!");
						break;
					}

				} else if (
					flavor.isMimeTypeEqual(
						DataFlavor.javaJVMLocalObjectMimeType)) {
					try {
						Point pt = e.getLocation();
						TreePath pathTarget =
							tree.getClosestPathForLocation(pt.x, pt.y);
						TreePath pathSource =
							(TreePath) transferable.getTransferData(flavor);

						System.out.println(
							"DROPPING: " + pathSource.getLastPathComponent());
						javax.swing.tree.TreeModel model =
							treeController.getModel();
						TreePath pathNewChild = null;

						Folder source =
							(Folder) pathSource.getLastPathComponent();
						FolderItem item = source.getFolderItem();
						//String type = item.getType();
						Folder dest =
							(Folder) pathTarget.getLastPathComponent();

						Rectangle raPath = tree.getPathBounds(pathTarget);

						Rectangle raPath2 = (Rectangle) raPath.clone();
						//raPath2.y = raPath2.y + 1;
						raPath2.height = raPath2.height;
						if (raPath2.contains(pt.x, pt.y)) {
							//System.out.println("direct collision");
							Folder sourceParent = (Folder) source.getParent();
							Folder destParent = (Folder) dest.getParent();

							if (sourceParent.equals(dest)) {
								// these drops don't make sense
								JOptionPane.showMessageDialog(
									null,
									"No valid folder for drop!");
							} else {

								System.out.println(
									"------------> append at="
										+ dest.getName());

								dest.append(source);

								MainInterface.treeModel.nodeStructureChanged(
									destParent);
								//MainInterface.treeModel.nodeStructureChanged(sourceParent);
								/*
								TreeNodeEvent updateEvent =
									new TreeNodeEvent(destParent, TreeNodeEvent.STRUCTURE_CHANGED);
								MainInterface.crossbar.fireTreeNodeChanged(updateEvent);
								*/
							}
						} else {
							Folder destParent = (Folder) dest.getParent();
							int count = destParent.getChildCount();
							int destIndex = destParent.getIndex(dest);
							Folder sourceParent = (Folder) source.getParent();
							int sourceIndex = sourceParent.getIndex(source);
							ColumbaLogger.log.debug(
								"source=" + source.getName());
							ColumbaLogger.log.debug("dest=" + dest.getName());

							if (source.getParent().equals(dest)) {
								// these drops don't make sense
								JOptionPane.showMessageDialog(
									null,
									"No valid folder for drop!");
							} else if (sourceParent.equals(destParent)) {
								ColumbaLogger.log.debug(
									"-------------> insert at:" + destIndex);
								ColumbaLogger.log.debug(
									"-------------> insert from:"
										+ sourceIndex);

								//destParent.insert(source, destIndex);

								if (sourceIndex < destIndex) {
									// move treenode up
									destParent.insert(source, destIndex);
								} else {
									// move treenode down
									destParent.insert(source, destIndex + 1);
								}

								MainInterface.treeModel.nodeStructureChanged(
									destParent);
								// FIXME
								/*
								TreeNodeEvent updateEvent =
									new TreeNodeEvent(dest.getParent(), TreeNodeEvent.STRUCTURE_CHANGED);
								ainInterface.crossbar.fireTreeNodeChanged(updateEvent);
								*/
							} else { /*
																												if (type.equals("imap"))
																												{
																													JOptionPane.showMessageDialog(
																														MainInterface.mainFrame,
																														"No valid folder for drop!");
																												}
																												else
																												*/
								if (sourceParent.equals(dest)) {
									// insert treenode at position 0
									// FIXME
									/*
									dest.insert(source, 0);
									TreeNodeEvent updateEvent =
									new TreeNodeEvent(dest, TreeNodeEvent.STRUCTURE_CHANGED);
									MainInterface.crossbar.fireTreeNodeChanged(updateEvent);
									*/
								} else { //destParent.append(source);
									// FIXME
									/*
									destParent.insert(source, destIndex+1);
									TreeNodeEvent updateEvent =
										new TreeNodeEvent(dest.getParent(), TreeNodeEvent.STRUCTURE_CHANGED);
									MainInterface.crossbar.fireTreeNodeChanged(updateEvent);
									
									TreeNodeEvent updateEvent2 =
										new TreeNodeEvent(sourceParent, TreeNodeEvent.STRUCTURE_CHANGED);
									MainInterface.crossbar.fireTreeNodeChanged(updateEvent2);
									*/
								}
							}

						} // .
						// .. Add your code here to ask your TreeModel to copy the node and act on the mouse gestures...
						// .
						// For example:
						// If pathTarget is an expanded BRANCH,
						// 		then insert source UNDER it (before the first child if any)
						// If pathTarget is a collapsed BRANCH (or a LEAF),
						//		then insert source AFTER it
						// 		Note: a leaf node is always marked as collapsed
						// You ask the model to do the copying...
						// ...and you supply the copyNode method in the model as well of course.
						//						if (_nShift == 0)
						//							pathNewChild = model.copyNode(pathSource, pathTarget, isExpanded(pathTarget));
						//						else if (_nShift > 0)	// The mouse is being flicked to the right (so move the node right)
						//							pathNewChild = model.copyNodeRight(pathSource, pathTarget);
						//						else					// The mouse is being flicked to the left (so move the node left)
						//							pathNewChild = model.copyNodeLeft(pathSource);
						if (pathNewChild != null)
							tree.setSelectionPath(pathNewChild);
						// Mark this as the selected path in the tree
						break;
						// No need to check remaining flavors
					} catch (UnsupportedFlavorException ufe) {
						System.out.println(ufe);
						e.dropComplete(false);
						return;
					} catch (IOException ioe) {
						System.out.println(ioe);
						e.dropComplete(false);
						return;
					}
				}
			}

			e.dropComplete(true);
		} // Helpers...
		public boolean isDragAcceptable(DropTargetDragEvent e) { // Only accept COPY or MOVE gestures (ie LINK is not supported)
			if ((e.getDropAction() & DnDConstants.ACTION_COPY_OR_MOVE) == 0)
				return false;
			/*
			// Only accept this particular flavor
			if (!e.isDataFlavorSupported(CTransferableTreePath.TREEPATH_FLAVOR))
				return false;
				*/ /*
																// Do this if you want to prohibit dropping onto the drag source...
																Point pt = e.getLocation();
																TreePath path = getClosestPathForLocation(pt.x, pt.y);
																if (path.equals(_pathSource))
																	return false;
													
													*/ /*
																// Do this if you want to select the best flavor on offer...
																DataFlavor[] flavors = e.getCurrentDataFlavors();
																for (int i = 0; i < flavors.length; i++ )
																{
																	DataFlavor flavor = flavors[i];
																	if (flavor.isMimeTypeEqual(DataFlavor.javaJVMLocalObjectMimeType))
																		return true;
																}
													*/
			return true;
		}

		public boolean isDropAcceptable(DropTargetDropEvent e) { // Only accept COPY or MOVE gestures (ie LINK is not supported)
			if ((e.getDropAction() & DnDConstants.ACTION_COPY_OR_MOVE) == 0)
				return false;
			/*
			// Only accept this particular flavor
			if (!e.isDataFlavorSupported(CTransferableTreePath.TREEPATH_FLAVOR))
				return false;
				*/ /*
																// Do this if you want to prohibit dropping onto the drag source...
																Point pt = e.getLocation();
																TreePath path = getClosestPathForLocation(pt.x, pt.y);
																if (path.equals(_pathSource))
																	return false;
													*/ /*
																// Do this if you want to select the best flavor on offer...
																DataFlavor[] flavors = e.getCurrentDataFlavors();
																for (int i = 0; i < flavors.length; i++ )
																{
																	DataFlavor flavor = flavors[i];
																	if (flavor.isMimeTypeEqual(DataFlavor.javaJVMLocalObjectMimeType))
																		return true;
																}
													*/
			return true;
		}

	} // Autoscroll Interface...
	// The following code was borrowed from the book:
	//		Java Swing
	//		By Robert Eckstein, Marc Loy & Dave Wood
	//		Paperback - 1221 pages 1 Ed edition (September 1998)
	//		O'Reilly & Associates; ISBN: 156592455X
	//
	// The relevant chapter of which can be found at:
	//		http://www.oreilly.com/catalog/jswing/chapter/dnd.beta.pdf
	private static final int AUTOSCROLL_MARGIN = 12;
	// Ok, weve been told to scroll because the mouse cursor is in our
	// scroll zone.
	public void autoscroll(Point pt) {
		// Figure out which row were on.
		int nRow = tree.getRowForLocation(pt.x, pt.y);
		// If we are not on a row then ignore this autoscroll request
		if (nRow < 0)
			return;
		Rectangle raOuter = tree.getBounds();
		// Now decide if the row is at the top of the screen or at the
		// bottom. We do this to make the previous row (or the next
		// row) visible as appropriate. If were at the absolute top or
		// bottom, just return the first or last row respectively.
		nRow = (pt.y + raOuter.y <= AUTOSCROLL_MARGIN)
			// Is row at top of screen?
		? (nRow <= 0 ? 0 : nRow - 1) // Yes, scroll up one row
	: (nRow < tree.getRowCount() - 1 ? nRow + 1 : nRow);
		// No, scroll down one row
		tree.scrollRowToVisible(nRow);
	} // Calculate the insets for the *JTREE*, not the viewport
	// the tree is in. This makes it a bit messy.
	public Insets getAutoscrollInsets() {
		Rectangle raOuter = tree.getBounds();
		Rectangle raInner = tree.getParent().getBounds();
		return new Insets(
			raInner.y - raOuter.y + AUTOSCROLL_MARGIN,
			raInner.x - raOuter.x + AUTOSCROLL_MARGIN,
			raOuter.height
				- raInner.height
				- raInner.y
				+ raOuter.y
				+ AUTOSCROLL_MARGIN,
			raOuter.width
				- raInner.width
				- raInner.x
				+ raOuter.x
				+ AUTOSCROLL_MARGIN);
	} /*
						// Use this method if you want to see the boundaries of the
						// autoscroll active region. Toss it out, otherwise.
						public void paintComponent(Graphics g)
						{
							super.paintComponent(g);
							Rectangle raOuter = getBounds();
							Rectangle raInner = getParent().getBounds();
							g.setColor(Color.red);
							g.drawRect(-raOuter.x + 12, -raOuter.y + 12,
								raInner.width - 24, raInner.height - 24);
						}
					
					*/ /*
					
					// TreeModelListener interface...
					public void treeNodesChanged(TreeModelEvent e)
					{
					System.out.println("treeNodesChanged");
					sayWhat(e);
					// We dont need to reset the selection path, since it has not moved
					}
					
					public void treeNodesInserted(TreeModelEvent e)
					{
					System.out.println("treeNodesInserted ");
					sayWhat(e);
					
					// We need to reset the selection path to the node just inserted
					int nChildIndex = e.getChildIndices()[0];
					TreePath pathParent = e.getTreePath();
					tree.setSelectionPath(getChildPath(pathParent, nChildIndex));
					}
					
					public void treeNodesRemoved(TreeModelEvent e)
					{
					System.out.println("treeNodesRemoved ");
					sayWhat(e);
					}
					
					public void treeStructureChanged(TreeModelEvent e)
					{
					System.out.println("treeStructureChanged ");
					sayWhat(e);
					}
					
					*/ /*
					
					// More helpers...
					private TreePath getChildPath(TreePath pathParent, int nChildIndex)
					{
						TreeModel model =  tree.getModel();
						return pathParent.pathByAddingChild(model.getChild(pathParent.getLastPathComponent(), nChildIndex));
					}
					*/

	private boolean isRootPath(TreePath path) {
		return tree.isRootVisible() && tree.getRowForPath(path) == 0;
	} /*
						private void sayWhat(TreeModelEvent e)
						{
							System.out.println(e.getTreePath().getLastPathComponent());
							int[] nIndex = e.getChildIndices();
							for (int i = 0; i < nIndex.length ;i++ )
							{
								System.out.println(i+". "+nIndex[i]);
							}
						}
						*/
}
.getColor("Menu.selectionForeground");

package org.columba.core.gui.docking;

import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Component;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.event.ActionEvent;
import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;

import javax.swing.AbstractAction;
import javax.swing.ImageIcon;
import javax.swing.JButton;
import javax.swing.JComponent;
import javax.swing.JPopupMenu;
import javax.swing.UIManager;

import org.flexdock.docking.DockingManager;
import org.flexdock.docking.defaults.AbstractDockable;
import org.flexdock.util.DockingUtility;

public class DockableView extends AbstractDockable implements
		PropertyChangeListener {

	public static Color INACTIVE_LABEL_COLOR = UIManager
			.getColor("Menu.foreground");

	public static Color ACTIVE_LABEL_COLOR = UIManager
			.getColor("Menu.selectionForeground");

	private DockingPanel panel;

	private JComponent dragInitiator;

	private TitleBar titleBar;

	private JPopupMenu menu;

	protected JButton menuButton;

	public DockableView(String id, String title) {
		super(id);

		panel = new DockingPanel(id, title);

		titleBar = panel.getTitleBar();

		menuButton = titleBar.addButton(new MenuIcon(), new MenuAction(this
				.getPersistentId()), BorderLayout.WEST);
		titleBar.addButton(new PinIcon(),
				new PinAction(this.getPersistentId()), BorderLayout.EAST);
		titleBar.addButton(new MaximizeIcon(), new MaximizeAction(this
				.getPersistentId()), BorderLayout.EAST);
		titleBar.addButton(new CloseIcon(), new CloseAction(this
				.getPersistentId()), BorderLayout.EAST);

		dragInitiator = panel.getTitleBar();
		setTabText(panel.getTitle());

		getDragSources().add(dragInitiator);
		getFrameDragSources().add(dragInitiator);

		DockingManager.registerDockable(this);
		DockableRegistry.getInstance().register(this);

		addPropertyChangeListener(this);
	}

	public void setPopupMenu(final JPopupMenu menu) {
		if (menu == null)
			throw new IllegalArgumentException("menu == null");

		this.menu = menu;
	}

	public boolean isActive() {
		return getDockingProperties().isActive().booleanValue();
	}

	public void setTitle(String title) {
		TitleBar titleBar = (TitleBar) panel.getTitleBar();
		titleBar.setTitle(title);
	}

	public String getTitle() {
		TitleBar titleBar = (TitleBar) panel.getTitleBar();
		return titleBar.getTitle();
	}

	public void setContentPane(JComponent c) {
		this.panel.setContentPane(c);

	}

	public Component getComponent() {
		return panel;
	}

	class MenuAction extends AbstractAction {
		String id;

		MenuAction(String id) {
			this.id = id;

			putValue(AbstractAction.NAME, "m");
		}

		public void actionPerformed(ActionEvent e) {
			// FIXME: should we align the menu to the left instead?
			// menu.show(b, b.getWidth() - menu.getWidth(), b.getHeight());
			menu.show(menuButton, 0, menuButton.getHeight());

			// menu.setVisible(true);
		}
	}

	class CloseAction extends AbstractAction {
		String id;

		CloseAction(String id) {
			this.id = id;

			putValue(AbstractAction.NAME, "x");
		}

		public void actionPerformed(ActionEvent e) {
			DockingManager.close(DockableView.this);
		}
	}

	class MaximizeAction extends AbstractAction {
		String id;

		MaximizeAction(String id) {
			this.id = id;

			putValue(AbstractAction.NAME, "m");
		}

		public void actionPerformed(ActionEvent e) {
			// DockingManager.(DockableView.this);
		}
	}

	class PinAction extends AbstractAction {
		String id;

		PinAction(String id) {
			this.id = id;

			putValue(AbstractAction.NAME, "P");

		}

		public void actionPerformed(ActionEvent e) {
			boolean minimize = DockingUtility.isMinimized(DockableView.this) ? false
					: true;
			DockingManager.setMinimized(DockableView.this, minimize);

		}
	}

	public void propertyChange(PropertyChangeEvent evt) {

		panel.setActive(isActive());

	}

	class CloseIcon extends ImageIcon {

		private CloseIcon() {
			super();
		}

		public void paintIcon(Component c, Graphics g, int x, int y) {
			Graphics2D g2 = (Graphics2D) g;

			int size = c.getWidth();
			int middle = size / 4;
			int w = c.getWidth();
			int h = c.getHeight();

			if (isActive())
				g2.setColor(ACTIVE_LABEL_COLOR);
			else
				g2.setColor(INACTIVE_LABEL_COLOR);

			g2.drawLine(x + 2, y + 2, w - 4, h - 4);
			g2.drawLine(w - 4, y + 2, x + 2, h - 4);

		}

		/**
		 * @see javax.swing.Icon#getIconHeight()
		 */
		public int getIconHeight() {
			return 6;
		}

		/**
		 * @see javax.swing.Icon#getIconWidth()
		 */
		public int getIconWidth() {
			return 6;
		}

	}

	class PinIcon extends ImageIcon {

		private PinIcon() {
			super();
		}

		public void paintIcon(Component c, Graphics g, int x, int y) {
			Graphics2D g2 = (Graphics2D) g;

			if (isActive())
				g2.setColor(ACTIVE_LABEL_COLOR);
			else
				g2.setColor(INACTIVE_LABEL_COLOR);
			g2.drawRect(3, 2, 4, 4);

			g2.drawLine(2, 2 + 4, 2 + 4 + 2, 2 + 4);
			g2.drawLine(5, 6, 5, 8);

		}

		/**
		 * @see javax.swing.Icon#getIconHeight()
		 */
		public int getIconHeight() {
			return 8;
		}

		/**
		 * @see javax.swing.Icon#getIconWidth()
		 */
		public int getIconWidth() {
			return 8;
		}

	}

	class MaximizeIcon extends ImageIcon {

		private MaximizeIcon() {
			super();
		}

		public void paintIcon(Component c, Graphics g, int x, int y) {
			Graphics2D g2 = (Graphics2D) g;

			int size = c.getWidth();
			int middle = size / 4;
			int w = c.getWidth();
			int h = c.getHeight();

			if (isActive())
				g2.setColor(ACTIVE_LABEL_COLOR);
			else
				g2.setColor(INACTIVE_LABEL_COLOR);
			g2.drawRect(2, 3, 5, 5);

			g2.drawLine(3 + 1, 1, 3 + 6, 1);
			g2.drawLine(3 + 6, 1, 3 + 6, 1 + 6 - 1);

		}

		/**
		 * @see javax.swing.Icon#getIconHeight()
		 */
		public int getIconHeight() {
			return 8;
		}

		/**
		 * @see javax.swing.Icon#getIconWidth()
		 */
		public int getIconWidth() {
			return 8;
		}

	}

	class MenuIcon extends ImageIcon {

		private MenuIcon() {
			super();
		}

		public void paintIcon(Component c, Graphics g, int x, int y) {
			Graphics2D g2 = (Graphics2D) g;

			int[] xp = new int[3];
			int[] yp = new int[3];

			int w = c.getWidth();
			int h = c.getHeight();

			xp[0] = x + 1;
			xp[1] = x + w - 3;
			xp[2] = x + 1 + 4;

			yp[0] = y + 3;
			yp[1] = y + 3;
			yp[2] = y + 3 + (int) (h - 1) / 2 - 1;

			if (isActive())
				g2.setColor(ACTIVE_LABEL_COLOR);
			else
				g2.setColor(INACTIVE_LABEL_COLOR);
			g2.drawPolygon(xp, yp, 3);

		}

		/**
		 * @see javax.swing.Icon#getIconHeight()
		 */
		public int getIconHeight() {
			return 6;
		}

		/**
		 * @see javax.swing.Icon#getIconWidth()
		 */
		public int getIconWidth() {
			return 10;
		}

	}

}
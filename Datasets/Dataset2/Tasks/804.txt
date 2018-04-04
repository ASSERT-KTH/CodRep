Vector ids = selectComponents.filesets;

/*
 * SwingInstall.java
 * Copyright (C) 1999, 2000, 2001 Slava Pestov
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
 */

package installer;

import javax.swing.border.*;
import javax.swing.event.*;
import javax.swing.*;
import java.awt.event.*;
import java.awt.*;
import java.io.File;
import java.io.IOException;
import java.util.Vector;

/*
 * Graphical front-end to installer.
 */
public class SwingInstall extends JFrame
{
	public SwingInstall()
	{
		installer = new Install();

		appName = installer.getProperty("app.name");
		appVersion = installer.getProperty("app.version");

		setTitle(appName + " " + appVersion + " installer");

		JPanel content = new JPanel(new WizardLayout());
		setContentPane(content);

		caption = new JLabel();
		caption.setFont(new Font("SansSerif",Font.BOLD,18));

		ActionHandler actionHandler = new ActionHandler();

		cancelButton = new JButton("Cancel");
		cancelButton.setRequestFocusEnabled(false);
		cancelButton.addActionListener(actionHandler);
		prevButton = new JButton("Previous");
		prevButton.setRequestFocusEnabled(false);
		prevButton.addActionListener(actionHandler);
		nextButton = new JButton();
		nextButton.setRequestFocusEnabled(false);
		nextButton.addActionListener(actionHandler);

		content.add(caption);
		content.add(cancelButton);
		content.add(prevButton);
		content.add(nextButton);

		pages = new Component[] {
			new TextPanel("app.readme"),
//			new TextPanel("app.license"),
			chooseDirectory = new ChooseDirectory(),
			selectComponents = new SelectComponents(),
			progress = new SwingProgress(),
			new Complete()
		};

		for(int i = 0; i < pages.length; i++)
			content.add(pages[i]);

		pageChanged();

		setDefaultCloseOperation(DO_NOTHING_ON_CLOSE);
		addWindowListener(new WindowHandler());

		Dimension screen = getToolkit().getScreenSize();
		pack();
		setLocation((screen.width - getSize().width) / 2,
			(screen.height - getSize().height) / 2);
		show();
	}

	// package-private members
	Install installer;
	String appName;
	String appVersion;

	JLabel caption;

	ChooseDirectory chooseDirectory;
	SelectComponents selectComponents;
	SwingProgress progress;

	JButton cancelButton;
	JButton prevButton;
	JButton nextButton;
	Component[] pages;
	int currentPage;

	private static final int PADDING = 12;

	void install()
	{
		Vector components = new Vector();
		int size = 0;

		JPanel comp = selectComponents.comp;
		Vector ids = selectedComponents.filesets;

		for(int i = 0; i < comp.getComponentCount(); i++)
		{
			if(((JCheckBox)comp.getComponent(i))
				.getModel().isSelected())
			{
				size += installer.getIntProperty(
					"comp." + ids.elementAt(i) + ".real-size");
				components.addElement(installer.getProperty(
					"comp." + ids.elementAt(i) + ".fileset"));
			}
		}

		JTextField binDir = chooseDirectory.binDir;
		String installDir = chooseDirectory.installDir.getText();

		InstallThread thread = new InstallThread(
			installer,progress,
			(installDir == null ? null : installDir),
			(binDir == null ? null : binDir.getText()),
			size,components);
		progress.setThread(thread);
		thread.start();
	}

	private void pageChanged()
	{
		switch(currentPage)
		{
		case 0:
			caption.setText("Installing " + appName);

			nextButton.setText("Next");
			prevButton.setEnabled(false);
			break;
		/*case 1:
			caption.setText("License");

			nextButton.setText("Next");
			prevButton.setEnabled(true);
			break;*/
		case 1:
			caption.setText("Specify where " + appName
				+ " is to be installed");

			nextButton.setText("Next");
			prevButton.setEnabled(true);
			break;
		case 2:
			caption.setText("Choose components to install");

			nextButton.setText("Install");
			prevButton.setEnabled(true);
			break;
		case 3:
			caption.setText("Installing " + appName);

			nextButton.setText("Finish");
			prevButton.setEnabled(false);
			nextButton.setEnabled(false);
			install();
			break;
		case 4:
			caption.setText("Installation complete");

			nextButton.setText("Finish");
			prevButton.setEnabled(false);
			nextButton.setEnabled(true);
			break;
		}

		getRootPane().invalidate();
		getRootPane().validate();
	}

	class ActionHandler implements ActionListener
	{
		public void actionPerformed(ActionEvent evt)
		{
			Object source = evt.getSource();
			if(evt.getSource() == cancelButton)
				System.exit(0);
			else if(evt.getSource() == prevButton)
			{
				currentPage--;
				pageChanged();
			}
			else if(evt.getSource() == nextButton)
			{
				if(currentPage == pages.length - 1)
					System.exit(0);
				else
				{
					currentPage++;
					pageChanged();
				}
			}
		}
	}

	class WindowHandler extends WindowAdapter
	{
		public void windowClosing(WindowEvent evt)
		{
			System.exit(0);
		}
	}

	class WizardLayout implements LayoutManager
	{
		public void addLayoutComponent(String name, Component comp)
		{
		}

		public void removeLayoutComponent(Component comp)
		{
		}

		public Dimension preferredLayoutSize(Container parent)
		{
			Dimension dim = new Dimension();

			Dimension captionSize = caption.getPreferredSize();
			dim.width = captionSize.width;

			for(int i = 0; i < pages.length; i++)
			{
				Dimension _dim = pages[i].getPreferredSize();
				dim.width = Math.max(_dim.width,dim.width);
				dim.height = Math.max(_dim.height,dim.height);
			}

			dim.width += PADDING * 2;
			dim.height += PADDING * 2;
			dim.height += nextButton.getPreferredSize().height;
			dim.height += captionSize.height;
			return dim;
		}

		public Dimension minimumLayoutSize(Container parent)
		{
			return preferredLayoutSize(parent);
		}

		public void layoutContainer(Container parent)
		{
			Dimension size = parent.getSize();

			Dimension captionSize = caption.getPreferredSize();
			caption.setBounds(PADDING,PADDING,captionSize.width,
				captionSize.height);

			// make all buttons the same size
			Dimension buttonSize = cancelButton.getPreferredSize();
			buttonSize.width = Math.max(buttonSize.width,prevButton.getPreferredSize().width);
			buttonSize.width = Math.max(buttonSize.width,nextButton.getPreferredSize().width);

			int bottomBorder = buttonSize.height + PADDING;

			// cancel button goes on far left
			cancelButton.setBounds(
				PADDING,
				size.height - buttonSize.height - PADDING,
				buttonSize.width,
				buttonSize.height);

			// prev and next buttons are on the right
			prevButton.setBounds(
				size.width - buttonSize.width * 2 - 6 - PADDING,
				size.height - buttonSize.height - PADDING,
				buttonSize.width,
				buttonSize.height);

			nextButton.setBounds(
				size.width - buttonSize.width - PADDING,
				size.height - buttonSize.height - PADDING,
				buttonSize.width,
				buttonSize.height);

			// calculate size for current page
			Rectangle currentPageBounds = new Rectangle();
			currentPageBounds.x = PADDING;
			currentPageBounds.y = PADDING * 2 + captionSize.height;
			currentPageBounds.width = size.width - currentPageBounds.x
				- PADDING;
			currentPageBounds.height = size.height - buttonSize.height
				- currentPageBounds.y - PADDING * 2;

			for(int i = 0; i < pages.length; i++)
			{
				Component page = pages[i];
				page.setBounds(currentPageBounds);
				page.setVisible(i == currentPage);
			}
		}
	}

	class TextPanel extends JPanel
	{
		TextPanel(String prop)
		{
			super(new BorderLayout());

			JEditorPane text = new JEditorPane();

			String file = installer.getProperty(prop);

			try
			{
				text.setPage(TextPanel.this.getClass().getResource(file));
			}
			catch(Exception e)
			{
				text.setText("Error loading '" + file + "'");
				e.printStackTrace();
			}

			text.setEditable(false);

			JScrollPane scrollPane = new JScrollPane(text);
			Dimension dim = new Dimension();
			dim.height = 200;
			scrollPane.setPreferredSize(dim);
			TextPanel.this.add(BorderLayout.CENTER,scrollPane);
		}
	}

	class ChooseDirectory extends JPanel
	implements ActionListener
	{
		JTextField installDir;
		JButton chooseInstall;
		JTextField binDir;
		JButton chooseBin;

		ChooseDirectory()
		{
			super(new BorderLayout());

			String _binDir = OperatingSystem.getOperatingSystem()
				.getShortcutDirectory(appName,appVersion);

			JPanel directoryPanel = new JPanel();
			GridBagLayout layout = new GridBagLayout();
			directoryPanel.setLayout(layout);
			GridBagConstraints cons = new GridBagConstraints();
			cons.anchor = GridBagConstraints.WEST;
			cons.fill = GridBagConstraints.HORIZONTAL;
			cons.gridy = 1;
			cons.insets = new Insets(0,0,6,0);

			JLabel label = new JLabel("Install program in: ",SwingConstants.RIGHT);
			label.setBorder(new EmptyBorder(0,0,0,12));
			layout.setConstraints(label,cons);
			directoryPanel.add(label);

			cons.weightx = 1.0f;
			installDir = new JTextField();
			installDir.setText(OperatingSystem.getOperatingSystem()
				.getInstallDirectory(appName,appVersion));
			layout.setConstraints(installDir,cons);
			directoryPanel.add(installDir);

			if(_binDir != null)
			{
				cons.gridy = 2;
				cons.weightx = 0.0f;
				cons.insets = new Insets(0,0,0,0);
				label = new JLabel("Install shortcut in: ",SwingConstants.RIGHT);
				label.setBorder(new EmptyBorder(0,0,0,12));
				layout.setConstraints(label,cons);
				directoryPanel.add(label);

				cons.weightx = 1.0f;
				binDir = new JTextField(_binDir);
				layout.setConstraints(binDir,cons);
				directoryPanel.add(binDir);
			}

			ChooseDirectory.this.add(BorderLayout.NORTH,directoryPanel);

			Box buttons = new Box(BoxLayout.X_AXIS);
			buttons.add(Box.createGlue());
			chooseInstall = new JButton("Choose Install Directory...");
			chooseInstall.setRequestFocusEnabled(false);
			chooseInstall.addActionListener(this);
			buttons.add(chooseInstall);
			if(_binDir != null)
			{
				buttons.add(Box.createHorizontalStrut(6));
				chooseBin = new JButton("Choose Shortcut Directory...");
				chooseBin.setRequestFocusEnabled(false);
				chooseBin.addActionListener(this);
				buttons.add(chooseBin);
			}
			buttons.add(Box.createGlue());

			ChooseDirectory.this.add(BorderLayout.SOUTH,buttons);
		}

		public void actionPerformed(ActionEvent evt)
		{
			JTextField field = (evt.getSource() == chooseInstall
				? installDir : binDir);

			File directory = new File(field.getText());
			JFileChooser chooser = new JFileChooser(directory.getParent());
			chooser.setFileSelectionMode(JFileChooser.DIRECTORIES_ONLY);
			chooser.setSelectedFile(directory);

			if(chooser.showOpenDialog(SwingInstall.this)
				== JFileChooser.APPROVE_OPTION)
				field.setText(chooser.getSelectedFile().getPath());
		}
	}

	class SelectComponents extends JPanel
	implements ActionListener
	{
		JPanel comp;
		JLabel sizeLabel;
		Vector filesets;

		SelectComponents()
		{
			super(new BorderLayout());

			comp = createCompPanel();
			SelectComponents.this.add(BorderLayout.NORTH,comp);

			sizeLabel = new JLabel("",SwingConstants.LEFT);
			SelectComponents.this.add(BorderLayout.SOUTH,sizeLabel);

			updateSize();
		}

		public void actionPerformed(ActionEvent evt)
		{
			updateSize();
		}

		private JPanel createCompPanel()
		{
			filesets = new Vector();

			int count = installer.getIntProperty("comp.count");
			JPanel panel = new JPanel(new GridLayout(count,1));

			String osClass = OperatingSystem.getOperatingSystem()
				.getClass().getName();
			osClass = osClass.substring(osClass.indexOf('$') + 1);

			for(int i = 0; i < count; i++)
			{
				String os = installer.getProperty("comp." + i + ".os");

				if(os != null && !osClass.equals(os))
					continue;

				JCheckBox checkBox = new JCheckBox(
					installer.getProperty("comp." + i + ".name")
					+ " (" + installer.getProperty("comp." + i
					+ ".disk-size") + "Kb)");
				checkBox.getModel().setSelected(true);
				checkBox.addActionListener(this);
				checkBox.setRequestFocusEnabled(false);

				filesets.addElement(new Integer(i));

				panel.add(checkBox);
			}

			Dimension dim = panel.getPreferredSize();
			dim.width = Integer.MAX_VALUE;
			panel.setMaximumSize(dim);

			return panel;
		}

		private void updateSize()
		{
			int size = 0;

			for(int i = 0; i < filesets.size(); i++)
			{
				if(((JCheckBox)comp.getComponent(i))
					.getModel().isSelected())
				{
					size += installer.getIntProperty("comp."
						+ filesets.elementAt(i)
						+ ".disk-size");
				}
			}

			sizeLabel.setText("Estimated disk usage of selected"
				+ " components: " + size + "Kb");
		}
	}

	class SwingProgress extends JPanel implements Progress
	{
		JProgressBar progress;
		InstallThread thread;

		SwingProgress()
		{
			super(new BorderLayout());

			progress = new JProgressBar();
			progress.setStringPainted(true);

			SwingProgress.this.add(BorderLayout.NORTH,progress);
		}

		public void setMaximum(final int max)
		{
			SwingUtilities.invokeLater(new Runnable()
			{
				public void run()
				{
					progress.setMaximum(max);
				}
			});
		}

		public void advance(final int value)
		{
			try
			{
				SwingUtilities.invokeAndWait(new Runnable()
				{
					public void run()
					{
						progress.setValue(progress
							.getValue() + value);
					}
				});
				Thread.yield();
			}
			catch(Exception e)
			{
			}
		}

		public void done()
		{
			SwingUtilities.invokeLater(new Runnable()
			{
				public void run()
				{
					currentPage++;
					pageChanged();
				}
			});
		}

		public void error(final String message)
		{
			SwingUtilities.invokeLater(new Runnable()
			{
				public void run()
				{
					dispose();
					JOptionPane.showMessageDialog(null,
						message,
						"Installation aborted",
						JOptionPane.ERROR_MESSAGE);
					System.exit(1);
				}
			});
		}

		public void setThread(InstallThread thread)
		{
			this.thread = thread;
		}
	}

	class Complete extends JPanel
	{
		Complete()
		{
			super(new BorderLayout());

			JEditorPane text = new JEditorPane();

			String clazz = OperatingSystem.getOperatingSystem()
				.getClass().getName();
			String readme = "done-" + clazz.substring(clazz.indexOf('$') + 1) + ".html";

			try
			{
				text.setPage(Complete.this.getClass().getResource(readme));
			}
			catch(Exception e)
			{
				text.setText("Error loading '" + readme + "'");
				e.printStackTrace();
			}

			text.setEditable(false);

			JScrollPane scrollPane = new JScrollPane(text);
			Dimension dim = new Dimension();
			dim.height = 200;
			scrollPane.setPreferredSize(dim);
			Complete.this.add(BorderLayout.CENTER,scrollPane);
		}
	}
}
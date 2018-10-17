setVisible(true);

/*
 * SwingInstall.java
 *
 * Originally written by Slava Pestov for the jEdit installer project. This work
 * has been placed into the public domain. You may use this work in any way and
 * for any purpose you wish.
 *
 * THIS SOFTWARE IS PROVIDED AS-IS WITHOUT WARRANTY OF ANY KIND, NOT EVEN THE
 * IMPLIED WARRANTY OF MERCHANTABILITY. THE AUTHOR OF THIS SOFTWARE, ASSUMES
 * _NO_ RESPONSIBILITY FOR ANY CONSEQUENCE RESULTING FROM THE USE, MODIFICATION,
 * OR REDISTRIBUTION OF THIS SOFTWARE.
 */

package installer;

import javax.swing.border.*;
import javax.swing.*;
import java.awt.event.*;
import java.awt.*;
import java.io.File;
import java.util.*;

/*
 * Graphical front-end to installer.
 */
public class SwingInstall extends JFrame
{
	public SwingInstall()
	{
		installer = new Install();
		osTasks = OperatingSystem.getOperatingSystem().getOSTasks(installer);

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

		String clazz = OperatingSystem.getOperatingSystem()
				.getClass().getName();
		String completedInfo = "done-" + clazz.substring(
			clazz.indexOf('$') + 1) + ".html";

		pages = new Component[] {
			new TextPanel(installer.getProperty("app.readme")),
			new TextPanel(installer.getProperty("app.license")),
			chooseDirectory = new ChooseDirectory(),
			selectComponents = new SelectComponents(),
			progress = new SwingProgress(),
			new TextPanel(completedInfo)
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
	// package-private, not private, for speedy access by inner classes
	Install installer;
	OperatingSystem.OSTask[] osTasks;
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
		Vector ids = selectComponents.filesets;

		for(int i = 0; i < comp.getComponentCount(); i++)
		{
			if(((JCheckBox)comp.getComponent(i))
				.getModel().isSelected())
			{
				size += installer.getIntegerProperty(
					"comp." + ids.elementAt(i) + ".real-size");
				components.addElement(installer.getProperty(
					"comp." + ids.elementAt(i) + ".fileset"));
			}
		}

		String installDir = chooseDirectory.installDir.getText();

		Map osTaskDirs = chooseDirectory.osTaskDirs;
		Iterator keys = osTaskDirs.keySet().iterator();
		while(keys.hasNext())
		{
			OperatingSystem.OSTask osTask = (OperatingSystem.OSTask)keys.next();
			String dir = ((JTextField)osTaskDirs.get(osTask)).getText();
			if(dir != null && dir.length() != 0)
			{
				osTask.setEnabled(true);
				osTask.setDirectory(dir);
			}
			else
				osTask.setEnabled(false);
		}

		InstallThread thread = new InstallThread(
			installer,progress,
			installDir,osTasks,
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
		case 1:
			caption.setText(installer.getProperty("app.license.title"));

			nextButton.setText("Next");
			prevButton.setEnabled(true);
			break;
		case 2:
			caption.setText("Specify where " + appName
				+ " is to be installed");

			nextButton.setText("Next");
			prevButton.setEnabled(true);
			break;
		case 3:
			caption.setText("Choose components to install");

			nextButton.setText("Install");
			prevButton.setEnabled(true);
			break;
		case 4:
			caption.setText("Installing " + appName);

			nextButton.setText("Finish");
			prevButton.setEnabled(false);
			nextButton.setEnabled(false);
			install();
			break;
		case 5:
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
			if(source == cancelButton)
				System.exit(0);
			else if(source == prevButton)
			{
				currentPage--;
				pageChanged();
			}
			else if(source == nextButton)
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
		TextPanel(String file)
		{
			super(new BorderLayout());

			JEditorPane text = new JEditorPane();

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
			dim.width = 450;
			dim.height = 200;
			scrollPane.setPreferredSize(dim);
			TextPanel.this.add(BorderLayout.CENTER,scrollPane);
		}
	}

	class ChooseDirectory extends JPanel
	{
		JTextField installDir;
		Map osTaskDirs;

		ChooseDirectory()
		{
			super(new BorderLayout());

			osTaskDirs = new HashMap();

			JPanel directoryPanel = new JPanel(new VariableGridLayout(
				VariableGridLayout.FIXED_NUM_COLUMNS,3,12,12));

			installDir = addField(directoryPanel,"Install program in:",
				OperatingSystem.getOperatingSystem()
				.getInstallDirectory(appName,appVersion));

			for(int i = 0; i < osTasks.length; i++)
			{
				OperatingSystem.OSTask osTask = osTasks[i];
				String label = osTask.getLabel();
				if(label != null)
				{
					JTextField field = addField(directoryPanel,label,
						osTask.getDirectory());
					osTaskDirs.put(osTask,field);
				}
			}
			ChooseDirectory.this.add(BorderLayout.NORTH,directoryPanel);
		}

		private JTextField addField(JPanel directoryPanel, String label,
			String defaultText)
		{
			JTextField field = new JTextField(defaultText);

			directoryPanel.add(new JLabel(label,SwingConstants.RIGHT));

			Box fieldBox = new Box(BoxLayout.Y_AXIS);
			fieldBox.add(Box.createGlue());
			Dimension dim = field.getPreferredSize();
			dim.width = Integer.MAX_VALUE;
			field.setMaximumSize(dim);
			fieldBox.add(field);
			fieldBox.add(Box.createGlue());
			directoryPanel.add(fieldBox);
			JButton choose = new JButton("Choose...");
			choose.setRequestFocusEnabled(false);
			choose.addActionListener(new ActionHandler(field));
			directoryPanel.add(choose);

			return field;
		}

		class ActionHandler implements ActionListener
		{
			JTextField field;

			ActionHandler(JTextField field)
			{
				this.field = field;
			}

			public void actionPerformed(ActionEvent evt)
			{
				File directory = new File(field.getText());
				JFileChooser chooser = new JFileChooser(directory.getParent());
				chooser.setFileSelectionMode(JFileChooser.DIRECTORIES_ONLY);
				chooser.setSelectedFile(directory);

				if(chooser.showOpenDialog(SwingInstall.this)
					== JFileChooser.APPROVE_OPTION)
					field.setText(chooser.getSelectedFile().getPath());
			}
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

			int count = installer.getIntegerProperty("comp.count");
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
					size += installer.getIntegerProperty("comp."
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
}
xmlFile = new XmlIO(file.toURL());

import java.awt.BorderLayout;
import java.io.File;
import java.net.MalformedURLException;

import javax.swing.JPanel;
import javax.swing.JTextField;

import org.columba.core.facade.Facade;
import org.columba.core.gui.plugin.AbstractConfigPlugin;
import org.columba.core.xml.XmlElement;
import org.columba.core.xml.XmlIO;

/**
 * @author fdietz
 *
 * This example demonstrates the use of the config extension point
 * 
 */
public class ConfigExample extends AbstractConfigPlugin {

	JTextField textField;
	XmlElement parent;

	XmlIO xmlFile;
	/**
	 * 
	 */
	public ConfigExample() {
		super();

		// open configuration file 
		File file = Facade.getPluginConfigFile("org.columba.example.ConfigExample");
		try {
			XmlIO xmlIO = new XmlIO(file.toURL());
			xmlFile.load();
			
			parent = xmlFile.getRoot();
		} catch (MalformedURLException e) {
			e.printStackTrace();
		}
			
	}

	/* (non-Javadoc)
	 * @see org.columba.core.gui.plugin.AbstractConfigPlugin#updateComponents(boolean)
	 */
	public void updateComponents(boolean b) {
		

		if (b) {
			// model -> view
			// read configuration and set gui elements appropriately

			// navigate to treenode "text"
			XmlElement text = parent.getElement("/config/text");

			// read attribute "value"
			String attribute = text.getAttribute("value");

			textField.setText(attribute);

		} else {
			// view -> model
			// write configuration given the data the user entered in the gui

			XmlElement text = parent.getElement("/config/text");
			text.addAttribute("value", textField.getText());
			
			try
			{
				xmlFile.save();
				
			} catch ( Exception ex)
			{
				ex.printStackTrace();
			}
		}

	}

	/* (non-Javadoc)
	 * @see org.columba.core.gui.plugin.AbstractConfigPlugin#createPanel()
	 */
	public JPanel createPanel() {

		JPanel panel = new JPanel();
		panel.setLayout(new BorderLayout());

		textField = new JTextField(20);
		panel.add(textField, BorderLayout.CENTER);

		return panel;
	}

}
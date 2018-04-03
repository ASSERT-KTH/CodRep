throw new JHotDrawRuntimeException("Iconkit instance isn't set");

/*
 * @(#)ToolButton.java 5.2
 *
 */

package CH.ifa.draw.standard;

import javax.swing.*;
import java.awt.*;
import CH.ifa.draw.util.*;
import CH.ifa.draw.framework.*;

/**
 * A PaletteButton that is associated with a tool.
 * @see Tool
 */
public class ToolButton extends PaletteButton {

    private String          fName;
    private Tool            fTool;
    private PaletteIcon     fIcon;

    public ToolButton(PaletteListener listener, String iconName, String name, Tool tool) {
        super(listener);
        // use a Mediatracker to ensure that all the images are initially loaded
        Iconkit kit = Iconkit.instance();
        if (kit == null)
            throw new HJDError("Iconkit instance isn't set");

        Image im[] = new Image[3];
        im[0] = kit.loadImageResource(iconName+"1.gif");
        im[1] = kit.loadImageResource(iconName+"2.gif");
        im[2] = kit.loadImageResource(iconName+"3.gif");

        MediaTracker tracker = new MediaTracker(this);
        for (int i = 0; i < 3; i++) {
            tracker.addImage(im[i], i);
        }
        try {
            tracker.waitForAll();
        } catch (Exception e) {  }

        fIcon = new PaletteIcon(new Dimension(24,24), im[0], im[1], im[2]);
        fTool = tool;
        fName = name;

        setIcon(new ImageIcon(im[0]));
        setPressedIcon(new ImageIcon(im[1]));
        setSelectedIcon(new ImageIcon(im[2]));
        setToolTipText(name);
    }

    public Tool tool() {
        return fTool;
    }

    public String name() {
        return fName;
    }

    public Object attributeValue() {
        return tool();
    }

    public Dimension getMinimumSize() {
        return new Dimension(fIcon.getWidth(), fIcon.getHeight());
    }

    public Dimension getPreferredSize() {
        return new Dimension(fIcon.getWidth(), fIcon.getHeight());
    }
    
    public Dimension getMaximumSize() {
        return new Dimension(fIcon.getWidth(), fIcon.getHeight());
    }

//  Not necessary anymore in JFC due to the support of Icons in JButton
/*
    public void paintBackground(Graphics g) { }

    public void paintNormal(Graphics g) {
        if (fIcon.normal() != null)
            g.drawImage(fIcon.normal(), 0, 0, this);
    }

    public void paintPressed(Graphics g) {
        if (fIcon.pressed() != null)
            g.drawImage(fIcon.pressed(), 0, 0, this);
    }
*/
    public void paintSelected(Graphics g) {
        if (fIcon.selected() != null)
            g.drawImage(fIcon.selected(), 0, 0, this);
    }

    public void paint(Graphics g) {
    	// selecting does not work as expected with JFC1.1
    	// see JavaBug: 4228035, 4233965
    	if (isSelected()) {
        	paintSelected(g);
    	}
    	else {
	    	super.paint(g);
    	}
    }
}

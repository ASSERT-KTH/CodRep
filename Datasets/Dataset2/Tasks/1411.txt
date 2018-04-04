public class ImageSequenceTimer extends ToolBarButton implements ActionListener,

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

package org.columba.core.gui.toolbar;

import java.awt.Insets;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

import javax.swing.ImageIcon;
import javax.swing.JButton;
import javax.swing.Timer;

import org.columba.core.command.TaskManager;
import org.columba.core.command.TaskManagerEvent;
import org.columba.core.command.TaskManagerListener;
import org.columba.core.resourceloader.ImageLoader;

/**
 * Animated image showing background activity.
 * <p>
 * Can be found in the toolbar in the right topmost corner of Columba.
 * <p>
 * ImageSequenceTimer actually only listens for {@link TaskManagerEvent} and
 * starts/stops as appropriate.
 * 
 * @author fdietz
 */
public class ImageSequenceTimer extends JButton implements ActionListener,
		TaskManagerListener {

	private static int DELAY = 100;

	private TaskManager taskManager;

	private Timer timer;

	private ImageIcon[] images;

	private ImageIcon restImage;

	private int frameNumber;

	private int frameCount;

	public ImageSequenceTimer() {
		super();

		taskManager = TaskManager.getInstance();

		timer = new Timer(DELAY, this);
		timer.setInitialDelay(0);
		timer.setCoalesce(true);
		setMargin(new Insets(0, 0, 0, 0));
		setRolloverEnabled(true);
		setBorder(null);
		setContentAreaFilled(false);

		setRequestFocusEnabled(false);

		initDefault();

		// register interested on changes in the running worker list
		this.taskManager = taskManager;
		taskManager.addTaskManagerListener(this);
	}

	/**
	 * Its an element of the toolbar, and therefor can't have the focus.
	 */
	public boolean isFocusTraversable() {
		return isRequestFocusEnabled();
	}

	/**
	 * Initialize the image array, using single frame images.
	 * 
	 */
	protected void initDefault() {
		frameCount = 60;
		frameNumber = 1;

		images = new ImageIcon[frameCount];

		for (int i = 0; i < frameCount; i++) {
			StringBuffer buf = new StringBuffer();

			if (i < 10) {
				buf.append("00");
			}

			if ((i >= 10) && (i < 100)) {
				buf.append("0");
			}

			buf.append(Integer.toString(i));

			buf.append(".png");

			images[i] = ImageLoader.getImageIcon(buf.toString());
		}

		restImage = ImageLoader.getImageIcon("rest.png");

		setIcon(restImage);
	}

	public void start() {
		if (!timer.isRunning()) {
			timer.start();
		}
	}

	public void stop() {
		if (timer.isRunning()) {
			timer.stop();
		}

		frameNumber = 0;

		setIcon(restImage);
	}

	/**
	 * Listen for timer actionevents and update the image
	 */
	public void actionPerformed(ActionEvent ev) {
		String action = ev.getActionCommand();

		frameNumber++;

		if (timer.isRunning()) {
			setIcon(new ImageIcon(images[frameNumber % frameCount].getImage()));
		} else {
			setIcon(restImage);
		}
	}

	public void workerAdded(TaskManagerEvent e) {
		updateTimer();
	}

	public void workerRemoved(TaskManagerEvent e) {
		updateTimer();
	}

	protected void updateTimer() {
		// just the animation, if there are more than zero
		// workers running
		if (taskManager.count() > 0) {
			start();
		} else {
			stop();
		}
	}
}
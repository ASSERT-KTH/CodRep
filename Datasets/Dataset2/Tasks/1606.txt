import org.columba.core.base.SwingWorker;

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
package org.columba.core.gui.statusbar;

import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

import javax.swing.Timer;

import org.columba.core.util.SwingWorker;


class WorkerItem {
    private final static int TWO_SECONDS = 2000;
    private SwingWorker worker;
    private int number;
    private String text;
    private int maximum;
    private int value;
    private Timer timer;
    private boolean allowed;
    private int priority;

    public WorkerItem(SwingWorker w, int i, int priority) {
        worker = w;
        number = i;
        this.priority = priority;

        allowed = false;

        timer = new Timer(TWO_SECONDS,
                new ActionListener() {
                    public void actionPerformed(ActionEvent e) {
                        allowed = true;
                    }
                });
    }

    public int getPriority() {
        return priority;
    }

    public boolean isAllowed() {
        return allowed;
    }

    public void setAllowed(boolean b) {
        allowed = b;
    }

    public void setWorker(SwingWorker w) {
        worker = w;
    }

    public void setCancel(boolean b) {
        worker.setCancel(b);
    }

    public boolean getCancel() {
        return worker.getCancel();
    }

    public void setNumber(int i) {
        number = i;
    }

    public int getNumber() {
        return number;
    }

    public Thread getThread() {
        return worker.getThread();
    }

    public void setText(String s) {
        this.text = s;
    }

    public String getText() {
        return text;
    }

    public void setProgressBarMaximum(int m) {
        maximum = m;
    }

    public int getProgressBarMaximum() {
        return maximum;
    }

    public void setProgressBarValue(int v) {
        if (v <= getProgressBarMaximum()) {
            value = v;
        }
    }

    public int getProgressBarValue() {
        return value;
    }
}
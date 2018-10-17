import org.frapuccino.awt.WindowsUtil;

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
package org.columba.core.gui.logdisplay;

import java.awt.BorderLayout;
import java.util.logging.LogRecord;

import javax.swing.JDialog;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTextArea;

import org.frappucino.awt.WindowsUtil;

import com.jgoodies.forms.builder.DefaultFormBuilder;
import com.jgoodies.forms.layout.FormLayout;

/**
 * A detailed view of a log record.
 * @author redsolo
 */
public class LogRecordPanel extends JPanel {

    private LogRecord logRecord;

    /**
     * Creates a panel for the record.
     *
     * @param record the log record to display.
     */
    public LogRecordPanel(LogRecord record) {
        super();
        logRecord = record;
        initComponents();
    }

    /**
     * Inits the components.
     */
    private void initComponents() {

        JPanel main = new JPanel();

        FormLayout layout = new FormLayout("right:pref, 3dlu, pref:grow, 7dlu, right:pref, 3dlu, pref:grow", //"right:max(40dlu;pref),3dlu,
                "");
        DefaultFormBuilder builder = new DefaultFormBuilder(main, layout);

        builder.appendSeparator("Details");

        String source;
        if (logRecord.getSourceClassName() == null) {
            source = "Unknown";
        } else {
            source = logRecord.getSourceClassName() + "." + logRecord.getSourceMethodName() + "()";
        }
        builder.append("Source:", new JLabel(source), 5);

        builder.append("Time:", new JLabel(Long.toString(logRecord.getMillis())));
        builder.append("level:", new JLabel(logRecord.getLevel().toString()));

        builder.append("Thread:", new JLabel(Integer.toString(logRecord.getThreadID())));
        builder.append("Seq nr:", new JLabel(Long.toString(logRecord.getSequenceNumber())));

        builder.appendSeparator("Message");

        JTextArea area = new JTextArea(logRecord.getMessage());
        area.setLineWrap(true);
        area.setRows(5);
        area.setEditable(false);
        builder.append(new JScrollPane(area), 7);

        Throwable thrown = logRecord.getThrown();
        if (thrown != null) {
            builder.appendSeparator("Exception");
            StringBuffer buffer = new StringBuffer();

            StackTraceElement[] stackTrace = thrown.getStackTrace();
            for (int i = 0; i < stackTrace.length; i++) {
                buffer.append(stackTrace[i]);
                buffer.append("\n");
            }
            area = new JTextArea(buffer.toString());
            area.setLineWrap(true);
            area.setRows(5);
            area.setEditable(false);
            builder.append(new JScrollPane(area), 7);
        }

        setLayout(new BorderLayout());
        add(main, BorderLayout.CENTER);
    }

    /**
     * Shows the record panel in a dialog.
     * @param owner owner to jframe.
     * @param record the log record to display.
     */
    public static void showRecord(JFrame owner, LogRecord record) {
        JDialog dialog = new JDialog(owner, "Log record", false);
        dialog.setDefaultCloseOperation(JDialog.DISPOSE_ON_CLOSE);
        dialog.getContentPane().setLayout(new BorderLayout());
        dialog.getContentPane().add(new LogRecordPanel(record), BorderLayout.CENTER);
        dialog.pack();
        dialog.setVisible(true);
        WindowsUtil.centerInScreen(dialog);
    }
}
public BusySocketDialog(Shell shell, Server server) {

/*******************************************************************************
 * Copyright (c) 2008, 2009 28msec Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     Gabriel Petrovay (28msec) - initial API and implementation
 *******************************************************************************/
package org.eclipse.wst.xquery.set.internal.debug.ui.dialogs;

import org.eclipse.dltk.ui.util.SWTFactory;
import org.eclipse.jface.dialogs.TrayDialog;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.events.SelectionListener;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.wst.xquery.set.internal.debug.ui.launchConfigurations.SocketSelectionBlock;
import org.eclipse.wst.xquery.set.internal.launching.server.Server;

public class BusySocketDialog extends TrayDialog {

    private class WidgetListener implements SelectionListener {

        public void widgetDefaultSelected(SelectionEvent e) {
        }

        public void widgetSelected(SelectionEvent e) {
            if (e.widget == fSocketBlock.fIpCombo) {
                fHost = fSocketBlock.fIpCombo.getText();
            } else if (e.widget == fSocketBlock.fPortSpinner) {
                fPort = fSocketBlock.fPortSpinner.getSelection();
            }
        }
    }

    private SocketSelectionBlock fSocketBlock;

    private WidgetListener fListener = new WidgetListener();

    private String fHost;
    private int fPort;

    protected BusySocketDialog(Shell shell, Server server) {
        super(shell);
        fHost = server.getHost();
        fPort = server.getPort();
    }

    @Override
    protected Control createDialogArea(Composite parent) {
        Composite composite = (Composite)super.createDialogArea(parent);

        SWTFactory.createLabel(composite, "This socket is already in use. Choose another one:", 1);

        createSocketBlock(composite);

        initializeDialogData();

        return composite;
    }

    private void initializeDialogData() {
        getShell().setText("Socket already in use");
        fSocketBlock.fIpCombo.setText(fHost);
        fSocketBlock.fPortSpinner.setSelection(fPort);
        fSocketBlock.fPortSpinner.setFocus();
    }

    protected void createSocketBlock(Composite comp) {
        fSocketBlock = new SocketSelectionBlock(comp);
        fSocketBlock.addSelectionListener(fListener);
    }

    public String getHost() {
        return fHost;
    }

    public int getPort() {
        return fPort;
    }
}
 No newline at end of file
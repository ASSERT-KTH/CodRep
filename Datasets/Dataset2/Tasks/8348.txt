import org.columba.core.gui.base.MultiLineLabel;

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
package org.columba.mail.gui.config.accountwizard;

import javax.swing.Box;
import javax.swing.BoxLayout;
import javax.swing.JComponent;
import javax.swing.JPanel;

import net.javaprog.ui.wizard.AbstractStep;

import org.columba.core.gui.util.MultiLineLabel;
import org.columba.mail.util.MailResourceLoader;


class FinishStep extends AbstractStep {
    public FinishStep() {
        super(MailResourceLoader.getString("dialog", "accountwizard", "finish"),
            MailResourceLoader.getString("dialog", "accountwizard",
                "finish_description"));
        setCanFinish(true);
    }

    protected JComponent createComponent() {
        JComponent component = new JPanel();
        component.setLayout(new BoxLayout(component, BoxLayout.Y_AXIS));

        MultiLineLabel label = new MultiLineLabel(MailResourceLoader.getString(
                    "dialog", "accountwizard", "finish_text"));
        component.add(label);
        component.add(Box.createVerticalGlue());

        return component;
    }

    public void prepareRendering() {
    }
}
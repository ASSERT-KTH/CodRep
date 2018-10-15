public void createProxyObject(ID target,String classname,String name);

/****************************************************************************
* Copyright (c) 2004 Composent, Inc. and others.
* All rights reserved. This program and the accompanying materials
* are made available under the terms of the Eclipse Public License v1.0
* which accompanies this distribution, and is available at
* http://www.eclipse.org/legal/epl-v10.html
*
* Contributors:
*    Composent, Inc. - initial API and implementation
*****************************************************************************/

package org.eclipse.ecf.example.collab.share;

import org.eclipse.core.resources.IResource;
import org.eclipse.ecf.core.ISharedObjectContext;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.swt.widgets.Control;
import org.eclipse.ui.IWorkbenchWindow;
import org.eclipse.ui.part.ViewPart;


/**
 * Interface describing access to the Eclipse project that is associated
 * with a given collaboration group.
 * 
 * @author slewis
 */
public interface EclipseProject {

	public ID getID();
	
	public IResource getResource();
	public IWorkbenchWindow getWorkbenchWindow();
	
	public ISharedObjectContext getContext();

	public void makeProxyObject(ID target,String classname,String name);
	public void messageProxyObject(ID target, String name, String meth, Object [] args);
	public void removeProxyObject(ID target,String name);

	public User getUser();
	public User getUserForID(ID user);
	public void sendPrivateMessageToUser(User touser, String msg);
	public void sendShowTextMsg(String msg);
	
	public ViewPart getViewPart();
	public Control getTreeControl();
	public Control getTextControl();

}
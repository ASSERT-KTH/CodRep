public IContainer createInstance(ContainerDescription description,

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.core.provider;

import org.eclipse.ecf.core.ContainerDescription;
import org.eclipse.ecf.core.ContainerInstantiationException;
import org.eclipse.ecf.core.IContainer;

public interface IContainerInstantiator {
	public IContainer makeInstance(ContainerDescription description,
			Class[] argTypes, Object[] args)
			throws ContainerInstantiationException;
}
 No newline at end of file
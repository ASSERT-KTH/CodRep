package org.eclipse.ecf.internal.example.collab.ui;

/*******************************************************************************
 * Copyright (c) 2004, 2007 Remy Suen, Composent, Inc., and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Remy Suen <remy.suen@gmail.com> - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.example.collab.ui;

import java.io.Serializable;

import org.eclipse.swt.graphics.ImageData;
import org.eclipse.swt.graphics.PaletteData;

public class ImageWrapper implements Serializable {

	private static final long serialVersionUID = -834839369167998998L;

	public final int width;
	public final int height;
	public final int depth;
	public final int scanlinePad;
	public final byte[] data;

	private final int redMask;
	private final int greenMask;
	private final int blueMask;

	ImageWrapper(ImageData data) {
		width = data.width;
		height = data.height;
		depth = data.depth;
		scanlinePad = data.scanlinePad;
		this.data = data.data;
		redMask = data.palette.redMask;
		greenMask = data.palette.greenMask;
		blueMask = data.palette.blueMask;
	}
	
	public ImageData createImageData() {
		PaletteData palette = new PaletteData(redMask, greenMask, blueMask);
		return new ImageData(width, height, depth, palette, scanlinePad, data);
	}
}
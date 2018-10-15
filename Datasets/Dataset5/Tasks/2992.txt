splitInfo(messages.get(0));

/*******************************************************************************
 * Copyright (c) 2005, 2007 committers of openArchitectureWare and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     committers of openArchitectureWare - initial API and implementation
 *******************************************************************************/

package org.eclipse.xtend.shared.ui.core.builder;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

import org.eclipse.jface.text.BadLocationException;
import org.eclipse.jface.text.IRegion;
import org.eclipse.jface.text.ITextHover;
import org.eclipse.jface.text.ITextViewer;
import org.eclipse.jface.text.Region;
import org.eclipse.jface.text.source.Annotation;
import org.eclipse.jface.text.source.IAnnotationHover;
import org.eclipse.jface.text.source.IAnnotationModel;
import org.eclipse.jface.text.source.ISourceViewer;
import org.eclipse.swt.graphics.Point;
import org.eclipse.ui.texteditor.MarkerAnnotation;
import org.eclipse.xtend.shared.ui.Messages;

public class XtendXpandProblemHover implements IAnnotationHover, ITextHover {

	private ISourceViewer sourceViewer;

	public XtendXpandProblemHover(final ISourceViewer sourceViewer) {
		this.sourceViewer = sourceViewer;
	}

	// for AnnotationHover
	public String getHoverInfo(final ISourceViewer sourceViewer, final int lineNumber) {
		return getHoverInfoInternal(lineNumber, -1);
	}

	// for TextHover
	public String getHoverInfo(final ITextViewer textViewer, final IRegion hoverRegion) {
		int lineNumber;
		try {
			lineNumber = sourceViewer.getDocument().getLineOfOffset(hoverRegion.getOffset());
		} catch (final BadLocationException e) {
			return null;
		}
		return getHoverInfoInternal(lineNumber, hoverRegion.getOffset());
	}

	public IRegion getHoverRegion(final ITextViewer textViewer, final int offset) {
		final Point selection = textViewer.getSelectedRange();
		if (selection.x <= offset && offset < selection.x + selection.y)
			return new Region(selection.x, selection.y);
		return new Region(offset, 0);
	}

	private String getHoverInfoInternal(final int lineNumber, final int offset) {
		final IAnnotationModel model = sourceViewer.getAnnotationModel();
		final List<String> messages = new ArrayList<String>();

		final Iterator<?> iterator = model.getAnnotationIterator();
		while (iterator.hasNext()) {
			final Annotation annotation = (Annotation) iterator.next();
			if (!(annotation instanceof MarkerAnnotation))
				continue;
			final MarkerAnnotation mAnno = (MarkerAnnotation) annotation;
			final int start = model.getPosition(mAnno).getOffset();
			final int end = start + model.getPosition(mAnno).getLength();

			if (offset > 0 && !(start <= offset && offset <= end))
				continue;
			try {
				if (lineNumber != sourceViewer.getDocument().getLineOfOffset(start))
					continue;
			} catch (final Exception x) {
				continue;
			}
			if (mAnno.getText() != null) {
				messages.add(mAnno.getText().trim());
			}
		}
		return formatInfo(messages);
	}

	private StringBuffer buffer;

	private String formatInfo(final List<String> messages) {
		buffer = new StringBuffer();
		if (messages.size() > 1) {
			buffer.append(Messages.XtendXpandProblemHover_MultipleMarkers);
			final Iterator<String> e = messages.iterator();
			while (e.hasNext()) {
				splitInfo("- " + e.next() + "\n");
			}
		} else if (messages.size() == 1)
			splitInfo((String) messages.get(0));
		return buffer.toString();
	}

	private String splitInfo(String message) {
		String prefix = "";
		int pos;
		do {
			pos = message.indexOf(" ", 60);
			if (pos > -1) {
				buffer.append(prefix + message.substring(0, pos) + "\n");
				message = message.substring(pos);
				prefix = "  ";
			} else
				buffer.append(prefix + message);
		} while (pos > -1);
		return buffer.toString();
	}
}
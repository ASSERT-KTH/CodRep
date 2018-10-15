IModelChange change = new DocumentChangeMessage(i + 150, newText.length(),	newText);

package org.eclipse.ecf.tests.sync;

import org.eclipse.ecf.sync.IModelChange;
import org.eclipse.ecf.sync.IModelChangeMessage;
import org.eclipse.ecf.sync.IModelSynchronizationStrategy;
import org.eclipse.ecf.sync.doc.DocumentChangeMessage;
import org.eclipse.jface.text.Document;

public class Initiator extends Thread {

	private Document fDocument;

	private SimpleMessageQueue queue;
	private SimpleMessageQueue receiverQueue;

	private IModelSynchronizationStrategy initiator;

	public Initiator(IModelSynchronizationStrategy initiator, Document document) {
		this.setInitiator(initiator);
		this.queue = new SimpleMessageQueue();
		fDocument = document;
	}

	public void run() {
		for (int i = 0; i < 10; i++) {
			String text = fDocument.get();
			String newText = ">";
			text = text.concat(newText);

			fDocument.set(text);
			IModelChange change = new DocumentChangeMessage(i + 150, 1,	newText);

			IModelChangeMessage[] changes = initiator.registerLocalChange(change);

			getReceiverQueue().put(changes);
			
		}

	}

	protected void setInitiator(IModelSynchronizationStrategy initiator) {
		this.initiator = initiator;
	}

	public IModelSynchronizationStrategy getInitiator() {
		return initiator;
	}

	public void setDocument(Document document) {
		this.fDocument = document;
	}

	public Document getDocument() {
		return fDocument;
	}

	public SimpleMessageQueue getQueue() {
		return queue;
	}

	public void setReceiverQueue(SimpleMessageQueue receiverQueue) {
		this.receiverQueue = receiverQueue;
	}

	public SimpleMessageQueue getReceiverQueue() {
		return receiverQueue;
	}

}
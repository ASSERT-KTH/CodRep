Copyright (c) 2010 Composent, Inc. and others. All rights reserved. This

/*******************************************************************************
* Copyright (c) 2010 Composent, Inc. and others. All rights reserved. This
* program and the accompanying materials are made available under the terms of
* the Eclipse Public License v1.0 which accompanies this distribution, and is
* available at http://www.eclipse.org/legal/epl-v10.html
*
* Contributors:
*   Composent, Inc. - initial API and implementation
******************************************************************************/
package org.eclipse.ecf.examples.internal.loadbalancing.ds.consumer;

import org.eclipse.ecf.examples.loadbalancing.IDataProcessor;
import org.eclipse.ecf.examples.loadbalancing.IDataProcessorAsync;
import org.eclipse.ecf.remoteservice.IAsyncCallback;

public class DataProcessorClientComponent {

	public void bind(IDataProcessor dataProcessor) {
		System.out.println("Got data processor on client");
		final String data = "Here's some data from a client";
		// Use it
		System.out.println("Invoking data processor");
		String result = dataProcessor.processData(data);
		System.out.println("Sync result="+result);
		System.out.println();
		// See if we've got an async interface and if so, use it
		if (dataProcessor instanceof IDataProcessorAsync) {
			IDataProcessorAsync dpAsync = (IDataProcessorAsync) dataProcessor;
			System.out.println("Got async data processor on client");
			IAsyncCallback<String> callback = new IAsyncCallback<String>() {
				public void onSuccess(String result) {
					System.out.println("Async result="+result);
				}
				public void onFailure(Throwable exception) {
					System.out.println("Async invoke failed with exception");
					if (exception != null) exception.printStackTrace();
				}
				
			};
			// Now invoke async
			dpAsync.processDataAsync(data, callback);
		}
	}
}
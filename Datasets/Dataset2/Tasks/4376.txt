import org.columba.core.scripting.service.api.IColumbaService;

/*
 The contents of this file are subject to the Mozilla Public License Version 1.1
 (the "License"); you may not use this file except in compliance with the 
 License. You may obtain a copy of the License at http://www.mozilla.org/MPL/
 
 Software distributed under the License is distributed on an "AS IS" basis,
 WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License 
 for the specific language governing rights and
 limitations under the License.

 The Original Code is "The Columba Project"
 
 The Initial Developers of the Original Code are Frederik Dietz and Timo Stich.
 Portions created by Frederik Dietz and Timo Stich are Copyright (C) 2003. 
 
 All Rights Reserved.
 */
package org.columba.core.filemonitor;

import java.io.File;
import java.io.FileNotFoundException;
import java.util.ArrayList;
import java.util.List;

import org.columba.core.scripting.service.IColumbaService;

/**
 * @author Celso Pinto <cpinto@yimports.com>
 */
public class FileMonitorService implements IColumbaService {

	private List<FileObserver> observerList;

	private ObserverThread observerThread;

	public FileMonitorService() {
		observerList = new ArrayList();
		/* TODO must get polling interval from config file */
		observerThread = new ObserverThread(
				ObserverThread.DEFAULT_POLLING_INTERVAL);
	}

	public void startService() {
		observerThread.start();
	}

	public void disposeService() {
	}

	public boolean initService() {
		return true;
	}

	public void stopService() {

		for (FileObserver obs : observerList)
			obs.stoppingService();

		observerList.clear();

	}

	public void monitorFile(File file, FileObserver observer)
			throws FileNotFoundException, FileMonitorException {

		if (!file.exists())
			throw new FileNotFoundException(file.getName());

		if (file.isDirectory())
			throw new FileMonitorException(
					"Monitoring directories not yet supported");

		if (!observerList.contains(observer))
			observerList.add(observer);

		observerThread.monitorFile(file, observer);

	}

}
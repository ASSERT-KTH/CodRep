import org.columba.ristretto.message.MimeHeader;

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

package org.columba.mail.gui.mimetype;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.URL;

import org.columba.core.logging.ColumbaLogger;
import org.columba.core.util.OSInfo;
import org.columba.mail.message.MimeHeader;

public class WindowsViewer extends AbstractViewer {

	public Process openWith(MimeHeader header, File tempFile) {
		// *20030714, karlpeder* openDocumentWidth now called
		openDocumentWith(tempFile.getPath());
		return null;
	}

	public Process open(MimeHeader header, File tempFile) {
		openDocument(tempFile.getPath());
		return null;
	}

	public Process openURL(URL url) {
		if (OSInfo.isWin2K() || OSInfo.isWinXP()) {
			Process proc = null;
			try {
				String[] cmd =
					new String[] { "cmd.exe", "/C", "start", url.toString()};
				Runtime rt = Runtime.getRuntime();
				ColumbaLogger.log.info("Executing " + cmd[0]
						+ " " + cmd[1] + " " + cmd[2] + " " + cmd[3]);
				proc = rt.exec(cmd);
				// any error message?
				StreamGobbler errorGobbler =
					new StreamGobbler(proc.getErrorStream(), "ERROR");
				errorGobbler.start();
				// any output?
				StreamGobbler outputGobbler =
					new StreamGobbler(proc.getInputStream(), "OUTPUT");
				outputGobbler.start();

				// any error?
				int exitVal = proc.waitFor();
				ColumbaLogger.log.info("ExitValue: " + exitVal);
			} catch (Throwable t) {
				t.printStackTrace();
			}
		} else {
			openDocument(url.getPath());
		}
		return null;
	}

	public Process openWithURL(URL url) {
		// *20030714, karlpeder* openDocumentWidth now called
		openDocumentWith(url.getPath());
		return null;
	}

	protected void openDocument(String filename) {
		try {
			Process proc = null;
			if (OSInfo.isWinNT()) {
				String[] cmd = new String[] { "cmd.exe", "/C", filename };
				Runtime rt = Runtime.getRuntime();
				ColumbaLogger.log.info("Executing " + cmd[0]
						 + " " + cmd[1] + " " + cmd[2]);
				proc = rt.exec(cmd);
			} else if (OSInfo.isWin95() || OSInfo.isWin98() || OSInfo.isWinME()) {
				String[] cmd = new String[] { "start", filename };
				Runtime rt = Runtime.getRuntime();
				ColumbaLogger.log.info("Executing " + cmd[0] + " " + cmd[1]);
				proc = rt.exec(cmd);
			} else if (OSInfo.isWin2K() || OSInfo.isWinXP()){

				/*
				 * *20030526, karlpeder* fixing bug #739277 by:
				 * Changing cmd line from "cmd.exe /C ..." to "cmd.exe /C start ..."
				 * So program execution is not blocked until viewer terminates.
				 * NB: WinNT, Win95, Win98, WinME not considered (not able to try it out)
				 *
				 * *20030713, karlpeder* fixing bug #763211 by moving first " in filename
				 * and adding extra parameter to the "start" command = title of
				 * dos window (which is not shown here - but is necessary).
				 */

				String[] cmd = new String[] {
						"cmd.exe", "/C", "start", "\"dummy\"", "\"" + filename + "\""
						};

				Runtime rt = Runtime.getRuntime();
					ColumbaLogger.log.info("Executing " +
						cmd[0] + " " + cmd[1] + " " + cmd[2] + " " +
						cmd[3] + " " + cmd[4]);
				proc = rt.exec(cmd);
			}

            if (proc == null) {
			ColumbaLogger.log.debug("The underlying Windows version is unknown.");
			return;
            }

			// any error message?
			StreamGobbler errorGobbler =
				new StreamGobbler(proc.getErrorStream(), "ERROR");
			errorGobbler.start();
			// any output?
			StreamGobbler outputGobbler =
				new StreamGobbler(proc.getInputStream(), "OUTPUT");
			outputGobbler.start();

			// any error?
			int exitVal = proc.waitFor();
			ColumbaLogger.log.info("ExitValue: " + exitVal);
		} catch (Throwable t) {
			t.printStackTrace();
		}
	}

	/**
	 * Used to open a file with an application specified by the user
	 * using the standard Windows Open With dialog.
	 * @param	filename	Name of file to open
	 * @author 	Karl Peder Olesen (karlpeder) 20030714
	 */
	protected void openDocumentWith(String filename) { 
		
		// TODO: Test with other platforms than Win2000
		
		try {
			Process proc = null;
			if (OSInfo.isWinNT() ||	OSInfo.isWin95() ||
					OSInfo.isWin98() ||	OSInfo.isWinME() || 
					OSInfo.isWin2K() || OSInfo.isWinXP()) {
				
				String[] cmd = new String[] { 
						"rundll32.exe",
						"SHELL32.DLL,OpenAs_RunDLL",
						filename
						};
				
				Runtime rt = Runtime.getRuntime();
				ColumbaLogger.log.info("Executing " + cmd[0]
						 + " " + cmd[1] + " " + cmd[2]);
				proc = rt.exec(cmd);
			}

			if (proc == null) {
				ColumbaLogger.log.debug(
							"The underlying Windows version is unknown.");
				return;
			}

			// any error message?
			StreamGobbler errorGobbler =
				new StreamGobbler(proc.getErrorStream(), "ERROR");
			errorGobbler.start();
			// any output?
			StreamGobbler outputGobbler =
				new StreamGobbler(proc.getInputStream(), "OUTPUT");
			outputGobbler.start();

			// any error?
			int exitVal = proc.waitFor();
			ColumbaLogger.log.info("ExitValue: " + exitVal);
		} catch (Throwable t) {
			t.printStackTrace();
		}
		
	}


	class StreamGobbler extends Thread {
		InputStream is;
		String type;

		StreamGobbler(InputStream is, String type) {
			this.is = is;
			this.type = type;
		}

		public void run() {
			try {
				InputStreamReader isr = new InputStreamReader(is);
				BufferedReader br = new BufferedReader(isr);
				String line = null;
				while ((line = br.readLine()) != null)
					System.out.println(type + ">" + line);
			} catch (IOException ioe) {
				ioe.printStackTrace();
			}
		}
	}
}
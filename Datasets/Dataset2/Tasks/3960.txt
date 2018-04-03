m.setAttribute("columba.fetchstate", Boolean.TRUE);

// The contents of this file are subject to the Mozilla Public License Version
// 1.1
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
//The Initial Developers of the Original Code are Frederik Dietz and Timo
// Stich.
//Portions created by Frederik Dietz and Timo Stich are Copyright (C) 2003.
//
//All Rights Reserved.
package org.columba.mail.pop3;

import java.util.Hashtable;
import java.util.List;

import javax.swing.JOptionPane;

import org.columba.core.command.CommandCancelledException;
import org.columba.core.command.StatusObservable;
import org.columba.core.command.StatusObservableImpl;
import org.columba.core.gui.util.NotifyDialog;
import org.columba.core.logging.ColumbaLogger;
import org.columba.core.main.MainInterface;
import org.columba.core.plugin.PluginHandlerNotFoundException;
import org.columba.core.xml.XmlElement;
import org.columba.mail.config.PopItem;
import org.columba.mail.gui.util.PasswordDialog;
import org.columba.mail.message.ColumbaMessage;
import org.columba.mail.message.ColumbaHeader;
import org.columba.mail.plugin.POP3PreProcessingFilterPluginHandler;
import org.columba.mail.pop3.plugins.AbstractPOP3PreProcessingFilter;
import org.columba.ristretto.message.Header;
import org.columba.ristretto.message.io.CharSequenceSource;
import org.columba.ristretto.message.io.Source;
import org.columba.ristretto.parser.HeaderParser;
import org.columba.ristretto.pop3.parser.SizeListParser;
import org.columba.ristretto.pop3.parser.UIDListParser;
import org.columba.ristretto.pop3.protocol.POP3Protocol;

/**
 * @author freddy
 * 
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates. To enable and disable the creation of
 * type comments go to Window>Preferences>Java>Code Generation.
 */
public class POP3Store {

	public static final int STATE_NONAUTHENTICATE = 0;
	public static final int STATE_AUTHENTICATE = 1;

	private int state = STATE_NONAUTHENTICATE;

	private POP3Protocol protocol;

	private PopItem popItem;

	private POP3PreProcessingFilterPluginHandler handler;

	private Hashtable filterCache;

	private StatusObservableImpl observable;

	/**
	 * Constructor for POP3Store.
	 */
	public POP3Store(PopItem popItem) {
		super();
		this.popItem = popItem;

		protocol =
			new POP3Protocol(
				popItem.get("user"),
				popItem.get("password"),
				popItem.get("host"),
				popItem.getInteger("port"),
				popItem.getBoolean("enable_ssl", false));

		// add status information observable
		observable = new StatusObservableImpl();
		protocol.registerInterest(observable);

		try {

			handler =
				(
					POP3PreProcessingFilterPluginHandler) MainInterface
						.pluginManager
						.getHandler(
					"org.columba.mail.pop3preprocessingfilter");
		} catch (PluginHandlerNotFoundException ex) {
			NotifyDialog d = new NotifyDialog();
			d.showDialog(ex);
		}

		filterCache = new Hashtable();

	}

	/**
	 * Returns the state.
	 * 
	 * @return int
	 */
	public int getState() {
		return state;
	}

	/**
	 * Sets the state.
	 * 
	 * @param state
	 *            The state to set
	 */
	public void setState(int state) {
		this.state = state;
	}

	public List fetchUIDList(int totalMessageCount) throws Exception {

		isLogin();

		String str = protocol.fetchUIDList(totalMessageCount);

		// need to parse here
		List v = UIDListParser.parse(str);

		return v;
	}

	public List fetchMessageSizeList() throws Exception {

		isLogin();

		String str = protocol.fetchMessageSizes();

		// need to parse here
		List v = SizeListParser.parse(str);

		return v;
	}

	public int fetchMessageCount() throws Exception {
		isLogin();

		int messageCount = protocol.fetchMessageCount();

		return messageCount;

	}

	public boolean deleteMessage(int index) throws Exception {

		isLogin();

		return protocol.deleteMessage(index);
	}

	/**
	 * 
	 * load the preprocessing filter pipe on message source
	 * 
	 * @param rawString
	 *            messagesource
	 * @return modified messagesource
	 */
	protected String modifyMessage(String rawString) {
		// pre-processing filter-pipe

		// configuration example (/accountlist/<my-example-account>/popserver):
		//
		//		<pop3preprocessingfilterlist>
		//		  <pop3preprocessingfilter name="myFilter"
		// class="myPackage.MyFilter"/>
		//        <pop3preprocessingfilter name="mySecondFilter"
		// class="myPackage.MySecondFilter"/>
		//		</pop3preprocessingfilterlist>
		//
		XmlElement listElement =
			popItem.getElement("pop3preprocessingfilterlist");

		if (listElement == null)
			return rawString;

		// go through all filters and apply them to the
		// rawString variable
		for (int i = 0; i < listElement.count(); i++) {
			XmlElement rootElement = listElement.getElement(i);
			String type = rootElement.getAttribute("name");

			Object[] args = { rootElement };

			AbstractPOP3PreProcessingFilter filter = null;
			try {

				//		try to re-use already instanciated class
				if (filterCache.containsKey(type) == true) {
					ColumbaLogger.log.debug(
						"re-using cached instanciation =" + type);
					filter =
						(AbstractPOP3PreProcessingFilter) filterCache.get(type);
				} else
					filter =
						(AbstractPOP3PreProcessingFilter) handler.getPlugin(
							type,
							args);

			} catch (Exception ex) {
				ex.printStackTrace();
			}

			if (filter != null) {
				// Filter was loaded correctly
				//  -> apply filter --> modify messagesource

				ColumbaLogger.log.debug("applying pop3 filter..");

				if (filter != null)
					filterCache.put(type, filter);

				rawString = filter.modify(rawString);

				ColumbaLogger.log.debug("rawString=" + rawString);
			}

		}

		return rawString;

	}

	public ColumbaMessage fetchMessage(int index) throws Exception {
		isLogin();

		String rawString = protocol.fetchMessage(new Integer(index).toString());
		if (rawString.length() == 0)
			return null;

		// pipe through preprocessing filter
		if (popItem.getBoolean("enable_pop3preprocessingfilter", false))
			rawString = modifyMessage(rawString);

		Source source = new CharSequenceSource(rawString);

		Header header = HeaderParser.parse(source);

		ColumbaMessage m = new ColumbaMessage(header);
		ColumbaHeader h = (ColumbaHeader) m.getHeaderInterface();

		m.setStringSource(rawString);
		m.setAttribute("columba.host", popItem.get("host"));
		m.setAttribute("columba.fetchstate", new Boolean(true));

		//h.set("columba.pop3uid", (String) uids.get(number - 1));

		return m;
	}

	public void logout() throws Exception {
		boolean b = protocol.logout();

		protocol.close();

		state = STATE_NONAUTHENTICATE;
	}

	public void close() throws Exception {
		protocol.close();

		state = STATE_NONAUTHENTICATE;
	}

	/**
	 * Try to login a user to a given pop3 server. While the login is not
	 * succeed, the connection to the server is opened, then a dialog box is
	 * coming up, then the user should fill in his password. The username and
	 * password is sended to the pop3 server. Then we recive a answer. Is the
	 * answer is false, we try to logout from the server and closing the
	 * connection. The we begin again with open connection, showing dialog and
	 * so on.
	 * 
	 * @param worker
	 *            used for cancel button
	 * @throws Exception
	 * 
	 * Bug number 619290 fixed.
	 */
	public void login() throws Exception {
		PasswordDialog dialog;
		boolean login = false;

		String password = null;
		String user = new String("");
		String method = new String("");
		boolean save = false;

		while (!login) {
			boolean b = protocol.openPort();
			ColumbaLogger.log.debug("open port: " + b);

			ColumbaLogger.log.debug("login==false");
			if ((password = popItem.get("password")).length() == 0) {
				dialog = new PasswordDialog();

				dialog.showDialog(
					popItem.get("user"),
					popItem.get("host"),
					popItem.get("password"),
					popItem.getBoolean("save_password"));

				if (dialog.success()) {
					// ok pressed
					password = new String(dialog.getPassword());

					save = dialog.getSave();

				} else {
					// cancel pressed
					protocol.cancelCurrent();

					throw new CommandCancelledException();
				}
			} else {

				save = popItem.getBoolean("save_password");

			}

			protocol.setLoginMethod(popItem.get("login_method"));
			ColumbaLogger.log.debug("try to login");
			login = protocol.login(popItem.get("user"), password);
			ColumbaLogger.log.debug("login=" + login);

			if (!login) {
				String answer = protocol.answer;

				JOptionPane.showMessageDialog(
					null,
					answer,
					"Authorization failed!",
					JOptionPane.ERROR_MESSAGE);

				popItem.set("password", "");
				state = STATE_NONAUTHENTICATE;

			}

		}

		popItem.set("save_password", save);

		state = STATE_AUTHENTICATE;

		if (save) {

			// save plain text password in config file
			// this is a security risk !!!
			popItem.set("password", password);
		}
	}

	public boolean isLogin() throws Exception {
		if (state == STATE_AUTHENTICATE)
			return true;
		else {
			login();

			return false;
		}
	}

	public StatusObservable getObservable() {
		return observable;
	}
}
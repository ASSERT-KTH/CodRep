if( protocol.getState() != POP3Protocol.NOT_CONNECTED ) {

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

package org.columba.mail.pop3;

import java.io.IOException;
import java.io.InputStream;
import java.text.MessageFormat;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Hashtable;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.logging.Logger;

import javax.net.ssl.SSLException;
import javax.swing.JOptionPane;

import org.columba.core.command.CommandCancelledException;
import org.columba.core.command.StatusObservable;
import org.columba.core.command.StatusObservableImpl;
import org.columba.core.gui.frame.FrameModel;
import org.columba.core.gui.util.MultiLineLabel;
import org.columba.core.util.Blowfish;
import org.columba.mail.config.IncomingItem;
import org.columba.mail.config.PopItem;
import org.columba.mail.gui.util.PasswordDialog;
import org.columba.mail.util.MailResourceLoader;
import org.columba.ristretto.auth.AuthenticationException;
import org.columba.ristretto.auth.AuthenticationFactory;
import org.columba.ristretto.pop3.MessageNotOnServerException;
import org.columba.ristretto.pop3.POP3Exception;
import org.columba.ristretto.pop3.POP3Protocol;
import org.columba.ristretto.pop3.ScanListEntry;
import org.columba.ristretto.pop3.UidListEntry;

/**
 * First abstractionlayer of the POP3 Protocol. Its task is to
 * manage the state of the server and handle the low level connection
 * stuff. This means open the connection using SSL or not, login
 * via the most secure or selected authentication method. It also
 * provides the capabilites to convert an POP3 uid to the index.
 *
 * @see POP3Server
 *
 * @author freddy, tstich
 */
public class POP3Store {
    
    /** JDK 1.4+ logging framework logger, used for logging. */
    private static final Logger LOG = Logger.getLogger("org.columba.mail.pop3");
    
    private POP3Protocol protocol;
    private PopItem popItem;
    private Map filterCache = new Hashtable();
    private StatusObservableImpl observable;
    
    private Map uidMap;
    private List sizeList;
    private String[] capas;
    private int messageCount = -1;
    
    private boolean usingSSL = false;
    
    /**
     * Constructor for POP3Store.
     */
    public POP3Store(PopItem popItem) {
        super();
        this.popItem = popItem;
        
        protocol = new POP3Protocol(popItem.get("host"), popItem.getInteger("port"));
        
        // add status information observable
        observable = new StatusObservableImpl();
    }
    
    public List getUIDList() throws Exception {
        return new ArrayList(getUidMap().keySet());
    }
    
    /** 	 
     * Returns the size of the message with the given index. 	 
     */
    public int getSize(int index) throws IOException, POP3Exception, CommandCancelledException {
        try {
            return ((Integer)getSizeList().get(index)).intValue();
        } catch (IndexOutOfBoundsException e) {
            throw new MessageNotOnServerException(new Integer(index));
        } catch (NullPointerException e){
            throw new MessageNotOnServerException(new Integer(index));
        }
    }
    
    /**
     * @return
     */
    private List getSizeList() throws IOException, POP3Exception, CommandCancelledException {
        if (sizeList == null) {
            ensureTransaction();
            ScanListEntry[] sizes = protocol.list();
            
            sizeList = new ArrayList(sizes.length+1);
            // since the indices on the pop server start with 1 we add
            // a dummy null for the 0 element in the list
            sizeList.add(null);
            
            for (int i = 0; i < sizes.length; i++) {
                if (sizes[i].getIndex() > sizeList.size() - 1) {
                    // fill with nulls
                    for (int nextIndex = sizeList.size() - 1;nextIndex < sizes[i].getIndex(); nextIndex++) {
                        sizeList.add(null);
                    }
                }
                
                // put size at the specified place
                sizeList.set(sizes[i].getIndex(), new Integer(sizes[i].getSize()));
            }
        }
        
        return sizeList;
    }
    
    /** 	 
     * Returns the number of messages on the server. 	 
     */
    public int getMessageCount() throws IOException, POP3Exception, CommandCancelledException {
        if (messageCount == -1) {
            ensureTransaction();
            int[] stat = protocol.stat();
            messageCount = stat[0];
        }
        
        return messageCount;
    }
    
    /** 	 
     * Deletes the message with the given UID from the server. 	 
     */
    public boolean deleteMessage(Object uid) throws CommandCancelledException, IOException, POP3Exception {
        ensureTransaction();
        return protocol.dele(getIndex(uid));
    }
    
    protected int getIndex(Object uid) throws IOException, POP3Exception,
    CommandCancelledException {
        
        if (getUidMap().containsKey(uid)) {
            return ((Integer)getUidMap().get(uid)).intValue();
        } else {
            throw new MessageNotOnServerException(uid);
        }
    }
    
    public InputStream fetchMessage(int index) throws IOException, POP3Exception, CommandCancelledException {
        ensureTransaction();
        return protocol.retr(index, getSize(index));
    }
    
    public void logout() throws IOException, POP3Exception {
        if( protocol.getState() != POP3Protocol.CONNECTION_CLOSED ) {
        	protocol.quit();
        }
        uidMap = null;
        sizeList = null;
        messageCount = -1;
    }
    
    /**
     * Returns whether a given POP3 command is supported by the server.
     */
    protected boolean isSupported(String command) throws IOException {
        fetchCapas();
        for (int i = 0; i < capas.length; i++) {
            if (capas[i].startsWith(command)) {
                return true;
            }
        }
        return false;
    }
    
    protected String getCapa(String command) throws IOException {
        fetchCapas();
        for (int i = 0; i < capas.length; i++) {
            if (capas[i].startsWith(command)) {
                return capas[i];
            }
        }
        return null;
    }
    
    
    private void fetchCapas() throws IOException {
        if (capas == null) {
            try {
                capas = protocol.capa();
            } catch (POP3Exception e) {
                // CAPA not supported
                capas = new String[]{};
            }
        }
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
    protected void login() throws IOException, POP3Exception,
    CommandCancelledException {
        PasswordDialog dialog;
        boolean login = false;
        
        char[] password = new char[0];
        String user = "";
        String method = "";
        boolean save = false;
        
        int loginMethod = getLoginMethod();
        
        while (!login) {
            if ((password = Blowfish.decrypt(popItem.getRoot().getAttribute("password", "")
            )).length == 0) {
                dialog = new PasswordDialog();
                
                dialog.showDialog(MessageFormat.format(MailResourceLoader
						.getString("dialog", "password", "enter_password"),
						new Object[] { popItem.get("user"), popItem.get("host") }),
                    popItem.get("password"), popItem.getBoolean("save_password"));
                
                if (dialog.success()) {
                    // ok pressed
                    password = dialog.getPassword();
                    save = dialog.getSave();
                } else {
                    throw new CommandCancelledException();
                }
            } else {
                save = popItem.getBoolean("save_password");
            }
            
            try {
                if (loginMethod == AuthenticationManager.USER) {
                    protocol.userPass(popItem.get("user"), password);
                    login = true;
                } else if (loginMethod == AuthenticationManager.APOP) {
                    try {
						protocol.apop(popItem.get("user"), password);
					} catch (POP3Exception e1) {
						// some server have a bogus apop
						// try user/pass to check if the password is
						// correct
						protocol.userPass(popItem.get("user"), password);
						
						LOG.warning(popItem.get("host") + " : bogus APOP implementation -> falling back to USER/PASS.");
						
						// user/pass worked -> this is indeed
						// a bogus server.
					}
                    login = true;
                } else {
                    try {
                        //AUTH
                        protocol.auth(AuthenticationManager.getSaslName(loginMethod),
                            popItem.get("user"), password);
                        login = true;
                    } catch (AuthenticationException e) {
						// If the cause is a IMAPExcpetion then only password wrong
						// else bogus authentication mechanism
						if( e.getCause() instanceof POP3Exception) throw (POP3Exception) e.getCause();
                    	
                        // Some error in the client/server communication
                        //  --> fall back to default login process
                        int result = JOptionPane.showConfirmDialog(
                        		FrameModel.getInstance().getActiveFrame(),
                            new MultiLineLabel(e.getMessage() + "\n" +
                                MailResourceLoader.getString("dialog", "error",
                                "authentication_fallback_to_default")),
                                MailResourceLoader.getString("dialog", "error",
                                "authentication_process_error"), JOptionPane.OK_CANCEL_OPTION);
                        if (result == JOptionPane.OK_OPTION) {
                            loginMethod = AuthenticationManager.USER;
                            popItem.setString("login_method", Integer.toString(loginMethod));
                        } else {
                            throw new CommandCancelledException();
                        }
                    }
                }
            } catch (POP3Exception e) {
                JOptionPane.showMessageDialog(null, e.getMessage(),
                    "Authorization failed!", JOptionPane.ERROR_MESSAGE);
                
                popItem.setString("password", "");
            }
            
            LOG.info("login=" + login);
        }
        
        popItem.setBoolean("save_password", save);
        
        if (save) {
            popItem.setString("password", Blowfish.encrypt(password));
        }
    }
    
    public List checkSupportedAuthenticationMethods() throws CommandCancelledException, IOException {
        ArrayList supportedMechanisms = new ArrayList();
        //USER/PASS is always supported
        supportedMechanisms.add(new Integer(AuthenticationManager.USER));
        
        try {
            ensureAuthorization();
            
            //APOP?
            if (protocol.isApopSupported()) {
                supportedMechanisms.add(new Integer(AuthenticationManager.APOP));
            }
        } catch (POP3Exception e) {
            //APOP not supported
        }
        
        try {
            String serverSaslMechansims = getCapa("SASL");
            
            //AUTH?
            if (serverSaslMechansims != null) {
                List authMechanisms = AuthenticationFactory.getInstance().getSupportedMechanisms(serverSaslMechansims);
                Iterator it = authMechanisms.iterator();
                while (it.hasNext()) {
                    supportedMechanisms.add(new Integer(
                        AuthenticationManager.getSaslCode((String)it.next())));
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
        
        return supportedMechanisms;
    }
    
    /**
     * Gets the selected Authentication method or else the most secure.
     *
     * @return the authentication method
     */
    private int getLoginMethod() throws CommandCancelledException, IOException {
        String loginMethod = popItem.get("login_method");
        int result = 0;
        
        try {
            result = Integer.parseInt(loginMethod);
        } catch (NumberFormatException e) {
            //Just use the default as fallback
        }
        
        if (result == 0) {
            List supported = checkSupportedAuthenticationMethods();
            
            if (usingSSL) {
                // NOTE if SSL is possible we just need the plain login
                // since SSL does the encryption for us.
                result = ((Integer)supported.get(0)).intValue();
            } else {
                Collections.sort(supported, new AuthenticationSecurityComparator());
                result = ((Integer)supported.get(supported.size() - 1)).intValue();
            }
            
        }
        
        return result;
    }
    
    public static void doPOPbeforeSMTP(PopItem popItem) throws IOException,
    POP3Exception, CommandCancelledException {
        POP3Store store = new POP3Store(popItem);
        store.ensureTransaction();
        store.logout();
    }
    
    protected void ensureTransaction() throws IOException, POP3Exception,
    CommandCancelledException {
        ensureAuthorization();
        if (protocol.getState() < POP3Protocol.TRANSACTION) {
            login();
        }
    }
    
    protected void ensureAuthorization() throws IOException, POP3Exception,
    CommandCancelledException {
        if (protocol.getState() < POP3Protocol.AUTHORIZATION) {
            openConnection();
        }
    }
    
    /**
     *
     */
    private void openConnection() throws IOException, POP3Exception,
    CommandCancelledException {
        int sslType = popItem.getIntegerWithDefault("ssl_type", IncomingItem.TLS);
        boolean sslEnabled = popItem.getBoolean("enable_ssl");
        
        // open a port to the server
        if (sslEnabled && sslType == IncomingItem.IMAPS_POP3S) {
            try {
                protocol.openSSLPort();
                usingSSL = true;
            } catch (SSLException e) {
                int result = showErrorDialog(MailResourceLoader.getString(
                    "dialog", "error", "ssl_handshake_error") + ": "
                    + e.getLocalizedMessage() + "\n"
                    + MailResourceLoader.getString("dialog", "error",
                    "ssl_turn_off"));
                
                if (result == JOptionPane.CANCEL_OPTION) {
                    throw new CommandCancelledException();
                }
                
                // turn off SSL for the future
                popItem.setBoolean("enable_ssl", false);
                popItem.setInteger("port", POP3Protocol.DEFAULT_PORT);
                
                // reopen the port
                protocol.openPort();
            }
        } else {
            protocol.openPort();
        }
        
        // shall we switch to SSL?
        if (!usingSSL && sslEnabled && sslType == IncomingItem.TLS) {
            // if CAPA was not support just give it a try...
            if (isSupported("STLS") || capas.length == 0) {
                try {
                    protocol.startTLS();
                    
                    usingSSL = true;
                    LOG.info("Switched to SSL");
                } catch (IOException e) {
                    int result = showErrorDialog(MailResourceLoader.getString(
                        "dialog", "error", "ssl_handshake_error") + ": "
                        + e.getLocalizedMessage() + "\n"
                        + MailResourceLoader.getString("dialog", "error",
                        "ssl_turn_off"));
                    
                    if (result == JOptionPane.CANCEL_OPTION) {
                        throw new CommandCancelledException();
                    }
                    
                    // turn off SSL for the future
                    popItem.setBoolean("enable_ssl", false);
                    
                    // reopen the port
                    protocol.openPort();
                } catch (POP3Exception e) {
                    int result = showErrorDialog(MailResourceLoader.getString(
                        "dialog", "error", "ssl_not_supported") + "\n"
                        + MailResourceLoader.getString("dialog", "error",
                        "ssl_turn_off"));
                    
                    if (result == JOptionPane.CANCEL_OPTION) {
                        throw new CommandCancelledException();
                    }
                    
                    // turn off SSL for the future
                    popItem.setBoolean("enable_ssl", false);
                }
            } else {
                // CAPAs say that SSL is not supported
                int result = showErrorDialog(MailResourceLoader.getString(
                    "dialog", "error", "ssl_not_supported") + "\n"
                    + MailResourceLoader.getString("dialog", "error",
                    "ssl_turn_off"));
                
                if (result == JOptionPane.CANCEL_OPTION) {
                    throw new CommandCancelledException();
                }
                
                // turn off SSL for the future
                popItem.setBoolean("enable_ssl", false);
            }
        }
    }
    
    private int showErrorDialog(String message) {
        int result = JOptionPane.showConfirmDialog(null, message, "Warning",
            JOptionPane.WARNING_MESSAGE, JOptionPane.OK_CANCEL_OPTION);
        return result;
    }
    
    public StatusObservable getObservable() {
        return observable;
    }
    
    /**
     * @return Returns the uidMap.
     */
    private Map getUidMap() throws CommandCancelledException, IOException, POP3Exception {
        if (uidMap == null) {
            if (getMessageCount() != 0) {
                ensureTransaction();
                
                UidListEntry[] uidList = protocol.uidl();
                uidMap = new Hashtable();
                
                for (int i = 0; i<uidList.length; i++) {
                    uidMap.put(uidList[i].getUid(), new Integer(uidList[i].getIndex()));
                }
            } else {
                uidMap = new Hashtable(0);
            }
        }
        return uidMap;
    }

	/**
	 * @throws IOException
	 * 
	 */
	public void dropConnection() throws IOException {
		protocol.dropConnection();
	}
}
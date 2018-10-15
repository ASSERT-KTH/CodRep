package org.eclipse.ecf.internal.example.collab;

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

package org.eclipse.ecf.example.collab;

public interface ClientPluginConstants {
//	public static final String PLUGIN_ID = "org.eclipse.ecf.example.collab";

	public static final String DEFAULT_WIN32_APPSHARE_NAME = "appsharewin32display";
    public static final String DEFAULT_FILE_TRANSFER_CHUNKTIME_NAME = "filetransferchunksize";
    public static final String DEFAULT_FILE_TRANSFER_DELAY_NAME= "filetransferdelay";

    /*
     * Contants for perference items.
     */
	public static final String PREF_USE_CHAT_WINDOW = "useChatWindow";
	public static final String PREF_DISPLAY_TIMESTAMP = "displayTimeStamp";
	public static final String PREF_CHAT_FONT = "chatFont";
	public static final String PREF_FILE_TRANSFER_RATE = "fileTransferRate";
	public static final String PREF_CONFIRM_FILE_SEND = "confirmFileSend";
	public static final String PREF_CONFIRM_REMOTE_VIEW = "confirmRemoteView";
	public static final String PREF_FILE_SEND_PATH = "findSendPath";
	public static final String PREF_CONFIRM_FILE_RECEIVE = "confirmFileReceive";
	public static final String PREF_ME_TEXT_COLOR = "prefMeTextColor";
	public static final String PREF_OTHER_TEXT_COLOR = "prefOtherTextColor";
	public static final String PREF_SYSTEM_TEXT_COLOR = "prefSystemTextColor";
	
	public static final String PREF_START_SERVER = "startServerOnStartup";
	public static final String PREF_REGISTER_SERVER = "registerServerOnStartup";
	
	public static final String PREF_SHAREDEDITOR_PLAY_EVENTS_IMMEDIATELY = "sharedEditorShowEvents";
	public static final String PREF_SHAREDEDITOR_ASK_RECEIVER = "sharedEditorAskReceiver";
	public static final String PREF_STORE_PASSWORD = "storePassword";
	/*
	 * Contstants used to describe decoration images.
	 */
	public static final String DECORATION_PROJECT = "resource";
	public static final String DECORATION_USER = "user";
	public static final String DECORATION_TIME = "time";
	public static final String DECORATION_TASK = "task";
	public static final String DECORATION_SEND = "send";
	public static final String DECORATION_RECEIVE = "receive";
	public static final String DECORATION_PRIVATE = "private";
	public static final String DECORATION_SYSTEM_MESSAGE = "system message";
	
	public static final String SHARED_MARKER_TYPE = "org.eclipse.ecf.example.collab.sharedmarker";
	public static final String SHARED_MARKER_KEY = "owner";

	public static final String DECORATION_DEFAULT_PROVIDER = "DECORATION_DEFAULT_PROVIDER";

}
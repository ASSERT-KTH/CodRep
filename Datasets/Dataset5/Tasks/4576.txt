debug(e,"Exception in receive start");

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

package org.eclipse.ecf.example.collab.share.io;

import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;

import org.eclipse.ecf.core.ISharedObjectConfig;
import org.eclipse.ecf.core.SharedObjectDescription;
import org.eclipse.ecf.core.SharedObjectInitException;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.example.collab.Trace;
import org.eclipse.ecf.example.collab.share.TransactionSharedObject;
import org.eclipse.ecf.example.collab.share.SharedObjectMsg;


public class FileTransferSharedObject extends TransactionSharedObject
{
    public static final Trace debug = Trace.create("filetransfersharedobject");

    public static final int DEFAULT_START_WAIT_INTERVAL = 5000;

    public static final String recvMethodName = "handleData";
    public static final String doneMethodName = "handleDone";
    public static final String startMethodName = "startSendToAll";
    // Both host and client
    protected FileTransferParams transferParams;
    protected FileTransferListener progressListener;
    // Host only
    protected ID targetReceiver;
    protected InputStream inputStream;
    // Client only
    protected OutputStream outputStream;
    protected long dataWritten = -1;

    public FileTransferSharedObject(ID receiver, InputStream ins, FileTransferParams params)
    {
        targetReceiver = receiver;
        if (ins == null) throw new NullPointerException("Input stream cannot be null");
        setInputStream(ins);
        if (params == null) {
            transferParams = new FileTransferParams();
        } else transferParams = params;
        progressListener = transferParams.getProgressListener();
        debug("<init>("+receiver+", "+ins+", "+params+")");
    }
    public FileTransferSharedObject() {
        super();
    }
    protected void setInputStream(InputStream src)
    {
        inputStream = src;
    }

    protected void setOutputStream(OutputStream src)
    {
        outputStream = src;
    }

    public FileTransferSharedObject(InputStream ins, FileTransferParams params)
    {
        this(null, ins, params);
    }

    public FileTransferSharedObject(InputStream ins)
    {
        this(null, ins, null);
    }

    public FileTransferSharedObject(FileTransferParams params)
    {
        if (params == null) {
            transferParams = new FileTransferParams();
        } else transferParams = params;
        progressListener = transferParams.getProgressListener();
        debug("<init>("+params+")");
    }
    public void activated(ID [] others)
    {
    	debug("activated()");
        try {
            // Only try to open output file if this is not the host instance
            if (!isHost() && !getContext().isGroupServer()) {
                // Then notify listener about starting the receive
                if (progressListener != null) {
                    progressListener.receiveStart(this, transferParams.getRemoteFile(), transferParams.getLength(), transferParams.getRate());
                }
                openOutputFile();
                long len = transferParams.getLength();
                if (len != -1) {
                    dataWritten = 0;
                }
            } else {
                // Just notify listener (if any) about the sending
                if (progressListener != null) {
                    progressListener.sendStart(this, transferParams.getLength(), transferParams.getRate());
                }
            }
        } catch (Exception e) {
        	debug(e,"Exception sending failure back to host");
            try {
                // Respond with create failure message back to host
                getContext().sendCreateResponse(getHomeContainerID(), e, getIdentifier());
            } catch (Exception e1) {
            	debug(e1,"Exception sending failure back to host");
             }
            return;
        }
        // Finally, call activated to report success
        super.activated(others);
    }
	protected void debug(Throwable e, String msg) {
		if (Trace.ON && debug != null) {
            debug.dumpStack(e, msg);
		}
	}
	protected void debug(String msg) {
		if (Trace.ON && debug != null) {
            debug.msg(msg);
		}
	}
    /**
     */
    protected void postOpenFile()
    {
    	debug("postOpenFile()");
    }
    protected void openOutputFile() throws IOException
    {
        File aFile = transferParams.getRemoteFile();
        if (aFile == null) throw new IOException("File is null");
        // If this is a server, and we shouldn't create a copy of ourselves on a server
        // then we skip the file creation totally
        if (getContext().isGroupServer() && !transferParams.getIncludeServer()) {
            // Set myFile to null and outputStream to null
            debug("File "+aFile+" not created on server.");
            setOutputStream(null);
        } else {
        	debug("File "+aFile+" being created");
            try {
                String parent = aFile.getParent();

                if (parent != null && new File(parent).mkdirs())
                    /**/;
            } catch(Exception ex) {
                // Ignore this exception.
                debug(ex, "Exception creating local directory for "+aFile);
            }
            setOutputStream(new BufferedOutputStream(new FileOutputStream(aFile)));
        }
        postOpenFile();
    }

     protected void replicate(ID remoteMember)
     {
        // If we don't have a specific receiver, simply allow superclass to handle replication.
        if (targetReceiver == null) { super.replicate(remoteMember); return; }
        // If we do have a specific receiver, only send create message to the specific receiver
        // if we're replicating on activation
        else if (remoteMember == null) {
            try {
                SharedObjectDescription createInfo = getReplicaDescription(targetReceiver);
                if (createInfo != null) {
                	getContext().sendCreate(targetReceiver, createInfo);
                    return;
                } 
            } catch (IOException e) {
                traceDump("Exception in replicateSelf",e);
                return;
            }
        }
    }
    public void init(ISharedObjectConfig config) throws SharedObjectInitException {
        super.init(config);
        Map map = config.getProperties();
        Object [] args = (Object []) map.get("args");
        if (args != null && args.length == 1) {
            transferParams = (FileTransferParams) args[0];
            progressListener = transferParams.getProgressListener();
        }
    }
    protected SharedObjectDescription getReplicaDescription(ID remoteMember)
    {
    	HashMap map = new HashMap();
    	map.put("args",new Object [] { transferParams });
    	map.put("types",new String [] { FileTransferParams.class.getName() });
        return new SharedObjectDescription(getID(),
                                        getClass().getName(),map,
                                        replicateID++);
    }

    protected boolean sendData(ID rcvr, FileData data) throws IOException
    {
        // Send it.  This does all data delivery.
        forwardMsgTo(rcvr, SharedObjectMsg.makeMsg(recvMethodName, data));
        return data.isDone();
    }

    protected boolean sendChunk(ID rcvr) throws IOException
    {
        FileData data = new FileData(inputStream, transferParams.getChunkSize());
        int size = data.getDataSize();
        if (progressListener != null && size != -1) progressListener.sendData(this, size);
        return sendData(rcvr, data);
    }

    protected void handleData(FileData data)
    {
        preSaveData(data);
        // Then save the file data.
        int size = data.getDataSize();
        if (progressListener != null && size != -1) progressListener.receiveData(this, size);
        saveData(data);
    }

    protected void preSaveData(FileData data)
    {
        if (data.myData != null && outputStream != null) {
        	debug("Saving "+data.read+" bytes.");
        } else {
        	debug("Not saving data locally");
        }
    }

    /**
     * Save data to File.  This method is called by handleData to actually
     * save data received (on the clients only) to the appropriate file.
     *
     * @param data the FileData to save
     */
    protected void saveData(FileData data)
    {
        // Save data locally...if we have an output stream
        try {
            if (outputStream != null) {
            	debug("saveData("+data+")");
                long len = transferParams.getLength();
                dataWritten += data.getDataSize();
                if (len != -1 && dataWritten > len) throw new IOException("File larger than "+len);
                data.saveData(outputStream);
                // Flush to verify that data was saved.
                outputStream.flush();
            }
        } catch (Exception e) {
        	debug(e,"Exception saving data");
            // Give subclasses opportunity to deal with this
            notifyExceptionOnSave(e);
            // Report failure back to host if we're not disconnected
            try {
                // Send it.  This does the done msg delivery.
                forwardMsgHome(SharedObjectMsg.makeMsg(doneMethodName, e));
                // Make sure everything is cleaned up
                hardClose();
            } catch (Exception e1) {
                // If this fails...then we should be outta here
                debug(e1, "Exception sending done msg back to host");
            }
            if (progressListener != null) progressListener.receiveDone(this, e);
            return;
        }
        Exception except = null;
        // If everything saved OK, and that was the last piece, then close
        // and report success.
        if (data.isDone()) {
            try {
                // Make sure everything is cleaned up
                hardClose();
            } catch (Exception e1) {
                // If this fails...then we should be outta here
                debug(e1,"Exception saving file.");
                except = e1;
                notifyExceptionOnClose(except);
            }
            // Calling the progress listener first, so that the reference
            // to ourselves will be valid even if doneReceiving kills this
            // object
            if (progressListener != null) progressListener.receiveDone(this, except);
            try {
                forwardMsgHome(SharedObjectMsg.makeMsg(doneMethodName, except));
            } catch (Exception e) {
            	debug(e,"Exception sending done message home");
            }
            // Now call doneReceiving...which may destroy us
            doneReceiving();
        }
    }

    protected void notifyExceptionOnSave(Throwable t)
    {
        // By default, do nothing
    }

    protected void notifyExceptionOnClose(Throwable t)
    {
        // By default, do nothing
    }

    public void doneReceiving()
    {
    	debug("File "+transferParams.getRemoteFile()+" received.");
    }
    /**
     * Handler for done msg.  NOTE:  If this method name is changed,
     * then the static variable 'doneMethodName' should be changed to match.
     *
     * @param data the FileData involved in the failure
     */
    public void handleDone(Exception e)
    {
        debug("handleDone("+e+")");
    }

    protected void preStartWaiting()
    {
		debug("preStartWaiting()");
    }

    protected void preStartSending()
    {
		debug("preStartSending()");
    }

    protected void preChunkSent()
    {
		debug("preChunkSent()");
    }

    protected void chunkSent()
    {
		debug("chunkSent()");
    }

    protected void doneSending(Exception e)
    {
		debug("doneSending("+e+")");
        if (progressListener != null) progressListener.sendDone(this, e);
    }

    protected void committed()
    {
		debug("committed()");
        preStartWaiting();
        start();
    }

    protected void preWait()
    {
		debug("preWait() until "+transferParams.getStartDate());
    }

    protected void start()
    {
		debug("start()");
        if (isHost()) {
            Date start = transferParams.getStartDate();
            if (start != null && start.after(new Date())) {
                try {
                    preWait();
                    synchronized (this) {
                        wait(DEFAULT_START_WAIT_INTERVAL);
                    }
                    // Asynchronous tail recursion.
                    sendSelf(SharedObjectMsg.makeMsg("start"));
                } catch (Exception e) {}
            } else {
                preStartSending();
                // Actually begin
                startSendToAll();
            }
        }
    }
    /**
     * Start sending data to all clients.  This is the entry point method for sending
     * the desired data to remotes.
     */
    protected void startSendToAll()
    {
        // Send chunks to all remotes until done.
        try {
            // Call subclass overrideable method before sending chunk
            preChunkSent();
            // Send chunk
            boolean res = sendChunk(targetReceiver);
            // Call subclass overrideable method after sending chunk
            chunkSent();
            if (!res) {
                synchronized (this) {
                	int waittime = transferParams.getWaitTime();
                	if (waittime <=0) waittime = 10;
                    wait(waittime);
                }
                // If all data not sent, send message to self.  This results
                // in this method iterating until entire file is sent.
                sendSelf(SharedObjectMsg.makeMsg(startMethodName));
            } else {
                // Close input stream.
                hardClose();
                doneSending(null);
            }
        } catch (Exception e) {
            doneSending(e);
        }
    }

    protected void hardClose() throws IOException
    {
        if (inputStream != null) {
        	try {
        		inputStream.close();
        	} catch (Exception e) {}
            inputStream = null;
        }
        if (outputStream != null) {
        	try {
        		outputStream.close();
        	} catch (Exception e) {}
            outputStream = null;
        }
    }

    public void deactivated()
    {
        super.deactivated();
        debug("deactivated()");
        // Make sure things are cleaned up properly in case of wrong trousers
        try {
            hardClose();
        } catch (Exception e) {}
    }

}
 No newline at end of file
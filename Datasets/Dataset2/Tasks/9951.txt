System.out.println("error in run " + ie);

/*
 * @(#) ProcessesManager.java	1.0 02/07/15
 *
 * Copyright (C) 2002 - INRIA (www.inria.fr)
 *
 * CAROL: Common Architecture for RMI ObjectWeb Layer
 *
 * This library is developed inside the ObjectWeb Consortium,
 * http://www.objectweb.org
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or any later version.
 * 
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 * 
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307
 * USA
 * 
 *
 */
package org.objectweb.carol.util.bootstrap;

import java.util.Hashtable;
import java.util.Enumeration;

import java.io.OutputStream;
import java.io.InputStream;
import java.io.FileOutputStream;
import java.io.FileInputStream;
import java.io.File;
import java.io.IOException;
	   
import java.util.jar.JarOutputStream;
import java.util.jar.JarInputStream;
import java.util.jar.JarFile;
import java.util.zip.ZipEntry;

import java.rmi.RemoteException;

/**
 * Class <code>ProcessesManager</code>Provide a Process Manager
 * for boostraping Process and send file to a process directory
 * Thie class extends a remote interface for RMI calls
 * 
 * 
 * @author  Guillaume Riviere (Guillaume.Riviere@inrialpes.fr)
 * @version 1.0, 15/11/2002
 *
 */

public class ProcessesManager implements RemoteProcessesManager {
 
    /**
     * Verbose boolean (default false)
     */
    private static boolean verbose = false;

    /**
     * clean processes/configuration hashtable at shudow (default TRUE) 
     *
	commands.clear();
	directories.clear(); Be carful, TRUE for this variable mean one more shudow THREAD
     * in the daemon  
     */
    public static boolean CLEAN_PROCESSES=true;

    /**
     * wait time for processe starting before getting error stream
     */
    public static final int START_WAIT_TIME=1000;

    /**
     * Java command line
     */
    public static String JAVA_CMD="java ";

    /**
     * Processes Hashtable with id
     */
    public static Hashtable processes = new Hashtable();
    
    /**
     * Object configuration with id
     */
    public static Hashtable commands = new Hashtable();

    /**
     * Object configuration with id
     */
    public static Hashtable directories = new Hashtable();

    /**
     * id variable
     */
    private static int idIcrement = 0; 

    /**
     * empty constructor 
     */
    public ProcessesManager() throws RemoteException {
    }

    /**
     * constructor with 2 param:
     * @param boolean cleanb for clean mode
     * @param boolean vb for verbose mode 
     */
    public ProcessesManager(boolean cleanb, boolean vb) throws RemoteException {
	CLEAN_PROCESSES=cleanb;
	verbose = vb;
    }

    /**
     * get a new Process id
     */
    private synchronized String getNewID() {
	idIcrement ++;
	return "p_"+idIcrement;
    }

    /**
     * clean process environment
     * this method just clean the hastable and directory
     * it not stop the process
     * @param String id the process id 
     */
    private void cleanProcess(String id) {
	File dirName = (File)directories.get(id);
	processes.remove(id);
	commands.remove(id); 
	directories.remove(id);

	// erase the directory if existe 
	recursiveRemoveDir(dirName);
    }

    /**
     * recursive delting of a directories if existe
     * this method only allow to make deletion of 
     * File directory inside the current directory
     * Your are not allow to delete other directory
     * and the directory is not deleted in this case
     *
     * @param File to delete 
     * 
     */
    private void recursiveRemoveDir(File dir) {
	if (dir != null) {
	    if (verbose) {
		System.out.println("Delete dir: " + dir);
	    }
	    if (System.getProperty("user.dir").trim().equals(dir.getParent().trim())) {
		String[] filelist = dir.list();
		File tmpFile = null;
		for (int i = 0; i < filelist.length; i++) {
		    if (verbose) {
			System.out.println("Delete Sub directory or file : " + filelist[i]);
		    }
		    tmpFile = new File(dir.getAbsolutePath(),filelist[i]);
		    if (tmpFile.isDirectory()) {
			recursiveRemoveDir(tmpFile);
		    } else if (tmpFile.isFile()) {     
			tmpFile.delete();
		    }
		} 
		dir.delete();
	    }
	}
    }

    /**
     * create a directory inside the current directory
     * if the directory existe do nothing
     *
     * @param String dir name to create
     * @throws ProcessException if a probleme occurs in the creation
     * @return File the created directory
     *
     */
    private File createDir(String dir) throws ProcessException {
	// test if the directory existe and if not create it
	File pDirFile = new File(System.getProperty("user.dir") + System.getProperty("file.separator") + dir);
	if((pDirFile.exists())) {
	    if (!(pDirFile.isDirectory())) {
		throw new ProcessException(pDirFile + " file is not a directory");
	    } else if (!(pDirFile.canRead())) {
		throw new ProcessException("Un-readable directory :" + pDirFile);
	    } else if (!(pDirFile.canWrite())) {
		throw new ProcessException("Un-writable directory :" + pDirFile);
	    }
	} else if (!(pDirFile.mkdir())) {
	    // can not build directory
	    throw new ProcessException("Can not mkdir directory :" + pDirFile);
	}
	return pDirFile;
    }


    /**
     * get Process output
     * @param p process
     * @return String process output or null if p is not available 
     */
    protected String getProcessOutput(Process p) {
	try {
	    InputStream pOutputStream = p.getInputStream();
	    byte [] b = new byte[pOutputStream.available()];
	    pOutputStream.read(b);
	    pOutputStream.close();
	    return new String(b);
	} catch (Exception pe) {
	    return null;
	}
    }

    /**
     * get Process error
     * @param p process
     * @return String process error or null if p is not available 
     */
    protected String getProcessError(Process p) {
	try {
	    InputStream pErrorStream = p.getErrorStream();
	    byte [] b = new byte[pErrorStream.available()];
	    pErrorStream.read(b);
	    pErrorStream.close();
	    return new String(b);
	} catch (Exception pe) {
	    return null;
	}
    }
 
    /**
     * Start a jvm process on the remote host in a tmp directory
     * @param JVMConfiguration configuration
     * @param String [] env property: "pkey=pvalue" can be null if there is no proprerty
     * @return String the process id
     * @throws ProcessException if an exception occurs at bootstrapting
     */
    public String startJVM(JVMConfiguration jvmConf, String [] envp) throws ProcessException, RemoteException {
	return startProcess(JAVA_CMD + jvmConf.getCommandString(), envp);
    }

    /**
     * Start a jvm process on the remote host
     * @param JVMConfiguration configuration
     * @param String [] env property: "pkey=pvalue" can be null if there is no proprerty
     * @param String processDir directory where to launch the process
     * @return String the process id
     * @throws ProcessException if an exception occurs at bootstrapting
     */
    public String startJVM(JVMConfiguration jvmConf, String [] envp, String processDir) throws ProcessException, RemoteException {
	return startProcess(JAVA_CMD + jvmConf.getCommandString(), envp, processDir);
    }

    /**
     * Start a jvm process on the remote host
     * @param JVMConfiguration configuration
     * @param String [] env property: "pkey=pvalue" can be null if there is no proprerty
     * @param String processDir directory where to launch the process 
     *               (inside the current directory and without file separator);
     * @param String the process id
     * @throws RProcessException if an exception occurs at bootstrapting
     */
    public void startJVM(JVMConfiguration jvmConf, String [] envp, String processDir, String id) throws ProcessException, RemoteException {
	startProcess(JAVA_CMD + jvmConf.getCommandString(), envp, processDir, id);
    }

    /**
     * Start a process on the remote host in a tmp directory
     * @param String processLine to launch the process
     * @param String [] env property: "pkey=pvalue" can be null if there is no proprerty
     * @return String the process id
     * @throws ProcessException if an exception occurs at bootstrapting
     */
    public String startProcess(String processLine, String [] envp) throws ProcessException, RemoteException  {
	String newid = getNewID();
	String processDir = "tmp_" + newid;
	startProcess(processLine, envp, processDir, newid);
	return newid;
    }

    /**
     * Start a process on the remote host
     * @param String processLine to launch the process
     * @param String [] env property: "pkey=pvalue" can be null if there is no proprerty
     * @param String processDir directory where to launch the process
     * @return String the process id
     * @throws ProcessException if an exception occurs at bootstrapting
     */
    public String startProcess(String processLine, String [] envp, String processDir) throws ProcessException, RemoteException  {
	String newid = getNewID();
	startProcess(processLine, envp, processDir, newid);
	return newid;
    }

    /**
     * Start a process on the remote host
     * @param String processLine to launch the process
     * @param String [] env property: "pkey=pvalue" can be null if there is no proprerty
     * @param String processDir directory where to launch the process 
     *               (inside the current directory and without file separator);
     * @param String the process id
     * @throws RProcessException if an exception occurs at bootstrapting
     */
    public void startProcess(String processLine, String [] envp, String processDir, String id) throws ProcessException, RemoteException  {
	Process p = null;
	if (verbose) {
	    System.out.println("Start a new Process with id: " + id);
	    System.out.println("and with : " + processLine);
	    System.out.println("in : " +  processDir);
	}
	
	File pDir = createDir(processDir);

	if ((commands.get(id)!=null) || (processes.get(id)!=null)||(directories.get(id)!=null)){
	    throw new ProcessException("Process Name already exist");
	} else {
	    try {
		p = Runtime.getRuntime().exec(processLine, envp, pDir);
		Thread.sleep(START_WAIT_TIME);
		int ev = p.exitValue();
		String processErr =  "\nProcess error  :\n" + getProcessOutput(p);
		String processOut =  "\nProcess output  :\n" + getProcessError(p);		
		cleanProcess(id);
		throw new ProcessException("The Process just stop after starting, exit value= " + ev +  processErr + processOut);

	    } catch (IllegalThreadStateException ite) {

		// the Tread is not yet terminated, OK continue 
		processes.put(id, p);
		commands.put(id, processLine);
		directories.put(id, pDir);
		// lauch a new process shudown thread if CLEAN_PROCESSES true
		if (CLEAN_PROCESSES) {
		    ProcessStopThread s = new ProcessStopThread(p, id);
		    s.start();
		}
	    } catch (IOException ioe) {
		throw new ProcessException("The Process is not started" + ioe.getMessage());
	    } catch (InterruptedException ite) {
		throw new ProcessException("The Process is not started" + ite.getMessage());
	    }
	}
    }



    /**
     * Kill a process (if existe) and remove it's process id and configuration
     * @param id the Process id 
     * @throws ProcessException if the id doesn't existe
     */
    public synchronized void killProcess(String id) throws ProcessException, RemoteException {
	if (verbose) {
	    System.out.println("Kill a Process with id: " + id);
	}
	if (processes.containsKey(id)) {
	    ((Process)processes.get(id)).destroy();
	    cleanProcess(id);
	} else {
	    cleanProcess(id);
	    throw new ProcessException("Process with id: "+"id"+" doesn't exist");
	} 
    }

    /**
     * Kill all processes and remove all process id and configuration
     */
    public synchronized void killAllProcesses() throws  RemoteException {
	if (verbose) {
	    System.out.println("Kill all Process");
	}
	for (Enumeration e = processes.keys() ; e.hasMoreElements() ;) {
	    String s = (String)e.nextElement();
	    ((Process)processes.get(s)).destroy();
	    cleanProcess(s);
	}
	commands.clear();
	directories.clear();
	processes.clear();
    }

    /**
     * Test if a Process is always alive
     * @param id the Process String id 
     * @return true if the Process is always alive and false if this Process doens't 
     * existe anymore or if the process of this Process is stopped
     */
    public synchronized boolean pingProcess(String id) throws ProcessException, RemoteException {
	if (verbose) {
	    System.out.println("ping Process");
	}
	if (processes.containsKey(id)) {
	    try {
		((Process)processes.get(id)).exitValue();
		return false;
	    } catch (IllegalThreadStateException ite) {
		return true;
	    }
	} else {
	    return false;
	}
    }


    /**
     * Test if a Process is not alive the exit value
     * @param id the jvm id
     * @return int the Process is always alive
     * @throws ProcessException if
     * - the id doen'st existe (with the CLEAN_Process_PROCESSES=true for example)
     * - teh jvm with this id is not yet terminated
     */
    public int getProcessExitValue(String id) throws ProcessException, RemoteException  {
	if (verbose) {
	    System.out.println("search exit value of Process with id: " + id);
	}
	if (processes.containsKey(id)) {
	    try {
		int ev_value = ((Process)processes.get(id)).exitValue();
		return ev_value;
	    } catch (IllegalThreadStateException ite) {
		// the Process isn'nt stopped for the moment
		throw new ProcessException("Process with id: "+id+" is not yet stopped");
	    }
	} else {
	    throw new ProcessException("Process with id: "+id + "doens'nt exist");
	}
    }

    /**
     * Get the Process command line
     * @param String id this id
     * @return String the process command line
     * @throws ProcessException if:
     * - The Process id doesn't exist
     * - The Process process is stop
     *
     */
    public String getProcessCommand(String id) throws ProcessException, RemoteException  {
	if (verbose) {
	    System.out.println("get Process id " +id +" commande line");
	}
	if (processes.containsKey(id)) {
	    try {
		int ev_value = ((Process)processes.get(id)).exitValue();
		throw new ProcessException("Process with id: "+id+" is stop with exit value: " + ev_value);
	    } catch (IllegalThreadStateException ite) {
		// the Tread is not yet terminated, OK continue 
		return (String)commands.get(id);
	    }
	} else {
	    throw new ProcessException ("Process with id: "+id+ "doens'nt exist");
	}
	
    }

    /**
     * Get the Process directory
     * @param String id this id
     * @return String the process directory
     * @throws ProcessException if:
     * - The Process id doesn't exist
     * - The Process process is stop
     *
     */
    public String getProcessDirectory(String id) throws ProcessException, RemoteException  {
	if (verbose) {
	    System.out.println("get Process id " +id +" directory");
	}
	if (processes.containsKey(id)) {
	    try {
		int ev_value = ((Process)processes.get(id)).exitValue();
		throw new ProcessException("Process with id: "+id+" is stop with exit value: " + ev_value);
	    } catch (IllegalThreadStateException ite) {
		// the Tread is not yet terminated, OK continue 
		return (String)directories.get(id);
	    }
	} else {
	    throw new ProcessException ("Process with id: "+id+ "doens'nt exist");
	}
	
    }

    /**
     * Get the all Process id with there command line
     * @return Hashtable the process id and his command line
     */
    public Hashtable getAllProcess() throws  RemoteException {
	if (verbose) {
	    System.out.println("get all Process");
	}
	return commands;
    }

   /**
     * get the rproc OutputStream
     * @param id the proc id
     * @throws ProcessException if
     * - the id doen'st existe
     */
    public String readProcessOutput(String id) throws ProcessException, RemoteException  {
	try {
	    Process p = (Process)processes.get(id);
	    if (p!=null) {
		// get the Err and Out stream of the process
		InputStream pOutputStream = p.getInputStream();
		byte [] b;
		b = new byte[pOutputStream.available()];
		pOutputStream.read(b);
		return new String(b);
	    } else {
		throw new ProcessException ("Process with id: "+id+ "doens'nt exist");
	    }
	} catch (Exception e) {
	    throw new ProcessException (e);
	}
    }

   /**
     * get the rjvm ErrorStream
     * @param id the jvm id
     * @throws ProcessException if
     * - the id doen'st existe
     */
    public String readProcessError(String id) throws ProcessException, RemoteException  {
	try {
	    Process p = (Process)processes.get(id);
	    if (p!=null) {
		// get the Err and Out stream of the process
		InputStream pErrorStream = p.getErrorStream();
		byte [] b;
		b = new byte[pErrorStream.available()];
		pErrorStream.read(b);
		return new String(b);
	    } else {
		throw new ProcessException ("Process with id: "+id+ "doens'nt exist");
	    }
	} catch (Exception e) {
	    throw new ProcessException (e);
	}
    }

    /**
     * send a String to the rjvm inputStream
     * @param s String to send to the InputStream
     * @param id the jvm id
     * @throws ProcessException if
     * - the id doen'st existe
     */
    public void writeProcessInput(String id, String s) throws  ProcessException, RemoteException  {
	try {
	    Process p = (Process)processes.get(id);
	    if (p!=null) {
		// get the In stream of the process
		OutputStream pInStream = p.getOutputStream();
		pInStream.write(s.getBytes());		
		pInStream.flush();
	    } else {
		throw new ProcessException ("Process with id: "+id+ "doens'nt exist");
	    }
	} catch (Exception e) {
	    throw new ProcessException (e);
	}	
    }
        
    /**
     * Send a file to a directory
     * (FileImputStream/FileOutputStream format)
     * this method build a directory in the current directory
     * if the directory
     * does not exite. Your are not allow to 
     * write some thing outside of the current 
     * directory 
     *
     * @param byte [] array of this file 
     * @param String directory name in the current directory 
     * @param String file name in the current directory 
     */
    public void sendFile(String dirName, String fileName, byte [] b) throws  RemoteException  {
	try {
	    createDir(dirName);
	    File dirC = createDir(dirName);
	    if (dirC != null) {
		FileOutputStream fou =  new FileOutputStream(new File(dirC + System.getProperty("file.separator") + fileName));
		fou.write(b);
		fou.flush();
		fou.close();
	    }
	} catch (Exception e) {
	    throw new RemoteException(""+e);
	}
    }

    /**
     * Stop the damemon and kill all the process
     */
    public void stop() throws RemoteException {
	killAllProcesses();
	System.exit(0);
    }

    /**
     * Process Shudown process Thread
     * For cleanong the Process's Hashtable
     */
    public class ProcessStopThread extends Thread {

	/**
	 * The associated process
	 */
	Process process;
	
	/**
	 * The Process id 
	 */
	String processID;

	/**
	 * constructor
	 * @param p Process process
	 * @param id Process id
	 */
	ProcessStopThread(Process p, String id) {
	    this.process=p;
	    this.processID=id;
	}
	
	/**
	 * Thread run method
	 */
	public void run() {
	    try {
		process.waitFor();
		if (verbose) {
		    System.out.println("Stopping process " + processID);
		    System.out.println("Error:");
		    System.out.println(getProcessError(process));
		    System.out.println("Output:");
		    System.out.println(getProcessOutput(process));
		}
		synchronized (this) {
		    cleanProcess(processID);
		}
	    } catch (Exception ie) {
		ie.printStackTrace();
	    }
	}
    }
   
}    

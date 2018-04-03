namespace = global;

/*
 * BeanShell.java - BeanShell scripting support
 * Copyright (C) 2000, 2001 Slava Pestov
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
 */

package org.gjt.sp.jedit;

import bsh.*;
import javax.swing.text.BadLocationException;
import javax.swing.text.Segment;
import javax.swing.JFileChooser;
import java.lang.reflect.InvocationTargetException;
import java.io.*;
import org.gjt.sp.jedit.io.*;
import org.gjt.sp.jedit.gui.BeanShellErrorDialog;
import org.gjt.sp.jedit.textarea.*;
import org.gjt.sp.util.Log;

public class BeanShell
{
	/**
	 * Evaluates the text selected in the specified text area.
	 * @since jEdit 2.7pre2
	 */
	public static void evalSelection(View view, JEditTextArea textArea)
	{
		String command = textArea.getSelectedText();
		if(command == null)
		{
			view.getToolkit().beep();
			return;
		}
		Object returnValue = eval(view,command,false);
		if(returnValue != null)
			textArea.setSelectedText(returnValue.toString());
	}

	/**
	 * Prompts for a BeanShell expression to evaluate.
	 * @since jEdit 2.7pre2
	 */
	public static void showEvaluateDialog(View view)
	{
		String command = GUIUtilities.input(view,"beanshell-eval-input",null);
		if(command != null)
		{
			if(!command.endsWith(";"))
				command = command + ";";

			int repeat = view.getInputHandler().getRepeatCount();

			if(view.getMacroRecorder() != null)
			{
				view.getMacroRecorder().record(repeat,command);
			}

			Object returnValue = null;
			try
			{
				for(int i = 0; i < repeat; i++)
				{
					returnValue = eval(view,command,true);
				}
			}
			catch(Throwable t)
			{
				// BeanShell error occured, abort execution
			}

			if(returnValue != null)
			{
				String[] args = { returnValue.toString() };
				GUIUtilities.message(view,"beanshell-eval",args);
			}
		}
	}

	/**
	 * Evaluates the specified script for each selected line.
	 * @since jEdit 4.0pre1
	 */
	public static void showEvaluateLinesDialog(View view)
	{
		String command = GUIUtilities.input(view,"beanshell-eval-line",null);
		if(command != null)
		{
			if(!command.endsWith(";"))
				command = command + ";";

			if(view.getMacroRecorder() != null)
				view.getMacroRecorder().record(1,command);

			JEditTextArea textArea = view.getTextArea();
			Buffer buffer = view.getBuffer();

			try
			{
				buffer.beginCompoundEdit();

				Selection[] selection = textArea.getSelection();
				for(int i = 0; i < selection.length; i++)
				{
					Selection s = selection[i];
					for(int j = s.getStartLine(); j <= s.getEndLine(); j++)
					{
						global.setVariable("line",new Integer(j));
						global.setVariable("index",new Integer(
							j - s.getStartLine()));
						int start = s.getStart(buffer,j);
						int end = s.getEnd(buffer,j);
						String text = buffer.getText(start,
							end - start);
						global.setVariable("text",text);

						Object returnValue = eval(view,command,true);
						if(returnValue != null)
						{
							buffer.remove(start,end - start);
							buffer.insertString(start,
								returnValue.toString(),
								null);
						}
					}
				}
			}
			catch(BadLocationException bl)
			{
				Log.log(Log.ERROR,BeanShell.class,bl);
			}
			catch(Throwable e)
			{
				// BeanShell error occured, abort execution
			}
			finally
			{
				buffer.endCompoundEdit();
			}

			textArea.selectNone();
		}
	}

	/**
	 * Prompts for a BeanShell script to run.
	 * @since jEdit 2.7pre2
	 */
	public static void showRunScriptDialog(View view)
	{
		String[] paths = GUIUtilities.showVFSFileDialog(view,
			null,JFileChooser.OPEN_DIALOG,true);
		if(paths != null)
		{
			Buffer buffer = view.getBuffer();
			try
			{
				buffer.beginCompoundEdit();

				for(int i = 0; i < paths.length; i++)
					runScript(view,paths[i],true,false);
			}
			finally
			{
				buffer.endCompoundEdit();
			}
		}
	}

	/**
	 * Runs a BeanShell script.
	 * @param view The view
	 * @param path The path name of the script. May be a jEdit VFS path
	 * @param ownNamespace Macros are run in their own namespace, startup
	 * scripts are run on the global namespace
	 * @param rethrowBshErrors Rethrow BeanShell errors, in addition to
	 * showing an error dialog box
	 * @since jEdit 2.7pre3
	 */
	public static void runScript(View view, String path,
		boolean ownNamespace, boolean rethrowBshErrors)
	{
		Reader in;
		Buffer buffer = jEdit.getBuffer(path);

		VFS vfs = VFSManager.getVFSForPath(path);
		Object session = vfs.createVFSSession(path,view);
		if(session == null)
		{
			// user cancelled???
			return;
		}

		try
		{
			if(buffer != null && buffer.isLoaded())
			{
				StringBuffer buf = new StringBuffer();
				try
				{
					buf.append(buffer.getText(0,buffer.getLength()));
				}
				catch(BadLocationException e)
				{
					// XXX
					throw new InternalError();
				}

				// Ugly workaround for a BeanShell bug
				buf.append("\n");

				in = new StringReader(buf.toString());
			}
			else
			{
				in = new BufferedReader(new InputStreamReader(
					vfs._createInputStream(session,path,
					true,view)));
			}

			runScript(view,path,in,ownNamespace,rethrowBshErrors);
		}
		catch(IOException e)
		{
			Log.log(Log.ERROR,BeanShell.class,e);
			GUIUtilities.error(view,"read-error",
				new String[] { path, e.toString() });
			return;
		}
		finally
		{
			try
			{
				vfs._endVFSSession(session,view);
			}
			catch(IOException io)
			{
				Log.log(Log.ERROR,BeanShell.class,io);
				GUIUtilities.error(view,"read-error",
					new String[] { path, io.toString() });
			}
		}
	}

	/**
	 * Runs a BeanShell script.
	 * @param view The view
	 * @param path For error reporting only
	 * @param in The reader to read the script from
	 * @param ownNamespace Macros are run in their own namespace, startup
	 * scripts are run on the global namespace
	 * @param rethrowBshErrors Rethrow BeanShell errors, in addition to
	 * showing an error dialog box
	 * @since jEdit 3.2pre4
	 */
	public static void runScript(View view, String path, Reader in,
		boolean ownNamespace, boolean rethrowBshErrors)
	{
		Log.log(Log.MESSAGE,BeanShell.class,"Running script " + path);

		NameSpace namespace;
		if(ownNamespace)
			namespace = new NameSpace(global,"script namespace");
		else
			namespace = global;

		Interpreter interp = createInterpreter(namespace);

		try
		{
			if(view != null)
			{
				EditPane editPane = view.getEditPane();
				interp.set("view",view);
				interp.set("editPane",editPane);
				interp.set("buffer",editPane.getBuffer());
				interp.set("textArea",editPane.getTextArea());
			}

			running = true;

			interp.eval(in,namespace,path);
		}
		catch(Throwable e)
		{
			if(e instanceof TargetError)
				e = ((TargetError)e).getTarget();

			if(e instanceof InvocationTargetException)
				e = ((InvocationTargetException)e).getTargetException();

			Log.log(Log.ERROR,BeanShell.class,e);

			new BeanShellErrorDialog(view,e.toString());

			if(e instanceof Error && rethrowBshErrors)
				throw (Error)e;
		}
		finally
		{
			running = false;
		}
	}

	/**
	 * Evaluates the specified BeanShell expression.
	 * @param view The view (may be null)
	 * @param command The expression
	 * @param rethrowBshErrors If true, BeanShell errors will
	 * be re-thrown to the caller
	 * @since jEdit 2.7pre3
	 */
	public static Object eval(View view, String command,
		boolean rethrowBshErrors)
	{
		return eval(view,global,command,rethrowBshErrors);
	}

	/**
	 * Evaluates the specified BeanShell expression.
	 * @param view The view (may be null)
	 * @param namespace The namespace
	 * @param command The expression
	 * @param rethrowBshErrors If true, BeanShell errors will
	 * be re-thrown to the caller
	 * @since jEdit 3.2pre7
	 */
	public static Object eval(View view, NameSpace namespace,
		String command, boolean rethrowBshErrors)
	{
		Interpreter interp = createInterpreter(namespace);

		try
		{
			if(view != null)
			{
				EditPane editPane = view.getEditPane();
				interp.set("view",view);
				interp.set("editPane",editPane);
				interp.set("buffer",editPane.getBuffer());
				interp.set("textArea",editPane.getTextArea());
			}

			return interp.eval(command);
		}
		catch(Throwable e)
		{
			if(e instanceof TargetError)
				e = ((TargetError)e).getTarget();

			if(e instanceof InvocationTargetException)
				e = ((InvocationTargetException)e).getTargetException();

			Log.log(Log.ERROR,BeanShell.class,e);

			new BeanShellErrorDialog(view,e.toString());

			if(e instanceof Error && rethrowBshErrors)
				throw (Error)e;
		}

		return null;
	}

	/**
	 * Caches a block of code, returning a handle that can be passed to
	 * runCachedBlock().
	 * @param id An identifier. If null, a unique identifier is generated
	 * @param code The code
	 * @param childNamespace If the method body should be run in a new
	 * namespace (slightly faster). Note that you must pass a null namespace
	 * to the runCachedBlock() method if you do this
	 * @since jEdit 3.2pre5
	 */
	public static String cacheBlock(String id, String code, boolean childNamespace)
	{
		String name;
		if(id == null)
			name = "b_" + (cachedBlockCounter++);
		else
			name = "b_" + id;

		code = "setNameSpace(__cruft.namespace);\n"
			+ name
			+ "(ns) {\n"
			+ "setNameSpace(ns);"
			+ code
			+ "\n}";

		eval(null,code,false);

		return name;
	}

	/**
	 * Runs a cached block of code in the specified namespace. Faster than
	 * evaluating the block each time.
	 * @param id The identifier returned by cacheBlock()
	 * @param view The view
	 * @param namespace The namespace to run the code in. Can only be null if
	 * childNamespace parameter was true in cacheBlock() call
	 * @since jEdit 3.2pre5
	 */
	public static Object runCachedBlock(String id, View view, NameSpace namespace)
	{
		if(namespace == null)
			namespace = internal;

		Object[] args = { namespace };

		try
		{
			if(view != null)
			{
				namespace.setVariable("view",view);
				EditPane editPane = view.getEditPane();
				namespace.setVariable("editPane",editPane);
				namespace.setVariable("buffer",editPane.getBuffer());
				namespace.setVariable("textArea",editPane.getTextArea());
			}

			Object retVal = internal.invokeMethod(id,args,interpForMethods);
			if(retVal instanceof Primitive)
			{
				if(retVal == Primitive.VOID)
					return null;
				else
					return ((Primitive)retVal).getValue();
			}
			else
				return retVal;
		}
		catch(Throwable e)
		{
			if(e instanceof TargetError)
				e = ((TargetError)e).getTarget();

			if(e instanceof InvocationTargetException)
				e = ((InvocationTargetException)e).getTargetException();

			Log.log(Log.ERROR,BeanShell.class,e);

			new BeanShellErrorDialog(view,e.toString());
		}
		finally
		{
			try
			{
				namespace.setVariable("view",null);
				namespace.setVariable("editPane",null);
				namespace.setVariable("buffer",null);
				namespace.setVariable("textArea",null);
			}
			catch(EvalError e)
			{
				// can't do much
			}
		}

		return null;
	}

	/**
	 * Returns if a BeanShell script or macro is currently running.
	 * @since jEdit 2.7pre2
	 */
	public static boolean isScriptRunning()
	{
		return running;
	}

	/**
	 * Returns the global namespace.
	 * @since jEdit 3.2pre5
	 */
	public static NameSpace getNameSpace()
	{
		return global;
	}

	static void init()
	{
		Log.log(Log.DEBUG,BeanShell.class,"Initializing BeanShell"
			+ " interpreter");

		BshClassManager.setClassLoader(new JARClassLoader());

		global = new NameSpace("jEdit embedded BeanShell Interpreter");
		interpForMethods = createInterpreter(global);

		try
		{
			Interpreter interp = createInterpreter(global);

			BufferedReader in = new BufferedReader(new InputStreamReader(
				BeanShell.class.getResourceAsStream("jedit.bsh")));

			interp.eval(in,global,"jedit.bsh");
		}
		catch(Throwable t)
		{
			Log.log(Log.ERROR,BeanShell.class,t);
			System.exit(1);
		}

		// jedit object in global namespace is set up by jedit.bsh
		internal = (NameSpace)eval(null,"__cruft.namespace;",false);
	}

	// private members
	private static Interpreter interpForMethods;
	private static NameSpace global;
	private static NameSpace internal;
	private static boolean running;
	private static int cachedBlockCounter;

	// until Pat updates Interpreter.java
	private static Interpreter createInterpreter(NameSpace nameSpace)
	{
		return new Interpreter(null,System.out,System.err,
			false,nameSpace);
	}
}
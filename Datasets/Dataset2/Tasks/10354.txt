_eval(null,global,name + "(ns) {\nthis.callstack.set(0,ns);\n" + code + "\n}");

/*
 * BeanShell.java - BeanShell scripting support
 * :tabSize=8:indentSize=8:noTabs=false:
 * :folding=explicit:collapseFolds=1:
 *
 * Copyright (C) 2000, 2001, 2002 Slava Pestov
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

//{{{ Imports
import bsh.*;
import javax.swing.text.Segment;
import javax.swing.JFileChooser;
import java.lang.reflect.InvocationTargetException;
import java.io.*;
import org.gjt.sp.jedit.io.*;
import org.gjt.sp.jedit.gui.BeanShellErrorDialog;
import org.gjt.sp.jedit.textarea.*;
import org.gjt.sp.util.Log;
//}}}

public class BeanShell
{
	//{{{ evalSelection() method
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
		Object returnValue = eval(view,global,command);
		if(returnValue != null)
			textArea.setSelectedText(returnValue.toString());
	} //}}}

	//{{{ showEvaluateDialog() method
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
					returnValue = _eval(view,global,command);
				}
			}
			catch(Throwable e)
			{
				Log.log(Log.ERROR,BeanShell.class,e);

				handleException(view,null,e);
			}

			if(returnValue != null)
			{
				String[] args = { returnValue.toString() };
				GUIUtilities.message(view,"beanshell-eval",args);
			}
		}
	} //}}}

	//{{{ showEvaluateLinesDialog() method
	/**
	 * Evaluates the specified script for each selected line.
	 * @since jEdit 4.0pre1
	 */
	public static void showEvaluateLinesDialog(View view)
	{
		String command = GUIUtilities.input(view,"beanshell-eval-line",null);

		JEditTextArea textArea = view.getTextArea();
		Buffer buffer = view.getBuffer();

		Selection[] selection = textArea.getSelection();
		if(selection.length == 0 || command == null || command.length() == 0)
		{
			view.getToolkit().beep();
			return;
		}

		if(!command.endsWith(";"))
			command = command + ";";

		if(view.getMacroRecorder() != null)
			view.getMacroRecorder().record(1,command);

		try
		{
			buffer.beginCompoundEdit();

			for(int i = 0; i < selection.length; i++)
			{
				Selection s = selection[i];
				for(int j = s.getStartLine(); j <= s.getEndLine(); j++)
				{
					// if selection ends on the start of a
					// line, don't filter that line
					if(s.getEnd() == textArea.getLineStartOffset(j))
						break;

					global.setVariable("line",new Integer(j));
					global.setVariable("index",new Integer(
						j - s.getStartLine()));
					int start = s.getStart(buffer,j);
					int end = s.getEnd(buffer,j);
					String text = buffer.getText(start,
						end - start);
					global.setVariable("text",text);

					Object returnValue = _eval(view,global,command);
					if(returnValue != null)
					{
						buffer.remove(start,end - start);
						buffer.insert(start,
							returnValue.toString());
					}
				}
			}
		}
		catch(Throwable e)
		{
			Log.log(Log.ERROR,BeanShell.class,e);

			handleException(view,null,e);
		}
		finally
		{
			buffer.endCompoundEdit();
		}

		textArea.selectNone();
	} //}}}

	//{{{ runScript() method
	/**
	 * Runs a BeanShell script. Errors are shown in a dialog box.
	 * @param view The view
	 * @param path For error reporting only
	 * @param in The reader to read the script from. If null, script will
	 * be read from the VFS corresponding to its path.
	 * @param ownNamespace Macros are run in their own namespace, startup
	 * scripts are run on the global namespace
	 * @since jEdit 4.0pre7
	 */
	public static void runScript(View view, String path, Reader in,
		boolean ownNamespace)
	{
		try
		{
			_runScript(view,path,in,ownNamespace);
		}
		catch(Throwable e)
		{
			Log.log(Log.ERROR,BeanShell.class,e);

			handleException(view,path,e);
		}
	} //}}}

	//{{{ _runScript() method
	/**
	 * Runs a BeanShell script. Errors are passed to the caller.
	 * @param view The view
	 * @param path For error reporting only
	 * @param in The reader to read the script from. If null, script will
	 * be read from the VFS corresponding to its path.
	 * @param ownNamespace Macros are run in their own namespace, startup
	 * scripts are run on the global namespace
	 * @exception Exception instances are thrown when various BeanShell errors
	 * occur
	 * @since jEdit 4.0pre7
	 */
	public static void _runScript(View view, String path, Reader in,
		boolean ownNamespace) throws Exception
	{
		Log.log(Log.MESSAGE,BeanShell.class,"Running script " + path);

		NameSpace namespace;
		if(ownNamespace)
			namespace = new NameSpace(global,"script namespace");
		else
			namespace = global;

		Interpreter interp = createInterpreter(namespace);

		VFS vfs = null;
		Object session = null;

		try
		{
			if(in == null)
			{
				Buffer buffer = jEdit.getBuffer(path);

				vfs = VFSManager.getVFSForPath(path);
				session = vfs.createVFSSession(path,view);
				if(session == null)
				{
					// user cancelled???
					return;
				}

				if(buffer != null)
				{
					if(!buffer.isLoaded())
						VFSManager.waitForRequests();

					in = new StringReader(buffer.getText(0,
						buffer.getLength()));
				}
				else
				{
					in = new BufferedReader(new InputStreamReader(
						vfs._createInputStream(session,
						path,false,view)));
				}
			}

			if(view != null)
			{
				interp.set("view",view);
				EditPane editPane = view.getEditPane();
				interp.set("editPane",editPane);
				interp.set("buffer",editPane.getBuffer());
				interp.set("textArea",editPane.getTextArea());
			}

			interp.set("scriptPath",path);

			running = true;

			interp.eval(in,namespace,path);
		}
		catch(Exception e)
		{
			unwrapException(e);
		}
		finally
		{
			running = false;

			if(session != null)
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

			try
			{
				if(view != null)
				{
					interp.unset("view");
					interp.unset("editPane");
					interp.unset("buffer");
					interp.unset("textArea");
				}

				interp.unset("scriptPath");
			}
			catch(EvalError e)
			{
				// do nothing
			}
		}
	} //}}}

	//{{{ eval() method
	/**
	 * Evaluates the specified BeanShell expression. Errors are reported in
	 * a dialog box.
	 * @param view The view (may be null)
	 * @param namespace The namespace
	 * @param command The expression
	 * @since jEdit 4.0pre8
	 */
	public static Object eval(View view, NameSpace namespace, String command)
	{
		try
		{
			return _eval(view,namespace,command);
		}
		catch(Throwable e)
		{
			Log.log(Log.ERROR,BeanShell.class,e);

			handleException(view,null,e);
		}

		return null;
	} //}}}

	//{{{ _eval() method
	/**
	 * Evaluates the specified BeanShell expression. Unlike
	 * <code>eval()</code>, this method passes any exceptions to the caller.
	 *
	 * @param view The view (may be null)
	 * @param namespace The namespace
	 * @param command The expression
	 * @exception Exception instances are thrown when various BeanShell
	 * errors occur
	 * @since jEdit 3.2pre7
	 */
	public static Object _eval(View view, NameSpace namespace, String command)
		throws Exception
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
		catch(Exception e)
		{
			unwrapException(e);
			// never called
			return null;
		}
		finally
		{
			try
			{
				if(view != null)
				{
					interp.unset("view");
					interp.unset("editPane");
					interp.unset("buffer");
					interp.unset("textArea");
				}
			}
			catch(EvalError e)
			{
				// do nothing
			}
		}
	} //}}}

	//{{{ cacheBlock() method
	/**
	 * Caches a block of code, returning a handle that can be passed to
	 * runCachedBlock().
	 * @param id An identifier. If null, a unique identifier is generated
	 * @param code The code
	 * @param namespace If true, the namespace will be set
	 * @exception Exception instances are thrown when various BeanShell errors
	 * occur
	 * @since jEdit 4.1pre1
	 */
	public static BshMethod cacheBlock(String id, String code, boolean namespace)
		throws Exception
	{
		String name = "__internal_" + id;

		// evaluate a method declaration
		if(namespace)
		{
			_eval(null,global,name + "(ns) {\this.callstack.set(0,ns);\n" + code + "\n}");
			return global.getMethod(name,new Class[] { NameSpace.class });
		}
		else
		{
			_eval(null,global,name + "() {\n" + code + "\n}");
			return global.getMethod(name,new Class[0]);
		}
	} //}}}

	//{{{ runCachedBlock() method
	/**
	 * Runs a cached block of code in the specified namespace. Faster than
	 * evaluating the block each time.
	 * @param method The method instance returned by cacheBlock()
	 * @param view The view
	 * @param namespace The namespace to run the code in
	 * @exception Exception instances are thrown when various BeanShell
	 * errors occur
	 * @since jEdit 4.1pre1
	 */
	public static Object runCachedBlock(BshMethod method, View view,
		NameSpace namespace) throws Exception
	{
		boolean useNamespace;
		if(namespace == null)
		{
			useNamespace = false;
			namespace = global;
		}
		else
			useNamespace = true;

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

			Object retVal = method.invoke(useNamespace
				? new Object[] { namespace }
				: NO_ARGS,
				interpForMethods,new CallStack());
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
		catch(Exception e)
		{
			unwrapException(e);
			// never called
			return null;
		}
		finally
		{
			if(view != null)
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
		}
	} //}}}

	//{{{ isScriptRunning() method
	/**
	 * Returns if a BeanShell script or macro is currently running.
	 * @since jEdit 2.7pre2
	 */
	public static boolean isScriptRunning()
	{
		return running;
	} //}}}

	//{{{ getNameSpace() method
	/**
	 * Returns the global namespace.
	 * @since jEdit 3.2pre5
	 */
	public static NameSpace getNameSpace()
	{
		return global;
	} //}}}

	//{{{ Deprecated functions

	//{{{ runScript() method
	/**
	 * @deprecated The <code>rethrowBshErrors</code> parameter is now
	 * obsolete; call <code>_runScript()</code> or <code>runScript()</code>
	 * instead.
	 */
	public static void runScript(View view, String path,
		boolean ownNamespace, boolean rethrowBshErrors)
	{
		runScript(view,path,null,ownNamespace);
	} //}}}

	//{{{ runScript() method
	/**
	 * @deprecated The <code>rethrowBshErrors</code> parameter is now
	 * obsolete; call <code>_runScript()</code> or <code>runScript()</code>
	 * instead.
	 */
	public static void runScript(View view, String path, Reader in,
		boolean ownNamespace, boolean rethrowBshErrors)
	{
		runScript(view,path,in,ownNamespace);
	} //}}}

	//{{{ eval() method
	/**
	 * @deprecated The <code>rethrowBshErrors</code> parameter is now
	 * obsolete; call <code>_eval()</code> or <code>eval()</code> instead.
	 */
	public static Object eval(View view, String command,
		boolean rethrowBshErrors)
	{
		return eval(view,global,command);
	} //}}}

	//{{{ eval() method
	/**
	 * @deprecated The <code>rethrowBshErrors</code> parameter is now
	 * obsolete; call <code>_eval()</code> or <code>eval()</code> instead.
	 */
	public static Object eval(View view, NameSpace namespace,
		String command, boolean rethrowBshErrors)
	{
		return eval(view,namespace,command);
	} //}}}

	//}}}

	//{{{ Package-private members

	//{{{ init() method
	static void init()
	{
		BshClassManager.setClassLoader(new JARClassLoader());

		global = new NameSpace("jEdit embedded BeanShell interpreter");
		global.importPackage("org.gjt.sp.jedit");
		global.importPackage("org.gjt.sp.jedit.browser");
		global.importPackage("org.gjt.sp.jedit.gui");
		global.importPackage("org.gjt.sp.jedit.io");
		global.importPackage("org.gjt.sp.jedit.msg");
		global.importPackage("org.gjt.sp.jedit.options");
		global.importPackage("org.gjt.sp.jedit.pluginmgr");
		global.importPackage("org.gjt.sp.jedit.print");
		global.importPackage("org.gjt.sp.jedit.search");
		global.importPackage("org.gjt.sp.jedit.syntax");
		global.importPackage("org.gjt.sp.jedit.textarea");
		global.importPackage("org.gjt.sp.util");

		interpForMethods = createInterpreter(global);

		Log.log(Log.DEBUG,BeanShell.class,"BeanShell interpreter version "
			+ Interpreter.VERSION);
	} //}}}

	//}}}

	//{{{ Private members

	//{{{ Static variables
	private static final Object[] NO_ARGS = new Object[0];
	private static Interpreter interpForMethods;
	private static NameSpace global;
	private static boolean running;
	//}}}

	//{{{ unwrapException() method
	/**
	 * This extracts an exception from a 'wrapping' exception, as BeanShell
	 * sometimes throws. This gives the user a more accurate error traceback
	 */
	private static void unwrapException(Exception e) throws Exception
	{
		if(e instanceof TargetError)
		{
			Throwable t = ((TargetError)e).getTarget();
			if(t instanceof Exception)
				throw (Exception)t;
			else if(t instanceof Error)
				throw (Error)t;
		}

		if(e instanceof InvocationTargetException)
		{
			Throwable t = ((InvocationTargetException)e).getTargetException();
			if(t instanceof Exception)
				throw (Exception)t;
			else if(t instanceof Error)
				throw (Error)t;
		}

		throw e;
	} //}}}

	//{{{ handleException() method
	private static void handleException(View view, String path, Throwable t)
	{
		if(t instanceof IOException)
		{
			VFSManager.error(view,path,"ioerror.read-error",
				new String[] { t.toString() });
		}
		else
			new BeanShellErrorDialog(view,t.toString());
	} //}}}

	//{{{ createInterpreter() method
	private static Interpreter createInterpreter(NameSpace nameSpace)
	{
		return new Interpreter(null,System.out,System.err,false,nameSpace);
	} //}}}

	//}}}
}
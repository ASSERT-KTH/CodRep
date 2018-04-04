inputStream.close();

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.PrintWriter;

/*
 * Created on 15.07.2003
 *
 * To change the template for this generated file go to
 * Window>Preferences>Java>Code Generation>Code and Comments
 */

/**
 * @author frd
 *
 * To change the template for this generated type comment go to
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
public class IPCHelper {

	protected StreamThread outputStream = null;
	protected StreamThread errorStream = null;
	protected PrintWriter inputStream = null;
	protected Process p;

	public IPCHelper() {
	}

	/**
	 * 
	 * execute command
	 * 
	 * initialize streams
	 * 
	 * @param command
	 * @throws Exception
	 */
	public void executeCommand(String command) throws Exception {
		p = Runtime.getRuntime().exec(command);

		errorStream = new StreamThread(p.getErrorStream());
		outputStream = new StreamThread(p.getInputStream());
		inputStream = new PrintWriter(p.getOutputStream());

		errorStream.start();
		outputStream.start();
	}

	/**
	 * 
	 * send input to process
	 * 
	 */
	public void send(String str) throws Exception {

		inputStream.println(str);
		inputStream.flush();
		//out.close();

	}

	public int waitFor() throws Exception {
		int exitVal = p.waitFor();

		return exitVal;
	}

	/**
	 * 
	 * return error 
	 * 
	 * @return
	 * @throws Exception
	 */
	public String getErrorString() throws Exception {
		String str = errorStream.getBuffer();
		return str;
	}

	/**
	 * 
	 * return output
	 * 
	 * @return
	 * @throws Exception
	 */
	public String getOutputString() throws Exception {
		String str = outputStream.getBuffer();
		return str;
	}

	/*
	 * wait for stream threads to die
	 * 
	 */
	public void waitForThreads() throws Exception {
		outputStream.join();
		errorStream.join();
	}

	public class StreamThread extends Thread {
		InputStream is;

		StringBuffer buf;

		public StreamThread(InputStream is) {
			this.is = is;

			buf = new StringBuffer();
		}

		public void run() {

			try {
				InputStreamReader isr = new InputStreamReader(is);
				BufferedReader br = new BufferedReader(isr);
				String line = null;
				while ((line = br.readLine()) != null) {
					System.out.println(">" + line);
					buf.append(line + "\n");
				}

			} catch (IOException ioe) {
				ioe.printStackTrace();
			}
		}

		public String getBuffer() {
			return buf.toString();
		}

	}
}
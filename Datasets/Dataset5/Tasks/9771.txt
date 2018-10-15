private List<String> loadContent() throws IOException {

/*******************************************************************************
 * Copyright (c) 2005, 2007 committers of openArchitectureWare and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     committers of openArchitectureWare - initial API and implementation
 *******************************************************************************/
package org.eclipse.xtend.util.stdlib.texttest;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;

import org.eclipse.emf.mwe.core.resources.ResourceLoaderFactory;

public class Handle {

	private String filename;
	private List<String> lines;
	private String contentsAsString;

	public Handle(String filename ) {
		this.filename = filename;
	}
	
	@Override
	public String toString() {
		return filename;
	}

	public void sameContentAs(Handle compareFile) {
		List<String> lines1 = getContents();
		List<String> lines2 = compareFile.getContents();
		int count = lines1.size() < lines2.size() ? lines1.size() : lines2.size();
		for (int i = 0; i < count; i++) {
			String s1 = lines1.get(i);
			String s2 = lines2.get(i);
			if ( !s1.equals(s2)) throw new Failed(filename+" does not have the same contents as "+compareFile.filename+". First difference in line "+i+": should be: '"+s2+"', but is '"+s1+"'");
		}
	}

	public List<String> getContents() {
		if ( lines == null )
			try {
				lines = loadContent();
			} catch (IOException e) {
				throw new RuntimeException(e);  
			}
		return lines;
	}

	private List loadContent() throws IOException {
		List<String> l = new ArrayList<String>();
		BufferedReader br = new BufferedReader( new InputStreamReader( getFileIS(filename) ) );
		while (br.ready()) l.add( br.readLine());
		br.close();
		return l;
	}

	public void contains(String substring) {
		if ( getContentsAsString().indexOf( substring ) < 0 ) throw new Failed(filename+" does not contain '"+substring+"'");
	}
	
	public int lineOf( String substring ) {
		for (int i = 0; i < getContents().size(); i++) {
			String line = getContents().get(i);
			if ( line.indexOf(substring) >= 0 ) return i;
		}
		throw new Failed("the substring '"+substring+"' can't be found in the content of "+filename);
	}

	private String getContentsAsString() {
		if ( contentsAsString == null ) {
			StringBuffer bf = new StringBuffer();
			for (String s : getContents()) {
				bf.append(s+"\n");
			}
			contentsAsString = bf.toString();
		}
		return contentsAsString;
	}

	public void removeBlankLines() {
		for (int i = getContents().size()-1; i>= 0; i--) {
			String line = getContents().get(i);
			if ( line.trim().equals("") ) getContents().remove(i);
		}
		contentsAsString = null;
	}

	public void containsInLine(int i, String string) {
		if ( getContents().get(i).indexOf(string) < 0 ) throw new Failed("'"+string+"' not found in line "+i+" of file "+filename);
	}
	
    private InputStream getFileIS(String fn) {
		final InputStream in = ResourceLoaderFactory.createResourceLoader().getResourceAsStream(fn);
        return in;
    }

	
	
	
}
private boolean _overwrite = false;

/*
Copyright (c) 2008 Arno Haase.
All rights reserved. This program and the accompanying materials
are made available under the terms of the Eclipse Public License v1.0
which accompanies this distribution, and is available at
http://www.eclipse.org/legal/epl-v10.html

Contributors:
    Arno Haase - initial API and implementation
 */
package org.eclipse.xtend.backend.syslib;

import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.io.Writer;
import java.util.ArrayList;
import java.util.List;

import org.eclipse.xtend.backend.util.ErrorHandler;
import org.eclipse.xtend.backend.util.NullWriter;


/**
 * 
 * @author Arno Haase (http://www.haase-consulting.com)
 */
public final class FileOutlet implements Outlet {
    private File _baseDir;
    private String _fileEncoding = System.getProperty ("file.encoding");
    private boolean _overwrite = false;;
    private boolean _append = false;

    private final List<InMemoryPostprocessor> _inMemoryPp = new ArrayList<InMemoryPostprocessor> ();
    private final List<UriBasedPostprocessor> _uriBasedPp = new ArrayList<UriBasedPostprocessor> ();
    
    public void register (InMemoryPostprocessor pp) {
        _inMemoryPp.add (pp);
    }
    
    public void register (UriBasedPostprocessor pp) {
        _uriBasedPp.add (pp);
    }
    
    public File getBaseDir () {
        return _baseDir;
    }

    public void setBaseDir (File baseDir) {
        _baseDir = baseDir;
    }

    public String getFileEncoding () {
        return _fileEncoding;
    }

    public void setFileEncoding (String fileEncoding) {
        _fileEncoding = fileEncoding;
    }

    public boolean isOverwrite () {
        return _overwrite;
    }

    public void setOverwrite (boolean overwrite) {
        _overwrite = overwrite;
    }

    public void setAppend (boolean append) {
        _append = append;
    }
    
    public boolean isAppend () {
        return _append;
    }
    
    public Writer createWriter (String filename) {
        return createWriter (filename, _append);
    }
        
    public Writer createWriter (String filename, boolean append) {
        try {
            final File target = createTargetFile (filename);
            if (target.exists() && !_overwrite)
                return new NullWriter ();
            
            final File f = new File (_baseDir, filename);
            final File parentDir = f.getParentFile();
            
            if (parentDir.isFile())
                throw new IllegalStateException ("'" + parentDir + "' exists but is no directory.");
            if (! parentDir.exists ())
                parentDir.mkdirs();
                
            final FileOutputStream fos = new FileOutputStream (f, append);
            final BufferedOutputStream bos = new BufferedOutputStream (fos);
            
            if (_fileEncoding == null)
                return new OutputStreamWriter (bos);
            else
                return new OutputStreamWriter (bos, _fileEncoding);
        } catch (IOException exc) {
            ErrorHandler.handle (exc);
            return null; // just for the compiler - this code is never executed
        }
    }

    private File createTargetFile (String filename) {
        return new File (_baseDir, filename);
    }
    
    public String createUri (String filename) {
        return createTargetFile (filename).getPath().replace ("\\", "/");
    }

    public List<InMemoryPostprocessor> getInMemoryPostprocessors () {
        return _inMemoryPp;
    }

    public List<UriBasedPostprocessor> getUriBasedPostprocessors () {
        return _uriBasedPp;
    }
}


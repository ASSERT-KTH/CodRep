return  _callableName + "@" + _lineNumber + " [" + _compilationUnit + "]";

/*
Copyright (c) 2008 Arno Haase.
All rights reserved. This program and the accompanying materials
are made available under the terms of the Eclipse Public License v1.0
which accompanies this distribution, and is available at
http://www.eclipse.org/legal/epl-v10.html

Contributors:
    Arno Haase - initial API and implementation
 */
package org.eclipse.xtend.backend.common;


/**
 * 
 * @author Arno Haase (http://www.haase-consulting.com)
 */
public class SourcePos {
    private final String _compilationUnit;
    private final String _callableName;
    private final int _lineNumber;
    
    public SourcePos (String compilationUnit, String callableName, int lineNumber) {
        super();
        _compilationUnit = compilationUnit;
        _callableName = callableName;
        _lineNumber = lineNumber;
    }
    
    public String getCallableName() {
        return _callableName;
    }
    public String getCompilationUnit() {
        return _compilationUnit;
    }
    public int getLineNumber() {
        return _lineNumber;
    }
    
    @Override
    public String toString () {
        return "line " + _lineNumber + "@" + _callableName + " [" + _compilationUnit + "]";
    }
}

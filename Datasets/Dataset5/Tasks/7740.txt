public static final String MARKER_FOR_IS_DELETE_LINE = "MARKER_FOR_XPAND_ISDELETELINE_59&21?%5&6<#_ENDMARKER";

/*
Copyright (c) 2008 Arno Haase, André Arnold.
All rights reserved. This program and the accompanying materials
are made available under the terms of the Eclipse Public License v1.0
which accompanies this distribution, and is available at
http://www.eclipse.org/legal/epl-v10.html

Contributors:
    Arno Haase - initial API and implementation
    André Arnold
 */
package org.eclipse.xtend.middleend.xtend.internal.xtendlib;


/**
 * This class supports the "isDeleteLine" feature of Xpand, i.e. the "-" at the end of a statement that deletes 
 *  whitespace both backward and forward.<br>
 *  
 * Since it is non-local functionality, it requires global postprocessing. For this purpose, a marker string is inserted wherever 
 *  this deletion of whitespace should be performed.<br>
 *  
 * Since this postprocessing requires transformation of the entire contents of a file into a flat string, this feature precludes
 *  streaming. Therefore a flag is introduced to indicate if the feature was actually used. This requires resetting at the beginning
 *  of each FILE statement.
 *  
 * @author Arno Haase (http://www.haase-consulting.com)
 */
public class XpandIsDeleteLine {
    public static final String MARKER_FOR_IS_DELETE_LINE = "MARKER_FOR_XPAND_ISDELETELINE_\ufa92Ä\u9988\u7123ä\u9881\u5499\u9284\u9934ÄÖÜß\ufa92Ä\u9988\u7123ä\u9882\u5499\u9284\u9934_ENDMARKER";

    private boolean _isInScope = false;
    private boolean _hasDeleteLine = false;
    
    
    public void XpandInitNewScope () {
        if (_isInScope)
            throw new IllegalStateException ("nested FILE statements are not permitted");
        _isInScope = true;
        _hasDeleteLine = false;
    }
    
    public void XpandRegisterDeleteLine() {
        _hasDeleteLine = true;
    }
    
    public CharSequence XpandPostprocess (CharSequence s) {
        try {
            if (! _hasDeleteLine)
                return s;

            String result = s.toString();
            int indMarker = result.indexOf (MARKER_FOR_IS_DELETE_LINE);
            
            while (indMarker >= 0) {
                // if and only if there is nothing but whitespace between the marker and the previous newline, delete this whitespace (leaving the newline alone)
                final int startOfDelete = indBeginDelete (result, indMarker);
                
                // delete all whitespace after the marker up to, and including, the subsequent newline - or nothing, if there is anything but whitespace between the marker and the subsequent newline
                final int endOfDelete = indEndDelete (result, indMarker);
                
                result = result.substring(0, startOfDelete) + result.substring (endOfDelete);
                indMarker = result.indexOf (MARKER_FOR_IS_DELETE_LINE);
            }
            
            return result;
        }
        finally {
            _isInScope = false;
            _hasDeleteLine = false;
        }
    }
    
    private boolean isNewLine(char c) {
        return c == '\n' || c == '\r';
    }

    private int indEndDelete (String buffer, int indMarker) {
        boolean wsOnly = true;
        int result = indMarker + MARKER_FOR_IS_DELETE_LINE.length();

        while (result < buffer.length() && wsOnly) {
            final char c = buffer.charAt (result);
            wsOnly = Character.isWhitespace(c);
            if (wsOnly && isNewLine(c)) {
                if (c == '\r' && result + 1 < buffer.length() && buffer.charAt (result + 1) == '\n')
                    result++;
                return result + 1;
            }
            
            result++;
        }
        
        return indMarker + MARKER_FOR_IS_DELETE_LINE.length();
    }
    
    private int indBeginDelete (String buffer, int indMarker) {
        boolean wsOnly = true;
        int result = indMarker;
        
        while (result > 0 && wsOnly) {
            final char c = buffer.charAt (result - 1);
            wsOnly = Character.isWhitespace(c);
            if (wsOnly && isNewLine (c))
                return result;
            
            result--;
        }
        
        if (wsOnly)
            return 0;
        else 
            return indMarker;
    }
}

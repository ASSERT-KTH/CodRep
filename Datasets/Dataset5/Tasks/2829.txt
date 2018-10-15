import org.apache.xerces.dom3.DOMError;

/*
 * Copyright (c) 2002 World Wide Web Consortium,
 * (Massachusetts Institute of Technology, Institut National de
 * Recherche en Informatique et en Automatique, Keio University). All
 * Rights Reserved. This program is distributed under the W3C's Software
 * Intellectual Property License. This program is distributed in the
 * hope that it will be useful, but WITHOUT ANY WARRANTY; without even
 * the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
 * PURPOSE.
 * See W3C License http://www.w3.org/Consortium/Legal/ for more details.
 */

package org.w3c.dom.ls;

import org.w3c.dom.events.Event;
import org.w3c.dom.DOMError;

/**
 * DOM Level 3 WD Experimental:
 * The DOM Level 3 specification is at the stage 
 * of Working Draft, which represents work in 
 * progress and thus may be updated, replaced, 
 * or obsoleted by other documents at any time. 
 * <p>
 * ParseErrorEvent is the event that is fired if there's an error in the XML 
 * document being parsed.
 * <p>See also the <a href='http://www.w3.org/TR/2002/WD-DOM-Level-3-ASLS-20020409'>Document Object Model (DOM) Level 3 Abstract Schemas and Load
and Save Specification</a>.
 */
public interface ParseErrorEvent extends Event {
    /**
     * An non-zero implementation dependent error code describing the error, 
     * or <code>0</code> if there is no error.
     */
    public DOMError getError();

}
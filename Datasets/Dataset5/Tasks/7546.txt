super(COMMENT, location);

/*
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 * 
 *      http://www.apache.org/licenses/LICENSE-2.0
 * 
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package org.apache.xerces.stax.events;

import javax.xml.stream.Location;
import javax.xml.stream.events.Comment;

/**
 * 
 * @author Lucian Holland
 *
 * @version $Id$
 */
public class CommentImpl extends XMLEventImpl implements Comment {

    /**
     * The text of the comment. Will be the empty string if there's no
     * body text in the comment.
     */
    private final String fText;

    /**
     * @param location
     */
    public CommentImpl(final String text, final Location location) {
        super(COMMENT, location, null);
        fText = text;
    }

    /**
     * @see javax.xml.stream.events.Comment#getText()
     */
    public String getText() {
        return fText; 
    }
}
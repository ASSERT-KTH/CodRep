private static final String ERROR_NAME = "error";

package org.eclipse.ecf.ui.messaging;

import org.eclipse.ecf.core.identity.ID;

public interface IMessageViewer {
    
    public void showMessage(ID fromID, ID toID, Type type, String subject, String message);

    public static class Type {
        
        private static final String NORMAL_NAME = "normal";
        private static final String CHAT_NAME = "chat";
        private static final String GROUP_CHAT_NAME = "group_chat";
        private static final String HEADLINE_NAME = "headline";
        private static final String ERROR_NAME = "to";
        
        private final transient String name;        
        // Protected constructor so that only subclasses are allowed to create instances
        protected Type(String name) {
            this.name = name;
        }
        public static Type fromString(String itemType) {
            if (itemType == null) return null;
            if (itemType.equals(NORMAL_NAME)) {
                return NORMAL;
            } else if (itemType.equals(CHAT_NAME)) {
                return CHAT;
            } else if (itemType.equals(GROUP_CHAT_NAME)) {
                return GROUP_CHAT;
            } else if (itemType.equals(HEADLINE_NAME)) {
                return HEADLINE;
            } else if (itemType.equals(ERROR_NAME)) {
                return ERROR;
            } else return null;
        }
        
        public static final Type NORMAL = new Type(NORMAL_NAME);
        public static final Type CHAT = new Type(CHAT_NAME);
        public static final Type GROUP_CHAT = new Type(GROUP_CHAT_NAME);
        public static final Type HEADLINE = new Type(HEADLINE_NAME);
        public static final Type ERROR = new Type(ERROR_NAME);
        
        public String toString() { return name; }
        // This is to make sure that subclasses don't screw up these methods
        public final boolean equals(Object that) {
            return super.equals(that);
        }
        public final int hashCode() {
            return super.hashCode();
        }
    }


}
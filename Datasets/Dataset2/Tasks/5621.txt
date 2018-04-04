import org.columba.core.pluginhandler.ExternalToolsPluginHandler;

import org.columba.core.main.MainInterface;
import org.columba.core.plugin.ExternalToolsPluginHandler;


/**
 * @author fdietz
 */
public class ExternalToolsHelper {
    public static String getSpamc() {
        return get("spamc");
    }

    public static String getSpamassassin() {
        return get("spamassassin");
    }

    public static String getSALearn() {
        return get("sa-learn");
    }

    public static String get(String name) {
        ExternalToolsPluginHandler handler = null;

        try {
            handler = (ExternalToolsPluginHandler) MainInterface.pluginManager.getHandler(
                    "org.columba.core.externaltools");

            return handler.getLocationOfExternalTool(name).getPath();
        } catch (Exception e) {
            e.printStackTrace();
        }

        return null;
    }
}
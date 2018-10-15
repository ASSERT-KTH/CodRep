import org.eclipse.wst.xquery.core.utils.PathUtil;

/*******************************************************************************
 * Copyright (c) 2008, 2009 28msec Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     Gabriel Petrovay (28msec) - initial API and implementation
 *******************************************************************************/
package org.eclipse.wst.xquery.internal.ui.templates;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import org.eclipse.core.runtime.IPath;
import org.eclipse.dltk.ast.declarations.ModuleDeclaration;
import org.eclipse.dltk.core.IExternalSourceModule;
import org.eclipse.dltk.core.IModelElement;
import org.eclipse.dltk.core.IModelElementVisitor;
import org.eclipse.dltk.core.IPreferencesLookupDelegate;
import org.eclipse.dltk.core.IScriptProject;
import org.eclipse.dltk.core.ISourceModule;
import org.eclipse.dltk.core.ModelException;
import org.eclipse.dltk.core.SourceParserUtil;
import org.eclipse.dltk.ui.CodeFormatterConstants;
import org.eclipse.dltk.ui.templates.IScriptTemplateIndenter;
import org.eclipse.dltk.ui.templates.ScriptTemplateContext;
import org.eclipse.dltk.ui.templates.TabExpandScriptTemplateIndenter;
import org.eclipse.dltk.ui.text.util.TabStyle;
import org.eclipse.jface.text.IDocument;
import org.eclipse.jface.text.templates.TemplateContextType;
import org.eclipse.wst.xquery.core.XQDTCorePlugin;
import org.eclipse.wst.xquery.core.model.ast.XQueryLibraryModule;
import org.eclipse.wst.xquery.core.model.ast.XQueryModule;
import org.eclipse.wst.xquery.internal.core.utils.PathUtil;
import org.eclipse.wst.xquery.ui.XQDTUIPlugin;

public class XQDTTemplateContext extends ScriptTemplateContext {

    protected XQDTTemplateContext(TemplateContextType type, IDocument document, int completionOffset,
            int completionLength, ISourceModule sourceModule) {
        super(type, document, completionOffset, completionLength, sourceModule);
    }

    protected IScriptTemplateIndenter getIndenter() {
        IPreferencesLookupDelegate prefs = getPreferences();
        if (TabStyle.SPACES == TabStyle.forName(prefs.getString(XQDTUIPlugin.PLUGIN_ID,
                CodeFormatterConstants.FORMATTER_TAB_CHAR))) {
            return new TabExpandScriptTemplateIndenter(prefs.getInt(XQDTUIPlugin.PLUGIN_ID,
                    CodeFormatterConstants.FORMATTER_TAB_SIZE));
        }
        return super.getIndenter();
    }

    public String[] getBoundarySpaceTypes() {
        return new String[] { "preserve", "strip" };
    }

    public String[] getDefaultNamespaceTypes() {
        return new String[] { "element", "function" };
    }

    public String[] getOrderingModes() {
        return new String[] { "ordered", "unordered" };
    }

    public String[] getEmptyOrderModes() {
        return new String[] { "greatest", "least" };
    }

    public String[] getPreserveModes() {
        return new String[] { "preserve", "no-preserve" };
    }

    public String[] getInheritModes() {
        return new String[] { "inherit", "no-inherit" };
    }

    public String[] getConstructionModes() {
        return new String[] { "strip", "preserve" };
    }

    public String[] getStrictOrder() {
        return new String[] { "order by", "stable order by" };
    }

    public String[] getOrderModifiers() {
        return new String[] { "ascending", "descending" };
    }

    public String[] getIterationVariables() {
        return new String[] { "e" };
    }

    public String[] getPositionalVariables() {
        return new String[] { "i" };
    }

    public String[] getVariables() {
        return new String[] { "x" };
    }

    public String[] getFunctionName() {
        // String key = getKey();
        // if ("function".startsWith(key)) {
        // key = "name";
        // }
        // return new String[] { key.length() != 0 ? key : "name" };
        return new String[] { "name" };
    }

    public String[] getFunctionNamespace() {
        XQueryModule xqModule = (XQueryModule)SourceParserUtil.getModuleDeclaration(getSourceModule());
        String namespacePrefix = xqModule.getNamespacePrefix();
        if (namespacePrefix != null) {
            return new String[] { namespacePrefix };
        }
        return new String[] { "" };
    }

    public String[] getFunctionParams() {
        return new String[] { "(: $param as type, ... :)" };
    }

    public String[] getQuantifiers() {
        String key = this.getKey();
        if (key != null && "every".startsWith(key)) {
            return new String[] { "every", "some" };
        }
        return new String[] { "some", "every" };
    }

    public String[] getSequenceTypes() {
        return new String[] { "item()", "node()", "text()", "empty-sequence()", "document-node( ... )",
                "element( ... )", "schema-element( ... )", "attribute( ... )", "schema-attribute( ... )",
                "processing-instruction( ... )", "comment()" };
    }

    public String[] getValidationModes() {
        return new String[] { "lax", "strict" };
    }

    public String[] getXQueryVersion() {
        return new String[] { "1.0" };
    }

    public String[] getXQueryEncoding() {
        return new String[] { "utf-8" };
    }

    // *************
    // XQuery Update
    // *************

    public String[] getTargetChoices() {
        return new String[] { "after", "before", "into", "as first into", "as last into" };
    }

    public String[] getNodeNodes() {
        return new String[] { "node", "nodes" };
    }

    public String[] getValueOf() {
        return new String[] { "", "value of " };
    }

    // ********
    // FullText
    // ********

    public String[] getSimpleFtOption() {
        return new String[] { "case insensitive", "case sensitive", "lowercase", "uppercase", "diacritics insensitive",
                "diacritics sensitive", "with stemming", "without stemming", "with thesaurus default",
                "with thesaurus at \"URI_literal\"", "without thesaurus", "with stop words (\"list_of_words\")",
                "without stop words", "with default stop words", "language \"string_literal\"", "with wildcards",
                "without wildcards", "without content expression" };
    }

    static class LibraryModuleCollector implements IModelElementVisitor {

        final Set<ISourceModule> modules = new HashSet<ISourceModule>();
        private boolean fBuiltins = false;

        public LibraryModuleCollector(boolean builtins) {
            fBuiltins = builtins;
        }

        public boolean visit(IModelElement element) {
            if (element.getElementType() == IModelElement.SOURCE_MODULE) {
                if (fBuiltins && element instanceof IExternalSourceModule) {
                    modules.add((ISourceModule)element);
                } else if (!fBuiltins && !(element instanceof IExternalSourceModule)) {
                    ModuleDeclaration module = SourceParserUtil.getModuleDeclaration((ISourceModule)element);
                    if (module instanceof XQueryLibraryModule) {
                        modules.add((ISourceModule)element);
                    }
                }
                return false;
            }
            return true;
        }
    }

    public String[] getBuiltingLibraryModuleURIs() {
        ISourceModule sourceModule = getSourceModule();
        IScriptProject project = sourceModule.getScriptProject();
        LibraryModuleCollector collector = new LibraryModuleCollector(true);
        List<String> namespaces = new ArrayList<String>();
        try {
            project.accept(collector);
            for (ISourceModule module : collector.modules) {
                XQueryLibraryModule library = (XQueryLibraryModule)SourceParserUtil.getModuleDeclaration(module);
                namespaces.add(library.getNamespaceUri().getValue());
            }
        } catch (ModelException e) {
            if (XQDTCorePlugin.DEBUG) {
                e.printStackTrace();
            }
            return new String[0];
        }

        String[] results = namespaces.toArray(new String[namespaces.size()]);
        Arrays.sort(results);
        return results;
    }

    private static final String DEFAULT_URI_AND_HINT_VARIABLE_VALUE = "\"URI\" at \"location hint\"";

    public String[] getLibraryModuleURIsAndHints() {
        ISourceModule sourceModule = getSourceModule();
        IScriptProject project = sourceModule.getScriptProject();
        LibraryModuleCollector collector = new LibraryModuleCollector(false);
        List<String> namespacesPlusHints = new ArrayList<String>();
        IPath parentPath = sourceModule.getParent().getPath();
        try {
            project.accept(collector);
            for (ISourceModule module : collector.modules) {
                XQueryLibraryModule library = (XQueryLibraryModule)SourceParserUtil.getModuleDeclaration(module);
                String uri = library.getNamespaceUri().getValue();
                String hint = PathUtil.makePathRelativeTo(module.getPath(), parentPath).toPortableString();
                namespacesPlusHints.add("\"" + uri + "\" at \"" + hint + "\"");
            }
        } catch (ModelException e) {
            if (XQDTCorePlugin.DEBUG) {
                e.printStackTrace();
            }
        }
        if (namespacesPlusHints.size() == 0) {
            return new String[] { DEFAULT_URI_AND_HINT_VARIABLE_VALUE };
        }

        String[] results = namespacesPlusHints.toArray(new String[namespacesPlusHints.size()]);
        Arrays.sort(results);
        return results;
    }

    public String[] getSchemaImportPrefix() {
        return new String[] { "namespace ns =", "default element namespace" };
    }

    public String[] getSchemaUriAndHints() {
        return new String[] { "\"\" at \"\"" };
    }

}
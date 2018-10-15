parameterNames[j] = ("$" + arg.getName()).toCharArray();

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
package org.eclipse.wst.xquery.internal.core.codeassist;

import java.net.URI;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import org.eclipse.core.resources.IProject;
import org.eclipse.core.runtime.IPath;
import org.eclipse.dltk.ast.declarations.Argument;
import org.eclipse.dltk.ast.declarations.MethodDeclaration;
import org.eclipse.dltk.ast.declarations.ModuleDeclaration;
import org.eclipse.dltk.codeassist.IAssistParser;
import org.eclipse.dltk.codeassist.ScriptCompletionEngine;
import org.eclipse.dltk.core.CompletionProposal;
import org.eclipse.dltk.core.IExternalSourceModule;
import org.eclipse.dltk.core.IField;
import org.eclipse.dltk.core.IMethod;
import org.eclipse.dltk.core.IModelElement;
import org.eclipse.dltk.core.IScriptProject;
import org.eclipse.dltk.core.ISourceModule;
import org.eclipse.dltk.core.IType;
import org.eclipse.dltk.core.ModelException;
import org.eclipse.dltk.core.SourceParserUtil;
import org.eclipse.wst.xquery.core.IUriResolver;
import org.eclipse.wst.xquery.core.XQDTCorePlugin;
import org.eclipse.wst.xquery.core.model.ast.XQueryLibraryModule;
import org.eclipse.wst.xquery.core.model.ast.XQueryModule;
import org.eclipse.wst.xquery.core.model.ast.XQueryModuleImport;
import org.eclipse.wst.xquery.core.model.ast.XQueryStringLiteral;
import org.eclipse.wst.xquery.internal.core.text.XQDTWordDetector;
import org.eclipse.wst.xquery.internal.core.utils.ImplicitImportsUtil;
import org.eclipse.wst.xquery.internal.core.utils.LanguageUtil;
import org.eclipse.wst.xquery.internal.core.utils.ResolverUtil;

public class XQDTCompletionEngine extends ScriptCompletionEngine {

    protected XQDTAssistParser fParser;
    protected org.eclipse.dltk.core.ISourceModule fSourceModule;
    protected int fLanguageLevel;
    protected String fPrefix;
    protected CompletionPrefixType fPrefixType = CompletionPrefixType.NORMAL;

    public static enum CompletionPrefixType {
        NORMAL, DOLLAR, COLON, AMPERSAND
    }

    public final static int RELEVANCE_KEYWORD = 100000;
    public final static int RELEVANCE_TEMPLATE = 1000000;
    public final static int RELEVANCE_FUNCTIONS = 10000000;
    public final static int RELEVANCE_VARIABLES = 100000000;

    protected int getEndOfEmptyToken() {
        return 0;
    }

    protected String processFieldName(IField field, String token) {
        // TODO Auto-generated method stub
        return null;
    }

    protected String processMethodName(IMethod method, String token) {
        return method.getElementName();
    }

    protected String processTypeName(IType method, String token) {
        // TODO Auto-generated method stub
        return null;
    }

    public IAssistParser getParser() {
        if (fParser == null) {
            fParser = new XQDTAssistParser();
        }
        return fParser;
    }

    public void complete(org.eclipse.dltk.compiler.env.ISourceModule sourceModule, int completionPosition, int pos) {
        fSourceModule = (ISourceModule)sourceModule.getModelElement();
        fileName = sourceModule.getFileName();
        actualCompletionPosition = completionPosition;
        offset = pos;
        fLanguageLevel = getLanguageLevel(fSourceModule);
        fPrefix = extractPrefix(completionPosition);
        setSourceRange(actualCompletionPosition - fPrefix.length(), actualCompletionPosition);

        if (DEBUG) {
            System.out.println("Completion requested: " + fSourceModule.getElementName() + " (" + completionPosition
                    + "," + pos + ",'" + fPrefix + "')");
        }

        this.requestor.beginReporting();

        // report the keywords
        reportKeywords();

        // report the functions
        reportFunctions();

        // report the entities
        reportEntities();

        this.requestor.endReporting();
    }

    protected int getLanguageLevel(ISourceModule module) {
        return LanguageUtil.getLanguageLevel(module);
    }

    private void reportKeywords() {
        // if this is NORMAL completion (not a DOLLAR, COLON, etc.)
        if (fPrefixType == CompletionPrefixType.NORMAL) {
            // if keywords should be suggested
            if (!this.requestor.isIgnored(CompletionProposal.KEYWORD)) {
                // only for non-empty prefix
                if (fPrefix.length() != 0) {
                    String[] keywords = XQDTKeywords.findByPrefix(fPrefix, fLanguageLevel);
                    for (int j = 0; j < keywords.length; j++) {
                        reportKeyword(keywords[j]);
                    }
                }
            }
        }
    }

    private void reportKeyword(String name) {
        // accept result
        if (!requestor.isIgnored(CompletionProposal.KEYWORD)) {
            noProposal = false;
            CompletionProposal proposal = createProposal(CompletionProposal.KEYWORD, actualCompletionPosition);

            proposal.setName(name.toCharArray());
            proposal.setCompletion(name.toCharArray());
            // proposal.setFlags(Flags.AccDefault);
            proposal.setReplaceRange(this.startPosition - this.offset, this.endPosition - this.offset);
            proposal.setRelevance(RELEVANCE_KEYWORD);
            this.requestor.accept(proposal);
        }
    }

    private void reportFunctions() {
        // only for NORMAL and COLON prefix types
        if (fPrefixType == CompletionPrefixType.NORMAL || fPrefixType == CompletionPrefixType.COLON) {
            // if method references should be suggested
            if (!this.requestor.isIgnored(CompletionProposal.METHOD_REF)) {
                reportDeclaredFunctions();
                reportImportedFunctions();
                reportVendorImplicitImportedFunctions();
                // XPath built-in functions are reported as templates through XQDTFnFunctionCompletionProcessor
            }
        }
    }

    private void reportDeclaredFunctions() {
        try {
            XQueryModule module = (XQueryModule)SourceParserUtil.getModuleDeclaration(fSourceModule);
            MethodDeclaration[] decls = module.getFunctions();
            buildFunctionCompletions(decls, null);
        } catch (Exception e) {
            if (DEBUG) {
                e.printStackTrace();
            }
        }
    }

    private void reportImportedFunctions() {
        try {
            XQueryModule module = (XQueryModule)SourceParserUtil.getModuleDeclaration(fSourceModule);
            List<XQueryModuleImport> importedModules = new ArrayList<XQueryModuleImport>(module.getImports());
            List<String> namespacePrefixes = new ArrayList<String>();
            for (XQueryModuleImport importedModule : importedModules) {
                namespacePrefixes.add(importedModule.getNamespacePrefix());
            }

            URI baseUri = getBaseUri();
            List<ISourceModule> resolvedModules = resolveImports(baseUri, importedModules);
            if (resolvedModules == null) {
                return;
            }

            for (int i = 0; i < resolvedModules.size(); i++) {
                ISourceModule resolvedModule = resolvedModules.get(i);
                if (resolvedModule == null) {
                    continue;
                }

                ModuleDeclaration imported = SourceParserUtil.getModuleDeclaration(resolvedModules.get(i));
                if (imported instanceof XQueryLibraryModule) {
                    XQueryLibraryModule lib = (XQueryLibraryModule)imported;
                    XQueryModuleImport importedModule = importedModules.get(i);
                    if ((importedModule != null)
                            && !lib.getNamespaceUri().getValue().equals(importedModule.getNamespaceUri().getValue())) {
                        continue;
                    }
                    buildFunctionCompletions(lib.getFunctions(), namespacePrefixes.get(i));
                }
            }

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private void reportVendorImplicitImportedFunctions() {
        Map<String, IPath> implicitModuleImports = ImplicitImportsUtil.getImplicitImportPrefixes(fSourceModule);

        for (String prefix : implicitModuleImports.keySet()) {
            reportBuiltinFunctions(prefix, implicitModuleImports.get(prefix));
        }
    }

    private void reportBuiltinFunctions(String namespacePrefix, IPath builtinModulePath) {
        try {
            IScriptProject project = fSourceModule.getScriptProject();

            IModelElement element = project.findElement(builtinModulePath);

            if (element instanceof IExternalSourceModule) {
                ModuleDeclaration imported = SourceParserUtil.getModuleDeclaration((ISourceModule)element);
                if (imported instanceof XQueryLibraryModule) {
                    buildFunctionCompletions(((XQueryLibraryModule)imported).getFunctions(), namespacePrefix);
                }
            } else {
                if (XQDTCorePlugin.DEBUG) {
                    System.out.println("Unable to find builtin module " + builtinModulePath);
                }
            }

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private void reportEntities() {
        // only for AMPERSAND prefix type
        if (fPrefixType == CompletionPrefixType.AMPERSAND) {
            for (int i = 0; i < XQDTKeywords.EMTITY_REFERECE_NAMES.length; i++) {
                String name = XQDTKeywords.EMTITY_REFERECE_NAMES[i];
                if (name.startsWith(fPrefix)) {
                    reportEntity(XQDTKeywords.EMTITY_REFERECE_NAMES[i], XQDTKeywords.EMTITY_REFERECE_CHAR[i]);
                }
            }
        }
    }

    private void reportEntity(String name, String character) {
        // accept result
        noProposal = false;
        CompletionProposal proposal = createProposal(CompletionProposal.KEYWORD, actualCompletionPosition);

        String completion = "&" + name + ";";
        String displayName = "&" + name + "; (" + character + ")";

        proposal.setName(displayName.toCharArray());
        proposal.setCompletion(completion.toCharArray());
        // proposal.setFlags(Flags.AccDefault);
        proposal.setReplaceRange(this.startPosition - this.offset - 1, this.endPosition - this.offset);
        proposal.setRelevance(RELEVANCE_KEYWORD);
        this.requestor.accept(proposal);
    }

    protected URI getBaseUri() {
        XQueryModule module = (XQueryModule)SourceParserUtil.getModuleDeclaration(fSourceModule);

        URI uri = module.getBaseUri();
        if (uri != null) {
            return uri;
        }

        return fSourceModule.getResource().getLocationURI();
    }

    private List<ISourceModule> resolveImports(URI baseUri, List<XQueryModuleImport> importedModules) {
        List<URI> resolvedUris = new ArrayList<URI>(importedModules.size());
        IUriResolver resolver = getModuleResolver();
        if (resolver == null) {
            return null;
        }

        // I. first resolve the import URI's
        for (XQueryModuleImport imp : importedModules) {
            String uri = imp.getNamespaceUri().getValue();
            List<XQueryStringLiteral> hintList = imp.getHints();
            String[] hints = new String[hintList.size()];
            for (int i = 0; i < hintList.size(); i++) {
                hints[i] = hintList.get(i).getValue();
            }

            // this will add either a resolved URI to the list or a null
            URI resolvedUri = resolver.resolveModuleImport(baseUri, uri, hints);
            resolvedUris.add(resolvedUri);
        }

        // II. get the ISourceModule for each module import
        List<ISourceModule> resolved = new ArrayList<ISourceModule>(resolvedUris.size());
        IScriptProject project = fSourceModule.getScriptProject();

        for (int i = 0; i < resolvedUris.size(); i++) {
            URI resolvedUri = resolvedUris.get(i);
            if (resolvedUri != null) {
                resolved.add(resolver.locateSourceModule(resolvedUri, project));
            } else {
                resolved.add(null);
            }
        }

        return resolved;
    }

    protected IUriResolver getModuleResolver() {
        IProject project = fSourceModule.getScriptProject().getProject();
        return ResolverUtil.getProjectUriResolver(project);
    }

    @SuppressWarnings("unchecked")
    private void buildFunctionCompletions(MethodDeclaration[] decls, String prefix) {
        if (decls == null) {
            return;
        }

        for (int i = 0; i < decls.length; i++) {
            MethodDeclaration decl = decls[i];
            String name = decl.getName();
            if (prefix != null) {
                name = prefix + ":" + name.substring(name.indexOf(':') + 1);
            }
            if (name.startsWith(fPrefix) || name.substring(name.indexOf(':') + 1).startsWith(fPrefix)) {
                CompletionProposal proposal = createProposal(CompletionProposal.METHOD_REF, actualCompletionPosition);
                proposal.setName(name.toCharArray());
                proposal.setCompletion(name.toCharArray());

                List args = decl.getArguments();
                char parameterNames[][] = new char[args.size()][];
                for (int j = 0; j < args.size(); ++j) {
                    Argument arg = (Argument)args.get(j);
                    parameterNames[j] = arg.getName().toCharArray();
                }
                proposal.setParameterNames(parameterNames);

                proposal.setReplaceRange(this.startPosition - this.offset, this.endPosition - this.offset);
                proposal.setRelevance(RELEVANCE_FUNCTIONS);
                requestor.accept(proposal);
                noProposal = false;
            }
        }
    }

    protected String extractPrefix(int offset) {
        char[] content;
        try {
            content = fSourceModule.getSourceAsCharArray();
        } catch (ModelException e) {
            return "";
        }
        if (offset > content.length) {
            return "";
        }

        XQDTWordDetector wd = new XQDTWordDetector();

        String word = extractWord(content, offset, wd, true);
        if (fPrefixType == CompletionPrefixType.COLON) {
            int prefixLen = word.length();
            String namespace = extractWord(content, offset - (prefixLen + 1), wd, false);
            word = namespace + ":" + word;
        }

        return word;
    }

    private String extractWord(char[] content, int offset, XQDTWordDetector wd, boolean checkPrefixPrefix) {
        int i = offset;
        char ch = 0;
        while (i > 0) {
            ch = content[i - 1];

            if (!wd.isWordPart(ch)) {
                break;
            }
            i--;
        }
        if (checkPrefixPrefix) {
            if (ch == ':') {
                fPrefixType = CompletionPrefixType.COLON;
            } else if (ch == '$') {
                fPrefixType = CompletionPrefixType.DOLLAR;
            } else if (ch == '&') {
                fPrefixType = CompletionPrefixType.AMPERSAND;
            } else {
                fPrefixType = CompletionPrefixType.NORMAL;
            }
        }
        return new String(content, i, offset - i);
    }

}
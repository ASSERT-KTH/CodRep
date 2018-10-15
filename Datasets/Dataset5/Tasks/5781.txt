+ (origDef!=null?origDef.getName():"") + "'", origDef));

/*******************************************************************************
 * Copyright (c) 2005, 2009 committers of openArchitectureWare and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     committers of openArchitectureWare - initial API and implementation
 *******************************************************************************/

package org.eclipse.internal.xpand2.ast;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Set;

import org.eclipse.internal.xpand2.model.XpandAdvice;
import org.eclipse.internal.xpand2.model.XpandDefinition;
import org.eclipse.internal.xpand2.model.XpandResource;
import org.eclipse.internal.xtend.expression.ast.SyntaxElement;
import org.eclipse.xpand2.XpandExecutionContext;
import org.eclipse.xpand2.XpandUtil;
import org.eclipse.xtend.expression.AnalysationIssue;

/**
 * *
 * 
 * @author Sven Efftinge (http://www.efftinge.de) *
 */
public class Template extends SyntaxElement implements XpandResource {
    private ImportDeclaration[] imports;

    private Definition[] definitions;

    private String fullyQualifiedName;

    private ImportDeclaration[] extensions;

    private Advice[] advices;

    public ImportDeclaration[] getExtensions() {
        return extensions;
    }
    
	public List<String> getImportedExtensionsAsList() {
        final List<String> result = new ArrayList<String>();
		for (ImportDeclaration ext : extensions) {
            result.add(ext.getImportString().getValue());
        }
        return result;
    }

    public String getFullyQualifiedName() {
        return fullyQualifiedName;
    }

    public void setFullyQualifiedName(final String fullyQualifiedName) {
        this.fullyQualifiedName = fullyQualifiedName;
    }

	public Template(final ImportDeclaration[] imports, final ImportDeclaration[] extensions,
			final Definition[] definitions, final Advice[] advices) {
        this.imports = imports;
        this.extensions = extensions;
        for (int i = 0; i < definitions.length; i++) {
            definitions[i].setOwner(this);
        }
        this.definitions = definitions;
        for (int i = 0; i < advices.length; i++) {
            advices[i].setOwner(this);
        }
        this.advices = advices;
    }

    public XpandDefinition[] getDefinitions() {
        return definitions;
    }
    
    public List<XpandDefinition> getDefinitionsAsList() {
        return Arrays.asList((XpandDefinition[]) definitions);
    }
    
    public AbstractDefinition[] getAllDefinitions() {
        List<AbstractDefinition> l = new ArrayList<AbstractDefinition>();
        l.addAll(Arrays.asList(definitions));
        l.addAll(Arrays.asList(advices));
        
		Collections.sort(l, new Comparator<SyntaxElement>() {

            public int compare(SyntaxElement o1, SyntaxElement o2) {
                return new Integer(o1.getStart()).compareTo(o2.getStart());
			}
		});
        return l.toArray(new AbstractDefinition[l.size()]);
    }

    public ImportDeclaration[] getImports() {
        return imports;
    }

    public List<ImportDeclaration> getImportsAsList() {
        return Arrays.asList(imports);
    }
    
    private String[] commonPrefixes = null;

    public void analyze(XpandExecutionContext ctx, final Set<AnalysationIssue> issues) {
    	try {
	        ctx = (XpandExecutionContext) ctx.cloneWithResource(this);
			if (ctx.getCallback() != null) {
				if(!ctx.getCallback().pre(this, ctx)) {
					return;
				}
			}

			checkDuplicateDefinitions(issues);
	        for (int i = 0; i < definitions.length; i++) {
	            definitions[i].analyze(ctx, issues);
	        }

	        for (int i = 0; i < advices.length; i++) {
	            advices[i].analyze(ctx, issues);
	        }
    	}
		catch (RuntimeException ex) {
			issues.add(new AnalysationIssue(AnalysationIssue.INTERNAL_ERROR, ex.getMessage(), this));
    }
		finally {
			if (ctx.getCallback() != null) {
				ctx.getCallback().post(this, ctx, null);
			}
		}
	}

    public XpandDefinition[] getDefinitionsByName(final String aName) {
        final List<Definition> defs = new ArrayList<Definition>();
        for (int i = 0; i < definitions.length; i++) {
            final Definition def = definitions[i];
            if (def.getName().equals(aName)) {
                defs.add(def);
            }
        }
        return defs.toArray(new XpandDefinition[defs.size()]);
    }

    public String[] getImportedNamespaces() {
        if (commonPrefixes == null) {
            final List<String> l = new ArrayList<String>();
            final String thisNs = XpandUtil.withoutLastSegment(getFullyQualifiedName());

            for (int i = 0; i < getImports().length; i++) {
                final ImportDeclaration anImport = getImports()[i];
                l.add(anImport.getImportString().getValue());
            }

			if (thisNs != null) {
				l.add(thisNs);
			}

            commonPrefixes = l.toArray(new String[l.size()]);
        }
        return commonPrefixes;
    }

    public List<String> getImportedNamespacesAsList() {
        return Arrays.asList(getImportedNamespaces());
    }
    
    String[] importedExtensions = null;

    public String[] getImportedExtensions() {
        if (importedExtensions == null) {
            final List<String> l = new ArrayList<String>();
            for (int i = 0; i < getExtensions().length; i++) {
                final ImportDeclaration anImport = getExtensions()[i];
                l.add(anImport.getImportString().getValue());
            }
            importedExtensions = l.toArray(new String[l.size()]);
        }
        return importedExtensions;
    }

    public XpandAdvice[] getAdvices() {
        return advices;
    }

	private void checkDuplicateDefinitions(Set<AnalysationIssue> issues) {
		Set<Definition> definitionSet = new HashSet<Definition>();
		for (Definition def : definitions) {
			if (!definitionSet.contains(def)) {
				definitionSet.add(def);
			}
			else {
				Definition origDef = null;
				for (Iterator<Definition> it = definitionSet.iterator(); it.hasNext();) {
					Definition d = it.next();
					if (d.equals(def)) {
						origDef = d;
						break;
					}
				}
				issues.add(new AnalysationIssue(AnalysationIssue.INTERNAL_ERROR, "Duplicate definition '"
						+ def.getName() + "'", def));
				issues.add(new AnalysationIssue(AnalysationIssue.INTERNAL_ERROR, "Duplicate definition '"
						+ origDef.getName() + "'", origDef));
			}
		}
	}
}
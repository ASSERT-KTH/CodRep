package org.eclipse.xtend.middleend.old.xtend;

/*
Copyright (c) 2008 Arno Haase.
All rights reserved. This program and the accompanying materials
are made available under the terms of the Eclipse Public License v1.0
which accompanies this distribution, and is available at
http://www.eclipse.org/legal/epl-v10.html

Contributors:
    Arno Haase - initial API and implementation
 */
package org.eclipse.xtend.middleend.old;

import java.io.InputStream;

import org.eclipse.emf.mwe.core.WorkflowContext;
import org.eclipse.emf.mwe.core.issues.Issues;
import org.eclipse.emf.mwe.core.monitor.ProgressMonitor;
import org.eclipse.emf.mwe.core.resources.ResourceLoaderFactory;
import org.eclipse.internal.xtend.expression.parser.SyntaxConstants;
import org.eclipse.internal.xtend.xtend.XtendFile;
import org.eclipse.xtend.expression.AbstractExpressionsUsingWorkflowComponent;
import org.eclipse.xtend.expression.ExecutionContext;
import org.eclipse.xtend.expression.ExpressionFacade;
import org.eclipse.xtend.expression.Variable;


/**
 * 
 * @author Arno Haase (http://www.haase-consulting.com)
 */
public class XtendComponent extends AbstractExpressionsUsingWorkflowComponent {

//    private final Log _log = LogFactory.getLog(getClass());

    
//    private List<String> extensionAdvices = new ArrayList<String>();
//
//    public void addExtensionAdvice(String extensionAdvices) {
//		if ( !this.extensionAdvices.contains(extensionAdvices) ) 
//			this.extensionAdvices.add( extensionAdvices );
//	}

    /** Stores the value of the 'invoke' property. Needed for error analysis. */ 
    private String _invokeExpression;
    String _extensionFile = null;
    private String _expression = null;
    private String _outputSlot = WorkflowContext.DEFAULT_SLOT;

//    private String collectProfileSummary = null;
//    private String verboseProfileFilename = null;
//    
//    public void setCollectProfileSummary (String c) {
//        collectProfileSummary = c;
//    }
//    
//    public void setVerboseProfileFilename (String f) {
//        verboseProfileFilename = f;
//    }

    
    @Override
    public String getLogMessage() {
    	return "executing '" + _invokeExpression + "'";
    }
    
    public void setInvoke (String invoke) {
    	_invokeExpression = invoke;
        final int i = invoke.lastIndexOf (SyntaxConstants.NS_DELIM);
        if (i != -1) {
            _extensionFile = invoke.substring(0, i);
            _expression = invoke.substring (i + SyntaxConstants.NS_DELIM.length());
        } 
        else 
            _expression = invoke;
    }

    public void setOutputSlot (String outputSlot) {
        _outputSlot = outputSlot;
    }
    
    @Override
    public void invokeInternal2(final WorkflowContext ctx, final ProgressMonitor monitor, final Issues issues) {
        if (! extensionFileExists ()) {
            issues.addError ("Cannot find extension file: " + _extensionFile);
            return;
        }
        
//        OutputStream verboseProfileOutputStream = null;
//
//        if (verboseProfileFilename != null) {
//            try {
//                verboseProfileOutputStream = new BufferedOutputStream (new FileOutputStream (verboseProfileFilename));
//                ProfileCollector.getInstance().setDetailedLoggingWriter(verboseProfileOutputStream);
//            }
//            catch (IOException exc) {
//                _log.warn("could not open profiling log file", exc);
//            }
//        }

        
        ExecutionContext ec = getExecutionContext(ctx);
        
//        for (String advice : extensionAdvices) {
//            final String[] allAdvices = advice.split(",");
//            for (int i = 0; i < allAdvices.length; i++) {
//                final String string = allAdvices[i];
//                ec.registerExtensionAdvices(string.trim());
//            }
//        }
//
//        ec = ec.cloneWithResource(new Resource() {
//            private String name = "noName";
//
//            public String getFullyQualifiedName() {
//                return name;
//            }
//
//            public void setFullyQualifiedName(final String fqn) {
//                name = fqn;
//            }
//
//            public String[] getImportedNamespaces() {
//                return new String[0];
//            }
//
//            public String[] getImportedExtensions() {
//                return new String[] { _extensionFile };
//            }
//        });
        final String[] slots = ctx.getSlotNames();
        for (int i = 0; i < slots.length; i++) {
            ec = ec.cloneWithVariable(new Variable(slots[i], ctx.get(slots[i])));
        }

//        if (monitor!=null) {
//        	ec.setMonitor(monitor);
//        }
        
        final Object result = new ExpressionFacade (ec).evaluate(_expression);
        ctx.set (_outputSlot, result);

//        ProfileCollector.getInstance().finish();
//        if ("true".equalsIgnoreCase(this.collectProfileSummary)) {
//            _log.info ("profiling info: \n" + ProfileCollector.getInstance().toString());
//        }
        
//        if (verboseProfileOutputStream != null) {
//            try {
//                verboseProfileOutputStream.close ();
//            }
//            catch (IOException exc) {
//                _log.warn("problem closing profile log file", exc);
//            }
//        }
    }

    private boolean extensionFileExists() {
        InputStream is = null;
        try {
            is = ResourceLoaderFactory.createResourceLoader().getResourceAsStream (_extensionFile.replace (SyntaxConstants.NS_DELIM, "/") + XtendFile.FILE_EXTENSION);
        }
        catch (Exception exc) {
            // do nothing - an exception just means that the extension file does not exist 
        }
        if (is != null) {
            try {
                is.close ();
            }
            catch (Exception e) {}
        }
        return is != null;
    }

    @Override
    public void checkConfiguration (Issues issues) {
        super.checkConfiguration (issues);
        
        // Try to create detailed error message (see Bug#172567)
        String compPrefix = getId()!=null ? getId()+": " : "";
        
        if (_invokeExpression == null || _invokeExpression.trim().length()==0) {
            issues.addError(compPrefix + "Property 'invoke' not specified.");
            return;
        }
        if (_extensionFile == null) {
            issues.addError (compPrefix + "Error parsing property 'invoke': Could not extract name of the extension file.");
            return;
        }
        if (! extensionFileExists () || _expression == null) {
            issues.addError (compPrefix + "Property 'invoke' not specified properly. Extension file '" + _extensionFile + "' not found.");
            return;
        }
        if (_expression == null) {
            issues.addError (compPrefix + "Error parsing property 'invoke': Could not extract the expression to invoke in extension file '" + _extensionFile + "'.");
            return;
        }
    }
}
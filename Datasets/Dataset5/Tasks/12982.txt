package org.eclipse.wst.xquery.ui.templates;

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

import org.eclipse.jface.text.templates.TemplateContext;
import org.eclipse.jface.text.templates.TemplateVariableResolver;

public class XQueryTemplateVariables {

    public static class IterationVariables extends TemplateVariableResolver {

        public IterationVariables() {
            super("iteration_variable", "XQuery: the name of the iteration variable");
        }

        protected String[] resolveAll(TemplateContext context) {
            return ((XQDTTemplateContext)context).getIterationVariables();
        }
    }

    public static class PositionalVariables extends TemplateVariableResolver {

        public PositionalVariables() {
            super("positional_variable", "XQuery: the name of the positional variable");
        }

        protected String[] resolveAll(TemplateContext context) {
            return ((XQDTTemplateContext)context).getPositionalVariables();
        }
    }

    public static class Variables extends TemplateVariableResolver {

        public Variables() {
            super("variable", "XQuery: the name of a variable");
        }

        protected String[] resolveAll(TemplateContext context) {
            return ((XQDTTemplateContext)context).getVariables();
        }
    }

    public static class FunctionName extends TemplateVariableResolver {

        public FunctionName() {
            super("function_name", "XQuery: the function name");
        }

        protected String[] resolveAll(TemplateContext context) {
            return ((XQDTTemplateContext)context).getFunctionName();
        }
    }

    public static class FunctionNamespace extends TemplateVariableResolver {

        public FunctionNamespace() {
            super("function_namespace", "XQuery: the function namespace");
        }

        protected String[] resolveAll(TemplateContext context) {
            return ((XQDTTemplateContext)context).getFunctionNamespace();
        }

        @Override
        protected boolean isUnambiguous(TemplateContext context) {
            return true;
        }
    }

    public static class FunctionParams extends TemplateVariableResolver {

        public FunctionParams() {
            super("function_params", "XQuery: the function parameters");
        }

        protected String[] resolveAll(TemplateContext context) {
            return ((XQDTTemplateContext)context).getFunctionParams();
        }
    }

    public static class Quantifiers extends TemplateVariableResolver {

        public Quantifiers() {
            super("quantifier",
                    "XQuery: the qualifiers of a in a Quantified Expression. Can be either \"some\" or \"every\"");
        }

        protected String[] resolveAll(TemplateContext context) {
            return ((XQDTTemplateContext)context).getQuantifiers();
        }
    }

    public static class SequenceTypes extends TemplateVariableResolver {

        public SequenceTypes() {
            super("sequence_type", "XQuery: common types of sequences");
        }

        protected String[] resolveAll(TemplateContext context) {
            return ((XQDTTemplateContext)context).getSequenceTypes();
        }
    }

    public static class BoundarySpaceTypes extends TemplateVariableResolver {

        public BoundarySpaceTypes() {
            super("boundary_space_type",
                    "XQuery: the type of the boundry space in a Boundary Space Declaration. Can be either \"preserve\" or \"strip\"");
        }

        protected String[] resolveAll(TemplateContext context) {
            return ((XQDTTemplateContext)context).getBoundarySpaceTypes();
        }
    }

    public static class DefaultNamespaceTypes extends TemplateVariableResolver {

        public DefaultNamespaceTypes() {
            super("default_namespace_type",
                    "XQuery: the target of the Default Namespace Declaration. Can be either \"element\" or \"function\"");
        }

        protected String[] resolveAll(TemplateContext context) {
            return ((XQDTTemplateContext)context).getDefaultNamespaceTypes();
        }
    }

    public static class OrderingModes extends TemplateVariableResolver {

        public OrderingModes() {
            super("ordering_mode",
                    "XQuery: the default ordering mode in an Ordering Mode Declaration. Can be either \"ordered\" or \"unordered\"");
        }

        protected String[] resolveAll(TemplateContext context) {
            return ((XQDTTemplateContext)context).getOrderingModes();
        }
    }

    public static class EmptyOrderModes extends TemplateVariableResolver {

        public EmptyOrderModes() {
            super("empty_order_mode",
                    "XQuery: the default ordering mode of the empty sequence. Can be either \"greatest\" or \"least\"");
        }

        protected String[] resolveAll(TemplateContext context) {
            return ((XQDTTemplateContext)context).getEmptyOrderModes();
        }
    }

    public static class PreserveModes extends TemplateVariableResolver {

        public PreserveModes() {
            super("preserve_mode",
                    "XQuery: the preserve mode in a in a Copy Namespace Declaration. Can be either \"preserve\" or \"no-preserve\"");
        }

        protected String[] resolveAll(TemplateContext context) {
            return ((XQDTTemplateContext)context).getPreserveModes();
        }
    }

    public static class InheritModes extends TemplateVariableResolver {

        public InheritModes() {
            super("inherit_mode",
                    "XQuery: the inherit mode in a in a Copy Namespace Declaration. Can be either \"inherit\" or \"no-inherit\"");
        }

        protected String[] resolveAll(TemplateContext context) {
            return ((XQDTTemplateContext)context).getInheritModes();
        }
    }

    public static class ConstructionModes extends TemplateVariableResolver {

        public ConstructionModes() {
            super("construction_mode",
                    "XQuery: the construction mode in a in a Construction Declaration. Can be either \"strip\" or \"preserve\"");
        }

        protected String[] resolveAll(TemplateContext context) {
            return ((XQDTTemplateContext)context).getConstructionModes();
        }
    }

    public static class StrictOrder extends TemplateVariableResolver {

        public StrictOrder() {
            super("strict_order",
                    "XQuery: the strict order mode in an Order by Expression. Can be either \"order by\" or \"stable order by\"");
        }

        protected String[] resolveAll(TemplateContext context) {
            return ((XQDTTemplateContext)context).getStrictOrder();
        }
    }

    public static class OrderModifiers extends TemplateVariableResolver {

        public OrderModifiers() {
            super("order_modifier",
                    "XQuery: the order modifier in an Order by Expression. Can be either \"ascending\" or \"descending\"");
        }

        protected String[] resolveAll(TemplateContext context) {
            return ((XQDTTemplateContext)context).getOrderModifiers();
        }
    }

    public static class ValidationModes extends TemplateVariableResolver {

        public ValidationModes() {
            super("validation_mode",
                    "XQuery: the validation mode in a validate Expression. Can be either \"lax\" or \"strict\"");
        }

        protected String[] resolveAll(TemplateContext context) {
            return ((XQDTTemplateContext)context).getValidationModes();
        }
    }

    public static class XQueryVersion extends TemplateVariableResolver {

        public XQueryVersion() {
            super("ver_string", "XQuery: the XQuery version of this module");
        }

        protected String[] resolveAll(TemplateContext context) {
            return ((XQDTTemplateContext)context).getXQueryVersion();
        }
    }

    public static class XQueryEncoding extends TemplateVariableResolver {

        public XQueryEncoding() {
            super("enc_string", "XQuery: the encoding of this module");
        }

        protected String[] resolveAll(TemplateContext context) {
            return ((XQDTTemplateContext)context).getXQueryEncoding();
        }
    }

    public static class TargetChoices extends TemplateVariableResolver {

        public TargetChoices() {
            super("target_choice", "XQuery Update: different target choices in an Insert Expression");
        }

        protected String[] resolveAll(TemplateContext context) {
            return ((XQDTTemplateContext)context).getTargetChoices();
        }
    }

    public static class NodeNodes extends TemplateVariableResolver {

        public NodeNodes() {
            super("node_nodes", "XQuery Update: the \"node\" or \"nodes\" in an Insert or Delete Expression");
        }

        protected String[] resolveAll(TemplateContext context) {
            return ((XQDTTemplateContext)context).getNodeNodes();
        }
    }

    public static class ValueOf extends TemplateVariableResolver {

        public ValueOf() {
            super("value_of", "XQuery Update: the optional \"value-of\" keyword in a Replace Expression");
        }

        protected String[] resolveAll(TemplateContext context) {
            return ((XQDTTemplateContext)context).getValueOf();
        }
    }

    public static class SimpleFtOption extends TemplateVariableResolver {

        public SimpleFtOption() {
            super("simple_ftoption", "XQuery Fulltext: different fulltext options");
        }

        protected String[] resolveAll(TemplateContext context) {
            return ((XQDTTemplateContext)context).getSimpleFtOption();
        }
    }

    public static class ImportBuiltinLibraryModuleURIs extends TemplateVariableResolver {

        public ImportBuiltinLibraryModuleURIs() {
            super("URI_literal", "XQuery: available builtin library module namespace URIs");
        }

        protected String[] resolveAll(TemplateContext context) {
            return ((XQDTTemplateContext)context).getBuiltingLibraryModuleURIs();
        }

    }

    public static class ImportLibraryModuleURIsAndHints extends TemplateVariableResolver {

        public ImportLibraryModuleURIsAndHints() {
            super("URI_and_location_hints", "XQuery: available library module namespace URIs");
        }

        protected String[] resolveAll(TemplateContext context) {
            return ((XQDTTemplateContext)context).getLibraryModuleURIsAndHints();
        }

    }

    public static class ImportSchemaPrefix extends TemplateVariableResolver {

        public ImportSchemaPrefix() {
            super("schema_prefix", "XQuery: schema import prefix");
        }

        protected String[] resolveAll(TemplateContext context) {
            return ((XQDTTemplateContext)context).getSchemaImportPrefix();
        }

    }

    public static class ImportSchemaUriAndHints extends TemplateVariableResolver {

        public ImportSchemaUriAndHints() {
            super("schema_URI_and_hints", "XQuery: schema import uri and location hints");
        }

        protected String[] resolveAll(TemplateContext context) {
            return ((XQDTTemplateContext)context).getSchemaUriAndHints();
        }

    }

}
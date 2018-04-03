f.write("\t\"cluster-config-0.1.dtd\">\n\n");

/*
 * Copyright (C) 2002-2003, Simon Nieuviarts
 */
/***
 * Jonathan: an Open Distributed Processing Environment
 * Copyright (C) 1999 France Telecom R&D
 * Copyright (C) 2002, Simon Nieuviarts
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 *
 * Release: 2.0
 *
 * Contact: jonathan@objectweb.org
 *
 * Author: Kathleen Milsted
 *
 * with contributions from:
 *   Francois Horn
 *   Bruno Dumant
 * 
 */
package org.objectweb.carol.cmi.compiler;
import java.util.Vector;

public class ClusterCompiler {
    private int nbClassArgs;
    private Vector classes;

    public ClusterCompiler() {
    }

    /**
     * Runs the stub compiler.
     *
     * @param args - options and input remote class names to the stub compiler.
     */
    public static void main(String[] args) {
        try {
            ClusterCompiler cc = new ClusterCompiler();
            cc.generate(args);
        } catch (Exception e) {
            e.printStackTrace();
            System.exit(1);
        }
        return;
    }

    public void generate(String[] args) throws Exception {
        ClusterConf cconf = new ClusterConf();
        CompilerContext cmpCtx = new CompilerContext();
        prepare(args, cmpCtx, cconf);

        if (cmpCtx.clusterCfgGen != null) {
            java.io.FileWriter f = new java.io.FileWriter(cmpCtx.clusterCfgGen);
            f.write("<!DOCTYPE cluster-config PUBLIC\n");
            f.write("\t\"\"\n");
            f.write("\t\"cluster-config.dtd\">\n\n");
            f.write("<cluster-config>\n\n");
            for (int i = 0; i < nbClassArgs; i++) {
                String className = (String) classes.elementAt(i);
                if (className == null || className == "") {
                    throw new Exception("Cluster stub compiler error: empty class name");
                }
                f.write("<class>\n\t<name>" + className + "</name>\n\n");
                ClassContext clCtx = new ClassContext(cmpCtx, className);
                MethodContext[] remMths = clCtx.getRemoteMethodContexts();
                for (int j = 0; j < remMths.length; j++) {
                    f.write("\t<method>\n\t\t<signature>");
                    f.write(remMths[j].mth.toString());
                    f.write("</signature>\n\t\t<one-choice/>\n\t</method>\n\n");
                }
                f.write("</class>\n\n");
            }
            f.write("</cluster-config>\n");
            f.close();
        } else {
            for (int i = 0; i < nbClassArgs; i++) {
                String className = (String) classes.elementAt(i);
                if (className == null || className == "") {
                    throw new Exception("Cluster stub compiler error: empty class name");
                }

                ClusterConfigCompiler ccc = new ClusterConfigCompiler(cmpCtx);
                ccc.run(className, cconf);
                ClusterStubCompiler csc = new ClusterStubCompiler(cmpCtx);
                csc.run(className, cconf);
            }
        }
    }

    private void prepare(
        String[] args,
        CompilerContext ctxt,
        ClusterConf cconf)
        throws Exception {
        int len = args.length;

        if (len == 0) {
            usage(ctxt);
            System.exit(0);
        }

        nbClassArgs = 0;
        classes = new Vector();

        int final_index = len - 1;
        for (int i = 0; i < len; i++) {
            if (args[i].equals("-v"))
                ctxt.verbose = true;
            else if (args[i].equals("-verbose"))
                ctxt.verbose = true;
            else if (args[i].equals("-keep"))
                ctxt.keep = true;
            else if (args[i].equals("-keepgenerated"))
                ctxt.keep = true;
            else if (args[i].equals("-noc")) {
                ctxt.compile = false;
                ctxt.keep = true;
            } else if (args[i].equals("-c")) {
                if (i != final_index) {
                    ctxt.javaCompiler = args[++i];
                } else {
                    warning("final -c option incomplete");
                }
            } else if (args[i].equals("-classpath")) {
                if (i != final_index) {
                    ctxt.classPath = args[++i];
                } else {
                    warning("final -classpath option incomplete");
                }
            } else if (args[i].equals("-conf")) {
                if (i != final_index) {
                    cconf.loadConfig(args[++i]);
                } else {
                    warning("final -conf option incomplete");
                }
            } else if (args[i].equals("-genconf")) {
                if (i != final_index) {
                    ctxt.clusterCfgGen = args[++i];
                } else {
                    warning("final -genconf option incomplete");
                }
            } else if (args[i].equals("-d")) {
                if (i != final_index) {
                    ctxt.classDir = args[++i];
                } else {
                    warning("final -d option incomplete");
                }
            } else if (args[i].equals("-s")) {
                if (i != final_index) {
                    ctxt.srcDir = args[++i];
                } else {
                    warning("final -s option incomplete");
                }
            } else if (args[i].startsWith("-")) {
                // ignore other options (for compatibility with rmic)
            } else {
                classes.addElement(args[i]);
                nbClassArgs++;
            }
        }

        if (ctxt.classDir == null)
            ctxt.classDir = ".";
        if (ctxt.srcDir == null)
            ctxt.srcDir = ctxt.classDir;
    }

    private void usage(CompilerContext ctxt) {
        System.out.println("Cluster stub compiler, version " + CompilerContext.version);
        System.out.println(
            "Usage: java "
                + this.getClass().getName()
                + " [options] [class names]");
        System.out.println();
        System.out.println(
            "Options:\n"
                + "  -v, -verbose         print details of what the compiler is doing\n"
                + "  -keep                do not delete generated source files\n"
                + "  -keepgenerated       same as -keep\n"
                + "  -noc                 do not compile generated source files (implies -keep)\n"
                + "  -c <java compiler>   compile generated source files with this java compiler\n"
                + "                       (defaults to javac)\n"
                + "  -classpath <path>    extra classpath passed to -c compiler\n"
                + "  -d <directory>       root directory for generated class files "
                + "                       (defaults to current directory)\n"
                + "  -s <directory>       root directory for generated source files\n"
                + "                       (defaults to -d directory)\n"
                + "  -conf <xml-file>     specify the XML configuration file to use\n"
                + "  -genconf <xml-file>  generate an XML configuration file example\n");
    }

    private static void warning(String str) {
        System.err.println("Cluster stub compiler warning: " + str);
    }

}
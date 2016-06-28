#!/usr/bin/env python
# Writes root analysis library boilerplate code.
# Must run from root of project. Will create a build directory for you.
# Your project should be structured:
#
# ROOT_DIRECTORY
# |_build
# |_source
# |_macros
# |_lib (install directory, i.e. $MYINSTALL)
#
# INSTALL_DIRECTORY
# Project should either install in a local directory "." OR in a
# global install directory such as $MYINSTALL
#

import argparse
import sys
import re
from subprocess import call
import os
import stat

# define a tuple to create a function with a type in C++
def func_type(s):
    '''
    Argument must be of form <C++ type> <function_name>. If the function is
    desired to have arguments, this must be done manually
    '''
    args = []
    args = s.split(',')
    if len(args) != 2:
        raise argparse.ArgumentTypeError("Coordinates must be <TYPE>,<NAME>")
    return (args[0],args[1])

def make_link_def(classes,functions):
    '''
    Argumets are arrays of strings for class names (classes)
    or tuples for function type+name defined in func_type
    
    Generates an array representing a well-formed link-def file.

    Defaults to generating classes without auto-generated dictionaries.
    '''
    linkDefFile = []
    linkDefFile.append("#ifdef __CINT__")
    linkDefFile.append("#pragma link off all classes;")
    linkDefFile.append("#pragma link off all globals;")
    linkDefFile.append("#pragma link off all functions;")
    linkDefFile.append("#pragma link off all nestedclasses;")
    linkDefFile.append("")
    linkDefFile.append("// Put Classes Here, like:")
    linkDefFile.append("// pragma link C++ class ClassName-!; // -! for no dict gen, + for dict gen")
    if classes is not None:
        for class_name in classes:
            linkDefFile.append("#pragma link C++ class %s-!;"%(class_name))
    linkDefFile.append("")
    linkDefFile.append("// Put Functions Here, like:")
    linkDefFile.append("// pragma link C++ function FunctionName;")
    if functions is not None:
        for func_name in functions:
            linkDefFile.append("#pragma link C++ function %s;"%(func_name[1]))
    linkDefFile.append("")
    linkDefFile.append("#endif /* __CINT__ */")
    return linkDefFile

# BE VERY CAREFUL ABOUT SPACING!!!
def make_makefile(classes,functions,lib_name):
    '''
    Argumets are arrays of strings for class names (classes)
    or tuples for function type+name defined in func_type, or
        a simple string, lib_name for the library name
    
    Generates an array representing a well-formed Makefile.
    '''
    compile_list = []
    if classes is not None:
        for class_name in classes:
            compile_list.append(class_name)
    if functions is not None:
        for func_tuple in functions:
            compile_list.append(func_tuple[1])
    sorted_list = sorted(compile_list, key=lambda s: s.lower())
    Makefile = []
    Makefile.append("AUTOMAKE_OPTIONS = foreign")
    Makefile.append("")
    Makefile.append("# these are flags sent to the C++ compiler")
    Makefile.append("# -Wall : I don\'t know what this does")
    Makefile.append("# -Werror: this will treat undefined and unused variables as errors")
    Makefile.append("AM_CXXFLAGS = -Wall -Werror -std=c++0x")
    Makefile.append("")
    Makefile.append("# This flag will build \"testexternals.C\" as a test for the build environment")
    Makefile.append("BUILT_SOURCES = \\")
    Makefile.append("\t"+"testexternals.C")
    Makefile.append("")
    Makefile.append("# This is where we set the directories where we put our neccessary header files")
    Makefile.append("AM_CPPFLAGS = \\")
    Makefile.append("\t"+"-I$(includedir) \\")
    Makefile.append("\t"+"-I$(ROOTSYS)/include")
    Makefile.append("")
    Makefile.append("lib_LTLIBRARIES = \\")
    Makefile.append("\t"+"lib%s.la"%(lib_name))
    Makefile.append("")
    Makefile.append("# Do not install these headers (reference)")
    Makefile.append("# uncomment and manually add headers which should not be installed.")
    Makefile.append("#noinst_HEADERS = \\")
    Makefile.append("#	dontIncludeMe.h")
    Makefile.append("")
    Makefile.append("lib%s_la_LDFLAGS = \\"%lib_name)
    Makefile.append("\t"+"-L$(ROOTSYS)/lib `root-config --libs`")
    Makefile.append("")
    Makefile.append("# Uncomment to add PHENIX offline libraries to build (local systems will")
    Makefile.append("# not have OFFLINE_MAIN defined)")
    Makefile.append("#  -L$(OFFLINE_MAIN)/lib \\")
    Makefile.append("AM_LDFLAGS = \\")
    Makefile.append("\t"+"-L$(OFFLINE_MAIN)/lib \\")
    Makefile.append("\t"+"-L$(ROOTSYS)/lib \\")
    Makefile.append("\t"+"-L$(libdir)")
    Makefile.append("")
    Makefile.append("# These sources are compiled into the final library")
    Makefile.append("lib%s_la_SOURCES = \\"%(lib_name))
    for name in sorted_list:
        Makefile.append("\t"+"%s.C \\"%name)
    Makefile.append("\t"+"DictOutput.cxx")
    Makefile.append("")
    Makefile.append("noinst_PROGRAMS = \\")
    Makefile.append("\t"+"testexternals")
    Makefile.append("")
    Makefile.append("testexternals_LDADD = \\")
    Makefile.append("\t"+"lib%s.la"%(lib_name))
    Makefile.append("")
    # MUST HAVE TABS
    Makefile.append("testexternals.C:")
    Makefile.append("\t"+"echo \"//*** this is a generated file. Do not commit, do not edit\" > $@")
    Makefile.append("\t"+"echo \"int main()\" >> $@")
    Makefile.append("\t"+"echo \"{\" >> $@")
    Makefile.append("\t"+"echo \"\t"+"return 0;\" >> $@")
    Makefile.append("\t"+"echo \"}\" >> $@")
    Makefile.append("")
    Makefile.append("# This is where the dictionary file is generated")
    Makefile.append("DictOutput.cxx: \\")
    for name in sorted_list:
        Makefile.append("\t"+"%s.h \\"%name)
    # MUST HAVE TABS
    Makefile.append("\t"+"%sLinkDef.h"%lib_name)
    Makefile.append("\t"+"rootcint -f $@ -c $(DEFAULT_INCLUDES) $(AM_CPPFLAGS) $^")
    Makefile.append("")
    Makefile.append("clean-local:")
    # MUST HAVE TABS
    Makefile.append("\t"+"rm -f *Dict.*")
    return Makefile

def make_configure_ac():
    '''
    Creates boilerplate configre.ac file
    '''
    configure_ac = []
    configure_ac.append("AC_INIT")
    configure_ac.append("AC_CONFIG_SRCDIR(autogen.sh)")
    configure_ac.append("")
    configure_ac.append("AM_INIT_AUTOMAKE(packagename, 1.00)")
    configure_ac.append("")
    configure_ac.append("AC_PROG_CXX(CC g++)")
    configure_ac.append("AC_ENABLE_STATIC(no)")
    configure_ac.append("\t"+"AC_PROG_LIBTOOL")
    configure_ac.append("")
    configure_ac.append("AC_OUTPUT(Makefile)")
    return configure_ac

def make_class_source(class_name):
    """Makes class source files"""
    class_source = []
    class_source.append("#include \"%s.h\""%class_name)
    class_source.append("#include <iostream>")
    class_source.append("")
    class_source.append("%s::%s() {"%(class_name,class_name))
    class_source.append("  std::cout << \"%s instantiated at \" << this << std::endl;"%class_name)
    class_source.append("}")
    class_source.append("")
    class_source.append("%s::~%s() {"%(class_name,class_name))
    class_source.append("  std::cout << \"Destroying %s from \" << this << std::endl;"%class_name)
    class_source.append("}")
    return class_source

def make_class_header(class_name):
    """Makes a class header files"""
    class_header = []
    class_header.append("class %s {"%class_name)
    class_header.append("  public:")
    class_header.append("    %s();"%class_name)
    class_header.append("    ~%s();"%class_name)
    class_header.append("  private:")
    class_header.append("};")
    return class_header

def make_function_source(type_name,func_name):
    """Makes a source file for func_name of type type_name"""
    function_source = []
    function_source.append("#include \"%s.h\""%func_name)
    function_source.append("#include<iostream>")
    function_source.append("")
    function_source.append("%s %s(){"%(type_name,func_name))
    function_source.append("  std::cout << \"Running %s\" << std::endl;"%func_name)
    function_source.append("  return 0;")
    function_source.append("}")
    return function_source

def make_function_header(type_name,func_name):
    """Makes a header file for func_name of type type_name"""
    function_header = []
    function_header.append("%s %s();"%(type_name,func_name))
    return function_header

def make_test_macro(classes,functions,lib_name):
    """
    Makes a root macro to test classes and functions.
    Expects lib to be in $PATH
    """
    test_macro = []
    test_macro.append("int Run_Tests(){")
    test_macro.append("  gSystem->Load(\"lib%s.so\");"%(lib_name))
    if classes is not None:
        for call in classes:
            test_macro.append("  %s %s_instance;"%(call,call))
    if functions is not None:
        for call in functions:
            test_macro.append("  %s();"%(call[1]))
    test_macro.append("  return 0;")
    test_macro.append("}")
    return test_macro

def make_autogen_sh():
    """Creates autogen.sh file"""
    autogen_sh = []
    autogen_sh.append("#!/bin/sh")
    autogen_sh.append("srcdir=`dirname $0`")
    autogen_sh.append("test -z \"$srcdir\" && srcdir=.")
    autogen_sh.append("")
    autogen_sh.append("(cd $srcdir; aclocal -I /usr/share;\\")
    autogen_sh.append("libtoolize --force; automake -a --add-missing; autoconf)")
    autogen_sh.append("")
    autogen_sh.append("$srcdir/configure  \"$@\"")
    return autogen_sh

def make_clean_file(lib_name,source_dir,build_dir,install_dir):
    """
    Creates file to clean up after building Takes lib_name as argument, which
    is transformed into the library name installed cannonically into $MYINSTALL
    path.

    Follows your build and source directory preferences.
    """
    clean_file = []
    clean_file.append("#! /bin/sh")
    clean_file.append("rm -rfv %s/config.status"%build_dir)
    clean_file.append("rm -rfv %s/Makefile"%build_dir)
    clean_file.append("rm -rfv %s/libtool"%build_dir)
    clean_file.append("rm -rfv %s/config.log"%build_dir)
    clean_file.append("rm -rfv %s/testexternals.C"%build_dir)
    clean_file.append("rm -rfv %s/DictOutput.h"%build_dir)
    clean_file.append("rm -rfv %s/DictOutput.cxx"%build_dir)
    clean_file.append("rm -rfv %s/.deps"%build_dir)
    clean_file.append("rm -rfv %s/.libs"%build_dir)
    clean_file.append("rm -rfv %s/aclocal.m4"%source_dir)
    clean_file.append("rm -rfv %s/autom4te.cache"%source_dir)
    clean_file.append("rm -rfv %s/missing"%source_dir)
    clean_file.append("rm -rfv %s/install-sh"%source_dir)
    clean_file.append("rm -rfv %s/config.sub"%source_dir)
    clean_file.append("rm -rfv %s/config.guess"%source_dir)
    clean_file.append("rm -rfv %s/depcomp"%source_dir)
    clean_file.append("rm -rfv %s/configure"%source_dir)
    clean_file.append("rm -rfv %s/ltmain.sh"%source_dir)
    clean_file.append("rm -rfv %s/Makefile.in"%source_dir)
    clean_file.append("rm -rfv %s/compile"%source_dir)
    clean_file.append("rm -vf lib/*")
    clean_file.append("rm -vf %s/lib/lib%s*"%(install_dir,lib_name))
    return clean_file

def dump_files(file_dict,file_suffix,directory,overwrite=False):
    """
    Dump a dictionary of files, indexed:
    <FILENAME>:<ARRAY OF LINES IN FILE>
    to directory dir

    Must provide the file_file suffix, and whether or not to overwrite the
    file, if it exists.
    """
    for name,file_lines in file_dict.iteritems():
        dump_name = "%s/%s%s"%(directory,name,file_suffix)
        file_exists = False
        if os.path.isfile(dump_name):
            file_exists = True
        if not file_exists:
            print "Creating new file:",dump_name
            with open(dump_name,'w') as out:
                for line in file_lines:
                    out.write("%s\n"%line)
        elif file_exists and overwrite:
            print "Creating new file:",dump_name
            with open(dump_name,'w') as out:
                for line in file_lines:
                    out.write("%s\n"%line)
        else:
            print "%s%s"%(name,file_suffix),'exists, but you have not explicity asked to overwrite it with a new file.'
    return 0

def main():
    parser = argparse.ArgumentParser(description="Create a compiled root project library for ROOT 5.34")
    parser.add_argument('-c','--classes',
            nargs='*',
            help='List the names of the classes to add to the project')
    parser.add_argument('-f','--functions',
            nargs='*',
            help='List the function and type as:<TYPE>,<FUNCTION NAME>',
            type = func_type)
    parser.add_argument('-l','--lib_name',
            help='Give a name for the library',
            type=str,
            required=True)
    parser.add_argument('-s','--source_dir',
            help='Give a path for the source directory',
            required=True)
    parser.add_argument('-m','--macros_dir',
            help='Give a path for the macros directory',
            required=True)
    parser.add_argument('-b','--build_dir',
            help='Give a path for the build directory',
            required=True)
    parser.add_argument('-i','--install_dir',
            help='Give a path for your library installation directory',
            required=True)
    parser.add_argument('-o','--overwrite',
            help='Forces all generated files to overwrite existing files. Otherwise, only new classes and functions are written. Other boilerplate code that is not generally modified by the user is also regenerated (i.e. autogen.sh, Makefile.am, etc.)',
            required=False,
            action = "store_true")
    args = parser.parse_args()

    classes = args.classes
    functions = args.functions
    lib_name = args.lib_name
    macros_dir = args.macros_dir
    source_dir = args.source_dir
    build_dir = args.build_dir
    install_dir = args.install_dir
    overwrite_toggle = False
    if args.overwrite:
        overwrite_toggle = True
    if source_dir[-1] == "/":
        source_dir = source_dir[:-1]
    if macros_dir[-1] == "/":
        macros_dir = macros_dir[:-1]
    if build_dir[-1] == "/":
        build_dir = build_dir[:-1]
    if install_dir[-1] == "/":
        install_dir = install_dir[:-1]

    if classes is None and functions is None:
        raise argparse.ArgumentTypeError(
            'Must specfiy at least one class or function with -c/--classes or -f/--functions'
            )
        return 1
   
    class_sources = {}
    class_headers = {}
    function_sources = {}
    function_headers = {}
    if classes is not None:
        print 'Building with classes:',classes
        for class_name in classes:
            class_sources[class_name] = make_class_source(class_name)
            class_headers[class_name] = make_class_header(class_name)
    if functions is not None:
        print 'Building with functions:',functions
        for func in functions:
            function_sources[func[1]] = make_function_source(func[0],func[1])
            function_headers[func[1]] = make_function_header(func[0],func[1])

    print "If you specified function return type other then the built-in type primatives, your must edit the source file to add an appropriate return value, if you want your code to compile."
    # Create the files for the project
    test_macro = {}
    autogen_sh = {}
    Makefile = {}
    configure_ac = {}
    linkDefFile = {}
    clean_file = {}
    linkDefFile[lib_name+'LinkDef'] = make_link_def(classes,functions)
    Makefile["Makefile"] = make_makefile(classes,functions,lib_name)
    configure_ac["configure"] = make_configure_ac()
    test_macro["Run_Tests"] = make_test_macro(classes,functions,lib_name)
    autogen_sh["autogen"] = make_autogen_sh()
    clean_file["fullClean"] = make_clean_file(lib_name,source_dir,build_dir,install_dir)

    # Dump to the various directories, creating them if necessary
    if not os.path.exists(source_dir):
        os.makedirs(source_dir)
    if not os.path.exists(macros_dir):
        os.makedirs(macros_dir)
    if not os.path.exists(build_dir):
        os.makedirs(build_dir)
    if not os.path.exists(install_dir):
        os.makedirs(install_dir)

    dump_files(class_sources,'.C',source_dir,overwrite_toggle)
    dump_files(class_headers,'.h',source_dir,overwrite_toggle)
    dump_files(function_sources,'.C',source_dir,overwrite_toggle)
    dump_files(function_headers,'.h',source_dir,overwrite_toggle)
    dump_files(Makefile,'.am',source_dir,True)
    dump_files(linkDefFile,'.h',source_dir,True)
    dump_files(autogen_sh,'.sh',source_dir,True)
    dump_files(configure_ac,'.ac',source_dir,True)
    dump_files(test_macro,'.C',macros_dir,True)
    dump_files(clean_file,'.sh','.',True)

    st = os.stat('fullClean.sh')
    os.chmod('fullClean.sh', st.st_mode | stat.S_IEXEC)
    st = os.stat('%s/autogen.sh'%source_dir)
    os.chmod('%s/autogen.sh'%source_dir, st.st_mode | stat.S_IEXEC)
    return 0

if __name__ == '__main__':
    sys.exit(main())


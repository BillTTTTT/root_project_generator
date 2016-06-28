# C++ Analysis Library Generation With Linking to ROOT
This program will generate an arbitrary number of functions, classes, LinkDef,
Makefile.am, autogen, etc, necessary to create a standalone analysis library
which can then be loaded and executed in a ROOT macro.

## Step 0
Read the documentation, email the author, michael.beaumier@gmail.com afterwards,
if you have questions.

## Step 1

Clone the repository:

<pre>
git clone https://github.com/Jollyhrothgar/root_project_generator
</pre>

## Step 2
### Example Usage

Execute the project generation command:
### Project Generation Example
<pre> 
./make_project.py --build_dir build --source_dir source --macros_dir \
macros -classes OneClass AnotherClass ThirdClass --functions int,FirstFunction \
double,SecondFunction --lib_name MyLibrary --install_dir $MYINSTALL 
</pre>

An analysis project will be generated in your working directory. The structure
will be as follows:

### Generated Project Structure Example
<pre>
PROJECT DIRECTORY
    fullClean.sh (run from PROJECT DIRECTORY to clean out all additional files
                 generated from building the project. This can be moved into the
                 Makefile, under 'make clean', if desired.)
    source/
        OneClass.C
        OneClass.h
        AnotherClass.C
        AnotherClass.h
        FirstFunction.C (returns an int)
        FirstFunction.h (returns an int)
        SecondFunction.C (returns a double)
        SecondFunction.h (returns a double)
        Makefile.am
        configure.ac
        MyLibraryLinkDef.h
        autogen.sh
    macros/
        Run_Tests.C        
    build/
</pre>

The default behavior in LinkDef is to *not* generate streamer libraries for
classes. You must manually edit linkdef to add automatic streamer generation for
your classes in order to enable writing a class to a root file. I find this
behavior to be somewhat buggy if you use the standard template library in your
classes (even with adding those STL objects to your linkdef), so I prefer to
leave it out.

Note, you can use shorter versions of each CLI flag - just type "make_project.py
-h"

You can call the classes and directories whatever you want. You can overlap
directories as well. Some people prefer to build in their source directory. In
that case just do: -source_dir source --build_dir source, this will put
everything in a directory called 'source'. This only effects where the fullClean.sh
script looks to delete unnecessary build files, if you want to clean up your
work area or re-compile.

## Step 3 

Go to your build directory, and generate the makefiles for your project with:

<pre>
../source/autogen.sh --prefix=$MYINSTALL
</pre>

## Step 4
While still in your build directory, compile your project with:
<pre>
make 
</pre>

And install your project libraries with:
<pre>
make install
</pre>

## Step 5
Now, go to the macros directory, and test the project with:

<pre>
root -l Run_Tests.C
</pre>

You should see a series of outputs confirming that each one of your functions
and classes was instantiated.

## Next Steps

You can now modify your classes and functions as you wish - add member functions
to classes to abstract data types, add arguments to functions, etc. You can
start the 'real work'!

## Requirements

You should have the path variable $MYINSTALL defined. It points to a directory
on your computer containing "$MYINSTALL/lib". This is where all your compiled
libraries should be. $MYINSTALL should be added to your $PATH variable, so that
you can use your root libraries from any location on your system.

In bash, (i.e. ~/.bashrc), this would look like:

<pre>
export MYINSTALL=/direct/phenix+u/workarea/beaumim/install
export PATH=$PATH:$MYINSTALL
</pre>

In cshell, (i.e. ~/.cshrc), this would look like:

<pre>
setenv MYINSTALL /direct/phenix+u/beaumim/workarea/install
set path = ($MYINSTALL/bin $path)
</pre>

If you use this script on a cluster, you will need to modify the autogen.sh file
to point to wherever libtoolize is installed (for PHENIX, its in $OFFLINE_MAIN).

You also need to have ROOT 5.34 installed. Running an earlier version should
also work, assuming that it supports CINT, and uses the Dict system of managing
building streamers for interactive use.

This will not work for ROOT 6, it will need to be modified. The C++ stuff will
be just fine, but ROOT 6 does not handle dictionary generation (needed to run
your functions and classes interactively in CINT) the same way as ROOT 5.34.

## Additional Documentation

Lists of classes and functions are white-space separated (i.e.):

* --classes foo bar baz
* --functions int,foo float,bar bool,baz

The only optional argument is --overwrite. Add this to the argument list if and
only if you wish to overwrite classes and functions with the blank template used
in this program. This way, you can add new classes or functions to your project
and get an automatically generated makefile and LinkDef for free.

Note that when you use this program to add to an existing project, you must
completely list all of the classes and functions that you are using in the
arguments to this program - so maybe you might want to generate the arguments
automatically.

This program probably won't work if you try to use it on a project that was
generated manually.

This program doesn't deal with multiple functions in one file, but this is
totally allowed in C++, and encouraged if there is a design reason for it.

Remember that the purpose of this software is to get you started, so if you do
too much more with it than getting the boilerplate stuff written, you might not
get the behavior you're expecting.

If you wish to run this software on RCF (if you're a PHENIX analyzer) you must
change your autogen.sh file to read as follows:

### PHENIX autogen.sh
<pre>
<code>
#!/bin/sh
srcdir=`dirname $0`
test -z "$srcdir" && srcdir=.

(cd $srcdir; aclocal -I ${OFFLINE_MAIN}/share;\
 libtoolize --force; automake -a --add-missing; autoconf)

$srcdir/configure "$@"
</code>
</pre>
Since PHENIX puts  its libtoolize and autotools installation in <pre>$OFFLINE_MAIN</pre>.

The standard -h output: 

<pre>
  -h, --help            show this help message and exit
  -c [CLASSES [CLASSES ...]], --classes [CLASSES [CLASSES ...]]
                        List the names of the classes to add to the project
  -f [FUNCTIONS [FUNCTIONS ...]], --functions [FUNCTIONS [FUNCTIONS ...]]
                        List the function and type as:<TYPE>,<FUNCTION NAME>
  -l LIB_NAME, --lib_name LIB_NAME
                        Give a name for the library
  -s SOURCE_DIR, --source_dir SOURCE_DIR
                        Give a path for the source directory
  -m MACROS_DIR, --macros_dir MACROS_DIR
                        Give a path for the macros directory
  -b BUILD_DIR, --build_dir BUILD_DIR
                        Give a path for the build directory
  -i INSTALL_DIR, --install_dir INSTALL_DIR
                        Give a path for your library installation directory
  -o, --overwrite       Forces all generated files to overwrite existing
                        files. Otherwise, only new classes and functions are
                        written. Other boilerplate code that is not generally
                        modified by the user is also regenerated (i.e.
                        autogen.sh, Makefile.am, etc.)
</pre>

## Standard Disclaimer

Any project you're working on should implement a frequent back up strategy. You
should commit your code edits frequently to a repository like github. If you
overwrite your whole project by using this tool, and you don't have a recent
back up, that's your fault.  I've tried to make sure this can't happen unless
you force it, but there may be bugs, so please proceed with caution.

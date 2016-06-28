# Boilerplate code for compiled funcitons and classes linked to ROOT

## 1

Clone the repository

## 2

Run the script (example):

<code> ./make_project.py --build_dir build --source_dir source --macros_dir
macros -classes OneClass AnotherClass ThirdClass --functions int,FirstFunction
double,SecondFunction --lib_name MyLibrary --install_dir $MYINSTALL 
</code>

Note, you can use shorter versions of each CLI flag - just type "make_project.py
-h"

This generates your project area with separated build, source and macros
directories. Run it, and see how your project is structured. You also get a
Makefile and a cleaning script as well. 

## 3 

Go to your build directory, and generate the makefiles for your project with:

<code>
../source/autogen --prefix=$MYINSTALL
</code>

## 4
Compile and install your project with:

<code>
make install
</code>

## 5
Now, go to the macros directory, and test the project with:

<code>
root -l Run_Tests.C
</code>

You should see a series of outputs confirming that each one of your functions
and classes was instantiated.

## Next Steps

You can now modify your classes and functions as you wish - add member functions
to classes to abstract data types, add arguments to functions, etc. Modify as you wish.

## Requirements

You should have the path variable $MYINSTALL defined. It points to a directory
on your computer containing "$MYINSTALL/lib". This is where all your compiled
libraries should be. $MYINSTALL should be added to your $PATH variable, so that
you can use your root libraries from any location on your system.

If you use this script on a cluster, you will need to modify the autogen.sh file
to point to wherever libtoolize is installed (for PHENIX, its in $OFFLINE_MAIN).

You also need to have ROOT 5.34 installed. Running an earlier version should
also work, assuming that it supports CINT, and uses the Dict system of managing
building streamers for interactive use.

This will not work for ROOT 6, it will need to be modified. The C++ stuff will
be just fine, but ROOT 6 does not handle dictionary generation (needed to run
your funcitons and classes interactively in CINT) the same way as ROOT 5.34.

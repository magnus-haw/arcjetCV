# Build the documentation locally (UNIX only)

The arcjetCV documentation is generated automatically using Sphinx, compiled online by ReadTheDocs
at every main branch new commit. The main commands that tell sphinx how to compile the documentation are inside the 
doc/source/conf.py file, which is called by the Makefile, whereas the main layout of the different webpages is 
controlled by the index.rst file. 

In order to compile the documentation locally, you need to install a new conda environment as: 

    conda env create --file sphinx_env.yml
    conda activate sphinx_rtd
    make html

This creates the documentation inside the doc/build/html folder (just double click the index.html file to open it in a browser).
Alternatively, the "make latex" command compiles a pdf file, which serves as the user-manual. Finally, you can use
"make clean" to clear previous builds.

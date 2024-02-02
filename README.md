# PSyACC: tools for automating OpenACC GPU porting efforts using PSyclone

## Introduction

Before introducing PSyACC, we should introduce
[PSyclone](https://github.com/stfc/PSyclone). PSyclone is a domain-specific compiler and
code transformation tool for earth system codes written in Fortran. In code
transformation mode (which is of main interest here), PSyclone can be used to read in
Fortran source code, along with a user-defined *transformation script* (written in
Python), which describes modifications to be made to the source code. With these two
ingredients, PSyclone converts the source code to its internal *intermediate
representation*, applies the transformations, and then writes out the modified code.

One key example of a transformation to be applied to the input code is to insert
[OpenACC](https://www.openacc.org) directives and clauses. Compiled under
[NVHPC](https://developer.nvidia.com/hpc-sdk), the OpenACC syntax tells the compiler how
to parallelise the code on Nvidia GPUs. This is the transformation of primary interest
as far as PSyACC goes.

PSyACC is a Python package which provides various helper functions for PSyclone,
particularly with regards to writing transformation scripts for OpenACC GPU porting.
Amongst other things, PSyACC provides functionality for:
 * simplifying tree traversal in PSyclone's intermediate representation,
 * analysing the structure of loops and loop nests,
 * applying OpenACC `kernels` and `loop` directives,
 * applying OpenACC clauses to `loop` directives,
 * querying `Node` types.

## Installation

To install PSyACC, you will first need a Python virtual environment, with Python version
at least 3.10. (On the Met Office VDI system, you can load an up-to-date Python version
with `module load scitools`.) Check your Python version with `python3 --version`.

Starting from the location where you want to install PSyACC and PSyclone (such as
`${HOME}/software`), first create your virtual environment:
```
python3 -m venv psyclone-venv
```
and activate it
```
source psyclone-venv/bin/activate
```
You can check the Python version again as a sanity check (and `module unload scitools`
if you wish).

Next, clone both of the repositories:
```
git clone git@github.com:stfc/PSyclone.git
git clone git@github.com:MetOffice/psyacc.git
```
Note that you will need to use the SSH protocol because PSyACC is not publicly visible.

Install PSyclone either by following the instructions in that repository or simply with
```
cd PSyclone
python3 -m pip install -r requirements.txt
python3 -m pip install -e .
cd ..
```

To install PSyACC, navigate to the repository and use the `make install` recipe:
```
cd psyacc
make install
```
This will install PSyACC's other requirements, the package itself, and set up
[`pre-commit`](https://pre-commit.com) hooks for consistent formatting.

## Developer notes

Contributions are very welcome! However, please read PSyACC's
[Coding Practices](https://github.com/MetOffice/psyacc/wiki/Coding-practices) before
commencing development work.

When you make your first contribution, make sure to add yourself to the
[contributors list](./CONTRIBUTORS.md).

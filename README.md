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

## General user instructions

Instructions for installing PSyACC and building and viewing its documentation may be found on the [Wiki page](https://github.com/MetOffice/psyacc/wiki#general-users).

## Developer notes

Contributions are very welcome! However, please read PSyACC's
[Coding Practices](./wiki/Coding-practices) before commencing development work.

When you make your first contribution, make sure to add yourself to the
[contributors list](./CONTRIBUTORS.md).

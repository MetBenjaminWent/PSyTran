##############################################################################
# Copyright (c) 2025,  Met Office, on behalf of HMSO and Queen's Printer
# For further details please refer to the file LICENCE.original which you
# should have received as part of this distribution.
##############################################################################
'''
Top level function(s) intended to be callable by
PSyclone Transmute global and override functions.
Override classes to be used to change some settings in transmute
functions. Override scripts will set their own versions of this
object.
'''

from __future__ import print_function
from family import (update_ignore_list,
                    check_omp_ancestry,
                    span_parallel,
                    validate_rules,
                    try_transformation)
from psyclone.transformations import OMPLoopTrans
from psyclone.psyir.nodes import Loop

__all__ = [
    "TagOverride",
    "OverridesClass",
    "try_loop_omp_pardo"
]

# Setup transformations and their properties
# OMP parallel do transformation
omp_transform_par_do = OMPLoopTrans(omp_schedule="static",
                                    omp_directive="paralleldo")
omp_transform_do = OMPLoopTrans(omp_schedule="static",
                                omp_directive="do")


class TagOverride:
    '''
    Class to store combined metadata of an ignore list associated with a
    loop tag.
    This data will be provided by a global.py or file override which calls
    global. These will need to be found by user and manually added to this
    object in global.py or file override for the transmute method.
    '''
    def __init__(
                self,
                loop_tag,
                options=None
                ):
        '''
        Initialise TagOverride with a loop tag and an options list
        '''
        # Validation checks into class
        if options is None:
            options = {}
        if not isinstance(options, dict):
            raise TypeError(f"Expected a options dict, not \
                            '{type(options)}'.")

        self._loop_tag = loop_tag
        self._options = options

    # Getters
    def get_loop_tag(self):
        '''
        Return the loop tag of the class, name of the loop index.
        Name tag has been set by Loop.set_loop_type_inference_rules
        in the global script.
        '''
        return self._loop_tag

    def options(self):
        '''
        Return the options list of the class
        '''
        return self._options


class OverridesClass:
    '''
    Class to act as a full override for the global script.
    This will adjust settings used functions later on.
    This will contain a list of specific overrides for given loop tags.
    '''
    def __init__(self,
                 loop_max_qty=None,
                 tag_overrides=None
                 ):

        # Validation checks into class
        # if function_overrides_dict == None:
        #     function_overrides_dict = {}
        if tag_overrides is None:
            self._tag_overrides = []
        else:
            for override in tag_overrides:
                if not isinstance(override, TagOverride):
                    raise TypeError(f"Expected a tag_override object, not \
                                    '{type(override)}'.")
            # Pass through the list of accepted loop tag overrides
            self._tag_overrides = tag_overrides

        # setup default values for object properties
        self._loop_max_qty = 12

        # Override the defaults with provided values
        if loop_max_qty:
            self._loop_max_qty = loop_max_qty

    # Getters
    def get_loop_max_qty(self):
        '''
        Return the loop max value for number of loops that a parallel section
        will span over in span_parallel.
        '''
        return self._loop_max_qty

    def get_tag_overrides(self):
        '''
        A list of TagOverride objects. Set the loop_tag which the object is for
        and it's associated options list for the transformation.
        '''
        return self._tag_overrides


def try_loop_omp_pardo(loop_node,
                       override_class
                       ):
    '''
    Called inside a loop running through the files schedule, and processing
    each loop one at a time, which occurs here.

    First it checks if a list of ignore dependencies objects has been provided

    Then it spans some parallel regions

    Then it adds in either parallel do or do clause to the loop node

    OpenMP ancestry for the loop is checked where relevant.

    :arg loop_node: The Loop node to transform
    :type loop_node: :py:class:`Loop`
    :arg override_class:  Class containing a list of override classes to check
                          against for an ignore_dependencies_for list, etc.
                          Also contains master override settings.
    :type override_class: :py:class:`override_class`
    '''

    if not isinstance(loop_node, Loop):
        raise TypeError(f"Expected a loop node \
                        '{type(Loop)}'.")

    if not isinstance(override_class, OverridesClass):
        raise TypeError(f"Expected a tag_override object, not \
                        '{type(override_class)}'.")

    # options dict setup
    options = {}

    # If there is an loop_tag_overrides_list, work through the objects
    # and update the options ignore_dependencies_for with tags where the
    # loop tags match
    options = update_ignore_list(loop_node, options, override_class)

    # Check if the ancestry for a omp_transform_par_do and a
    # omp_transform_do transformation is correct for the given node
    # We expect there to be no parallel ancestry for either transformation
    # when we are attempting to span a parallel region.
    if (not check_omp_ancestry(loop_node, omp_transform_par_do) or
            check_omp_ancestry(loop_node, omp_transform_do)):
        span_parallel(loop_node, override_class.get_loop_max_qty())

    # Given whether the loop is now currently in a parallel section
    # change the OMP transformation to the correct option.
    # Either parallel do, if there is no parallel region above
    # or do
    # check_omp_ancestry for the omp_transform_do will return false if there
    # is a parallel section for a omp_transform_do transformation
    # default transformation will be parallel do
    if not check_omp_ancestry(loop_node, omp_transform_do):
        transformation = omp_transform_do
    else:
        transformation = omp_transform_par_do

    # Check the ability to transform given OMP ancestry
    if not check_omp_ancestry(loop_node, transformation):

        loop_continue, options = validate_rules(loop_node, options)

        # Given the rule checks above, if they are all clear
        if loop_continue:
            # Try the transformation - either a OMP parallel do or do
            error = try_transformation(loop_node, transformation, options)
            print(error)

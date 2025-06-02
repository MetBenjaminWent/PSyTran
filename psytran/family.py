# (C) Crown Copyright 2023, Met Office. All rights reserved.
#
# This file is part of PSyTran and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

r"""
This module provides functions for determining the ancestors and descendents of
:py:class:`Node`\s, as well as for querying their existence and nature.
"""

from psyclone.psyir.nodes import Loop, Node

__all__ = [
    "get_descendents",
    "get_ancestors",
    "get_children",
    "has_descendent",
    "has_ancestor",
    "child_valid_trans",
    "check_omp_ancestry",
    "get_last_child_shed",
    "get_specific_children",
    "span_check_loop",
    "span_parallel",
    "strip_index",
    "string_match_ref_var",
    "try_transformation",
    "try_validation",
    "update_ignore_list",
    "validate_rules_para",
    "validate_rules",
    "work_out_collapse_depth"
]


def get_descendents(
    node, node_type=Node, inclusive=False, exclude=(), depth=None
):
    """
    Get all ancestors of a Node with a given type.

    :arg node: the Node to search for descendents of.
    :type node: :py:class:`Node`
    :kwarg node_type: the type of node to search for.
    :type node_type: :py:class:`type`
    :kwarg inclusive: if ``True``, the current node is included.
    :type inclusive: :py:class:`bool`
    :kwarg exclude: type(s) of node to exclude.
    :type exclude: :py:class:`bool`
    :kwarg depth: specify a depth for the descendents to have.
    :type depth: :py:class:`int`

    :returns: list of descendents according to specifications.
    :rtype: :py:class:`list`
    """
    assert isinstance(node, Node), f"Expected a Node, not '{type(node)}'."
    assert isinstance(
        inclusive, bool
    ), f"Expected a bool, not '{type(inclusive)}'."
    assert isinstance(node_type, tuple) or issubclass(node_type, Node)
    if depth is not None:
        assert isinstance(depth, int), f"Expected an int, not '{type(depth)}'."
    return [
        descendent
        for descendent in node.walk(node_type, depth=depth)
        if not isinstance(descendent, exclude)
        and (inclusive or descendent is not node)
    ]


def get_ancestors(
    node, node_type=Loop, inclusive=False, exclude=(), depth=None
):
    """
    Get all ancestors of a Node with a given type.

    :arg node: the Node to search for ancestors of.
    :type node: :py:class:`Node`
    :kwarg node_type: the type of node to search for.
    :type node_type: :py:class:`type`
    :kwarg inclusive: if ``True``, the current node is included.
    :type inclusive: :py:class:`bool`
    :kwarg exclude: type(s) of node to exclude.
    :type exclude: :py:class:`bool`
    :kwarg depth: specify a depth for the ancestors to have.
    :type depth: :py:class:`int`

    :returns: list of ancestors according to specifications.
    :rtype: :py:class:`list`
    """
    assert isinstance(node, Node), f"Expected a Node, not '{type(node)}'."
    assert isinstance(
        inclusive, bool
    ), f"Expected a bool, not '{type(inclusive)}'."
    assert isinstance(node_type, tuple) or issubclass(node_type, Node)
    if depth is not None:
        assert isinstance(depth, int), f"Expected an int, not '{type(depth)}'."
    ancestors = []
    node = node.ancestor(node_type, excluding=exclude, include_self=inclusive)
    while node is not None:
        ancestors.append(node)
        node = node.ancestor(node_type, excluding=exclude)
    if depth is not None:
        ancestors = [a for a in ancestors if a.depth == depth]
    return ancestors


def get_children(node, node_type=Node, exclude=()):
    """
    Get all immediate descendents of a Node with a given type, i.e., those at
    the next depth level.

    :arg node: the Node to search for descendents of.
    :type node: :py:class:`Node`
    :kwarg node_type: the type of node to search for.
    :type node_type: :py:class:`type`
    :kwarg exclude: type(s) of node to exclude.
    :type exclude: :py:class:`bool`

    :returns: list of children according to specifications.
    :rtype: :py:class:`list`
    """
    assert isinstance(node, Node), f"Expected a Node, not '{type(node)}'."
    if not isinstance(node_type, tuple):
        issubclass(node_type, Node)
        node_type = (node_type,)
    children = [
        grandchild
        for child in node.children
        for grandchild in child.children
        if isinstance(grandchild, node_type)
        and not isinstance(grandchild, exclude)
    ]
    return children


def has_descendent(node, node_type, inclusive=False):
    """
    Check whether a Node has a descendent node with a given type.

    :arg node: the Node to check for descendents of.
    :type node: :py:class:`Node`
    :arg node_type: the type of node to search for.
    :type node_type: :py:class:`type`
    :kwarg inclusive: if ``True``, the current node is included.
    :type inclusive: :py:class:`bool`

    :returns: ``True`` if there are descendents meeting specifications, else
        ``False``.
    :rtype: :py:class:`bool`
    """
    return bool(
        get_descendents(node, inclusive=inclusive, node_type=node_type)
    )


def has_ancestor(node, node_type=Loop, inclusive=False, name=None):
    """
    Check whether a Node has an ancestor node with a given type.

    :arg node: the Node to check for ancestors of.
    :type node: :py:class:`Node`
    :kwarg node_type: the type of node to search for.
    :type node_type: :py:class:`type`
    :kwarg inclusive: if ``True``, the current node is included.
    :type inclusive: :py:class:`bool`
    :kwarg name: check whether the node has an ancestor with a particular name.
    :type name: :py:class:`str`

    :returns: ``True`` if there are ancestors meeting specifications, else
        ``False``.
    :rtype: :py:class:`bool`
    """
    ancestors = get_ancestors(node, inclusive=inclusive, node_type=node_type)
    if name:
        return any(ancestor.variable.name == name for ancestor in ancestors)
    return bool(ancestors)


def child_valid_trans(check_current_node):
    '''
    We want to see if the loop could be parallelised with a
    pardo transformation. Given we are going all the way down
    the tree in the wider loop, we have to do this manually here.
    We check the current loop to see if it can be pardo.
    Checks are standard checks (ignoring OMP ancestry
    as this is done at the top level).
    '''
    valid_loop = False

    # Setup
    options = {}

    loop_child_list = get_specific_children(check_current_node)

    # If there is a list of loops
    if loop_child_list:
        # If the current node is a loop, we want to check it to, first
        if isinstance(check_current_node, Loop):
            loop_child_list.insert(0, check_current_node)

        for loop in loop_child_list:
            # check the validate rules list specific for parallel sections
            loop_continue, options = validate_rules_para(check_current_node,
                                                         options)

            if loop_continue:
                # Call the validation instead
                error = try_validation(loop, omp_transform_par_do, options)

                # IF there are no errors, continue, otherwise exit
                if len(error) == 0 or error == "":
                    valid_loop = True
                else:
                    valid_loop = False
                    break

    # Return number of children spanning over also
    # Used in in rule for no of loops spanning over
    if valid_loop:
        ret_child_loop_qty = len(loop_child_list)
    else:
        ret_child_loop_qty = 0

    return valid_loop, ret_child_loop_qty


def check_omp_ancestry(
    node_target: Node,
    transformation: Transformation,
):
    '''
    Check the OMP ancestry, both for spanning parallel or
    parallel do. Returns True, which will stop future transformations
    from occurring.
    If the transformation to apply is a simple OMP do then we instead
    expect the presence of a parallel region, and therefore will
    return false.
    Due to psyir tree returning sibling loop ancestors during psyclone,
    also check the path to each OMP parallel.
    If there is a path to both, that is incorrect.
    See the list of exceptions below.
    '''

    # Store whether there is a current Loop and a
    # OMP Parallel, Parallel Do or Do ancestor
    omp_ancestor_par = node_target.ancestor(OMPParallelDirective)
    omp_ancestor_par_do = node_target.ancestor(OMPParallelDoDirective)
    omp_ancestor_do = node_target.ancestor(OMPDoDirective)

    # There seems to be an issue in PSyclone where the presence of an OMP
    # parallel section.
    # Under the same parent node is causing a little confusion.
    # The paths allow us to check index references for closeness
    # Given a certain circumstance we can iron out the confusion
    # Needs to be wrapped in a try else it fails
    try:
        path_to_omp_par = node_target.path_from(omp_ancestor_par)
    except ValueError:
        path_to_omp_par = False
    try:
        path_to_omp_par_do = node_target.path_from(omp_ancestor_par_do)
    except ValueError:
        path_to_omp_par_do = False

    # DEFAULT result
    # The default presence of OMP given the below ancestry
    # True is it thinking there is OMP present above, so it will not try.
    # False is that there is no OMP ancestry.
    # If there is a parallel ancestor and path, or there is a parallel do
    # ancestor and path.
    if ((omp_ancestor_par and path_to_omp_par)
            or (omp_ancestor_par_do and path_to_omp_par_do)):
        print("Parallel OMP region ancestor found")
        omp_ancestry_presence = True
    else:
        omp_ancestry_presence = False

    # Below are exceptions to the rules

    # A do transformation wants a parallel section above, it checks and
    # corrects. An occurrence where adjacent parallel do regions are being
    # picked up and the parallel ancestor is misreporting. Therefore,
    # if there a parallel ancestor and path, but there is not a path to a
    # parallel do reference node. Checking the paths mitigates this occurrence.
    # To be reported to STFC as a bug in psyclone.
    if omp_ancestor_par and path_to_omp_par and not path_to_omp_par_do:
        if transformation.omp_directive == "do":
            print("Adjacent node detected in Ancestry")
            print("Parallel OMP region ignored as transformation is OMP do")
            omp_ancestry_presence = False

    # Psyclone is trying to add a do, to a section without a parallel and is
    # crashing We should handle this checking here for now and report back.
    if transformation.omp_directive == "do":
        if not omp_ancestor_par and not path_to_omp_par:
            print("No Parallel region present, cannot try do")
            omp_ancestry_presence = True

    # This stops the nesting of OMP do under parallel sections
    # If there is one already present, it will effectively understand the above
    # a parallel and a do, which we don't want to try parallelism in this
    # occurrence.
    if transformation.omp_directive == "do":
        if omp_ancestor_do:
            omp_ancestry_presence = True

    # Generally returns True if OMP detected.
    # Depending on the transformation provided, it may intentionally return
    # False, for example if the transformation is a do, and it's found a
    # parallel section.

    return omp_ancestry_presence


    def get_last_child_shed(loop_node):
    '''
    Get the last child loop schedule of the provided node.
    Then we can do some checks on it
    '''

    child_list = loop_node.children
    loop_list = []

    if child_list:
        # Work through the children
        for node in loop_node.children:
            # If its the Schedule - there is always a Schedule
            if isinstance(node, Schedule):
                loop_list = node.walk(Loop)
                # The loop will find the first schedule. Then exit the loop.
                break

        # If there is a list of loops
        if loop_list:
            # Had an error when accessing the last of a
            # single element array
            if len(loop_list) > 1:
                indexer = -1
            else:
                indexer = 0
            # get the schedule of the last loop
            shed_list = loop_list[indexer].walk(Schedule)
            if shed_list:
                # Had an error when accessing the last of a
                # single element array
                if len(shed_list) > 1:
                    indexer = -1
                else:
                    indexer = 0
                # If there are multiple
                # schedules, get the of the last one
                ret_shed = shed_list[indexer]
            # Always otherwise return False
            else:
                ret_shed = False
        # Always otherwise return False
        else:
            ret_shed = False

    # Always otherwise return False
    else:
        ret_shed = False

    return ret_shed


def get_specific_children(loop_node):
    '''
    Psytrans function only returns one child, we might want all children.
    '''

    ret_node_list = []
    # The list of children is a node list
    # Walk each node in the list for Loops
    # If the node was a loop
    # And the child returned is not itself
    for node in loop_node.children:
        for child in node.walk(Loop):
            if loop_node != child:
                ret_node_list.append(child)

    # Return all of the children
    return ret_node_list


def span_check_loop(child_list, start_index_loop, loop_max_qty):
    '''
    Run through child_list from the provided start index.
    Check each node.
    If it is an If block or a Loop node, check loops, self
    and children. These loops are checked against their own set
    of rules and a provided limit from the override.
    '''
    # Setup for loop
    last_good_index = 0
    loop_child_qty = 0

    # Assume we are unable to span a region if nothing is found
    parallel_possible = False

    # Work through the child list of nodes of the given ancestor
    # Starting at the current node, ending at the last child node
    # The goal of the loop is to find the most appropriate end node for
    # a parallel region. It will check all of the loops present in the
    # current proposed parallel region can be transformed.
    # As soon as one cannot be, it ends the loop, leaving the end index
    # as the previous step through the loop.
    for index in range(start_index_loop, len(child_list)-1):
        check_current_node = child_list[index]

        # reset each loop
        try_parallel = False

        assignment_cont = False

        # If its an assignment we want to continue to the next index to check
        # but not try a parallel region. This way they can be included in the
        # spanning region, but will not be the start or end nodes.
        # May need to be adjusted in the future
        if isinstance(check_current_node, Assignment):
            assignment_cont = True

        # If the node is an if block or loop,
        # check all of the loops could be OpenMP
        # parallel do normally, as a safety check for the region as a whole.
        if isinstance(check_current_node, (IfBlock, Loop)):
            ret_child_qty = 0
            try_parallel, ret_child_qty = child_valid_trans(check_current_node)
            # Add more checks here and keep setting try_parallel or similar
            if try_parallel:
                loop_child_qty = loop_child_qty + ret_child_qty

        if loop_child_qty > loop_max_qty:
            break

        # if the node is a loop, if or assignment, we want to continue
        # we've checked as to whether to loop children are good to parallelise
        # if it's an assignment node, we want to continue the loop,
        # but go no further with the checks.
        if try_parallel or assignment_cont:
            # Leave these if checks in place, try_parallel and else,
            # index > start_index_loop, they work well
            # If the node loop children are good, and it's not the first node
            if try_parallel:
                if index > start_index_loop:
                    check_span_nodes = []
                    # Surely we should be checking the current index?
                    for index_inner in range(start_index_loop, index+1):
                        check_span_nodes.append(child_list[index_inner])
                    # Try the transformation
                    error = try_validation(check_span_nodes, omp_parallel, {})
                    # If there is an error, we cannot do this one and
                    # should break
                    if len(error) == 0 or error == "":
                        parallel_possible = True
                        last_good_index = index
                    else:
                        print(error)
                        break
            # else:
            #     break
        else:
            break

    return parallel_possible, last_good_index


    def span_parallel(loop_node, loop_max_qty):
    '''
    Transformation used is omp_parallel. Span a parallel section.
    Get the ancestor node of the provided node, then grab it's children.
    This is a list of all nodes, including the provided node.
    This provided node will be the first node checked.
    '''

    # Find the ancestor schedule.
    # Given all of this stems from the first loop
    # There is an occurrence where this needs to stem
    # from the first if above a loop
    # so far no adverse effects of doing so
    if_loop_ancestor = loop_node.ancestor(IfBlock)
    if if_loop_ancestor:
        shared_ancestor = if_loop_ancestor.ancestor(Schedule)
        check_node = if_loop_ancestor
    # Otherwise get an reference to the ancestor schedule
    # Even the top loop, who's ancestor is a subroutine
    # Or similar, will
    else:
        shared_ancestor = loop_node.ancestor(Schedule)
        check_node = loop_node

    # Get the child list of the ancestors schedule
    # This will be used to have a list of potential nodes
    # to span over ready.
    child_list = shared_ancestor.children

    # Work through the list, until we meet the node which is
    # the current origin in the schedule of the ancestor.
    # This will be the first index node which a potential
    # parallel region is spanned from.
    start_index_loop = 0
    for index, node in enumerate(child_list):
        if check_node == node:
            start_index_loop = index
            # We only want the start, we can exit the loop
            break

    # Check each node in the child list
    # Check all loop nodes under each node (including node if is a loop)
    parallel_possible, last_good_index = span_check_loop(child_list,
                                                         start_index_loop,
                                                         loop_max_qty)

    # The final attempt to see if parallel region is possible
    # Given these indexes have been validated, it should be
    if parallel_possible:
        span_nodes = []
        for index_inner in range(start_index_loop, last_good_index+1):
            span_nodes.append(child_list[index_inner])
        if len(span_nodes) > 1:
            error = try_transformation(span_nodes, omp_parallel, {})
            if len(error) == 0 or error == "":
                print("Spanning over")
                print(span_nodes)


def strip_index(line, str_tag):
    '''
    Run through the provided string line from a schedule, and
    strip the line at the given tag down to just an index.
    There does not seem to be an alterative method in PSYIR
    to return just this property. In order to check a
    struct (type) that is accessed by a list, this is method
    required.
    '''

    breakout_string = line.partition(str_tag)
    # We know it's the start of the array, given the str_tag
    indexer_list = breakout_string[2].split(",")
    # formatting
    indexer_ref = indexer_list[0]
    # A list of characters which will be removed from strings.
    for char in ["[", "]", "'"]:
        indexer_ref = indexer_ref.replace(char, "")

    # return the index without any clutter
    return indexer_ref


def string_match_ref_var(loop_node):
    '''
    We need to check the metadata of whether references of a
    loop node match to certain properties.
    Return True, if a Array of types (or ArrayOfStructures)
    is found.
    ArrayOfStructures is a good reference to find, it notes
    that there is an array of objects in the children that is accessed
    in the loop body, likely better being parallelised differently.
    Therefore if we find this match, we want to skip it.
    '''

    # Note, I've tried to access things a bit more cleanly,
    # but either way we are going to have to manipulate a
    # string. This is functional and does the job required.

    # Find out whether there is an Array_struct_ref, and does
    # it's reference patch the current loop nodes
    ret_struct_ref = False

    # get the last child schedule, only do work if shed exists
    last_child_shed = get_last_child_shed(loop_node)

    # Only do the work if ArrayOfStructuresReference exists
    do_checks = False

    if last_child_shed:
        reference_tags = []
        for struct_ref in last_child_shed.walk(ArrayOfStructuresReference):
            if struct_ref:
                do_checks = True

                # get the reference the hard way as we cannot seem to
                # access it directly
                information = str(struct_ref)
                array_info = information.splitlines()

                # Work through each line of the struct_ref turned into a str
                for line in array_info:
                    # If there is a Reference, this is what we are going to
                    # manipulate to gather out the index reference
                    if ("Reference[name:" in line and
                            "ArrayOfStructures" not in line):
                        # This is an array of structure index references
                        # that are present in the lowest down loop body
                        # We are to use this list to check a loop variable
                        reference_tags.append(strip_index(line,
                                                          "Reference[name:"))

        # Only do the work if ArrayOfStructuresReference exists
        if do_checks:
            # get the variable reference the hard way as we cannot seem to
            # access it directly
            information = str(loop_node)
            array_info = information.splitlines()

            # Note we can access loop_node.variable. However to remove all of
            # the extra jargon, and just return the loop, we will have to do
            # similar to the below anyway. Below is consistent
            # with the above which still seems to be the only way to access the
            # struct references with psyir.
            variable_tags = []
            for line in array_info:
                if "Loop[variable:" in line:
                    variable_tags.append(strip_index(line,
                                                     "Loop[variable:"))

            # The first is the current indexer of the loop
            # If the loop index is in the indexes found related to the
            # ArrayOfStructures reference, then we've found a match
            if variable_tags[0] in reference_tags:
                ret_struct_ref = True

    return ret_struct_ref


def try_transformation(
    node_target: Node,
    transformation: Transformation,
    options: dict = None
):
    '''
    Try the provided transformation provided.
    Otherwise raise an error which is returned.
    The try transformation is present is all transformations for OMP,
    so it has been made generic and called by most below.

    :arg node_target: The Node to transform - Can instead be provided
                        as a list of nodes to apply.
    :type node_target: :py:class:`Node`
    :arg transformation: The transformation to apply
    :type transformation: :py:class:`Transformation`
    :kwarg options: a dictionary of clause options.
    :type options: :py:class:`dict`
    '''

    if options is None:
        options = {}

    error_message = ""

    try:
        print("Trying")
        transformation.apply(node_target, options=options)

    except (TransformationError, IndexError) as err:
        print(f"Could not transform "
              f"because:\n{err.value}")
        # Catch the error message for later comparison
        error_message = str(err.value)

    return error_message


def try_validation(
    node_target: Node,
    transformation: Transformation,
    options: dict = None
):
    '''
    Try the provided transformation provided.
    Instead with a validate as opposed to apply
    Otherwise raise an error which is returned.
    The try transformation is present is all transformations for OMP,
    so it has been made generic and called by most below.

    :arg node_target: The Node to transform - Can instead be provided
                        as a list of nodes to apply.
    :type node_target: :py:class:`Node`
    :arg transformation: The transformation to apply
    :type transformation: :py:class:`Transformation`
    :kwarg options: a dictionary of clause options.
    :type options: :py:class:`dict`
    '''

    if options is None:
        options = {}

    error_message = ""

    try:
        print("Validating")
        transformation.validate(node_target, options=options)

    except (TransformationError, IndexError) as err:
        error_message = str(err)
        print(f"Could not transform "
              f"because:\n{error_message}")
    # Catch the error message for later comparison

    return error_message


def update_ignore_list(
                    loop_node,
                    current_options,
                    override_class
                    ):
    '''
    Pass in a loop_node and array of loop_tag_overrides objects.
    Check each object and if the tag matches the loop, check the
    know list, and append new options.
    '''

    # Setup References
    loop_tag = str(loop_node.loop_type)
    current_ignore_list = []

    overrides = override_class.get_tag_overrides()
    if overrides:
        for override_obj in overrides:
            if loop_tag == override_obj.get_loop_tag():
                override_options = override_obj.options()
                if "ignore_dependencies_for" in override_options:
                    current_ignore_list.append(
                        override_options["ignore_dependencies_for"])

    current_options["ignore_dependencies_for"] = current_ignore_list

    if current_options["ignore_dependencies_for"]:
        print("ignore_dependencies_for")
        print(current_options["ignore_dependencies_for"])

    return current_options


def validate_rules_para(loop_node, options):
    '''
    This is being duplicated in a few locations
    Check the current Loop node against a number of
    rule patterns to confirm whether we transform
    or not
    '''

    valid_loop = False

    n_collapse = work_out_collapse_depth(loop_node)
    if n_collapse > 1:
        options["collapse"] = n_collapse

    valid_loop = True

    return valid_loop, options


def validate_rules(loop_node, options):
    '''
    This is being duplicated in a few locations
    Check the current Loop node against a number of
    rule patterns to confirm whether we transform
    or not
    '''

    valid_loop = False
    check_struct = False
    check_struct = string_match_ref_var(loop_node)

    if not check_struct:
        n_collapse = work_out_collapse_depth(loop_node)
        if n_collapse > 1:
            options["collapse"] = n_collapse
        valid_loop = True

    return valid_loop, options


def work_out_collapse_depth(loop_node):
    '''
    Generate a value for how many collapses to specifically
    do given the number of children.
    '''

    # The default number of loops is 1 given self
    n_collapse = 1
    # Are there any loop children, will return array of child
    # nodes.
    child_loop_list = get_specific_children(loop_node)
    if child_loop_list:
        # Add the length of the node array, or the number of
        # to the n_collapse value to return
        n_collapse = n_collapse + len(child_loop_list)

    return n_collapse

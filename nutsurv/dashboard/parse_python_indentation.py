import warnings


def parse_indentation(raw_python_file_contents):
    """Parse the contents of a file with python style indentation.
    >>> clean_file_contents = '''
    ... # ignored line
    ... level 1 # comments are ignored
    ...     level 2
    ...         level 3
    ... level 1
    ... level 1
    ...     level 2'''
    >>> out = parse_python_indentation(clean_file_contents)
    >>> result = [{
    ...     'key': 'level 1',
    ...     'offspring': [{
    ...         'key': 'level 2',
    ...         'offspring': [{
    ...             'key': 'level 3',
    ...             'offspring': []
    ...         }]
    ...     }]
    ... }, {
    ...     'key': 'level 1',
    ...     'offspring': []
    ... }, {
    ...     'key': 'level 1',
    ...     'offspring': [{
    ...         'key': 'level 2',
    ...         'offspring': []
    ...     }]
    ... }]
    >>> cmp(out, result)
    0
    >>> unclean_file_contents = '''
    ... # ignored line
    ... level 1 # comments are ignored
    ...     level 2
    ...       level 3 # The indentation level is too low here.
    ... level 1
    ... level 1
    ...     level 2'''
    >>> with warnings.catch_warnings(record=True) as w:
    ...     warnings.simplefilter("always")
    ...     a = parse_python_indentation(unclean_file_contents)
    >>> len(w)
    1
    >>> w[0].category
    <type 'exceptions.UserWarning'>
    >>> str(w[0].message)
    'Indentation with errors!'
    """

    raw_lines = raw_python_file_contents.split('\n')
    cleaned_lines = []
    python_output = []
    indentation_length = 0
    error = False
    i = 0

    # Remove comments and empty lines
    for raw_line in raw_lines:
        line_wo_comment = raw_line.split('#')[0].rstrip()
        if len(line_wo_comment.strip()) > 0:
            cleaned_lines.append(line_wo_comment)

    # Find indentation length
    while indentation_length == 0 and i < len(cleaned_lines):
        if len(cleaned_lines[i]) - len(cleaned_lines[i].lstrip()) > 0:
            indentation_length = len(cleaned_lines[i]) - len(cleaned_lines[i].lstrip())
        i += 1

    # Don't allow indentations of zero
    if indentation_length == 0:
        indentation_length = 1

    # Turn Python into a construct of Lists and Objects
    for cleaned_line in cleaned_lines:
        indentations = float(len(cleaned_line) - len(cleaned_line.lstrip())) / indentation_length
        current_list = python_output

        if indentations % 1 != 0:
            # indentation characters do not correspond to a known indentation level.
            error = True

        indentations = int(indentations)

        for j in range(0, indentations):
            if len(current_list) == 0:
                # The indentations tell us to go a place that it's not possible to go.
                error = True
            else:
                current_list = current_list[-1]['offspring']

        current_list.append({
            'key': cleaned_line.lstrip(),
            'offspring': []
        })

    if error:
        warnings.warn('Indentation with errors!', UserWarning)

    return python_output

if __name__ == "__main__":
    import doctest
    doctest.testmod()

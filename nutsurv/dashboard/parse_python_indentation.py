import warnings

def parse_python_indentation(raw_python_file_contents):
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
        indentations = (len(cleaned_line) - len(cleaned_line.lstrip())) / indentation_length
        current_list = python_output


        if indentations % 1 != 0:
            # indentation characters do not correspond to a known indentation level.
            error = True

        for j in range(0, indentations):
            if len(current_list) == 0:
                # The indentations tell us to go a place that it's not possible to go.
                error = True
            else:
                current_list = current_list[-1]['children']

        current_list.append({
            'key': cleaned_line.lstrip(),
            'children': []
        })

    if error:
        warnings.warn('Python formatting with errors!', UserWarning)

    return python_output

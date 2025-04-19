from wcwidth import wcswidth


def format_cn(text: str, width: int, align: str = '<'):
    current_width = wcswidth(text)
    padding = max(width - current_width, 0)
    sss = ' '

    if align == '<':
        res =  text + sss * padding
    elif align == '>':
        res =  sss * padding + text
    elif align == '^':
        left = padding // 2
        right = padding - left
        res =  sss * left + text + sss * right
    else:
        raise ValueError('align must be <, >, or ^')
    print("_________________________________________________________")
    print(f"Res: |{res}|,Text:{text}, width: {current_width}, padding: {padding}")

    return res

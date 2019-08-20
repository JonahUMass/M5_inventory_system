import inventory as inv


'''def switch(msg, options = ('',) ):
    #msg = [sntc.strip(' ') for sntc in msg.split('.')]
    #[sntc[0] = sntc[0].Upper() for sntc in msg]
    #print('. '.join(msg) + '\n' + '\n'.join(options))
    print(msg)
    [print(op) for op in options]
    resp = input('input:').lower().split(' ')
    '''




while 1:
    options = {'add new uid item' : 0,
                'add new type id' : 1,
                'checkout item'   : 2,
                'search type ids '}
    valin = input("what would you like to do?").lower().replace(' ', '')

    def pife(str):
        """
        desc: "pop if front (is) equal" checks if valin starts with a specific sequence.
                if it does that is popped of the front and True is returned;
        arg str: the string to check for at the beginging of valin;
        """
        global valin
        if valin.startswith(str):
            valin = valin[len(str):]
            return True
        else:
            return False

    # arguments for a function
    args = []
    kwargs = {}

    if pife('addnew'):
        if
    elif pife('check'):
        if pife('out'):
            pass
        elif pife('in'):
            pass
    elif pife('search'):
        print('feature not yet supported')

    print()

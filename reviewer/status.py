
__author__ = 'TimeWz667'
__all__ = ['Status', 'in_status', 'summarise_status', 'approve_status', 'disapprove_status', 'drop_status']


Status = [
    'Context In',
    'Abstract In',
    'Title In',
    'None',
    'Title Out',
    'Abstract Out',
    'Context Out'
]


def is_context_out(st):
    return st == 'Context Out'


def is_context_in(st):
    return st == 'Context In'


def is_abstract_out(st):
    return st == 'Abstract Out'


def is_abstract_in(st):
    return st == 'Abstract In' or is_context_in(st) or is_context_out(st)


def is_title_out(st):
    return st == 'Title Out'


def is_title_in(st):
    return st == 'Title In' or is_abstract_in(st) or is_abstract_out(st)


def is_none(st):
    return st in Status


Inclusion = {
    'None': is_none,
    'Title In': is_title_in,
    'Title Out': is_title_out,
    'Abstract In': is_abstract_in,
    'Abstract Out': is_abstract_out,
    'Context In': is_context_in,
    'Context Out': is_context_out
}


def in_status(sub, st):
    return Inclusion[st](sub)


ApproveStatus = {
    'None': 'Title In',
    'Title In': 'Abstract In',
    'Title Out': 'None',
    'Abstract In': 'Context In',
    'Abstract Out': 'Title In',
    'Context Out': 'Abstract In'
}


DisapproveStatus = {
    'Title In': 'None',
    'Abstract In': 'Title In',
    'Context In': 'Abstract In',
    'Title Out': 'None',
    'Abstract Out': 'Title In',
    'Context Out': 'Abstract In',
}


DropStatus = {
    'None': 'Title Out',
    'Title In': 'Abstract Out',
    'Abstract In': 'Context Out'
}


def approve_status(st):
    try:
        return ApproveStatus[st]
    except KeyError:
        return st


def disapprove_status(st):
    try:
        return DisapproveStatus[st]
    except KeyError:
        return st


def drop_status(st):
    try:
        return DropStatus[st]
    except KeyError:
        return st


def summarise_status(sts, exclusive=False):
    if exclusive:
        return [(gp, len([st for st in sts if st == gp])) for gp in Status]
    else:
        return [(gp,len([st for st in sts if in_status(st, gp)])) for gp in Status]


if __name__ == '__main__':
    print(is_title_in('Context In'))

    print(in_status('Context In', 'Abstract In'))

    print(in_status('Context Out', 'Abstract In'))

    print(in_status('Abstract In', 'Abstract In'))

    print(disapprove_status('Abstract In'))

    sts = ['Abstract In' for _ in range(100)] + ['Abstract Out'for _ in range(30)]
    sts += ['Title In' for _ in range(100)] + ['Title Out'for _ in range(30)]
    sts += ['Context In' for _ in range(100)] + ['Context Out' for _ in range(30)]

    for k, v in summarise_status(sts):
        print(k, v)

    for k, v in summarise_status(sts, True):
        print(k, v)

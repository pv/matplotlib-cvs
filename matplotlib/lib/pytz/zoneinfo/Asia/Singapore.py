'''tzinfo timezone information for Asia/Singapore.'''
from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as d
from pytz.tzinfo import memorized_ttinfo as i

class Singapore(DstTzInfo):
    '''Asia/Singapore timezone definition. See datetime.tzinfo for details'''

    _zone = 'Asia/Singapore'

    _utc_transition_times = [
d(1,1,1,0,0,0),
d(1905,5,31,17,4,35),
d(1932,12,31,17,0,0),
d(1935,12,31,16,40,0),
d(1941,8,31,16,40,0),
d(1942,2,15,16,30,0),
d(1945,9,11,15,0,0),
d(1965,8,8,16,30,0),
d(1981,12,31,16,30,0),
        ]

    _transition_info = [
i(24900,0,'SMT'),
i(25200,0,'MALT'),
i(26400,1200,'MALST'),
i(26400,0,'MALT'),
i(27000,0,'MALT'),
i(32400,0,'JST'),
i(27000,0,'MALT'),
i(27000,0,'SGT'),
i(28800,0,'SGT'),
        ]

Singapore = Singapore()


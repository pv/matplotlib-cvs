from matplotlib.matlab import *

font = {'fontname'   : 'Courier',
        'color'      : 'r',
        'fontweight' : 'normal',
        'fontsize'   : 12}

def f(t):
    s1 = cos(2*pi*t)
    e1 = exp(-t)
    return multiply(s1,e1)

t1 = arange(0.0, 5.0, 0.1)
t2 = arange(0.0, 5.0, 0.02)

plot(t1, f(t1), 'bo', t2, f(t2), 'k')
title('Damped exponential decay', font, fontsize=14, color='r')
text(3, 0.65, 'cos(2 pi t) exp(-t)', font, color='k')
xlabel('time (s)', font)
ylabel('voltage (mV)', font)

savefig('text_themes', dpi=150)
show()
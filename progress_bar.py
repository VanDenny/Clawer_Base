import sys

def view_bar(num, total):
    rate = float(num) / float(total)
    rate_num = int(rate * 100)
    r = '\r[%s%s]%d%%' % ("="*(rate_num+1), " "*(100-rate_num-1), rate_num, )
    sys.stdout.write(r)
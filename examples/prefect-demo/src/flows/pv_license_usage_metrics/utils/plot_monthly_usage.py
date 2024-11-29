import matplotlib.pyplot as plt


def PlotMonthlyUsage(Count):
    fig, ax = plt.subplots()
    ax.plot(Count['Month'], Count['Count'])
    plt.setp(ax.get_xticklabels(), rotation=45,
             ha='right', rotation_mode='anchor')

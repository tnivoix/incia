import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

fig = plt.figure()

gs = gridspec.GridSpec(3, 1, height_ratios=[5, 2, 1], hspace=0.3)
gs2 = gridspec.GridSpec(2,1, height_ratios=[5,3])

ax1 = fig.add_subplot(gs[0])
ax2 = fig.add_subplot(gs[1], sharex=ax1)
ax3 = fig.add_subplot(gs[2], sharex=ax2)

ax1.plot([1,2,3], [1,2,3], color="crimson")
ax2.plot([1,2,3], [2,3,1], color="darkorange")
ax3.plot([1,2,3], [3,2,1], color="limegreen")

visible = True

def toggle_ax2(event):
    global visible
    visible = not visible
    ax2.set_visible(visible)
    if visible:
        ax1.set_position(gs[0].get_position(fig))
        ax3.set_position(gs[2].get_position(fig))
    else:
        ax1.set_position(gs2[0].get_position(fig))
        ax3.set_position(gs2[1].get_position(fig))

    plt.draw()

fig.canvas.mpl_connect('button_press_event', toggle_ax2)
plt.show()
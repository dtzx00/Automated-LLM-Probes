"""Figure 3 - between-person divergence (uniqueness) alone, by model release date."""
from overtime_style import *
dat,btw,H_DAT,H_BTW,models=load_all(); xmin,xmax=limits(dat,models)
fig,ax=new_fig()
lineages(ax,dat,btw,models,'between')
human_lines(ax,xmin,xmax,H_DAT,H_BTW,show_dat=False,show_btw=True)
between_markers(ax,dat,btw,models)
frame(ax,xmin,xmax,"Between-Person Divergence by Model Release Date\n"
                   "Open markers = model between-person score; purple dotted = human baseline; lines = OpenAI and Claude")
legend(ax,dat,models,[Line2D([0],[0],marker='o',ls='none',markerfacecolor='white',markeredgecolor='#555',
                             markeredgewidth=2.6,ms=12,label='Between-person'),
                      Line2D([0],[0],color=HUMAN_PURPLE,lw=3,ls=':',marker='o',ms=12,label='Human')],
       open_style=True)
save(fig,"/home/user/fig3_uniqueness.png")

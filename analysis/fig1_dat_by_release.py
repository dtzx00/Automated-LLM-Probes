"""Figure 1 - within-person divergence (DAT) by model release date."""
from overtime_style import *
dat,btw,H_DAT,H_BTW,models=load_all(); xmin,xmax=limits(dat,models)
fig,ax=new_fig()
lineages(ax,dat,btw,models,'dat')
human_lines(ax,xmin,xmax,H_DAT,H_BTW,show_dat=True,show_btw=False)
dat_markers(ax,dat,models,alpha=1.0)
frame(ax,xmin,xmax,"Within-Person Divergence (DAT) by Model Release Date\n"
                   "Filled markers = model DAT score; purple = human baseline; lines = OpenAI and Claude")
legend(ax,dat,models,[Line2D([0],[0],marker='o',ls='none',color='#555',ms=12,label='Within-person (DAT)'),
                      Line2D([0],[0],color=HUMAN_PURPLE,lw=3,marker='o',ms=12,label='Human')])
save(fig,"/home/user/verify/results/fig1_dat_by_release.png")

"""Figure 2 - the shift from within-person (DAT) to between-person divergence, by release date."""
from overtime_style import *
dat,btw,H_DAT,H_BTW,models=load_all(); xmin,xmax=limits(dat,models)
fig,ax=new_fig()
lineages(ax,dat,btw,models,'both')
human_lines(ax,xmin,xmax,H_DAT,H_BTW,show_dat=True,show_btw=True,dat_alpha=0.50,band=True)
shift_arrows(ax,dat,btw,models)
dat_markers(ax,dat,models,alpha=0.50)
between_markers(ax,dat,btw,models)
frame(ax,xmin,xmax,"From Within-Person (DAT) to Between-Person Divergence by Model Release Date\n"
                   "Transparent filled = DAT; open = between-person; arrow = direction of shift; shading = OpenAI and Claude gap")
legend(ax,dat,models,[
    Line2D([0],[0],marker='o',ls='none',color='#555',alpha=0.50,ms=12,label='Within-person (DAT)'),
    Line2D([0],[0],marker='o',ls='none',markerfacecolor='white',markeredgecolor='#555',markeredgewidth=2.6,ms=12,label='Between-person'),
    Line2D([0],[0],color='#555',lw=2.4,alpha=0.50,label='Shift DAT to between'),
    Patch(facecolor='#555',alpha=0.10,label='Gap of scores'),
    Line2D([0],[0],color=HUMAN_PURPLE,lw=3,marker='o',ms=12,label='Human')])
save(fig,"/home/user/fig2_dat_to_uniqueness.png")
